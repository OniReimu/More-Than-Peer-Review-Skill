#!/usr/bin/env python3
"""Generate a local structured peer-review scaffold for one review ID."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

from _common import ValidationError, error_exit, read_markdown, write_markdown

TEMPLATE_PATH = Path(__file__).resolve().parents[1] / "assets" / "review_scaffold_template.md"
REVIEW_ID_RE = re.compile(r"^[A-Za-z][A-Za-z0-9._-]{0,95}$")


def generate(review_id: str, template_path: Path = TEMPLATE_PATH) -> str:
    if not REVIEW_ID_RE.fullmatch(review_id):
        raise ValidationError("review ID contains unsupported characters")
    rendered = read_markdown(template_path).replace("{{REVIEW_ID}}", review_id)
    if "{{" in rendered or "}}" in rendered:
        raise ValidationError("scaffold template contains unresolved placeholders")
    return rendered


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate a private local Markdown review scaffold.")
    parser.add_argument("review_id", help="Filesystem-safe review identifier")
    parser.add_argument("-o", "--output", required=True, help="Output Markdown path")
    parser.add_argument("--force", action="store_true", help="Replace an existing output file")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        destination = write_markdown(generate(args.review_id), args.output, force=args.force)
        print(f"Created local review scaffold: {destination}")
        return 0
    except ValidationError as exc:
        return error_exit(exc)


if __name__ == "__main__":
    raise SystemExit(main())
