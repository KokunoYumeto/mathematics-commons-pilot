from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def object_keys(value: object) -> set[str]:
    keys: set[str] = set()
    if isinstance(value, dict):
        for key, child in value.items():
            keys.add(key)
            keys.update(object_keys(child))
    elif isinstance(value, list):
        for child in value:
            keys.update(object_keys(child))
    return keys


class LanguageEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.catalog = json.loads(
            (ROOT / "catalog" / "translations.json").read_text(encoding="utf-8")
        )
        cls.choices = json.loads(
            (ROOT / "kits" / "translate" / "WORKS.json").read_text(
                encoding="utf-8"
            )
        )
        cls.priority = cls.catalog["language_priority"]

    def test_v7_catalog_has_explicit_semantic_collections(self) -> None:
        self.assertEqual(
            self.catalog["schema"], "math-commons-translation-catalog/v7"
        )
        self.assertEqual(
            self.choices["schema"], "math-commons-translation-choices/v7"
        )
        self.assertEqual(len(self.catalog["topics"]), 10)
        self.assertEqual(len(self.catalog["works"]), 27)
        self.assertEqual(len(self.catalog["resources"]), 12)
        self.assertEqual(
            len(self.catalog["works"]) + len(self.catalog["resources"]), 39
        )
        self.assertEqual(len(self.catalog["source_editions"]), 39)
        self.assertEqual(len(self.catalog["translation_editions"]), 14)
        self.assertEqual(len(self.catalog["jobs"]), 1)
        self.assertEqual(self.catalog["jobs"][0]["state"], "runnable")
        self.assertEqual(len(self.catalog["jobs"][0]["assets"]), 1)

    def test_historical_reports_do_not_claim_current_activity(self) -> None:
        historical = [
            row
            for row in self.catalog["translation_editions"]
            if row["identity_state"] == "unverified_report"
        ]
        self.assertEqual(len(historical), 13)
        self.assertTrue(
            all(
                row["progress_state"].startswith("historical_report_")
                and row["progress_state"].endswith("_at_recording")
                for row in historical
            )
        )
        self.assertFalse(
            any(row["progress_state"] == "reported_active" for row in historical)
        )

    def test_two_unesco_evidence_records_remain_distinct(self) -> None:
        education = self.priority["education_access_source"]
        education_facts = "\n".join(education["reported_facts"])
        self.assertIn("40%", education_facts)
        self.assertIn("351", education_facts)
        self.assertIn("7,000", education_facts)
        self.assertNotIn("alphabetic_language_count", education)

        study = self.priority["uis_96_language_study"]
        self.assertEqual(study["publisher"], "UNESCO Institute for Statistics")
        self.assertEqual(study["page"], 22)
        self.assertEqual(study["country_count"], 48)
        self.assertEqual(study["alphabetic_language_count"], 96)
        self.assertEqual(
            study["cited_study"]["doi_url"],
            "https://doi.org/10.1038/s41562-024-02028-x",
        )
        self.assertEqual(study["cited_study"]["language_table"], "Table S1")
        self.assertNotIn("40%", "\n".join(study["reported_facts"]))
        self.assertIs(self.priority["unesco_fixed_translation_priority_list"], False)
        self.assertIn("distinct evidence", self.priority["note"])

    def test_cited_study_language_labels_are_exactly_96_unique_rows(self) -> None:
        labels = self.priority["uis_96_language_study"]["language_labels"]
        self.assertEqual(len(labels), 96)
        self.assertEqual(len(set(labels)), 96)
        self.assertEqual(labels[:4], ["French", "Kirundi", "English", "Kiswahili"])
        self.assertEqual(labels[-4:], ["Macedonian", "Kyrgyz", "Russian", "Tajik"])
        self.assertIn("Bahasa", labels)
        self.assertIn("Ŋatoposa", labels)
        self.assertIn("Leb Acöli", labels)

    def test_topic_membership_is_an_exact_bidirectional_projection(self) -> None:
        works = {row["id"]: row for row in self.catalog["works"]}
        resources = {row["id"]: row for row in self.catalog["resources"]}
        topic_ids = {row["id"] for row in self.catalog["topics"]}
        work_memberships = {work_id: [] for work_id in works}
        resource_memberships = {resource_id: [] for resource_id in resources}

        for topic in self.catalog["topics"]:
            self.assertEqual(len(topic["work_ids"]), len(set(topic["work_ids"])))
            self.assertEqual(
                len(topic["resource_ids"]), len(set(topic["resource_ids"]))
            )
            for work_id in topic["work_ids"]:
                self.assertIn(work_id, works)
                work_memberships[work_id].append(topic["id"])
            for resource_id in topic["resource_ids"]:
                self.assertIn(resource_id, resources)
                resource_memberships[resource_id].append(topic["id"])

        self.assertEqual(set(work_memberships), set(works))
        self.assertEqual(set(resource_memberships), set(resources))
        for work_id, memberships in work_memberships.items():
            self.assertEqual(memberships, works[work_id]["topic_ids"])
            self.assertEqual(len(memberships), 1)
        for resource_id, memberships in resource_memberships.items():
            self.assertEqual(memberships, resources[resource_id]["topic_ids"])
            self.assertEqual(len(memberships), 1)
        self.assertEqual(
            {
                topic_id
                for row in [*works.values(), *resources.values()]
                for topic_id in row["topic_ids"]
            },
            topic_ids,
        )

    def test_public_catalog_does_not_expose_opaque_legacy_state_fields(self) -> None:
        prohibited = {
            "legacy_id",
            "current_production",
            "current_production_status",
            "production_row",
        }
        self.assertTrue(prohibited.isdisjoint(object_keys(self.catalog)))
        self.assertTrue(prohibited.isdisjoint(object_keys(self.choices)))
        semantic_ids = [
            row["id"]
            for collection in (
                "topics",
                "works",
                "resources",
                "source_editions",
                "translation_editions",
                "jobs",
            )
            for row in self.catalog[collection]
        ]
        self.assertFalse(any(value.startswith(("R00", "O00")) for value in semantic_ids))


if __name__ == "__main__":
    unittest.main()
