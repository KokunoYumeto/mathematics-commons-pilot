from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class LanguageEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.catalog = json.loads(
            (ROOT / "catalog" / "translations.json").read_text(encoding="utf-8")
        )
        cls.priority = cls.catalog["language_priority"]

    def test_two_unesco_evidence_records_remain_distinct(self) -> None:
        self.assertEqual(
            self.catalog["schema"], "math-commons-translation-catalog/v3"
        )
        education = self.priority["education_access_source"]
        facts = "\n".join(education["reported_facts"])
        self.assertIn("40%", facts)
        self.assertIn("351", facts)
        self.assertIn("7,000", facts)

        study = self.priority["uis_96_language_study"]
        self.assertEqual(study["publisher"], "UNESCO Institute for Statistics")
        self.assertEqual(study["page"], 22)
        self.assertEqual(study["country_count"], 48)
        self.assertEqual(study["alphabetic_language_count"], 96)
        self.assertEqual(
            study["cited_study"]["doi_url"],
            "https://doi.org/10.1038/s41562-024-02028-x",
        )
        self.assertIs(self.priority["unesco_fixed_translation_priority_list"], False)

    def test_cited_study_language_labels_are_exactly_96_unique_rows(self) -> None:
        labels = self.priority["uis_96_language_study"]["language_labels"]
        self.assertEqual(len(labels), 96)
        self.assertEqual(len(set(labels)), 96)
        self.assertEqual(labels[:4], ["French", "Kirundi", "English", "Kiswahili"])
        self.assertEqual(labels[-4:], ["Macedonian", "Kyrgyz", "Russian", "Tajik"])
        self.assertIn("Bahasa", labels)
        self.assertIn("Ŋatoposa", labels)
        self.assertIn("Leb Acöli", labels)


if __name__ == "__main__":
    unittest.main()
