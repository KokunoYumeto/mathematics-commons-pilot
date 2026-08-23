#!/usr/bin/env python3
"""Project exact public Indonesian reader receipts into the live catalog.

The generic translation-starter v7 release remains an immutable snapshot.  This
script starts from the checked-out current catalog and applies the later
Figshare readback as a deterministic, additive catalog update.  ``INPUT_PATH``
and ``OUTPUT_PATH`` are separate so a replay can write to a temporary path
without accidentally using that path as its input.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from copy import deepcopy
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
# v8 is maintained from the checked-out live catalog.  The v7 release remains
# immutable history; this updater is intentionally idempotent on the v8 file.
BASE_COMMIT = None
EVIDENCE_ID = "figshare-id-readers-20260822"
RECEIPT_PATH = ROOT / "catalog" / "receipts" / "id-readers.json"
INPUT_PATH = ROOT / "catalog" / "translations.json"
OUTPUT_PATH = ROOT / "catalog" / "translations.json"
COMPUTING_WORK_ID = "mathematical-computing-reproducible-experiments"
DIONNE_WORK_ID = "dionne-partial-differential-equations"
NEW_WORK_IDS = {COMPUTING_WORK_ID, DIONNE_WORK_ID}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def load_json(data: bytes, label: str) -> dict[str, Any]:
    if data.startswith(b"\xef\xbb\xbf") or b"\r" in data:
        raise ValueError(f"{label} must be UTF-8 LF without BOM")
    value = json.loads(data.decode("utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{label} root is not an object")
    return value


def tagged_catalog() -> dict[str, Any]:
    if BASE_COMMIT is None:
        return load_json(INPUT_PATH.read_bytes(), "current translation catalog")
    result = subprocess.run(
        ["git", "show", f"{BASE_COMMIT}:catalog/translations.json"],
        cwd=ROOT,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    data = result.stdout
    if len(data) != 187_603 or sha256(data) != "ABFD27FF21D57FBB7389C876162BD73A7950D424D130846B352BD8D1B1559744":
        raise ValueError("translation-starter v7 catalog identity drift")
    return load_json(data, "translation-starter v7 catalog")


def unknown_gate(basis: str) -> dict[str, Any]:
    return {
        "state": "unknown",
        "basis": basis,
        "evidence_ids": [EVIDENCE_ID],
    }


def computing_work(reader_id: str) -> dict[str, Any]:
    return {
        "id": COMPUTING_WORK_ID,
        "kind": "work",
        "title": "Mathematical Computing and Reproducible Experiments",
        "creators": None,
        "creators_note": "Not established by the public-reader receipt.",
        "topic_ids": ["computing"],
        "curricular_role": "mathematical computing and reproducible experiments",
        "pages": None,
        "page_note": "Page count and whole-work scope have not been independently assessed.",
        "coverage_note": (
            "A public Indonesian reader PDF is recorded below with exact DOI, "
            "filename, byte length, and SHA-256. Its whole-work coverage, source "
            "lineage, and independent translation QA have not been established. "
            "Coverage in other languages is unknown, not absent."
        ),
        "why_listed": (
            "A public Indonesian reader is available; its source identity, license "
            "note, components, and scope are recorded below."
        ),
        "source_edition_ids": [f"{COMPUTING_WORK_ID}-source"],
        "translation_edition_ids": [reader_id],
        "job_ids": [],
        "evidence_ids": [EVIDENCE_ID],
    }


def dionne_work(reader_id: str) -> dict[str, Any]:
    return {
        "id": DIONNE_WORK_ID,
        "kind": "work",
        "title": "Partial Differential Equations — Dionne Unit 1",
        "creators": ["Dionne"],
        "creators_note": (
            "The surname and unit label are supported by the public filename; "
            "the full bibliographic identity remains unresolved."
        ),
        "topic_ids": ["analysis"],
        "curricular_role": "partial differential equations",
        "pages": None,
        "page_note": "Page count and exact unit scope have not been independently assessed.",
        "coverage_note": (
            "A public Indonesian Unit 1 reader PDF is recorded below with exact DOI, "
            "filename, byte length, and SHA-256. Its exact source identity, unit "
            "coverage, and independent translation QA have not been established. "
            "It is separate from the Victor Ivrii work listed in this catalog."
        ),
        "why_listed": (
            "A public Indonesian Unit 1 reader is available; its current identity, "
            "license note, components, and scope are recorded below."
        ),
        "source_edition_ids": [f"{DIONNE_WORK_ID}-source"],
        "translation_edition_ids": [reader_id],
        "job_ids": [],
        "evidence_ids": [EVIDENCE_ID],
    }


def new_source(work_id: str) -> dict[str, Any]:
    return {
        "id": f"{work_id}-source",
        "item_id": work_id,
        "item_type": "work",
        "identity_state": "unresolved",
        "label": "source identity not established by the public-reader receipt",
        "source_language": {
            "tag": None,
            "name": None,
            "locale": None,
            "script": None,
            "orthographic_standard": None,
        },
        "locator": {
            "url": None,
            "repository": None,
            "commit": None,
            "tree": None,
            "archive": None,
        },
        "rights": {
            "state": "reported_unverified",
            "work_license": {
                "name": None,
                "url": None,
                "scope": (
                    "The public-reader receipt does not establish the source work "
                    "or its translation license."
                ),
            },
            "derivative_translation_allowed": None,
            "distribution_class": "terms_unclassified",
            "distribution_note": "The public-reader receipt does not establish a normalized source license note.",
            "component_notices": [],
            "evidence_ids": [EVIDENCE_ID],
        },
        "components": {"included": None, "excluded": None, "receipt": None},
        "evidence_checks": {
            "work_identity": unknown_gate(
                "The public reader establishes a titled PDF, not the exact source work."
            ),
            "source_edition_identity": unknown_gate(
                "No exact source edition is bound by the public-reader receipt."
            ),
            "immutable_source": unknown_gate(
                "No immutable source archive or complete Git tree is bound."
            ),
            "translation_permission": unknown_gate(
            "The current catalog has no normalized license note for this source. Choose a source with published terms or add the exact terms when preparing a packet."
            ),
            "component_rights": unknown_gate(
                "Source components and media rights have not been censused."
            ),
            "editable_source": unknown_gate(
                "No editable source has been identified and replayed."
            ),
            "baseline_build": unknown_gate(
                "No exact source baseline-build receipt is bound."
            ),
        },
        "readiness": "identity_unresolved",
        "next_action": (
            "Choose a target language and identify the exact source edition before returning the first translation checkpoint."
        ),
        "evidence_ids": [EVIDENCE_ID],
    }


def public_edition(
    reader: dict[str, Any], related_historical_ids: list[str], observed_at: str, collection_doi: str
) -> dict[str, Any]:
    reader_id = str(reader["id"])
    if related_historical_ids:
        overlap = {
            "mode": "declared_parallel",
            "related_edition_ids": related_historical_ids,
            "purpose": (
                "The public reader and older historical report are retained "
                "separately because their exact byte lineage and scope relationship "
                "have not been established."
            ),
        }
    else:
        overlap = {
            "mode": "none_known",
            "related_edition_ids": [],
            "purpose": None,
        }
    return {
        "id": reader_id,
        "work_id": reader["work_id"],
        "source_edition_id": None,
        "identity_state": "public_edition_verified",
        "target_language": {
            "tag": "id",
            "name": "Indonesian",
            "locale": None,
            "script": None,
            "orthographic_standard": None,
        },
        "progress_state": "public_reader_available_scope_unassessed",
        "review_state": "not_independently_assessed",
        "scope_note": (
            "The exact public PDF bytes were anonymously verified. Whole-work "
            "coverage, source lineage, and independent translation QA remain unassessed."
        ),
        "owner": None,
        "overlap": overlap,
        "evidence": {
            "status": "public_bytes_verified",
            "observed_at": observed_at,
            "recorded_at": observed_at,
            "public_url": f"https://doi.org/{reader['doi']}",
            "commit": None,
            "tree": None,
            "doi": reader["doi"],
            "file": reader["file"],
            "bytes": reader["bytes"],
            "sha256": reader["sha256"],
            "download_url": reader["download_url"],
            "collection_doi": collection_doi,
            "receipt_path": "catalog/receipts/id-readers.json",
            "evidence_ids": [EVIDENCE_ID],
        },
    }


def main() -> int:
    catalog = tagged_catalog()
    prior_work_templates = {
        str(row["id"]): deepcopy(row)
        for row in catalog.get("works", [])
        if isinstance(row, dict) and isinstance(row.get("id"), str)
        and row.get("id") in NEW_WORK_IDS
    }
    prior_source_templates = {
        str(row["id"]): deepcopy(row)
        for row in catalog.get("source_editions", [])
        if isinstance(row, dict) and isinstance(row.get("id"), str)
        and row.get("item_id") in NEW_WORK_IDS
    }
    receipt_data = RECEIPT_PATH.read_bytes()
    receipt = load_json(receipt_data, "Indonesian reader receipt")
    readers = receipt.get("readers")
    collection = receipt.get("collection")
    if not isinstance(readers, list) or not isinstance(collection, dict):
        raise ValueError("Indonesian reader receipt structure is malformed")
    if (
        receipt.get("schema") != "math-commons-reader-receipt/v1"
        or len(readers) != 9
        or len({row.get("id") for row in readers if isinstance(row, dict)}) != 9
        or collection.get("reader_count") != 9
        or collection.get("reader_bytes")
        != sum(int(row.get("bytes", 0)) for row in readers if isinstance(row, dict))
    ):
        raise ValueError("Indonesian reader receipt boundary mismatch")

    observed_at = str(receipt["observed_at"])
    collection_doi = str(collection["doi"])
    reader_ids = {
        str(row["id"])
        for row in readers
        if isinstance(row, dict) and isinstance(row.get("id"), str)
    }
    # Remove a prior v8 projection before rebuilding it, so replay produces
    # one byte-identical catalog rather than accumulating duplicate rows.
    catalog["evidence"] = [
        row for row in catalog.get("evidence", [])
        if isinstance(row, dict) and row.get("id") != EVIDENCE_ID
    ]
    catalog["works"] = [
        row for row in catalog.get("works", [])
        if isinstance(row, dict) and row.get("id") not in NEW_WORK_IDS
    ]
    catalog["source_editions"] = [
        row for row in catalog.get("source_editions", [])
        if isinstance(row, dict) and row.get("item_id") not in NEW_WORK_IDS
    ]
    catalog["translation_editions"] = [
        row for row in catalog.get("translation_editions", [])
        if isinstance(row, dict) and row.get("id") not in reader_ids
    ]
    for topic in catalog.get("topics", []):
        if isinstance(topic, dict):
            topic["work_ids"] = [
                value for value in topic.get("work_ids", []) if value not in NEW_WORK_IDS
            ]
    for work in catalog.get("works", []):
        if isinstance(work, dict):
            work["translation_edition_ids"] = [
                value for value in work.get("translation_edition_ids", []) if value not in reader_ids
            ]
            work["evidence_ids"] = [
                value for value in work.get("evidence_ids", []) if value != EVIDENCE_ID
            ]
    # Preserve the current catalog timestamp when replaying an already-current
    # v8 catalog; a first projection from an older catalog uses the receipt date.
    if catalog.get("schema") != "math-commons-translation-catalog/v8":
        catalog["updated_at"] = observed_at
    catalog["evidence"].append(
        {
            "id": EVIDENCE_ID,
            "kind": "same_commit_receipt",
            "observed_at": observed_at,
            "path": "catalog/receipts/id-readers.json",
            "bytes": len(receipt_data),
            "sha256": sha256(receipt_data),
            "note": (
                "Anonymous Figshare collection and nine-reader PDF length/SHA-256 "
                "readback; this does not establish whole-work coverage, source "
                "lineage, or translation QA."
            ),
        }
    )

    works = {row["id"]: row for row in catalog["works"]}
    works["dmoi4"]["why_listed"] = (
        "A historical report describes an Indonesian edition as complete at its "
        "recording date; verify the exact source and public edition before further work."
    )
    computing_reader = next(
        row
        for row in readers
        if isinstance(row, dict) and row["work_id"] == COMPUTING_WORK_ID
    )
    dionne_reader = next(
        row
        for row in readers
        if isinstance(row, dict) and row["work_id"] == DIONNE_WORK_ID
    )
    computing_template = prior_work_templates.get(
        COMPUTING_WORK_ID, computing_work(str(computing_reader["id"]))
    )
    computing_template["translation_edition_ids"] = []
    computing_template["evidence_ids"] = []
    catalog["works"].append(computing_template)
    works[COMPUTING_WORK_ID] = catalog["works"][-1]
    dionne_template = prior_work_templates.get(
        DIONNE_WORK_ID, dionne_work(str(dionne_reader["id"]))
    )
    dionne_template["translation_edition_ids"] = []
    dionne_template["evidence_ids"] = []
    catalog["works"].append(dionne_template)
    works[DIONNE_WORK_ID] = catalog["works"][-1]
    computing_topic = next(row for row in catalog["topics"] if row["id"] == "computing")
    computing_topic["work_ids"].append(COMPUTING_WORK_ID)
    analysis_topic = next(row for row in catalog["topics"] if row["id"] == "analysis")
    analysis_topic["work_ids"].append(DIONNE_WORK_ID)
    catalog["source_editions"].append(
        prior_source_templates.get(
            f"{COMPUTING_WORK_ID}-source", new_source(COMPUTING_WORK_ID)
        )
    )
    catalog["source_editions"].append(
        prior_source_templates.get(
            f"{DIONNE_WORK_ID}-source", new_source(DIONNE_WORK_ID)
        )
    )

    coverage_note = (
        "A public Indonesian reader PDF is recorded below with exact DOI, "
        "filename, byte length, and SHA-256. Its whole-work coverage, source "
        "lineage, and independent translation QA have not been established. "
        "Coverage in other languages is unknown, not absent."
    )
    historical_by_work: dict[str, list[dict[str, Any]]] = {}
    for edition in catalog["translation_editions"]:
        if edition.get("identity_state") == "unverified_report":
            historical_by_work.setdefault(str(edition["work_id"]), []).append(edition)

    for reader in readers:
        if not isinstance(reader, dict):
            raise ValueError("Indonesian reader row is malformed")
        work_id = str(reader["work_id"])
        reader_id = str(reader["id"])
        work = works.get(work_id)
        if work is None:
            raise ValueError(f"unknown reader work: {work_id}")
        work["translation_edition_ids"].append(reader_id)
        if work_id != DIONNE_WORK_ID:
            work["coverage_note"] = coverage_note
        if EVIDENCE_ID not in work["evidence_ids"]:
            work["evidence_ids"].append(EVIDENCE_ID)

        historical_rows = historical_by_work.get(work_id, [])
        historical_ids = [str(row["id"]) for row in historical_rows]
        for historical in historical_rows:
            historical["overlap"] = {
                "mode": "declared_parallel",
                "related_edition_ids": [reader_id],
                "purpose": (
                    "The older report and public reader are retained separately "
                    "because their exact byte lineage and scope relationship have "
                    "not been established."
                ),
            }
        catalog["translation_editions"].append(
            public_edition(reader, historical_ids, observed_at, collection_doi)
        )

    output = (json.dumps(catalog, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    OUTPUT_PATH.write_bytes(output)
    print(
        "PASS: "
        f"{len(catalog['works'])} works, "
        f"{len(catalog['source_editions'])} source editions, "
        f"{len(catalog['translation_editions'])} translation editions; "
        f"{len(output)} bytes / {sha256(output)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
