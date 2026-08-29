from __future__ import annotations

import json
import unittest
from pathlib import Path

import sys


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from validate_packets import (  # noqa: E402
    SchemaDocument,
    SchemaSet,
    iter_schema_nodes,
    lint_schema,
    validate_instance,
)


class EducationTranslationCatalogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.catalog_path = ROOT / "catalog" / "edu.json"
        cls.schema_path = ROOT / "schemas" / "edu.schema.json"
        cls.catalog = json.loads(cls.catalog_path.read_text(encoding="utf-8"))
        cls.schema = json.loads(cls.schema_path.read_text(encoding="utf-8"))

    def test_catalog_is_schema_valid(self) -> None:
        document = SchemaDocument(path=self.schema_path, body=self.schema)
        schema_set = SchemaSet([document])
        errors = lint_schema(document)
        for _, node in iter_schema_nodes(document.body):
            if isinstance(node, dict) and isinstance(node.get("$ref"), str):
                try:
                    schema_set.resolve(node["$ref"], document)
                except ValueError as exc:
                    errors.append(str(exc))
        errors.extend(
            validate_instance(self.catalog, document.body, schema_set, document)
        )
        self.assertEqual(errors, [])

    def test_language_access_lineage_is_not_conflated(self) -> None:
        access = self.catalog["language_access"]
        walter = access["walter_benson_2012"]
        self.assertEqual(walter["languages_over_ten_million"], 97)
        self.assertEqual(walter["used_in_education_over_ten_million"], 52)
        self.assertEqual(walter["not_used_in_education_over_ten_million"], 45)
        self.assertAlmostEqual(
            walter["population_not_used_in_education_all_bands"]
            / (
                walter["population_used_in_education_all_bands"]
                + walter["population_not_used_in_education_all_bands"]
            )
            * 100,
            walter["population_without_first_language_access_percent_rounded"],
            places=3,
        )
        self.assertEqual(
            access["separate_96_language_study"]["relationship"],
            "unrelated_sample",
        )
        self.assertEqual(walter["chapter_pages"], "278-300")
        self.assertEqual(walter["evidence_pages"], "282-283")
        self.assertIn("rounded to three decimals", walter["calculation_note"])
        self.assertIn("not a named list", walter["limitation"])

    def test_material_and_workflow_keys_are_unique_and_ordered(self) -> None:
        material_ids = [row["id"] for row in self.catalog["materials"]]
        self.assertEqual(len(material_ids), len(set(material_ids)))
        steps = [row["step"] for row in self.catalog["workflow"]]
        self.assertEqual(steps, [1, 2, 3, 4, 5, 6])

    def test_indonesian_program_has_exact_forty_role_partition(self) -> None:
        program = self.catalog["indonesian_program"]
        works = program["works"]
        ids = [row["id"] for row in works]
        self.assertEqual(len(works), 40)
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(
            ids,
            [
                "prealgebra",
                "elementary-algebra",
                "intermediate-algebra",
                "precalculus",
                "discrete-mathematics",
                "differential-calculus",
                "integral-calculus",
                "linear-algebra",
                "multivariable-calculus",
                "vector-calculus",
                "ordinary-differential-equations",
                "mathematical-computing",
                "probability",
                "applied-statistics",
                "real-analysis-1",
                "real-analysis-2",
                "abstract-algebra-1",
                "abstract-algebra-2",
                "complex-analysis",
                "number-theory",
                "applied-combinatorics",
                "mathematical-logic",
                "point-set-topology",
                "foundations-of-geometry",
                "numerical-analysis",
                "mathematical-modeling",
                "mathematical-programming",
                "mathematical-statistics",
                "measure-theory",
                "functional-analysis",
                "stochastic-processes",
                "partial-differential-equations",
                "smooth-manifolds",
                "algebraic-topology",
                "graduate-algebra",
                "category-homological-algebra",
                "advanced-optimization",
                "algebraic-geometry",
                "mathematics-in-lean",
                "research-practice",
            ],
        )
        source_project_ids = [row["source_project_id"] for row in works]
        self.assertEqual(len(source_project_ids), len(set(source_project_ids)))
        self.assertEqual(
            sum(row["state"] == "complete_public" for row in works), 21
        )
        self.assertEqual(
            sum(row["state"] == "active_or_partial" for row in works), 19
        )
        self.assertEqual(
            program["complete_public_role_count"]
            + program["active_or_partial_role_count"],
            program["role_count"],
        )
        complete_ids = {
            row["id"] for row in works if row["state"] == "complete_public"
        }
        shared_groups = program["shared_complete_public_editions"]
        shared_roles = [role for group in shared_groups for role in group["roles"]]
        self.assertEqual(len(shared_roles), len(set(shared_roles)))
        self.assertTrue(set(shared_roles) <= complete_ids)
        derived_editions = len(complete_ids) - sum(
            len(group["roles"]) - 1 for group in shared_groups
        )
        self.assertEqual(program["complete_public_edition_count"], 20)
        self.assertEqual(program["complete_public_edition_count"], derived_editions)
        self.assertEqual(
            set(program["stale_detail_source_project_ids"]),
            {
                "A20",
                "A30",
                "B30",
                "B50",
                "B95",
                "C10",
                "C90",
                "C100",
                "C140",
                "D10",
                "D30",
                "D50",
                "D70",
                "D100",
            },
        )
        self.assertTrue(
            set(program["stale_detail_source_project_ids"])
            <= {row["source_project_id"] for row in works}
        )

    def test_public_source_and_report_identities_are_exact(self) -> None:
        program = self.catalog["indonesian_program"]
        self.assertEqual(
            program["source_commit"],
            "a0d6ebb1f7143f0478d538944d57f4ec7bab9775",
        )
        self.assertIn(program["source_commit"], program["raw_catalog"])
        self.assertEqual(program["raw_catalog_bytes"], 60649)
        self.assertEqual(
            program["raw_catalog_sha256"],
            "A2DA8A4165326DC64ACB5DDD9B1BC227980D48B5E28928D927EC35C1CBC001A5",
        )

        report = self.catalog["research_report"]
        self.assertEqual(report["pages"], 87)
        self.assertEqual(report["pdf_bytes"], 2089824)
        self.assertEqual(
            report["pdf_sha256"],
            "74F2BC8AD9CBC2B7BFB9CFAF95D6162F38BBE35306B7909CA73A741E2565193B",
        )
        self.assertEqual(report["version_doi"], "10.5281/zenodo.22103007")

    def test_wikiversity_example_preserves_scope(self) -> None:
        example = self.catalog["highlighted_example"]
        self.assertEqual(example["source_lectures"], 30)
        self.assertEqual(example["source_worksheets"], 30)
        self.assertEqual(example["volume_state"], "complete_public")
        self.assertEqual(example["larger_bridge_state"], "active_or_partial")
        self.assertIn("wikiversity", example["source_url"].lower())
        self.assertIn("2012", example["source_url_2012"])


if __name__ == "__main__":
    unittest.main()
