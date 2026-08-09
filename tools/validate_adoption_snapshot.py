#!/usr/bin/env python3
"""Validate and inspect one pinned interlanguage adoption snapshot.

The application performs no HTTP/API request and never executes a URL or
command from the external board.  The caller supplies four files on local,
non-on-demand storage in a private snapshot directory that is not being changed
concurrently.  The tool recognizes one code-reviewed production snapshot and
turns its coordination rows into inert candidate pointers.  Importing a row as
a live Mathematics Commons packet remains a separate steward-controlled act.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import stat
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path, PurePosixPath
from typing import Any, Iterable, Sequence
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
PIN_PATH = Path(__file__).with_name("interlanguage_adoption_pin.json")

MAX_PIN_BYTES = 128 * 1024
MAX_SNAPSHOT_FILE_BYTES = 2 * 1024 * 1024
MAX_SNAPSHOT_TOTAL_BYTES = 4 * 1024 * 1024
MAX_JSON_DEPTH = 64
MAX_JSON_NODES = 250_000
MAX_ITEMS = 10_000
MAX_MIRRORS = 100_000
MAX_QUERY_CHARS = 256

WINDOWS_RESERVED_NAMES = {
    "CON",
    "PRN",
    "AUX",
    "NUL",
    *(f"COM{index}" for index in range(1, 10)),
    *(f"LPT{index}" for index in range(1, 10)),
}
WINDOWS_FILE_ATTRIBUTE_REPARSE_POINT = 0x00000400
WINDOWS_FILE_ATTRIBUTE_OFFLINE = 0x00001000
WINDOWS_FILE_ATTRIBUTE_RECALL_ON_OPEN = 0x00040000
WINDOWS_FILE_ATTRIBUTE_RECALL_ON_DATA_ACCESS = 0x00400000
WINDOWS_UNSAFE_STORAGE_ATTRIBUTES = (
    WINDOWS_FILE_ATTRIBUTE_REPARSE_POINT
    | WINDOWS_FILE_ATTRIBUTE_OFFLINE
    | WINDOWS_FILE_ATTRIBUTE_RECALL_ON_OPEN
    | WINDOWS_FILE_ATTRIBUTE_RECALL_ON_DATA_ACCESS
)
WINDOWS_LOCAL_DRIVE_TYPES = {2, 3, 6}  # removable, fixed, RAM disk
BIDI_FORMATTING_CODEPOINTS = {
    0x061C,
    0x200E,
    0x200F,
    *range(0x202A, 0x202F),
    *range(0x2066, 0x206A),
}

PRODUCTION_APPROVED_COMMIT = "5ccd9357187c2f4a246a40fd5ef45f6df6ae88b0"
PRODUCTION_APPROVED_TREE = "739cb174f6a9efb262923c7f09cd69c09f7d5529"
PRODUCTION_CONTENT_SOURCE_COMMIT = "ae59d85d406d52448eacc0794916b34c8189a739"
PRODUCTION_CONTENT_SOURCE_TREE = "4452635bf293d379e55652280781c3d077615fab"
PRODUCTION_WORKTREE_BASE_COMMIT = "1ecde9651d5fa508c5a3c0056021bfa89c4ea888"
VALIDATION_INPUT_MODE = "named_worktree_files"
PRODUCTION_EVIDENCE_CLOSURE_COMMIT = PRODUCTION_APPROVED_COMMIT
PRODUCTION_EVIDENCE_BASE_COMMIT = "9c858b61c57f0c7e7281c275e0bb9c6c0f999d53"
PRODUCTION_MAP_OBSERVATION_COMMIT = "61b9d5cab6441b8fa02e34630d7145a916f0ea37"
PRODUCTION_FILE_IDENTITIES = {
    "board": (
        "manifests/adopt.json",
        82281,
        "bba918fd8255d07af7a312577d7cf92be1052f8fe39f2c1caa9afb8be05f2a6e",
    ),
    "schema": (
        "manifests/adopt.schema.json",
        18528,
        "c0a4527e8b32649a7792e7eee0d192c2e80dc373ff4d98270173304af55de996",
    ),
    "check": (
        "manifests/adopt.check.json",
        5661,
        "013f6766aab6c0dfec598af03fde64a00bcc3225cc1f90f14abf8abfa3baec56",
    ),
    "map_manifest": (
        "manifests/github-custody/20260807_maps_r5.json",
        17998,
        "ec0f2b625455efa88ffc3c376c46fad8024114f1f87819d776accf6837f1864d",
    ),
}
PRODUCTION_EXPECTED_AGGREGATE = {
    "items": 46,
    "mirrors": 0,
    "current_work": 3,
    "ready_for_adoption": 38,
    "future": 5,
    "required_maps": 19,
    "queue_sources": 2,
    "queue_snapshot_sources": 2,
    "queue_snapshot_bytes": 93584,
    "human_board_rows": 46,
    "represented_human_board_items": 46,
    "missing_human_board_items": 0,
    "unknown_human_board_ids": 0,
    "duplicate_human_board_ids": 0,
    "human_index_rows": 46,
    "human_index_authors": 38,
    "human_index_works": 46,
    "human_index_series": 16,
    "human_index_languages": 16,
    "human_index_corpora": 21,
    "repository_path_checks": 135,
    "tracked_repository_paths": 135,
    "issue_labels": 4,
    "issue_label_templates": 6,
    "consumer_modes": 2,
    "claim_auditor_board_modes": 2,
    "claim_auditor_issue_modes": 2,
    "continuous_validation_checks": 4,
    "workflow_registry": 14,
    "workflow_tokens_used": 14,
    "unreferenced_workflows": 0,
    "named_owner_rows": 3,
    "unclaimed_owner_rows": 43,
}

REPOSITORY_URL = "https://github.com/KokunoYumeto/modern-latex-manuscripts"
REPOSITORY_NAME = "KokunoYumeto/modern-latex-manuscripts"
SCHEMA_PATH = "manifests/adopt.schema.json"
BOARD_PATH = "manifests/adopt.json"
CHECK_PATH = "manifests/adopt.check.json"
MAP_PATH = "manifests/github-custody/20260807_maps_r5.json"
CLAIM_URL = (
    "https://github.com/KokunoYumeto/modern-latex-manuscripts/"
    "issues/new?template=adopt.yml"
)
HANDBACK_URL = (
    "https://github.com/KokunoYumeto/modern-latex-manuscripts/"
    "issues/new?template=handback.yml"
)
CONSUMER_HELPER_PATH = "scripts/get-adopt.py"
CONSUMER_REGRESSION_PATH = "scripts/test-adopt-offline.py"
CLAIM_AUDITOR_PATH = "scripts/check-claims.py"
CLAIM_REGRESSION_PATH = "scripts/test-claims.py"
CONTINUOUS_VALIDATION_PATH = ".github/workflows/adopt.yml"
HUMAN_BOARD_PATH = "docs/adopt.md"
HUMAN_INDEX_PATH = "docs/adopt-index.md"
HUMAN_WORKFLOWS_PATH = "docs/adopt-flows.md"
ISSUE_LABELS_PATH = ".github/labels.json"
HUMAN_BOARD_IDENTITY = (
    HUMAN_BOARD_PATH,
    30105,
    "8996cc8bdcdddfd72e10865386b3555bb2edf065f1e8a6421cac4cdc155cec7c",
)
CONSUMER_HELPER_IDENTITY = (
    CONSUMER_HELPER_PATH,
    10952,
    "0351d7c759ce8825e3dcdd7fb36b1ce29b58ff1e6676e7be07f660ab21edda15",
)
CONSUMER_REGRESSION_IDENTITY = (
    CONSUMER_REGRESSION_PATH,
    7526,
    "68f1cfee2af3d2fb74ca86b8bd9266ad026699809239d4a6a09cbd24122a0b74",
)
CLAIM_AUDITOR_IDENTITY = (
    CLAIM_AUDITOR_PATH,
    13596,
    "100f8d72f2f6beedd979c69d99bfc519b8d19351e73ae01516b1e86bd32591b6",
)
CLAIM_REGRESSION_IDENTITY = (
    CLAIM_REGRESSION_PATH,
    7501,
    "22cd1c6fe9b42310b830b0299acc2e09f2c6a41d37ad078332281f63e279f1aa",
)
CONTINUOUS_VALIDATION_IDENTITY = (
    CONTINUOUS_VALIDATION_PATH,
    3546,
    "0c3c179bae2b83862f9a5f4bb05a34c8e4256ff41c069958ef1babebcb357bcf",
)
HUMAN_INDEX_IDENTITY = (
    HUMAN_INDEX_PATH,
    8025,
    "e8a9708f72f2f5042cca278fdbb8fe2563aac64eb0af7a494d5e21253a2c662d",
)
HUMAN_WORKFLOWS_IDENTITY = (
    HUMAN_WORKFLOWS_PATH,
    6390,
    "03a643656961c27b2aafb8bd8e4c5dc52926b35f55e847f22b0c06ae2decbdd2",
)
ISSUE_LABELS_IDENTITY = (
    ISSUE_LABELS_PATH,
    1104,
    "b0e1267fb5e0e5db0aaba796755cb4806c4775b26297ed4bbcf6e9989c084e61",
)
SEALED_PUBLIC_RECEIPTS = (
    (
        "continuous_validation_readback",
        "manifests/published-github/20260809_adopt_ci_rb.json",
        7332,
        "ad7e38d1604e7e5f5e6ed31848117b8d3d8ec2210610329f1d27d31e929499b1",
    ),
    (
        "source_link_audit",
        "manifests/github-custody/20260809_links_r28.json",
        10767,
        "93745d9cc5f64f148ecdcaec026a52c4cb6da87dd323bade03264cf5f6df89de",
    ),
)

TOP_REQUIRED = (
    "schema",
    "schema_url",
    "validation",
    "board_role",
    "updated",
    "evidence_base_commit",
    "repository",
    "human_board",
    "human_index",
    "archive_authority",
    "ownership_policy",
    "map_manifest",
    "required_maps",
    "queue_sources",
    "queue_snapshot",
    "snapshot_policy",
    "consumer_helper",
    "consumer_modes",
    "consumer_regression",
    "claim_auditor",
    "claim_auditor_modes",
    "claim_regression",
    "continuous_validation",
    "claim_interface",
    "handback_interface",
    "human_workflows",
    "workflow_fields",
    "workflows",
    "enums",
    "fields",
    "mirror_fields",
    "mirrors",
    "items",
)
ITEM_FIELDS = (
    "id",
    "author",
    "work",
    "series",
    "corpus",
    "lane_state",
    "coverage_state",
    "adoption_status",
    "priority",
    "readiness",
    "owner",
    "owner_scope",
    "languages",
    "archive_path",
    "related_paths",
    "source_basis",
    "next_cursor",
    "prerequisites",
    "workflow",
    "claim_url",
    "updated",
    "notes",
)
MIRROR_FIELDS = ("id", "item_id", "owner", "scope", "url", "status", "updated")
LANE_STATES = ("current_work", "ready_for_adoption", "future")
PRIORITIES = ("high", "medium", "exploratory")
READINESS = (
    "active",
    "exact_cursor",
    "repair_ready",
    "review_ready",
    "expansion_ready",
    "continuation_ready",
    "intake_ready",
    "source_discovery_first",
)
ADOPTION_STATUSES = (
    "maintained_parallel_review_welcome",
    "open_parallel_mirrors_welcome",
    "claimed_active_parallel_mirrors_welcome",
    "paused_open_for_handoff",
    "future_evidence_needed",
)
MIRROR_STATUSES = ("declared", "active", "returned", "paused", "withdrawn")
QUEUE_SOURCES = ("docs/known-gaps.md", "docs/work-queue.md")
QUEUE_SNAPSHOT = (
    (
        "docs/known-gaps.md",
        37422,
        "72125D27EDBD1C38BC1BCF70D887A976FC1AE1E39114EFBFEA00F62F3552BDC2",
    ),
    (
        "docs/work-queue.md",
        56162,
        "3A1431FB3DF8F18942BABAE4F411DBC156C4BC5A1742B81ECBFB74E8F087BA46",
    ),
)
OWNERSHIP_POLICY = {
    "named_owner_required_for": ["current_work"],
    "null_owner_means": "unclaimed",
    "null_owner_allowed_for": ["ready_for_adoption", "future"],
    "unclaimed_scope_prefix": "unclaimed",
    "claims_are_nonexclusive": True,
}
CONSUMER_MODES = ("raw_github", "local_git_object_database")
CLAIM_AUDITOR_MODES = {
    "board": list(CONSUMER_MODES),
    "issues": ["public_github_api", "json_fixture"],
}
CONTINUOUS_VALIDATION = {
    "workflow": CONTINUOUS_VALIDATION_PATH,
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
WORKFLOW_FIELDS = (
    "id",
    "purpose",
    "start_when",
    "inputs",
    "steps",
    "evidence",
    "stop_conditions",
    "handback",
)
WORKFLOW_IDS = (
    "assembly_review",
    "bounded_continuation",
    "bounded_pilot",
    "bounded_repair",
    "bounded_transcription",
    "bounded_translation",
    "correction_propagation",
    "independent_mirror",
    "independent_review",
    "source_audit",
    "source_discovery",
    "source_intake",
    "source_recovery",
    "table_audit",
)
WORKFLOW_REGISTRY_SHA256 = (
    "21c6803abe09fb240be4e7863c5500a6471e3a44eff3a6082e392205a3ebe4ae"
)
ISSUE_TEMPLATE_PATHS = (
    ".github/ISSUE_TEMPLATE/adopt.yml",
    ".github/ISSUE_TEMPLATE/correction.yml",
    ".github/ISSUE_TEMPLATE/handback.yml",
    ".github/ISSUE_TEMPLATE/rendering_problem.md",
    ".github/ISSUE_TEMPLATE/source-suggestion.yml",
    ".github/ISSUE_TEMPLATE/source_or_translation_correction.md",
)
SNAPSHOT_PATHS = (BOARD_PATH, SCHEMA_PATH, CHECK_PATH, MAP_PATH)
REQUIRED_CHECKS = (
    "validation_status_pass",
    "validation_errors_empty",
    "declared_bytes_sha256_match",
    "schema_validation_pass",
)
ARCHIVE_AUTHORITY_FIELDS = (
    "coverage_maps",
    "reader_shelf",
    "source_shelf",
    "archive_history",
)
CHECK_FLAGS = {
    "exact_item_field_contract": True,
    "enum_contract": True,
    "unique_ids": True,
    "state_partitions_present": True,
    "repository_paths_tracked": True,
    "archive_layer_preserved": True,
    "required_map_contract": True,
    "required_maps_represented": True,
    "queue_source_contract": True,
    "queue_sources_represented": True,
    "queue_snapshot_contract": True,
    "human_board_complete": True,
    "human_dimension_index_complete": True,
    "consumer_helper_contract": True,
    "consumer_regression_contract": True,
    "claim_auditor_contract": True,
    "claim_regression_contract": True,
    "continuous_validation_contract": True,
    "contributor_interface_contract": True,
    "issue_label_contract": True,
    "workflow_registry_contract": True,
    "ownership_semantics": True,
    "snapshot_policy_contract": True,
    "external_network_queried": False,
    "producer_files_mutated": False,
    "compile_render_or_ocr_run": False,
    "global_filesystem_search": False,
}
CHECK_AGGREGATE_FIELDS = (
    "items",
    "mirrors",
    "current_work",
    "ready_for_adoption",
    "future",
    "unique_item_ids",
    "unique_mirror_ids",
    "required_maps",
    "represented_required_maps",
    "missing_required_maps",
    "queue_sources",
    "represented_queue_sources",
    "missing_queue_sources",
    "queue_snapshot_sources",
    "queue_snapshot_bytes",
    "human_board_rows",
    "represented_human_board_items",
    "missing_human_board_items",
    "unknown_human_board_ids",
    "duplicate_human_board_ids",
    "human_index_rows",
    "human_index_authors",
    "human_index_works",
    "human_index_series",
    "human_index_languages",
    "human_index_corpora",
    "repository_path_checks",
    "tracked_repository_paths",
    "issue_labels",
    "issue_label_templates",
    "consumer_modes",
    "claim_auditor_board_modes",
    "claim_auditor_issue_modes",
    "continuous_validation_checks",
    "workflow_registry",
    "workflow_tokens_used",
    "unreferenced_workflows",
    "named_owner_rows",
    "unclaimed_owner_rows",
)
TRUST_BOUNDARY = {
    "application_http_api_fetch": "forbidden",
    "snapshot_storage": "caller_supplied_local_non_on_demand_private_directory",
    "contributed_urls": "data_only_never_fetched_or_executed",
    "mathematical_authority": "none",
    "live_packet_creation": "forbidden",
}

FULL_COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
SNAKE_RE = re.compile(r"^[a-z0-9]+(?:_[a-z0-9]+)*$")
MAP_RE = re.compile(r"^docs/[a-z0-9]+(?:-[a-z0-9]+)*-map\.md$")


class SnapshotValidationError(ValueError):
    """A deterministic collection of fail-closed snapshot errors."""

    def __init__(self, errors: Iterable[str]):
        unique = tuple(dict.fromkeys(str(error) for error in errors))
        self.errors = unique
        super().__init__("; ".join(unique))


class DuplicateKeyError(ValueError):
    """Raised when JSON contains an ambiguous duplicate object key."""


@dataclass(frozen=True)
class ValidatedSnapshot:
    pin: dict[str, Any]
    board: dict[str, Any]
    schema_document: dict[str, Any]
    check: dict[str, Any]
    map_manifest: dict[str, Any]
    identities: dict[str, dict[str, Any]]
    aggregate: dict[str, int]


def _pairs_without_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateKeyError(f"duplicate JSON key {key!r}")
        result[key] = value
    return result


def _reject_nonfinite_constant(value: str) -> None:
    raise ValueError(f"non-finite JSON number {value!r} is forbidden")


def _bound_json_structure(value: Any, label: str) -> None:
    stack: list[tuple[Any, int]] = [(value, 0)]
    nodes = 0
    while stack:
        current, depth = stack.pop()
        nodes += 1
        if nodes > MAX_JSON_NODES:
            raise ValueError(f"{label} exceeds the bounded JSON node count")
        if depth > MAX_JSON_DEPTH:
            raise ValueError(f"{label} exceeds the bounded JSON nesting depth")
        if isinstance(current, dict):
            stack.extend((item, depth + 1) for item in current.values())
        elif isinstance(current, list):
            stack.extend((item, depth + 1) for item in current)


def _decode_json(payload: bytes, label: str) -> Any:
    if payload.startswith(b"\xef\xbb\xbf"):
        raise ValueError(f"{label} must be UTF-8 without a BOM")
    if b"\x00" in payload:
        raise ValueError(f"{label} contains NUL bytes")
    if b"\r" in payload:
        raise ValueError(f"{label} must use LF line endings")
    if not payload.endswith(b"\n"):
        raise ValueError(f"{label} must end with one LF-delimited JSON document")
    try:
        text = payload.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError(f"{label} is not strict UTF-8: {exc}") from exc
    try:
        value = json.loads(
            text,
            object_pairs_hook=_pairs_without_duplicates,
            parse_constant=_reject_nonfinite_constant,
        )
        _bound_json_structure(value, label)
        return value
    except (json.JSONDecodeError, DuplicateKeyError, RecursionError, ValueError) as exc:
        raise ValueError(f"{label} is not unambiguous JSON: {exc}") from exc


def _read_pin(path: Path = PIN_PATH) -> dict[str, Any]:
    try:
        size = path.stat().st_size
    except OSError as exc:
        raise SnapshotValidationError([f"cannot inspect pin descriptor: {exc}"]) from exc
    if size > MAX_PIN_BYTES:
        raise SnapshotValidationError(["pin descriptor exceeds its bounded size limit"])
    try:
        payload = path.read_bytes()
        value = _decode_json(payload, "pin descriptor")
    except (OSError, ValueError) as exc:
        raise SnapshotValidationError([str(exc)]) from exc
    if not isinstance(value, dict):
        raise SnapshotValidationError(["pin descriptor must be a JSON object"])
    return value


def _error(errors: list[str], label: str, message: str) -> None:
    errors.append(f"{label}: {message}")


def _require_keys(
    value: Any,
    required: Sequence[str],
    label: str,
    errors: list[str],
    *,
    exact: bool,
) -> bool:
    if not isinstance(value, dict):
        _error(errors, label, "must be an object")
        return False
    missing = [key for key in required if key not in value]
    if missing:
        _error(errors, label, f"missing required keys {missing}")
    if exact:
        extra = sorted(set(value) - set(required))
        if extra:
            _error(errors, label, f"contains undeclared keys {extra}")
    return not missing and (not exact or not (set(value) - set(required)))


def _safe_text(value: Any, label: str, errors: list[str], *, min_length: int = 0) -> bool:
    if not isinstance(value, str):
        _error(errors, label, "must be a string")
        return False
    if len(value) < min_length:
        _error(errors, label, f"must contain at least {min_length} character(s)")
        return False
    if any(
        ord(character) < 32
        or 0x7F <= ord(character) <= 0x9F
        or ord(character) in BIDI_FORMATTING_CODEPOINTS
        for character in value
    ):
        _error(errors, label, "contains a terminal, C1, or bidirectional formatting control")
        return False
    return True


def _valid_date(value: Any, label: str, errors: list[str]) -> bool:
    if not _safe_text(value, label, errors, min_length=10):
        return False
    try:
        parsed = date.fromisoformat(value)
    except ValueError:
        _error(errors, label, "must be an RFC 3339 full-date")
        return False
    if parsed.isoformat() != value:
        _error(errors, label, "must use canonical YYYY-MM-DD form")
        return False
    return True


def _valid_commit(value: Any, label: str, errors: list[str]) -> bool:
    if not isinstance(value, str) or FULL_COMMIT_RE.fullmatch(value) is None:
        _error(errors, label, "must be a full lowercase 40-hex Git object ID")
        return False
    return True


def _valid_repo_locator(
    value: Any,
    label: str,
    errors: list[str],
    *,
    allow_null: bool,
    allow_empty: bool,
) -> bool:
    if value is None:
        if allow_null:
            return True
        _error(errors, label, "must not be null")
        return False
    if not _safe_text(value, label, errors, min_length=0 if allow_empty else 1):
        return False
    if not value and allow_empty:
        return True
    path_part, separator, fragment = value.partition("#")
    if separator and not fragment:
        _error(errors, label, "has an empty fragment")
        return False
    decoded = unquote(path_part)
    if decoded != path_part:
        _error(errors, label, "must not use percent-encoded path components")
        return False
    if (
        not path_part
        or path_part.startswith(("/", "\\"))
        or "\\" in path_part
        or ":" in path_part
        or "?" in path_part
    ):
        _error(errors, label, "must be a portable repository-relative path")
        return False
    parts = PurePosixPath(path_part).parts
    if not parts or any(part in {"", ".", ".."} for part in parts):
        _error(errors, label, "contains an unsafe or ambiguous path component")
        return False
    if PurePosixPath(path_part).as_posix() != path_part:
        _error(errors, label, "must be lexically normalized")
        return False
    for part in parts:
        if part.rstrip(" .") != part:
            _error(errors, label, "contains a Windows-aliased trailing dot or space")
            return False
        reserved_stem = part.split(".", 1)[0].upper()
        if reserved_stem in WINDOWS_RESERVED_NAMES:
            _error(errors, label, f"contains reserved Windows component {part!r}")
            return False
    return True


def _valid_https_uri(value: Any, label: str, errors: list[str]) -> bool:
    if not _safe_text(value, label, errors, min_length=1):
        return False
    parsed = urlsplit(value)
    if parsed.scheme != "https" or not parsed.netloc:
        _error(errors, label, "must be an absolute HTTPS URI")
        return False
    if parsed.username is not None or parsed.password is not None:
        _error(errors, label, "must not contain URI credentials")
        return False
    if any(character.isspace() for character in value):
        _error(errors, label, "must not contain whitespace")
        return False
    return True


def _unique_string_list(
    value: Any,
    label: str,
    errors: list[str],
    *,
    min_items: int,
    min_length: int,
) -> list[str] | None:
    if not isinstance(value, list):
        _error(errors, label, "must be an array")
        return None
    if len(value) < min_items:
        _error(errors, label, f"must contain at least {min_items} item(s)")
    if len(value) != len(set(item for item in value if isinstance(item, str))):
        _error(errors, label, "must contain unique strings")
    for index, item in enumerate(value):
        _safe_text(item, f"{label}[{index}]", errors, min_length=min_length)
    if not all(isinstance(item, str) for item in value):
        return None
    return value


def _validate_pin(pin: dict[str, Any], errors: list[str], *, production: bool) -> None:
    required = (
        "schema",
        "repository",
        "approved_snapshot_commit",
        "approved_snapshot_tree",
        "content_source_commit",
        "content_source_tree",
        "evidence_closure_commit",
        "evidence_base_commit",
        "map_observation_commit",
        "discovery_ref",
        "discovery_ref_role",
        "snapshot_paths",
        "files",
        "optional_human_projection",
        "optional_consumer_helper_identity",
        "optional_consumer_regression_identity",
        "optional_claim_auditor_identity",
        "optional_claim_regression_identity",
        "optional_continuous_validation_identity",
        "sealed_public_receipts",
        "expected_aggregate",
        "trust_boundary",
    )
    if not _require_keys(pin, required, "pin", errors, exact=True):
        return
    if pin.get("schema") != "mathematics-commons-adoption-pin-v2":
        _error(errors, "pin.schema", "has an unsupported value")
    if pin.get("repository") != REPOSITORY_URL:
        _error(errors, "pin.repository", "does not name the approved repository")
    _valid_commit(pin.get("approved_snapshot_commit"), "pin.approved_snapshot_commit", errors)
    _valid_commit(pin.get("approved_snapshot_tree"), "pin.approved_snapshot_tree", errors)
    _valid_commit(pin.get("content_source_commit"), "pin.content_source_commit", errors)
    _valid_commit(pin.get("content_source_tree"), "pin.content_source_tree", errors)
    _valid_commit(pin.get("evidence_closure_commit"), "pin.evidence_closure_commit", errors)
    _valid_commit(pin.get("evidence_base_commit"), "pin.evidence_base_commit", errors)
    _valid_commit(pin.get("map_observation_commit"), "pin.map_observation_commit", errors)
    if pin.get("evidence_closure_commit") != pin.get("approved_snapshot_commit"):
        _error(
            errors,
            "pin.evidence_closure_commit",
            "must equal the immutable approved snapshot closure",
        )
    if pin.get("discovery_ref") != "main":
        _error(errors, "pin.discovery_ref", "must remain the discovery-only main ref")
    if pin.get("discovery_ref_role") != "locator_only_not_an_immutable_snapshot":
        _error(errors, "pin.discovery_ref_role", "must deny snapshot authority to the locator")
    if pin.get("snapshot_paths") != list(SNAPSHOT_PATHS):
        _error(errors, "pin.snapshot_paths", "must list the four ordered same-commit paths")
    if pin.get("trust_boundary") != TRUST_BOUNDARY:
        _error(errors, "pin.trust_boundary", "does not match the offline data-only boundary")

    files = pin.get("files")
    roles = tuple(PRODUCTION_FILE_IDENTITIES)
    if not isinstance(files, list) or len(files) != len(roles):
        _error(errors, "pin.files", "must contain exactly four file identities")
    else:
        seen: set[str] = set()
        seen_paths: dict[str, str] = {}
        for index, value in enumerate(files):
            label = f"pin.files[{index}]"
            if not _require_keys(value, ("role", "path", "bytes", "sha256"), label, errors, exact=True):
                continue
            role = value.get("role")
            if role not in roles:
                _error(errors, f"{label}.role", "is not a recognized snapshot role")
            elif role in seen:
                _error(errors, f"{label}.role", "is duplicated")
            else:
                seen.add(role)
            path_value = value.get("path")
            path_valid = _valid_repo_locator(
                path_value,
                f"{label}.path",
                errors,
                allow_null=False,
                allow_empty=False,
            )
            if path_valid and isinstance(path_value, str):
                path_key = path_value.casefold()
                prior_path = seen_paths.get(path_key)
                if prior_path is not None:
                    _error(
                        errors,
                        f"{label}.path",
                        f"collides portably with another snapshot path {prior_path!r}",
                    )
                else:
                    seen_paths[path_key] = path_value
            byte_count = value.get("bytes")
            if type(byte_count) is not int or not (0 < byte_count <= MAX_SNAPSHOT_FILE_BYTES):
                _error(errors, f"{label}.bytes", "must be a positive bounded integer")
            digest = value.get("sha256")
            if not isinstance(digest, str) or SHA256_RE.fullmatch(digest) is None:
                _error(errors, f"{label}.sha256", "must be lowercase SHA-256")
        if seen != set(roles):
            _error(errors, "pin.files", "does not cover every required role exactly once")

    human_projection = pin.get("optional_human_projection")
    if _require_keys(
        human_projection,
        ("role", "path", "bytes", "sha256", "machine_required"),
        "pin.optional_human_projection",
        errors,
        exact=True,
    ):
        assert isinstance(human_projection, dict)
        if human_projection.get("role") != "human_board":
            _error(errors, "pin.optional_human_projection.role", "must be human_board")
        _valid_repo_locator(
            human_projection.get("path"),
            "pin.optional_human_projection.path",
            errors,
            allow_null=False,
            allow_empty=False,
        )
        if type(human_projection.get("bytes")) is not int or human_projection.get("bytes") <= 0:
            _error(errors, "pin.optional_human_projection.bytes", "must be a positive integer")
        digest = human_projection.get("sha256")
        if not isinstance(digest, str) or SHA256_RE.fullmatch(digest) is None:
            _error(errors, "pin.optional_human_projection.sha256", "must be lowercase SHA-256")
        if human_projection.get("machine_required") is not False:
            _error(
                errors,
                "pin.optional_human_projection.machine_required",
                "must remain false for the four-file machine contract",
            )

    optional_code_specs = (
        (
            "optional_consumer_helper_identity",
            "consumer_helper",
            CONSUMER_HELPER_IDENTITY,
        ),
        (
            "optional_consumer_regression_identity",
            "consumer_regression",
            CONSUMER_REGRESSION_IDENTITY,
        ),
        (
            "optional_claim_auditor_identity",
            "claim_auditor",
            CLAIM_AUDITOR_IDENTITY,
        ),
        (
            "optional_claim_regression_identity",
            "claim_regression",
            CLAIM_REGRESSION_IDENTITY,
        ),
        (
            "optional_continuous_validation_identity",
            "continuous_validation",
            CONTINUOUS_VALIDATION_IDENTITY,
        ),
    )
    optional_code_identities: dict[str, Any] = {}
    for field, expected_role, _expected_identity in optional_code_specs:
        identity = pin.get(field)
        optional_code_identities[field] = identity
        label = f"pin.{field}"
        if not _require_keys(
            identity,
            ("role", "path", "bytes", "sha256", "machine_required"),
            label,
            errors,
            exact=True,
        ):
            continue
        assert isinstance(identity, dict)
        if identity.get("role") != expected_role:
            _error(errors, f"{label}.role", f"must be {expected_role}")
        _valid_repo_locator(
            identity.get("path"),
            f"{label}.path",
            errors,
            allow_null=False,
            allow_empty=False,
        )
        if type(identity.get("bytes")) is not int or identity.get("bytes") <= 0:
            _error(errors, f"{label}.bytes", "must be a positive integer")
        digest = identity.get("sha256")
        if not isinstance(digest, str) or SHA256_RE.fullmatch(digest) is None:
            _error(errors, f"{label}.sha256", "must be lowercase SHA-256")
        if identity.get("machine_required") is not False:
            _error(
                errors,
                f"{label}.machine_required",
                "must remain false for the four-file machine contract",
            )

    receipts = pin.get("sealed_public_receipts")
    if not isinstance(receipts, list) or len(receipts) != len(SEALED_PUBLIC_RECEIPTS):
        _error(
            errors,
            "pin.sealed_public_receipts",
            "must contain exactly the two reviewed non-input receipt identities",
        )
    else:
        seen_receipt_roles: set[str] = set()
        for index, receipt in enumerate(receipts):
            label = f"pin.sealed_public_receipts[{index}]"
            if not _require_keys(
                receipt,
                ("role", "path", "bytes", "sha256", "machine_required"),
                label,
                errors,
                exact=True,
            ):
                continue
            assert isinstance(receipt, dict)
            role = receipt.get("role")
            if role not in {value[0] for value in SEALED_PUBLIC_RECEIPTS}:
                _error(errors, f"{label}.role", "is not a recognized sealed receipt role")
            elif role in seen_receipt_roles:
                _error(errors, f"{label}.role", "is duplicated")
            else:
                seen_receipt_roles.add(role)
            _valid_repo_locator(
                receipt.get("path"),
                f"{label}.path",
                errors,
                allow_null=False,
                allow_empty=False,
            )
            if type(receipt.get("bytes")) is not int or receipt.get("bytes") <= 0:
                _error(errors, f"{label}.bytes", "must be a positive integer")
            digest = receipt.get("sha256")
            if not isinstance(digest, str) or SHA256_RE.fullmatch(digest) is None:
                _error(errors, f"{label}.sha256", "must be lowercase SHA-256")
            if receipt.get("machine_required") is not False:
                _error(errors, f"{label}.machine_required", "must remain false")

    expected = pin.get("expected_aggregate")
    if not _require_keys(
        expected,
        tuple(PRODUCTION_EXPECTED_AGGREGATE),
        "pin.expected_aggregate",
        errors,
        exact=True,
    ):
        expected = None
    if isinstance(expected, dict):
        for key, value in expected.items():
            if type(value) is not int or value < 0:
                _error(errors, f"pin.expected_aggregate.{key}", "must be a nonnegative integer")

    if production:
        if pin.get("approved_snapshot_commit") != PRODUCTION_APPROVED_COMMIT:
            _error(errors, "pin.approved_snapshot_commit", "does not match the compiled production pin")
        if pin.get("approved_snapshot_tree") != PRODUCTION_APPROVED_TREE:
            _error(errors, "pin.approved_snapshot_tree", "does not match the compiled production pin")
        if pin.get("content_source_commit") != PRODUCTION_CONTENT_SOURCE_COMMIT:
            _error(errors, "pin.content_source_commit", "does not match the compiled production pin")
        if pin.get("content_source_tree") != PRODUCTION_CONTENT_SOURCE_TREE:
            _error(errors, "pin.content_source_tree", "does not match the compiled production pin")
        if pin.get("evidence_closure_commit") != PRODUCTION_EVIDENCE_CLOSURE_COMMIT:
            _error(errors, "pin.evidence_closure_commit", "does not match the compiled production pin")
        if pin.get("evidence_base_commit") != PRODUCTION_EVIDENCE_BASE_COMMIT:
            _error(errors, "pin.evidence_base_commit", "does not match the compiled production pin")
        if pin.get("map_observation_commit") != PRODUCTION_MAP_OBSERVATION_COMMIT:
            _error(errors, "pin.map_observation_commit", "does not match the compiled production pin")
        if isinstance(files, list):
            actual = {
                value.get("role"): (value.get("path"), value.get("bytes"), value.get("sha256"))
                for value in files
                if isinstance(value, dict)
            }
            if actual != PRODUCTION_FILE_IDENTITIES:
                _error(errors, "pin.files", "does not match the compiled production identities")
        if expected != PRODUCTION_EXPECTED_AGGREGATE:
            _error(errors, "pin.expected_aggregate", "does not match the compiled production aggregate")
        if isinstance(human_projection, dict):
            actual_human = (
                human_projection.get("path"),
                human_projection.get("bytes"),
                human_projection.get("sha256"),
            )
            if actual_human != HUMAN_BOARD_IDENTITY:
                _error(
                    errors,
                    "pin.optional_human_projection",
                    "does not match the compiled optional human-board identity",
                )
        for field, _expected_role, expected_identity in optional_code_specs:
            identity = optional_code_identities.get(field)
            if not isinstance(identity, dict):
                continue
            actual_identity = (
                identity.get("path"),
                identity.get("bytes"),
                identity.get("sha256"),
            )
            if actual_identity != expected_identity:
                _error(
                    errors,
                    f"pin.{field}",
                    "does not match the compiled optional code identity",
                )
        if isinstance(receipts, list):
            actual_receipts = tuple(
                (
                    value.get("role"),
                    value.get("path"),
                    value.get("bytes"),
                    value.get("sha256"),
                )
                for value in receipts
                if isinstance(value, dict)
            )
            if actual_receipts != SEALED_PUBLIC_RECEIPTS:
                _error(
                    errors,
                    "pin.sealed_public_receipts",
                    "does not match the compiled non-input receipt identities",
                )


def _unsafe_windows_storage(stat_result: os.stat_result) -> bool:
    if os.name != "nt":
        return False
    attributes = int(getattr(stat_result, "st_file_attributes", 0))
    reparse_tag = int(getattr(stat_result, "st_reparse_tag", 0))
    return bool(attributes & WINDOWS_UNSAFE_STORAGE_ATTRIBUTES or reparse_tag)


def _windows_drive_type(anchor: str) -> int:
    import ctypes

    get_drive_type = ctypes.windll.kernel32.GetDriveTypeW
    get_drive_type.argtypes = [ctypes.c_wchar_p]
    get_drive_type.restype = ctypes.c_uint
    return int(get_drive_type(anchor))


def _local_snapshot_root(root: Path, errors: list[str]) -> Path | None:
    """Return an absolute local root after rejecting remote/on-demand indirection."""

    raw_root = os.fspath(root)
    if os.name == "nt" and raw_root.replace("/", "\\").startswith("\\\\"):
        _error(errors, "snapshot root", "must not use a UNC or device namespace")
        return None
    absolute_root = Path(os.path.abspath(root))
    if os.name == "nt":
        anchor = absolute_root.anchor
        if not anchor or _windows_drive_type(anchor) not in WINDOWS_LOCAL_DRIVE_TYPES:
            _error(errors, "snapshot root", "must be on a local fixed, removable, or RAM drive")
            return None
        current = Path(anchor)
        lexical_components = [current]
        for part in absolute_root.parts[1:]:
            current = current / part
            lexical_components.append(current)
        for component_path in lexical_components:
            try:
                component = os.lstat(component_path)
            except OSError as exc:
                _error(errors, "snapshot root", f"cannot inspect a path component: {exc}")
                return None
            if stat.S_ISLNK(component.st_mode) or _unsafe_windows_storage(component):
                _error(
                    errors,
                    "snapshot root",
                    "must not traverse a link, junction, reparse point, or on-demand component",
                )
                return None
    return absolute_root


def _component_identity(value: os.stat_result) -> tuple[int, int, int, int, int]:
    return (
        int(value.st_dev),
        int(value.st_ino),
        int(stat.S_IFMT(value.st_mode)),
        int(getattr(value, "st_file_attributes", 0)),
        int(getattr(value, "st_reparse_tag", 0)),
    )


def _opened_handle_path(file_descriptor: int) -> Path | None:
    """Bind an open descriptor to its kernel-resolved path before reading."""

    if os.name == "nt":
        import ctypes
        import msvcrt

        handle = msvcrt.get_osfhandle(file_descriptor)
        get_final_path = ctypes.windll.kernel32.GetFinalPathNameByHandleW
        get_final_path.argtypes = [
            ctypes.c_void_p,
            ctypes.c_wchar_p,
            ctypes.c_uint,
            ctypes.c_uint,
        ]
        get_final_path.restype = ctypes.c_uint
        needed = int(get_final_path(handle, None, 0, 0))
        if needed <= 0:
            raise OSError(ctypes.get_last_error(), "cannot resolve the opened file handle")
        buffer = ctypes.create_unicode_buffer(needed + 1)
        written = int(get_final_path(handle, buffer, len(buffer), 0))
        if written <= 0 or written >= len(buffer):
            raise OSError(ctypes.get_last_error(), "cannot resolve the opened file handle")
        value = buffer.value
        if value.startswith("\\\\?\\UNC\\"):
            value = "\\\\" + value[8:]
        elif value.startswith("\\\\?\\"):
            value = value[4:]
        return Path(value).resolve(strict=True)
    if sys.platform.startswith("linux"):
        descriptor_link = Path(f"/proc/self/fd/{file_descriptor}")
        target = os.readlink(descriptor_link)
        if target.endswith(" (deleted)"):
            raise OSError("opened snapshot file was deleted")
        return Path(target).resolve(strict=True)
    return None


def _same_path(left: Path, right: Path) -> bool:
    return os.path.normcase(os.path.normpath(str(left))) == os.path.normcase(
        os.path.normpath(str(right))
    )


def _snapshot_file_bytes(
    root: Path,
    relative: str,
    expected_bytes: int,
    expected_sha256: str,
    errors: list[str],
) -> bytes | None:
    label = f"snapshot file {relative}"
    if not _valid_repo_locator(relative, label, errors, allow_null=False, allow_empty=False):
        return None
    local_root = _local_snapshot_root(root, errors)
    if local_root is None:
        return None
    try:
        root_lstat = os.lstat(local_root)
    except OSError as exc:
        _error(errors, "snapshot root", f"cannot be inspected: {exc}")
        return None
    if stat.S_ISLNK(root_lstat.st_mode) or _unsafe_windows_storage(root_lstat):
        _error(errors, "snapshot root", "must not be a link, reparse point, or on-demand path")
        return None
    if not stat.S_ISDIR(root_lstat.st_mode):
        _error(errors, "snapshot root", "must be an existing directory")
        return None
    try:
        resolved_root = local_root.resolve(strict=True)
    except OSError as exc:
        _error(errors, "snapshot root", f"cannot be resolved: {exc}")
        return None

    candidate = local_root
    component_identities: list[tuple[Path, tuple[int, int, int, int, int]]] = []
    for part in PurePosixPath(relative).parts:
        candidate = candidate / part
        try:
            component = os.lstat(candidate)
        except OSError as exc:
            _error(errors, label, f"cannot inspect a required component: {exc}")
            return None
        if stat.S_ISLNK(component.st_mode) or _unsafe_windows_storage(component):
            _error(errors, label, "must not traverse a link, junction, reparse point, or on-demand file")
            return None
        component_identities.append((candidate, _component_identity(component)))
    try:
        resolved_candidate = candidate.resolve(strict=True)
        resolved_candidate.relative_to(resolved_root)
        before = os.stat(candidate, follow_symlinks=False)
    except (OSError, ValueError) as exc:
        _error(errors, label, f"does not resolve as a file inside the snapshot root: {exc}")
        return None
    if not stat.S_ISREG(before.st_mode):
        _error(errors, label, "must be an ordinary file")
        return None
    if before.st_nlink != 1:
        _error(errors, label, "must not be a hard-linked file")
        return None
    if before.st_size != expected_bytes or before.st_size > MAX_SNAPSHOT_FILE_BYTES:
        _error(errors, label, "does not have the approved bounded byte length")
        return None

    flags = os.O_RDONLY
    for optional_flag in ("O_BINARY", "O_CLOEXEC", "O_NOFOLLOW", "O_NONBLOCK"):
        flags |= int(getattr(os, optional_flag, 0))
    file_descriptor: int | None = None
    try:
        file_descriptor = os.open(candidate, flags)
        opened = os.fstat(file_descriptor)
        if not stat.S_ISREG(opened.st_mode) or opened.st_nlink != 1:
            raise OSError("opened object is not one ordinary unlinked file")
        if _unsafe_windows_storage(opened):
            raise OSError("opened object is a reparse point or on-demand file")
        identity_fields = ("st_dev", "st_ino", "st_size", "st_mtime_ns")
        if any(getattr(before, field) != getattr(opened, field) for field in identity_fields):
            raise OSError("required file changed before its handle was bound")
        opened_path = _opened_handle_path(file_descriptor)
        if opened_path is None:
            raise OSError("this platform cannot bind an opened file handle to its resolved path")
        if not _same_path(opened_path, resolved_candidate):
            raise OSError("opened handle does not match the inspected snapshot path")
        try:
            opened_path.relative_to(resolved_root)
        except ValueError as exc:
            raise OSError("opened handle escapes the snapshot root") from exc
        for component_path, prior_identity in component_identities:
            current = os.lstat(component_path)
            if _component_identity(current) != prior_identity:
                raise OSError("snapshot path changed before the file was read")

        chunks: list[bytes] = []
        remaining = MAX_SNAPSHOT_FILE_BYTES + 1
        while remaining:
            chunk = os.read(file_descriptor, min(64 * 1024, remaining))
            if not chunk:
                break
            chunks.append(chunk)
            remaining -= len(chunk)
        payload = b"".join(chunks)
        after = os.fstat(file_descriptor)
        if any(getattr(opened, field) != getattr(after, field) for field in identity_fields):
            raise OSError("required file changed while its bound handle was being read")
        for component_path, prior_identity in component_identities:
            current = os.lstat(component_path)
            if _component_identity(current) != prior_identity:
                raise OSError("snapshot path changed while the file was read")
    except OSError as exc:
        _error(errors, label, f"cannot be read through a stable local handle: {exc}")
        return None
    finally:
        if file_descriptor is not None:
            os.close(file_descriptor)

    if len(payload) != expected_bytes or hashlib.sha256(payload).hexdigest() != expected_sha256:
        _error(errors, label, "does not match the approved byte identity")
    return payload


def _validate_schema_document(value: Any, errors: list[str]) -> None:
    label = "schema document"
    if not isinstance(value, dict):
        _error(errors, label, "must be an object")
        return
    if value.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
        _error(errors, f"{label}.$schema", "must declare Draft 2020-12")
    if value.get("$id") != (
        "https://raw.githubusercontent.com/KokunoYumeto/"
        "modern-latex-manuscripts/main/manifests/adopt.schema.json"
    ):
        _error(errors, f"{label}.$id", "does not identify the upstream board schema")
    if value.get("type") != "object":
        _error(errors, f"{label}.type", "must be object")
    if value.get("required") != list(TOP_REQUIRED):
        _error(errors, f"{label}.required", "does not match the compiled top-level contract")
    properties = value.get("properties")
    if not isinstance(properties, dict):
        _error(errors, f"{label}.properties", "must be an object")
    else:
        if properties.get("schema", {}).get("const") != "math-commons-adoption-v1":
            _error(errors, f"{label}.properties.schema", "does not bind the board schema name")
        if properties.get("schema_url", {}).get("const") != SCHEMA_PATH:
            _error(errors, f"{label}.properties.schema_url", "does not bind the schema path")
        if properties.get("validation", {}).get("const") != CHECK_PATH:
            _error(errors, f"{label}.properties.validation", "does not bind the check path")
        if properties.get("map_manifest", {}).get("const") != MAP_PATH:
            _error(errors, f"{label}.properties.map_manifest", "does not bind the map path")
        if properties.get("human_index", {}).get("const") != HUMAN_INDEX_PATH:
            _error(errors, f"{label}.properties.human_index", "does not bind the human index")
        if properties.get("consumer_helper", {}).get("const") != CONSUMER_HELPER_PATH:
            _error(errors, f"{label}.properties.consumer_helper", "does not bind the helper path")
        consumer_modes_schema = properties.get("consumer_modes")
        expected_consumer_modes_schema = {
            "type": "array",
            "prefixItems": [{"const": mode} for mode in CONSUMER_MODES],
            "items": False,
            "minItems": len(CONSUMER_MODES),
            "maxItems": len(CONSUMER_MODES),
        }
        if consumer_modes_schema != expected_consumer_modes_schema:
            _error(
                errors,
                f"{label}.properties.consumer_modes",
                "does not bind the exact offline/remote mode contract",
            )
        if properties.get("consumer_regression", {}).get("const") != CONSUMER_REGRESSION_PATH:
            _error(
                errors,
                f"{label}.properties.consumer_regression",
                "does not bind the offline consumer regression path",
            )
        if properties.get("claim_auditor", {}).get("const") != CLAIM_AUDITOR_PATH:
            _error(errors, f"{label}.properties.claim_auditor", "does not bind the claim auditor")
        expected_claim_auditor_modes_schema = {
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
                for key, modes in CLAIM_AUDITOR_MODES.items()
            },
            "additionalProperties": False,
        }
        if properties.get("claim_auditor_modes") != expected_claim_auditor_modes_schema:
            _error(
                errors,
                f"{label}.properties.claim_auditor_modes",
                "does not bind the exact board/issue auditor mode contract",
            )
        if properties.get("claim_regression", {}).get("const") != CLAIM_REGRESSION_PATH:
            _error(
                errors,
                f"{label}.properties.claim_regression",
                "does not bind the claim lifecycle regression path",
            )
        expected_continuous_validation_schema = {
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
                        {"const": value} for value in CONTINUOUS_VALIDATION["events"]
                    ],
                    "items": False,
                    "minItems": len(CONTINUOUS_VALIDATION["events"]),
                    "maxItems": len(CONTINUOUS_VALIDATION["events"]),
                },
                "checks": {
                    "type": "array",
                    "prefixItems": [
                        {"const": value} for value in CONTINUOUS_VALIDATION["checks"]
                    ],
                    "items": False,
                    "minItems": len(CONTINUOUS_VALIDATION["checks"]),
                    "maxItems": len(CONTINUOUS_VALIDATION["checks"]),
                },
                "pinned_actions": {"const": CONTINUOUS_VALIDATION["pinned_actions"]},
                "corpus_builds": {"const": CONTINUOUS_VALIDATION["corpus_builds"]},
            },
            "additionalProperties": False,
        }
        if properties.get("continuous_validation") != expected_continuous_validation_schema:
            _error(
                errors,
                f"{label}.properties.continuous_validation",
                "does not bind the exact closed continuous-validation contract",
            )
        if properties.get("claim_interface", {}).get("const") != CLAIM_URL:
            _error(errors, f"{label}.properties.claim_interface", "does not bind the claim form")
        if properties.get("handback_interface", {}).get("const") != HANDBACK_URL:
            _error(errors, f"{label}.properties.handback_interface", "does not bind the handback form")
        if properties.get("human_workflows", {}).get("const") != HUMAN_WORKFLOWS_PATH:
            _error(
                errors,
                f"{label}.properties.human_workflows",
                "does not bind the human workflow guide",
            )
        expected_workflow_fields_schema = {
            "type": "array",
            "prefixItems": [{"const": field} for field in WORKFLOW_FIELDS],
            "items": False,
            "minItems": len(WORKFLOW_FIELDS),
            "maxItems": len(WORKFLOW_FIELDS),
        }
        if properties.get("workflow_fields") != expected_workflow_fields_schema:
            _error(
                errors,
                f"{label}.properties.workflow_fields",
                "does not bind the exact ordered workflow fields",
            )
    definitions = value.get("$defs")
    if not isinstance(definitions, dict):
        _error(errors, f"{label}.$defs", "must be an object")
        return
    item = definitions.get("item")
    mirror = definitions.get("mirror")
    source_identity = definitions.get("sourceIdentity")
    workflow = definitions.get("workflow")
    expected_source_identity = {
        "type": "object",
        "required": ["path", "bytes", "sha256"],
        "properties": {
            "path": {"type": "string", "minLength": 1},
            "bytes": {"type": "integer", "minimum": 0},
            "sha256": {"type": "string", "pattern": "^[0-9A-F]{64}$"},
        },
        "additionalProperties": False,
    }
    if source_identity != expected_source_identity:
        _error(
            errors,
            f"{label}.$defs.sourceIdentity",
            "does not match the exact queue identity contract",
        )
    string_list_schema = {
        "type": "array",
        "minItems": 1,
        "uniqueItems": True,
        "items": {"type": "string", "minLength": 1},
    }
    expected_workflow = {
        "type": "object",
        "required": list(WORKFLOW_FIELDS),
        "properties": {
            "id": {
                "type": "string",
                "pattern": "^[a-z0-9]+(?:_[a-z0-9]+)*$",
            },
            "purpose": {"type": "string", "minLength": 1},
            "start_when": {"type": "string", "minLength": 1},
            **{
                field: dict(string_list_schema)
                for field in ("inputs", "steps", "evidence", "stop_conditions", "handback")
            },
        },
        "additionalProperties": False,
    }
    if workflow != expected_workflow:
        _error(
            errors,
            f"{label}.$defs.workflow",
            "does not match the exact workflow field contract",
        )
    if not isinstance(item, dict) or item.get("required") != list(ITEM_FIELDS):
        _error(errors, f"{label}.$defs.item.required", "does not match the compiled item fields")
    if not isinstance(item, dict) or item.get("additionalProperties") is not False:
        _error(errors, f"{label}.$defs.item", "must reject extra item fields")
    if not isinstance(mirror, dict) or mirror.get("required") != list(MIRROR_FIELDS):
        _error(errors, f"{label}.$defs.mirror.required", "does not match the compiled mirror fields")
    if not isinstance(mirror, dict) or mirror.get("additionalProperties") is not False:
        _error(errors, f"{label}.$defs.mirror", "must reject extra mirror fields")


def _validate_item(
    item: Any,
    index: int,
    claim_interface: Any,
    errors: list[str],
) -> None:
    label = f"board.items[{index}]"
    if not _require_keys(item, ITEM_FIELDS, label, errors, exact=True):
        return
    item_id = item.get("id")
    if not isinstance(item_id, str) or SLUG_RE.fullmatch(item_id) is None:
        _error(errors, f"{label}.id", "must be a lowercase hyphenated slug")
    _safe_text(item.get("author"), f"{label}.author", errors, min_length=1)
    _safe_text(item.get("work"), f"{label}.work", errors, min_length=1)
    series = item.get("series")
    if series is not None:
        _safe_text(series, f"{label}.series", errors)
    corpus = item.get("corpus")
    if not isinstance(corpus, str) or SNAKE_RE.fullmatch(corpus) is None:
        _error(errors, f"{label}.corpus", "must be a lowercase snake-case token")
    lane = item.get("lane_state")
    if lane not in LANE_STATES:
        _error(errors, f"{label}.lane_state", "is outside the declared enum")
    coverage = item.get("coverage_state")
    if not isinstance(coverage, str) or SNAKE_RE.fullmatch(coverage) is None:
        _error(errors, f"{label}.coverage_state", "must be a lowercase snake-case token")
    if item.get("adoption_status") not in ADOPTION_STATUSES:
        _error(errors, f"{label}.adoption_status", "is outside the declared enum")
    if item.get("priority") not in PRIORITIES:
        _error(errors, f"{label}.priority", "is outside the declared enum")
    if item.get("readiness") not in READINESS:
        _error(errors, f"{label}.readiness", "is outside the declared enum")
    owner = item.get("owner")
    if owner is not None:
        _safe_text(owner, f"{label}.owner", errors)
    _safe_text(item.get("owner_scope"), f"{label}.owner_scope", errors, min_length=1)
    _unique_string_list(item.get("languages"), f"{label}.languages", errors, min_items=1, min_length=2)
    _valid_repo_locator(
        item.get("archive_path"),
        f"{label}.archive_path",
        errors,
        allow_null=True,
        allow_empty=True,
    )
    related = _unique_string_list(
        item.get("related_paths"), f"{label}.related_paths", errors, min_items=0, min_length=1
    )
    if related is not None:
        for related_index, path in enumerate(related):
            _valid_repo_locator(
                path,
                f"{label}.related_paths[{related_index}]",
                errors,
                allow_null=False,
                allow_empty=False,
            )
    _safe_text(item.get("source_basis"), f"{label}.source_basis", errors, min_length=1)
    _safe_text(item.get("next_cursor"), f"{label}.next_cursor", errors, min_length=1)
    _unique_string_list(
        item.get("prerequisites"), f"{label}.prerequisites", errors, min_items=1, min_length=1
    )
    workflow = _unique_string_list(
        item.get("workflow"), f"{label}.workflow", errors, min_items=1, min_length=1
    )
    if workflow is not None:
        for workflow_index, token in enumerate(workflow):
            if SNAKE_RE.fullmatch(token) is None:
                _error(errors, f"{label}.workflow[{workflow_index}]", "must be snake case")
    _valid_https_uri(item.get("claim_url"), f"{label}.claim_url", errors)
    if item.get("claim_url") != claim_interface:
        _error(errors, f"{label}.claim_url", "must use the board's single claim interface")
    _valid_date(item.get("updated"), f"{label}.updated", errors)
    _safe_text(item.get("notes"), f"{label}.notes", errors, min_length=1)

    if lane == "current_work":
        if not isinstance(owner, str) or not owner:
            _error(errors, f"{label}.owner", "must identify an owner for current work")
        if item.get("readiness") != "active":
            _error(errors, f"{label}.readiness", "must be active for current work")
    elif lane == "ready_for_adoption":
        if not isinstance(item.get("archive_path"), str) or not item.get("archive_path"):
            _error(errors, f"{label}.archive_path", "must be nonempty for adoption-ready work")
    elif lane == "future":
        if owner is not None:
            _error(errors, f"{label}.owner", "must be null for future work")
        if item.get("adoption_status") != "future_evidence_needed":
            _error(errors, f"{label}.adoption_status", "must be future_evidence_needed")
        if item.get("readiness") != "source_discovery_first":
            _error(errors, f"{label}.readiness", "must be source_discovery_first")


def _validate_mirror(mirror: Any, index: int, errors: list[str]) -> None:
    label = f"board.mirrors[{index}]"
    if not _require_keys(mirror, MIRROR_FIELDS, label, errors, exact=True):
        return
    for field in ("id", "item_id"):
        value = mirror.get(field)
        if not isinstance(value, str) or SLUG_RE.fullmatch(value) is None:
            _error(errors, f"{label}.{field}", "must be a lowercase hyphenated slug")
    _safe_text(mirror.get("owner"), f"{label}.owner", errors, min_length=1)
    _safe_text(mirror.get("scope"), f"{label}.scope", errors, min_length=1)
    _valid_https_uri(mirror.get("url"), f"{label}.url", errors)
    if mirror.get("status") not in MIRROR_STATUSES:
        _error(errors, f"{label}.status", "is outside the declared enum")
    _valid_date(mirror.get("updated"), f"{label}.updated", errors)


def _base_locator(value: Any) -> str | None:
    if not isinstance(value, str) or not value:
        return None
    return value.split("#", 1)[0]


def _represented_paths(items: list[Any]) -> set[str]:
    represented: set[str] = set()
    for item in items:
        if not isinstance(item, dict):
            continue
        archive = _base_locator(item.get("archive_path"))
        if archive:
            represented.add(archive)
        related = item.get("related_paths")
        if isinstance(related, list):
            for value in related:
                base = _base_locator(value)
                if base:
                    represented.add(base)
    return represented


def _canonical_json_sha256(value: Any) -> str:
    payload = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _validate_queue_snapshot(value: Any, errors: list[str]) -> list[dict[str, Any]]:
    label = "board.queue_snapshot"
    if not isinstance(value, list):
        _error(errors, label, "must be an array")
        return []
    if len(value) != len(QUEUE_SNAPSHOT):
        _error(errors, label, "must contain exactly two source identities")
    observed: list[dict[str, Any]] = []
    for index, identity in enumerate(value):
        identity_label = f"{label}[{index}]"
        if not _require_keys(
            identity,
            ("path", "bytes", "sha256"),
            identity_label,
            errors,
            exact=True,
        ):
            continue
        assert isinstance(identity, dict)
        _valid_repo_locator(
            identity.get("path"),
            f"{identity_label}.path",
            errors,
            allow_null=False,
            allow_empty=False,
        )
        if type(identity.get("bytes")) is not int or identity.get("bytes") < 0:
            _error(errors, f"{identity_label}.bytes", "must be a nonnegative integer")
        digest = identity.get("sha256")
        if not isinstance(digest, str) or re.fullmatch(r"[0-9A-F]{64}", digest) is None:
            _error(errors, f"{identity_label}.sha256", "must be uppercase SHA-256")
        observed.append(identity)
    expected = [
        {"path": path, "bytes": size, "sha256": digest}
        for path, size, digest in QUEUE_SNAPSHOT
    ]
    if observed != expected:
        _error(errors, label, "does not match the two compiled queue-source identities")
    return observed


def _validate_workflow_registry(value: Any, errors: list[str]) -> set[str]:
    label = "board.workflows"
    if not isinstance(value, list):
        _error(errors, label, "must be an array")
        return set()
    if len(value) != len(WORKFLOW_IDS):
        _error(errors, label, f"must contain exactly {len(WORKFLOW_IDS)} definitions")
    observed_ids: list[str] = []
    for index, workflow in enumerate(value):
        workflow_label = f"{label}[{index}]"
        if not _require_keys(
            workflow,
            WORKFLOW_FIELDS,
            workflow_label,
            errors,
            exact=True,
        ):
            continue
        assert isinstance(workflow, dict)
        workflow_id = workflow.get("id")
        if not isinstance(workflow_id, str) or SNAKE_RE.fullmatch(workflow_id) is None:
            _error(errors, f"{workflow_label}.id", "must be a lowercase snake-case token")
        else:
            observed_ids.append(workflow_id)
        for field in ("purpose", "start_when"):
            _safe_text(workflow.get(field), f"{workflow_label}.{field}", errors, min_length=1)
        for field in ("inputs", "steps", "evidence", "stop_conditions", "handback"):
            _unique_string_list(
                workflow.get(field),
                f"{workflow_label}.{field}",
                errors,
                min_items=1,
                min_length=1,
            )
    if observed_ids != list(WORKFLOW_IDS):
        _error(errors, label, "does not contain the exact ordered workflow ID registry")
    if len(observed_ids) != len(set(observed_ids)):
        _error(errors, label, "contains duplicate workflow IDs")
    if _canonical_json_sha256(value) != WORKFLOW_REGISTRY_SHA256:
        _error(errors, label, "does not match the compiled exact workflow definitions")
    return set(observed_ids)


def _repository_path_references(board: dict[str, Any]) -> list[str]:
    references: list[str] = []
    # schema_url and validation are already counted in same_commit_paths.  This
    # mirrors the sealed producer check's exact 135-reference accounting.
    for key in (
        "human_board",
        "human_index",
        "map_manifest",
        "consumer_helper",
        "consumer_regression",
        "claim_auditor",
        "claim_regression",
        "human_workflows",
    ):
        value = board.get(key)
        if isinstance(value, str) and value:
            references.append(value)
    continuous_validation = board.get("continuous_validation")
    if isinstance(continuous_validation, dict):
        workflow = continuous_validation.get("workflow")
        if isinstance(workflow, str) and workflow:
            references.append(workflow)
    authority = board.get("archive_authority")
    if isinstance(authority, dict):
        for key in ARCHIVE_AUTHORITY_FIELDS:
            value = authority.get(key)
            if isinstance(value, str) and value:
                references.append(value)
    for key in ("required_maps", "queue_sources"):
        values = board.get(key)
        if isinstance(values, list):
            references.extend(value for value in values if isinstance(value, str) and value)
    queue_snapshot = board.get("queue_snapshot")
    if isinstance(queue_snapshot, list):
        references.extend(
            value.get("path")
            for value in queue_snapshot
            if isinstance(value, dict)
            and isinstance(value.get("path"), str)
            and value.get("path")
        )
    policy = board.get("snapshot_policy")
    if isinstance(policy, dict):
        values = policy.get("same_commit_paths")
        if isinstance(values, list):
            references.extend(value for value in values if isinstance(value, str) and value)
    references.extend((ISSUE_LABELS_PATH, *ISSUE_TEMPLATE_PATHS))
    items = board.get("items")
    if isinstance(items, list):
        for item in items:
            if not isinstance(item, dict):
                continue
            archive = item.get("archive_path")
            if isinstance(archive, str) and archive:
                references.append(archive)
            related = item.get("related_paths")
            if isinstance(related, list):
                references.extend(
                    value for value in related if isinstance(value, str) and value
                )
    return references


def _validate_board(value: Any, pin: dict[str, Any], errors: list[str]) -> dict[str, int]:
    if not _require_keys(value, TOP_REQUIRED, "board", errors, exact=False):
        return {}
    assert isinstance(value, dict)
    constants = {
        "schema": "math-commons-adoption-v1",
        "schema_url": SCHEMA_PATH,
        "validation": CHECK_PATH,
        "board_role": "operational_layer",
        "repository": REPOSITORY_URL,
        "human_board": HUMAN_BOARD_PATH,
        "human_index": HUMAN_INDEX_PATH,
        "map_manifest": MAP_PATH,
        "consumer_helper": CONSUMER_HELPER_PATH,
        "consumer_regression": CONSUMER_REGRESSION_PATH,
        "claim_auditor": CLAIM_AUDITOR_PATH,
        "claim_regression": CLAIM_REGRESSION_PATH,
        "human_workflows": HUMAN_WORKFLOWS_PATH,
    }
    for key, expected in constants.items():
        if value.get(key) != expected:
            _error(errors, f"board.{key}", f"must equal {expected!r}")
    _valid_date(value.get("updated"), "board.updated", errors)
    _valid_commit(value.get("evidence_base_commit"), "board.evidence_base_commit", errors)
    if value.get("evidence_base_commit") != pin.get("evidence_base_commit"):
        _error(errors, "board.evidence_base_commit", "does not match the approved pin")

    authority = value.get("archive_authority")
    if _require_keys(
        authority, ARCHIVE_AUTHORITY_FIELDS, "board.archive_authority", errors, exact=True
    ):
        for key in ARCHIVE_AUTHORITY_FIELDS:
            _valid_repo_locator(
                authority.get(key),
                f"board.archive_authority.{key}",
                errors,
                allow_null=False,
                allow_empty=False,
            )

    required_maps = _unique_string_list(
        value.get("required_maps"), "board.required_maps", errors, min_items=1, min_length=1
    )
    if required_maps is not None:
        for index, path in enumerate(required_maps):
            if MAP_RE.fullmatch(path) is None:
                _error(errors, f"board.required_maps[{index}]", "is not a canonical map path")
    if value.get("queue_sources") != list(QUEUE_SOURCES):
        _error(errors, "board.queue_sources", "must preserve the two ordered queue sources")
    queue_snapshot = _validate_queue_snapshot(value.get("queue_snapshot"), errors)
    if [entry.get("path") for entry in queue_snapshot] != list(QUEUE_SOURCES):
        _error(
            errors,
            "board.queue_snapshot",
            "must bind the same ordered paths as board.queue_sources",
        )

    if value.get("ownership_policy") != OWNERSHIP_POLICY:
        _error(
            errors,
            "board.ownership_policy",
            "does not match the non-exclusive named/unclaimed ownership contract",
        )

    policy = value.get("snapshot_policy")
    policy_fields = (
        "stable_locator_ref",
        "immutable_unit",
        "same_commit_paths",
        "required_checks",
        "mixed_revisions_forbidden",
    )
    if _require_keys(policy, policy_fields, "board.snapshot_policy", errors, exact=True):
        expected_policy = {
            "stable_locator_ref": "main",
            "immutable_unit": "human_approved_exact_commit",
            "same_commit_paths": list(SNAPSHOT_PATHS),
            "required_checks": list(REQUIRED_CHECKS),
            "mixed_revisions_forbidden": True,
        }
        if policy != expected_policy:
            _error(errors, "board.snapshot_policy", "does not match the fail-closed snapshot contract")
    _valid_https_uri(value.get("claim_interface"), "board.claim_interface", errors)
    if value.get("claim_interface") != CLAIM_URL:
        _error(errors, "board.claim_interface", "does not match the approved issue route")
    _valid_https_uri(value.get("handback_interface"), "board.handback_interface", errors)
    if value.get("handback_interface") != HANDBACK_URL:
        _error(errors, "board.handback_interface", "does not match the approved handback route")
    if value.get("workflow_fields") != list(WORKFLOW_FIELDS):
        _error(errors, "board.workflow_fields", "does not match the exact workflow field contract")
    workflow_ids = _validate_workflow_registry(value.get("workflows"), errors)
    if value.get("consumer_modes") != list(CONSUMER_MODES):
        _error(
            errors,
            "board.consumer_modes",
            "does not match the exact remote/offline consumer modes",
        )
    if value.get("claim_auditor_modes") != CLAIM_AUDITOR_MODES:
        _error(
            errors,
            "board.claim_auditor_modes",
            "does not match the exact board/issue auditor mode contract",
        )
    if value.get("continuous_validation") != CONTINUOUS_VALIDATION:
        _error(
            errors,
            "board.continuous_validation",
            "does not match the exact closed continuous-validation contract",
        )

    expected_enums = {
        "lane_state": list(LANE_STATES),
        "priority": list(PRIORITIES),
        "readiness": list(READINESS),
        "adoption_status": list(ADOPTION_STATUSES),
        "mirror_status": list(MIRROR_STATUSES),
    }
    if value.get("enums") != expected_enums:
        _error(errors, "board.enums", "does not match the compiled enum contract")
    if value.get("fields") != list(ITEM_FIELDS):
        _error(errors, "board.fields", "does not match the exact item field contract")
    if value.get("mirror_fields") != list(MIRROR_FIELDS):
        _error(errors, "board.mirror_fields", "does not match the exact mirror field contract")

    items = value.get("items")
    if not isinstance(items, list):
        _error(errors, "board.items", "must be an array")
        items = []
    elif not items:
        _error(errors, "board.items", "must not be empty")
    elif len(items) > MAX_ITEMS:
        _error(errors, "board.items", f"exceeds the {MAX_ITEMS}-item bound")
    for index, item in enumerate(items[:MAX_ITEMS]):
        _validate_item(item, index, value.get("claim_interface"), errors)

    named_owner_rows = 0
    unclaimed_owner_rows = 0
    used_workflows: set[str] = set()
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            continue
        lane = item.get("lane_state")
        owner = item.get("owner")
        owner_scope = item.get("owner_scope")
        if lane == "current_work":
            if isinstance(owner, str) and owner:
                named_owner_rows += 1
        elif lane in {"ready_for_adoption", "future"}:
            if owner is not None:
                _error(
                    errors,
                    f"board.items[{index}].owner",
                    "must be null for an unclaimed ready or future row",
                )
            else:
                unclaimed_owner_rows += 1
            if not isinstance(owner_scope, str) or not owner_scope.startswith("unclaimed"):
                _error(
                    errors,
                    f"board.items[{index}].owner_scope",
                    "must begin with the compiled unclaimed scope prefix",
                )
        workflow_tokens = item.get("workflow")
        if isinstance(workflow_tokens, list):
            for token in workflow_tokens:
                if isinstance(token, str):
                    used_workflows.add(token)
                    if token not in workflow_ids:
                        _error(
                            errors,
                            f"board.items[{index}].workflow",
                            f"uses undefined workflow token {token!r}",
                        )
    unused_workflows = workflow_ids - used_workflows
    if unused_workflows:
        _error(
            errors,
            "board.workflows",
            f"contains unreferenced workflow definitions {sorted(unused_workflows)}",
        )

    mirrors = value.get("mirrors")
    if not isinstance(mirrors, list):
        _error(errors, "board.mirrors", "must be an array")
        mirrors = []
    elif len(mirrors) > MAX_MIRRORS:
        _error(errors, "board.mirrors", f"exceeds the {MAX_MIRRORS}-mirror bound")
    for index, mirror in enumerate(mirrors[:MAX_MIRRORS]):
        _validate_mirror(mirror, index, errors)

    item_ids = [item.get("id") for item in items if isinstance(item, dict)]
    if len(item_ids) != len(set(item_ids)):
        _error(errors, "board.items", "contains duplicate item IDs")
    mirror_ids = [mirror.get("id") for mirror in mirrors if isinstance(mirror, dict)]
    if len(mirror_ids) != len(set(mirror_ids)):
        _error(errors, "board.mirrors", "contains duplicate mirror IDs")
    item_id_set = set(item_ids)
    for index, mirror in enumerate(mirrors):
        if isinstance(mirror, dict) and mirror.get("item_id") not in item_id_set:
            _error(errors, f"board.mirrors[{index}].item_id", "does not resolve to an item")

    represented = _represented_paths(items)
    missing_maps = sorted(set(required_maps or []) - represented)
    if missing_maps:
        _error(errors, "board.required_maps", f"not represented by operational rows: {missing_maps}")
    missing_queue = sorted(set(QUEUE_SOURCES) - represented)
    if missing_queue:
        _error(errors, "board.queue_sources", f"not represented by operational rows: {missing_queue}")

    counts = {
        state: sum(
            1
            for item in items
            if isinstance(item, dict) and item.get("lane_state") == state
        )
        for state in LANE_STATES
    }
    path_references = _repository_path_references(value)
    casefold_paths: dict[str, str] = {}
    for index, locator in enumerate(path_references):
        _valid_repo_locator(
            locator,
            f"board.repository_path_references[{index}]",
            errors,
            allow_null=False,
            allow_empty=False,
        )
        base = _base_locator(locator)
        if base is None:
            continue
        key = base.casefold()
        previous = casefold_paths.get(key)
        if previous is not None and previous != base:
            _error(
                errors,
                "board.repository_path_references",
                f"portable-path collision between {previous!r} and {base!r}",
            )
        casefold_paths[key] = base
    authors = {
        item.get("author")
        for item in items
        if isinstance(item, dict) and isinstance(item.get("author"), str)
    }
    works = {
        item.get("work")
        for item in items
        if isinstance(item, dict) and isinstance(item.get("work"), str)
    }
    series = {
        item.get("series")
        for item in items
        if isinstance(item, dict) and isinstance(item.get("series"), str)
    }
    corpora = {
        item.get("corpus")
        for item in items
        if isinstance(item, dict) and isinstance(item.get("corpus"), str)
    }
    languages = {
        language
        for item in items
        if isinstance(item, dict) and isinstance(item.get("languages"), list)
        for language in item.get("languages", [])
        if isinstance(language, str)
    }
    aggregate = {
        "items": len(items),
        "mirrors": len(mirrors),
        **counts,
        "unique_item_ids": len(set(item_ids)),
        "unique_mirror_ids": len(set(mirror_ids)),
        "required_maps": len(required_maps or []),
        "represented_required_maps": len(set(required_maps or []) & represented),
        "missing_required_maps": len(missing_maps),
        "queue_sources": len(QUEUE_SOURCES),
        "represented_queue_sources": len(set(QUEUE_SOURCES) & represented),
        "missing_queue_sources": len(missing_queue),
        "queue_snapshot_sources": len(queue_snapshot),
        "queue_snapshot_bytes": sum(
            entry.get("bytes", 0)
            for entry in queue_snapshot
            if type(entry.get("bytes")) is int
        ),
        "human_board_rows": len(items),
        "represented_human_board_items": len(set(item_ids)),
        "missing_human_board_items": 0,
        "unknown_human_board_ids": 0,
        "duplicate_human_board_ids": len(item_ids) - len(set(item_ids)),
        "human_index_rows": len(items),
        "human_index_authors": len(authors),
        "human_index_works": len(works),
        "human_index_series": len(series),
        "human_index_languages": len(languages),
        "human_index_corpora": len(corpora),
        "repository_path_checks": len(path_references),
        "tracked_repository_paths": len(path_references),
        "issue_labels": 4,
        "issue_label_templates": len(ISSUE_TEMPLATE_PATHS),
        "consumer_modes": len(CONSUMER_MODES),
        "claim_auditor_board_modes": len(CLAIM_AUDITOR_MODES["board"]),
        "claim_auditor_issue_modes": len(CLAIM_AUDITOR_MODES["issues"]),
        "continuous_validation_checks": (
            len(value.get("continuous_validation", {}).get("checks", []))
            if isinstance(value.get("continuous_validation"), dict)
            and isinstance(value.get("continuous_validation", {}).get("checks"), list)
            else 0
        ),
        "workflow_registry": len(workflow_ids),
        "workflow_tokens_used": len(used_workflows),
        "unreferenced_workflows": len(unused_workflows),
        "named_owner_rows": named_owner_rows,
        "unclaimed_owner_rows": unclaimed_owner_rows,
    }
    return aggregate


def _validate_exact_file_set(
    value: Any,
    label: str,
    errors: list[str],
    *,
    include_links: bool,
) -> list[dict[str, Any]]:
    if not isinstance(value, dict):
        _error(errors, label, "must be an object")
        return []
    entries = value.get("files_exact")
    if not isinstance(entries, list):
        _error(errors, f"{label}.files_exact", "must be an array")
        return []
    entry_fields = (
        ("path", "bytes", "sha256", "local_links", "external_links")
        if include_links
        else ("path", "bytes", "sha256")
    )
    valid_entries: list[dict[str, Any]] = []
    byte_sum = 0
    local_link_sum = 0
    external_link_sum = 0
    stream_parts: list[str] = []
    for index, entry in enumerate(entries):
        entry_label = f"{label}.files_exact[{index}]"
        if not _require_keys(entry, entry_fields, entry_label, errors, exact=True):
            continue
        assert isinstance(entry, dict)
        path = entry.get("path")
        size = entry.get("bytes")
        digest = entry.get("sha256")
        if not _valid_repo_locator(
            path, f"{entry_label}.path", errors, allow_null=False, allow_empty=False
        ):
            continue
        if type(size) is not int or size < 0:
            _error(errors, f"{entry_label}.bytes", "must be a nonnegative integer")
            continue
        if not isinstance(digest, str) or re.fullmatch(r"[0-9A-F]{64}", digest) is None:
            _error(errors, f"{entry_label}.sha256", "must be uppercase SHA-256")
            continue
        local_links = entry.get("local_links", 0)
        external_links = entry.get("external_links", 0)
        if include_links:
            if type(local_links) is not int or local_links < 0:
                _error(errors, f"{entry_label}.local_links", "must be a nonnegative integer")
                continue
            if type(external_links) is not int or external_links < 0:
                _error(errors, f"{entry_label}.external_links", "must be a nonnegative integer")
                continue
        byte_sum += size
        local_link_sum += local_links
        external_link_sum += external_links
        stream_parts.append(f"{path}\t{size}\t{digest}\n")
        valid_entries.append(entry)
    paths = [entry["path"] for entry in valid_entries]
    if len(paths) != len(set(paths)):
        _error(errors, f"{label}.files_exact", "contains duplicate paths")
    expected_scalars = {"files": len(entries), "bytes": byte_sum}
    if include_links:
        expected_scalars.update(
            {
                "local_links": local_link_sum,
                "external_links": external_link_sum,
                "missing_local_links": 0,
            }
        )
    for key, expected in expected_scalars.items():
        if value.get(key) != expected:
            _error(errors, f"{label}.{key}", f"must equal {expected}")
    stream = "".join(stream_parts).encode("utf-8")
    if value.get("canonical_stream_bytes") != len(stream):
        _error(errors, f"{label}.canonical_stream_bytes", "does not match the canonical stream")
    stream_digest = hashlib.sha256(stream).hexdigest().upper()
    if value.get("tree_sha256") != stream_digest:
        _error(errors, f"{label}.tree_sha256", "does not match the canonical stream")
    return valid_entries


def _validate_map_manifest(
    value: Any,
    board: dict[str, Any],
    pin: dict[str, Any],
    errors: list[str],
) -> None:
    label = "map manifest"
    if not isinstance(value, dict):
        _error(errors, label, "must be an object")
        return
    if value.get("schema") != "github-map-index/v6":
        _error(errors, f"{label}.schema", "has an unsupported value")
    if value.get("repository") != REPOSITORY_NAME:
        _error(errors, f"{label}.repository", "does not name the approved repository")
    _valid_date(value.get("observed_date"), f"{label}.observed_date", errors)
    _valid_commit(value.get("observed_commit"), f"{label}.observed_commit", errors)
    if value.get("observed_commit") != pin.get("map_observation_commit"):
        _error(errors, f"{label}.observed_commit", "does not match the pinned map observation")

    predecessor = value.get("predecessor")
    predecessor_entries: list[dict[str, Any]] = []
    if not isinstance(predecessor, dict):
        _error(errors, f"{label}.predecessor", "must be an object")
    else:
        _valid_repo_locator(
            predecessor.get("path"),
            f"{label}.predecessor.path",
            errors,
            allow_null=False,
            allow_empty=False,
        )
        _valid_commit(predecessor.get("commit"), f"{label}.predecessor.commit", errors)
        if type(predecessor.get("bytes")) is not int or predecessor.get("bytes") < 0:
            _error(errors, f"{label}.predecessor.bytes", "must be a nonnegative integer")
        if not isinstance(predecessor.get("sha256"), str) or re.fullmatch(
            r"[0-9A-F]{64}", predecessor.get("sha256", "")
        ) is None:
            _error(errors, f"{label}.predecessor.sha256", "must be uppercase SHA-256")
        predecessor_entries = _validate_exact_file_set(
            predecessor.get("map_set"),
            f"{label}.predecessor.map_set",
            errors,
            include_links=True,
        )

    current = value.get("current_map_set")
    current_entries = _validate_exact_file_set(
        current, f"{label}.current_map_set", errors, include_links=True
    )
    current_paths = [entry["path"] for entry in current_entries]
    required_maps = board.get("required_maps")
    if isinstance(required_maps, list) and current_paths != required_maps:
        _error(errors, f"{label}.current_map_set.files_exact", "does not exactly match board.required_maps")
    if predecessor_entries and [entry["path"] for entry in predecessor_entries] != current_paths:
        _error(errors, f"{label}.predecessor.map_set.files_exact", "must cover the same ordered map paths")

    predecessor_by_path = {entry["path"]: entry for entry in predecessor_entries}
    changed_entries = [
        entry
        for entry in current_entries
        if (
            entry["bytes"],
            entry["sha256"],
        )
        != (
            predecessor_by_path.get(entry["path"], {}).get("bytes"),
            predecessor_by_path.get(entry["path"], {}).get("sha256"),
        )
    ]
    if isinstance(current, dict):
        if current.get("changed_from_predecessor") != len(changed_entries):
            _error(errors, f"{label}.current_map_set.changed_from_predecessor", "does not match the exact diff")
        if current.get("unchanged_from_predecessor") != len(current_entries) - len(changed_entries):
            _error(errors, f"{label}.current_map_set.unchanged_from_predecessor", "does not match the exact diff")
    if value.get("changed_maps") != changed_entries:
        _error(errors, f"{label}.changed_maps", "does not match the exact predecessor/current diff")

    evidence = value.get("current_explicit_evidence_set")
    evidence_entries = _validate_exact_file_set(
        evidence,
        f"{label}.current_explicit_evidence_set",
        errors,
        include_links=False,
    )
    if isinstance(evidence, dict):
        evidence_by_path = {entry["path"]: entry for entry in evidence_entries}
        added = evidence.get("added")
        if not isinstance(added, list):
            _error(errors, f"{label}.current_explicit_evidence_set.added", "must be an array")
        else:
            for index, entry in enumerate(added):
                if not isinstance(entry, dict) or evidence_by_path.get(entry.get("path")) != entry:
                    _error(
                        errors,
                        f"{label}.current_explicit_evidence_set.added[{index}]",
                        "must exactly match a member of files_exact",
                    )

    checks = value.get("checks")
    if not isinstance(checks, dict):
        _error(errors, f"{label}.checks", "must be an object")
    else:
        required = {
            "predecessor_identity_replay": "1/1",
            "current_map_identity_replay": f"{len(current_entries)}/{len(current_entries)}",
            "unchanged_map_identity_replay": (
                f"{len(current_entries) - len(changed_entries)}/"
                f"{len(current_entries) - len(changed_entries)}"
            ),
            "changed_map_identity_replay": f"{len(changed_entries)}/{len(changed_entries)}",
            "current_explicit_evidence_identity_replay": (
                f"{len(evidence_entries)}/{len(evidence_entries)}"
            ),
            "local_link_replay": (
                f"{current.get('local_links', 0)}/{current.get('local_links', 0)}"
                if isinstance(current, dict)
                else "0/0"
            ),
            "missing_local_links": 0,
            "prohibited_targets": 0,
            "external_requests": 0,
            "producer_files_mutated": False,
            "compile_render_or_ocr_run": False,
            "zenodo_network_queried": False,
            "global_filesystem_search": False,
            "prohibited_or_revoked_roots_inspected": False,
        }
        for key, expected in required.items():
            if checks.get(key) != expected:
                _error(errors, f"{label}.checks.{key}", f"must equal {expected!r}")


def _pin_files_by_role(pin: dict[str, Any]) -> dict[str, dict[str, Any]]:
    files = pin.get("files")
    if not isinstance(files, list):
        return {}
    return {
        value.get("role"): value
        for value in files
        if isinstance(value, dict) and isinstance(value.get("role"), str)
    }


def _validate_check(
    value: Any,
    pin: dict[str, Any],
    board: dict[str, Any],
    aggregate: dict[str, int],
    identities: dict[str, dict[str, Any]],
    errors: list[str],
    *,
    production: bool,
) -> None:
    label = "validation check"
    required_keys = (
        "schema",
        "status",
        "errors",
        "observed_date",
        "input_mode",
        "worktree_base_commit",
        "worktree_dirty",
        "board",
        "schema_file",
        "map_manifest",
        "human_board",
        "human_index",
        "human_workflows",
        "issue_labels",
        "snapshot_policy",
        "consumer_helper",
        "consumer_modes",
        "consumer_regression",
        "claim_auditor",
        "claim_auditor_modes",
        "claim_regression",
        "continuous_validation",
        "ownership_policy",
        "queue_snapshot",
        "aggregate",
        "checks",
    )
    if not _require_keys(value, required_keys, label, errors, exact=True):
        return
    assert isinstance(value, dict)
    if value.get("schema") != "math-commons-adoption-check-v1":
        _error(errors, f"{label}.schema", "has an unsupported value")
    if value.get("status") != "PASS":
        _error(errors, f"{label}.status", "must be PASS")
    if value.get("errors") != []:
        _error(errors, f"{label}.errors", "must be an empty array")
    _valid_date(value.get("observed_date"), f"{label}.observed_date", errors)
    if value.get("input_mode") != VALIDATION_INPUT_MODE:
        _error(
            errors,
            f"{label}.input_mode",
            "must identify validation of the named worktree files",
        )
    _valid_commit(
        value.get("worktree_base_commit"),
        f"{label}.worktree_base_commit",
        errors,
    )
    if production and value.get("worktree_base_commit") != PRODUCTION_WORKTREE_BASE_COMMIT:
        _error(
            errors,
            f"{label}.worktree_base_commit",
            "does not match the compiled production predecessor",
        )
    if value.get("worktree_dirty") is not True:
        _error(
            errors,
            f"{label}.worktree_dirty",
            "must preserve the producer's explicit dirty-worktree qualification",
        )

    declarations = {
        "board": ("board", "schema", "math-commons-adoption-v1"),
        "schema_file": ("schema", "draft", "https://json-schema.org/draft/2020-12/schema"),
        "map_manifest": ("map_manifest", "required_maps", aggregate.get("required_maps")),
    }
    for key, (role, qualifier_key, qualifier_value) in declarations.items():
        declaration = value.get(key)
        identity = identities.get(role, {})
        if not isinstance(declaration, dict):
            _error(errors, f"{label}.{key}", "must be an object")
            continue
        if declaration.get("path") != identity.get("path"):
            _error(errors, f"{label}.{key}.path", "does not match the pinned file")
        if declaration.get("bytes") != identity.get("bytes"):
            _error(errors, f"{label}.{key}.bytes", "does not match the observed file")
        declared_hash = declaration.get("sha256")
        if not isinstance(declared_hash, str) or declared_hash.lower() != identity.get("sha256"):
            _error(errors, f"{label}.{key}.sha256", "does not match the observed file")
        if declaration.get(qualifier_key) != qualifier_value:
            _error(errors, f"{label}.{key}.{qualifier_key}", f"must equal {qualifier_value!r}")

    human_board = value.get("human_board")
    human_pin = pin.get("optional_human_projection")
    if not isinstance(human_board, dict):
        _error(errors, f"{label}.human_board", "must be an object")
    elif not isinstance(human_pin, dict):
        _error(errors, f"{label}.human_board", "has no optional projection identity in the pin")
    else:
        expected_human = {
            "path": human_pin.get("path"),
            "bytes": human_pin.get("bytes"),
            "sha256": str(human_pin.get("sha256", "")).upper(),
            "rows": pin.get("expected_aggregate", {}).get("human_board_rows"),
        }
        if human_board != expected_human:
            _error(errors, f"{label}.human_board", "does not match the pinned optional projection")

    human_index = value.get("human_index")
    expected_human_index = {
        "path": HUMAN_INDEX_IDENTITY[0],
        "bytes": HUMAN_INDEX_IDENTITY[1],
        "sha256": HUMAN_INDEX_IDENTITY[2].upper(),
        "rows": aggregate.get("human_index_rows"),
        "authors": aggregate.get("human_index_authors"),
        "works": aggregate.get("human_index_works"),
        "series": aggregate.get("human_index_series"),
        "languages": aggregate.get("human_index_languages"),
        "corpora": aggregate.get("human_index_corpora"),
    }
    if human_index != expected_human_index:
        _error(errors, f"{label}.human_index", "does not match the compiled index receipt")

    human_workflows = value.get("human_workflows")
    expected_human_workflows = {
        "path": HUMAN_WORKFLOWS_IDENTITY[0],
        "bytes": HUMAN_WORKFLOWS_IDENTITY[1],
        "sha256": HUMAN_WORKFLOWS_IDENTITY[2].upper(),
        "flows": aggregate.get("workflow_registry"),
        "headings": aggregate.get("workflow_registry"),
    }
    if human_workflows != expected_human_workflows:
        _error(
            errors,
            f"{label}.human_workflows",
            "does not match the compiled workflow-guide receipt",
        )

    issue_labels = value.get("issue_labels")
    expected_issue_labels = {
        "path": ISSUE_LABELS_IDENTITY[0],
        "bytes": ISSUE_LABELS_IDENTITY[1],
        "sha256": ISSUE_LABELS_IDENTITY[2].upper(),
        "labels": aggregate.get("issue_labels"),
        "templates": aggregate.get("issue_label_templates"),
    }
    if issue_labels != expected_issue_labels:
        _error(errors, f"{label}.issue_labels", "does not match the compiled label receipt")

    if value.get("consumer_helper") != CONSUMER_HELPER_PATH:
        _error(errors, f"{label}.consumer_helper", "does not match the compiled helper path")
    if board.get("consumer_helper") != value.get("consumer_helper"):
        _error(errors, "board.consumer_helper", "does not match the validation receipt")
    if value.get("consumer_modes") != list(CONSUMER_MODES):
        _error(errors, f"{label}.consumer_modes", "does not match the exact mode contract")
    if board.get("consumer_modes") != value.get("consumer_modes"):
        _error(errors, "board.consumer_modes", "does not match the validation receipt")
    if value.get("consumer_regression") != CONSUMER_REGRESSION_PATH:
        _error(
            errors,
            f"{label}.consumer_regression",
            "does not match the compiled offline regression path",
        )
    if board.get("consumer_regression") != value.get("consumer_regression"):
        _error(errors, "board.consumer_regression", "does not match the validation receipt")
    if value.get("claim_auditor") != CLAIM_AUDITOR_PATH:
        _error(errors, f"{label}.claim_auditor", "does not match the compiled claim auditor")
    if board.get("claim_auditor") != value.get("claim_auditor"):
        _error(errors, "board.claim_auditor", "does not match the validation receipt")
    if value.get("claim_auditor_modes") != CLAIM_AUDITOR_MODES:
        _error(
            errors,
            f"{label}.claim_auditor_modes",
            "does not match the exact board/issue auditor modes",
        )
    if board.get("claim_auditor_modes") != value.get("claim_auditor_modes"):
        _error(errors, "board.claim_auditor_modes", "does not match the validation receipt")
    if value.get("claim_regression") != CLAIM_REGRESSION_PATH:
        _error(
            errors,
            f"{label}.claim_regression",
            "does not match the compiled claim lifecycle regression path",
        )
    if board.get("claim_regression") != value.get("claim_regression"):
        _error(errors, "board.claim_regression", "does not match the validation receipt")
    if value.get("continuous_validation") != CONTINUOUS_VALIDATION:
        _error(
            errors,
            f"{label}.continuous_validation",
            "does not match the exact closed continuous-validation contract",
        )
    if board.get("continuous_validation") != value.get("continuous_validation"):
        _error(
            errors,
            "board.continuous_validation",
            "does not match the validation receipt",
        )
    if value.get("ownership_policy") != OWNERSHIP_POLICY:
        _error(errors, f"{label}.ownership_policy", "does not match the ownership contract")
    if board.get("ownership_policy") != value.get("ownership_policy"):
        _error(errors, "board.ownership_policy", "does not match the validation receipt")
    expected_queue_snapshot = [
        {"path": path, "bytes": size, "sha256": digest}
        for path, size, digest in QUEUE_SNAPSHOT
    ]
    if value.get("queue_snapshot") != expected_queue_snapshot:
        _error(errors, f"{label}.queue_snapshot", "does not match the exact queue identities")
    if board.get("queue_snapshot") != value.get("queue_snapshot"):
        _error(errors, "board.queue_snapshot", "does not match the validation receipt")

    expected_policy = {
        "stable_locator_ref": "main",
        "immutable_unit": "human_approved_exact_commit",
        "same_commit_paths": len(SNAPSHOT_PATHS),
        "required_checks": len(REQUIRED_CHECKS),
        "mixed_revisions_forbidden": True,
    }
    if value.get("snapshot_policy") != expected_policy:
        _error(errors, f"{label}.snapshot_policy", "does not match the board's snapshot policy")

    recorded_aggregate = value.get("aggregate")
    if _require_keys(
        recorded_aggregate,
        CHECK_AGGREGATE_FIELDS,
        f"{label}.aggregate",
        errors,
        exact=True,
    ):
        assert isinstance(recorded_aggregate, dict)
        for key, expected in aggregate.items():
            if recorded_aggregate.get(key) != expected:
                _error(errors, f"{label}.aggregate.{key}", f"must equal {expected}")
        expected_pin = pin.get("expected_aggregate")
        if isinstance(expected_pin, dict):
            for key, expected in expected_pin.items():
                if recorded_aggregate.get(key) != expected:
                    _error(errors, f"{label}.aggregate.{key}", f"does not match pin value {expected}")
    if value.get("checks") != CHECK_FLAGS:
        _error(errors, f"{label}.checks", "does not match the complete required check set")

    if board.get("snapshot_policy", {}).get("same_commit_paths") != list(SNAPSHOT_PATHS):
        _error(errors, "board.snapshot_policy.same_commit_paths", "is not the pinned four-file unit")


def validate_snapshot(
    snapshot_root: Path,
    *,
    pin: dict[str, Any] | None = None,
    production: bool = True,
) -> ValidatedSnapshot:
    """Validate a local snapshot against a code-reviewed pin.

    ``production=False`` exists for adversarial unit fixtures.  The public CLI
    never exposes that switch and always enforces the compiled production pin.
    """

    errors: list[str] = []
    if pin is None:
        pin = _read_pin()
    _validate_pin(pin, errors, production=production)
    if errors:
        raise SnapshotValidationError(errors)

    roles = _pin_files_by_role(pin)
    payloads: dict[str, bytes] = {}
    identities: dict[str, dict[str, Any]] = {}
    total_bytes = 0
    for role in PRODUCTION_FILE_IDENTITIES:
        identity = roles[role]
        payload = _snapshot_file_bytes(
            Path(snapshot_root),
            identity["path"],
            identity["bytes"],
            identity["sha256"],
            errors,
        )
        if payload is None:
            continue
        payloads[role] = payload
        total_bytes += len(payload)
        identities[role] = {
            "path": identity["path"],
            "bytes": len(payload),
            "sha256": hashlib.sha256(payload).hexdigest(),
        }
    if total_bytes > MAX_SNAPSHOT_TOTAL_BYTES:
        _error(errors, "snapshot", "exceeds the bounded total size limit")
    if errors:
        raise SnapshotValidationError(errors)

    documents: dict[str, Any] = {}
    for role, payload in payloads.items():
        try:
            documents[role] = _decode_json(payload, identities[role]["path"])
        except ValueError as exc:
            errors.append(str(exc))
    if errors:
        raise SnapshotValidationError(errors)

    board = documents["board"]
    schema_document = documents["schema"]
    check = documents["check"]
    map_manifest = documents["map_manifest"]
    _validate_schema_document(schema_document, errors)
    aggregate = _validate_board(board, pin, errors)
    if isinstance(board, dict):
        _validate_map_manifest(map_manifest, board, pin, errors)
        _validate_check(
            check,
            pin,
            board,
            aggregate,
            identities,
            errors,
            production=production,
        )
    else:
        _error(errors, "board", "must be an object")
    if errors:
        raise SnapshotValidationError(errors)
    assert isinstance(board, dict)
    assert isinstance(schema_document, dict)
    assert isinstance(check, dict)
    assert isinstance(map_manifest, dict)
    return ValidatedSnapshot(
        pin=pin,
        board=board,
        schema_document=schema_document,
        check=check,
        map_manifest=map_manifest,
        identities=identities,
        aggregate=aggregate,
    )


def select_items(
    snapshot: ValidatedSnapshot,
    *,
    lane_states: Sequence[str] | None,
    priorities: Sequence[str] | None,
    readiness: Sequence[str] | None,
    language: str | None,
    query: str | None,
    unowned: bool,
    limit: int,
) -> list[dict[str, Any]]:
    """Return inert, deterministically ranked candidate rows."""

    if limit < 1 or limit > MAX_ITEMS:
        raise ValueError(f"limit must be between 1 and {MAX_ITEMS}")
    selected_lanes = set(lane_states or ("ready_for_adoption",))
    selected_priorities = set(priorities or PRIORITIES)
    selected_readiness = set(readiness or READINESS)
    language_key = language.casefold() if language else None
    query_key = query.casefold() if query else None
    if query:
        query_errors: list[str] = []
        if len(query) > MAX_QUERY_CHARS:
            raise ValueError(f"query exceeds the {MAX_QUERY_CHARS}-character bound")
        _safe_text(query, "query", query_errors)
        if query_errors:
            raise ValueError(query_errors[0])

    items: list[dict[str, Any]] = []
    for item in snapshot.board["items"]:
        if item["lane_state"] not in selected_lanes:
            continue
        if item["priority"] not in selected_priorities:
            continue
        if item["readiness"] not in selected_readiness:
            continue
        if language_key and not any(value.casefold() == language_key for value in item["languages"]):
            continue
        if unowned and item["owner"] is not None:
            continue
        if query_key:
            haystack = "\n".join(
                str(item.get(field) or "")
                for field in ("id", "author", "work", "series", "corpus", "source_basis")
            ).casefold()
            if query_key not in haystack:
                continue
        items.append(item)

    priority_rank = {value: index for index, value in enumerate(PRIORITIES)}
    readiness_order = (
        "exact_cursor",
        "repair_ready",
        "review_ready",
        "continuation_ready",
        "expansion_ready",
        "intake_ready",
        "active",
        "source_discovery_first",
    )
    readiness_rank = {value: index for index, value in enumerate(readiness_order)}
    items.sort(
        key=lambda item: (
            priority_rank[item["priority"]],
            readiness_rank[item["readiness"]],
            item["author"].casefold(),
            item["id"],
        )
    )
    return items[:limit]


def _candidate_payload(snapshot: ValidatedSnapshot, items: list[dict[str, Any]]) -> dict[str, Any]:
    repository = snapshot.pin["repository"]
    commit = snapshot.pin["approved_snapshot_commit"]
    candidates: list[dict[str, Any]] = []
    for item in items:
        copied = dict(item)
        locator = item.get("archive_path")
        if isinstance(locator, str) and locator:
            copied["pinned_archive_url"] = f"{repository}/blob/{commit}/{locator}"
        else:
            copied["pinned_archive_url"] = None
        candidates.append(copied)
    return {
        "schema": "mathematics-commons-adoption-candidates-v1",
        "source": {
            "repository": repository,
            "approved_snapshot_commit": commit,
            "approved_snapshot_tree": snapshot.pin["approved_snapshot_tree"],
            "content_source_commit": snapshot.pin["content_source_commit"],
            "content_source_tree": snapshot.pin["content_source_tree"],
            "input_mode": snapshot.check["input_mode"],
            "worktree_base_commit": snapshot.check["worktree_base_commit"],
            "worktree_dirty": snapshot.check["worktree_dirty"],
            "evidence_closure_commit": snapshot.pin["evidence_closure_commit"],
            "evidence_base_commit": snapshot.pin["evidence_base_commit"],
            "map_observation_commit": snapshot.pin["map_observation_commit"],
            "discovery_ref_role": snapshot.pin["discovery_ref_role"],
            "contract_files": [dict(value) for value in snapshot.pin["files"]],
            "optional_human_projection": dict(
                snapshot.pin["optional_human_projection"]
            ),
            "optional_consumer_helper_identity": dict(
                snapshot.pin["optional_consumer_helper_identity"]
            ),
            "optional_consumer_regression_identity": dict(
                snapshot.pin["optional_consumer_regression_identity"]
            ),
            "optional_claim_auditor_identity": dict(
                snapshot.pin["optional_claim_auditor_identity"]
            ),
            "optional_claim_regression_identity": dict(
                snapshot.pin["optional_claim_regression_identity"]
            ),
            "optional_continuous_validation_identity": dict(
                snapshot.pin["optional_continuous_validation_identity"]
            ),
            "optional_code_identities_role": (
                "non_input_executable_provenance_only_not_a_trust_anchor"
            ),
            "sealed_public_receipts": [
                dict(value) for value in snapshot.pin["sealed_public_receipts"]
            ],
            "sealed_public_receipts_role": (
                "non_input_provenance_only_not_mathematical_source_or_rights_certification"
            ),
        },
        "validation": {
            "status": "PASS",
            "errors": [],
            "items": snapshot.aggregate["items"],
            "mirrors": snapshot.aggregate["mirrors"],
        },
        "authority": "coordination_metadata_only_not_mathematical_evidence",
        "interfaces": {
            "claim": snapshot.board["claim_interface"],
            "handback": snapshot.board["handback_interface"],
            "consumer_helper": snapshot.board["consumer_helper"],
            "consumer_modes": snapshot.board["consumer_modes"],
            "consumer_regression": snapshot.board["consumer_regression"],
            "claim_auditor": snapshot.board["claim_auditor"],
            "claim_auditor_modes": snapshot.board["claim_auditor_modes"],
            "claim_regression": snapshot.board["claim_regression"],
            "continuous_validation": snapshot.board["continuous_validation"],
        },
        "application_http_api_requests_performed": 0,
        "snapshot_storage_requirement": "caller_supplied_local_non_on_demand_private_directory",
        "live_packets_created": 0,
        "candidates": candidates,
    }


def _render_text(snapshot: ValidatedSnapshot, items: list[dict[str, Any]]) -> str:
    lines = [
        "PASS: pinned local interlanguage adoption snapshot",
        f"approved snapshot: {snapshot.pin['approved_snapshot_commit']}",
        f"content source: {snapshot.pin['content_source_commit']}",
        (
            f"producer validation input: {snapshot.check['input_mode']} on a "
            f"dirty worktree based at {snapshot.check['worktree_base_commit']} "
            "(receipt context; not snapshot authority)"
        ),
        (
            "board: "
            f"{snapshot.aggregate['items']} items "
            f"({snapshot.aggregate['current_work']} current, "
            f"{snapshot.aggregate['ready_for_adoption']} ready, "
            f"{snapshot.aggregate['future']} future), "
            f"{snapshot.aggregate['mirrors']} mirrors"
        ),
        "authority: coordination metadata only; the application fetched or executed no board URL or command",
        f"selected candidates: {len(items)}",
    ]
    for item in items:
        archive_locator = item.get("archive_path")
        pinned_archive = (
            f"{snapshot.pin['repository']}/blob/"
            f"{snapshot.pin['approved_snapshot_commit']}/{archive_locator}"
            if isinstance(archive_locator, str) and archive_locator
            else "not yet available; source discovery is prerequisite"
        )
        lines.extend(
            (
                "",
                (
                    f"- {item['id']} "
                    f"[{item['lane_state']}; {item['priority']}; {item['readiness']}]"
                ),
                f"  {item['author']} — {item['work']}",
                f"  owner: {item['owner'] or 'unowned'} ({item['owner_scope']})",
                f"  languages: {', '.join(item['languages'])}",
                f"  source basis: {item['source_basis']}",
                f"  prerequisites: {'; '.join(item['prerequisites'])}",
                f"  next: {item['next_cursor']}",
                f"  pinned archive: {pinned_archive}",
                f"  claim: {item['claim_url']}",
                f"  handback: {snapshot.board['handback_interface']}",
            )
        )
    return "\n".join(lines)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "snapshot_root",
        type=Path,
        help="extracted repository root containing the four pinned manifests",
    )
    parser.add_argument(
        "--lane-state",
        action="append",
        choices=LANE_STATES,
        help="lane to include; repeatable (default: ready_for_adoption)",
    )
    parser.add_argument("--all-lanes", action="store_true", help="include every lane")
    parser.add_argument("--priority", action="append", choices=PRIORITIES, help="priority to include")
    parser.add_argument("--readiness", action="append", choices=READINESS, help="readiness to include")
    parser.add_argument("--language", help="require one exact language tag, case-insensitively")
    parser.add_argument("--query", help="case-insensitive author/work/corpus search")
    parser.add_argument("--unowned", action="store_true", help="show only rows whose owner is null")
    parser.add_argument("--limit", type=int, default=20, help="maximum rows to emit (default: 20)")
    parser.add_argument("--json", action="store_true", help="emit a machine-readable candidate envelope")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if args.all_lanes and args.lane_state:
        print("ERROR: --all-lanes and --lane-state are mutually exclusive", file=sys.stderr)
        return 2
    if args.limit < 1 or args.limit > MAX_ITEMS:
        print(f"ERROR: limit must be between 1 and {MAX_ITEMS}", file=sys.stderr)
        return 2
    if args.query:
        query_errors: list[str] = []
        if len(args.query) > MAX_QUERY_CHARS:
            print(f"ERROR: query exceeds the {MAX_QUERY_CHARS}-character bound", file=sys.stderr)
            return 2
        _safe_text(args.query, "query", query_errors)
        if query_errors:
            print(f"ERROR: {query_errors[0]}", file=sys.stderr)
            return 2
    lane_states = list(LANE_STATES) if args.all_lanes else args.lane_state
    try:
        snapshot = validate_snapshot(args.snapshot_root)
        items = select_items(
            snapshot,
            lane_states=lane_states,
            priorities=args.priority,
            readiness=args.readiness,
            language=args.language,
            query=args.query,
            unowned=args.unowned,
            limit=args.limit,
        )
    except SnapshotValidationError as exc:
        for error in exc.errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(_candidate_payload(snapshot, items), indent=2, ensure_ascii=False))
    else:
        print(_render_text(snapshot, items))
    return 0


if __name__ == "__main__":
    sys.exit(main())
