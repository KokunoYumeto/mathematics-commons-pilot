from __future__ import annotations

import copy
import importlib.util
import io
import json
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path


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


class JobCatalogTests(unittest.TestCase):
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
        self.assertEqual(result, (28, 30, 488, 6_691_065_999, 6_599_622_703, 492, 2))
        self.assertEqual(translations, 40)
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

    def test_translation_starter_catalogs_are_exactly_pinned(self) -> None:
        choices, _ = validate_jobs.load(ROOT / "kits" / "translate" / "WORKS.json")
        open_education = choices["catalogs"]["open_education"]
        catalog_bytes = (ROOT / open_education["path"]).read_bytes()
        self.assertEqual(open_education["commit"], "bade016f98f1516e86ceb0601e592f82a83a3035")
        self.assertEqual(open_education["tree"], "f69682edae344c2730f1769505a9e9a4293c4547")
        self.assertEqual(open_education["bytes"], len(catalog_bytes))
        self.assertEqual(open_education["sha256"], validate_jobs.sha256(catalog_bytes))
        interlanguage = choices["catalogs"]["interlanguage_archive"]
        self.assertRegex(interlanguage["commit"], r"^[0-9a-f]{40}$")
        self.assertRegex(interlanguage["tree"], r"^[0-9a-f]{40}$")
        self.assertRegex(interlanguage["sha256"], r"^[0-9A-F]{64}$")

    def test_asset_manifest_set_identity(self) -> None:
        identity = validate_jobs.manifest_set_identity()
        self.assertEqual(identity["files"], 31)
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
                "subject_commit": "049a2c9c351e827c85e69f21c2ebd0c3a98db705",
                "release_tag": "jobs-2026-08-21-r1",
                "release_id": 374306971,
                "transport": "anonymous_https",
                "observed_date": "2026-08-21",
                "release_assets": 30,
                "release_asset_bytes": 6_599_622_703,
                "raw_files": 7,
                "mismatches": 0,
                "errors": 0,
            },
        )

    def test_public_readback_rejects_observed_hash_drift(self) -> None:
        catalog, _ = validate_jobs.load(ROOT / "catalog" / "jobs.json")
        receipt, _ = validate_jobs.load(ROOT / "catalog" / "readback.json")
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
        receipt, _ = validate_jobs.load(ROOT / "catalog" / "readback.json")
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

    def test_pack_job_rejects_invalid_output_name_and_zero_byte_source(self) -> None:
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
            self.assertNotEqual(completed.returncode, 0)
            self.assertIn("zero-byte source members", completed.stdout + completed.stderr)

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
            [sys.executable, "tools/validate_jobs.py", "--verify-receipt"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        self.assertIn(
            "PASS: 28 jobs, 30 release assets, 40 translation entries, 3 portal sections",
            completed.stdout,
        )

    def test_catalog_schema_files_are_valid_json(self) -> None:
        for name in (
            "job-meta.schema.json",
            "job-catalog.schema.json",
            "job-asset.schema.json",
            "translation-catalog.schema.json",
            "portal-catalog.schema.json",
            "portal-readback.schema.json",
            "catalog-check.schema.json",
            "release-readback.schema.json",
        ):
            value = json.loads((ROOT / "schemas" / name).read_text(encoding="utf-8"))
            self.assertEqual(value["$schema"], "https://json-schema.org/draft/2020-12/schema")


if __name__ == "__main__":
    unittest.main()
