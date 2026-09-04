from __future__ import annotations

import importlib.util
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).parents[1]
MODULE_PATH = ROOT / "more-than-peer-review" / "scripts" / "init_review.py"
SPEC = importlib.util.spec_from_file_location("init_review", MODULE_PATH)
assert SPEC and SPEC.loader
INIT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(INIT)


class InitReviewTests(unittest.TestCase):
    def test_initializes_content_free_workspace(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = INIT.initialize(Path(directory) / "reviews", "Review-001")
            self.assertTrue((target / "source").is_dir())
            self.assertTrue((target / "security" / "rendered").is_dir())
            self.assertTrue((target / "venue-rubric.md").is_file())
            self.assertEqual(list((target / "source").iterdir()), [])

    def test_refuses_existing_review(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "reviews"
            INIT.initialize(root, "Review-001")
            with self.assertRaises(INIT.InitError):
                INIT.initialize(root, "Review-001")

    def test_rejects_unsafe_review_id(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(INIT.InitError):
                INIT.initialize(Path(directory) / "reviews", "../escape")


if __name__ == "__main__":
    unittest.main()
