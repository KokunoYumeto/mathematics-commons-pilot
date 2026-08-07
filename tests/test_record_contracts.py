#!/usr/bin/env python3
"""Adversarial tests for durable problem and packet-transition contracts."""

from __future__ import annotations

import contextlib
import copy
import hashlib
import io
import json
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

import validate_packets  # noqa: E402


CALIBRATION = ROOT / "examples" / "calibration"


class DurableRecordContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.schema_set = validate_packets.load_schema_set(ROOT / "schemas")
        cls.base_paths = sorted(CALIBRATION.glob("*.json"))

    def collection_errors(self, mutations: dict[str, object]) -> list[str]:
        """Replace named records with schema-valid mutations and validate the set."""

        with tempfile.TemporaryDirectory() as temporary:
            temporary_root = Path(temporary)
            selected: list[Path] = []
            for base in self.base_paths:
                mutate = mutations.get(base.name)
                if mutate is None:
                    selected.append(base)
                    continue
                body = json.loads(base.read_text(encoding="utf-8"))
                mutate(body)  # type: ignore[operator]
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

    def write_record(
        self, directory: Path, name: str, body: dict[str, object]
    ) -> Path:
        path = directory / name
        path.write_text(
            json.dumps(body, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        self.assertEqual(
            [],
            validate_packets.validate_record_file(path, self.schema_set),
        )
        return path

    def synthetic_live_graph(
        self,
        repository_root: Path,
        *,
        calibration_copy: bool = False,
        include_ready_transition: bool = True,
    ) -> list[Path]:
        """Build a small exact-reference live graph from public record shapes."""

        records = repository_root / "records"
        artifacts = records / "artifacts"
        artifacts.mkdir(parents=True)

        def rewrite(value: object) -> object:
            if isinstance(value, dict):
                return {key: rewrite(child) for key, child in value.items()}
            if isinstance(value, list):
                return [rewrite(child) for child in value]
            if isinstance(value, str):
                rendered = value.replace(
                    "MC-PILOT-CALIBRATION", "MC-LIVE-SYNTHETIC"
                ).replace("CAL-", "LIVE-")
                if not calibration_copy:
                    rendered = rendered.replace(
                        "Calibration", "Live verification"
                    ).replace("calibration", "live verification")
                return rendered
            return value

        if calibration_copy:
            statement_bytes = (
                CALIBRATION / "artifacts" / "odd-sum-statement.md"
            ).read_bytes()
        else:
            statement_bytes = (
                b"# Synthetic live known-result statement\n\n"
                b"For every nonnegative integer n, the sum of the first n odd "
                b"positive integers equals n squared. This independent wording "
                b"exercises the live graph contract.\n"
            )
        statement_path = artifacts / "live-statement.md"
        statement_path.write_bytes(statement_bytes)
        statement_digest = hashlib.sha256(statement_bytes).hexdigest()

        source = rewrite(
            json.loads(
                (CALIBRATION / "source-record.json").read_text(encoding="utf-8")
            )
        )
        self.assertIsInstance(source, dict)
        source = source  # type: ignore[assignment]
        source["locator"]["canonical_reference"] = (
            "records/artifacts/live-statement.md"
        )
        source["integrity"].update(
            hashed_object_description=(
                "Exact UTF-8 bytes of records/artifacts/live-statement.md"
            ),
            byte_size=len(statement_bytes),
            hashes=[{"algorithm": "sha256", "digest": statement_digest}],
        )
        source_path = self.write_record(records, "source-record.json", source)
        source_record_digest = validate_packets.sha256_record_file(source_path)

        problem = rewrite(
            json.loads(
                (CALIBRATION / "problem-record.json").read_text(encoding="utf-8")
            )
        )
        self.assertIsInstance(problem, dict)
        problem = problem  # type: ignore[assignment]
        problem["statement"].update(
            artifact_path="records/artifacts/live-statement.md",
            byte_size=len(statement_bytes),
            hashes=[{"algorithm": "sha256", "digest": statement_digest}],
        )
        if not calibration_copy:
            problem["current_status"]["assessment_method"] = (
                "source_verified_known_result"
            )
        problem["source_refs"][0]["hashes"][0]["digest"] = source_record_digest
        problem_path = self.write_record(records, "problem-record.json", problem)
        problem_record_digest = validate_packets.sha256_record_file(problem_path)

        draft = rewrite(
            json.loads(
                (CALIBRATION / "research-packet-01-draft.json").read_text(
                    encoding="utf-8"
                )
            )
        )
        self.assertIsInstance(draft, dict)
        draft = draft  # type: ignore[assignment]
        draft["dependencies"][0]["hashes"][0]["digest"] = problem_record_digest
        draft["source_inputs"][0]["hashes"][0]["digest"] = source_record_digest
        draft_path = self.write_record(records, "research-packet-draft.json", draft)
        selected = [source_path, problem_path, draft_path]
        if not include_ready_transition:
            return selected

        ready = rewrite(
            json.loads(
                (CALIBRATION / "research-packet-02-ready.json").read_text(
                    encoding="utf-8"
                )
            )
        )
        self.assertIsInstance(ready, dict)
        ready = ready  # type: ignore[assignment]
        ready["dependencies"][0]["hashes"][0]["digest"] = problem_record_digest
        ready["source_inputs"][0]["hashes"][0]["digest"] = source_record_digest
        ready_path = self.write_record(records, "research-packet-ready.json", ready)

        transition = rewrite(
            json.loads(
                (
                    CALIBRATION / "packet-transition-01-draft-ready.json"
                ).read_text(encoding="utf-8")
            )
        )
        self.assertIsInstance(transition, dict)
        transition = transition  # type: ignore[assignment]
        transition["from_packet_ref"]["hashes"][0]["digest"] = (
            validate_packets.sha256_record_file(draft_path)
        )
        transition["to_packet_ref"]["hashes"][0]["digest"] = (
            validate_packets.sha256_record_file(ready_path)
        )
        transition_path = self.write_record(
            records, "packet-transition-draft-ready.json", transition
        )
        return [*selected, ready_path, transition_path]

    def successor_pair(
        self,
        directory: Path,
        *,
        from_snapshot_name: str = "research-packet-05-submitted.json",
        from_snapshot_path: Path | None = None,
        record_version: str = "1.5.0",
        to_status: str = "under_review",
        event_kind: str = "state_transition",
        sequence: int = 5,
        occurred_at: str = "2026-08-07T17:45:00Z",
        mutate_snapshot: object | None = None,
    ) -> tuple[Path, Path]:
        from_path = from_snapshot_path or (CALIBRATION / from_snapshot_name)
        from_body = json.loads(from_path.read_text(encoding="utf-8"))
        to_body = copy.deepcopy(from_body)
        to_body["record_version"] = record_version
        to_body["status"] = to_status
        to_body["updated_at"] = occurred_at
        to_body["scope"]["continuation_cursor"] = f"{to_status} snapshot"
        if mutate_snapshot is not None:
            mutate_snapshot(to_body)  # type: ignore[operator]
        to_path = self.write_record(
            directory, f"research-packet-{record_version}.json", to_body
        )

        event = json.loads(
            (
                CALIBRATION
                / "packet-transition-04-in-progress-submitted.json"
            ).read_text(encoding="utf-8")
        )
        event.update(
            transition_id=f"CAL-TRANSITION-{sequence:03d}",
            record_version="1.0.0",
            event_kind=event_kind,
            sequence=sequence,
            from_status=from_body["status"],
            to_status=to_status,
            occurred_at=occurred_at,
            reason="Append one immutable regression-test packet snapshot.",
            from_packet_ref={
                "packet_id": from_body["packet_id"],
                "record_version": from_body["record_version"],
                "hashes": [
                    {
                        "algorithm": "sha256",
                        "digest": validate_packets.sha256_record_file(from_path),
                    }
                ],
            },
            to_packet_ref={
                "packet_id": to_body["packet_id"],
                "record_version": to_body["record_version"],
                "hashes": [
                    {
                        "algorithm": "sha256",
                        "digest": validate_packets.sha256_record_file(to_path),
                    }
                ],
            },
        )
        event.pop("evidence_refs", None)
        event.pop("review_refs", None)
        event["submission_boundary"]["allowlisted_artifact_ids"] = []
        event["submission_rights"]["submitted_component_ids"] = [
            event["transition_id"]
        ]
        event_path = self.write_record(
            directory, f"packet-transition-{sequence:02d}.json", event
        )
        return to_path, event_path

    def test_calibration_is_one_non_novel_known_result_with_submitted_history(self) -> None:
        self.assertEqual(13, len(self.base_paths))
        problem = json.loads(
            (CALIBRATION / "problem-record.json").read_text(encoding="utf-8")
        )
        packet = json.loads(
            (CALIBRATION / "research-packet-05-submitted.json").read_text(
                encoding="utf-8"
            )
        )
        transitions = sorted(
            (
                json.loads(path.read_text(encoding="utf-8"))
                for path in CALIBRATION.glob("packet-transition-*.json")
            ),
            key=lambda record: record["sequence"],
        )
        snapshots = sorted(
            (
                json.loads(path.read_text(encoding="utf-8"))
                for path in CALIBRATION.glob("research-packet*.json")
            ),
            key=lambda record: record["record_version"],
        )

        self.assertEqual("known_result", problem["kind"])
        self.assertEqual("known_result", problem["current_status"]["assessment"])
        self.assertFalse(
            problem["current_status"]["tracker_or_model_agreement_sufficient"]
        )
        qualifications = " ".join(
            problem["current_status"]["caveats"] + problem["limitations"]["items"]
        ).lower()
        self.assertIn("not an open problem", qualifications)
        self.assertIn("no evidence", qualifications)
        self.assertEqual([problem["problem_id"]], packet["subject_ids"])
        problem_dependencies = [
            item
            for item in packet["dependencies"]
            if item["record_type"] == "problem_record"
        ]
        self.assertEqual(1, len(problem_dependencies))
        self.assertEqual(problem["problem_id"], problem_dependencies[0]["record_id"])
        self.assertEqual(problem["record_version"], problem_dependencies[0]["record_version"])
        self.assertEqual(
            validate_packets.sha256_record_file(CALIBRATION / "problem-record.json"),
            problem_dependencies[0]["hashes"][0]["digest"],
        )
        self.assertEqual(4, len(transitions))
        self.assertEqual(5, len(snapshots))
        self.assertEqual(
            [
                "draft",
                "ready",
                "claimed",
                "in_progress",
                "submitted",
            ],
            [snapshot["status"] for snapshot in snapshots],
        )
        self.assertEqual(list(range(1, 5)), [item["sequence"] for item in transitions])
        self.assertEqual("draft", transitions[0]["from_status"])
        self.assertEqual("submitted", transitions[-1]["to_status"])
        self.assertTrue(
            all(item["event_model"] == "append_only" for item in transitions)
        )
        self.assertTrue(
            all(item["event_kind"] == "state_transition" for item in transitions)
        )
        for index, transition in enumerate(transitions):
            self.assertEqual(
                snapshots[index]["record_version"],
                transition["from_packet_ref"]["record_version"],
            )
            self.assertEqual(
                snapshots[index + 1]["record_version"],
                transition["to_packet_ref"]["record_version"],
            )
        evidence = json.loads(
            (CALIBRATION / "evidence-record.json").read_text(encoding="utf-8")
        )
        submitted_evidence_digest = transitions[-1]["evidence_refs"][0]["hashes"][
            0
        ]["digest"]
        self.assertEqual(
            validate_packets.sha256_record_file(CALIBRATION / "evidence-record.json"),
            submitted_evidence_digest,
        )
        self.assertEqual("complete", evidence["status"])
        self.assertFalse(evidence["reproducibility"]["independently_reproduced"])
        self.assertNotEqual(evidence["hashes"][0]["digest"], submitted_evidence_digest)

        self.assertEqual(
            ["unclaimed", "unclaimed", "claimed", "active", "completed"],
            [snapshot["lease"]["status"] for snapshot in snapshots],
        )
        protected_base = "3fd7a29560e78ac3ecaa131707b61727c25ae9fd"
        self.assertTrue(
            all(
                snapshot["lease"]["base_commit"] == protected_base
                for snapshot in snapshots[2:]
            )
        )

    def test_problem_statement_and_source_bindings_match_exact_bytes(self) -> None:
        problem_path = CALIBRATION / "problem-record.json"
        problem = json.loads(problem_path.read_text(encoding="utf-8"))
        statement = problem["statement"]
        artifact = ROOT / statement["artifact_path"]
        payload = artifact.read_bytes()
        digest = next(
            item["digest"]
            for item in statement["hashes"]
            if item["algorithm"] == "sha256"
        )
        self.assertEqual(statement["byte_size"], len(payload))
        self.assertEqual(digest, hashlib.sha256(payload).hexdigest())
        self.assertEqual("new_record_version_required", statement["change_policy"])
        self.assertTrue(problem["source_refs"])
        self.assertTrue(problem["provenance"])

        third_party_wording = copy.deepcopy(problem)
        third_party_wording["statement"]["exactness"] = "verbatim_source_statement"
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "problem-record.json"
            path.write_text(
                json.dumps(third_party_wording, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
                newline="\n",
            )
            errors = validate_packets.validate_record_file(path, self.schema_set)
        self.assertIn(
            "must equal 'canonical_project_statement'", "\n".join(errors)
        )

    def test_calibration_timestamps_are_utc_and_not_future_dated(self) -> None:
        now = datetime.now(timezone.utc)

        def timestamps(value: object) -> list[str]:
            if isinstance(value, dict):
                found: list[str] = []
                for key, child in value.items():
                    if key.endswith("_at") and isinstance(child, str):
                        found.append(child)
                    found.extend(timestamps(child))
                return found
            if isinstance(value, list):
                found = []
                for child in value:
                    found.extend(timestamps(child))
                return found
            return []

        for path in self.base_paths:
            record = json.loads(path.read_text(encoding="utf-8"))
            for value in timestamps(record):
                self.assertTrue(value.endswith("Z"), f"non-UTC timestamp in {path}: {value}")
                parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
                self.assertLessEqual(parsed, now, f"future timestamp in {path}: {value}")

    def test_research_packet_rejects_unresolved_problem_subject(self) -> None:
        self.assert_collection_error(
            {
                "research-packet-05-submitted.json": lambda body: body.update(
                    subject_ids=["CAL-MISSING-PROBLEM"]
                )
            },
            "unresolved problem_record subject 'CAL-MISSING-PROBLEM'",
        )

    def test_research_packet_requires_exact_problem_version_and_digest(self) -> None:
        self.assert_collection_error(
            {
                "research-packet-05-submitted.json": lambda body: body.update(
                    dependencies=[]
                )
            },
            "lacks an exact problem_record dependency with matching version and digest",
        )
        self.assert_collection_error(
            {
                "research-packet-05-submitted.json": lambda body: body[
                    "dependencies"
                ][0]["hashes"][0].update(digest="0" * 64)
            },
            "normalized-record sha256 mismatch",
        )
        self.assert_collection_error(
            {
                "research-packet-05-submitted.json": lambda body: body[
                    "dependencies"
                ][0].update(record_version="9.9.9")
            },
            "unresolved problem_record reference 'CAL-ODD-SUM-IDENTITY' at exact record_version '9.9.9'",
        )

    def test_problem_rejects_bad_statement_hash_and_path_escape(self) -> None:
        self.assert_collection_error(
            {
                "problem-record.json": lambda body: body["statement"]["hashes"][
                    0
                ].update(digest="0" * 64)
            },
            "$.statement.hashes does not match exact artifact bytes",
        )

        body = json.loads(
            (CALIBRATION / "problem-record.json").read_text(encoding="utf-8")
        )
        body["statement"]["artifact_path"] = "../private-statement.md"
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "problem-record.json"
            path.write_text(
                json.dumps(body, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
                newline="\n",
            )
            errors = validate_packets.validate_record_file(path, self.schema_set)
        self.assertTrue(errors)
        self.assertIn("artifact_path", "\n".join(errors))

    def test_problem_requires_bound_status_and_provenance_sources(self) -> None:
        self.assert_collection_error(
            {
                "problem-record.json": lambda body: body["current_status"].update(
                    basis_source_ids=["CAL-MISSING-SOURCE"]
                )
            },
            "current-status assessment has unresolved or unbound basis sources",
        )
        self.assert_collection_error(
            {
                "problem-record.json": lambda body: body["provenance"][0].update(
                    source_record_ids=["CAL-MISSING-SOURCE"]
                )
            },
            "has unresolved or unbound sources",
        )

    def test_transition_rejects_illegal_and_discontinuous_steps(self) -> None:
        self.assert_collection_error(
            {
                "packet-transition-01-draft-ready.json": lambda body: body.update(
                    to_status="accepted"
                )
            },
            "illegal packet transition 'draft' -> 'accepted'",
        )
        self.assert_collection_error(
            {
                "packet-transition-02-ready-claimed.json": lambda body: body.update(
                    from_status="claimed", to_status="in_progress"
                )
            },
            "from_status does not match from-packet snapshot status",
        )

    def test_transition_rejects_packet_version_and_final_status_mismatch(self) -> None:
        self.assert_collection_error(
            {
                "packet-transition-01-draft-ready.json": lambda body: body.update(
                    from_packet_ref={
                        **body["from_packet_ref"],
                        "record_version": "9.9.9",
                    }
                )
            },
            "unresolved research_packet reference 'CAL-PACKET-001' at exact record_version '9.9.9'",
        )
        self.assert_collection_error(
            {
                "packet-transition-04-in-progress-submitted.json": lambda body: body.update(
                    to_status="rejected"
                )
            },
            "to_status does not match to-packet snapshot status",
        )

    def test_transition_rejects_duplicate_id_and_terminal_continuation(self) -> None:
        self.assert_collection_error(
            {
                "packet-transition-02-ready-claimed.json": lambda body: body.update(
                    transition_id="CAL-TRANSITION-001"
                )
            },
            "duplicate exact record identity ('packet_transition', 'CAL-TRANSITION-001', '1.0.0')",
        )
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            withdrawn, withdrawal = self.successor_pair(
                directory,
                record_version="1.5.0",
                to_status="withdrawn",
                sequence=5,
                occurred_at="2026-08-07T17:45:00Z",
            )
            closed, continuation = self.successor_pair(
                directory,
                from_snapshot_path=withdrawn,
                record_version="1.6.0",
                to_status="closed",
                sequence=6,
                occurred_at="2026-08-07T17:50:00Z",
            )
            errors = validate_packets.validate_collection(
                [
                    *self.base_paths,
                    withdrawn,
                    withdrawal,
                    closed,
                    continuation,
                ],
                self.schema_set,
            )
        self.assertIn(
            "transition follows terminal packet status 'withdrawn'",
            "\n".join(errors),
        )

    def test_transition_rejects_bad_chronology_and_commit(self) -> None:
        self.assert_collection_error(
            {
                "packet-transition-02-ready-claimed.json": lambda body: body.update(
                    occurred_at="2026-08-06T08:10:00Z"
                )
            },
            "transition timestamps must be strictly increasing",
        )
        self.assert_collection_error(
            {
                "packet-transition-03-claimed-in-progress.json": lambda body: body.update(
                    git_commit="0" * 40
                )
            },
            "git_commit must identify a real state/basis commit",
        )

    def test_require_live_excludes_examples_and_rejects_ambiguous_modes(self) -> None:
        fixture_parent = ROOT / "tests" / "fixtures" / "hardening"
        with tempfile.TemporaryDirectory(dir=fixture_parent) as temporary:
            temporary_root = Path(temporary)
            shutil.copytree(ROOT / "examples", temporary_root / "examples")
            shutil.copytree(ROOT / "work", temporary_root / "work")
            self.assertEqual(
                [], validate_packets.discover_live_instances(temporary_root)
            )

            output = io.StringIO()
            with mock.patch.object(validate_packets, "ROOT", temporary_root):
                with contextlib.redirect_stdout(output):
                    default_status = validate_packets.main([])
                    live_status = validate_packets.main(["--require-live"])
            rendered = output.getvalue()
            self.assertEqual(0, default_status)
            self.assertEqual(1, live_status)
            self.assertIn("default discovered collection", rendered)
            self.assertIn("calibration-only: no live packet queue exists", rendered)
            self.assertIn("cannot satisfy the Day-1 gate", rendered)

            live_dir = temporary_root / "records"
            live_dir.mkdir()
            (live_dir / "placeholder.json").write_text("{}\n", encoding="utf-8")
            self.assertEqual(
                [live_dir / "placeholder.json"],
                validate_packets.discover_live_instances(temporary_root),
            )

            (live_dir / "placeholder.json").unlink()
            shutil.copy2(
                CALIBRATION / "source-record.json",
                live_dir / "source-record.json",
            )
            with mock.patch.object(validate_packets, "ROOT", temporary_root):
                _, live_errors = validate_packets.validate_selected_paths(
                    schema_set=self.schema_set,
                    require_live=True,
                )
            self.assertIn(
                "no research_packet lineage or derived head",
                "\n".join(live_errors),
            )

        ambiguous_cases = [
            ["--require-live", "examples/calibration"],
            ["--require-live", "--schema-only"],
        ]
        for arguments in ambiguous_cases:
            with self.subTest(arguments=arguments):
                output = io.StringIO()
                with contextlib.redirect_stdout(output):
                    status = validate_packets.main(arguments)
                self.assertEqual(2, status)
                self.assertIn("cannot be combined", output.getvalue())

    def test_live_gate_rejects_calibration_copied_into_records(self) -> None:
        fixture_parent = ROOT / "tests" / "fixtures" / "hardening"
        with tempfile.TemporaryDirectory(dir=fixture_parent) as temporary:
            temporary_root = Path(temporary)
            shutil.copytree(ROOT / "examples", temporary_root / "examples")
            records = temporary_root / "records"
            records.mkdir()
            for name in (
                "source-record.json",
                "problem-record.json",
                "research-packet-01-draft.json",
            ):
                shutil.copy2(CALIBRATION / name, records / name)
            with mock.patch.object(validate_packets, "ROOT", temporary_root):
                _, errors = validate_packets.validate_selected_paths(
                    schema_set=self.schema_set,
                    require_live=True,
                )
        rendered = "\n".join(errors)
        self.assertIn("reserved by a published example/calibration", rendered)
        self.assertIn("live record points into examples/**", rendered)
        self.assertIn("no transition-backed actionable packet head", rendered)

    def test_live_gate_rejects_renamed_coherent_calibration(self) -> None:
        fixture_parent = ROOT / "tests" / "fixtures" / "hardening"
        with tempfile.TemporaryDirectory(dir=fixture_parent) as temporary:
            temporary_root = Path(temporary)
            self.synthetic_live_graph(
                temporary_root,
                calibration_copy=True,
                include_ready_transition=True,
            )
            with mock.patch.object(validate_packets, "ROOT", temporary_root):
                _, errors = validate_packets.validate_selected_paths(
                    schema_set=self.schema_set,
                    require_live=True,
                )
        rendered = "\n".join(errors)
        self.assertIn("calibration_designation", rendered)
        self.assertIn("exact problem statement bytes are reserved", rendered)

    def test_live_gate_requires_transition_backing_and_allows_known_results(self) -> None:
        fixture_parent = ROOT / "tests" / "fixtures" / "hardening"
        with tempfile.TemporaryDirectory(dir=fixture_parent) as temporary:
            temporary_root = Path(temporary)
            self.synthetic_live_graph(
                temporary_root,
                include_ready_transition=False,
            )
            with mock.patch.object(validate_packets, "ROOT", temporary_root):
                _, draft_errors = validate_packets.validate_selected_paths(
                    schema_set=self.schema_set,
                    require_live=True,
                )
        self.assertIn(
            "no transition-backed actionable packet head",
            "\n".join(draft_errors),
        )

        with tempfile.TemporaryDirectory(dir=fixture_parent) as temporary:
            temporary_root = Path(temporary)
            paths = self.synthetic_live_graph(temporary_root)
            problem = json.loads(
                next(path for path in paths if path.name == "problem-record.json").read_text(
                    encoding="utf-8"
                )
            )
            self.assertEqual("known_result", problem["kind"])
            with mock.patch.object(validate_packets, "ROOT", temporary_root):
                _, live_errors = validate_packets.validate_selected_paths(
                    schema_set=self.schema_set,
                    require_live=True,
                )
        self.assertEqual([], live_errors, "\n".join(live_errors))

    def test_transition_commit_is_defined_as_non_self_referential_basis(self) -> None:
        schema = json.loads(
            (ROOT / "schemas" / "packet-transition.schema.json").read_text(
                encoding="utf-8"
            )
        )
        description = schema["properties"]["git_commit"]["description"]
        self.assertIn("state/basis commit", description)
        self.assertIn("avoiding an impossible self-reference", description)

    def test_prior_snapshots_and_events_remain_byte_identical_when_appending(self) -> None:
        prior_bytes = {path: path.read_bytes() for path in self.base_paths}
        with tempfile.TemporaryDirectory() as temporary:
            successor, event = self.successor_pair(Path(temporary))
            selected = [*self.base_paths, successor, event]
            self.assertEqual(
                [], validate_packets.validate_collection(selected, self.schema_set)
            )
        self.assertEqual(prior_bytes, {path: path.read_bytes() for path in self.base_paths})

    def test_packet_history_rejects_forks_and_has_one_derived_head(self) -> None:
        heads = validate_packets.resolve_packet_heads(self.base_paths)
        self.assertEqual(1, len(heads))
        self.assertEqual("1.4.0", heads[0].record_version)
        self.assertEqual("submitted", heads[0].body["status"])

        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            successor, event = self.successor_pair(
                directory,
                from_snapshot_name="research-packet-04-in-progress.json",
                record_version="1.3.1",
                to_status="withdrawn",
                sequence=5,
            )
            errors = validate_packets.validate_collection(
                [*self.base_paths, successor, event], self.schema_set
            )
        rendered = "\n".join(errors)
        self.assertIn("packet history forks from exact snapshot", rendered)
        self.assertIn("one unambiguous head", rendered)

    def test_event_kind_and_diff_classes_prevent_silent_contract_rewrites(self) -> None:
        self.assert_collection_error(
            {
                "packet-transition-01-draft-ready.json": lambda body: body.update(
                    event_kind="record_revision"
                )
            },
            "record_revision must preserve packet status",
        )
        self.assert_collection_error(
            {
                "research-packet-03-claimed.json": lambda body: body[
                    "acceptance_criteria"
                ][0].update(description="Silently changed criterion")
            },
            "state_transition changes task-content fields outside its allowed diff class",
        )
        with tempfile.TemporaryDirectory() as temporary:
            successor, event = self.successor_pair(
                Path(temporary),
                from_snapshot_name="research-packet-04-in-progress.json",
                record_version="1.3.1",
                to_status="in_progress",
                event_kind="record_revision",
                sequence=4,
                occurred_at="2026-08-07T17:30:00Z",
                mutate_snapshot=lambda body: body["acceptance_criteria"][0].update(
                    description="Explicitly versioned criterion revision"
                ),
            )
            selected = [
                path
                for path in self.base_paths
                if path.name
                not in {
                    "packet-transition-04-in-progress-submitted.json",
                    "research-packet-05-submitted.json",
                }
            ]
            errors = validate_packets.validate_collection(
                [*selected, successor, event], self.schema_set
            )
        self.assertEqual([], errors, "\n".join(errors))

    def test_problem_successor_preserves_old_problem_and_packet_binding(self) -> None:
        problem_path = CALIBRATION / "problem-record.json"
        packet_paths = sorted(CALIBRATION.glob("research-packet*.json"))
        frozen_bytes = {
            path: path.read_bytes() for path in [problem_path, *packet_paths]
        }
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            successor = json.loads(problem_path.read_text(encoding="utf-8"))
            successor["record_version"] = "1.1.0"
            successor["previous_problem_ref"] = {
                "problem_id": successor["problem_id"],
                "record_version": "1.0.0",
                "hashes": [
                    {
                        "algorithm": "sha256",
                        "digest": validate_packets.sha256_record_file(problem_path),
                    }
                ],
            }
            successor["current_status"]["assessed_at"] = "2026-08-06T21:10:00Z"
            successor["current_status"]["qualified_label"] = (
                "Later calibration reaffirmation; still a known non-novel identity."
            )
            successor["updated_at"] = "2026-08-06T21:10:00Z"
            successor_path = self.write_record(
                directory, "problem-record-v1.1.0.json", successor
            )
            errors = validate_packets.validate_collection(
                [*self.base_paths, successor_path], self.schema_set
            )
        self.assertEqual([], errors, "\n".join(errors))
        self.assertEqual(
            frozen_bytes,
            {path: path.read_bytes() for path in [problem_path, *packet_paths]},
        )

    def test_problem_version_lineage_rejects_forks(self) -> None:
        problem_path = CALIBRATION / "problem-record.json"
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            successors: list[Path] = []
            for index, version in enumerate(("1.1.0", "1.2.0"), start=1):
                body = json.loads(problem_path.read_text(encoding="utf-8"))
                body["record_version"] = version
                body["previous_problem_ref"] = {
                    "problem_id": body["problem_id"],
                    "record_version": "1.0.0",
                    "hashes": [
                        {
                            "algorithm": "sha256",
                            "digest": validate_packets.sha256_record_file(problem_path),
                        }
                    ],
                }
                body["current_status"]["assessed_at"] = (
                    f"2026-08-06T21:1{index}:00Z"
                )
                body["updated_at"] = f"2026-08-06T21:1{index}:00Z"
                successors.append(
                    self.write_record(directory, f"problem-record-{version}.json", body)
                )
            errors = validate_packets.validate_collection(
                [*self.base_paths, *successors], self.schema_set
            )
        rendered = "\n".join(errors)
        self.assertIn("problem-record lineage forks from exact version", rendered)
        self.assertIn("one unambiguous head", rendered)

    def test_transition_basis_commit_exists_before_each_calibration_event(self) -> None:
        for path in CALIBRATION.glob("packet-transition-*.json"):
            event = json.loads(path.read_text(encoding="utf-8"))
            commit = event["git_commit"]
            completed = subprocess.run(
                ["git", "show", "-s", "--format=%cI", commit],
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(0, completed.returncode, completed.stderr)
            commit_time = datetime.fromisoformat(completed.stdout.strip())
            event_time = datetime.fromisoformat(
                event["occurred_at"].replace("Z", "+00:00")
            )
            self.assertLessEqual(commit_time, event_time)

    def test_checked_in_public_artifact_rejects_metadata_only_rights(self) -> None:
        self.assert_collection_error(
            {
                "source-record.json": lambda body: body[
                    "rights_assessment"
                ].update(redistribution_status="metadata_only")
            },
            "checked-in canonical source bytes require "
            "$.rights_assessment.redistribution_status 'permitted'",
        )

    def test_acceptance_command_requires_argv_and_safe_repository_cwd(self) -> None:
        packet = json.loads(
            (CALIBRATION / "research-packet-01-draft.json").read_text(
                encoding="utf-8"
            )
        )
        command = {
            "command_id": "CAL-COMMAND-001",
            "command": ["python", "-V"],
            "cwd": ".",
            "timeout_seconds": 30,
            "criterion_ids": [packet["acceptance_criteria"][0]["criterion_id"]],
        }
        packet["execution_limits"]["acceptance_commands"] = [command]

        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            for name, mutate, expected in (
                (
                    "string-command.json",
                    lambda body: body["execution_limits"]["acceptance_commands"][
                        0
                    ].update(command="python -V"),
                    "expected array",
                ),
                (
                    "parent-cwd.json",
                    lambda body: body["execution_limits"]["acceptance_commands"][
                        0
                    ].update(cwd="../outside"),
                    "does not match required pattern",
                ),
                (
                    "absolute-cwd.json",
                    lambda body: body["execution_limits"]["acceptance_commands"][
                        0
                    ].update(cwd="C:/outside"),
                    "does not match required pattern",
                ),
            ):
                candidate = copy.deepcopy(packet)
                mutate(candidate)
                path = directory / name
                path.write_text(
                    json.dumps(candidate, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8",
                    newline="\n",
                )
                rendered = "\n".join(
                    validate_packets.validate_record_file(path, self.schema_set)
                )
                self.assertIn(expected, rendered, rendered)

    def test_packet_output_allowlist_is_confined_to_packet_work_namespace(self) -> None:
        self.assert_collection_error(
            {
                "research-packet-01-draft.json": lambda body: body[
                    "execution_limits"
                ].update(
                    allowed_output_paths=[
                        "examples/calibration/artifacts/odd-sum-proof.md"
                    ]
                )
            },
            "must be inside 'work/CAL-PACKET-001/'",
        )


if __name__ == "__main__":
    unittest.main()
