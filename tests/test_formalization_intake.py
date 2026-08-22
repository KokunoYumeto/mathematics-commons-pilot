from __future__ import annotations

import copy
import importlib.util
import sys
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
SPEC = importlib.util.spec_from_file_location(
    "validate_jobs", ROOT / "tools" / "validate_jobs.py"
)
assert SPEC is not None and SPEC.loader is not None
validate_jobs = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validate_jobs)


class FormalizationIntakeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.catalog, _ = validate_jobs.load(ROOT / "catalog" / "formalize.json")
        errors: list[str] = []
        cls.count = validate_jobs.validate_formalization(errors)
        if errors:
            raise AssertionError(errors)

    def mutation_errors(self, catalog: dict) -> list[str]:
        original_load = validate_jobs.load

        def patched_load(path: Path):
            if Path(path) == ROOT / "catalog" / "formalize.json":
                return catalog, b"mutation"
            return original_load(path)

        errors: list[str] = []
        with mock.patch.object(validate_jobs, "load", side_effect=patched_load):
            validate_jobs.validate_formalization(errors)
        return errors

    def test_catalog_is_scaffold_not_release(self) -> None:
        self.assertEqual(self.count, 19)
        self.assertEqual(self.catalog["status"], "scaffold")
        self.assertEqual(self.catalog["summary"]["runnable_packets"], 0)
        self.assertEqual(self.catalog["summary"]["statement_reviews_complete"], 0)
        self.assertEqual(self.catalog["summary"]["mathlib_audits_complete"], 0)
        self.assertTrue(
            all(row["packet"]["state"] == "not_started" for row in self.catalog["items"])
        )

    def test_exact_external_source_snapshots(self) -> None:
        sources = {row["id"]: row for row in self.catalog["sources"]}
        lean = sources["lean-theorems-1-6cf9ce4"]
        self.assertEqual(
            lean["snapshot"]["commit"],
            "6cf9ce44c1a8281699fa2f3128a764e0c347e7f6",
        )
        self.assertEqual(
            lean["snapshot"]["tree"],
            "eee97092915b388bf4b30bcdf60c5ad2201af133",
        )
        self.assertEqual(lean["inventory"]["files"], 36)
        self.assertEqual(lean["inventory"]["bytes"], 592_129)
        self.assertEqual(lean["inventory"]["lean_files"], 30)
        self.assertEqual(lean["build"]["scope"], "default_targets")
        self.assertEqual(lean["build"]["compiled_files"], 29)
        self.assertEqual(lean["build"]["placeholders"]["count"], 4)

        current = sources["lean-theorems-1-4fce53c"]
        self.assertEqual(
            current["snapshot"]["commit"],
            "4fce53cf5e0be46bfc12e633e2a4924102f12bd8",
        )
        self.assertEqual(
            current["snapshot"]["tree"],
            "99c6732878a3f9ae34bc3bb607b5c202e824e59a",
        )
        self.assertEqual(current["inventory"]["files"], 36)
        self.assertEqual(current["inventory"]["bytes"], 635_125)
        self.assertEqual(current["inventory"]["archive"]["bytes"], 162_915)
        self.assertEqual(
            current["inventory"]["archive"]["sha256"],
            "1D770EFC0A8E6B4EB7B8C27FE37551F426ECF5636B7864C6F5152DDB9C1BA2B1",
        )
        self.assertEqual(current["build"]["state"], "not_run")
        self.assertEqual(current["build"]["compiled_files"], 0)
        self.assertEqual(current["build"]["placeholders"]["count"], 6)

        sidecars = sources["zenodo-21129946"]
        self.assertEqual(sidecars["snapshot"]["doi"], "10.5281/zenodo.21129946")
        self.assertEqual(sidecars["inventory"]["archive"]["bytes"], 9_834)
        self.assertEqual(
            sidecars["inventory"]["archive"]["sha256"],
            "E9E494210774F814505CEC76F5AA5F2D6C8309EC46EA8B1A70CB77B070691FA9",
        )
        self.assertEqual(sidecars["build"]["scope"], "selected_files")
        self.assertEqual(sidecars["build"]["placeholders"]["count"], 0)

    def test_desargues_and_s_named_intake_are_explicit(self) -> None:
        items = {row["id"]: row for row in self.catalog["items"]}
        self.assertEqual(items["desargues-vector"]["intake_state"], "review_candidate")
        self.assertEqual(items["desargues-projective"]["placeholder_relation"], "affected")
        expected = {
            "sylvester-gallai",
            "schur-sum-free",
            "sperner-1d-2d",
            "sperner-3d",
            "erdos-szekeres",
            "sarkaria-tverberg",
            "sos-friendship",
            "sos-windmill",
            "szekely-crossing",
            "szemeredi-trotter",
            "schoenberg-cauchy-arm",
            "suk-erdos-szekeres-lead",
            "szekeres-peters-lead",
            "steinitz-perfect-ring",
        }
        self.assertTrue(expected.issubset(items))
        self.assertEqual(
            items["sos-windmill"]["source_path"],
            "Formalization/FriendshipWindmill.lean",
        )
        self.assertEqual(
            items["suk-erdos-szekeres-lead"]["source_path"],
            "Formalization/ErdosSzekeresConvex.lean",
        )

    def test_fail_closed_semantic_mutations(self) -> None:
        mutations: list[tuple[str, dict]] = []

        wrong_summary = copy.deepcopy(self.catalog)
        wrong_summary["summary"]["items"] = 999
        mutations.append(("summary", wrong_summary))

        duplicate_source = copy.deepcopy(self.catalog)
        duplicate_source["sources"][1]["id"] = duplicate_source["sources"][0]["id"]
        mutations.append(("source IDs", duplicate_source))

        unsafe_path = copy.deepcopy(self.catalog)
        unsafe_path["items"][0]["source_path"] = "../../secret"
        mutations.append(("source path", unsafe_path))

        bad_command = copy.deepcopy(self.catalog)
        bad_command["sources"][0]["build"]["commands"][0]["exit_code"] = 99
        mutations.append(("passing command exit", bad_command))

        bad_placeholder_count = copy.deepcopy(self.catalog)
        bad_placeholder_count["sources"][0]["build"]["placeholders"]["count"] = 0
        mutations.append(("placeholders count", bad_placeholder_count))

        bad_citation = copy.deepcopy(self.catalog)
        next(
            row for row in bad_citation["items"] if row["id"] == "suk-erdos-szekeres-lead"
        )["declarations"] = ["invented"]
        mutations.append(("citation-only boundary", bad_citation))

        bad_runnable = copy.deepcopy(self.catalog)
        bad_runnable["items"][0]["packet"]["state"] = "runnable"
        mutations.append(("runnable admission gate", bad_runnable))

        for expected_error, mutated in mutations:
            with self.subTest(expected_error=expected_error):
                self.assertTrue(
                    any(expected_error in error for error in self.mutation_errors(mutated))
                )


if __name__ == "__main__":
    unittest.main()
