#!/usr/bin/env python3
"""Adversarial regression tests for collection-level validator hardening."""

from __future__ import annotations

import contextlib
import hashlib
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import validate_packets  # noqa: E402


CALIBRATION = ROOT / "examples" / "calibration"
HARDENING = ROOT / "tests" / "fixtures" / "hardening"
SCHEMA_FRAGMENTS = HARDENING / "schema_fragments"


class ValidatorHardeningTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.schema_set = validate_packets.load_schema_set(ROOT / "schemas")
        cls.base_paths = sorted(CALIBRATION.glob("*.json"))

    def collection_errors(
        self,
        mutations: dict[str, object],
    ) -> list[str]:
        """Replace named calibration records with schema-valid mutated copies."""

        with tempfile.TemporaryDirectory() as temporary:
            temporary_root = Path(temporary)
            selected: list[Path] = []
            for base in self.base_paths:
                mutation = mutations.get(base.name)
                if mutation is None:
                    selected.append(base)
                    continue
                body = json.loads(base.read_text(encoding="utf-8"))
                mutation(body)  # type: ignore[operator]
                replacement = temporary_root / base.name
                replacement.write_text(
                    json.dumps(body, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8",
                    newline="\n",
                )
                schema_errors = validate_packets.validate_record_file(
                    replacement, self.schema_set
                )
                self.assertEqual([], schema_errors, "\n".join(schema_errors))
                selected.append(replacement)
            return validate_packets.validate_collection(selected, self.schema_set)

    def assert_collection_error(
        self,
        mutations: dict[str, object],
        expected: str,
    ) -> None:
        rendered = "\n".join(self.collection_errors(mutations))
        self.assertIn(expected, rendered, rendered)

    def run_git(self, repository: Path, *arguments: str) -> str:
        completed = subprocess.run(
            ["git", *arguments],
            cwd=repository,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(
            0,
            completed.returncode,
            completed.stdout + completed.stderr,
        )
        return completed.stdout.strip()

    def make_repository_binding_fixture(
        self, repository: Path
    ) -> tuple[list[Path], str]:
        """Create an honest two-commit reviewed-subject history."""

        self.run_git(repository, "init", "--quiet")
        self.run_git(repository, "config", "user.name", "Binding Test")
        self.run_git(
            repository,
            "config",
            "user.email",
            "binding-test@example.invalid",
        )
        (repository / "README.md").write_text(
            "# Protected integration base\n",
            encoding="utf-8",
            newline="\n",
        )
        self.run_git(repository, "add", "--", "README.md")
        self.run_git(repository, "commit", "--quiet", "-m", "Protected base")
        proof = repository / "work" / "TEST-EVIDENCE-001" / "proof.txt"
        proof.parent.mkdir(parents=True)
        proof.write_text("Exact reviewed artifact.\n", encoding="utf-8", newline="\n")
        evidence = repository / "evidence" / "evidence-record.json"
        evidence.parent.mkdir()
        evidence_body = {
            "record_type": "evidence_record",
            "schema_version": "0.1.0",
            "record_version": "1.0.0",
            "artifact_id": "TEST-EVIDENCE-001",
            "created_at": "2020-01-01T00:00:00Z",
            "artifact_path": proof.relative_to(repository).as_posix(),
        }
        evidence.write_text(
            json.dumps(evidence_body, sort_keys=True, indent=2) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        self.run_git(
            repository,
            "add",
            "--",
            evidence.relative_to(repository).as_posix(),
            proof.relative_to(repository).as_posix(),
        )
        self.run_git(repository, "commit", "--quiet", "-m", "Freeze evidence")
        subject_commit = self.run_git(repository, "rev-parse", "HEAD")

        review = repository / "reviews" / "review-record.json"
        review.parent.mkdir()
        review_body = {
            "record_type": "review_record",
            "schema_version": "0.1.0",
            "record_version": "1.0.0",
            "review_id": "TEST-REVIEW-001",
            "updated_at": "2099-01-01T00:00:00Z",
            "reviewed_subject": {
                "record_type": "evidence_record",
                "record_id": "TEST-EVIDENCE-001",
                "record_version": "1.0.0",
                "hashes": [
                    {
                        "algorithm": "sha256",
                        "digest": validate_packets.sha256_record_file(evidence),
                    }
                ],
                "git_commit": subject_commit,
                "artifact_path": evidence.relative_to(repository).as_posix(),
            },
        }
        review.write_text(
            json.dumps(review_body, sort_keys=True, indent=2) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        self.run_git(
            repository,
            "add",
            "--",
            review.relative_to(repository).as_posix(),
        )
        self.run_git(repository, "commit", "--quiet", "-m", "Record review")
        return [evidence, review], subject_commit

    def test_source_permissions_and_submission_allowlists_are_cross_checked(self) -> None:
        def prohibit_extraction(body: dict[str, object]) -> None:
            body["rights_assessment"]["permissions"]["extraction"] = "prohibited"  # type: ignore[index]
            body["third_party_components"][0]["permissions"][  # type: ignore[index]
                "extraction"
            ] = "prohibited"

        cases = [
            (
                {"source-record.json": prohibit_extraction},
                "does not grant extraction permission",
            ),
            (
                {
                    "research-packet-05-submitted.json": lambda body: body[
                        "submission_boundary"
                    ].update(allowlisted_artifact_ids=[])
                },
                "packet outputs are absent from the public artifact allowlist",
            ),
            (
                {
                    "producer-run.json": lambda body: body[
                        "submission_rights"
                    ].update(submitted_component_ids=["CAL-RUN-PRODUCER-001"])
                },
                "output artifacts are absent from submitted components",
            ),
            (
                {
                    "evidence-record.json": lambda body: body[
                        "submission_rights"
                    ].update(submitted_component_ids=["CAL-OTHER-001"])
                },
                "must include this record id 'CAL-EVIDENCE-001'",
            ),
        ]
        for mutations, expected in cases:
            with self.subTest(expected=expected):
                self.assert_collection_error(mutations, expected)

    def test_explicit_execution_limits_bind_paths_commands_and_actual_usage(self) -> None:
        def add_usage(body: dict[str, object], cpu_seconds: int) -> None:
            body["resources"].update(  # type: ignore[index, union-attr]
                paid_spend=0,
                cpu_seconds=cpu_seconds,
                peak_ram_bytes=0,
                gpu_seconds=0,
                storage_bytes=0,
                upload_bytes=0,
            )

        self.assert_collection_error(
            {
                "producer-run.json": lambda body: add_usage(body, 4000),
            },
            "$.resources.cpu_seconds exceeds packet maximum_cpu_seconds",
        )

        def command_without_allowlist(body: dict[str, object]) -> None:
            body["acceptance_criteria"][0][  # type: ignore[index]
                "verification_method"
            ] = "test_command"

        self.assert_collection_error(
            {"research-packet-01-draft.json": command_without_allowlist},
            "mandatory command-based criteria lack an allowlisted acceptance command",
        )

    def test_record_hash_normalizes_line_endings_but_artifact_hash_does_not(self) -> None:
        source = CALIBRATION / "research-packet-05-submitted.json"
        lf_payload = source.read_bytes().replace(b"\r\n", b"\n")
        self.assertNotIn(b"\r\n", lf_payload)
        with tempfile.TemporaryDirectory(dir=HARDENING) as temporary:
            lf_path = Path(temporary) / "research-packet-05-submitted-lf.json"
            crlf_path = Path(temporary) / "research-packet-05-submitted.json"
            crlf_payload = lf_payload.replace(b"\n", b"\r\n")
            lf_path.write_bytes(lf_payload)
            crlf_path.write_bytes(crlf_payload)
            self.assertEqual(
                validate_packets.sha256_record_file(lf_path),
                validate_packets.sha256_record_file(crlf_path),
            )
            self.assertEqual(
                validate_packets.sha256_record_file(source),
                validate_packets.sha256_record_file(lf_path),
            )
            self.assertNotEqual(
                hashlib.sha256(lf_payload).hexdigest(),
                hashlib.sha256(crlf_payload).hexdigest(),
            )

    def test_schema_subset_meta_validation_and_exact_refs_fail_closed(self) -> None:
        cases = [
            ("malformed-items.json", "items must be a boolean or one schema object"),
            ("aliased-remote-ref.json", "target must be an exact local $id"),
            ("nested-quantifier-pattern.json", "prohibited nested quantifier"),
        ]
        for fragment_name, expected in cases:
            with self.subTest(fragment=fragment_name):
                with tempfile.TemporaryDirectory() as temporary:
                    schema_dir = Path(temporary) / "schemas"
                    shutil.copytree(ROOT / "schemas", schema_dir)
                    target_path = schema_dir / "research-packet.schema.json"
                    target = json.loads(target_path.read_text(encoding="utf-8"))
                    fragment = json.loads(
                        (SCHEMA_FRAGMENTS / fragment_name).read_text(encoding="utf-8")
                    )
                    target["properties"]["project_id"] = fragment
                    target_path.write_text(
                        json.dumps(target, ensure_ascii=False, indent=2) + "\n",
                        encoding="utf-8",
                        newline="\n",
                    )
                    with self.assertRaisesRegex(ValueError, re.escape(expected)):
                        validate_packets.load_schema_set(schema_dir)

    def test_discovery_proves_containment_and_enforces_resource_bounds(self) -> None:
        with tempfile.TemporaryDirectory() as outside:
            outside_file = Path(outside) / "record.json"
            outside_file.write_text("{}", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "escapes the repository"):
                validate_packets.expand_paths([outside_file], repository_root=ROOT)

        with tempfile.TemporaryDirectory(dir=HARDENING) as temporary:
            directory = Path(temporary)
            (directory / "one.json").write_text("{}", encoding="utf-8")
            (directory / "two.json").write_text("{}", encoding="utf-8")
            with mock.patch.object(validate_packets, "MAX_INSTANCE_FILES", 1):
                with self.assertRaisesRegex(ValueError, "exceeds 1 files"):
                    validate_packets.expand_paths([directory], repository_root=ROOT)

        with tempfile.TemporaryDirectory(dir=HARDENING) as temporary:
            directory = Path(temporary)
            oversized = directory / "oversized.json"
            oversized.write_bytes(b" " * 9)
            with mock.patch.object(validate_packets, "MAX_JSON_FILE_BYTES", 8):
                with self.assertRaisesRegex(ValueError, "limit is 8"):
                    validate_packets.expand_paths([directory], repository_root=ROOT)

        with tempfile.TemporaryDirectory(dir=HARDENING) as temporary:
            directory = Path(temporary)
            nested = directory / "nested"
            nested.mkdir()
            (nested / "record.json").write_text("{}", encoding="utf-8")
            with mock.patch.object(validate_packets, "MAX_DIRECTORY_DEPTH", 0):
                with self.assertRaisesRegex(ValueError, "directory depth exceeds 0"):
                    validate_packets.expand_paths([directory], repository_root=ROOT)

    def test_discovery_rejects_symlinks_without_following_them(self) -> None:
        with tempfile.TemporaryDirectory(dir=HARDENING) as temporary:
            directory = Path(temporary)
            target = directory / "target.json"
            target.write_text("{}", encoding="utf-8")
            link = directory / "linked.json"
            try:
                os.symlink(target, link)
            except OSError as exc:
                # Windows may deny symlink creation without Developer Mode.
                # Exercise the same fail-closed branch deterministically.
                self.assertTrue(exc)
                with mock.patch.object(
                    Path,
                    "is_symlink",
                    lambda candidate: candidate.name == "linked.json",
                ):
                    with self.assertRaisesRegex(
                        ValueError, "symbolic links are not permitted"
                    ):
                        validate_packets.ensure_safe_path_components(link, ROOT)
                return
            with self.assertRaisesRegex(ValueError, "symbolic links are not permitted"):
                validate_packets.expand_paths([directory], repository_root=ROOT)

    def test_schema_only_rejects_paths_and_default_validation_is_full_collection(self) -> None:
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            status = validate_packets.main(["--schema-only", "examples/calibration"])
        self.assertEqual(2, status)
        self.assertIn("cannot be combined with record paths", output.getvalue())

        paths, errors = validate_packets.validate_selected_paths(None, self.schema_set)
        self.assertEqual([], errors, "\n".join(errors))
        self.assertEqual(13, len(paths))
        self.assertEqual(
            set(validate_packets.EXECUTION_LIMIT_DEFAULTS),
            set(validate_packets.effective_execution_limits({})),
        )
        defaults = validate_packets.effective_execution_limits({})
        self.assertEqual([], defaults["allowed_output_paths"])
        self.assertEqual([], defaults["acceptance_commands"])
        self.assertTrue(
            all(
                value == 0
                for key, value in defaults.items()
                if key not in {"allowed_output_paths", "acceptance_commands"}
            )
        )

    def test_repository_aware_review_binds_exact_ancestor_blob_and_scrubs_git_env(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repository = Path(temporary)
            paths, _ = self.make_repository_binding_fixture(repository)
            with mock.patch.dict(
                os.environ,
                {
                    "GIT_DIR": str(repository / "attacker.git"),
                    "git_object_directory": str(repository / "attacker-objects"),
                    "GIT_REPLACE_REF_BASE": "refs/attacker/",
                },
                clear=False,
            ):
                errors = validate_packets.validate_repository_bindings(
                    paths, repository_root=repository
                )
            self.assertEqual([], errors, "\n".join(errors))

            review = json.loads(paths[1].read_text(encoding="utf-8"))
            review["reviewed_subject"]["hashes"][0]["digest"] = "0" * 64
            paths[1].write_text(
                json.dumps(review, sort_keys=True, indent=2) + "\n",
                encoding="utf-8",
                newline="\n",
            )
            errors = validate_packets.validate_repository_bindings(
                paths, repository_root=repository
            )
            self.assertIn(
                "does not match the exact LF-normalized reviewed-record digest",
                "\n".join(errors),
            )

    def test_repository_aware_validation_rejects_history_redirection_metadata(
        self,
    ) -> None:
        for attack in ("grafts", "alternates", "replace"):
            with self.subTest(attack=attack), tempfile.TemporaryDirectory() as temporary:
                repository = Path(temporary)
                paths, subject_commit = self.make_repository_binding_fixture(repository)
                git_dir = repository / ".git"
                if attack == "grafts":
                    metadata = git_dir / "info" / "grafts"
                    metadata.parent.mkdir(parents=True, exist_ok=True)
                    metadata.write_text(
                        subject_commit + " " + self.run_git(repository, "rev-parse", "HEAD") + "\n",
                        encoding="utf-8",
                        newline="\n",
                    )
                    expected = "Git grafts metadata"
                elif attack == "alternates":
                    metadata = git_dir / "objects" / "info" / "alternates"
                    metadata.parent.mkdir(parents=True, exist_ok=True)
                    metadata.write_text(
                        str(repository / "alternate-objects") + "\n",
                        encoding="utf-8",
                        newline="\n",
                    )
                    expected = "Git object alternates metadata"
                else:
                    self.run_git(
                        repository,
                        "replace",
                        "-f",
                        subject_commit,
                        self.run_git(repository, "rev-parse", "HEAD"),
                    )
                    expected = "Git replacement refs"
                errors = validate_packets.validate_repository_bindings(
                    paths, repository_root=repository
                )
                self.assertIn(expected, "\n".join(errors), "\n".join(errors))

    def test_protected_base_enforces_two_phase_review_and_append_only_history(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repository = Path(temporary)
            paths, subject_commit = self.make_repository_binding_fixture(repository)
            pre_submission_base = self.run_git(
                repository, "rev-parse", f"{subject_commit}^"
            )

            errors = validate_packets.validate_repository_bindings(
                paths,
                repository_root=repository,
                protected_base_commit=subject_commit,
            )
            self.assertEqual([], errors, "\n".join(errors))

            errors = validate_packets.validate_repository_bindings(
                paths,
                repository_root=repository,
                protected_base_commit=pre_submission_base,
            )
            self.assertIn(
                "not an ancestor of the protected integration base",
                "\n".join(errors),
            )

            proof_path = repository / json.loads(
                paths[0].read_text(encoding="utf-8")
            )["artifact_path"]
            proof_path.write_text(
                "Rewritten after review.\n", encoding="utf-8", newline="\n"
            )
            self.run_git(
                repository,
                "add",
                "--",
                proof_path.relative_to(repository).as_posix(),
            )
            self.run_git(repository, "commit", "--quiet", "-m", "Rewrite old artifact")
            errors = validate_packets.validate_repository_bindings(
                paths,
                repository_root=repository,
                protected_base_commit=subject_commit,
            )
            self.assertIn(
                "protected immutable path was modified: "
                "work/TEST-EVIDENCE-001/proof.txt",
                "\n".join(errors),
            )

            evidence_body = json.loads(paths[0].read_text(encoding="utf-8"))
            evidence_body["created_at"] = "2021-01-01T00:00:00Z"
            paths[0].write_text(
                json.dumps(evidence_body, sort_keys=True, indent=2) + "\n",
                encoding="utf-8",
                newline="\n",
            )
            self.run_git(
                repository,
                "add",
                "--",
                paths[0].relative_to(repository).as_posix(),
            )
            self.run_git(repository, "commit", "--quiet", "-m", "Rewrite old record")
            errors = validate_packets.validate_repository_bindings(
                paths,
                repository_root=repository,
                protected_base_commit=subject_commit,
            )
            self.assertIn(
                "protected immutable path was modified: "
                "evidence/evidence-record.json",
                "\n".join(errors),
            )

    def test_protected_base_does_not_freeze_record_shaped_test_fixtures(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repository = Path(temporary)
            paths, subject_commit = self.make_repository_binding_fixture(repository)
            fixture = repository / "tests" / "fixtures" / "invalid-record.json"
            fixture.parent.mkdir(parents=True)
            fixture.write_text(
                json.dumps(
                    {
                        "record_type": "evidence_record",
                        "record_version": "1.0.0",
                        "artifact_id": "INVALID-FIXTURE",
                        "artifact_path": "fixture-only.txt",
                    },
                    sort_keys=True,
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
                newline="\n",
            )
            self.run_git(repository, "add", "--", fixture.relative_to(repository).as_posix())
            self.run_git(repository, "commit", "--quiet", "-m", "Add test fixture")
            fixture_base = self.run_git(repository, "rev-parse", "HEAD")
            fixture.write_text("{}\n", encoding="utf-8", newline="\n")
            self.run_git(repository, "add", "--", fixture.relative_to(repository).as_posix())
            self.run_git(repository, "commit", "--quiet", "-m", "Maintain test fixture")

            errors = validate_packets.validate_repository_bindings(
                paths,
                repository_root=repository,
                protected_base_commit=fixture_base,
            )
            self.assertNotIn("tests/fixtures/invalid-record.json", "\n".join(errors))

    def test_repository_bindings_check_packet_leases_and_run_revisions(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repository = Path(temporary)
            self.run_git(repository, "init", "--quiet")
            self.run_git(repository, "config", "user.name", "Binding Test")
            self.run_git(
                repository,
                "config",
                "user.email",
                "binding-test@example.invalid",
            )
            (repository / "README.md").write_text(
                "# Test\n", encoding="utf-8", newline="\n"
            )
            self.run_git(repository, "add", "--", "README.md")
            self.run_git(repository, "commit", "--quiet", "-m", "Base")
            missing = "f" * 40
            packet = repository / "packet.json"
            run = repository / "run.json"
            packet.write_text(
                json.dumps(
                    {
                        "record_type": "research_packet",
                        "record_version": "1.0.0",
                        "packet_id": "TEST-PACKET-001",
                        "lease": {
                            "base_commit": missing,
                            "claimed_at": "2099-01-01T00:00:00Z",
                        },
                    }
                )
                + "\n",
                encoding="utf-8",
                newline="\n",
            )
            run.write_text(
                json.dumps(
                    {
                        "record_type": "run_record",
                        "record_version": "1.0.0",
                        "run_id": "TEST-RUN-001",
                        "started_at": "2099-01-01T00:00:00Z",
                        "workspace_revision": {
                            "version_control": "git",
                            "revision": missing,
                        },
                    }
                )
                + "\n",
                encoding="utf-8",
                newline="\n",
            )
            errors = validate_packets.validate_repository_bindings(
                [packet, run], repository_root=repository
            )
            rendered = "\n".join(errors)
            self.assertIn("$.lease.base_commit", rendered)
            self.assertIn("$.workspace_revision.revision", rendered)

            run_body = json.loads(run.read_text(encoding="utf-8"))
            run_body["workspace_revision"]["revision"] = "--batch"
            run.write_text(
                json.dumps(run_body) + "\n", encoding="utf-8", newline="\n"
            )
            errors = validate_packets.validate_repository_bindings(
                [run], repository_root=repository
            )
            self.assertIn(
                "nonzero full lowercase SHA-1",
                "\n".join(errors),
            )

    def test_accepting_review_git_run_cannot_predate_reviewed_subject(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repository = Path(temporary)
            self.run_git(repository, "init", "--quiet")
            self.run_git(repository, "config", "user.name", "Binding Test")
            self.run_git(
                repository,
                "config",
                "user.email",
                "binding-test@example.invalid",
            )
            (repository / "README.md").write_text(
                "# Base\n", encoding="utf-8", newline="\n"
            )
            self.run_git(repository, "add", "--", "README.md")
            self.run_git(repository, "commit", "--quiet", "-m", "Base")
            pre_subject_commit = self.run_git(repository, "rev-parse", "HEAD")

            proof = repository / "work" / "TEST-EVIDENCE-001" / "proof.txt"
            proof.parent.mkdir(parents=True)
            proof.write_text("Reviewed bytes.\n", encoding="utf-8", newline="\n")
            proof_digest = hashlib.sha256(proof.read_bytes()).hexdigest()
            evidence = repository / "evidence" / "evidence-record.json"
            evidence.parent.mkdir()
            evidence_body = {
                "record_type": "evidence_record",
                "record_version": "1.0.0",
                "artifact_id": "TEST-EVIDENCE-001",
                "created_at": "2020-01-01T00:00:00Z",
                "artifact_path": proof.relative_to(repository).as_posix(),
                "hashes": [
                    {"algorithm": "sha256", "digest": proof_digest}
                ],
            }
            evidence.write_text(
                json.dumps(evidence_body, sort_keys=True, indent=2) + "\n",
                encoding="utf-8",
                newline="\n",
            )
            self.run_git(
                repository,
                "add",
                "--",
                evidence.relative_to(repository).as_posix(),
                proof.relative_to(repository).as_posix(),
            )
            self.run_git(repository, "commit", "--quiet", "-m", "Freeze subject")
            subject_commit = self.run_git(repository, "rev-parse", "HEAD")

            run = repository / "runs" / "review-run.json"
            run.parent.mkdir()
            run_body = {
                "record_type": "run_record",
                "record_version": "1.0.0",
                "run_id": "TEST-REVIEW-RUN-001",
                "status": "completed",
                "started_at": "2099-01-01T00:00:00Z",
                "recorded_at": "2099-01-01T00:01:00Z",
                "input_artifacts": [
                    {
                        "artifact_id": "TEST-EVIDENCE-001",
                        "record_version": "1.0.0",
                        "hashes": [
                            {"algorithm": "sha256", "digest": proof_digest}
                        ],
                    }
                ],
                "workspace_revision": {
                    "version_control": "git",
                    "revision": pre_subject_commit,
                },
            }
            run.write_text(
                json.dumps(run_body, sort_keys=True, indent=2) + "\n",
                encoding="utf-8",
                newline="\n",
            )
            review = repository / "reviews" / "review-record.json"
            review.parent.mkdir()
            review_body = {
                "record_type": "review_record",
                "record_version": "1.0.0",
                "review_id": "TEST-REVIEW-001",
                "updated_at": "2099-01-01T00:02:00Z",
                "reviewed_subject": {
                    "record_type": "evidence_record",
                    "record_id": "TEST-EVIDENCE-001",
                    "record_version": "1.0.0",
                    "hashes": [
                        {
                            "algorithm": "sha256",
                            "digest": validate_packets.sha256_record_file(evidence),
                        }
                    ],
                    "git_commit": subject_commit,
                    "artifact_path": evidence.relative_to(repository).as_posix(),
                },
                "review_run_refs": [
                    {
                        "run_id": "TEST-REVIEW-RUN-001",
                        "record_version": "1.0.0",
                    }
                ],
                "conclusion": {"recommendation": "accept_for_network_record"},
            }
            review.write_text(
                json.dumps(review_body, sort_keys=True, indent=2) + "\n",
                encoding="utf-8",
                newline="\n",
            )
            self.run_git(
                repository,
                "add",
                "--",
                run.relative_to(repository).as_posix(),
                review.relative_to(repository).as_posix(),
            )
            self.run_git(repository, "commit", "--quiet", "-m", "Review")

            errors = validate_packets.validate_repository_bindings(
                [evidence, run, review],
                repository_root=repository,
                protected_base_commit=subject_commit,
            )
            self.assertIn(
                "reviewed-subject commit is not an ancestor of exact review run",
                "\n".join(errors),
            )

            run_body["workspace_revision"]["revision"] = subject_commit
            run.write_text(
                json.dumps(run_body, sort_keys=True, indent=2) + "\n",
                encoding="utf-8",
                newline="\n",
            )
            errors = validate_packets.validate_repository_bindings(
                [evidence, run, review],
                repository_root=repository,
                protected_base_commit=subject_commit,
            )
            self.assertNotIn(
                "reviewed-subject commit is not an ancestor of exact review run",
                "\n".join(errors),
            )

    def test_protected_base_cli_requires_repository_aware_mode(self) -> None:
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            status = validate_packets.main(
                ["--protected-base", "1" * 40]
            )
        self.assertEqual(2, status)
        self.assertIn(
            "--protected-base requires --repository-aware", output.getvalue()
        )


if __name__ == "__main__":
    unittest.main()
