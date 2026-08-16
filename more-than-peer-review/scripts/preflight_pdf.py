#!/usr/bin/env python3
"""Local, bounded PDF preflight for the peer-review workspace.

The scanner never executes PDF actions, opens links, or extracts attachments.
It emits metadata, rule IDs, counts, and page numbers without manuscript text.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable
import xml.etree.ElementTree as ET


SCHEMA_VERSION = "1.0"
MAX_INPUT_BYTES = 128 * 1024 * 1024
MAX_EXPANDED_BYTES = 256 * 1024 * 1024
MAX_TEXT_BYTES = 64 * 1024 * 1024
MAX_TOOL_OUTPUT_BYTES = 1024 * 1024
MAX_REPORTED_PAGES = 20
MAX_OCR_PAGES = 10


TOKEN_RULES: tuple[tuple[str, str, bytes, str], ...] = (
    (
        "PDF_ACTIVE_JAVASCRIPT",
        "BLOCK",
        rb"/(?:JavaScript|JS)\b",
        "JavaScript action token is present.",
    ),
    (
        "PDF_AUTOMATIC_ACTION",
        "BLOCK",
        rb"/AA\b",
        "An additional-action dictionary token is present.",
    ),
    (
        "PDF_LAUNCH_ACTION",
        "BLOCK",
        rb"/Launch\b",
        "External launch action token is present.",
    ),
    (
        "PDF_FORM_ACTION",
        "BLOCK",
        rb"/(?:SubmitForm|ImportData)\b",
        "Form submission or data-import action token is present.",
    ),
    (
        "PDF_RICH_MEDIA",
        "BLOCK",
        rb"/RichMedia\b",
        "Rich-media content token is present.",
    ),
    (
        "PDF_EMBEDDED_FILE",
        "INFO",
        rb"/(?:EmbeddedFile|Filespec)\b",
        "Embedded-file or file-specification token is present.",
    ),
    (
        "PDF_INTERACTIVE_FORM",
        "INFO",
        rb"/(?:AcroForm|XFA)\b",
        "Interactive form token is present.",
    ),
    (
        "PDF_OPTIONAL_CONTENT",
        "INFO",
        rb"/(?:OCProperties|OCG)\b",
        "Optional-content layer token is present.",
    ),
    (
        "PDF_INVISIBLE_TEXT_MODE",
        "INFO",
        rb"(?<![0-9.])3\s+Tr\b",
        "Invisible text-rendering mode appears in a content stream.",
    ),
    (
        "PDF_ZERO_ALPHA",
        "INFO",
        rb"/(?:CA|ca)\s+0(?:\.0+)?\b",
        "A fully transparent graphics-state alpha appears.",
    ),
    (
        "PDF_WHITE_TEXT_HEURISTIC",
        "INFO",
        rb"(?<![0-9.])1(?:\.0+)?\s+1(?:\.0+)?\s+1(?:\.0+)?\s+rg\b",
        "A white text/fill color operator appears.",
    ),
    (
        "PDF_EXTERNAL_REFERENCE",
        "INFO",
        rb"/(?:URI|GoToR)\b",
        "External URI or remote-go-to token is present.",
    ),
    (
        "PDF_ANNOTATIONS",
        "INFO",
        rb"/Annots\b",
        "Annotation array token is present.",
    ),
)


OPEN_ACTION_REFERENCE = re.compile(rb"^\s*(\d+)\s+(\d+)\s+R\b")
PDF_OBJECT = re.compile(
    rb"(?ms)^\s*(\d+)\s+(\d+)\s+obj\b(.*?)\bendobj\b"
)


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
    pages: Iterable[int] | None = None,
    source: str | None = None,
) -> dict[str, Any]:
    item: dict[str, Any] = {
        "rule_id": rule_id,
        "severity": severity,
        "category": category,
        "message": message,
        "count": count,
    }
    if pages:
        unique_pages = sorted(set(pages))
        item["pages"] = unique_pages[:MAX_REPORTED_PAGES]
        item["pages_truncated"] = len(unique_pages) > MAX_REPORTED_PAGES
    if source:
        item["source"] = source
    return item


def scan_token_features(data: bytes, source: str) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for rule_id, severity, pattern, message in TOKEN_RULES:
        count = len(re.findall(pattern, data))
        if count:
            results.append(
                finding(
                    rule_id,
                    severity,
                    "pdf_structure",
                    message,
                    count=count,
                    source=source,
                )
            )
    return results


def scan_open_actions(data: bytes, source: str) -> list[dict[str, Any]]:
    """Classify document-open entries without executing or following them.

    An internal destination or ``/S /GoTo`` only selects the initial page/view and
    is informational. Other or unresolved action dictionaries remain blocking.
    This scan is intended for qpdf QDF output, where referenced objects are
    available in a bounded, uncompressed representation.
    """

    occurrences = list(re.finditer(rb"/OpenAction\b", data))
    if not occurrences:
        return []
    objects = {
        (match.group(1), match.group(2)): match.group(3)
        for match in PDF_OBJECT.finditer(data)
    }
    internal_count = 0
    blocking_count = 0
    for occurrence in occurrences:
        tail = data[occurrence.end() : occurrence.end() + 4096].lstrip()
        if tail.startswith(b"["):
            internal_count += 1
            continue
        reference = OPEN_ACTION_REFERENCE.match(tail)
        if reference:
            body = objects.get((reference.group(1), reference.group(2)))
        elif tail.startswith(b"<<"):
            body = tail
        else:
            body = None
        if body is not None and re.search(rb"/S\s*/GoTo\b", body):
            internal_count += 1
        else:
            blocking_count += 1

    results: list[dict[str, Any]] = []
    if internal_count:
        results.append(
            finding(
                "PDF_INTERNAL_OPEN_DESTINATION",
                "INFO",
                "pdf_structure",
                "The document-open entry is an internal GoTo destination.",
                count=internal_count,
                source=source,
            )
        )
    if blocking_count:
        results.append(
            finding(
                "PDF_AUTOMATIC_ACTION",
                "BLOCK",
                "pdf_structure",
                "A document-open action is executable, non-navigation, or unresolved.",
                count=blocking_count,
                source=source,
            )
        )
    return results


def merge_findings(items: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    merged: dict[tuple[str, str, str], dict[str, Any]] = {}
    for item in items:
        key = (item["rule_id"], item["severity"], item["category"])
        current = merged.get(key)
        if current is None:
            current = dict(item)
            if "source" in current:
                current["sources"] = [current.pop("source")]
            merged[key] = current
            continue
        current["count"] = max(current["count"], item.get("count", 1))
        if item.get("source"):
            current.setdefault("sources", []).append(item["source"])
        pages = set(current.get("pages", [])) | set(item.get("pages", []))
        if pages:
            current["pages"] = sorted(pages)[:MAX_REPORTED_PAGES]
            current["pages_truncated"] = (
                current.get("pages_truncated", False)
                or item.get("pages_truncated", False)
                or len(pages) > MAX_REPORTED_PAGES
            )
    for item in merged.values():
        if "sources" in item:
            item["sources"] = sorted(set(item["sources"]))
    return sorted(
        merged.values(),
        key=lambda item: (
            {"BLOCK": 0, "WARN": 1, "INFO": 2}.get(item["severity"], 3),
            item["rule_id"],
        ),
    )


def has_block(findings: Iterable[dict[str, Any]]) -> bool:
    return any(item["severity"] == "BLOCK" for item in findings)


def status_for(findings: Iterable[dict[str, Any]]) -> str:
    severities = {item["severity"] for item in findings}
    if "BLOCK" in severities:
        return "BLOCK"
    if "WARN" in severities:
        return "WARN"
    return "PASS"


def _resource_limiter() -> None:
    try:
        import resource

        resource.setrlimit(resource.RLIMIT_CPU, (20, 20))
        resource.setrlimit(
            resource.RLIMIT_FSIZE,
            (MAX_EXPANDED_BYTES, MAX_EXPANDED_BYTES),
        )
    except (ImportError, OSError, ValueError):
        return


def run_tool(command: list[str], timeout: int = 30) -> dict[str, Any]:
    with tempfile.TemporaryFile() as stdout_file, tempfile.TemporaryFile() as stderr_file:
        try:
            completed = subprocess.run(
                command,
                stdin=subprocess.DEVNULL,
                stdout=stdout_file,
                stderr=stderr_file,
                check=False,
                timeout=timeout,
                env={"LANG": "C", "LC_ALL": "C"},
                start_new_session=True,
                preexec_fn=_resource_limiter if os.name == "posix" else None,
            )
        except subprocess.TimeoutExpired:
            return {
                "returncode": None,
                "timed_out": True,
                "stdout": b"",
                "stderr": b"",
                "output_truncated": False,
            }
        stdout_file.seek(0)
        stderr_file.seek(0)
        stdout = stdout_file.read(MAX_TOOL_OUTPUT_BYTES + 1)
        stderr = stderr_file.read(MAX_TOOL_OUTPUT_BYTES + 1)
    output_truncated = (
        len(stdout) > MAX_TOOL_OUTPUT_BYTES or len(stderr) > MAX_TOOL_OUTPUT_BYTES
    )
    return {
        "returncode": completed.returncode,
        "timed_out": False,
        "stdout": stdout[:MAX_TOOL_OUTPUT_BYTES],
        "stderr": stderr[:MAX_TOOL_OUTPUT_BYTES],
        "output_truncated": output_truncated,
    }


def parse_pdfinfo(output: bytes) -> dict[str, Any]:
    metadata: dict[str, Any] = {}
    text = output.decode("utf-8", errors="replace")
    for line in text.splitlines():
        if ":" not in line:
            continue
        key, value = (part.strip() for part in line.split(":", 1))
        if key == "Pages" and value.isdigit():
            metadata["pages"] = int(value)
        elif key == "Encrypted":
            metadata["encrypted"] = value.lower().startswith("yes")
        elif key == "PDF version":
            metadata["pdf_version"] = value
        elif key == "Page size":
            metadata["page_size_reported"] = value[:160]
    return metadata


def scan_prompt_like_text(text_path: Path) -> tuple[list[dict[str, Any]], dict[str, set[int]]]:
    if text_path.stat().st_size > MAX_TEXT_BYTES:
        return (
            [
                finding(
                    "PDF_TEXT_LAYER_TOO_LARGE",
                    "WARN",
                    "coverage",
                    "The extracted text layer exceeded the bounded scan limit.",
                )
            ],
            {},
        )
    text = text_path.read_text(encoding="utf-8", errors="replace")
    pages = text.split("\f")
    results: list[dict[str, Any]] = []
    rule_pages: dict[str, set[int]] = {}
    for page_number, page_text in enumerate(pages, start=1):
        for rule_id, pattern in PROMPT_RULES:
            matches = list(pattern.finditer(page_text))
            if matches:
                rule_pages.setdefault(rule_id, set()).add(page_number)
    for rule_id, matched_pages in sorted(rule_pages.items()):
        results.append(
            finding(
                rule_id,
                "INFO",
                "prompt_like_text",
                "Instruction-like language appears in the PDF text layer and is treated as untrusted manuscript data.",
                count=len(matched_pages),
                pages=matched_pages,
            )
        )
    if not text.strip():
        results.append(
            finding(
                "PDF_NO_TEXT_LAYER",
                "INFO",
                "coverage",
                "No usable text layer was extracted; there is no text-layer instruction surface to compare.",
            )
        )
    return results, rule_pages


def scan_bbox(bbox_path: Path) -> list[dict[str, Any]]:
    if bbox_path.stat().st_size > MAX_EXPANDED_BYTES:
        return [
            finding(
                "PDF_BBOX_OUTPUT_TOO_LARGE",
                "INFO",
                "coverage",
                "Bounding-box output exceeded the bounded scan limit.",
            )
        ]
    tiny_pages: set[int] = set()
    off_page_pages: set[int] = set()
    tiny_count = 0
    off_page_count = 0
    page_number = 0
    page_width = 0.0
    page_height = 0.0
    try:
        for event, element in ET.iterparse(bbox_path, events=("start", "end")):
            tag = element.tag.rsplit("}", 1)[-1]
            if event == "start" and tag == "page":
                page_number += 1
                page_width = float(element.attrib.get("width", "0"))
                page_height = float(element.attrib.get("height", "0"))
            elif event == "end" and tag == "word":
                x_min = float(element.attrib.get("xMin", "0"))
                y_min = float(element.attrib.get("yMin", "0"))
                x_max = float(element.attrib.get("xMax", "0"))
                y_max = float(element.attrib.get("yMax", "0"))
                if (y_max - y_min) < 1.2 or (x_max - x_min) < 0.2:
                    tiny_count += 1
                    tiny_pages.add(page_number)
                if (
                    x_min < -0.5
                    or y_min < -0.5
                    or x_max > page_width + 0.5
                    or y_max > page_height + 0.5
                ):
                    off_page_count += 1
                    off_page_pages.add(page_number)
                element.clear()
    except (ET.ParseError, OSError, ValueError):
        return [
            finding(
                "PDF_BBOX_PARSE_FAILED",
                "INFO",
                "coverage",
                "Bounding-box output could not be parsed completely.",
            )
        ]
    results: list[dict[str, Any]] = []
    if tiny_count:
        results.append(
            finding(
                "PDF_EXTREMELY_SMALL_TEXT",
                "INFO",
                "text_geometry",
                "Extremely small text-layer boxes were detected.",
                count=tiny_count,
                pages=tiny_pages,
            )
        )
    if off_page_count:
        results.append(
            finding(
                "PDF_OFF_PAGE_TEXT",
                "INFO",
                "text_geometry",
                "Text-layer boxes extend outside the declared page bounds.",
                count=off_page_count,
                pages=off_page_pages,
            )
        )
    return results


def ocr_compare_prompt_pages(
    source: Path,
    rule_pages: dict[str, set[int]],
    temp_root: Path,
    tooling: dict[str, Any],
) -> list[dict[str, Any]]:
    pages = sorted({page for matches in rule_pages.values() for page in matches})
    if not pages:
        return []
    pdftoppm = shutil.which("pdftoppm")
    tesseract = shutil.which("tesseract")
    tooling["pdftoppm"] = {"available": bool(pdftoppm)}
    tooling["tesseract"] = {"available": bool(tesseract)}
    if not pdftoppm or not tesseract:
        return [
            finding(
                "PDF_RENDER_OCR_COMPARISON_UNAVAILABLE",
                "WARN",
                "coverage",
                "Prompt-like text was found, but local render/OCR comparison was unavailable.",
                pages=pages,
            )
        ]
    results: list[dict[str, Any]] = []
    mismatch_by_rule: dict[str, set[int]] = {}
    if len(pages) > MAX_OCR_PAGES:
        results.append(
            finding(
                "PDF_OCR_PAGE_LIMIT_REACHED",
                "WARN",
                "coverage",
                "Prompt-like text occurred on more pages than the bounded OCR comparison permits.",
                count=len(pages),
                pages=pages,
            )
        )
    for page in pages[:MAX_OCR_PAGES]:
        prefix = temp_root / f"render-{page}"
        render_result = run_tool(
            [
                pdftoppm,
                "-f",
                str(page),
                "-l",
                str(page),
                "-singlefile",
                "-r",
                "120",
                "-png",
                str(source),
                str(prefix),
            ],
            timeout=30,
        )
        image_path = prefix.with_suffix(".png")
        if render_result["returncode"] != 0 or not image_path.exists():
            results.append(
                finding(
                    "PDF_PAGE_RENDER_FAILED",
                    "WARN",
                    "coverage",
                    "A page with prompt-like text could not be rendered for comparison.",
                    pages=[page],
                )
            )
            continue
        ocr_result = run_tool([tesseract, str(image_path), "stdout"], timeout=30)
        if ocr_result["returncode"] != 0:
            results.append(
                finding(
                    "PDF_PAGE_OCR_FAILED",
                    "WARN",
                    "coverage",
                    "A rendered page could not be OCR-checked.",
                    pages=[page],
                )
            )
            continue
        ocr_text = ocr_result["stdout"].decode("utf-8", errors="replace")
        for rule_id, pattern in PROMPT_RULES:
            if page in rule_pages.get(rule_id, set()) and not pattern.search(ocr_text):
                mismatch_by_rule.setdefault(rule_id, set()).add(page)
    for rule_id, mismatch_pages in sorted(mismatch_by_rule.items()):
        results.append(
            finding(
                "PDF_TEXT_RENDER_MISMATCH",
                "WARN",
                "visibility_mismatch",
                "Instruction-like text was extracted from the text layer but not recovered from the rendered-page OCR.",
                count=len(mismatch_pages),
                pages=mismatch_pages,
                source=rule_id,
            )
        )
    return results


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
        description="Run a local, non-executing security preflight on an authorized PDF."
    )
    parser.add_argument("pdf", type=Path, help="Authorized source PDF")
    parser.add_argument("--review-id", required=True, help="Stable manuscript review ID")
    parser.add_argument("--output", required=True, type=Path, help="JSON report path")
    parser.add_argument(
        "--authorization-confirmed",
        action="store_true",
        help="Declare that the user and venue authorize this local scan",
    )
    parser.add_argument("--overwrite", action="store_true", help="Replace an existing report")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if not args.authorization_confirmed:
        print(
            "Refusing to read the PDF without --authorization-confirmed.",
            file=sys.stderr,
        )
        return 1
    source = args.pdf.expanduser()
    if source.is_symlink():
        print("Refusing symlink PDF input.", file=sys.stderr)
        return 1
    if not source.is_file():
        print(f"PDF not found: {source}", file=sys.stderr)
        return 1
    size = source.stat().st_size
    if size <= 0 or size > MAX_INPUT_BYTES:
        print("PDF size is empty or exceeds the bounded input limit.", file=sys.stderr)
        return 1
    with source.open("rb") as handle:
        header = handle.read(8)
    if not header.startswith(b"%PDF-"):
        print("Input does not have a PDF file signature.", file=sys.stderr)
        return 1

    tooling: dict[str, Any] = {}
    findings: list[dict[str, Any]] = []
    metadata: dict[str, Any] = {
        "path": str(source.resolve()),
        "size_bytes": size,
        "sha256": sha256_file(source),
    }

    raw_bytes = source.read_bytes()
    findings.extend(scan_token_features(raw_bytes, "raw_pdf"))

    with tempfile.TemporaryDirectory(prefix="pdf-preflight-") as temporary:
        temp_root = Path(temporary)
        qpdf = shutil.which("qpdf")
        tooling["qpdf"] = {"available": bool(qpdf)}
        normalized_path = temp_root / "normalized.pdf"
        if qpdf:
            check = run_tool([qpdf, "--check", str(source)], timeout=30)
            tooling["qpdf"].update(
                {
                    "check_returncode": check["returncode"],
                    "check_timed_out": check["timed_out"],
                }
            )
            if check["timed_out"] or check["returncode"] == 2:
                findings.append(
                    finding(
                        "PDF_QPDF_CHECK_FAILED",
                        "BLOCK",
                        "parser",
                        "qpdf could not safely validate the PDF structure.",
                    )
                )
            elif check["returncode"] not in (0, None):
                findings.append(
                    finding(
                        "PDF_QPDF_CHECK_WARNING",
                        "INFO",
                        "parser",
                        "qpdf reported structural warnings.",
                    )
                )
            normalize = run_tool(
                [
                    qpdf,
                    "--qdf",
                    "--object-streams=disable",
                    "--stream-data=uncompress",
                    str(source),
                    str(normalized_path),
                ],
                timeout=45,
            )
            tooling["qpdf"].update(
                {
                    "normalize_returncode": normalize["returncode"],
                    "normalize_timed_out": normalize["timed_out"],
                }
            )
            if (
                normalize["timed_out"]
                or normalize["returncode"] not in (0, 3)
                or not normalized_path.exists()
                or normalized_path.stat().st_size > MAX_EXPANDED_BYTES
            ):
                findings.append(
                    finding(
                        "PDF_NORMALIZATION_FAILED",
                        "BLOCK",
                        "parser",
                        "The PDF could not be normalized within bounded limits.",
                    )
                )
            else:
                normalized_bytes = normalized_path.read_bytes()
                findings.extend(
                    scan_token_features(normalized_bytes, "qpdf_normalized")
                )
                findings.extend(
                    scan_open_actions(normalized_bytes, "qpdf_normalized")
                )
        else:
            findings.append(
                finding(
                    "PDF_QPDF_UNAVAILABLE",
                    "WARN",
                    "coverage",
                    "qpdf is unavailable; compressed object coverage is incomplete.",
                )
            )

        pdfinfo = shutil.which("pdfinfo")
        tooling["pdfinfo"] = {"available": bool(pdfinfo)}
        if pdfinfo:
            info = run_tool([pdfinfo, str(source)], timeout=30)
            tooling["pdfinfo"].update(
                {"returncode": info["returncode"], "timed_out": info["timed_out"]}
            )
            if info["returncode"] == 0:
                metadata.update(parse_pdfinfo(info["stdout"]))
                if metadata.get("encrypted"):
                    findings.append(
                        finding(
                            "PDF_ENCRYPTED",
                            "BLOCK",
                            "coverage",
                            "The PDF is encrypted; complete preflight coverage is unavailable.",
                        )
                    )
            else:
                findings.append(
                    finding(
                        "PDF_INFO_FAILED",
                        "WARN",
                        "coverage",
                        "PDF metadata inspection failed.",
                    )
                )
        else:
            findings.append(
                finding(
                    "PDFINFO_UNAVAILABLE",
                    "WARN",
                    "coverage",
                    "pdfinfo is unavailable; page and encryption coverage is incomplete.",
                )
            )

        findings = merge_findings(findings)
        if not has_block(findings):
            pdftotext = shutil.which("pdftotext")
            tooling["pdftotext"] = {"available": bool(pdftotext)}
            if pdftotext:
                text_path = temp_root / "text.txt"
                text_result = run_tool(
                    [pdftotext, "-enc", "UTF-8", str(source), str(text_path)],
                    timeout=45,
                )
                tooling["pdftotext"].update(
                    {
                        "text_returncode": text_result["returncode"],
                        "text_timed_out": text_result["timed_out"],
                    }
                )
                rule_pages: dict[str, set[int]] = {}
                if text_result["returncode"] == 0 and text_path.exists():
                    text_findings, rule_pages = scan_prompt_like_text(text_path)
                    findings.extend(text_findings)
                else:
                    findings.append(
                        finding(
                            "PDF_TEXT_EXTRACTION_FAILED",
                            "WARN",
                            "coverage",
                            "The text layer could not be extracted within bounded limits.",
                        )
                    )

                bbox_path = temp_root / "bbox.html"
                bbox_result = run_tool(
                    [pdftotext, "-bbox-layout", str(source), str(bbox_path)],
                    timeout=45,
                )
                tooling["pdftotext"].update(
                    {
                        "bbox_returncode": bbox_result["returncode"],
                        "bbox_timed_out": bbox_result["timed_out"],
                    }
                )
                if bbox_result["returncode"] == 0 and bbox_path.exists():
                    findings.extend(scan_bbox(bbox_path))
                else:
                    findings.append(
                        finding(
                            "PDF_BBOX_EXTRACTION_FAILED",
                            "INFO",
                            "coverage",
                            "Text geometry could not be extracted within bounded limits.",
                        )
                    )
                findings.extend(
                    ocr_compare_prompt_pages(source, rule_pages, temp_root, tooling)
                )
            else:
                findings.append(
                    finding(
                        "PDFTOTEXT_UNAVAILABLE",
                        "WARN",
                        "coverage",
                        "pdftotext is unavailable; text-layer and geometry coverage is incomplete.",
                    )
                )

    findings = merge_findings(findings)
    status = status_for(findings)
    report = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": utc_now(),
        "review_id": args.review_id,
        "status": status,
        "authorization": {
            "confirmed_for_local_scan": True,
            "declared_by_operator": True,
        },
        "source": metadata,
        "summary": {
            "block_findings": sum(item["severity"] == "BLOCK" for item in findings),
            "warning_findings": sum(item["severity"] == "WARN" for item in findings),
            "informational_findings": sum(item["severity"] == "INFO" for item in findings),
        },
        "findings": findings,
        "tooling": tooling,
        "limitations": [
            "This is a bounded heuristic scan, not proof that a PDF is safe or malicious.",
            "Ordinary scholarly discussion may trigger informational instruction-like-language findings.",
            "Passive layout or drawing anomalies are informational unless correlated with a render/text visibility mismatch.",
            "The original PDF remains untrusted after PASS; manuscript text never becomes an instruction source.",
        ],
        "notice": (
            "PASS permits intake; WARN requires documented human clearance; BLOCK stops substantive review."
        ),
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
