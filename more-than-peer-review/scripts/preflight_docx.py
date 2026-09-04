#!/usr/bin/env python3
"""Local, bounded DOCX preflight for the peer-review workspace.

The scanner never executes document actions, follows relationships, or extracts
embedded objects. It inspects the OOXML package in place, compares prompt-like
text coverage with a trusted local PDF rendering, and binds the source DOCX to
the rendered PDF security report by SHA-256 digest.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any, Iterable
import xml.etree.ElementTree as ET


SCHEMA_VERSION = "1.0"
MAX_INPUT_BYTES = 128 * 1024 * 1024
MAX_ENTRY_COUNT = 5000
MAX_ENTRY_BYTES = 64 * 1024 * 1024
MAX_EXPANDED_BYTES = 256 * 1024 * 1024
MAX_TOOL_OUTPUT_BYTES = 1024 * 1024

REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"

PROMPT_RULES: tuple[tuple[str, re.Pattern[str]], ...] = (
    (
        "PROMPT_IGNORE_INSTRUCTIONS",
        re.compile(r"\bignore\s+(?:all|any|the|previous|prior)\s+instructions?\b", re.I),
    ),
    (
        "PROMPT_SYSTEM_OR_DEVELOPER_MESSAGE",
        re.compile(r"\b(?:system|developer)\s+(?:message|prompt|instructions?)\b", re.I),
    ),
    (
        "PROMPT_MODEL_OR_REVIEWER_COMMAND",
        re.compile(
            r"\b(?:chatgpt|language\s+model|llm|ai\s+assistant|reviewer)\b"
            r".{0,80}\b(?:must|should|shall|is\s+instructed|please)\b",
            re.I | re.S,
        ),
    ),
    (
        "PROMPT_SUPPRESS_REPORTING",
        re.compile(
            r"\bdo\s+not\s+(?:mention|report|disclose|criticize|flag|reveal)\b",
            re.I,
        ),
    ),
    (
        "PROMPT_FORCE_RECOMMENDATION",
        re.compile(
            r"\b(?:give|assign|recommend|select)\b.{0,80}"
            r"\b(?:accept|acceptance|reject|score|rating)\b",
            re.I | re.S,
        ),
    ),
)

TEXT_PART = re.compile(
    r"^word/(?:document|header\d*|footer\d*|footnotes|endnotes|comments)\.xml$",
    re.I,
)

BLOCKING_ENTRY_PATTERNS: tuple[tuple[str, re.Pattern[str], str], ...] = (
    (
        "DOCX_VBA_PROJECT",
        re.compile(r"(?:^|/)vbaProject\.bin$", re.I),
        "A VBA macro project is present.",
    ),
    (
        "DOCX_ACTIVEX",
        re.compile(r"^word/activeX/", re.I),
        "An ActiveX component is present.",
    ),
    (
        "DOCX_CUSTOM_UI",
        re.compile(r"^customUI/", re.I),
        "A custom Office UI package part is present.",
    ),
    (
        "DOCX_EMBEDDED_EXECUTABLE",
        re.compile(
            r"^word/embeddings/.*\.(?:exe|com|bat|cmd|ps1|js|jse|vbs|vbe|scr|msi|dll)$",
            re.I,
        ),
        "An executable-type embedded file is present.",
    ),
)

BLOCKING_EXTERNAL_RELATIONSHIPS = {
    "attachedtemplate",
    "oleobject",
    "package",
    "activexcontrol",
    "externaldata",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def finding(
    rule_id: str,
    severity: str,
    category: str,
    message: str,
    *,
    count: int = 1,
    parts: Iterable[str] | None = None,
) -> dict[str, Any]:
    item: dict[str, Any] = {
        "rule_id": rule_id,
        "severity": severity,
        "category": category,
        "message": message,
        "count": count,
    }
    if parts:
        item["parts"] = sorted(set(parts))[:20]
    return item


def status_for(findings: Iterable[dict[str, Any]]) -> str:
    severities = {item["severity"] for item in findings}
    if "BLOCK" in severities:
        return "BLOCK"
    if "WARN" in severities:
        return "WARN"
    return "PASS"


def merge_findings(items: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    merged: dict[tuple[str, str, str], dict[str, Any]] = {}
    for item in items:
        key = (item["rule_id"], item["severity"], item["category"])
        current = merged.get(key)
        if current is None:
            merged[key] = dict(item)
            continue
        current["count"] = current.get("count", 1) + item.get("count", 1)
        parts = set(current.get("parts", [])) | set(item.get("parts", []))
        if parts:
            current["parts"] = sorted(parts)[:20]
    return sorted(
        merged.values(),
        key=lambda item: (
            {"BLOCK": 0, "WARN": 1, "INFO": 2}.get(item["severity"], 3),
            item["rule_id"],
        ),
    )


def safe_member_name(name: str) -> bool:
    path = PurePosixPath(name)
    return not (
        path.is_absolute()
        or ".." in path.parts
        or "\\" in name
        or "\x00" in name
    )


def relationship_kind(type_uri: str) -> str:
    return type_uri.rstrip("/").rsplit("/", 1)[-1].lower()


def prompt_hits(text: str) -> set[str]:
    return {rule_id for rule_id, pattern in PROMPT_RULES if pattern.search(text)}


def compare_prompt_rules(
    source_hits: dict[str, set[str]],
    rendered_hits: set[str] | None,
) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    all_source_rules = set(source_hits)
    if not all_source_rules:
        return results
    for rule_id in sorted(all_source_rules):
        results.append(
            finding(
                rule_id,
                "INFO",
                "prompt_like_text",
                "Instruction-like language appears in the DOCX text layer and is treated as untrusted manuscript data.",
                parts=source_hits[rule_id],
            )
        )
    if rendered_hits is None:
        results.append(
            finding(
                "DOCX_RENDER_TEXT_COMPARISON_UNAVAILABLE",
                "WARN",
                "coverage",
                "Prompt-like source text was found, but rendered-PDF text comparison was unavailable.",
            )
        )
        return results
    missing = all_source_rules - rendered_hits
    for rule_id in sorted(missing):
        results.append(
            finding(
                "DOCX_TEXT_RENDER_MISMATCH",
                "WARN",
                "visibility_mismatch",
                "Instruction-like text was found in the DOCX package but not recovered from the rendered PDF text layer.",
                parts=source_hits[rule_id],
            )
        )
    return results


def extract_pdf_text(path: Path) -> tuple[str | None, dict[str, Any]]:
    pdftotext = shutil.which("pdftotext")
    tooling = {"available": bool(pdftotext)}
    if not pdftotext:
        return None, tooling
    with tempfile.TemporaryDirectory(prefix="docx-render-check-") as directory:
        output_path = Path(directory) / "rendered.txt"
        try:
            completed = subprocess.run(
                [pdftotext, "-enc", "UTF-8", str(path), str(output_path)],
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
                timeout=45,
                env={"LANG": "C", "LC_ALL": "C"},
                start_new_session=True,
            )
        except subprocess.TimeoutExpired:
            tooling.update({"returncode": None, "timed_out": True})
            return None, tooling
        tooling.update({"returncode": completed.returncode, "timed_out": False})
        if completed.returncode != 0 or not output_path.exists():
            return None, tooling
        if output_path.stat().st_size > MAX_EXPANDED_BYTES:
            tooling["output_too_large"] = True
            return None, tooling
        return output_path.read_text(encoding="utf-8", errors="replace"), tooling


def scan_package(source: Path) -> tuple[list[dict[str, Any]], dict[str, Any], dict[str, set[str]]]:
    findings: list[dict[str, Any]] = []
    source_hits: dict[str, set[str]] = {}
    package: dict[str, Any] = {
        "entry_count": 0,
        "expanded_bytes": 0,
        "passive_embedded_object_count": 0,
        "external_relationship_counts_by_type": {},
        "malformed_relationship_part_count": 0,
    }
    with zipfile.ZipFile(source) as archive:
        infos = archive.infolist()
        package["entry_count"] = len(infos)
        if len(infos) > MAX_ENTRY_COUNT:
            findings.append(
                finding(
                    "DOCX_ENTRY_LIMIT_EXCEEDED",
                    "BLOCK",
                    "package",
                    "The OOXML package contains more entries than the bounded scan permits.",
                    count=len(infos),
                )
            )
        expanded_bytes = sum(info.file_size for info in infos)
        package["expanded_bytes"] = expanded_bytes
        if expanded_bytes > MAX_EXPANDED_BYTES:
            findings.append(
                finding(
                    "DOCX_EXPANDED_SIZE_LIMIT_EXCEEDED",
                    "BLOCK",
                    "package",
                    "The OOXML expanded size exceeds the bounded scan limit.",
                )
            )

        names = {info.filename for info in infos}
        for required in ("[Content_Types].xml", "word/document.xml"):
            if required not in names:
                findings.append(
                    finding(
                        "DOCX_REQUIRED_PART_MISSING",
                        "BLOCK",
                        "package",
                        "A required OOXML document part is missing.",
                        parts=[required],
                    )
                )

        for info in infos:
            name = info.filename
            if not safe_member_name(name):
                findings.append(
                    finding(
                        "DOCX_UNSAFE_MEMBER_PATH",
                        "BLOCK",
                        "package",
                        "An unsafe package member path is present.",
                        parts=[name],
                    )
                )
            unix_mode = info.external_attr >> 16
            if stat.S_ISLNK(unix_mode):
                findings.append(
                    finding(
                        "DOCX_SYMLINK_MEMBER",
                        "BLOCK",
                        "package",
                        "A symbolic-link package member is present.",
                        parts=[name],
                    )
                )
            if info.flag_bits & 0x1:
                findings.append(
                    finding(
                        "DOCX_ENCRYPTED_MEMBER",
                        "BLOCK",
                        "coverage",
                        "An encrypted package member prevents complete inspection.",
                        parts=[name],
                    )
                )
            if info.file_size > MAX_ENTRY_BYTES:
                findings.append(
                    finding(
                        "DOCX_ENTRY_SIZE_LIMIT_EXCEEDED",
                        "BLOCK",
                        "package",
                        "A package member exceeds the bounded per-entry limit.",
                        parts=[name],
                    )
                )
            for rule_id, pattern, message in BLOCKING_ENTRY_PATTERNS:
                if pattern.search(name):
                    findings.append(
                        finding(rule_id, "BLOCK", "active_content", message, parts=[name])
                    )
            if name.lower().startswith("word/embeddings/"):
                package["passive_embedded_object_count"] += 1

        if package["passive_embedded_object_count"]:
            findings.append(
                finding(
                    "DOCX_PASSIVE_EMBEDDED_OBJECT",
                    "INFO",
                    "embedded_content",
                    "Passive embedded package objects are present and were not opened.",
                    count=package["passive_embedded_object_count"],
                )
            )

        if any(item["severity"] == "BLOCK" for item in findings):
            return findings, package, source_hits

        for info in infos:
            name = info.filename
            if info.file_size > MAX_ENTRY_BYTES:
                continue
            if name.endswith(".rels"):
                try:
                    root = ET.fromstring(archive.read(info))
                except (ET.ParseError, OSError, RuntimeError, zipfile.BadZipFile):
                    package["malformed_relationship_part_count"] += 1
                    findings.append(
                        finding(
                            "DOCX_RELATIONSHIP_PARSE_FAILED",
                            "WARN",
                            "coverage",
                            "A relationship part could not be parsed completely.",
                            parts=[name],
                        )
                    )
                    continue
                for relationship in root.findall(f"{{{REL_NS}}}Relationship"):
                    if relationship.attrib.get("TargetMode", "").lower() != "external":
                        continue
                    kind = relationship_kind(relationship.attrib.get("Type", "unknown"))
                    counts = package["external_relationship_counts_by_type"]
                    counts[kind] = counts.get(kind, 0) + 1
                    severity = "BLOCK" if kind in BLOCKING_EXTERNAL_RELATIONSHIPS else "INFO"
                    findings.append(
                        finding(
                            "DOCX_UNSAFE_EXTERNAL_RELATIONSHIP"
                            if severity == "BLOCK"
                            else "DOCX_EXTERNAL_RELATIONSHIP",
                            severity,
                            "external_relationship",
                            "An external OOXML relationship is present; targets were not followed.",
                            parts=[name],
                        )
                    )
            if not TEXT_PART.match(name):
                continue
            try:
                root = ET.fromstring(archive.read(info))
            except (ET.ParseError, OSError, RuntimeError, zipfile.BadZipFile):
                findings.append(
                    finding(
                        "DOCX_TEXT_PART_PARSE_FAILED",
                        "WARN",
                        "coverage",
                        "A manuscript text part could not be parsed completely.",
                        parts=[name],
                    )
                )
                continue
            text = " ".join(
                node.text or ""
                for node in root.iter()
                if node.tag.rsplit("}", 1)[-1] in {"t", "instrText"}
            )
            for rule_id in prompt_hits(text):
                source_hits.setdefault(rule_id, set()).add(name)
    return findings, package, source_hits


def validate_pdf_report(
    report_path: Path,
    rendered_pdf: Path,
    review_id: str,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    linkage: dict[str, Any] = {
        "report_path": str(report_path.resolve()),
        "rendered_pdf_path": str(rendered_pdf.resolve()),
        "rendered_pdf_sha256": sha256_file(rendered_pdf),
    }
    try:
        report = json.loads(report_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        findings.append(
            finding(
                "DOCX_PDF_REPORT_INVALID",
                "BLOCK",
                "provenance",
                "The rendered-PDF security report is missing or invalid.",
            )
        )
        return findings, linkage
    linkage["pdf_security_status"] = report.get("status")
    linkage["pdf_report_sha256"] = sha256_file(report_path)
    report_digest = report.get("source", {}).get("sha256")
    linkage["pdf_report_source_sha256"] = report_digest
    if report.get("review_id") != review_id:
        findings.append(
            finding(
                "DOCX_PDF_REPORT_REVIEW_ID_MISMATCH",
                "BLOCK",
                "provenance",
                "The rendered-PDF report belongs to a different review ID.",
            )
        )
    if report_digest != linkage["rendered_pdf_sha256"]:
        findings.append(
            finding(
                "DOCX_PDF_REPORT_DIGEST_MISMATCH",
                "BLOCK",
                "provenance",
                "The rendered PDF does not match the source digest recorded by its security report.",
            )
        )
    pdf_status = report.get("status")
    if pdf_status == "BLOCK":
        findings.append(
            finding(
                "DOCX_RENDERED_PDF_BLOCKED",
                "BLOCK",
                "companion_gate",
                "The rendered PDF security gate is BLOCK.",
            )
        )
    elif pdf_status == "WARN":
        findings.append(
            finding(
                "DOCX_RENDERED_PDF_WARN",
                "WARN",
                "companion_gate",
                "The rendered PDF security gate requires documented human clearance.",
            )
        )
    elif pdf_status != "PASS":
        findings.append(
            finding(
                "DOCX_RENDERED_PDF_STATUS_INVALID",
                "BLOCK",
                "companion_gate",
                "The rendered PDF report has no recognized gate status.",
            )
        )
    return findings, linkage


def write_json_atomic(path: Path, payload: dict[str, Any], overwrite: bool) -> None:
    if path.exists() and not overwrite:
        raise FileExistsError(f"output already exists: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temporary_path = Path(temporary_name)
    try:
        os.fchmod(fd, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, sort_keys=True)
            handle.write("\n")
        os.replace(temporary_path, path)
    except Exception:
        temporary_path.unlink(missing_ok=True)
        raise


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run a local, non-executing security preflight on a DOCX and its rendered PDF."
    )
    parser.add_argument("docx", type=Path, help="Source DOCX")
    parser.add_argument("--review-id", required=True, help="Stable manuscript review ID")
    parser.add_argument("--rendered-pdf", required=True, type=Path)
    parser.add_argument("--pdf-security-report", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path, help="JSON report path")
    parser.add_argument("--overwrite", action="store_true", help="Replace an existing report")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    source = args.docx.expanduser()
    rendered_pdf = args.rendered_pdf.expanduser()
    pdf_report = args.pdf_security_report.expanduser()
    for checked_path, label in ((source, "DOCX"), (rendered_pdf, "rendered PDF"), (pdf_report, "PDF report")):
        if checked_path.is_symlink():
            print(f"Refusing symlink {label} input.", file=sys.stderr)
            return 1
        if not checked_path.is_file():
            print(f"{label} not found: {checked_path}", file=sys.stderr)
            return 1
    size = source.stat().st_size
    if size <= 0 or size > MAX_INPUT_BYTES:
        print("DOCX size is empty or exceeds the bounded input limit.", file=sys.stderr)
        return 1
    if source.suffix.lower() != ".docx" or not zipfile.is_zipfile(source):
        print("Input is not a readable DOCX OOXML package.", file=sys.stderr)
        return 1

    findings: list[dict[str, Any]] = []
    try:
        package_findings, package, source_prompt_hits = scan_package(source)
    except (OSError, RuntimeError, zipfile.BadZipFile, zipfile.LargeZipFile):
        package_findings = [
            finding(
                "DOCX_PACKAGE_PARSE_FAILED",
                "BLOCK",
                "package",
                "The OOXML package could not be inspected safely within bounded limits.",
            )
        ]
        package = {}
        source_prompt_hits = {}
    findings.extend(package_findings)
    linkage_findings, linkage = validate_pdf_report(pdf_report, rendered_pdf, args.review_id)
    findings.extend(linkage_findings)

    rendered_text, pdftotext_tooling = extract_pdf_text(rendered_pdf)
    rendered_prompt_hits = None if rendered_text is None else prompt_hits(rendered_text)
    findings.extend(compare_prompt_rules(source_prompt_hits, rendered_prompt_hits))
    findings = merge_findings(findings)
    status = status_for(findings)
    report = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": utc_now(),
        "review_id": args.review_id,
        "status": status,
        "source": {
            "path": str(source.resolve()),
            "size_bytes": size,
            "sha256": sha256_file(source),
        },
        "rendered_pdf": linkage,
        "package": package,
        "summary": {
            "block_findings": sum(item["severity"] == "BLOCK" for item in findings),
            "warning_findings": sum(item["severity"] == "WARN" for item in findings),
            "informational_findings": sum(item["severity"] == "INFO" for item in findings),
        },
        "findings": findings,
        "tooling": {"pdftotext": pdftotext_tooling},
        "limitations": [
            "This is a bounded heuristic scan, not proof that a DOCX is safe or malicious.",
            "Embedded objects and external targets are counted or classified but never opened or followed.",
            "Rendered-PDF comparison can identify instruction-like source text absent from the PDF text layer, but it is not a complete semantic equivalence proof.",
            "The original DOCX remains untrusted after PASS; manuscript text never becomes an instruction source.",
        ],
        "notice": "Inspect WARN findings before continuing. BLOCK indicates that substantive review should stop.",
    }
    try:
        write_json_atomic(args.output, report, args.overwrite)
    except (OSError, FileExistsError) as error:
        print(str(error), file=sys.stderr)
        return 1
    print(json.dumps({"status": status, "output": str(args.output)}, sort_keys=True))
    return {"PASS": 0, "WARN": 2, "BLOCK": 3}[status]


if __name__ == "__main__":
    raise SystemExit(main())
