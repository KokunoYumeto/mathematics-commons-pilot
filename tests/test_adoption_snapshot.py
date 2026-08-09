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
    / "06f918eee33729f760b1459934f9a50c2aca9e31"
)
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import validate_adoption_snapshot as adoption  # noqa: E402


CLAIM_REGRESSION_PATH = "scripts/test-claims.py"
PRODUCTION_WORKTREE_BASE_COMMIT = "10d2df083bf0b47b758d5f094b6fcaeed9167011"
PRODUCTION_FIRST_COMPLETE_CONTRACT_COMMIT = (
    "62b13062c7b3deea30fd924d6cf585fd637a58f8"
)
PRODUCTION_FIRST_COMPLETE_CONTRACT_TREE = (
    "e65c8dd8000abdb02f31949e1fed5d73ced3d22d"
)
PRODUCTION_PREDECESSOR_COMMIT = "5ccd9357187c2f4a246a40fd5ef45f6df6ae88b0"
PRODUCTION_SOURCE_CHECK_IDENTITY = (
    5663,
    "21584e4bf46e6fcdcef38ae637026d58c82aac8bc45d1afff5d9070b3c0b8dfa",
)
RETIRED_UMBRELLA_ITEM_IDS = (
    "noether-multilingual",
    "grothendieck-school",
)
NOETHER_SCOPE_ITEM_IDS = (
    "noether-de-auth",
    "noether-en",
    "noether-es",
    "noether-fr",
    "noether-ru",
    "noether-uk",
    "noether-isv",
    "noether-ko-review",
    "noether-ko-p09",
    "noether-zh-r5",
    "noether-zh-hant",
    "noether-ja",
    "noether-ar-p06",
    "noether-fa-p06",
    "noether-id-p36",
    "noether-vi-p01",
)
GROTHENDIECK_SCOPE_ITEM_IDS = (
    "ega-0-iv",
    "fga-foundements",
    "verdier-thesis",
    "tohoku-paper",
    "illusie-cotangent-i-ii",
    "deligne-papers-letters",
)
PRODUCTION_CURRENT_ITEM_IDS = (
    "noether-de-auth",
    *GROTHENDIECK_SCOPE_ITEM_IDS,
    "weber-algebra",
)
CONTINUOUS_VALIDATION = {
    "workflow": ".github/workflows/adopt.yml",
    "checkout": "blobless_sparse_metadata",
    "events": ["pull_request", "push_main", "workflow_dispatch"],
    "checks": [
        "board_schema_maps",
        "exact_local_consumer",
        "promisor_no_lazy_fetch",
        "claim_lifecycle_fixtures",
    ],
    "pinned_actions": True,
    "corpus_builds": False,
}


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
                "owner_scope": "maintained bounded test row",
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


def exact_workflows() -> list[dict[str, object]]:
    """Return the sealed workflow registry without duplicating it in test code."""

    board = json.loads((PRODUCTION_FIXTURE / adoption.BOARD_PATH).read_text(encoding="utf-8"))
    workflows = board["workflows"]
    assert [workflow["id"] for workflow in workflows] == list(adoption.WORKFLOW_IDS)
    return copy.deepcopy(workflows)


class SnapshotFixture:
    commit = "a" * 40
    tree = "1" * 40
    content_commit = "2" * 40
    content_tree = "3" * 40
    first_complete_contract_commit = "4" * 40
    first_complete_contract_tree = "5" * 40
    worktree_base_commit = PRODUCTION_WORKTREE_BASE_COMMIT
    evidence_commit = "c" * 40
    map_commit = "d" * 40
    evidence_closure_commit = commit

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
            "queue_snapshot_sources": 2,
            "queue_snapshot_bytes": sum(identity[1] for identity in adoption.QUEUE_SNAPSHOT),
            "human_board_rows": 3,
            "represented_human_board_items": 3,
            "missing_human_board_items": 0,
            "unknown_human_board_ids": 0,
            "duplicate_human_board_ids": 0,
            "human_index_rows": 3,
            "human_index_authors": 1,
            "human_index_works": 3,
            "human_index_series": 0,
            "human_index_languages": 1,
            "human_index_corpora": 1,
            "repository_path_checks": 33,
            "tracked_repository_paths": 33,
            "issue_labels": 4,
            "issue_label_templates": len(adoption.ISSUE_TEMPLATE_PATHS),
            "consumer_modes": len(adoption.CONSUMER_MODES),
            "claim_auditor_board_modes": len(adoption.CLAIM_AUDITOR_MODES["board"]),
            "claim_auditor_issue_modes": len(adoption.CLAIM_AUDITOR_MODES["issues"]),
            "continuous_validation_checks": len(CONTINUOUS_VALIDATION["checks"]),
            "workflow_registry": len(adoption.WORKFLOW_IDS),
            "workflow_tokens_used": len(adoption.WORKFLOW_IDS),
            "unreferenced_workflows": 0,
            "named_owner_rows": 1,
            "unclaimed_owner_rows": 2,
        }
        self.check = self.make_check()
        self.write("check", self.check)
        self.pin: dict[str, object] = {}
        self.rebind()

    def make_board(self) -> dict[str, object]:
        items = [
            base_item("current-item", "current_work"),
            base_item("ready-item", "ready_for_adoption"),
            base_item("future-item", "future"),
        ]
        workflow_ids = list(adoption.WORKFLOW_IDS)
        items[0]["workflow"] = workflow_ids[:5]
        items[1]["workflow"] = workflow_ids[5:10]
        items[2]["workflow"] = workflow_ids[10:]
        return {
            "schema": "math-commons-adoption-v1",
            "schema_url": adoption.SCHEMA_PATH,
            "validation": adoption.CHECK_PATH,
            "board_role": "operational_layer",
            "updated": "2026-08-09",
            "evidence_base_commit": self.evidence_commit,
            "repository": adoption.REPOSITORY_URL,
            "human_board": "docs/adopt.md",
            "human_index": adoption.HUMAN_INDEX_PATH,
            "archive_authority": {
                "coverage_maps": "docs/github-maps.md",
                "reader_shelf": "reader-pdfs/README.md",
                "source_shelf": "sources/README.md",
                "archive_history": "docs/github-archive.md",
            },
            "ownership_policy": copy.deepcopy(adoption.OWNERSHIP_POLICY),
            "map_manifest": adoption.MAP_PATH,
            "required_maps": ["docs/test-map.md"],
            "queue_sources": list(adoption.QUEUE_SOURCES),
            "queue_snapshot": [
                {"path": path, "bytes": size, "sha256": digest}
                for path, size, digest in adoption.QUEUE_SNAPSHOT
            ],
            "snapshot_policy": {
                "stable_locator_ref": "main",
                "immutable_unit": "human_approved_exact_commit",
                "same_commit_paths": list(adoption.SNAPSHOT_PATHS),
                "required_checks": list(adoption.REQUIRED_CHECKS),
                "mixed_revisions_forbidden": True,
            },
            "consumer_helper": adoption.CONSUMER_HELPER_PATH,
            "consumer_modes": list(adoption.CONSUMER_MODES),
            "consumer_regression": adoption.CONSUMER_REGRESSION_PATH,
            "claim_auditor": adoption.CLAIM_AUDITOR_PATH,
            "claim_auditor_modes": copy.deepcopy(adoption.CLAIM_AUDITOR_MODES),
            "claim_regression": CLAIM_REGRESSION_PATH,
            "continuous_validation": copy.deepcopy(CONTINUOUS_VALIDATION),
            "claim_interface": adoption.CLAIM_URL,
            "handback_interface": adoption.HANDBACK_URL,
            "human_workflows": adoption.HUMAN_WORKFLOWS_PATH,
            "workflow_fields": list(adoption.WORKFLOW_FIELDS),
            "workflows": exact_workflows(),
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
            "items": items,
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
                "human_index": {"const": adoption.HUMAN_INDEX_PATH},
                "consumer_helper": {"const": adoption.CONSUMER_HELPER_PATH},
                "consumer_modes": {
                    "type": "array",
                    "prefixItems": [
                        {"const": mode} for mode in adoption.CONSUMER_MODES
                    ],
                    "items": False,
                    "minItems": len(adoption.CONSUMER_MODES),
                    "maxItems": len(adoption.CONSUMER_MODES),
                },
                "consumer_regression": {"const": adoption.CONSUMER_REGRESSION_PATH},
                "claim_auditor": {"const": adoption.CLAIM_AUDITOR_PATH},
                "claim_auditor_modes": {
                    "type": "object",
                    "required": ["board", "issues"],
                    "properties": {
                        key: {
                            "type": "array",
                            "prefixItems": [{"const": mode} for mode in modes],
                            "items": False,
                            "minItems": len(modes),
                            "maxItems": len(modes),
                        }
                        for key, modes in adoption.CLAIM_AUDITOR_MODES.items()
                    },
                    "additionalProperties": False,
                },
                "claim_regression": {"const": CLAIM_REGRESSION_PATH},
                "continuous_validation": {
                    "type": "object",
                    "required": [
                        "workflow",
                        "checkout",
                        "events",
                        "checks",
                        "pinned_actions",
                        "corpus_builds",
                    ],
                    "properties": {
                        "workflow": {"const": CONTINUOUS_VALIDATION["workflow"]},
                        "checkout": {"const": CONTINUOUS_VALIDATION["checkout"]},
                        "events": {
                            "type": "array",
                            "prefixItems": [
                                {"const": value}
                                for value in CONTINUOUS_VALIDATION["events"]
                            ],
                            "items": False,
                            "minItems": len(CONTINUOUS_VALIDATION["events"]),
                            "maxItems": len(CONTINUOUS_VALIDATION["events"]),
                        },
                        "checks": {
                            "type": "array",
                            "prefixItems": [
                                {"const": value}
                                for value in CONTINUOUS_VALIDATION["checks"]
                            ],
                            "items": False,
                            "minItems": len(CONTINUOUS_VALIDATION["checks"]),
                            "maxItems": len(CONTINUOUS_VALIDATION["checks"]),
                        },
                        "pinned_actions": {
                            "const": CONTINUOUS_VALIDATION["pinned_actions"]
                        },
                        "corpus_builds": {
                            "const": CONTINUOUS_VALIDATION["corpus_builds"]
                        },
                    },
                    "additionalProperties": False,
                },
                "claim_interface": {"const": adoption.CLAIM_URL},
                "handback_interface": {"const": adoption.HANDBACK_URL},
                "human_workflows": {"const": adoption.HUMAN_WORKFLOWS_PATH},
                "workflow_fields": {
                    "type": "array",
                    "prefixItems": [
                        {"const": field} for field in adoption.WORKFLOW_FIELDS
                    ],
                    "items": False,
                    "minItems": len(adoption.WORKFLOW_FIELDS),
                    "maxItems": len(adoption.WORKFLOW_FIELDS),
                },
            },
            "additionalProperties": True,
            "$defs": {
                "sourceIdentity": {
                    "type": "object",
                    "required": ["path", "bytes", "sha256"],
                    "properties": {
                        "path": {"type": "string", "minLength": 1},
                        "bytes": {"type": "integer", "minimum": 0},
                        "sha256": {
                            "type": "string",
                            "pattern": "^[0-9A-F]{64}$",
                        },
                    },
                    "additionalProperties": False,
                },
                "workflow": {
                    "type": "object",
                    "required": list(adoption.WORKFLOW_FIELDS),
                    "properties": {
                        "id": {
                            "type": "string",
                            "pattern": "^[a-z0-9]+(?:_[a-z0-9]+)*$",
                        },
                        "purpose": {"type": "string", "minLength": 1},
                        "start_when": {"type": "string", "minLength": 1},
                        **{
                            field: {
                                "type": "array",
                                "minItems": 1,
                                "uniqueItems": True,
                                "items": {"type": "string", "minLength": 1},
                            }
                            for field in (
                                "inputs",
                                "steps",
                                "evidence",
                                "stop_conditions",
                                "handback",
                            )
                        },
                    },
                    "additionalProperties": False,
                },
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
            "input_mode": "named_worktree_files",
            "worktree_base_commit": self.worktree_base_commit,
            "worktree_dirty": False,
            "board": {},
            "schema_file": {},
            "map_manifest": {},
            "human_board": {},
            "human_index": {},
            "human_workflows": {},
            "issue_labels": {},
            "snapshot_policy": {
                "stable_locator_ref": "main",
                "immutable_unit": "human_approved_exact_commit",
                "same_commit_paths": 4,
                "required_checks": 4,
                "mixed_revisions_forbidden": True,
            },
            "consumer_helper": adoption.CONSUMER_HELPER_PATH,
            "consumer_modes": list(adoption.CONSUMER_MODES),
            "consumer_regression": adoption.CONSUMER_REGRESSION_PATH,
            "claim_auditor": adoption.CLAIM_AUDITOR_PATH,
            "claim_auditor_modes": copy.deepcopy(adoption.CLAIM_AUDITOR_MODES),
            "claim_regression": CLAIM_REGRESSION_PATH,
            "continuous_validation": copy.deepcopy(CONTINUOUS_VALIDATION),
            "ownership_policy": copy.deepcopy(adoption.OWNERSHIP_POLICY),
            "queue_snapshot": [
                {"path": path, "bytes": size, "sha256": digest}
                for path, size, digest in adoption.QUEUE_SNAPSHOT
            ],
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
        self.check["human_index"] = {
            "path": adoption.HUMAN_INDEX_IDENTITY[0],
            "bytes": adoption.HUMAN_INDEX_IDENTITY[1],
            "sha256": adoption.HUMAN_INDEX_IDENTITY[2].upper(),
            "rows": int(self.aggregate["human_index_rows"]),
            "authors": int(self.aggregate["human_index_authors"]),
            "works": int(self.aggregate["human_index_works"]),
            "series": int(self.aggregate["human_index_series"]),
            "languages": int(self.aggregate["human_index_languages"]),
            "corpora": int(self.aggregate["human_index_corpora"]),
        }
        self.check["human_workflows"] = {
            "path": adoption.HUMAN_WORKFLOWS_IDENTITY[0],
            "bytes": adoption.HUMAN_WORKFLOWS_IDENTITY[1],
            "sha256": adoption.HUMAN_WORKFLOWS_IDENTITY[2].upper(),
            "flows": int(self.aggregate["workflow_registry"]),
            "headings": int(self.aggregate["workflow_registry"]),
        }
        self.check["issue_labels"] = {
            "path": adoption.ISSUE_LABELS_IDENTITY[0],
            "bytes": adoption.ISSUE_LABELS_IDENTITY[1],
            "sha256": adoption.ISSUE_LABELS_IDENTITY[2].upper(),
            "labels": int(self.aggregate["issue_labels"]),
            "templates": int(self.aggregate["issue_label_templates"]),
        }
        self.write("check", self.check)
        identities["check"] = self.identity("check")
        ordered_identities = [
            identities[role]
            for role in ("board", "schema", "check", "map_manifest")
        ]
        self.pin = {
            "schema": "mathematics-commons-adoption-pin-v3",
            "repository": adoption.REPOSITORY_URL,
            "approved_snapshot_commit": self.commit,
            "approved_snapshot_tree": self.tree,
            "content_source_commit": self.content_commit,
            "content_source_tree": self.content_tree,
            "first_complete_contract_commit": self.first_complete_contract_commit,
            "first_complete_contract_tree": self.first_complete_contract_tree,
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
            "optional_human_index_projection": {
                "role": "human_index",
                "path": adoption.HUMAN_INDEX_IDENTITY[0],
                "bytes": adoption.HUMAN_INDEX_IDENTITY[1],
                "sha256": adoption.HUMAN_INDEX_IDENTITY[2],
                "machine_required": False,
            },
            "optional_consumer_helper_identity": {
                "role": "consumer_helper",
                "path": adoption.CONSUMER_HELPER_PATH,
                "bytes": 654,
                "sha256": "6" * 64,
                "machine_required": False,
            },
            "optional_consumer_regression_identity": {
                "role": "consumer_regression",
                "path": adoption.CONSUMER_REGRESSION_PATH,
                "bytes": 655,
                "sha256": "5" * 64,
                "machine_required": False,
            },
            "optional_claim_auditor_identity": {
                "role": "claim_auditor",
                "path": adoption.CLAIM_AUDITOR_PATH,
                "bytes": 656,
                "sha256": "4" * 64,
                "machine_required": False,
            },
            "optional_claim_regression_identity": {
                "role": "claim_regression",
                "path": CLAIM_REGRESSION_PATH,
                "bytes": 657,
                "sha256": "3" * 64,
                "machine_required": False,
            },
            "optional_continuous_validation_identity": {
                "role": "continuous_validation",
                "path": CONTINUOUS_VALIDATION["workflow"],
                "bytes": 658,
                "sha256": "2" * 64,
                "machine_required": False,
            },
            "sealed_public_receipts": [
                {
                    "role": adoption.SEALED_PUBLIC_RECEIPTS[0][0],
                    "path": "manifests/published-github/test-adopt-ci-readback.json",
                    "bytes": 456,
                    "sha256": "7" * 64,
                    "machine_required": False,
                },
                {
                    "role": adoption.SEALED_PUBLIC_RECEIPTS[1][0],
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
            pin["content_source_commit"], adoption.PRODUCTION_CONTENT_SOURCE_COMMIT
        )
        self.assertEqual(
            pin["content_source_tree"], adoption.PRODUCTION_CONTENT_SOURCE_TREE
        )
        self.assertEqual(
            pin["first_complete_contract_commit"],
            PRODUCTION_FIRST_COMPLETE_CONTRACT_COMMIT,
        )
        self.assertEqual(
            pin["first_complete_contract_tree"],
            PRODUCTION_FIRST_COMPLETE_CONTRACT_TREE,
        )
        self.assertNotIn("validation_context_commit", pin)
        self.assertNotIn("validation_context_role", pin)
        self.assertEqual(
            pin["evidence_closure_commit"], pin["approved_snapshot_commit"]
        )
        optional_identities = (
            (
                "optional_human_index_projection",
                adoption.HUMAN_INDEX_IDENTITY,
            ),
            ("optional_consumer_helper_identity", adoption.CONSUMER_HELPER_IDENTITY),
            (
                "optional_consumer_regression_identity",
                adoption.CONSUMER_REGRESSION_IDENTITY,
            ),
            ("optional_claim_auditor_identity", adoption.CLAIM_AUDITOR_IDENTITY),
            (
                "optional_claim_regression_identity",
                adoption.CLAIM_REGRESSION_IDENTITY,
            ),
            (
                "optional_continuous_validation_identity",
                adoption.CONTINUOUS_VALIDATION_IDENTITY,
            ),
        )
        for field, expected in optional_identities:
            with self.subTest(field=field):
                self.assertEqual(
                    (
                        pin[field]["path"],
                        pin[field]["bytes"],
                        pin[field]["sha256"],
                    ),
                    expected,
                )
                self.assertIs(pin[field]["machine_required"], False)
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
        self.assertEqual(snapshot.aggregate["items"], 66)
        self.assertEqual(snapshot.aggregate["current_work"], 8)
        self.assertEqual(snapshot.aggregate["ready_for_adoption"], 53)
        self.assertEqual(snapshot.aggregate["future"], 5)
        self.assertEqual(snapshot.aggregate["mirrors"], 0)
        self.assertEqual(snapshot.aggregate["required_maps"], 19)
        self.assertEqual(snapshot.aggregate["queue_sources"], 2)
        self.assertEqual(snapshot.aggregate["human_board_rows"], 66)
        self.assertEqual(snapshot.aggregate["human_index_rows"], 66)
        self.assertEqual(snapshot.aggregate["human_index_authors"], 43)
        self.assertEqual(snapshot.aggregate["human_index_works"], 66)
        self.assertEqual(snapshot.aggregate["human_index_series"], 18)
        self.assertEqual(snapshot.aggregate["human_index_languages"], 20)
        self.assertEqual(snapshot.aggregate["human_index_corpora"], 21)
        self.assertEqual(snapshot.aggregate["workflow_registry"], 14)
        self.assertEqual(snapshot.aggregate["named_owner_rows"], 8)
        self.assertEqual(snapshot.aggregate["unclaimed_owner_rows"], 58)
        self.assertEqual(snapshot.aggregate["repository_path_checks"], 214)
        self.assertEqual(snapshot.aggregate["tracked_repository_paths"], 214)
        self.assertEqual(snapshot.aggregate["claim_auditor_board_modes"], 2)
        self.assertEqual(snapshot.aggregate["claim_auditor_issue_modes"], 2)
        self.assertEqual(snapshot.aggregate["continuous_validation_checks"], 4)
        self.assertEqual(snapshot.check["input_mode"], "named_worktree_files")
        self.assertEqual(
            snapshot.check["worktree_base_commit"], PRODUCTION_WORKTREE_BASE_COMMIT
        )
        self.assertIs(snapshot.check["worktree_dirty"], False)
        self.assertNotIn("observed_commit", snapshot.check)
        self.assertEqual([item["id"] for item in selected], ["gauss-werke-ii"])
        self.assertIn(adoption.PRODUCTION_APPROVED_COMMIT, rendered)
        self.assertIn("[ready_for_adoption; high; exact_cursor]", rendered)
        self.assertIn("pinned archive: https://github.com/", rendered)
        self.assertNotIn("validation context", rendered.lower())
        self.assertNotIn("not publicly resolvable", rendered.lower())

    def test_generated_snapshot_passes_compiled_contract(self) -> None:
        snapshot = self.fixture.validate()
        self.assertEqual(snapshot.aggregate["items"], 3)
        self.assertEqual(snapshot.aggregate["repository_path_checks"], 33)
        self.assertEqual(snapshot.aggregate["tracked_repository_paths"], 33)
        self.assertEqual(snapshot.aggregate["claim_auditor_board_modes"], 2)
        self.assertEqual(snapshot.aggregate["claim_auditor_issue_modes"], 2)
        self.assertEqual(snapshot.aggregate["continuous_validation_checks"], 4)
        self.assertEqual(snapshot.check["status"], "PASS")

    def test_production_scope_split_is_exact_and_retires_umbrella_claims(self) -> None:
        snapshot = adoption.validate_snapshot(PRODUCTION_FIXTURE)
        items = snapshot.board["items"]
        item_ids = [item["id"] for item in items]
        split_ids = (*NOETHER_SCOPE_ITEM_IDS, *GROTHENDIECK_SCOPE_ITEM_IDS)

        self.assertEqual(item_ids[: len(split_ids)], list(split_ids))
        self.assertEqual(len(split_ids), 22)
        self.assertTrue(set(RETIRED_UMBRELLA_ITEM_IDS).isdisjoint(item_ids))
        self.assertEqual(
            {item["id"] for item in items if item["lane_state"] == "current_work"},
            set(PRODUCTION_CURRENT_ITEM_IDS),
        )

        noether_rows = [item for item in items if item["id"] in NOETHER_SCOPE_ITEM_IDS]
        self.assertEqual(len(noether_rows), 16)
        self.assertEqual(
            [item["id"] for item in noether_rows if item["lane_state"] == "current_work"],
            ["noether-de-auth"],
        )
        self.assertTrue(
            all(
                item["owner"] is None
                for item in noether_rows
                if item["lane_state"] == "ready_for_adoption"
            )
        )

        grothendieck_rows = [
            item for item in items if item["id"] in GROTHENDIECK_SCOPE_ITEM_IDS
        ]
        self.assertEqual(len(grothendieck_rows), 6)
        self.assertTrue(
            all(
                item["lane_state"] == "current_work" and item["owner"] is not None
                for item in grothendieck_rows
            )
        )

    def test_mixed_source_check_and_final_contract_fail_closed(self) -> None:
        mixed_root = self.root / "mixed-source-final"
        shutil.copytree(PRODUCTION_FIXTURE, mixed_root)
        check_path = mixed_root / adoption.CHECK_PATH
        source_check = check_path.read_bytes().replace(
            PRODUCTION_WORKTREE_BASE_COMMIT.encode("ascii"),
            PRODUCTION_PREDECESSOR_COMMIT.encode("ascii"),
        ).replace(b'"worktree_dirty": false', b'"worktree_dirty": true')
        self.assertEqual(len(source_check), PRODUCTION_SOURCE_CHECK_IDENTITY[0])
        self.assertEqual(
            hashlib.sha256(source_check).hexdigest(),
            PRODUCTION_SOURCE_CHECK_IDENTITY[1],
        )
        check_path.write_bytes(source_check)

        with self.assertRaises(adoption.SnapshotValidationError) as caught:
            adoption.validate_snapshot(mixed_root)
        joined = "\n".join(caught.exception.errors)
        self.assertIn(adoption.CHECK_PATH, joined)
        self.assertIn("approved bounded byte length", joined)

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
        self.assertEqual(payload["schema"], "mathematics-commons-adoption-candidates-v2")
        self.assertEqual(payload["authority"], "coordination_metadata_only_not_mathematical_evidence")
        self.assertEqual(payload["application_http_api_requests_performed"], 0)
        self.assertEqual(payload["live_packets_created"], 0)
        self.assertEqual(payload["interfaces"]["claim"], adoption.CLAIM_URL)
        self.assertEqual(payload["interfaces"]["handback"], adoption.HANDBACK_URL)
        self.assertEqual(
            payload["interfaces"]["consumer_helper"], adoption.CONSUMER_HELPER_PATH
        )
        self.assertEqual(
            payload["interfaces"]["consumer_modes"], list(adoption.CONSUMER_MODES)
        )
        self.assertEqual(
            payload["interfaces"]["consumer_regression"],
            adoption.CONSUMER_REGRESSION_PATH,
        )
        self.assertEqual(
            payload["interfaces"]["claim_auditor"], adoption.CLAIM_AUDITOR_PATH
        )
        self.assertEqual(
            payload["interfaces"]["claim_auditor_modes"],
            adoption.CLAIM_AUDITOR_MODES,
        )
        self.assertEqual(
            payload["interfaces"]["claim_regression"], CLAIM_REGRESSION_PATH
        )
        self.assertEqual(
            payload["interfaces"]["continuous_validation"], CONTINUOUS_VALIDATION
        )
        self.assertEqual(
            payload["migration"],
            {
                "retired_ids": ["grothendieck-school", "noether-multilingual"],
                "change": "stable_id_breaking_one_to_many_scope_split",
                "automatic_remap": "forbidden",
                "replacement_selection": (
                    "human_selection_of_one_or_more_bounded_ids_required"
                ),
            },
        )
        self.assertEqual(
            payload["source"]["pin_schema"], "mathematics-commons-adoption-pin-v3"
        )
        self.assertEqual(payload["source"]["approved_snapshot_tree"], self.fixture.tree)
        self.assertEqual(
            payload["source"]["content_source_commit"], self.fixture.content_commit
        )
        self.assertEqual(
            payload["source"]["first_complete_contract_commit"],
            self.fixture.first_complete_contract_commit,
        )
        self.assertEqual(
            payload["source"]["first_complete_contract_tree"],
            self.fixture.first_complete_contract_tree,
        )
        self.assertEqual(
            payload["source"]["first_complete_contract_role"],
            "first_commit_with_all_four_approved_contract_identities",
        )
        self.assertEqual(
            payload["source"]["contract_identity_relation"],
            {
                "content_source_matches_approved": "three_of_four",
                "first_complete_contract_matches_approved": "four_of_four",
            },
        )
        self.assertEqual(payload["source"]["input_mode"], "named_worktree_files")
        self.assertEqual(
            payload["source"]["worktree_base_commit"], self.fixture.worktree_base_commit
        )
        self.assertIs(payload["source"]["worktree_dirty"], False)
        self.assertNotIn("validation_context_commit", payload["source"])
        self.assertNotIn("validation_context_role", payload["source"])
        self.assertNotIn("observed_commit", payload["source"])
        self.assertEqual(len(payload["source"]["contract_files"]), 4)
        self.assertIs(
            payload["source"]["optional_human_projection"]["machine_required"], False
        )
        self.assertIs(
            payload["source"]["optional_human_index_projection"]["machine_required"],
            False,
        )
        self.assertEqual(
            payload["source"]["optional_human_projections_role"],
            "same_commit_human_guidance_only_not_machine_contract_inputs",
        )
        self.assertIs(
            payload["source"]["optional_consumer_helper_identity"]["machine_required"],
            False,
        )
        self.assertIs(
            payload["source"]["optional_consumer_regression_identity"][
                "machine_required"
            ],
            False,
        )
        self.assertIs(
            payload["source"]["optional_claim_auditor_identity"]["machine_required"],
            False,
        )
        self.assertIs(
            payload["source"]["optional_claim_regression_identity"]["machine_required"],
            False,
        )
        self.assertIs(
            payload["source"]["optional_continuous_validation_identity"][
                "machine_required"
            ],
            False,
        )
        self.assertEqual(
            payload["source"]["optional_code_identities_role"],
            "non_input_executable_provenance_only_not_a_trust_anchor",
        )
        self.assertEqual(len(payload["source"]["sealed_public_receipts"]), 2)
        serialized = json.dumps(payload)
        self.assertNotIn("record_type", serialized)
        self.assertNotIn("validation_context_commit", serialized)
        self.assertNotIn("validation_context_role", serialized)
        self.assertNotIn("observed_commit", serialized)
        self.assertNotIn("not_publicly_resolvable", serialized)

    def test_support_and_receipts_are_provenance_not_additional_inputs(self) -> None:
        snapshot = self.fixture.validate()
        required_paths = [entry["path"] for entry in snapshot.pin["files"]]
        support_fields = (
            "optional_human_index_projection",
            "optional_consumer_helper_identity",
            "optional_consumer_regression_identity",
            "optional_claim_auditor_identity",
            "optional_claim_regression_identity",
            "optional_continuous_validation_identity",
        )
        support_paths = [snapshot.pin[field]["path"] for field in support_fields]
        receipt_paths = [
            entry["path"] for entry in snapshot.pin["sealed_public_receipts"]
        ]
        self.assertEqual(len(required_paths), 4)
        self.assertTrue(set(required_paths).isdisjoint(support_paths))
        self.assertTrue(set(required_paths).isdisjoint(receipt_paths))
        self.assertTrue(
            all(snapshot.pin[field]["machine_required"] is False for field in support_fields)
        )
        self.assertTrue(
            all(entry["machine_required"] is False for entry in snapshot.pin["sealed_public_receipts"])
        )

        mutations = [
            (field, lambda pin, field=field: pin[field].__setitem__("machine_required", True))
            for field in support_fields
        ]
        mutations.append(
            (
                "sealed_public_receipts",
                lambda pin: pin["sealed_public_receipts"][0].__setitem__(
                    "machine_required", True
                ),
            )
        )
        for name, mutate in mutations:
            with self.subTest(name=name):
                pin = copy.deepcopy(self.fixture.pin)
                mutate(pin)
                with self.assertRaises(adoption.SnapshotValidationError) as caught:
                    adoption.validate_snapshot(self.root, pin=pin, production=False)
                self.assertIn("must remain false", "\n".join(caught.exception.errors))

    def test_production_support_and_receipt_identity_drift_is_rejected(self) -> None:
        mutations = (
            (
                "optional_human_index_projection",
                lambda pin: pin["optional_human_index_projection"].__setitem__(
                    "sha256", "0" * 64
                ),
            ),
            (
                "optional_consumer_regression_identity",
                lambda pin: pin["optional_consumer_regression_identity"].__setitem__(
                    "sha256", "0" * 64
                ),
            ),
            (
                "optional_claim_auditor_identity",
                lambda pin: pin["optional_claim_auditor_identity"].__setitem__(
                    "bytes", pin["optional_claim_auditor_identity"]["bytes"] + 1
                ),
            ),
            (
                "optional_claim_regression_identity",
                lambda pin: pin["optional_claim_regression_identity"].__setitem__(
                    "sha256", "0" * 64
                ),
            ),
            (
                "optional_continuous_validation_identity",
                lambda pin: pin["optional_continuous_validation_identity"].__setitem__(
                    "bytes", pin["optional_continuous_validation_identity"]["bytes"] + 1
                ),
            ),
            (
                "sealed_public_receipts",
                lambda pin: pin["sealed_public_receipts"][0].__setitem__(
                    "sha256", "0" * 64
                ),
            ),
        )
        for field, mutate in mutations:
            with self.subTest(field=field):
                pin = adoption._read_pin()  # noqa: SLF001 - compiled contract audit
                mutate(pin)
                errors: list[str] = []
                adoption._validate_pin(pin, errors, production=True)  # noqa: SLF001
                self.assertTrue(any(field in error for error in errors), errors)

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

    def test_unbound_check_state_tampering_is_rejected_even_when_it_says_pass(self) -> None:
        self.fixture.check["worktree_dirty"] = True
        self.fixture.write("check", self.fixture.check)
        self.assert_validation_error("snapshot file manifests/adopt.check.json")

    def test_rebound_check_requires_explicit_named_worktree_state(self) -> None:
        mutations = (
            ("input-mode", "input_mode", "other_mode", "input_mode"),
            ("malformed-base", "worktree_base_commit", "Z" * 40, "worktree_base_commit"),
            ("wrong-base", "worktree_base_commit", "b" * 40, "worktree_base_commit"),
            ("dirty-true", "worktree_dirty", True, "worktree_dirty"),
        )
        for name, field, value, fragment in mutations:
            with self.subTest(name=name):
                child = self.root / f"check-state-{name}"
                fixture = SnapshotFixture(child)
                fixture.check[field] = value
                fixture.rebind()
                with self.assertRaises(adoption.SnapshotValidationError) as caught:
                    fixture.validate()
                self.assertIn(fragment, "\n".join(caught.exception.errors))

        for field in ("input_mode", "worktree_base_commit", "worktree_dirty"):
            with self.subTest(missing=field):
                child = self.root / f"check-state-missing-{field}"
                fixture = SnapshotFixture(child)
                fixture.check.pop(field)
                fixture.rebind()
                with self.assertRaises(adoption.SnapshotValidationError) as caught:
                    fixture.validate()
                self.assertIn(f"missing required keys ['{field}']", "\n".join(caught.exception.errors))

    def test_pin_requires_first_complete_contract_identity(self) -> None:
        for field in (
            "first_complete_contract_commit",
            "first_complete_contract_tree",
        ):
            with self.subTest(missing=field):
                pin = copy.deepcopy(self.fixture.pin)
                pin.pop(field)
                with self.assertRaises(adoption.SnapshotValidationError) as caught:
                    adoption.validate_snapshot(self.root, pin=pin, production=False)
                self.assertIn(field, "\n".join(caught.exception.errors))

            with self.subTest(drift=field):
                pin = adoption._read_pin()  # noqa: SLF001 - compiled contract audit
                pin[field] = "f" * 40
                errors: list[str] = []
                adoption._validate_pin(pin, errors, production=True)  # noqa: SLF001
                self.assertTrue(any(field in error for error in errors), errors)

    def test_pin_requires_exact_human_index_projection(self) -> None:
        pin = copy.deepcopy(self.fixture.pin)
        pin.pop("optional_human_index_projection")
        with self.assertRaises(adoption.SnapshotValidationError) as caught:
            adoption.validate_snapshot(self.root, pin=pin, production=False)
        self.assertIn("optional_human_index_projection", "\n".join(caught.exception.errors))

        pin = copy.deepcopy(self.fixture.pin)
        pin["optional_human_index_projection"]["bytes"] += 1
        with self.assertRaises(adoption.SnapshotValidationError) as caught:
            adoption.validate_snapshot(self.root, pin=pin, production=False)
        self.assertIn("human_index", "\n".join(caught.exception.errors))

    def test_obsolete_validation_context_and_observed_commit_are_rejected(self) -> None:
        for field, value in (
            ("validation_context_commit", "f" * 40),
            ("validation_context_role", "public_trust_anchor"),
        ):
            with self.subTest(pin_field=field):
                pin = copy.deepcopy(self.fixture.pin)
                pin[field] = value
                with self.assertRaises(adoption.SnapshotValidationError) as caught:
                    adoption.validate_snapshot(self.root, pin=pin, production=False)
                self.assertIn("pin: contains undeclared keys", "\n".join(caught.exception.errors))

        self.fixture.check["observed_commit"] = "f" * 40
        self.fixture.rebind()
        self.assert_validation_error("contains undeclared keys ['observed_commit']")

    def test_retired_umbrella_item_ids_are_rejected_after_rebinding(self) -> None:
        for retired_id in RETIRED_UMBRELLA_ITEM_IDS:
            with self.subTest(retired_id=retired_id):
                child = self.root / f"retired-{retired_id}"
                fixture = SnapshotFixture(child)
                fixture.board["items"][1]["id"] = retired_id
                fixture.write("board", fixture.board)
                fixture.rebind()
                with self.assertRaises(adoption.SnapshotValidationError) as caught:
                    fixture.validate()
                joined = "\n".join(caught.exception.errors)
                self.assertIn("retired umbrella item ID", joined)
                self.assertIn(retired_id, joined)

    def test_pass_with_nonempty_errors_is_rejected(self) -> None:
        self.fixture.check["errors"] = ["hidden failure"]
        self.fixture.rebind()
        self.assert_validation_error("must be an empty array")

    def test_contributor_and_support_path_bindings_are_exact(self) -> None:
        mutations = (
            ("claim_interface", "https://example.invalid/claim", "approved issue route"),
            ("handback_interface", "https://example.invalid/return", "approved handback route"),
            ("consumer_helper", "scripts/other.py", "must equal 'scripts/get-adopt.py'"),
            (
                "consumer_regression",
                "scripts/other-offline-test.py",
                "must equal 'scripts/test-adopt-offline.py'",
            ),
            ("claim_auditor", "scripts/other-auditor.py", "must equal 'scripts/check-claims.py'"),
            ("claim_regression", "scripts/other-claims.py", "must equal 'scripts/test-claims.py'"),
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

    def test_missing_consumer_regression_binding_is_rejected(self) -> None:
        self.fixture.board.pop("consumer_regression")
        self.fixture.write("board", self.fixture.board)
        self.fixture.rebind()
        self.assert_validation_error("missing required keys ['consumer_regression']")

    def test_missing_claim_regression_and_continuous_validation_are_rejected(self) -> None:
        for field in ("claim_regression", "continuous_validation"):
            with self.subTest(field=field):
                child = self.root / f"missing-{field}"
                fixture = SnapshotFixture(child)
                fixture.board.pop(field)
                fixture.write("board", fixture.board)
                fixture.rebind()
                with self.assertRaises(adoption.SnapshotValidationError) as caught:
                    fixture.validate()
                self.assertIn(
                    f"missing required keys ['{field}']", "\n".join(caught.exception.errors)
                )

    def test_consumer_modes_reject_wrong_reversed_and_extra_ordering(self) -> None:
        mutations = (
            ("wrong", [adoption.CONSUMER_MODES[0], "working_tree"]),
            ("reversed", list(reversed(adoption.CONSUMER_MODES))),
            ("extra", [*adoption.CONSUMER_MODES, "working_tree"]),
        )
        for name, modes in mutations:
            with self.subTest(name=name):
                child = self.root / f"consumer-modes-{name}"
                fixture = SnapshotFixture(child)
                fixture.board["consumer_modes"] = modes
                fixture.write("board", fixture.board)
                fixture.rebind()
                with self.assertRaises(adoption.SnapshotValidationError) as caught:
                    fixture.validate()
                self.assertIn("board.consumer_modes", "\n".join(caught.exception.errors))

    def test_board_and_check_consumer_modes_must_match(self) -> None:
        self.fixture.check["consumer_modes"] = list(reversed(adoption.CONSUMER_MODES))
        self.fixture.rebind()
        error = self.assert_validation_error("validation check.consumer_modes")
        self.assertIn("does not match the validation receipt", "\n".join(error.errors))

    def test_claim_auditor_modes_reject_reversed_extra_and_missing_entries(self) -> None:
        mutations: list[tuple[str, str, list[str]]] = []
        for channel, modes in adoption.CLAIM_AUDITOR_MODES.items():
            mutations.extend(
                (
                    (channel, "reversed", list(reversed(modes))),
                    (channel, "extra", [*modes, "working_tree"]),
                    (channel, "missing", list(modes[:-1])),
                )
            )
        for channel, name, modes in mutations:
            with self.subTest(channel=channel, name=name):
                child = self.root / f"claim-auditor-modes-{channel}-{name}"
                fixture = SnapshotFixture(child)
                fixture.board["claim_auditor_modes"][channel] = modes
                fixture.write("board", fixture.board)
                fixture.rebind()
                with self.assertRaises(adoption.SnapshotValidationError) as caught:
                    fixture.validate()
                self.assertIn("board.claim_auditor_modes", "\n".join(caught.exception.errors))

    def test_continuous_validation_rejects_every_contract_drift(self) -> None:
        def set_field(field: str, value: object):
            return lambda contract: contract.__setitem__(field, value)

        mutations = (
            ("workflow", set_field("workflow", ".github/workflows/other.yml")),
            ("checkout", set_field("checkout", "full_checkout")),
            (
                "events-reversed",
                set_field("events", list(reversed(CONTINUOUS_VALIDATION["events"]))),
            ),
            ("events-extra", set_field("events", [*CONTINUOUS_VALIDATION["events"], "schedule"])),
            ("events-missing", set_field("events", CONTINUOUS_VALIDATION["events"][:-1])),
            (
                "checks-reversed",
                set_field("checks", list(reversed(CONTINUOUS_VALIDATION["checks"]))),
            ),
            ("checks-extra", set_field("checks", [*CONTINUOUS_VALIDATION["checks"], "corpus_build"])),
            ("checks-missing", set_field("checks", CONTINUOUS_VALIDATION["checks"][:-1])),
            ("unpinned-actions", set_field("pinned_actions", False)),
            ("corpus-builds", set_field("corpus_builds", True)),
            ("extra-field", set_field("surprise", True)),
        )
        for name, mutate in mutations:
            with self.subTest(name=name):
                child = self.root / f"continuous-validation-{name}"
                fixture = SnapshotFixture(child)
                mutate(fixture.board["continuous_validation"])
                fixture.write("board", fixture.board)
                fixture.rebind()
                with self.assertRaises(adoption.SnapshotValidationError) as caught:
                    fixture.validate()
                self.assertIn("continuous_validation", "\n".join(caught.exception.errors))

    def test_board_and_check_new_transport_bindings_must_match(self) -> None:
        mutations = (
            (
                "consumer_regression",
                "scripts/other-offline-test.py",
                "validation check.consumer_regression",
            ),
            (
                "claim_auditor_modes",
                {
                    "board": list(reversed(adoption.CLAIM_AUDITOR_MODES["board"])),
                    "issues": list(adoption.CLAIM_AUDITOR_MODES["issues"]),
                },
                "validation check.claim_auditor_modes",
            ),
            (
                "claim_regression",
                "scripts/other-claims.py",
                "validation check.claim_regression",
            ),
            (
                "continuous_validation",
                {
                    **copy.deepcopy(CONTINUOUS_VALIDATION),
                    "pinned_actions": False,
                },
                "validation check.continuous_validation",
            ),
        )
        for field, value, fragment in mutations:
            with self.subTest(field=field):
                child = self.root / f"check-mismatch-{field}"
                fixture = SnapshotFixture(child)
                fixture.check[field] = value
                fixture.rebind()
                with self.assertRaises(adoption.SnapshotValidationError) as caught:
                    fixture.validate()
                joined = "\n".join(caught.exception.errors)
                self.assertIn(fragment, joined)
                self.assertIn("does not match the validation receipt", joined)

    def test_check_requires_claim_regression_and_continuous_validation(self) -> None:
        for field in ("claim_regression", "continuous_validation"):
            with self.subTest(field=field):
                child = self.root / f"check-missing-{field}"
                fixture = SnapshotFixture(child)
                fixture.check.pop(field)
                fixture.rebind()
                with self.assertRaises(adoption.SnapshotValidationError) as caught:
                    fixture.validate()
                self.assertIn(
                    f"missing required keys ['{field}']", "\n".join(caught.exception.errors)
                )

    def test_schema_consumer_mode_contract_drift_is_rejected(self) -> None:
        self.fixture.schema["properties"]["consumer_modes"]["prefixItems"] = [
            {"const": mode} for mode in reversed(adoption.CONSUMER_MODES)
        ]
        self.fixture.write("schema", self.fixture.schema)
        self.fixture.rebind()
        self.assert_validation_error("schema document.properties.consumer_modes")

    def test_schema_new_transport_contract_rejects_wrong_loose_and_dropped_rules(self) -> None:
        def wrong_regression(schema: dict[str, object]) -> None:
            schema["properties"]["consumer_regression"]["const"] = "scripts/other.py"

        def loose_mode_array(schema: dict[str, object]) -> None:
            schema["properties"]["claim_auditor_modes"]["properties"]["board"][
                "items"
            ] = {}

        def dropped_issue_rule(schema: dict[str, object]) -> None:
            schema["properties"]["claim_auditor_modes"]["properties"].pop("issues")

        mutations = (
            ("wrong-regression", wrong_regression, "properties.consumer_regression"),
            ("loose-mode-array", loose_mode_array, "properties.claim_auditor_modes"),
            ("dropped-issue-rule", dropped_issue_rule, "properties.claim_auditor_modes"),
        )
        for name, mutate, fragment in mutations:
            with self.subTest(name=name):
                child = self.root / f"schema-{name}"
                fixture = SnapshotFixture(child)
                mutate(fixture.schema)
                fixture.write("schema", fixture.schema)
                fixture.rebind()
                with self.assertRaises(adoption.SnapshotValidationError) as caught:
                    fixture.validate()
                self.assertIn(fragment, "\n".join(caught.exception.errors))

    def test_schema_claim_regression_and_continuous_validation_are_closed_exactly(self) -> None:
        def cv(schema: dict[str, object]) -> dict[str, object]:
            return schema["properties"]["continuous_validation"]

        def wrong_claim_regression(schema: dict[str, object]) -> None:
            schema["properties"]["claim_regression"]["const"] = "scripts/other.py"

        def drop_top_required(schema: dict[str, object]) -> None:
            schema["required"].remove("continuous_validation")

        def drop_inner_required(schema: dict[str, object]) -> None:
            cv(schema)["required"].remove("workflow")

        def wrong_workflow(schema: dict[str, object]) -> None:
            cv(schema)["properties"]["workflow"]["const"] = ".github/workflows/other.yml"

        def wrong_checkout(schema: dict[str, object]) -> None:
            cv(schema)["properties"]["checkout"]["const"] = "full_checkout"

        def reverse_events(schema: dict[str, object]) -> None:
            cv(schema)["properties"]["events"]["prefixItems"].reverse()

        def open_events(schema: dict[str, object]) -> None:
            cv(schema)["properties"]["events"]["items"] = {}

        def reverse_checks(schema: dict[str, object]) -> None:
            cv(schema)["properties"]["checks"]["prefixItems"].reverse()

        def loosen_check_count(schema: dict[str, object]) -> None:
            cv(schema)["properties"]["checks"]["maxItems"] += 1

        def unpin_actions(schema: dict[str, object]) -> None:
            cv(schema)["properties"]["pinned_actions"]["const"] = False

        def permit_corpus_builds(schema: dict[str, object]) -> None:
            cv(schema)["properties"]["corpus_builds"]["const"] = True

        def open_object(schema: dict[str, object]) -> None:
            cv(schema)["additionalProperties"] = True

        mutations = (
            ("wrong-claim-regression", wrong_claim_regression, "properties.claim_regression"),
            ("drop-top-required", drop_top_required, "required"),
            ("drop-inner-required", drop_inner_required, "properties.continuous_validation"),
            ("wrong-workflow", wrong_workflow, "properties.continuous_validation"),
            ("wrong-checkout", wrong_checkout, "properties.continuous_validation"),
            ("reverse-events", reverse_events, "properties.continuous_validation"),
            ("open-events", open_events, "properties.continuous_validation"),
            ("reverse-checks", reverse_checks, "properties.continuous_validation"),
            ("loosen-check-count", loosen_check_count, "properties.continuous_validation"),
            ("unpin-actions", unpin_actions, "properties.continuous_validation"),
            ("permit-corpus-builds", permit_corpus_builds, "properties.continuous_validation"),
            ("open-object", open_object, "properties.continuous_validation"),
        )
        for name, mutate, fragment in mutations:
            with self.subTest(name=name):
                child = self.root / f"schema-continuous-{name}"
                fixture = SnapshotFixture(child)
                mutate(fixture.schema)
                fixture.write("schema", fixture.schema)
                fixture.rebind()
                with self.assertRaises(adoption.SnapshotValidationError) as caught:
                    fixture.validate()
                self.assertIn(fragment, "\n".join(caught.exception.errors))

    def test_consumer_mode_aggregate_drift_is_rejected(self) -> None:
        self.fixture.check["aggregate"]["consumer_modes"] = 3
        self.fixture.rebind()
        self.assert_validation_error("validation check.aggregate.consumer_modes")

    def test_claim_auditor_mode_aggregate_drift_is_rejected(self) -> None:
        for field in ("claim_auditor_board_modes", "claim_auditor_issue_modes"):
            with self.subTest(field=field):
                child = self.root / f"aggregate-{field}"
                fixture = SnapshotFixture(child)
                fixture.check["aggregate"][field] = 3
                fixture.rebind()
                with self.assertRaises(adoption.SnapshotValidationError) as caught:
                    fixture.validate()
                self.assertIn(
                    f"validation check.aggregate.{field}",
                    "\n".join(caught.exception.errors),
                )

    def test_continuous_validation_aggregate_drift_is_rejected(self) -> None:
        self.fixture.check["aggregate"]["continuous_validation_checks"] = 5
        self.fixture.rebind()
        self.assert_validation_error(
            "validation check.aggregate.continuous_validation_checks"
        )

    def test_consumer_regression_check_flag_must_be_present_and_true(self) -> None:
        for name, mutate in (
            (
                "false",
                lambda checks: checks.__setitem__("consumer_regression_contract", False),
            ),
            ("missing", lambda checks: checks.pop("consumer_regression_contract")),
        ):
            with self.subTest(name=name):
                child = self.root / f"consumer-regression-flag-{name}"
                fixture = SnapshotFixture(child)
                mutate(fixture.check["checks"])
                fixture.rebind()
                with self.assertRaises(adoption.SnapshotValidationError) as caught:
                    fixture.validate()
                self.assertIn("validation check.checks", "\n".join(caught.exception.errors))

    def test_claim_regression_and_continuous_validation_flags_must_be_present_and_true(
        self,
    ) -> None:
        for field in ("claim_regression_contract", "continuous_validation_contract"):
            for name, mutate in (
                ("false", lambda checks, field=field: checks.__setitem__(field, False)),
                ("missing", lambda checks, field=field: checks.pop(field)),
            ):
                with self.subTest(field=field, name=name):
                    child = self.root / f"{field}-{name}"
                    fixture = SnapshotFixture(child)
                    mutate(fixture.check["checks"])
                    fixture.rebind()
                    with self.assertRaises(adoption.SnapshotValidationError) as caught:
                        fixture.validate()
                    self.assertIn(
                        "validation check.checks", "\n".join(caught.exception.errors)
                    )

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

    def test_repository_path_aggregates_must_match_recomputed_and_pinned_counts(self) -> None:
        for field in ("repository_path_checks", "tracked_repository_paths"):
            with self.subTest(field=field):
                child = self.root / f"path-aggregate-{field}"
                fixture = SnapshotFixture(child)
                fixture.check["aggregate"][field] = 999
                fixture.rebind()
                with self.assertRaises(adoption.SnapshotValidationError) as caught:
                    fixture.validate()
                joined = "\n".join(caught.exception.errors)
                self.assertIn(f"validation check.aggregate.{field}", joined)
                self.assertIn("does not match pin value 33", joined)

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
