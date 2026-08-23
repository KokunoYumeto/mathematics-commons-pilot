from __future__ import annotations

import copy
from contextlib import redirect_stderr
import importlib.util
import io
import json
import subprocess
import sys
import tempfile
import unittest
import zipfile
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
BUILD_SPEC = importlib.util.spec_from_file_location(
    "build_jobs", ROOT / "tools" / "build_jobs.py"
)
assert BUILD_SPEC is not None and BUILD_SPEC.loader is not None
build_jobs = importlib.util.module_from_spec(BUILD_SPEC)
BUILD_SPEC.loader.exec_module(build_jobs)
READBACK_SPEC = importlib.util.spec_from_file_location(
    "readback_jobs_release", ROOT / "tools" / "readback_jobs_release.py"
)
assert READBACK_SPEC is not None and READBACK_SPEC.loader is not None
readback_jobs_release = importlib.util.module_from_spec(READBACK_SPEC)
READBACK_SPEC.loader.exec_module(readback_jobs_release)
READER_SPEC = importlib.util.spec_from_file_location(
    "add_id_readers", ROOT / "tools" / "add_id_readers.py"
)
assert READER_SPEC is not None and READER_SPEC.loader is not None
add_id_readers = importlib.util.module_from_spec(READER_SPEC)
READER_SPEC.loader.exec_module(add_id_readers)


class JobCatalogTests(unittest.TestCase):
    def test_validator_missing_required_input_fails_without_traceback(self) -> None:
        stderr = io.StringIO()
        with (
            mock.patch.object(
                validate_jobs,
                "validate_jobs",
                return_value=(28, 31, 538, 8_922_333_939, 8_808_381_269, 542, 2),
            ),
            mock.patch.object(validate_jobs, "validate_translations", return_value=41),
            mock.patch.object(validate_jobs, "validate_formalization", return_value=19),
            mock.patch.object(validate_jobs, "validate_portals", return_value=3),
            mock.patch.object(
                validate_jobs,
                "validate_public_readback",
                return_value=validate_jobs.failed_readback_contract(),
            ),
            mock.patch.object(
                validate_jobs,
                "input_identity",
                side_effect=FileNotFoundError("required receipt is missing"),
            ),
            mock.patch.object(sys, "argv", ["validate_jobs.py"]),
            redirect_stderr(stderr),
        ):
            result = validate_jobs.main()
        self.assertEqual(result, 1)
        self.assertIn("cannot bind validator inputs", stderr.getvalue())

    def test_readback_output_is_tag_derived_and_r1_receipt_is_immutable(self) -> None:
        self.assertEqual(
            readback_jobs_release.required_output_path("jobs-2026-08-21-r2"),
            (ROOT / "catalog" / "readback-r2.json").resolve(),
        )
        stderr = io.StringIO()
        with redirect_stderr(stderr):
            result = readback_jobs_release.main(
                [
                    "--repository",
                    "KokunoYumeto/mathematics-commons-pilot",
                    "--tag",
                    "jobs-2026-08-21-r1",
                    "--commit",
                    "0" * 40,
                    "--catalog",
                    "catalog/jobs.json",
                    "--output",
                    "catalog/readback.json",
                ]
            )
        self.assertEqual(result, 2)
        self.assertIn("immutable R1 receipt", stderr.getvalue())

    def test_r2_prompt_counts_are_positive_integers_without_a_fixed_total(self) -> None:
        for accepted in (1, 2, 13, 45, 91):
            self.assertTrue(validate_jobs.valid_prompt_count(accepted))
        for rejected in (True, False, 0, -1, 1.0, "45", None):
            self.assertFalse(validate_jobs.valid_prompt_count(rejected))

    def test_r2_control_files_are_independently_bound_to_packet_members(self) -> None:
        members = {
            "00_READ_FIRST.md": {
                "path": "00_READ_FIRST.md",
                "bytes": 11,
                "sha256": "A" * 64,
            },
            "04_ALL_13_LITERAL_SESSION_PROMPTS.md": {
                "path": "04_ALL_13_LITERAL_SESSION_PROMPTS.md",
                "bytes": 22,
                "sha256": "B" * 64,
            },
            "98_PACKET_MANIFEST_SHA256.tsv": {
                "path": "98_PACKET_MANIFEST_SHA256.tsv",
                "bytes": 33,
                "sha256": "C" * 64,
            },
        }
        job = {
            "id": "bounded-test-job",
            "start_file": {
                "basename": "00_READ_FIRST.md",
                "bytes": 11,
                "sha256": "A" * 64,
            },
            "prompt_file": {
                "basename": "04_ALL_13_LITERAL_SESSION_PROMPTS.md",
                "bytes": 22,
                "sha256": "B" * 64,
            },
            "packet_manifest": {
                "basename": "98_PACKET_MANIFEST_SHA256.tsv",
                "bytes": 33,
                "sha256": "C" * 64,
            },
        }
        errors: list[str] = []
        validate_jobs.bind_job_control_members(job, members, errors)
        self.assertEqual(errors, [])

        mutated = copy.deepcopy(job)
        mutated["prompt_file"]["sha256"] = "D" * 64
        errors = []
        validate_jobs.bind_job_control_members(mutated, members, errors)
        self.assertEqual(
            errors,
            ["bounded-test-job: prompt file: member SHA-256"],
        )

    def test_catalog_and_manifest_projection(self) -> None:
        errors: list[str] = []
        result = validate_jobs.validate_jobs(None, errors)
        translations = validate_jobs.validate_translations(errors)
        portals = validate_jobs.validate_portals(errors)
        self.assertEqual(errors, [])
        self.assertEqual(result, (28, 31, 538, 8_922_333_939, 8_808_381_269, 542, 2))
        self.assertEqual(translations, 41)
        self.assertEqual(portals, 3)

    def test_portal_states_fail_closed(self) -> None:
        portal, _ = validate_jobs.load(ROOT / "catalog" / "portals.json")
        mutations = []

        published_null = copy.deepcopy(portal)
        published_null["sections"][0]["release"]["tag"] = None
        published_null["sections"][0]["release"]["url"] = None
        mutations.append(published_null)

        missing_expected = copy.deepcopy(portal)
        del missing_expected["sections"][2]["expected_asset"]
        mutations.append(missing_expected)

        empty_tag = copy.deepcopy(portal)
        empty_tag["sections"][1]["release"]["tag"] = ""
        mutations.append(empty_tag)

        recovery_nonzero = copy.deepcopy(portal)
        recovery_nonzero["sections"][2]["release"]["asset_count"] = 1
        mutations.append(recovery_nonzero)

        for mutated in mutations:
            errors: list[str] = []
            validate_jobs.validate_schema(mutated, "portals", "mutated portal", errors)
            self.assertTrue(errors, mutated)

    def test_legacy_portal_identity_is_frozen(self) -> None:
        portal, data = validate_jobs.load(ROOT / "tests" / "fixtures" / "portal-v1.json")
        self.assertEqual(portal["schema"], "math-commons-portal-catalog/v1")
        self.assertEqual(len(data), validate_jobs.PORTAL_V1_BYTES)
        self.assertEqual(validate_jobs.sha256(data), validate_jobs.PORTAL_V1_SHA256)

        mutated = data.replace(b'"updated": "2026-08-22"', b'"updated": "2026-08-23"')
        self.assertEqual(len(mutated), len(data))
        self.assertNotEqual(validate_jobs.sha256(mutated), validate_jobs.PORTAL_V1_SHA256)

    def test_current_portal_schema_requires_commit_bound_releases(self) -> None:
        portal, _ = validate_jobs.load(ROOT / "catalog" / "portals.json")
        current = copy.deepcopy(portal)
        current["schema"] = "math-commons-portal-catalog/v2"
        transcription = current["sections"][0]
        self.assertEqual(transcription["release"]["asset_count"], 31)
        self.assertEqual(transcription["release"]["asset_bytes"], 8_808_381_269)
        self.assertEqual(transcription["release"]["runnable_asset_count"], 30)
        self.assertEqual(
            transcription["release"]["runnable_asset_bytes"], 8_808_377_826
        )
        transcription["release"]["target_commit"] = "a" * 40
        transcription["release"]["target_tree"] = "b" * 40

        translation = current["sections"][1]
        translation["state"] = "runnable"
        translation["release"] = {
            "tag": "translate-openlogic-v1",
            "url": "https://github.com/KokunoYumeto/mathematics-commons-pilot/releases/tag/translate-openlogic-v1",
            "target_commit": "e2e4f5bf2f5b7ae0fc15fadcd4d17b27716f1384",
            "target_tree": "acf7ef634c8871cf58b9d2e871ff6f650e81e69a",
            "asset_count": 1,
            "asset_bytes": 1_921_531,
            "asset_catalog": "catalog/assets/openlogic.json",
            "admission_receipt": "catalog/receipts/openlogic.json",
            "readback": "catalog/openlogic-rb.json",
            "assets": [
                {
                    "name": "openlogic-v1.zip",
                    "bytes": 1_921_531,
                    "sha256": "C91EFD16C6DCF22DAEAFDBDC7F544A9E07C9B9C3BA04CE000BFCD933B52E9B8A",
                }
            ],
        }
        translation["starter"] = {
            "tag": "translate-v7",
            "url": "https://github.com/KokunoYumeto/mathematics-commons-pilot/releases/tag/translate-v7",
            "target_commit": "c" * 40,
            "target_tree": "d" * 40,
            "asset_count": 1,
            "asset_bytes": 15_980,
            "asset_catalog": "catalog/assets/translate-v7.json",
            "admission_receipt": None,
            "readback": "catalog/translate-rb-v7.json",
            "assets": [
                {
                    "name": "translation-starter-v7.zip",
                    "bytes": 15_980,
                    "sha256": "492938BDC0D0E16CA344F7627BA7C225D4F51564B3D025675ED6BE4540480C89",
                }
            ],
        }

        errors: list[str] = []
        validate_jobs.validate_schema(current, "portals", "current portal", errors)
        self.assertEqual(errors, [])

        missing_runnable_total = copy.deepcopy(current)
        del missing_runnable_total["sections"][0]["release"]["runnable_asset_bytes"]
        errors = []
        validate_jobs.validate_schema(
            missing_runnable_total, "portals", "current portal", errors
        )
        self.assertTrue(errors)

        del current["sections"][1]["starter"]["target_tree"]
        errors = []
        validate_jobs.validate_schema(current, "portals", "current portal", errors)
        self.assertTrue(errors)

    def test_translation_starter_chooser_projects_live_catalog(self) -> None:
        choices, _ = validate_jobs.load(ROOT / "kits" / "translate" / "WORKS.json")
        catalog, _ = validate_jobs.load(ROOT / "catalog" / "translations.json")
        readers, _ = validate_jobs.load(
            ROOT / "catalog" / "receipts" / "id-readers.json"
        )
        self.assertEqual(choices["schema"], "math-commons-translation-choices/v8")
        self.assertEqual(
            choices["catalog"],
            {
                "path": "catalog/translations.json",
                "bytes": validate_jobs.TRANSLATE_V9_CATALOG_BYTES,
                "sha256": validate_jobs.TRANSLATE_V9_CATALOG_SHA256,
            },
        )
        self.assertEqual(choices["separate_archive"], catalog["separate_archive"])
        self.assertEqual(choices["jobs"], catalog["jobs"])
        self.assertEqual(choices["language_priority"], catalog["language_priority"])
        self.assertEqual(len(choices["works"]), 27)
        self.assertEqual(len(choices["source_editions"]), 39)
        self.assertEqual(len(choices["translation_editions"]), 14)
        self.assertEqual(len(catalog["works"]), 29)
        self.assertEqual(len(catalog["source_editions"]), 41)
        self.assertEqual(len(catalog["translation_editions"]), 23)
        reader_ids = {row["id"] for row in readers["readers"]}
        self.assertEqual(
            {
                row["id"]
                for row in catalog["translation_editions"]
                if row["progress_state"]
                == "public_reader_available_scope_unassessed"
            },
            reader_ids,
        )
        self.assertTrue(
            {row["id"] for row in choices["works"]}.issubset(
                {row["id"] for row in catalog["works"]}
            )
        )
        self.assertTrue(
            {row["id"] for row in choices["source_editions"]}.issubset(
                {row["id"] for row in catalog["source_editions"]}
            )
        )
        self.assertTrue(
            {row["id"] for row in choices["translation_editions"]}.issubset(
                {row["id"] for row in catalog["translation_editions"]}
            )
        )
        self.assertNotIn("catalogs", choices)
        self.assertNotIn("suggestions", choices)

    def test_indonesian_reader_projection_is_deterministic(self) -> None:
        expected = (ROOT / "catalog" / "translations.json").read_bytes()
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "translations.json"
            with mock.patch.object(add_id_readers, "OUTPUT_PATH", output):
                self.assertEqual(add_id_readers.main(), 0)
            self.assertEqual(output.read_bytes(), expected)

    def test_translation_semantics_reject_false_current_or_ready_states(self) -> None:
        catalog, _ = validate_jobs.load(ROOT / "catalog" / "translations.json")
        catalog_path = (ROOT / "catalog" / "translations.json").resolve()
        real_load = validate_jobs.load

        mutations: list[tuple[dict, str]] = []

        false_current = copy.deepcopy(catalog)
        historical = next(
            row
            for row in false_current["translation_editions"]
            if row["identity_state"] == "unverified_report"
        )
        historical["progress_state"] = "verified_complete"
        historical["review_state"] = "passed"
        mutations.append((false_current, "unverified report boundary"))

        stale_receipt = copy.deepcopy(catalog)
        receipt = next(
            row
            for row in stale_receipt["evidence"]
            if row["kind"] == "same_commit_receipt"
        )
        receipt["bytes"] += 1
        mutations.append((stale_receipt, "receipt identity"))

        false_ready = copy.deepcopy(catalog)
        openlogic = next(
            row
            for row in false_ready["source_editions"]
            if row["id"] == "openlogic-core-source"
        )
        openlogic["identity_state"] = "reported_locator"
        mutations.append((false_ready, "publication-ready source/rights/components"))

        for mutated, expected in mutations:
            encoded = (json.dumps(mutated, ensure_ascii=False, indent=2) + "\n").encode(
                "utf-8"
            )

            def fake_load(path: Path) -> tuple[dict, bytes]:
                if path.resolve() == catalog_path:
                    return mutated, encoded
                return real_load(path)

            errors: list[str] = []
            with mock.patch.object(validate_jobs, "load", side_effect=fake_load):
                validate_jobs.validate_translations(errors)
            self.assertTrue(any(expected in error for error in errors), errors)

    def test_translation_workflow_startability_is_not_packet_readiness(self) -> None:
        catalog, _ = validate_jobs.load(ROOT / "catalog" / "translations.json")
        works = [
            row
            for row in catalog["source_editions"]
            if row.get("item_type") == "work"
        ]
        resources = [
            row
            for row in catalog["source_editions"]
            if row.get("item_type") == "resource"
        ]
        self.assertEqual(len(works), 29)
        self.assertEqual(
            sum(row["workflow_startability"] == "source_bound_packet" for row in works),
            1,
        )
        self.assertEqual(
            sum(row["workflow_startability"] == "starter_available" for row in works),
            28,
        )
        self.assertTrue(
            all(
                row["workflow_startability"] in {"starter_available", "source_bound_packet"}
                for row in works
            )
        )
        self.assertTrue(
            all(row["workflow_startability"] == "reference_only" for row in resources)
        )
        openlogic = next(
            row for row in works if row["id"] == "openlogic-core-source"
        )
        self.assertEqual(openlogic["readiness"], "runnable")
        self.assertEqual(openlogic["workflow_startability"], "source_bound_packet")

    def test_asset_manifest_set_identity(self) -> None:
        identity = validate_jobs.manifest_set_identity()
        self.assertEqual(identity["files"], 38)
        self.assertGreater(identity["bytes"], 0)
        self.assertGreater(identity["canonical_stream_bytes"], 0)
        self.assertRegex(identity["tree_sha256"], r"^[0-9A-F]{64}$")

    def test_public_readback_binds_release_and_raw_files(self) -> None:
        errors: list[str] = []
        contract = validate_jobs.validate_public_readback(errors)
        self.assertEqual(errors, [])
        self.assertEqual(
            contract,
            {
                "status": "PASS",
                "subject_commit": "6c0c7bbd368cb554d4d9ab9133881a5d4bf56a75",
                "release_tag": "jobs-2026-08-21-r2",
                "release_id": 374540343,
                "transport": "anonymous_https",
                "observed_date": "2026-08-22",
                "release_assets": 31,
                "release_asset_bytes": 8_808_381_269,
                "raw_files": 9,
                "mismatches": 0,
                "errors": 0,
            },
        )

    def test_public_readback_rejects_observed_hash_drift(self) -> None:
        catalog, _ = validate_jobs.load(ROOT / "catalog" / "jobs.json")
        receipt, _ = validate_jobs.load(ROOT / "catalog" / "readback-r2.json")
        mutated = copy.deepcopy(receipt)
        mutated["assets"][0]["observed_sha256"] = "0" * 64
        errors: list[str] = []
        contract = validate_jobs.validate_public_readback_projection(
            catalog, mutated, errors
        )
        self.assertEqual(contract["status"], "FAIL")
        self.assertGreater(contract["errors"], 0)
        self.assertTrue(
            any(error.endswith("exact asset projection") for error in errors), errors
        )

    def test_public_readback_rejects_subject_drift(self) -> None:
        catalog, _ = validate_jobs.load(ROOT / "catalog" / "jobs.json")
        receipt, _ = validate_jobs.load(ROOT / "catalog" / "readback-r2.json")
        mutated = copy.deepcopy(receipt)
        mutated["subject"]["commit"] = "0" * 40
        errors: list[str] = []
        contract = validate_jobs.validate_public_readback_projection(
            catalog, mutated, errors
        )
        self.assertEqual(contract["status"], "FAIL")
        self.assertTrue(any(error.endswith("subject") for error in errors), errors)

    def test_r2_admission_rows_bind_every_job_and_control_file(self) -> None:
        meta, _ = validate_jobs.load(ROOT / "catalog" / "job-meta.json")
        projection = meta["audit_receipt"]["public_projection"]
        audit, _ = validate_jobs.load(ROOT / projection["path"])
        rows = {row["packet_id"]: row for row in audit["rows"]}
        self.assertEqual(audit["schema"], "math-commons-packet-r2-admission/v1")
        self.assertEqual(len(rows), len(meta["jobs"]))
        for job in meta["jobs"]:
            self.assertEqual(job["audit_basis"], "global_receipt", job["id"])
            self.assertTrue(validate_jobs.valid_prompt_count(job["prompt_count"]))
            manifest, _ = validate_jobs.load(
                ROOT / "catalog" / "assets" / f"{job['id']}.json"
            )
            row = rows[job["packet_id"]]
            self.assertEqual(row["job_id"], job["id"])
            self.assertEqual(
                row["direct_snapshot_sha256"],
                validate_jobs.audit_snapshot_sha256(manifest["members"]),
                job["id"],
            )
            members = {member["path"]: member for member in manifest["members"]}
            for field in ("start_file", "prompt_file", "packet_manifest"):
                self.assertEqual(row[field], job[field], f"{job['id']} {field}")
                identity = job[field]
                self.assertEqual(
                    members[identity["basename"]],
                    {
                        "path": identity["basename"],
                        "bytes": identity["bytes"],
                        "sha256": identity["sha256"],
                    },
                    f"{job['id']} {field}",
                )
            receipt = job["validation_receipt"]
            self.assertIs(receipt["included_in_packet"], False)
            self.assertEqual(receipt["public_projection"], projection)

    def test_r2_validator_rejects_non_global_job_basis(self) -> None:
        catalog = {
            "admission": {
                "audit_receipt": {
                    "public_projection": {
                        "path": "catalog/receipts/r2-admission.json",
                    }
                }
            }
        }
        receipt = {
            "included_in_packet": False,
            "public_projection": {
                "path": "catalog/receipts/r2-admission.json",
            },
        }
        self.assertEqual(
            validate_jobs.binds_global_admission_projection(
                catalog,
                {"audit_basis": "global_receipt"},
                receipt,
            ),
            True,
        )
        self.assertEqual(
            validate_jobs.binds_global_admission_projection(
                catalog,
                {"audit_basis": "terminal_sidecar"},
                receipt,
            ),
            False,
        )

    def test_nested_authority_replay_binds_inner_member_hash(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            outer_buffer = io.BytesIO()
            authority_bytes = b"exact nested authority bytes"
            with zipfile.ZipFile(outer_buffer, "w", zipfile.ZIP_DEFLATED) as outer:
                outer.writestr("source/authority.bin", authority_bytes)
            with zipfile.ZipFile(root / "asset.zip", "w", zipfile.ZIP_DEFLATED) as release:
                release.writestr("test-job/outer.zip", outer_buffer.getvalue())
            manifest = {"assets": [{"name": "asset.zip"}]}
            authority = {
                "path": "outer.zip!/source/authority.bin",
                "sha256": validate_jobs.sha256(authority_bytes),
            }
            errors: list[str] = []
            self.assertTrue(
                validate_jobs.replay_nested_authority(
                    root, "test-job", manifest, authority, errors
                )
            )
            self.assertEqual(errors, [])

            authority["sha256"] = "0" * 64
            errors = []
            self.assertFalse(
                validate_jobs.replay_nested_authority(
                    root, "test-job", manifest, authority, errors
                )
            )
            self.assertTrue(any(error.endswith(": SHA-256") for error in errors), errors)

    def test_paths_fail_closed(self) -> None:
        valid = [
            "00_READ_FIRST.md",
            "source/sub/file.tex",
            "a-b_c/01.pdf",
        ]
        invalid = [
            "",
            "/absolute",
            "../escape",
            "a/../../escape",
            "C:/machine/path",
            r"source\file.tex",
        ]
        self.assertTrue(all(validate_jobs.safe_path(item) for item in valid))
        self.assertTrue(all(not validate_jobs.safe_path(item) for item in invalid))

    def test_duplicate_json_key_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "duplicate.json"
            path.write_bytes(b'{"schema":"first","schema":"second"}\n')
            with self.assertRaises(validate_jobs.DuplicateKey):
                validate_jobs.load(path)

    def test_pack_job_rejects_invalid_output_name_and_preserves_zero_byte_source(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source"
            source.mkdir()
            (source / "empty.txt").write_bytes(b"")
            completed = subprocess.run(
                [
                    sys.executable,
                    "tools/pack_job.py",
                    "--source",
                    str(source),
                    "--job-id",
                    "test-job",
                    "--asset",
                    str(root / "Bad Name.ZIP"),
                    "--manifest",
                    str(root / "manifest.json"),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertNotEqual(completed.returncode, 0)
            self.assertIn("lowercase portable .zip", completed.stdout + completed.stderr)

            completed = subprocess.run(
                [
                    sys.executable,
                    "tools/pack_job.py",
                    "--source",
                    str(source),
                    "--job-id",
                    "test-job",
                    "--asset",
                    str(root / "test-job.zip"),
                    "--manifest",
                    str(root / "manifest.json"),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
            manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["source_files"], 1)
            self.assertEqual(manifest["source_bytes"], 0)
            self.assertEqual(
                manifest["members"],
                [
                    {
                        "path": "empty.txt",
                        "bytes": 0,
                        "sha256": validate_jobs.sha256(b""),
                    }
                ],
            )
            with zipfile.ZipFile(root / "test-job.zip", "r") as archive:
                self.assertEqual(archive.namelist(), ["test-job/empty.txt"])
                self.assertEqual(archive.read("test-job/empty.txt"), b"")

    def test_bulk_builder_rejects_output_inside_packet_root(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            packet_root = Path(directory) / "packets"
            output = packet_root / "some-packet" / "release"
            packet_root.mkdir()
            completed = subprocess.run(
                [
                    sys.executable,
                    "tools/build_jobs.py",
                    "--packet-root",
                    str(packet_root),
                    "--output",
                    str(output),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertNotEqual(completed.returncode, 0)
            self.assertIn(
                "release output must not be inside the producer packet root",
                completed.stdout + completed.stderr,
            )
            self.assertFalse(output.exists())

    def test_bulk_builder_rejects_output_inside_translation_kit(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "kit" / "release"
            kit = output.parent
            kit.mkdir()
            with self.assertRaisesRegex(
                ValueError, "release output must not be inside the translation-kit source"
            ):
                build_jobs.reject_output_inside_sources(
                    output.resolve(), (("translation-kit source", kit.resolve()),)
                )
            self.assertFalse(output.exists())

    def test_tracked_full_replay_receipt(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                "tools/validate_jobs.py",
                "--verify-receipt",
                "--json",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        receipt = json.loads(completed.stdout)
        self.assertEqual(receipt["schema"], "math-commons-catalog-check/v3")
        self.assertNotIn("translation_entries", receipt)
        self.assertEqual(
            receipt["translation"],
            {
                "topics": 10,
                "works": 29,
                "resources": 12,
                "source_editions": 41,
                "translation_editions": 23,
                "jobs": 1,
                "workflow_startable_works": 29,
                "packaged_runnable_jobs": 1,
                "runnable_jobs": 1,
                "runnable_jobs_scope": "self_contained_public_packets_only",
                "public_release_assets": 2,
                "public_release_bytes": 1_938_111,
            },
        )
        self.assertIsNone(receipt["inputs"]["translate_v7_readback"])
        self.assertEqual(
            receipt["inputs"]["translate_v8_readback"],
            {
                "path": "catalog/translate-rb-v8.json",
                "bytes": 1_199,
                "sha256": "562B666EAA685299AF226A24501EBD8B3687BED0B1DE39CC56E35246337A4A22",
            },
        )

    def test_catalog_schema_files_are_valid_json(self) -> None:
        for name in (
            "job-meta.schema.json",
            "job-catalog.schema.json",
            "job-asset.schema.json",
            "translation-catalog.schema.json",
            "translation-choices.schema.json",
            "translation-source.schema.json",
            "translation-build.schema.json",
            "formalization-intake.schema.json",
            "portal-catalog.schema.json",
            "portal-readback.schema.json",
            "catalog-check.schema.json",
            "release-readback.schema.json",
        ):
            value = json.loads((ROOT / "schemas" / name).read_text(encoding="utf-8"))
            self.assertEqual(value["$schema"], "https://json-schema.org/draft/2020-12/schema")


if __name__ == "__main__":
    unittest.main()
