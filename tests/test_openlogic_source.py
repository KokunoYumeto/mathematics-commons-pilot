from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class OpenLogicSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.catalog = json.loads(
            (ROOT / "catalog" / "translations.json").read_text(encoding="utf-8")
        )
        cls.rows = {row["id"]: row for row in cls.catalog["entries"]}

    def test_exact_public_core_source_boundary(self) -> None:
        row = self.rows["openlogic-core"]
        self.assertEqual(row["source_repo"], "OpenLogicProject/OpenLogic")
        self.assertEqual(
            row["source_commit"], "1e960beff9ed7835bf3e3f1335e21af3439cd107"
        )
        self.assertEqual(
            row["source_tree"], "45cad6b3bf0dd96985a7b3d1dc5c343984b0e1c8"
        )
        self.assertEqual(row["license"], "CC BY 4.0")
        self.assertIs(row["derivative_allowed"], True)
        self.assertEqual(row["legacy_id"], "R020")
        self.assertEqual(row["translation_readiness"], "preflight_required")
        self.assertEqual(
            row["source_evidence_status"], "independently_verified_public_boundary"
        )
        self.assertIn("not runnable", row["reported_status"])
        evidence = "\n".join(row["evidence_refs"])
        self.assertIn(
            "5CAF9C104FD864181BE05951028041799AAAA9F3DD52321B678B944D1BE60176",
            evidence,
        )
        self.assertIn(
            "BB5E0179A1E9BDB55634A4303784CF73C297A1DCEE27B92CD546BF398075531C",
            evidence,
        )
        self.assertIn(
            "151BEA19E90E928D718A74C75DCCA8B2439DA5BFE1A4821CF55D9468E9DDC0E2",
            evidence,
        )
        self.assertIn("b46686df0e06f302a7b75a74b379c802f7c7b565", evidence)

    def test_indonesian_snapshot_row_remains_separate_and_unverified(self) -> None:
        row = self.rows["openlogic-indonesian-edition-unresolved"]
        self.assertEqual(row["legacy_id"], "R013")
        self.assertEqual(
            row["title"],
            "Reported Indonesian edition of Open Logic (exact edition unresolved)",
        )
        self.assertEqual(row["known_editions"][0]["language_tag"], "id")
        self.assertEqual(
            row["known_editions"][0]["evidence_status"],
            "non_public_coordination_snapshot",
        )
        self.assertIsNone(row["source_url"])
        self.assertIsNone(row["source_commit"])
        self.assertIsNone(row["license"])
        self.assertIsNone(row["derivative_allowed"])


if __name__ == "__main__":
    unittest.main()
