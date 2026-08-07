#!/usr/bin/env python3
"""Fail-closed collection and Git-lease tests for the pilot CLI."""

from __future__ import annotations

import argparse
import contextlib
import copy
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import commons  # noqa: E402


class CommonsCliHardeningTests(unittest.TestCase):
    def collection_temporary_directory(self) -> tempfile.TemporaryDirectory[str]:
        build_root = ROOT / "dist"
        build_root.mkdir(exist_ok=True)
        return tempfile.TemporaryDirectory(dir=build_root)

    def run_git(
        self,
        repository: Path,
        *arguments: str,
        input_text: str | None = None,
    ) -> str:
        completed = subprocess.run(
            ["git", *arguments],
            cwd=repository,
            check=False,
            capture_output=True,
            text=True,
            input=input_text,
        )
        self.assertEqual(
            0,
            completed.returncode,
            f"git {' '.join(arguments)} failed:\n{completed.stderr}",
        )
        return completed.stdout.strip()

    @contextlib.contextmanager
    def patched_root(self, repository: Path):
        with mock.patch.object(commons, "ROOT", repository), mock.patch.object(
            commons.packet_validator, "ROOT", repository
        ):
            yield

    def copy_calibration_collection(self, repository: Path) -> None:
        target = repository / "examples" / "calibration"
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(ROOT / "examples" / "calibration", target)
        calibration_work = ROOT / "work" / "CAL-PACKET-001"
        if calibration_work.exists():
            work_target = repository / "work" / "CAL-PACKET-001"
            work_target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(calibration_work, work_target)

    def make_git_repository(self, repository: Path) -> tuple[str, str]:
        self.run_git(repository, "init")
        self.run_git(repository, "config", "user.name", "CLI hardening test")
        self.run_git(repository, "config", "user.email", "cli-test@example.invalid")
        self.run_git(repository, "config", "core.autocrlf", "false")
        branch = "work/CAL-PACKET-001"
        self.run_git(repository, "checkout", "-b", branch)
        (repository / "README.md").write_text("test repository\n", encoding="utf-8")
        self.run_git(repository, "add", "README.md")
        self.run_git(repository, "commit", "-m", "Create test base")
        return branch, self.run_git(repository, "rev-parse", "HEAD")

    def active_packet(self, repository: Path, branch: str, base_commit: str) -> commons.Packet:
        body = json.loads(
            (
                ROOT
                / "examples"
                / "calibration"
                / "research-packet-04-in-progress.json"
            ).read_text(encoding="utf-8")
        )
        body["capability"]["code_execution"] = "isolated"
        body["created_at"] = "2026-08-07T00:00:00Z"
        body["updated_at"] = "2026-08-07T00:00:01Z"
        body["lease"] = {
            "status": "active",
            "generation": 1,
            "claimant_id": "CAL-CONTRIBUTOR-001",
            "claimed_at": "2026-08-07T00:00:00Z",
            "expires_at": "2099-08-07T00:00:00Z",
            "base_commit": base_commit,
            "branch_name": branch,
        }
        body["execution_limits"] = {
            "allowed_output_paths": [
                "work/CAL-PACKET-001/CAL-EVIDENCE-001.md"
            ],
            "acceptance_commands": [
                {
                    "command_id": "CHECK-PACKET-001",
                    "command": [
                        "python",
                        "-m",
                        "unittest",
                        "discover",
                        "-s",
                        "tests",
                        "-v",
                    ],
                    "cwd": ".",
                    "dependency_paths": ["README.md"],
                    "timeout_seconds": 120,
                    "criterion_ids": ["CAL-CRITERION-ALGEBRA"],
                }
            ],
            "maximum_paid_spend": 0,
            "maximum_cpu_seconds": 3600,
            "maximum_ram_bytes": 1073741824,
            "maximum_gpu_seconds": 0,
            "maximum_storage_bytes": 10485760,
            "maximum_upload_bytes": 0,
        }
        return commons.Packet(repository / "packet.json", body)

    def invoke(self, arguments: list[str]) -> tuple[int, str]:
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            result = commons.main(arguments)
        return result, output.getvalue()

    def test_node_handoff_uses_approved_brief_and_exact_lease_branch(self) -> None:
        guide = (ROOT / "NODE_HANDOFF.md").read_text(encoding="utf-8")
        approved_command = (
            "python tools/commons.py agent-brief --packet-root packets "
            "<PACKET_ID> --expected-handoff-commit <HANDOFF_COMMIT> --approve-safety"
        )
        self.assertEqual(2, guide.count(approved_command))
        self.assertIn("a human must inspect the exact packet", guide)
        self.assertIn("is only an unauthenticated assertion by the caller", guide)
        self.assertIn("is not a sandbox", guide)
        self.assertIn("dependency_paths", guide)
        self.assertIn("git push -u origin <LEASE_BRANCH>", guide)
        self.assertNotIn("git push -u origin packet/<packet-id>", guide)
        self.assertIn("those phrases are not packet statuses", guide)
        self.assertNotIn("close the packet as accepted evidence", guide)
        self.assertIn(
            "exact packet snapshot ID, record version, digest, and repository path",
            guide,
        )
        self.assertIn(
            "exact problem-record reference ID, version, digest, and repository path",
            guide,
        )

    def test_packet_schema_requires_explicit_command_dependency_paths(self) -> None:
        schema = json.loads(
            (ROOT / "schemas" / "research-packet.schema.json").read_text(
                encoding="utf-8"
            )
        )
        command_schema = schema["properties"]["execution_limits"]["properties"][
            "acceptance_commands"
        ]["items"]
        self.assertIn("dependency_paths", command_schema["required"])
        self.assertIn("external runtime", command_schema["properties"]["dependency_paths"]["description"])

    def test_packet_commands_validate_the_complete_collection(self) -> None:
        for bad_kind in ("unknown", "malformed"):
            for command in ("list", "show", "agent-brief"):
                with self.subTest(
                    bad_kind=bad_kind, command=command
                ), self.collection_temporary_directory() as temporary:
                    repository = Path(temporary)
                    self.copy_calibration_collection(repository)
                    bad = repository / "sources" / "bad.json"
                    bad.parent.mkdir(parents=True)
                    if bad_kind == "unknown":
                        bad.write_text(
                            json.dumps(
                                {
                                    "record_type": "unknown_record",
                                    "schema_version": "0.1.0",
                                }
                            ),
                            encoding="utf-8",
                        )
                    else:
                        bad.write_text('{"record_type":', encoding="utf-8")
                    arguments = [command, "--packet-root", "examples/calibration"]
                    if command in {"show", "agent-brief"}:
                        arguments.append("CAL-PACKET-001")
                    if command == "agent-brief":
                        arguments.extend(
                            [
                                "--expected-handoff-commit",
                                "0" * 40,
                                "--approve-safety",
                            ]
                        )
                    with self.patched_root(repository):
                        result, output = self.invoke(arguments)
                    self.assertEqual(1, result, output)
                    expected = "unknown record_type" if bad_kind == "unknown" else "invalid JSON"
                    self.assertIn(expected, output)

    def test_list_rejects_cross_record_failure_outside_packet_selection(self) -> None:
        with self.collection_temporary_directory() as temporary:
            repository = Path(temporary)
            self.copy_calibration_collection(repository)
            run_path = repository / "examples" / "calibration" / "producer-run.json"
            run = json.loads(run_path.read_text(encoding="utf-8"))
            run["packet_ref"]["packet_id"] = "MISSING-PACKET-001"
            run_path.write_text(json.dumps(run, indent=2) + "\n", encoding="utf-8")
            with self.patched_root(repository):
                result, output = self.invoke(
                    ["list", "--packet-root", "examples/calibration"]
                )
        self.assertEqual(1, result, output)
        self.assertIn("unresolved research_packet reference", output)

    def test_validate_defaults_to_every_live_record_directory(self) -> None:
        with self.collection_temporary_directory() as temporary:
            repository = Path(temporary)
            self.copy_calibration_collection(repository)
            bad = repository / "sources" / "malformed.json"
            bad.parent.mkdir(parents=True)
            bad.write_text("not json", encoding="utf-8")
            with self.patched_root(repository):
                result, output = self.invoke(["validate"])
        self.assertEqual(1, result, output)
        self.assertIn("malformed.json", output)
        self.assertIn("invalid JSON", output)

    def test_validate_default_accepts_the_complete_calibration_collection(self) -> None:
        with self.collection_temporary_directory() as temporary:
            repository = Path(temporary)
            self.copy_calibration_collection(repository)
            with self.patched_root(repository):
                result, output = self.invoke(["validate"])
                head = commons.select_packet(
                    Path("examples/calibration"), "CAL-PACKET-001"
                )
        self.assertEqual(0, result, output)
        self.assertIn("default discovered collection", output)
        self.assertIn("13 records", output)
        self.assertEqual("1.4.0", head.body["record_version"])
        self.assertEqual("submitted", head.body["status"])
        self.assertEqual("research-packet-05-submitted.json", head.path.name)

    def test_require_live_rejects_examples_and_copied_calibration_records(self) -> None:
        with self.collection_temporary_directory() as temporary:
            repository = Path(temporary)
            self.copy_calibration_collection(repository)
            with self.patched_root(repository):
                missing_result, missing_output = self.invoke(
                    ["validate", "--require-live"]
                )
            self.assertEqual(1, missing_result, missing_output)
            self.assertIn("examples do not satisfy the Day-1 launch gate", missing_output)

            live_root = repository / "records"
            live_root.mkdir()
            for name in ("source-record.json", "problem-record.json"):
                shutil.copy2(ROOT / "examples" / "calibration" / name, live_root / name)
            shutil.copy2(
                ROOT
                / "examples"
                / "calibration"
                / "research-packet-05-submitted.json",
                live_root / "research-packet.json",
            )
            packet_path = live_root / "research-packet.json"
            packet = json.loads(packet_path.read_text(encoding="utf-8"))
            packet["status"] = "draft"
            packet["lease"] = {
                "status": "unclaimed",
                "generation": 0,
                "claimant_id": None,
                "claimed_at": None,
                "expires_at": None,
                "base_commit": None,
                "branch_name": None,
            }
            packet_path.write_text(
                json.dumps(packet, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
                newline="\n",
            )
            with self.patched_root(repository):
                copied_result, copied_output = self.invoke(
                    ["validate", "--require-live"]
                )
            self.assertEqual(1, copied_result, copied_output)
            self.assertIn("calibration", copied_output.lower())

    def test_require_live_rejects_explicit_paths(self) -> None:
        with self.collection_temporary_directory() as temporary:
            repository = Path(temporary)
            self.copy_calibration_collection(repository)
            with self.patched_root(repository):
                result, output = self.invoke(
                    ["validate", "--require-live", "examples/calibration"]
                )
        self.assertEqual(1, result, output)
        self.assertIn("cannot be combined with explicit record paths", output)

    def test_validate_rejects_ambiguous_schema_only_and_packet_root_flags(self) -> None:
        for arguments in (
            ["validate", "--schema-only"],
            ["validate", "--packet-root", "examples/calibration"],
        ):
            with self.subTest(arguments=arguments), contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit) as raised:
                    commons.parser().parse_args(arguments)
            self.assertEqual(2, raised.exception.code)

    def test_agent_brief_rejects_submitted_packet_status(self) -> None:
        with self.collection_temporary_directory() as temporary:
            repository = Path(temporary)
            self.copy_calibration_collection(repository)
            with self.patched_root(repository):
                result, output = self.invoke(
                    [
                        "agent-brief",
                        "--packet-root",
                        "examples/calibration",
                        "CAL-PACKET-001",
                        "--expected-handoff-commit",
                        "0" * 40,
                        "--approve-safety",
                    ]
                )
        self.assertEqual(1, result, output)
        self.assertIn("requires packet status 'claimed' or 'in_progress'", output)
        self.assertIn("'submitted'", output)

    def test_git_wrapper_ignores_inherited_git_redirection_and_config(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            repository = root / "repository"
            attacker = root / "attacker"
            repository.mkdir()
            attacker.mkdir()
            _, expected = self.make_git_repository(repository)
            self.make_git_repository(attacker)
            poisoned_environment = {
                "GIT_DIR": str(attacker / ".git"),
                "GIT_WORK_TREE": str(attacker),
                "GIT_INDEX_FILE": str(attacker / ".git" / "index"),
                "GIT_OBJECT_DIRECTORY": str(attacker / ".git" / "objects"),
                "GIT_ALTERNATE_OBJECT_DIRECTORIES": str(
                    attacker / ".git" / "objects"
                ),
                "GIT_SHALLOW_FILE": str(attacker / ".git" / "shallow"),
                "GIT_EXEC_PATH": str(attacker / "fake-git-exec-path"),
                "GIT_CONFIG_COUNT": "1",
                "GIT_CONFIG_KEY_0": "core.worktree",
                "GIT_CONFIG_VALUE_0": str(attacker),
                "git_common_dir": str(attacker / ".git"),
            }
            with self.patched_root(repository), mock.patch.dict(
                os.environ, poisoned_environment, clear=False
            ):
                code, observed = commons.git_output(["rev-parse", "HEAD"])
                sanitized = commons.git_environment()
            self.assertEqual(0, code)
            self.assertEqual(expected, observed)
            self.assertFalse(
                any(name.upper().startswith("GIT_") for name in sanitized if name not in {
                    "GIT_NO_REPLACE_OBJECTS",
                    "GIT_OPTIONAL_LOCKS",
                })
            )

            nested = repository / "nested"
            nested.mkdir()
            with self.patched_root(nested):
                wrong_root_code, _ = commons.git_output(["rev-parse", "HEAD"])
            self.assertNotEqual(0, wrong_root_code)

    def test_git_wrapper_rejects_replace_refs_grafts_and_alternates(self) -> None:
        for attack in ("replace", "grafts", "alternates"):
            with self.subTest(attack=attack), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                repository = root / "repository"
                repository.mkdir()
                _, base = self.make_git_repository(repository)
                if attack == "replace":
                    (repository / "README.md").write_text(
                        "replacement bytes\n", encoding="utf-8", newline="\n"
                    )
                    self.run_git(repository, "add", "README.md")
                    tree = self.run_git(repository, "write-tree")
                    replacement = self.run_git(
                        repository,
                        "commit-tree",
                        tree,
                        input_text="replacement commit\n",
                    )
                    self.run_git(repository, "reset", "--hard", base)
                    self.run_git(repository, "replace", base, replacement)
                elif attack == "grafts":
                    grafts = repository / ".git" / "info" / "grafts"
                    grafts.write_text(base + "\n", encoding="ascii", newline="\n")
                else:
                    alternate_objects = root / "alternate-objects"
                    alternate_objects.mkdir()
                    alternates = repository / ".git" / "objects" / "info" / "alternates"
                    alternates.write_text(
                        str(alternate_objects.resolve()) + "\n",
                        encoding="utf-8",
                        newline="\n",
                    )
                with self.patched_root(repository):
                    code, _ = commons.git_output(["rev-parse", "HEAD"])
                self.assertNotEqual(0, code)

    def test_git_handoff_rejects_future_record_and_claim_times(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repository = Path(temporary)
            branch, base = self.make_git_repository(repository)
            fixed_now = datetime(2026, 8, 7, 1, 0, tzinfo=timezone.utc)
            packets: list[commons.Packet] = []

            future_created = self.active_packet(repository, branch, base)
            future_created.body["created_at"] = "2026-08-07T02:00:00Z"
            future_created.body["updated_at"] = "2026-08-07T02:00:00Z"
            future_created.body["lease"]["claimed_at"] = "2026-08-07T02:00:00Z"
            packets.append(future_created)

            future_updated = self.active_packet(repository, branch, base)
            future_updated.body["updated_at"] = "2026-08-07T02:00:00Z"
            packets.append(future_updated)

            future_claimed = self.active_packet(repository, branch, base)
            future_claimed.body["updated_at"] = "2026-08-07T02:00:00Z"
            future_claimed.body["lease"]["claimed_at"] = "2026-08-07T02:00:00Z"
            packets.append(future_claimed)

            with self.patched_root(repository):
                for packet in packets:
                    with self.subTest(packet=packet.body), self.assertRaisesRegex(
                        ValueError, "future"
                    ):
                        commons.require_agent_handoff_state(packet, now=fixed_now)

    def test_git_handoff_accepts_clean_matching_active_lease(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repository = Path(temporary)
            branch, base = self.make_git_repository(repository)
            packet = self.active_packet(repository, branch, base)
            with self.patched_root(repository):
                state = commons.require_agent_handoff_state(packet)
        self.assertEqual(branch, state.branch)
        self.assertEqual(base, state.base_commit)
        self.assertEqual(base, state.commit)

    def test_git_handoff_rejects_expired_or_inactive_lease(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repository = Path(temporary)
            branch, base = self.make_git_repository(repository)
            expired = self.active_packet(repository, branch, base)
            expired.body["created_at"] = "2000-01-01T00:00:00Z"
            expired.body["updated_at"] = "2000-01-01T00:00:01Z"
            expired.body["lease"]["claimed_at"] = "2000-01-01T00:00:00Z"
            expired.body["lease"]["expires_at"] = "2001-01-01T00:00:00Z"
            inactive = self.active_packet(repository, branch, base)
            inactive.body["lease"]["status"] = "claimed"
            for packet, expected in (
                (expired, "lease expired"),
                (inactive, "requires lease status 'active'"),
            ):
                with self.subTest(expected=expected), self.patched_root(repository):
                    with self.assertRaisesRegex(ValueError, expected):
                        commons.require_agent_handoff_state(packet)

    def test_git_handoff_rejects_every_nonwork_packet_status(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repository = Path(temporary)
            branch, base = self.make_git_repository(repository)
            for status in ("ready", "accepted", "closed"):
                with self.subTest(status=status):
                    packet = self.active_packet(repository, branch, base)
                    packet.body["status"] = status
                    with self.patched_root(repository):
                        with self.assertRaisesRegex(
                            ValueError, "requires packet status 'claimed' or 'in_progress'"
                        ):
                            commons.require_agent_handoff_state(packet)

    def test_git_handoff_rejects_wrong_branch_and_missing_base(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repository = Path(temporary)
            branch, base = self.make_git_repository(repository)
            wrong_branch = self.active_packet(repository, "work/OTHER-PACKET", base)
            invalid_branch = self.active_packet(repository, "bad branch", base)
            missing_base = self.active_packet(repository, branch, "0" * 40)
            with self.patched_root(repository):
                with self.assertRaisesRegex(ValueError, "not a valid Git branch"):
                    commons.require_agent_handoff_state(invalid_branch)
                with self.assertRaisesRegex(ValueError, "does not match current branch"):
                    commons.require_agent_handoff_state(wrong_branch)
                with self.assertRaisesRegex(ValueError, "does not name an existing commit"):
                    commons.require_agent_handoff_state(missing_base)

    def test_git_handoff_rejects_existing_nonancestor_base(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repository = Path(temporary)
            branch, base = self.make_git_repository(repository)
            empty_tree = self.run_git(repository, "mktree", input_text="")
            unrelated = self.run_git(
                repository,
                "commit-tree",
                empty_tree,
                input_text="Unrelated root\n",
            )
            self.assertNotEqual(base, unrelated)
            packet = self.active_packet(repository, branch, unrelated)
            with self.patched_root(repository):
                with self.assertRaisesRegex(ValueError, "is not an ancestor of HEAD"):
                    commons.require_agent_handoff_state(packet)

    def test_git_handoff_rejects_dirty_initial_worktree(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repository = Path(temporary)
            branch, base = self.make_git_repository(repository)
            packet = self.active_packet(repository, branch, base)
            (repository / "UNTRACKED.txt").write_text("dirty\n", encoding="utf-8")
            with self.patched_root(repository):
                with self.assertRaisesRegex(ValueError, "clean initial working tree"):
                    commons.require_agent_handoff_state(packet)

    def test_agent_brief_renders_exact_limits_and_commands(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repository = Path(temporary)
            branch, base = self.make_git_repository(repository)
            packet = self.active_packet(repository, branch, base)
            arguments = argparse.Namespace(
                packet_root=Path("packets"),
                packet_id=packet.packet_id,
                expected_handoff_commit=base,
                approve_safety=True,
            )
            output = io.StringIO()
            with self.patched_root(repository), mock.patch.object(
                commons, "select_packet", return_value=packet
            ), mock.patch.object(
                commons,
                "complete_collection_files",
                return_value=([packet.path], [packet.path]),
            ), mock.patch.object(
                commons, "collection_errors", return_value=[]
            ), mock.patch.object(
                commons,
                "require_handoff_repository_baseline",
                return_value=commons.HandoffInputs(
                    record_paths=("packets/CAL-PACKET-001.json",),
                    artifact_paths=("sources/CAL-SOURCE-001.md",),
                    command_dependency_paths=("README.md",),
                ),
            ), contextlib.redirect_stdout(output):
                result = commons.command_agent_brief(arguments)
        rendered = output.getvalue()
        self.assertEqual(0, result)
        self.assertIn("work/CAL-PACKET-001/CAL-EVIDENCE-001.md", rendered)
        self.assertIn('["python", "-m", "unittest", "discover"', rendered)
        self.assertIn("Repository-relative cwd: `.`", rendered)
        self.assertIn("CHECK-PACKET-001", rendered)
        self.assertIn("Maximum CPU time: `3600` seconds", rendered)
        self.assertIn("Maximum RAM: `1073741824` bytes", rendered)
        self.assertIn(f"Lease base commit: `{base}`", rendered)
        self.assertIn(f"Current branch: `{branch}`", rendered)
        self.assertIn(f"Operator-supplied expected handoff commit: `{base}`", rendered)
        self.assertIn("AI systems are disclosed tools, never authors", rendered)
        self.assertIn("Ordinary AI interactions are private by default", rendered)
        self.assertIn("Never request or include raw prompts", rendered)
        self.assertIn("Do not commit, push, open a pull request, merge, release, or publicize", rendered)
        self.assertIn("Safety-review assertion", rendered)
        self.assertIn("unauthenticated flag", rendered)
        self.assertIn("Acceptance-command dependency files", rendered)
        self.assertIn("External/runtime argv[0] is caller-reviewed", rendered)
        self.assertIn("This brief is not a sandbox", rendered)
        self.assertIn("Steward-only correction", rendered)
        self.assertIn("packets/CAL-PACKET-001.json", rendered)

    def test_agent_brief_accepts_exact_head_for_command_free_non_code_packet(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repository = Path(temporary)
            branch, base = self.make_git_repository(repository)
            packet = self.active_packet(repository, branch, base)
            packet.body["capability"]["code_execution"] = "forbidden"
            packet.body["execution_limits"]["acceptance_commands"] = []
            arguments = argparse.Namespace(
                packet_root=Path("packets"),
                packet_id=packet.packet_id,
                expected_handoff_commit=base,
                approve_safety=True,
            )
            output = io.StringIO()
            with self.patched_root(repository), mock.patch.object(
                commons, "select_packet", return_value=packet
            ), mock.patch.object(
                commons,
                "complete_collection_files",
                return_value=([packet.path], [packet.path]),
            ), mock.patch.object(
                commons, "collection_errors", return_value=[]
            ), mock.patch.object(
                commons,
                "require_handoff_repository_baseline",
                return_value=commons.HandoffInputs(
                    record_paths=("packets/CAL-PACKET-001.json",),
                    artifact_paths=(),
                    command_dependency_paths=(),
                ),
            ), contextlib.redirect_stdout(output):
                result = commons.command_agent_brief(arguments)

        rendered = output.getvalue()
        self.assertEqual(0, result)
        self.assertIn(f"Operator-supplied expected handoff commit: `{base}`", rendered)
        self.assertIn("none — code execution is forbidden", rendered)
        self.assertIn("Do not invent or run an acceptance command", rendered)

    def test_agent_brief_rejects_expected_handoff_commit_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repository = Path(temporary)
            branch, base = self.make_git_repository(repository)
            packet = self.active_packet(repository, branch, base)
            wrong_commit = "0" * 40 if base != "0" * 40 else "1" * 40
            arguments = argparse.Namespace(
                packet_root=Path("packets"),
                packet_id=packet.packet_id,
                expected_handoff_commit=wrong_commit,
                approve_safety=True,
            )
            with self.patched_root(repository), mock.patch.object(
                commons, "select_packet", return_value=packet
            ):
                with self.assertRaisesRegex(ValueError, "does not match current Git HEAD"):
                    commons.command_agent_brief(arguments)

    def test_expected_handoff_commit_must_be_full_lowercase_sha(self) -> None:
        handoff = commons.HandoffState(
            commit="a" * 40,
            branch="work/CAL-PACKET-001",
            claimant_id="CAL-CONTRIBUTOR-001",
            claimed_at="2026-08-07T00:00:00Z",
            expires_at="2099-08-07T00:00:00Z",
            base_commit="b" * 40,
        )
        for invalid in ("a" * 39, "A" * 40, "g" * 40, None):
            with self.subTest(invalid=invalid), self.assertRaisesRegex(
                ValueError, "full 40-character lowercase hexadecimal"
            ):
                commons.require_expected_handoff_commit(invalid, handoff)

    def test_agent_brief_parser_requires_full_expected_commit_argument(self) -> None:
        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit) as raised:
                commons.parser().parse_args(
                    ["agent-brief", "CAL-PACKET-001", "--approve-safety"]
                )
        self.assertEqual(2, raised.exception.code)

        parsed = commons.parser().parse_args(
            [
                "agent-brief",
                "CAL-PACKET-001",
                "--expected-handoff-commit",
                "a" * 40,
                "--approve-safety",
            ]
        )
        self.assertEqual("a" * 40, parsed.expected_handoff_commit)

    def test_repository_path_accepts_an_already_canonical_root_alias(self) -> None:
        """Model Windows long-name/8.3 identity without requiring 8.3 locally."""

        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            canonical_root = base / "canonical-repository-root"
            canonical_root.mkdir()
            canonical_file = canonical_root / "README.md"
            canonical_file.write_text("test\n", encoding="utf-8", newline="\n")

            class EquivalentAliasRoot:
                def absolute(self) -> Path:
                    return base / "CANONI~1"

                def resolve(self) -> Path:
                    return canonical_root.resolve()

            with mock.patch.object(commons, "ROOT", EquivalentAliasRoot()):
                resolved, relative = commons.repository_path(
                    canonical_file.resolve(), "canonical handoff input"
                )
                self.assertEqual(canonical_file.resolve(), resolved)
                self.assertEqual("README.md", relative)
                with self.assertRaisesRegex(ValueError, "escapes the repository"):
                    commons.repository_path(
                        (base / "outside.md").resolve(), "outside handoff input"
                    )

    def test_show_renders_declared_operational_bounds(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repository = Path(temporary)
            branch, base = self.make_git_repository(repository)
            packet = self.active_packet(repository, branch, base)
            arguments = argparse.Namespace(
                packet_root=Path("packets"), packet_id=packet.packet_id, json=False
            )
            output = io.StringIO()
            with self.patched_root(repository), mock.patch.object(
                commons, "select_packet", return_value=packet
            ), contextlib.redirect_stdout(output):
                result = commons.command_show(arguments)
        rendered = output.getvalue()
        self.assertEqual(0, result)
        self.assertIn("Allowed output paths:", rendered)
        self.assertIn("work/CAL-PACKET-001/CAL-EVIDENCE-001.md", rendered)
        self.assertIn("Exact acceptance commands:", rendered)
        self.assertIn("CHECK-PACKET-001 [120s; cwd=.]", rendered)
        self.assertIn("paid spend: $0 USD", rendered)
        self.assertIn("RAM: 1073741824 bytes", rendered)
        self.assertIn(f"Lease branch: {branch}", rendered)
        self.assertIn(f"Lease base commit: {base}", rendered)
        self.assertIn("Lease expires at: 2099-08-07T00:00:00Z", rendered)

    def test_agent_brief_requires_explicit_human_safety_approval(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repository = Path(temporary)
            branch, base = self.make_git_repository(repository)
            packet = self.active_packet(repository, branch, base)
            arguments = argparse.Namespace(
                packet_root=Path("packets"),
                packet_id=packet.packet_id,
                expected_handoff_commit=base,
                approve_safety=False,
            )
            with self.patched_root(repository), mock.patch.object(
                commons, "select_packet", return_value=packet
            ):
                with self.assertRaisesRegex(ValueError, "--approve-safety"):
                    commons.command_agent_brief(arguments)

    def test_operational_limits_require_packet_namespace_argv_and_relative_cwd(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repository = Path(temporary)
            branch, base = self.make_git_repository(repository)

            outside = self.active_packet(repository, branch, base)
            outside.body["execution_limits"]["allowed_output_paths"] = [
                "records/steward-transition.json"
            ]
            shell_string = self.active_packet(repository, branch, base)
            shell_string.body["execution_limits"]["acceptance_commands"][0][
                "command"
            ] = "python -m unittest"
            escaping_cwd = self.active_packet(repository, branch, base)
            escaping_cwd.body["execution_limits"]["acceptance_commands"][0][
                "cwd"
            ] = "../outside"
            git_metadata_cwd = self.active_packet(repository, branch, base)
            git_metadata_cwd.body["execution_limits"]["acceptance_commands"][0][
                "cwd"
            ] = ".git"

            with self.patched_root(repository):
                with self.assertRaisesRegex(ValueError, "work/CAL-PACKET-001/"):
                    commons.require_operational_limits(outside)
                with self.assertRaisesRegex(ValueError, "non-empty argv array"):
                    commons.require_operational_limits(shell_string)
                with self.assertRaisesRegex(ValueError, "stay within the repository"):
                    commons.require_operational_limits(escaping_cwd)
                with self.assertRaisesRegex(ValueError, "protected Git metadata"):
                    commons.require_operational_limits(git_metadata_cwd)
                with self.assertRaisesRegex(ValueError, "stay within the repository"):
                    list(
                        commons.iter_repository_artifact_paths(
                            {
                                "record_type": "source_record",
                                "locator": {
                                    "canonical_reference": "../private-input.md"
                                },
                            }
                        )
                    )

    def test_operational_limits_require_explicit_dependencies_and_consistent_capability(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repository = Path(temporary)
            branch, base = self.make_git_repository(repository)
            missing_dependencies = self.active_packet(repository, branch, base)
            del missing_dependencies.body["execution_limits"]["acceptance_commands"][0][
                "dependency_paths"
            ]
            forbidden = self.active_packet(repository, branch, base)
            forbidden.body["capability"]["code_execution"] = "forbidden"
            network_contradiction = self.active_packet(repository, branch, base)
            network_contradiction.body["execution_limits"]["maximum_upload_bytes"] = 1
            undeclared_repository_argument = self.active_packet(repository, branch, base)
            command = undeclared_repository_argument.body["execution_limits"][
                "acceptance_commands"
            ][0]
            command["command"] = ["python", "README.md"]
            command["dependency_paths"] = []

            with self.patched_root(repository):
                with self.assertRaisesRegex(ValueError, "dependency_paths"):
                    commons.require_operational_limits(missing_dependencies)
                with self.assertRaisesRegex(ValueError, "code_execution='forbidden'"):
                    commons.require_operational_limits(forbidden)
                with self.assertRaisesRegex(ValueError, "upload authority contradicts"):
                    commons.require_operational_limits(network_contradiction)
                with self.assertRaisesRegex(ValueError, "does not bind it"):
                    commons.require_operational_limits(undeclared_repository_argument)

    def test_operational_limits_condition_command_presence_on_mandatory_methods(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repository = Path(temporary)
            branch, base = self.make_git_repository(repository)

            command_free = self.active_packet(repository, branch, base)
            command_free.body["capability"]["code_execution"] = "forbidden"
            command_free.body["execution_limits"]["acceptance_commands"] = []

            executable_but_empty = self.active_packet(repository, branch, base)
            executable_but_empty.body["execution_limits"]["acceptance_commands"] = []

            mandatory_without_command = self.active_packet(repository, branch, base)
            mandatory_without_command.body["acceptance_criteria"][0][
                "verification_method"
            ] = "test_command"
            mandatory_without_command.body["execution_limits"][
                "acceptance_commands"
            ] = []

            mandatory_without_mapping = self.active_packet(repository, branch, base)
            mandatory_without_mapping.body["acceptance_criteria"][1][
                "verification_method"
            ] = "formal_compile"

            with self.patched_root(repository):
                limits = commons.require_operational_limits(command_free)
                self.assertEqual([], limits["acceptance_commands"])
                with self.assertRaisesRegex(ValueError, "command-free handoff"):
                    commons.require_operational_limits(executable_but_empty)
                with self.assertRaisesRegex(
                    ValueError, "mandatory command-based criteria require"
                ):
                    commons.require_operational_limits(mandatory_without_command)
                with self.assertRaisesRegex(
                    ValueError, "mandatory command-based criteria lack"
                ):
                    commons.require_operational_limits(mandatory_without_mapping)

    def test_operational_limits_reject_hardlinks_and_nonportable_aliases(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            repository = root / "repository"
            repository.mkdir()
            branch, base = self.make_git_repository(repository)
            packet = self.active_packet(repository, branch, base)
            outside = root / "outside-private.md"
            outside.write_text("private\n", encoding="utf-8", newline="\n")
            output = repository / "work" / packet.packet_id / "CAL-EVIDENCE-001.md"
            output.parent.mkdir(parents=True)
            os.link(outside, output)
            with self.patched_root(repository):
                with self.assertRaisesRegex(ValueError, "multi-link"):
                    commons.require_operational_limits(packet)
            self.run_git(repository, "add", "work")
            self.run_git(repository, "commit", "-m", "Track malicious hardlink")
            hardlink_commit = self.run_git(repository, "rev-parse", "HEAD")
            with self.patched_root(repository):
                with self.assertRaisesRegex(ValueError, "multi-link"):
                    commons.require_tracked_head_file(
                        output,
                        "handoff artifact",
                        expected_commit=hardlink_commit,
                    )

            for unsafe_path, expected in (
                (f"work/{packet.packet_id}/CON.txt", "Windows-reserved"),
                (f"work/{packet.packet_id}/result.", "trailing character"),
            ):
                candidate = self.active_packet(repository, branch, base)
                candidate.body["execution_limits"]["allowed_output_paths"] = [unsafe_path]
                with self.subTest(unsafe_path=unsafe_path), self.patched_root(repository):
                    with self.assertRaisesRegex(ValueError, expected):
                        commons.require_operational_limits(candidate)

            with self.assertRaisesRegex(ValueError, "portable path collision"):
                commons.require_no_portable_path_collisions(
                    packet,
                    [f"work/{packet.packet_id}/Result.md"],
                    [
                        {
                            "command_id": "CHECK",
                            "dependency_paths": [
                                f"work/{packet.packet_id}/result.md"
                            ],
                        }
                    ],
                )

    def test_handoff_baseline_rejects_assume_unchanged_packet_bytes(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repository = Path(temporary)
            branch, base = self.make_git_repository(repository)
            packet = self.active_packet(repository, branch, base)
            packet.body["dependencies"] = []
            packet.body["source_inputs"] = []
            packet_path = repository / "packets" / "CAL-PACKET-001.json"
            packet_path.parent.mkdir()
            packet_path.write_text(
                json.dumps(packet.body, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
                newline="\n",
            )
            self.run_git(repository, "add", "packets/CAL-PACKET-001.json")
            self.run_git(repository, "commit", "-m", "Add packet")
            tracked_packet = commons.Packet(packet_path, packet.body)
            with self.patched_root(repository):
                handoff = commons.require_agent_handoff_state(tracked_packet)
            packet_path.write_text(
                packet_path.read_text(encoding="utf-8") + " ", encoding="utf-8"
            )
            self.run_git(
                repository,
                "update-index",
                "--assume-unchanged",
                "packets/CAL-PACKET-001.json",
            )
            self.assertEqual("", self.run_git(repository, "status", "--porcelain"))
            with self.patched_root(repository):
                limits = commons.require_operational_limits(tracked_packet)
                with self.assertRaisesRegex(
                    ValueError, "assume-unchanged|not byte-identical"
                ):
                    commons.require_handoff_repository_baseline(
                        tracked_packet, [packet_path], limits, handoff
                    )

    def test_handoff_baseline_rejects_ignored_input_and_output_paths(self) -> None:
        for ignored in ("packets/", "work/"):
            with self.subTest(ignored=ignored), tempfile.TemporaryDirectory() as temporary:
                repository = Path(temporary)
                branch, base = self.make_git_repository(repository)
                packet = self.active_packet(repository, branch, base)
                packet.body["dependencies"] = []
                packet.body["source_inputs"] = []
                packet_path = repository / "packets" / "CAL-PACKET-001.json"
                packet_path.parent.mkdir()
                packet_path.write_text(
                    json.dumps(packet.body, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8",
                    newline="\n",
                )
                self.run_git(repository, "add", "packets/CAL-PACKET-001.json")
                self.run_git(repository, "commit", "-m", "Add packet")
                (repository / ".gitignore").write_text(ignored + "\n", encoding="utf-8")
                self.run_git(repository, "add", ".gitignore")
                self.run_git(repository, "commit", "-m", "Add ignore rule")
                tracked_packet = commons.Packet(packet_path, packet.body)
                with self.patched_root(repository):
                    handoff = commons.require_agent_handoff_state(tracked_packet)
                    limits = commons.require_operational_limits(tracked_packet)
                    with self.assertRaisesRegex(ValueError, "ignored by repository rules"):
                        commons.require_handoff_repository_baseline(
                            tracked_packet, [packet_path], limits, handoff
                        )

    def test_handoff_baseline_rejects_mutable_output_aliasing_transitive_artifact(
        self,
    ) -> None:
        immutable_path = "work/CAL-PACKET-001/immutable-source.md"
        for output_path in (
            immutable_path,
            "work/CAL-PACKET-001/Immutable-Source.md",
        ):
            with self.subTest(output_path=output_path), tempfile.TemporaryDirectory(
            ) as temporary:
                repository = Path(temporary)
                branch, base = self.make_git_repository(repository)
                packet = self.active_packet(repository, branch, base)
                packet.body["dependencies"] = []
                packet.body["source_inputs"] = [
                    {
                        "source_record_id": "LIVE-SOURCE-001",
                        "record_version": "1.0.0",
                        "hashes": [{"algorithm": "sha256", "digest": "0" * 64}],
                        "permitted_uses": ["inspect"],
                    }
                ]
                packet.body["execution_limits"]["allowed_output_paths"] = [
                    output_path
                ]
                packet_path = repository / "packets" / "CAL-PACKET-001.json"
                source_path = repository / "sources" / "LIVE-SOURCE-001.json"
                artifact_path = repository.joinpath(*immutable_path.split("/"))
                packet_path.parent.mkdir()
                source_path.parent.mkdir()
                artifact_path.parent.mkdir(parents=True)
                packet_path.write_text(
                    json.dumps(packet.body) + "\n", encoding="utf-8", newline="\n"
                )
                source_path.write_text(
                    json.dumps(
                        {
                            "record_type": "source_record",
                            "record_version": "1.0.0",
                            "source_id": "LIVE-SOURCE-001",
                            "locator": {"canonical_reference": immutable_path},
                        }
                    )
                    + "\n",
                    encoding="utf-8",
                    newline="\n",
                )
                artifact_path.write_text(
                    "immutable input\n", encoding="utf-8", newline="\n"
                )
                self.run_git(repository, "add", "packets", "sources", "work")
                self.run_git(
                    repository, "commit", "-m", "Add colliding transitive input"
                )
                tracked_packet = commons.Packet(packet_path, packet.body)

                with self.patched_root(repository):
                    handoff = commons.require_agent_handoff_state(tracked_packet)
                    limits = commons.require_operational_limits(tracked_packet)
                    with self.assertRaisesRegex(
                        ValueError,
                        "allowed mutable output path.*immutable handoff artifact",
                    ):
                        commons.require_handoff_repository_baseline(
                            tracked_packet,
                            [packet_path, source_path],
                            limits,
                            handoff,
                        )

    def test_handoff_baseline_binds_transitive_record_and_artifact_bytes(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repository = Path(temporary)
            branch, base = self.make_git_repository(repository)
            packet = self.active_packet(repository, branch, base)
            packet.body["dependencies"] = []
            packet.body["source_inputs"] = [
                {
                    "source_record_id": "LIVE-SOURCE-001",
                    "record_version": "1.0.0",
                    "hashes": [{"algorithm": "sha256", "digest": "0" * 64}],
                    "permitted_uses": ["inspect"],
                }
            ]
            packet_path = repository / "packets" / "CAL-PACKET-001.json"
            source_path = repository / "sources" / "LIVE-SOURCE-001.json"
            artifact_path = repository / "sources" / "input.md"
            packet_path.parent.mkdir()
            source_path.parent.mkdir()
            packet_path.write_text(
                json.dumps(packet.body) + "\n", encoding="utf-8", newline="\n"
            )
            source_path.write_text(
                json.dumps(
                    {
                        "record_type": "source_record",
                        "record_version": "1.0.0",
                        "source_id": "LIVE-SOURCE-001",
                        "locator": {"canonical_reference": "sources/input.md"},
                    }
                )
                + "\n",
                encoding="utf-8",
                newline="\n",
            )
            artifact_path.write_text(
                "immutable input\n", encoding="utf-8", newline="\n"
            )
            self.run_git(repository, "add", "packets", "sources")
            self.run_git(repository, "commit", "-m", "Add transitive handoff inputs")
            tracked_packet = commons.Packet(packet_path, packet.body)
            with self.patched_root(repository):
                handoff = commons.require_agent_handoff_state(tracked_packet)
                limits = commons.require_operational_limits(tracked_packet)
                baseline = commons.require_handoff_repository_baseline(
                    tracked_packet, [packet_path, source_path], limits, handoff
                )
            self.assertEqual(
                ("packets/CAL-PACKET-001.json", "sources/LIVE-SOURCE-001.json"),
                baseline.record_paths,
            )
            self.assertEqual(("sources/input.md",), baseline.artifact_paths)

            artifact_path.write_text(
                "tampered input\n", encoding="utf-8", newline="\n"
            )
            self.run_git(
                repository, "update-index", "--assume-unchanged", "sources/input.md"
            )
            with self.patched_root(repository):
                with self.assertRaisesRegex(
                    ValueError, "assume-unchanged|not byte-identical"
                ):
                    commons.require_handoff_repository_baseline(
                        tracked_packet, [packet_path, source_path], limits, handoff
                    )

    def test_command_dependencies_reject_special_index_flags_and_ignore_aliases(
        self,
    ) -> None:
        for flag in ("--assume-unchanged", "--skip-worktree"):
            with self.subTest(flag=flag), tempfile.TemporaryDirectory() as temporary:
                repository = Path(temporary)
                branch, commit = self.make_git_repository(repository)
                self.run_git(repository, "update-index", flag, "README.md")
                with self.patched_root(repository):
                    packet = self.active_packet(repository, branch, commit)
                    with self.assertRaisesRegex(ValueError, "non-ordinary Git index"):
                        commons.require_agent_handoff_state(packet)
                    with self.assertRaisesRegex(
                        ValueError, "assume-unchanged|skip-worktree"
                    ):
                        commons.require_tracked_head_file(
                            repository / "README.md",
                            "acceptance command dependency",
                            expected_commit=commit,
                        )

        with tempfile.TemporaryDirectory() as temporary:
            repository = Path(temporary)
            _, _ = self.make_git_repository(repository)
            (repository / ".gitignore").write_text(
                "README.md\n", encoding="utf-8", newline="\n"
            )
            self.run_git(repository, "add", ".gitignore")
            self.run_git(repository, "commit", "-m", "Ignore tracked dependency")
            commit = self.run_git(repository, "rev-parse", "HEAD")
            with self.patched_root(repository):
                with self.assertRaisesRegex(ValueError, "ignored by repository rules"):
                    commons.require_tracked_head_file(
                        repository / "README.md",
                        "acceptance command dependency",
                        expected_commit=commit,
                    )

    def test_handoff_baseline_rejects_clean_commit_after_state_capture(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repository = Path(temporary)
            branch, base = self.make_git_repository(repository)
            packet = self.active_packet(repository, branch, base)
            packet.body["dependencies"] = []
            packet.body["source_inputs"] = []
            packet_path = repository / "packets" / "CAL-PACKET-001.json"
            packet_path.parent.mkdir()
            packet_path.write_text(
                json.dumps(packet.body, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
                newline="\n",
            )
            self.run_git(repository, "add", "packets/CAL-PACKET-001.json")
            self.run_git(repository, "commit", "-m", "Add packet")
            tracked_packet = commons.Packet(packet_path, packet.body)
            with self.patched_root(repository):
                handoff = commons.require_agent_handoff_state(tracked_packet)
                limits = commons.require_operational_limits(tracked_packet)

            (repository / "README.md").write_text(
                "changed after capture\n", encoding="utf-8", newline="\n"
            )
            self.run_git(repository, "add", "README.md")
            self.run_git(repository, "commit", "-m", "Concurrent clean commit")
            self.assertNotEqual(handoff.commit, self.run_git(repository, "rev-parse", "HEAD"))
            with self.patched_root(repository):
                with self.assertRaisesRegex(ValueError, "captured commit"):
                    commons.require_handoff_repository_baseline(
                        tracked_packet, [packet_path], limits, handoff
                    )

    def test_agent_brief_final_recheck_rejects_repository_change(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repository = Path(temporary)
            branch, base = self.make_git_repository(repository)
            packet = self.active_packet(repository, branch, base)
            arguments = argparse.Namespace(
                packet_root=Path("packets"),
                packet_id=packet.packet_id,
                expected_handoff_commit=base,
                approve_safety=True,
            )
            changed = False

            def change_repository(*_args, **_kwargs):
                nonlocal changed
                if not changed:
                    (repository / "README.md").write_text(
                        "changed during handoff\n", encoding="utf-8", newline="\n"
                    )
                    self.run_git(repository, "add", "README.md")
                    self.run_git(repository, "commit", "-m", "Race handoff")
                    changed = True
                return commons.HandoffInputs(
                    record_paths=("packets/CAL-PACKET-001.json",),
                    artifact_paths=(),
                    command_dependency_paths=("README.md",),
                )

            with self.patched_root(repository), mock.patch.object(
                commons, "select_packet", return_value=packet
            ), mock.patch.object(
                commons,
                "complete_collection_files",
                return_value=([packet.path], [packet.path]),
            ), mock.patch.object(
                commons, "collection_errors", return_value=[]
            ), mock.patch.object(
                commons,
                "require_handoff_repository_baseline",
                side_effect=change_repository,
            ):
                with self.assertRaisesRegex(ValueError, "changed while building"):
                    commons.command_agent_brief(arguments)

    def test_agent_brief_final_recheck_rejects_input_identity_change(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repository = Path(temporary)
            branch, base = self.make_git_repository(repository)
            packet = self.active_packet(repository, branch, base)
            arguments = argparse.Namespace(
                packet_root=Path("packets"),
                packet_id=packet.packet_id,
                expected_handoff_commit=base,
                approve_safety=True,
            )
            initial_inputs = commons.HandoffInputs(
                record_paths=("packets/CAL-PACKET-001.json",),
                artifact_paths=(),
                command_dependency_paths=("README.md",),
            )
            changed_inputs = commons.HandoffInputs(
                record_paths=("packets/CAL-PACKET-001.json",),
                artifact_paths=("sources/late-added-source.md",),
                command_dependency_paths=("README.md",),
            )

            with self.patched_root(repository), mock.patch.object(
                commons, "select_packet", return_value=packet
            ), mock.patch.object(
                commons,
                "complete_collection_files",
                return_value=([packet.path], [packet.path]),
            ), mock.patch.object(
                commons, "collection_errors", return_value=[]
            ), mock.patch.object(
                commons,
                "require_handoff_repository_baseline",
                side_effect=(initial_inputs, changed_inputs),
            ):
                with self.assertRaisesRegex(ValueError, "input identity changed"):
                    commons.command_agent_brief(arguments)

    def test_agent_brief_revalidates_collection_after_state_capture(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repository = Path(temporary)
            branch, base = self.make_git_repository(repository)
            packet = self.active_packet(repository, branch, base)
            arguments = argparse.Namespace(
                packet_root=Path("packets"),
                packet_id=packet.packet_id,
                expected_handoff_commit=base,
                approve_safety=True,
            )
            with self.patched_root(repository), mock.patch.object(
                commons, "select_packet", return_value=packet
            ), mock.patch.object(
                commons,
                "complete_collection_files",
                return_value=([packet.path], [packet.path]),
            ), mock.patch.object(
                commons,
                "collection_errors",
                return_value=["dependency changed after initial validation"],
            ), mock.patch.object(
                commons, "require_handoff_repository_baseline"
            ) as baseline:
                with self.assertRaisesRegex(ValueError, "exact pre-emission revalidation"):
                    commons.command_agent_brief(arguments)
            baseline.assert_not_called()

    def test_agent_brief_requires_explicit_nonzero_operational_limits(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repository = Path(temporary)
            branch, base = self.make_git_repository(repository)
            packet = self.active_packet(repository, branch, base)
            packet_without_limits = commons.Packet(
                packet.path,
                {key: copy.deepcopy(value) for key, value in packet.body.items() if key != "execution_limits"},
            )
            with self.patched_root(repository):
                with self.assertRaisesRegex(ValueError, "zero-authority default"):
                    commons.require_operational_limits(packet_without_limits)
                packet.body["execution_limits"]["maximum_cpu_seconds"] = 0
                with self.assertRaisesRegex(ValueError, "positive maximum_cpu_seconds"):
                    commons.require_operational_limits(packet)


if __name__ == "__main__":
    unittest.main()
