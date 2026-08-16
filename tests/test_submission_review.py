from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).parents[1]
SCRIPTS = ROOT / "more-than-peer-review" / "scripts"
sys.path.insert(0, str(SCRIPTS))
SPEC = importlib.util.spec_from_file_location(
    "validate_submission_review", SCRIPTS / "validate_submission_review.py"
)
assert SPEC and SPEC.loader
VALIDATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATOR)


VALID_REVIEW = """# Recommendation

Major Revision

# Comments to the Author(s)

The paper presents a useful framework, but the current evidence does not yet
establish the central generalization claim.

1. Section 3 defines the target population inconsistently with Table 1. This changes
the estimand and must be reconciled before the main effect can be interpreted.

2. Table 2 reports only point estimates from one split. Add repeated paired estimates
and compatible uncertainty intervals for the principal comparisons.

3. Section 5 omits preprocessing parameters and seeds. Provide the configuration,
environment, and immutable split identifiers needed to reproduce the reported run.

# Confidential Comments to the Editor

I recommend major revision because the estimand mismatch and single-split evaluation
currently limit the central claim. Both concerns are disclosed to the authors and
appear addressable through a corrected analysis and reproducibility record.
"""


class SubmissionReviewTests(unittest.TestCase):
    def test_valid_review_passes(self) -> None:
        report = VALIDATOR.validate(VALID_REVIEW)
        self.assertTrue(report["valid"])
        self.assertEqual(report["counts"]["author_points"], 3)

    def test_template_placeholders_block(self) -> None:
        report = VALIDATOR.validate(
            VALID_REVIEW.replace(
                "The paper presents a useful framework, but the current evidence does not yet\n"
                "establish the central generalization claim.",
                "[20-40 word contribution-level opening assessment.]",
            )
        )
        self.assertFalse(report["valid"])
        self.assertIn(
            "UNRESOLVED_PLACEHOLDER",
            {item["code"] for item in report["errors"]},
        )

    def test_more_than_eight_points_blocks(self) -> None:
        points = "\n".join(
            f"{index}. Section {index} contains an independently consequential issue."
            for index in range(1, 10)
        )
        review = (
            "# Recommendation\n\nReject\n\n# Comments to the Author(s)\n\n"
            "The central contribution is not established.\n\n"
            + points
        )
        report = VALIDATOR.validate(review)
        self.assertFalse(report["valid"])
        self.assertIn(
            "AUTHOR_POINT_LIMIT_EXCEEDED",
            {item["code"] for item in report["errors"]},
        )


if __name__ == "__main__":
    unittest.main()
