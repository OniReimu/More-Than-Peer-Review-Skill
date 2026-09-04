from __future__ import annotations

import importlib.util
from pathlib import Path
import re
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
        self.assertIn(
            "AUTHOR_POINT_COUNT_DEFAULT_FOUR",
            {item["code"] for item in report["warnings"]},
        )

    def test_non_accept_review_with_fewer_than_three_points_blocks(self) -> None:
        two_point_review = VALID_REVIEW.rsplit("\n3. ", 1)[0]
        report = VALIDATOR.validate(two_point_review)
        self.assertFalse(report["valid"])
        self.assertIn(
            "AUTHOR_POINT_MINIMUM_NOT_MET",
            {item["code"] for item in report["errors"]},
        )

    def test_four_connected_points_match_default(self) -> None:
        review = VALID_REVIEW.replace(
            "# Confidential Comments to the Editor",
            "4. This same mismatch carries into the conclusion, which should be "
            "limited to the population and evidence actually assessed.\n\n"
            "# Confidential Comments to the Editor",
        )
        report = VALIDATOR.validate(review)
        self.assertTrue(report["valid"])
        self.assertNotIn(
            "AUTHOR_POINT_COUNT_DEFAULT_FOUR",
            {item["code"] for item in report["warnings"]},
        )

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

    def test_current_template_placeholders_block(self) -> None:
        template = (
            ROOT
            / "more-than-peer-review"
            / "assets"
            / "submission_review_template.md"
        ).read_text(encoding="utf-8")
        report = VALIDATOR.validate(
            template.replace(
                "`Accept | Minor Revision | Major Revision | Reject`", "Reject"
            )
        )
        self.assertFalse(report["valid"])
        self.assertIn(
            "UNRESOLVED_PLACEHOLDER",
            {item["code"] for item in report["errors"]},
        )

    def test_more_than_twelve_points_blocks(self) -> None:
        points = "\n".join(
            f"{index}. Section {index} contains an independently consequential issue."
            for index in range(1, 14)
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

    def test_each_current_template_placeholder_blocks_on_its_own(self) -> None:
        template = (
            ROOT / "more-than-peer-review" / "assets" / "submission_review_template.md"
        ).read_text(encoding="utf-8")
        for placeholder in re.findall(r"\[[^\]]+\]", template):
            with self.subTest(placeholder=placeholder):
                review = VALID_REVIEW.replace("1. Section 3", placeholder + "\n\n1. Section 3")
                report = VALIDATOR.validate(review)
                self.assertFalse(report["valid"])
                self.assertIn(
                    "UNRESOLVED_PLACEHOLDER",
                    {item["code"] for item in report["errors"]},
                )

    def test_partially_filled_template_without_editor_section_blocks(self) -> None:
        template = (
            ROOT / "more-than-peer-review" / "assets" / "submission_review_template.md"
        ).read_text(encoding="utf-8")
        review = template.replace(
            "`Accept | Minor Revision | Major Revision | Reject`", "Reject"
        ).replace(
            "[Short overall assessment or useful summary in prose.]",
            "The central contribution is not established.",
        ).split("# Confidential Comments to the Editor")[0]
        report = VALIDATOR.validate(review)
        self.assertFalse(report["valid"])
        self.assertIn(
            "UNRESOLVED_PLACEHOLDER", {item["code"] for item in report["errors"]}
        )

    def test_eleven_points_warn_but_remain_structurally_valid(self) -> None:
        points = "\n".join(
            f"{index}. Section {index} contains an independently consequential issue."
            for index in range(1, 12)
        )
        review = (
            "# Recommendation\n\nReject\n\n# Comments to the Author(s)\n\n"
            "The verification rule does not establish the property claimed.\n\n"
            + points
        )
        report = VALIDATOR.validate(review)
        self.assertTrue(report["valid"])
        self.assertIn(
            "AUTHOR_POINT_COUNT_REVIEW",
            {item["code"] for item in report["warnings"]},
        )

    def test_formulaic_review_gets_style_warnings(self) -> None:
        points = "\n\n".join(
            (
                f"{index}. Section {index} reports a synthetic protocol condition "
                "without defining the corresponding state transition. This leaves "
                "the claimed guarantee unsupported. Please clarify this issue."
            )
            for index in range(1, 6)
        )
        review = (
            "# Recommendation\n\nMajor Revision\n\n"
            "# Comments to the Author(s)\n\n"
            "The paper addresses an important problem.\n\n"
            + points
        )
        report = VALIDATOR.validate(review)
        warning_codes = {item["code"] for item in report["warnings"]}
        self.assertTrue(report["valid"])
        self.assertIn("STOCK_OPENING_LANGUAGE_REVIEW", warning_codes)
        self.assertIn("UNIFORM_POINT_LENGTH_REVIEW", warning_codes)
        self.assertIn("REPETITIVE_REQUEST_ENDINGS_REVIEW", warning_codes)

    def test_prohibited_punctuation_blocks_submission_prose(self) -> None:
        replacements = {
            "EM_DASH_IN_PROSE": "The protocol claims safety—its check measures throughput.",
            "SEMICOLON_IN_PROSE": "The protocol claims safety; its check measures throughput.",
            "COLON_IN_PROSE": "The mismatch is direct: the check measures throughput.",
        }
        for expected_code, sentence in replacements.items():
            with self.subTest(expected_code=expected_code):
                review = VALID_REVIEW.replace(
                    "The paper presents a useful framework, but the current evidence does not yet\n"
                    "establish the central generalization claim.",
                    sentence,
                )
                report = VALIDATOR.validate(review)
                self.assertFalse(report["valid"])
                self.assertIn(
                    expected_code,
                    {item["code"] for item in report["errors"]},
                )

    def test_technical_punctuation_preserved_in_both_fields(self) -> None:
        technical_spans = (
            "See https://example.org/data.",
            "See [the artifact](https://example.org/data).",
            "See <https://example.org/data>.",
            r"Equation 2 defines $f: X \to Y$.",
            r"Equation 2 defines \(f: X \to Y\).",
            "Equation 2 states\n$$f: X \\to Y$$\nunder this assumption.",
            r"Equation 2 states \[p(x; \theta)\] under this assumption.",
            "## Evidence:\nThe evidence concerns the stated population.",
        )
        for anchor in ("1. Section 3", "I recommend major revision"):
            for span in technical_spans:
                with self.subTest(anchor=anchor, span=span):
                    review = VALID_REVIEW.replace(anchor, span + "\n\n" + anchor)
                    report = VALIDATOR.validate(review)
                    self.assertTrue(report["valid"], report["errors"])

    def test_surrounding_prose_still_enforces_punctuation(self) -> None:
        cases = (
            ("See https://example.org/data; the split is missing.", "SEMICOLON_IN_PROSE"),
            ("See https://example.org/data: the split is missing.", "COLON_IN_PROSE"),
            ("See https://example.org/data—the split is missing.", "EM_DASH_IN_PROSE"),
            ("[Artifact: source](https://example.org/data)", "COLON_IN_PROSE"),
            (r"The map $f: X \to Y$ is defined; its domain is unclear.", "SEMICOLON_IN_PROSE"),
            (r"Equation 2 contains an unmatched $f: X reference.", "COLON_IN_PROSE"),
            ("The claim is `important: true`.", "COLON_IN_PROSE"),
        )
        for anchor in ("1. Section 3", "I recommend major revision"):
            for sentence, code in cases:
                with self.subTest(anchor=anchor, sentence=sentence):
                    report = VALIDATOR.validate(
                        VALID_REVIEW.replace(anchor, sentence + "\n\n" + anchor)
                    )
                    self.assertFalse(report["valid"])
                    self.assertIn(code, {item["code"] for item in report["errors"]})

    def test_page_and_line_locators_block_submission_prose(self) -> None:
        replacements = {
            "PAGE_LOCATOR_IN_PROSE": "The acceptance rule on page 7 checks only accuracy.",
            "LINE_LOCATOR_IN_PROSE": "The claim in lines 418 to 426 does not follow.",
        }
        for expected_code, sentence in replacements.items():
            with self.subTest(expected_code=expected_code):
                review = VALID_REVIEW.replace(
                    "The paper presents a useful framework, but the current evidence does not yet\n"
                    "establish the central generalization claim.",
                    sentence,
                )
                report = VALIDATOR.validate(review)
                self.assertFalse(report["valid"])
                self.assertIn(
                    expected_code,
                    {item["code"] for item in report["errors"]},
                )

    def test_section_figure_and_table_locators_remain_valid(self) -> None:
        review = VALID_REVIEW.replace(
            "The paper presents a useful framework, but the current evidence does not yet\n"
            "establish the central generalization claim.",
            "Section 4 and Figure 3 use a threshold that conflicts with Table 2.",
        )
        report = VALIDATOR.validate(review)
        self.assertTrue(report["valid"])

    def test_repeated_first_person_scenario_openings_warn(self) -> None:
        points = "\n\n".join(
            (
                f"{index}. Here, I consider a construction in Section {index}. "
                "The stated check accepts it even though the claimed work is absent."
            )
            for index in range(1, 5)
        )
        review = (
            "# Recommendation\n\nMajor Revision\n\n"
            "# Comments to the Author(s)\n\n"
            "The verification rule does not establish the claimed property.\n\n"
            + points
        )
        report = VALIDATOR.validate(review)
        self.assertTrue(report["valid"])
        self.assertIn(
            "REPEATED_FIRST_PERSON_SCENARIO_OPENING_REVIEW",
            {item["code"] for item in report["warnings"]},
        )


if __name__ == "__main__":
    unittest.main()
