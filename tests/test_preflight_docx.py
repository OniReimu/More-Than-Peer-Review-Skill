from __future__ import annotations

import hashlib
import importlib.util
import io
import json
from pathlib import Path
from contextlib import redirect_stdout
import tempfile
import unittest
import zipfile


MODULE_PATH = (
    Path(__file__).parents[1]
    / "more-than-peer-review"
    / "scripts"
    / "preflight_docx.py"
)
SPEC = importlib.util.spec_from_file_location("preflight_docx", MODULE_PATH)
assert SPEC and SPEC.loader
PREFLIGHT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PREFLIGHT)


class PreflightDocxTests(unittest.TestCase):
    @staticmethod
    def write_docx(path: Path, text: str = "Ordinary manuscript text", extras=None) -> None:
        extras = extras or {}
        with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            archive.writestr(
                "[Content_Types].xml",
                "<?xml version='1.0'?><Types xmlns='http://schemas.openxmlformats.org/package/2006/content-types'/>",
            )
            archive.writestr(
                "_rels/.rels",
                "<?xml version='1.0'?><Relationships xmlns='http://schemas.openxmlformats.org/package/2006/relationships'/>",
            )
            archive.writestr(
                "word/document.xml",
                "<?xml version='1.0'?><w:document xmlns:w='http://schemas.openxmlformats.org/wordprocessingml/2006/main'><w:body><w:p><w:r><w:t>"
                + text
                + "</w:t></w:r></w:p></w:body></w:document>",
            )
            for name, value in extras.items():
                archive.writestr(name, value)

    @staticmethod
    def write_pdf_report(path: Path, pdf: Path, review_id: str, status: str = "PASS") -> None:
        digest = hashlib.sha256(pdf.read_bytes()).hexdigest()
        path.write_text(
            json.dumps(
                {
                    "review_id": review_id,
                    "status": status,
                    "source": {"sha256": digest},
                }
            ),
            encoding="utf-8",
        )

    def test_benign_package_passes_package_scan(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "paper.docx"
            self.write_docx(source)
            findings, package, prompt_rules = PREFLIGHT.scan_package(source)
        self.assertEqual(PREFLIGHT.status_for(findings), "PASS")
        self.assertEqual(package["entry_count"], 3)
        self.assertEqual(prompt_rules, {})

    def test_macro_part_blocks(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "paper.docx"
            self.write_docx(source, extras={"word/vbaProject.bin": b"macro"})
            findings, _, _ = PREFLIGHT.scan_package(source)
        self.assertEqual(PREFLIGHT.status_for(findings), "BLOCK")
        self.assertIn("DOCX_VBA_PROJECT", {item["rule_id"] for item in findings})

    def test_external_template_blocks(self) -> None:
        relationships = """<?xml version='1.0'?>
        <Relationships xmlns='http://schemas.openxmlformats.org/package/2006/relationships'>
          <Relationship Id='rId1' Type='http://schemas.openxmlformats.org/officeDocument/2006/relationships/attachedTemplate' Target='https://example.invalid/template.dotm' TargetMode='External'/>
        </Relationships>"""
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "paper.docx"
            self.write_docx(source, extras={"word/_rels/settings.xml.rels": relationships})
            findings, _, _ = PREFLIGHT.scan_package(source)
        self.assertEqual(PREFLIGHT.status_for(findings), "BLOCK")
        self.assertIn(
            "DOCX_UNSAFE_EXTERNAL_RELATIONSHIP",
            {item["rule_id"] for item in findings},
        )

    def test_hidden_prompt_rule_warns_without_render_match(self) -> None:
        source_hits = {"PROMPT_IGNORE_INSTRUCTIONS": {"word/comments.xml"}}
        findings = PREFLIGHT.compare_prompt_rules(source_hits, set())
        self.assertEqual(PREFLIGHT.status_for(findings), "WARN")
        self.assertIn("DOCX_TEXT_RENDER_MISMATCH", {item["rule_id"] for item in findings})
        self.assertNotIn("ignore previous instructions", json.dumps(findings).lower())

    def test_pdf_report_digest_mismatch_blocks(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            pdf = root / "rendered.pdf"
            report = root / "report.json"
            pdf.write_bytes(b"%PDF-1.4\nfirst")
            self.write_pdf_report(report, pdf, "review")
            pdf.write_bytes(b"%PDF-1.4\nchanged")
            findings, _ = PREFLIGHT.validate_pdf_report(report, pdf, "review")
        self.assertEqual(PREFLIGHT.status_for(findings), "BLOCK")
        self.assertIn(
            "DOCX_PDF_REPORT_DIGEST_MISMATCH",
            {item["rule_id"] for item in findings},
        )

    def test_end_to_end_report_contains_no_manuscript_text(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "paper.docx"
            pdf = root / "rendered.pdf"
            pdf_report = root / "pdf-report.json"
            output_report = root / "docx-report.json"
            secret_text = "Ordinary synthetic manuscript sentence"
            self.write_docx(source, secret_text)
            pdf.write_bytes(b"%PDF-1.4\n%%EOF")
            self.write_pdf_report(pdf_report, pdf, "synthetic")
            output = io.StringIO()
            with redirect_stdout(output):
                return_code = PREFLIGHT.main(
                    [
                        str(source),
                        "--review-id",
                        "synthetic",
                        "--rendered-pdf",
                        str(pdf),
                        "--pdf-security-report",
                        str(pdf_report),
                        "--output",
                        str(output_report),
                    ]
                )
            report_text = output_report.read_text(encoding="utf-8")
        self.assertEqual(return_code, 0)
        self.assertNotIn(secret_text, report_text)


if __name__ == "__main__":
    unittest.main()
