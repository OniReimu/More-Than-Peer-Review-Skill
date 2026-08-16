from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).parents[1]
SKILL = ROOT / "more-than-peer-review"
SCRIPTS = SKILL / "scripts"
sys.path.insert(0, str(SCRIPTS))
SPEC = importlib.util.spec_from_file_location(
    "validate_review_intake", SCRIPTS / "validate_review_intake.py"
)
assert SPEC and SPEC.loader
INTAKE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(INTAKE)


class ReviewIntakeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.template = json.loads(
            (SKILL / "assets" / "review_intake_template.json").read_text("utf-8")
        )

    def approved(self) -> dict:
        payload = copy.deepcopy(self.template)
        payload["authorization"].update(
            basis="journal_invitation",
            documented=True,
            local_processing_authorized=True,
            external_processing_authorized=False,
        )
        payload["reviewer"].update(
            capacity="assigned_reviewer",
            human_accountable=True,
            competence_areas=["machine_learning"],
            conflict_status="none_identified",
            conflicts=[],
        )
        payload["venue_policy"].update(
            checked=True,
            peer_review_model="double_anonymized",
        )
        payload["ai_use"].update(
            policy="permitted_with_disclosure",
            planned="approved_ai_assistance",
            permission_confirmed=True,
            disclosure_planned=True,
        )
        payload["handling"].update(
            local_only=True,
            external_service_use=False,
            data_reuse_permitted=False,
            deletion_or_retention_record_planned=True,
        )
        payload["scope"].update(
            manuscript_type="research_article",
            requested_focus=["methods", "statistics", "reporting"],
        )
        return payload

    def test_default_template_is_blocked(self) -> None:
        report = INTAKE.validate_intake(copy.deepcopy(self.template))
        self.assertFalse(report["valid"])
        self.assertEqual(report["status"], "BLOCKED")

    def test_explicitly_approved_local_ai_intake_passes(self) -> None:
        report = INTAKE.validate_intake(self.approved())
        self.assertTrue(report["valid"])
        self.assertEqual(report["status"], "READY_FOR_LOCAL_REVIEW")

    def test_ai_permission_cannot_default_to_false(self) -> None:
        payload = self.approved()
        payload["ai_use"]["permission_confirmed"] = False
        report = INTAKE.validate_intake(payload)
        self.assertFalse(report["valid"])
        self.assertIn(
            "AI_PERMISSION_NOT_CONFIRMED",
            {item["code"] for item in report["errors"]},
        )


if __name__ == "__main__":
    unittest.main()
