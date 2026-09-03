#!/usr/bin/env python3
"""Validate bounded structure of a submission-ready journal review draft."""

from __future__ import annotations

import argparse
import re
from typing import Any

from _common import (
    ValidationError,
    error_exit,
    issue,
    read_markdown,
    write_json_report,
)


RECOMMENDATIONS = {"Accept", "Minor Revision", "Major Revision", "Reject"}
WORD_RE = re.compile(r"\b[\w'-]+\b", re.UNICODE)
POINT_RE = re.compile(r"(?ms)^\s*(\d+)\.\s+(.*?)(?=^\s*\d+\.\s+|\Z)")
PLACEHOLDER_RE = re.compile(
    r"\{\{[^}]+\}\}|\b(?:TODO|TBD)\b|"
    r"\[(?:Contribution-level|Independent contribution-level|20-40 word|"
    r"Short overall|Write the first|Add an independent|Use as few|Use only when)",
    re.IGNORECASE,
)
STOCK_OPENING_RE = re.compile(
    r"\b(?:addresses|tackles) an important (?:problem|topic)|"
    r"\btimely and (?:important|valuable)|\ba welcome (?:choice|contribution)\b",
    re.IGNORECASE,
)
REQUEST_END_RE = re.compile(
    r"\b(?:please|the authors should|the paper should|"
    r"I encourage the authors to)\b[^.!?]*[.!?]?\s*$",
    re.IGNORECASE,
)
INTERNAL_PROCESS_RE = re.compile(
    r"\b(?:local AI assistance|AI assistance was used|recorded permission|"
    r"policy-compliant disclosure|venue-compliant disclosure|"
    r"accountable-human verification|human verification|"
    r"working draft|optional draft pending|security preflight|"
    r"intake record)\b",
    re.IGNORECASE,
)


def words(text: str) -> int:
    return len(WORD_RE.findall(text))


def sections(markdown: str) -> dict[str, str]:
    found: dict[str, str] = {}
    matches = list(re.finditer(r"(?m)^#\s+(.+?)\s*$", markdown))
    for index, match in enumerate(matches):
        name = match.group(1).strip().lower()
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(markdown)
        found[name] = markdown[start:end].strip()
    return found


def validate(markdown: str) -> dict[str, Any]:
    parsed = sections(markdown)
    errors: list[dict[str, str]] = []
    warnings: list[dict[str, str]] = []

    recommendation_text = parsed.get("recommendation", "")
    author_text = parsed.get("comments to the author(s)", "")
    editor_text = parsed.get("confidential comments to the editor", "")

    normalized = recommendation_text.strip().strip("`").splitlines()[0].strip() \
        if recommendation_text.strip() else ""
    if normalized not in RECOMMENDATIONS:
        errors.append(issue("INVALID_OR_MISSING_RECOMMENDATION", "recommendation"))

    if not author_text:
        errors.append(issue("AUTHOR_COMMENTS_REQUIRED", "comments_to_authors"))

    author_words = words(author_text)
    editor_words = words(editor_text)
    points = list(POINT_RE.finditer(author_text))
    point_word_counts = [words(match.group(2)) for match in points]

    if author_words > 1200:
        errors.append(issue("AUTHOR_WORD_LIMIT_EXCEEDED", "comments_to_authors"))
    if editor_words > 100:
        errors.append(issue("EDITOR_WORD_LIMIT_EXCEEDED", "comments_to_editor"))
    if len(points) > 12:
        errors.append(issue("AUTHOR_POINT_LIMIT_EXCEEDED", "comments_to_authors"))
    if any(count > 180 for count in point_word_counts):
        errors.append(issue("AUTHOR_POINT_WORD_LIMIT_EXCEEDED", "comments_to_authors"))

    if points:
        opening = author_text[: points[0].start()]
        if words(opening) > 150:
            errors.append(issue("OPENING_WORD_LIMIT_EXCEEDED", "comments_to_authors"))
        numbering = [int(match.group(1)) for match in points]
        if numbering != list(range(1, len(numbering) + 1)):
            errors.append(issue("NONSEQUENTIAL_AUTHOR_POINTS", "comments_to_authors"))
    if normalized != "Accept" and len(points) < 3:
        errors.append(
            issue("AUTHOR_POINT_MINIMUM_NOT_MET", "comments_to_authors")
        )
    elif normalized != "Accept" and len(points) == 3:
        warnings.append(
            issue("AUTHOR_POINT_COUNT_DEFAULT_FOUR", "comments_to_authors")
        )
    elif normalized != "Accept" and len(points) > 4:
        warnings.append(issue("AUTHOR_POINT_COUNT_REVIEW", "comments_to_authors"))

    if points and STOCK_OPENING_RE.search(author_text[: points[0].start()]):
        warnings.append(issue("STOCK_OPENING_LANGUAGE_REVIEW", "comments_to_authors"))

    if len(point_word_counts) >= 4:
        mean_words = sum(point_word_counts) / len(point_word_counts)
        if mean_words and max(point_word_counts) - min(point_word_counts) <= 0.35 * mean_words:
            warnings.append(
                issue("UNIFORM_POINT_LENGTH_REVIEW", "comments_to_authors")
            )
        request_endings = sum(
            bool(REQUEST_END_RE.search(match.group(2))) for match in points
        )
        if request_endings / len(points) >= 0.75:
            warnings.append(
                issue("REPETITIVE_REQUEST_ENDINGS_REVIEW", "comments_to_authors")
            )

    if PLACEHOLDER_RE.search(markdown):
        errors.append(issue("UNRESOLVED_PLACEHOLDER", "review"))

    submission_prose = {
        "comments_to_authors": author_text,
        "comments_to_editor": editor_text,
    }
    prohibited_punctuation = {
        "EM_DASH_IN_PROSE": "—",
        "SEMICOLON_IN_PROSE": ";",
        "COLON_IN_PROSE": ":",
    }
    for field, prose in submission_prose.items():
        if INTERNAL_PROCESS_RE.search(prose):
            errors.append(issue("INTERNAL_PROCESS_TEXT_IN_SUBMISSION", field))
        for code, mark in prohibited_punctuation.items():
            if mark in prose:
                errors.append(issue(code, field))

    valid = not errors
    return {
        "schema_version": "1.0",
        "valid": valid,
        "status": "READY_FOR_HUMAN_VERIFICATION" if valid else "BLOCKED",
        "errors": errors,
        "warnings": warnings,
        "counts": {
            "author_words": author_words,
            "editor_words": editor_words,
            "author_points": len(points),
            "author_point_words": point_word_counts,
        },
        "notice": (
            "This validator checks bounded structure only. It does not verify "
            "manuscript facts, scientific merit, tone, or recommendation correctness."
        ),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate a submission-ready journal review without echoing it."
    )
    parser.add_argument("review", help="Submission review Markdown file")
    parser.add_argument("-o", "--output", help="Optional bounded JSON report")
    parser.add_argument(
        "--force", action="store_true", help="Replace an existing output file"
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        report = validate(read_markdown(args.review))
        write_json_report(report, args.output, force=args.force)
        return 0 if report["valid"] else 1
    except ValidationError as exc:
        return error_exit(exc)


if __name__ == "__main__":
    raise SystemExit(main())
