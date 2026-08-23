from __future__ import annotations

import copy
import importlib.util
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
SPEC = importlib.util.spec_from_file_location(
    "validate_jobs_openlogic", ROOT / "tools" / "validate_jobs.py"
)
assert SPEC is not None and SPEC.loader is not None
validate_jobs = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validate_jobs)
OPENLOGIC_COMMIT = "1e960beff9ed7835bf3e3f1335e21af3439cd107"
OPENLOGIC_TREE = "45cad6b3bf0dd96985a7b3d1dc5c343984b0e1c8"


class OpenLogicSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.catalog = json.loads(
            (ROOT / "catalog" / "translations.json").read_text(encoding="utf-8")
        )
        cls.works = {row["id"]: row for row in cls.catalog["works"]}
        cls.sources = {row["id"]: row for row in cls.catalog["source_editions"]}
        cls.editions = {
            row["id"]: row for row in cls.catalog["translation_editions"]
        }
        cls.jobs = {row["id"]: row for row in cls.catalog["jobs"]}
        cls.packet_source = json.loads(
            (ROOT / "kits" / "openlogic" / "SOURCE.json").read_text(
                encoding="utf-8"
            )
        )
        cls.asset_manifest = json.loads(
            (ROOT / "catalog" / "assets" / "openlogic.json").read_text(
                encoding="utf-8"
            )
        )
        cls.build_receipt = json.loads(
            (ROOT / "catalog" / "receipts" / "openlogic.json").read_text(
                encoding="utf-8"
            )
        )
        cls.public_readback = json.loads(
            (ROOT / "catalog" / "openlogic-rb.json").read_text(encoding="utf-8")
        )

    def test_exact_public_root_source_and_rights_boundary(self) -> None:
        work = self.works["openlogic-core"]
        source = self.sources["openlogic-core-source"]
        self.assertEqual(work["title"], "Open Logic Text")
        self.assertEqual(work["kind"], "source_project")
        self.assertEqual(work["source_edition_ids"], ["openlogic-core-source"])

        self.assertEqual(source["item_id"], "openlogic-core")
        self.assertEqual(source["item_type"], "work")
        self.assertEqual(source["identity_state"], "frozen")
        self.assertEqual(source["locator"]["repository"], "OpenLogicProject/OpenLogic")
        self.assertEqual(source["locator"]["commit"], OPENLOGIC_COMMIT)
        self.assertEqual(source["locator"]["tree"], OPENLOGIC_TREE)
        self.assertIsNone(source["locator"]["archive"])
        self.assertEqual(source["rights"]["state"], "verified_translation_allowed")
        self.assertEqual(source["rights"]["work_license"]["name"], "CC BY 4.0")
        self.assertEqual(
            source["rights"]["work_license"]["url"],
            "https://creativecommons.org/licenses/by/4.0/",
        )
        self.assertIs(source["rights"]["derivative_translation_allowed"], True)
        self.assertEqual(
            {row["path"] for row in source["rights"]["component_notices"]},
            {"sty/bussproofs-extra.sty", "bib/natbib-oup.bst", "NOTICE.md"},
        )

    def test_all_source_evidence_checks_pass_and_job_is_runnable(self) -> None:
        source = self.sources["openlogic-core-source"]
        self.assertEqual(
            set(source["evidence_checks"]),
            {
                "work_identity",
                "source_edition_identity",
                "immutable_source",
                "translation_permission",
                "component_rights",
                "editable_source",
                "baseline_build",
            },
        )
        self.assertEqual(
            {gate["state"] for gate in source["evidence_checks"].values()}, {"pass"}
        )
        self.assertTrue(
            all(gate["evidence_ids"] for gate in source["evidence_checks"].values())
        )
        self.assertEqual(source["readiness"], "runnable")

        job = self.jobs["openlogic-v1"]
        self.assertEqual(job["work_id"], "openlogic-core")
        self.assertEqual(job["source_edition_id"], "openlogic-core-source")
        self.assertEqual(job["target_mode"], "contributor_selects")
        self.assertEqual(job["state"], "runnable")
        self.assertEqual(
            job["assets"],
            [
                {
                    "name": "openlogic-v1.zip",
                    "bytes": 1_921_531,
                    "sha256": "C91EFD16C6DCF22DAEAFDBDC7F544A9E07C9B9C3BA04CE000BFCD933B52E9B8A",
                    "url": "https://github.com/KokunoYumeto/mathematics-commons-pilot/releases/download/translate-openlogic-v1/openlogic-v1.zip",
                }
            ],
        )
        self.assertEqual(job["asset_manifest"], "catalog/assets/openlogic.json")
        self.assertEqual(job["source_receipt"], "catalog/receipts/openlogic.json")
        self.assertEqual(
            job["public_readback"],
            {
                "receipt": "catalog/openlogic-rb.json",
                "observed_date": "2026-08-22",
                "assets": job["assets"],
            },
        )
        self.assertEqual(job["start_files"], {"local": "LOCAL.md", "web": "WEB.md"})

    def test_release_manifest_receipt_and_anonymous_readback_bind_the_same_asset(self) -> None:
        identity = {
            "name": "openlogic-v1.zip",
            "bytes": 1_921_531,
            "sha256": "C91EFD16C6DCF22DAEAFDBDC7F544A9E07C9B9C3BA04CE000BFCD933B52E9B8A",
        }
        manifest_asset = self.asset_manifest["assets"][0]
        self.assertEqual(self.asset_manifest["job_id"], "openlogic-v1")
        self.assertEqual(self.asset_manifest["source_files"], 807)
        self.assertEqual(self.asset_manifest["source_bytes"], 4_562_041)
        self.assertEqual(
            {
                "name": manifest_asset["name"],
                "bytes": manifest_asset["zip_bytes"],
                "sha256": manifest_asset["zip_sha256"],
            },
            identity,
        )

        self.assertEqual(self.build_receipt["schema"], "math-commons-translation-build/v1")
        self.assertEqual(self.build_receipt["job_id"], "openlogic-v1")
        self.assertEqual(
            self.build_receipt["packet_binding"]["packet_zip"],
            {**identity, "members": 807},
        )
        manifest_identity = validate_jobs.input_identity(
            ROOT / "catalog" / "assets" / "openlogic.json"
        )
        self.assertEqual(
            self.build_receipt["packet_binding"]["asset_manifest"],
            {
                "name": "openlogic.json",
                "bytes": manifest_identity["bytes"],
                "sha256": manifest_identity["sha256"],
            },
        )
        self.assertEqual(self.build_receipt["input_closure"]["all_closed"], True)
        self.assertEqual(self.build_receipt["input_closure"]["excluded_doc_inputs"], 0)
        self.assertEqual(
            self.build_receipt["input_closure"]["unbound_repo_relative_inputs"], 0
        )

        readback = self.public_readback
        self.assertEqual(readback["schema"], "math-commons-portal-readback/v1")
        self.assertEqual(readback["status"], "PASS")
        self.assertEqual(readback["release"]["tag"], "translate-openlogic-v1")
        self.assertEqual(
            readback["transport"],
            {
                "method": "anonymous_https_and_git",
                "authorization": False,
                "cookies": False,
                "payload_persisted": False,
            },
        )
        self.assertEqual(
            readback["assets"],
            [
                {
                    "id": None,
                    "name": identity["name"],
                    "url": "https://github.com/KokunoYumeto/mathematics-commons-pilot/releases/download/translate-openlogic-v1/openlogic-v1.zip",
                    "expected_bytes": identity["bytes"],
                    "observed_bytes": identity["bytes"],
                    "expected_sha256": identity["sha256"],
                    "observed_sha256": identity["sha256"],
                    "match": True,
                }
            ],
        )
        self.assertEqual(
            readback["summary"],
            {
                "assets": 1,
                "bytes": identity["bytes"],
                "matches": 1,
                "mismatches": 0,
                "errors": [],
            },
        )

    def test_packet_source_state_matches_the_exact_git_object_boundary(self) -> None:
        state = self.packet_source
        self.assertEqual(state["schema"], "math-commons-translation-source/v4")
        self.assertEqual(state["state"], "awaiting_target_selection")
        self.assertEqual(state["work"]["work_id"], "openlogic-core")
        self.assertEqual(state["work"]["source_language"], "English")
        self.assertIsNone(state["target"]["language"])
        self.assertIsNone(state["target"]["language_tag"])
        self.assertEqual(state["source"]["commit"], OPENLOGIC_COMMIT)
        self.assertEqual(state["source"]["tree"], OPENLOGIC_TREE)
        self.assertEqual(state["source"]["files"], 792)
        self.assertEqual(state["source"]["bytes"], 4_302_140)
        self.assertEqual(state["source"]["tree_receipt"], "SOURCE_TREE.tsv")
        self.assertEqual(state["source"]["immutable_path"], "source")
        self.assertEqual(state["rights"]["work_license"], "CC BY 4.0")
        self.assertIs(state["rights"]["derivative_translation_allowed"], True)

    def test_portuguese_row_is_a_conservative_unbound_public_relationship(self) -> None:
        row = self.editions["openlogic-pt-openlogicpt"]
        self.assertEqual(row["work_id"], "openlogic-core")
        self.assertIsNone(row["source_edition_id"])
        self.assertEqual(row["identity_state"], "public_repository_verified")
        self.assertEqual(row["target_language"]["tag"], "pt")
        self.assertEqual(row["target_language"]["name"], "Portuguese")
        self.assertIsNone(row["target_language"]["locale"])
        self.assertIsNone(row["target_language"]["script"])
        self.assertIsNone(row["target_language"]["orthographic_standard"])
        self.assertEqual(row["progress_state"], "repository_available")
        self.assertEqual(row["review_state"], "not_independently_assessed")
        self.assertIn("not independently established", row["scope_note"])
        self.assertEqual(row["evidence"]["status"], "public_repository_identity_verified")
        self.assertEqual(
            row["evidence"]["commit"],
            "51c227190f56bae45d19a85747fc031de430bd3c",
        )
        self.assertEqual(
            row["evidence"]["tree"],
            "5083d9763a3b6de3718e8400950f43e1eb4bd955",
        )

    def test_indonesian_row_remains_a_historical_report_not_source_proof(self) -> None:
        row = self.editions["openlogic-id-reported-20260821"]
        self.assertEqual(row["work_id"], "openlogic-core")
        self.assertIsNone(row["source_edition_id"])
        self.assertEqual(row["identity_state"], "unverified_report")
        self.assertEqual(row["target_language"]["tag"], "id")
        self.assertEqual(row["target_language"]["name"], "Indonesian")
        self.assertEqual(
            row["progress_state"], "historical_report_complete_at_recording"
        )
        self.assertEqual(row["review_state"], "unknown")
        self.assertEqual(row["evidence"]["status"], "non_public_historical_report")
        self.assertIsNone(row["evidence"]["observed_at"])
        self.assertEqual(row["evidence"]["recorded_at"], "2026-08-21T00:00:00Z")
        self.assertIsNone(row["evidence"]["public_url"])
        self.assertIsNone(row["evidence"]["commit"])
        self.assertIsNone(row["evidence"]["tree"])

    def test_build_semantics_reject_duplicate_reversed_or_failed_targets(self) -> None:
        errors: list[str] = []
        validate_jobs.validate_openlogic_build(
            self.build_receipt, "Open Logic test receipt", errors
        )
        self.assertEqual(errors, [])

        mutations = []
        reversed_targets = copy.deepcopy(self.build_receipt)
        reversed_targets["targets"].reverse()
        mutations.append(reversed_targets)

        duplicate_target = copy.deepcopy(self.build_receipt)
        duplicate_target["targets"][1] = copy.deepcopy(duplicate_target["targets"][0])
        mutations.append(duplicate_target)

        failed = copy.deepcopy(self.build_receipt)
        failed["targets"][0]["exit_code"] = 1
        mutations.append(failed)

        wrong_pages = copy.deepcopy(self.build_receipt)
        wrong_pages["targets"][1]["pdf"]["pages"] = 1012
        mutations.append(wrong_pages)

        fatal = copy.deepcopy(self.build_receipt)
        fatal["targets"][0]["log"]["fatal_markers"] = 1
        mutations.append(fatal)

        open_input = copy.deepcopy(self.build_receipt)
        open_input["targets"][1]["input_closure"]["closed"] = False
        mutations.append(open_input)

        for mutated in mutations:
            errors = []
            validate_jobs.validate_openlogic_build(
                mutated, "mutated Open Logic receipt", errors
            )
            self.assertTrue(errors, mutated)


if __name__ == "__main__":
    unittest.main()
