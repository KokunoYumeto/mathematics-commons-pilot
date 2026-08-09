from __future__ import annotations

import contextlib
import copy
import hashlib
import io
import json
import os
import shutil
import socket
import subprocess
import sys
import tempfile
import unittest
import webbrowser
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
PRODUCTION_FIXTURE = (
    ROOT
    / "tests"
    / "fixtures"
    / "interlanguage-adoption"
    / "5f41b18467c315aee5f465894dd85a277081c74e"
)
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import validate_adoption_snapshot as adoption  # noqa: E402


def json_bytes(value: object) -> bytes:
    return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


def stream_identity(entries: list[dict[str, object]]) -> tuple[int, str]:
    stream = "".join(
        f"{entry['path']}\t{entry['bytes']}\t{entry['sha256']}\n"
        for entry in entries
    ).encode("utf-8")
    return len(stream), hashlib.sha256(stream).hexdigest().upper()


def file_set(
    entries: list[dict[str, object]], *, links: bool, **extra: object
) -> dict[str, object]:
    stream_bytes, tree_sha256 = stream_identity(entries)
    value: dict[str, object] = {
        "files": len(entries),
        "bytes": sum(int(entry["bytes"]) for entry in entries),
        "canonical_stream_bytes": stream_bytes,
        "tree_sha256": tree_sha256,
    }
    if links:
        value.update(
            {
                "local_links": sum(int(entry["local_links"]) for entry in entries),
                "external_links": sum(int(entry["external_links"]) for entry in entries),
                "missing_local_links": 0,
            }
        )
    value.update(extra)
    value["files_exact"] = entries
    return value


def base_item(item_id: str, lane: str) -> dict[str, object]:
    item: dict[str, object] = {
        "id": item_id,
        "author": "Ada Example",
        "work": f"Work {item_id}",
        "series": None,
        "corpus": "test_corpus",
        "lane_state": lane,
        "coverage_state": "bounded_cursor",
        "adoption_status": "open_parallel_mirrors_welcome",
        "priority": "high",
        "readiness": "exact_cursor",
        "owner": None,
        "owner_scope": "unclaimed coordination row",
        "languages": ["en"],
        "archive_path": "docs/work-queue.md#test",
        "related_paths": [],
        "source_basis": "bounded public test fixture",
        "next_cursor": "continue from the exact cursor",
        "prerequisites": ["inspect the pinned archive row"],
        "workflow": ["bounded_continuation"],
        "claim_url": adoption.CLAIM_URL,
        "updated": "2026-08-09",
        "notes": "Coordination metadata only.",
    }
    if lane == "current_work":
        item.update(
            {
                "adoption_status": "maintained_parallel_review_welcome",
                "readiness": "active",
                "owner": "Current Maintainer",
                "archive_path": "docs/test-map.md",
                "related_paths": ["docs/known-gaps.md#test"],
            }
        )
    elif lane == "future":
        item.update(
            {
                "adoption_status": "future_evidence_needed",
                "readiness": "source_discovery_first",
                "owner": None,
                "archive_path": "README.md",
            }
        )
    return item


class SnapshotFixture:
    commit = "a" * 40
    tree = "1" * 40
    validation_commit = "b" * 40
    evidence_commit = "c" * 40
    map_commit = "d" * 40
    evidence_closure_commit = "f" * 40

    def __init__(self, root: Path):
        self.root = root
        (root / "manifests" / "github-custody").mkdir(parents=True)
        self.paths = {
            "board": root / adoption.BOARD_PATH,
            "schema": root / adoption.SCHEMA_PATH,
            "check": root / adoption.CHECK_PATH,
            "map_manifest": root / adoption.MAP_PATH,
        }
        self.board = self.make_board()
        self.schema = self.make_schema()
        self.map_manifest = self.make_map_manifest()
        self.write("board", self.board)
        self.write("schema", self.schema)
        self.write("map_manifest", self.map_manifest)
        self.aggregate = {
            "items": 3,
            "mirrors": 0,
            "current_work": 1,
            "ready_for_adoption": 1,
            "future": 1,
            "unique_item_ids": 3,
            "unique_mirror_ids": 0,
            "required_maps": 1,
            "represented_required_maps": 1,
            "missing_required_maps": 0,
            "queue_sources": 2,
            "represented_queue_sources": 2,
            "missing_queue_sources": 0,
            "human_board_rows": 3,
            "represented_human_board_items": 3,
            "missing_human_board_items": 0,
            "unknown_human_board_ids": 0,
            "duplicate_human_board_ids": 0,
            "repository_path_checks": 20,
            "tracked_repository_paths": 20,
        }
        self.check = self.make_check()
        self.write("check", self.check)
        self.pin: dict[str, object] = {}
        self.rebind()

    def make_board(self) -> dict[str, object]:
        return {
            "schema": "math-commons-adoption-v1",
            "schema_url": adoption.SCHEMA_PATH,
            "validation": adoption.CHECK_PATH,
            "board_role": "operational_layer",
            "updated": "2026-08-09",
            "evidence_base_commit": self.evidence_commit,
            "repository": adoption.REPOSITORY_URL,
            "human_board": "docs/adopt.md",
            "archive_authority": {
                "coverage_maps": "docs/github-maps.md",
                "reader_shelf": "reader-pdfs/README.md",
                "source_shelf": "sources/README.md",
                "archive_history": "docs/github-archive.md",
            },
            "map_manifest": adoption.MAP_PATH,
            "required_maps": ["docs/test-map.md"],
            "queue_sources": list(adoption.QUEUE_SOURCES),
            "snapshot_policy": {
                "stable_locator_ref": "main",
                "immutable_unit": "human_approved_exact_commit",
                "same_commit_paths": list(adoption.SNAPSHOT_PATHS),
                "required_checks": list(adoption.REQUIRED_CHECKS),
                "mixed_revisions_forbidden": True,
            },
            "consumer_helper": adoption.CONSUMER_HELPER_PATH,
            "claim_interface": adoption.CLAIM_URL,
            "handback_interface": adoption.HANDBACK_URL,
            "enums": {
                "lane_state": list(adoption.LANE_STATES),
                "priority": list(adoption.PRIORITIES),
                "readiness": list(adoption.READINESS),
                "adoption_status": list(adoption.ADOPTION_STATUSES),
                "mirror_status": list(adoption.MIRROR_STATUSES),
            },
            "fields": list(adoption.ITEM_FIELDS),
            "mirror_fields": list(adoption.MIRROR_FIELDS),
            "mirrors": [],
            "items": [
                base_item("current-item", "current_work"),
                base_item("ready-item", "ready_for_adoption"),
                base_item("future-item", "future"),
            ],
        }

    def make_schema(self) -> dict[str, object]:
        return {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "$id": (
                "https://raw.githubusercontent.com/KokunoYumeto/"
                "modern-latex-manuscripts/main/manifests/adopt.schema.json"
            ),
            "title": "Mathematics Commons adoption board",
            "type": "object",
            "required": list(adoption.TOP_REQUIRED),
            "properties": {
                "schema": {"const": "math-commons-adoption-v1"},
                "schema_url": {"const": adoption.SCHEMA_PATH},
                "validation": {"const": adoption.CHECK_PATH},
                "map_manifest": {"const": adoption.MAP_PATH},
                "consumer_helper": {"const": adoption.CONSUMER_HELPER_PATH},
                "claim_interface": {"const": adoption.CLAIM_URL},
                "handback_interface": {"const": adoption.HANDBACK_URL},
            },
            "additionalProperties": True,
            "$defs": {
                "item": {
                    "required": list(adoption.ITEM_FIELDS),
                    "additionalProperties": False,
                },
                "mirror": {
                    "required": list(adoption.MIRROR_FIELDS),
                    "additionalProperties": False,
                },
            },
        }

    def make_map_manifest(self) -> dict[str, object]:
        predecessor_entry = {
            "path": "docs/test-map.md",
            "bytes": 9,
            "sha256": "A" * 64,
            "local_links": 1,
            "external_links": 0,
        }
        current_entry = {
            "path": "docs/test-map.md",
            "bytes": 10,
            "sha256": "B" * 64,
            "local_links": 2,
            "external_links": 0,
        }
        evidence_entry = {
            "path": "manifests/test-evidence.json",
            "bytes": 7,
            "sha256": "C" * 64,
        }
        predecessor_set = file_set(
            [predecessor_entry],
            links=True,
            unchanged_from_predecessor=0,
            changed_from_predecessor=1,
        )
        current_set = file_set(
            [current_entry],
            links=True,
            unchanged_from_predecessor=0,
            changed_from_predecessor=1,
        )
        evidence_set = file_set(
            [evidence_entry],
            links=False,
            derivation="bounded test evidence",
            added=[evidence_entry],
        )
        return {
            "schema": "github-map-index/v6",
            "observed_date": "2026-08-09",
            "repository": adoption.REPOSITORY_NAME,
            "branch": "test-branch",
            "observed_commit": self.map_commit,
            "scope": "bounded test manifest",
            "canonical_stream": "path<TAB>bytes<TAB>SHA256<LF>",
            "predecessor": {
                "path": "manifests/previous.json",
                "commit": "e" * 40,
                "bytes": 123,
                "sha256": "D" * 64,
                "map_set": predecessor_set,
                "disposition": "test predecessor",
            },
            "current_map_set": current_set,
            "changed_maps": [current_entry],
            "current_explicit_evidence_set": evidence_set,
            "excluded_scope": {
                "policy": "not inspected",
                "entries_listed": False,
            },
            "checks": {
                "predecessor_identity_replay": "1/1",
                "current_map_identity_replay": "1/1",
                "unchanged_map_identity_replay": "0/0",
                "changed_map_identity_replay": "1/1",
                "current_explicit_evidence_identity_replay": "1/1",
                "local_link_replay": "2/2",
                "missing_local_links": 0,
                "prohibited_targets": 0,
                "external_requests": 0,
                "producer_files_mutated": False,
                "compile_render_or_ocr_run": False,
                "zenodo_network_queried": False,
                "global_filesystem_search": False,
                "prohibited_or_revoked_roots_inspected": False,
            },
        }

    def make_check(self) -> dict[str, object]:
        return {
            "schema": "math-commons-adoption-check-v1",
            "status": "PASS",
            "errors": [],
            "observed_date": "2026-08-09",
            "observed_commit": self.validation_commit,
            "board": {},
            "schema_file": {},
            "map_manifest": {},
            "human_board": {},
            "snapshot_policy": {
                "stable_locator_ref": "main",
                "immutable_unit": "human_approved_exact_commit",
                "same_commit_paths": 4,
                "required_checks": 4,
                "mixed_revisions_forbidden": True,
            },
            "consumer_helper": adoption.CONSUMER_HELPER_PATH,
            "aggregate": copy.deepcopy(self.aggregate),
            "checks": copy.deepcopy(adoption.CHECK_FLAGS),
        }

    def write(self, role: str, value: object) -> None:
        self.paths[role].write_bytes(json_bytes(value))

    def write_raw(self, role: str, payload: bytes) -> None:
        self.paths[role].write_bytes(payload)

    def identity(self, role: str) -> dict[str, object]:
        payload = self.paths[role].read_bytes()
        return {
            "role": role,
            "path": self.paths[role].relative_to(self.root).as_posix(),
            "bytes": len(payload),
            "sha256": hashlib.sha256(payload).hexdigest(),
        }

    def rebind(self) -> None:
        identities = {
            role: self.identity(role)
            for role in ("board", "schema", "map_manifest")
        }
        self.check["board"] = {
            "path": identities["board"]["path"],
            "bytes": identities["board"]["bytes"],
            "sha256": str(identities["board"]["sha256"]).upper(),
            "schema": "math-commons-adoption-v1",
        }
        self.check["schema_file"] = {
            "path": identities["schema"]["path"],
            "bytes": identities["schema"]["bytes"],
            "sha256": str(identities["schema"]["sha256"]).upper(),
            "draft": "https://json-schema.org/draft/2020-12/schema",
        }
        self.check["map_manifest"] = {
            "path": identities["map_manifest"]["path"],
            "bytes": identities["map_manifest"]["bytes"],
            "sha256": str(identities["map_manifest"]["sha256"]).upper(),
            "required_maps": int(self.aggregate["required_maps"]),
        }
        human_projection = self.pin.get("optional_human_projection") if self.pin else None
        if not isinstance(human_projection, dict):
            human_projection = {
                "path": adoption.HUMAN_BOARD_PATH,
                "bytes": 321,
                "sha256": "9" * 64,
            }
        self.check["human_board"] = {
            "path": human_projection["path"],
            "bytes": human_projection["bytes"],
            "sha256": str(human_projection["sha256"]).upper(),
            "rows": int(self.aggregate["human_board_rows"]),
        }
        self.write("check", self.check)
        identities["check"] = self.identity("check")
        ordered_identities = [
            identities[role]
            for role in ("board", "schema", "check", "map_manifest")
        ]
        self.pin = {
            "schema": "mathematics-commons-adoption-pin-v1",
            "repository": adoption.REPOSITORY_URL,
            "approved_snapshot_commit": self.commit,
            "approved_snapshot_tree": self.tree,
            "validation_source_commit": self.validation_commit,
            "evidence_closure_commit": self.evidence_closure_commit,
            "evidence_base_commit": self.evidence_commit,
            "map_observation_commit": self.map_commit,
            "discovery_ref": "main",
            "discovery_ref_role": "locator_only_not_an_immutable_snapshot",
            "snapshot_paths": list(adoption.SNAPSHOT_PATHS),
            "files": ordered_identities,
            "optional_human_projection": {
                "role": "human_board",
                "path": adoption.HUMAN_BOARD_PATH,
                "bytes": 321,
                "sha256": "9" * 64,
                "machine_required": False,
            },
            "sealed_public_receipts": [
                {
                    "role": "source_readback",
                    "path": "manifests/published-github/test-readback.json",
                    "bytes": 456,
                    "sha256": "7" * 64,
                    "machine_required": False,
                },
                {
                    "role": "link_audit",
                    "path": "manifests/github-custody/test-links.json",
                    "bytes": 789,
                    "sha256": "8" * 64,
                    "machine_required": False,
                },
            ],
            "expected_aggregate": {
                key: self.aggregate[key]
                for key in adoption.PRODUCTION_EXPECTED_AGGREGATE
            },
            "trust_boundary": copy.deepcopy(adoption.TRUST_BOUNDARY),
        }

    def validate(self) -> adoption.ValidatedSnapshot:
        return adoption.validate_snapshot(
            self.root, pin=copy.deepcopy(self.pin), production=False
        )


class AdoptionSnapshotTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.fixture = SnapshotFixture(self.root)

    def assert_validation_error(self, fragment: str) -> adoption.SnapshotValidationError:
        with self.assertRaises(adoption.SnapshotValidationError) as caught:
            self.fixture.validate()
        self.assertIn(fragment, "\n".join(caught.exception.errors))
        return caught.exception

    def test_production_pin_matches_compiled_trust_anchor(self) -> None:
        pin = adoption._read_pin()  # noqa: SLF001 - intentional contract audit
        errors: list[str] = []
        adoption._validate_pin(pin, errors, production=True)  # noqa: SLF001
        self.assertEqual(errors, [])
        self.assertEqual(
            pin["approved_snapshot_commit"], adoption.PRODUCTION_APPROVED_COMMIT
        )
        self.assertEqual(pin["approved_snapshot_tree"], adoption.PRODUCTION_APPROVED_TREE)
        self.assertEqual(
            tuple(
                (entry["role"], entry["path"], entry["bytes"], entry["sha256"])
                for entry in pin["sealed_public_receipts"]
            ),
            adoption.SEALED_PUBLIC_RECEIPTS,
        )

    def test_exact_production_snapshot_passes_inertly(self) -> None:
        self.assertTrue(PRODUCTION_FIXTURE.is_dir())
        with (
            mock.patch.object(socket.socket, "connect", side_effect=AssertionError("network used")),
            mock.patch.object(subprocess, "run", side_effect=AssertionError("command run")),
            mock.patch.object(subprocess, "Popen", side_effect=AssertionError("command spawned")),
            mock.patch.object(os, "system", side_effect=AssertionError("shell used")),
            mock.patch.object(webbrowser, "open", side_effect=AssertionError("browser used")),
        ):
            snapshot = adoption.validate_snapshot(PRODUCTION_FIXTURE)
            selected = adoption.select_items(
                snapshot,
                lane_states=None,
                priorities=None,
                readiness=None,
                language=None,
                query="gauss",
                unowned=False,
                limit=10,
            )
            rendered = adoption._render_text(snapshot, selected)  # noqa: SLF001
        self.assertEqual(snapshot.aggregate["items"], 46)
        self.assertEqual(snapshot.aggregate["repository_path_checks"], 122)
        self.assertEqual([item["id"] for item in selected], ["gauss-werke-ii"])
        self.assertIn(adoption.PRODUCTION_APPROVED_COMMIT, rendered)
        self.assertIn("[ready_for_adoption; high; exact_cursor]", rendered)
        self.assertIn("pinned archive: https://github.com/", rendered)

    def test_generated_snapshot_passes_compiled_contract(self) -> None:
        snapshot = self.fixture.validate()
        self.assertEqual(snapshot.aggregate["items"], 3)
        self.assertEqual(snapshot.aggregate["repository_path_checks"], 20)
        self.assertEqual(snapshot.check["status"], "PASS")

    def test_default_projection_is_ready_only_and_deterministic(self) -> None:
        snapshot = self.fixture.validate()
        selected = adoption.select_items(
            snapshot,
            lane_states=None,
            priorities=None,
            readiness=None,
            language=None,
            query=None,
            unowned=False,
            limit=20,
        )
        self.assertEqual([item["id"] for item in selected], ["ready-item"])
        payload = adoption._candidate_payload(snapshot, selected)  # noqa: SLF001
        self.assertEqual(payload["authority"], "coordination_metadata_only_not_mathematical_evidence")
        self.assertEqual(payload["application_http_api_requests_performed"], 0)
        self.assertEqual(payload["live_packets_created"], 0)
        self.assertEqual(payload["interfaces"]["claim"], adoption.CLAIM_URL)
        self.assertEqual(payload["interfaces"]["handback"], adoption.HANDBACK_URL)
        self.assertEqual(
            payload["interfaces"]["consumer_helper"], adoption.CONSUMER_HELPER_PATH
        )
        self.assertEqual(payload["source"]["approved_snapshot_tree"], self.fixture.tree)
        self.assertEqual(len(payload["source"]["contract_files"]), 4)
        self.assertIs(
            payload["source"]["optional_human_projection"]["machine_required"], False
        )
        self.assertEqual(len(payload["source"]["sealed_public_receipts"]), 2)
        self.assertNotIn("record_type", json.dumps(payload))

    def test_sealed_receipts_are_provenance_not_additional_inputs(self) -> None:
        snapshot = self.fixture.validate()
        required_paths = [entry["path"] for entry in snapshot.pin["files"]]
        receipt_paths = [
            entry["path"] for entry in snapshot.pin["sealed_public_receipts"]
        ]
        self.assertEqual(len(required_paths), 4)
        self.assertTrue(set(required_paths).isdisjoint(receipt_paths))
        self.assertTrue(
            all(entry["machine_required"] is False for entry in snapshot.pin["sealed_public_receipts"])
        )
        pin = copy.deepcopy(self.fixture.pin)
        pin["sealed_public_receipts"][0]["machine_required"] = True
        with self.assertRaises(adoption.SnapshotValidationError) as caught:
            adoption.validate_snapshot(self.root, pin=pin, production=False)
        self.assertIn("must remain false", "\n".join(caught.exception.errors))

    def test_filtering_by_lane_language_query_and_unowned(self) -> None:
        snapshot = self.fixture.validate()
        selected = adoption.select_items(
            snapshot,
            lane_states=list(adoption.LANE_STATES),
            priorities=["high"],
            readiness=list(adoption.READINESS),
            language="EN",
            query="work ready",
            unowned=True,
            limit=5,
        )
        self.assertEqual([item["id"] for item in selected], ["ready-item"])

    def test_unbound_byte_tampering_fails_before_semantic_use(self) -> None:
        tampered = self.fixture.paths["board"].read_bytes() + b" "
        self.fixture.paths["board"].write_bytes(tampered)
        error = self.assert_validation_error("snapshot file manifests/adopt.json")
        self.assertTrue(any("approved bounded byte length" in item for item in error.errors))
        self.assertNotIn(hashlib.sha256(tampered).hexdigest(), "\n".join(error.errors))

    def test_mixed_revision_check_file_is_rejected_even_when_it_says_pass(self) -> None:
        self.fixture.check["observed_commit"] = "f" * 40
        self.fixture.write("check", self.fixture.check)
        self.assert_validation_error("snapshot file manifests/adopt.check.json")

    def test_rebound_check_must_still_bind_validation_source(self) -> None:
        self.fixture.check["observed_commit"] = "f" * 40
        self.fixture.rebind()
        self.assert_validation_error("observed_commit")

    def test_pass_with_nonempty_errors_is_rejected(self) -> None:
        self.fixture.check["errors"] = ["hidden failure"]
        self.fixture.rebind()
        self.assert_validation_error("must be an empty array")

    def test_claim_handback_and_consumer_helper_bindings_are_exact(self) -> None:
        mutations = (
            ("claim_interface", "https://example.invalid/claim", "approved issue route"),
            ("handback_interface", "https://example.invalid/return", "approved handback route"),
            ("consumer_helper", "scripts/other.py", "must equal 'scripts/get-adopt.py'"),
        )
        for field, value, fragment in mutations:
            with self.subTest(field=field):
                child = self.root / field
                fixture = SnapshotFixture(child)
                fixture.board[field] = value
                fixture.write("board", fixture.board)
                fixture.rebind()
                with self.assertRaises(adoption.SnapshotValidationError) as caught:
                    fixture.validate()
                self.assertIn(fragment, "\n".join(caught.exception.errors))

    def test_human_projection_receipt_is_pinned_but_not_a_fifth_input(self) -> None:
        self.fixture.check["human_board"]["bytes"] = 999
        self.fixture.write("check", self.fixture.check)
        new_identity = self.fixture.identity("check")
        for entry in self.fixture.pin["files"]:
            if entry["role"] == "check":
                entry.update(new_identity)
        error = self.assert_validation_error("does not match the pinned optional projection")
        self.assertNotIn(adoption.HUMAN_BOARD_PATH, [entry["path"] for entry in self.fixture.pin["files"]])
        self.assertIn("human_board", "\n".join(error.errors))

    def test_pin_rejects_casefold_colliding_machine_paths(self) -> None:
        pin = copy.deepcopy(self.fixture.pin)
        pin["files"][1]["path"] = pin["files"][0]["path"].upper()
        with self.assertRaises(adoption.SnapshotValidationError) as caught:
            adoption.validate_snapshot(self.root, pin=pin, production=False)
        self.assertIn("collides portably", "\n".join(caught.exception.errors))

    def test_duplicate_json_keys_are_rejected_after_valid_rebinding(self) -> None:
        original = self.fixture.paths["board"].read_bytes()
        duplicate = b'{"schema":"shadow",' + original[1:]
        self.fixture.write_raw("board", duplicate)
        self.fixture.rebind()
        self.assert_validation_error("duplicate JSON key")

    def test_nonfinite_json_numbers_are_rejected(self) -> None:
        raw = self.fixture.paths["board"].read_bytes()
        injected = raw.rstrip()[:-1] + b',"nonfinite":NaN}\n'
        self.fixture.write_raw("board", injected)
        self.fixture.rebind()
        self.assert_validation_error("non-finite JSON number")

    def test_bom_and_crlf_are_rejected_even_when_rebound(self) -> None:
        for name, transform, fragment in (
            ("bom", lambda data: b"\xef\xbb\xbf" + data, "without a BOM"),
            ("crlf", lambda data: data.replace(b"\n", b"\r\n"), "LF line endings"),
        ):
            with self.subTest(name=name):
                child = self.root / name
                fixture = SnapshotFixture(child)
                fixture.write_raw("board", transform(fixture.paths["board"].read_bytes()))
                fixture.rebind()
                with self.assertRaises(adoption.SnapshotValidationError) as caught:
                    fixture.validate()
                self.assertIn(fragment, "\n".join(caught.exception.errors))

    def test_schema_identity_is_not_accepted_from_hash_alone(self) -> None:
        self.fixture.schema["$id"] = "https://example.invalid/schema.json"
        self.fixture.write("schema", self.fixture.schema)
        self.fixture.rebind()
        self.assert_validation_error("does not identify the upstream board schema")

    def test_item_extra_field_and_duplicate_id_are_rejected(self) -> None:
        self.fixture.board["items"][0]["surprise"] = True
        self.fixture.board["items"][1]["id"] = "current-item"
        self.fixture.write("board", self.fixture.board)
        self.fixture.rebind()
        error = self.assert_validation_error("contains undeclared keys")
        self.assertIn("duplicate item IDs", "\n".join(error.errors))

    def test_every_lane_conditional_is_enforced(self) -> None:
        mutations = (
            (0, "owner", None, "must identify an owner"),
            (0, "readiness", "review_ready", "must be active for current work"),
            (1, "archive_path", None, "must be nonempty for adoption-ready work"),
            (2, "owner", "Someone", "must be null for future work"),
            (2, "adoption_status", "open_parallel_mirrors_welcome", "must be future_evidence_needed"),
            (2, "readiness", "intake_ready", "must be source_discovery_first"),
        )
        for index, field, value, fragment in mutations:
            with self.subTest(index=index, field=field):
                child = self.root / f"lane-{index}-{field}-{len(str(value))}"
                fixture = SnapshotFixture(child)
                fixture.board["items"][index][field] = value
                fixture.write("board", fixture.board)
                fixture.rebind()
                with self.assertRaises(adoption.SnapshotValidationError) as caught:
                    fixture.validate()
                self.assertIn(fragment, "\n".join(caught.exception.errors))

    def test_orphan_and_duplicate_mirrors_are_rejected(self) -> None:
        mirror = {
            "id": "mirror-one",
            "item_id": "missing-item",
            "owner": "Mirror Operator",
            "scope": "bounded review",
            "url": "https://example.invalid/mirror",
            "status": "active",
            "updated": "2026-08-09",
        }
        self.fixture.board["mirrors"] = [mirror, copy.deepcopy(mirror)]
        self.fixture.write("board", self.fixture.board)
        self.fixture.rebind()
        error = self.assert_validation_error("duplicate mirror IDs")
        self.assertIn("does not resolve to an item", "\n".join(error.errors))

    def test_required_map_and_queue_sources_need_operational_rows(self) -> None:
        self.fixture.board["items"][0]["archive_path"] = "README.md"
        self.fixture.board["items"][0]["related_paths"] = []
        self.fixture.board["items"][1]["archive_path"] = "README.md"
        self.fixture.write("board", self.fixture.board)
        self.fixture.rebind()
        error = self.assert_validation_error("not represented by operational rows")
        joined = "\n".join(error.errors)
        self.assertIn("docs/test-map.md", joined)
        self.assertIn("docs/known-gaps.md", joined)
        self.assertIn("docs/work-queue.md", joined)

    def test_unsafe_internal_backslash_and_case_collision_are_rejected(self) -> None:
        self.fixture.board["items"][0]["related_paths"] = [
            "docs\\..\\private.txt",
            "Docs/Case.md",
            "docs/case.md",
        ]
        self.fixture.write("board", self.fixture.board)
        self.fixture.rebind()
        error = self.assert_validation_error("portable repository-relative path")
        self.assertIn("portable-path collision", "\n".join(error.errors))

    def test_windows_reserved_path_and_terminal_formatting_controls_are_rejected(self) -> None:
        self.fixture.board["items"][0]["related_paths"] = ["docs/NUL.txt"]
        self.fixture.write("board", self.fixture.board)
        self.fixture.rebind()
        self.assert_validation_error("reserved Windows component")

        child = self.root / "bidi-control"
        fixture = SnapshotFixture(child)
        fixture.board["items"][1]["notes"] = "looks safe\u202ebut reverses terminal text"
        fixture.write("board", fixture.board)
        fixture.rebind()
        with self.assertRaises(adoption.SnapshotValidationError) as caught:
            fixture.validate()
        self.assertIn("bidirectional formatting control", "\n".join(caught.exception.errors))

    def test_map_stream_and_changed_map_claims_are_recomputed(self) -> None:
        self.fixture.map_manifest["current_map_set"]["tree_sha256"] = "0" * 64
        self.fixture.map_manifest["changed_maps"] = []
        self.fixture.write("map_manifest", self.fixture.map_manifest)
        self.fixture.rebind()
        error = self.assert_validation_error("does not match the canonical stream")
        self.assertIn("exact predecessor/current diff", "\n".join(error.errors))

    def test_sealed_tracked_path_assertion_must_match_pin(self) -> None:
        self.fixture.check["aggregate"]["tracked_repository_paths"] = 999
        self.fixture.rebind()
        self.assert_validation_error("does not match pin value 20")

    def test_symlinked_required_file_is_rejected(self) -> None:
        original = self.fixture.paths["board"]
        target = self.root / "board-target.json"
        original.replace(target)
        try:
            os.symlink(target, original)
        except (OSError, NotImplementedError) as exc:
            self.skipTest(f"symbolic links unavailable: {exc}")
        self.assert_validation_error("must not traverse a link")

    @unittest.skipUnless(os.name == "nt", "Windows junction regression")
    def test_windows_junction_component_is_rejected_without_symlink_privilege(self) -> None:
        junction = self.root / "manifests"
        target = self.root / "actual-manifests"
        junction.rename(target)
        result = subprocess.run(
            ["cmd", "/c", "mklink", "/J", str(junction), str(target)],
            check=False,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            target.rename(junction)
            self.skipTest(f"junction creation unavailable: {result.stderr or result.stdout}")
        try:
            self.assertNotEqual(getattr(os.lstat(junction), "st_reparse_tag", 0), 0)
            self.assert_validation_error("junction, reparse point, or on-demand")
        finally:
            if junction.exists() and getattr(os.lstat(junction), "st_reparse_tag", 0):
                os.rmdir(junction)
            if target.exists() and not junction.exists():
                target.rename(junction)

    @unittest.skipUnless(os.name == "nt", "Windows UNC regression")
    def test_unc_root_rejects_before_any_filesystem_access(self) -> None:
        with mock.patch.object(
            adoption.os,
            "lstat",
            side_effect=AssertionError("UNC path was accessed"),
        ):
            with self.assertRaises(adoption.SnapshotValidationError) as caught:
                adoption.validate_snapshot(
                    Path(r"\\127.0.0.1\must-not-connect"),
                    pin=copy.deepcopy(self.fixture.pin),
                    production=False,
                )
        self.assertIn("must not use a UNC or device namespace", "\n".join(caught.exception.errors))

    def test_opened_handle_path_mismatch_rejects_before_content_read(self) -> None:
        outside = self.root / "unrelated-private-file"
        outside.write_text("unrelated private bytes", encoding="utf-8")
        with (
            mock.patch.object(adoption, "_opened_handle_path", return_value=outside.resolve()),
            mock.patch.object(adoption.os, "read", side_effect=AssertionError("content was read")),
        ):
            self.assert_validation_error("opened handle does not match the inspected snapshot path")

    def test_hardlinked_required_file_is_rejected(self) -> None:
        original = self.fixture.paths["board"]
        target = self.root / "board-hardlink-target.json"
        original.replace(target)
        try:
            os.link(target, original)
        except OSError as exc:
            self.skipTest(f"hard links unavailable: {exc}")
        self.assert_validation_error("must not be a hard-linked file")

    def test_validator_reads_only_four_allowlisted_files_and_writes_nothing(self) -> None:
        canary = self.root / "unrelated-private-canary.txt"
        canary.write_text("must remain unread and unchanged", encoding="utf-8")
        before = {
            path: (path.read_bytes(), path.stat().st_mtime_ns)
            for path in [*self.fixture.paths.values(), canary]
        }
        opened: list[Path] = []
        original_open = os.open

        def recording_open(path: object, *args: object, **kwargs: object):
            opened.append(Path(path).resolve())
            return original_open(path, *args, **kwargs)

        with mock.patch.object(adoption.os, "open", recording_open):
            self.fixture.validate()
        self.assertNotIn(canary.resolve(), opened)
        self.assertEqual(set(opened), {path.resolve() for path in self.fixture.paths.values()})
        after = {
            path: (path.read_bytes(), path.stat().st_mtime_ns)
            for path in [*self.fixture.paths.values(), canary]
        }
        self.assertEqual(before, after)

    def test_shell_like_cursor_is_rendered_as_inert_text(self) -> None:
        canary = self.root / "should-not-exist"
        shell_text = f"$(touch '{canary.resolve()}')"
        self.fixture.board["items"][1]["next_cursor"] = shell_text
        self.fixture.write("board", self.fixture.board)
        self.fixture.rebind()
        snapshot = self.fixture.validate()
        selected = adoption.select_items(
            snapshot,
            lane_states=None,
            priorities=None,
            readiness=None,
            language=None,
            query=None,
            unowned=False,
            limit=20,
        )
        with (
            mock.patch.object(subprocess, "run", side_effect=AssertionError("command run")),
            mock.patch.object(subprocess, "Popen", side_effect=AssertionError("command spawned")),
            mock.patch.object(os, "system", side_effect=AssertionError("shell used")),
        ):
            rendered = adoption._render_text(snapshot, selected)  # noqa: SLF001
        self.assertIn(shell_text, rendered)
        self.assertFalse(canary.exists())

    def test_cli_fails_closed_without_snapshot_and_performs_no_network(self) -> None:
        missing = self.root / "missing"
        stderr = io.StringIO()
        with mock.patch("socket.socket.connect", side_effect=AssertionError("network used")):
            with contextlib.redirect_stderr(stderr):
                result = adoption.main([str(missing)])
        self.assertEqual(result, 1)
        self.assertIn("ERROR:", stderr.getvalue())

    def test_invalid_limit_and_conflicting_lane_flags_are_usage_errors(self) -> None:
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            invalid_limit = adoption.main([str(self.root), "--limit", "0"])
            conflict = adoption.main(
                [str(self.root), "--all-lanes", "--lane-state", "future"]
            )
            c1_query = adoption.main([str(self.root), "--query", "unsafe\u009bquery"])
            oversized_query = adoption.main(
                [str(self.root), "--query", "x" * (adoption.MAX_QUERY_CHARS + 1)]
            )
        self.assertEqual(invalid_limit, 2)
        self.assertEqual(conflict, 2)
        self.assertEqual(c1_query, 2)
        self.assertEqual(oversized_query, 2)


if __name__ == "__main__":
    unittest.main()
