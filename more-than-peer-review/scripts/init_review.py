#!/usr/bin/env python3
"""Create an isolated, content-free review workspace from bundled templates."""

from __future__ import annotations

import argparse
import json
import re
import shutil
from pathlib import Path


REVIEW_ID_RE = re.compile(r"^[A-Za-z][A-Za-z0-9._-]{0,95}$")
SKILL_ROOT = Path(__file__).resolve().parents[1]
ASSETS = SKILL_ROOT / "assets"


class InitError(ValueError):
    """A deterministic, user-correctable initialization error."""


def initialize(root: Path, review_id: str) -> Path:
    if not REVIEW_ID_RE.fullmatch(review_id):
        raise InitError(
            "review ID must start with a letter and contain only letters, digits, "
            "dots, underscores, or hyphens"
        )
    if root.is_symlink():
        raise InitError(f"review root must not be a symlink: {root}")
    root.mkdir(parents=True, exist_ok=True)
    resolved_root = root.resolve(strict=True)
    if not resolved_root.is_dir():
        raise InitError(f"review root is not a directory: {resolved_root}")

    target = resolved_root / review_id
    if target.exists() or target.is_symlink():
        raise InitError(f"review directory already exists: {target}")

    (target / "source").mkdir(parents=True)
    (target / "security" / "rendered").mkdir(parents=True)

    intake = json.loads((ASSETS / "review_intake_template.json").read_text("utf-8"))
    intake["review_id"] = review_id
    (target / "review_intake.json").write_text(
        json.dumps(intake, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    copies = {
        "venue_rubric_template.md": "venue-rubric.md",
        "study_profile_template.json": "study_profile.json",
        "claim_evidence_matrix_template.csv": "claim_evidence_matrix.csv",
        "statistical_reproducibility_template.json":
            "statistics_reproducibility.json",
    }
    for source_name, destination_name in copies.items():
        shutil.copyfile(ASSETS / source_name, target / destination_name)
    return target


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Create a new content-free local review workspace."
    )
    parser.add_argument("review_id", help="Filesystem-safe review identifier")
    parser.add_argument(
        "--root", default="reviews", help="Review archive root (default: reviews)"
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        destination = initialize(Path(args.root).expanduser(), args.review_id)
        print(f"Created review workspace: {destination}")
        return 0
    except (InitError, OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
