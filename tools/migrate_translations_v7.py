#!/usr/bin/env python3
"""Build the current translation catalog from the reviewed snapshot."""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

from build_translate import replay_internal_manifest, write_internal_manifest


ROOT = Path(__file__).resolve().parents[1]
BASE = "025399ebc8d510413130afd002ba60718c3a2e64"
CATALOG_PATH = "catalog/translations.json"
WORKS_PATH = "kits/translate/WORKS.json"
OPENLOGIC_REPORT = "openlogic-indonesian-edition-unresolved"
RECORDED = "2026-08-21T00:00:00Z"
UPDATED = "2026-08-22T04:45:00Z"
WORK_ROLES = {"work", "series", "course", "source_project"}
GATE_NAMES = (
    "work_identity",
    "source_edition_identity",
    "immutable_source",
    "translation_permission",
    "component_rights",
    "editable_source",
    "baseline_build",
)
PLANNING_CANDIDATES = "planning-candidates-20260821"
PLANNING_ACTIVITY = "planning-activity-20260821"

HISTORICAL_PROGRESS = {
    "reported_active": "historical_report_active_at_recording",
    "reported_complete": "historical_report_complete_at_recording",
    "reported_planned": "historical_report_planned_at_recording",
}


def git_json(path: str) -> dict:
    raw = subprocess.run(
        ["git", "-C", str(ROOT), "show", f"{BASE}:{path}"],
        check=True,
        stdout=subprocess.PIPE,
    ).stdout
    value = json.loads(raw)
    if not isinstance(value, dict):
        raise ValueError(f"base JSON is not an object: {path}")
    return value


def write(path: Path, value: object) -> bytes:
    data = (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    path.write_bytes(data)
    return data


def evidence_ids(entry: dict) -> list[str]:
    result: list[str] = []
    refs = entry.get("evidence_refs")
    if not isinstance(refs, list):
        raise ValueError(f"malformed evidence refs: {entry.get('id')}")
    if any(str(value).startswith("09:") for value in refs):
        result.append(PLANNING_CANDIDATES)
    if any(str(value).startswith("10:") for value in refs):
        result.append(PLANNING_ACTIVITY)
    return result or [PLANNING_CANDIDATES]


def gate(state: str, basis: str, ids: list[str]) -> dict:
    return {"state": state, "basis": basis, "evidence_ids": ids}


def language(tag: str | None, name: str | None, locale: str | None = None) -> dict:
    return {
        "tag": tag,
        "name": name,
        "locale": locale,
        "script": None,
        "orthographic_standard": None,
    }


def unresolved_work(entry: dict) -> bool:
    return "unresolved" in str(entry.get("title") or "").lower()


def safe_tag(tag: str) -> str:
    return tag.lower().replace("_", "-")


def main() -> int:
    old = git_json(CATALOG_PATH)
    old_choices = git_json(WORKS_PATH)
    manifest_path = ROOT / "catalog" / "assets" / "openlogic.json"
    receipt_path = ROOT / "catalog" / "receipts" / "openlogic.json"
    readback_path = ROOT / "catalog" / "openlogic-rb.json"
    manifest_data = manifest_path.read_bytes()
    receipt_data = receipt_path.read_bytes()
    readback_data = readback_path.read_bytes()
    manifest = json.loads(manifest_data)
    receipt = json.loads(receipt_data)
    readback = json.loads(readback_data)
    if not all(isinstance(value, dict) for value in (manifest, receipt, readback)):
        raise ValueError("Open Logic release evidence roots must be objects")
    if manifest.get("job_id") != "openlogic-v1" or manifest.get("asset_count") != 1:
        raise ValueError("Open Logic asset manifest boundary differs")
    asset_row = manifest.get("assets", [None])[0]
    if not isinstance(asset_row, dict):
        raise ValueError("Open Logic asset row is malformed")
    asset_identity = [
        {
            "name": asset_row.get("name"),
            "bytes": asset_row.get("zip_bytes"),
            "sha256": asset_row.get("zip_sha256"),
        }
    ]
    public_assets = [
        {
            **asset_identity[0],
            "url": "https://github.com/KokunoYumeto/mathematics-commons-pilot/releases/download/translate-openlogic-v1/openlogic-v1.zip",
        }
    ]
    binding = receipt.get("packet_binding", {})
    observed_assets = [
        {
            "name": row.get("name"),
            "bytes": row.get("observed_bytes"),
            "sha256": row.get("observed_sha256"),
        }
        for row in readback.get("assets", [])
        if isinstance(row, dict)
    ]
    if (
        asset_identity
        != [
            {
                "name": "openlogic-v1.zip",
                "bytes": 1_921_531,
                "sha256": "C91EFD16C6DCF22DAEAFDBDC7F544A9E07C9B9C3BA04CE000BFCD933B52E9B8A",
            }
        ]
        or binding.get("packet_zip", {}).get("sha256") != asset_identity[0]["sha256"]
        or binding.get("asset_manifest", {}).get("sha256")
        != hashlib.sha256(manifest_data).hexdigest().upper()
        or readback.get("status") != "PASS"
        or readback.get("release", {}).get("tag") != "translate-openlogic-v1"
        or observed_assets != asset_identity
    ):
        raise ValueError("Open Logic admission/readback evidence differs")
    entries = old.get("entries")
    if not isinstance(entries, list) or len(entries) != 40:
        raise ValueError("reviewed v3 entry boundary differs")
    old_by_id = {row["id"]: row for row in entries if isinstance(row, dict)}
    if len(old_by_id) != len(entries) or OPENLOGIC_REPORT not in old_by_id:
        raise ValueError("reviewed v3 IDs differ")
    indonesian = old_by_id[OPENLOGIC_REPORT]
    if len(indonesian.get("known_editions", [])) != 1:
        raise ValueError("Open Logic Indonesian report shape differs")
    kept = [row for row in entries if row["id"] != OPENLOGIC_REPORT]
    kept_ids = {row["id"] for row in kept}
    roles = {row["id"]: row["catalog_role"] for row in kept}

    topics: list[dict] = []
    topic_lookup: dict[str, list[str]] = {item_id: [] for item_id in kept_ids}
    for old_topic in old_choices["topics"]:
        ordered: list[str] = []
        for item_id in old_topic["work_ids"]:
            normalized = "openlogic-core" if item_id == OPENLOGIC_REPORT else item_id
            if normalized not in kept_ids:
                raise ValueError(f"unknown topic item: {normalized}")
            if normalized not in ordered:
                ordered.append(normalized)
        for item_id in ordered:
            topic_lookup[item_id].append(old_topic["id"])
        topics.append(
            {
                "id": old_topic["id"],
                "title": old_topic["title"],
                "work_ids": [item_id for item_id in ordered if roles[item_id] in WORK_ROLES],
                "resource_ids": [item_id for item_id in ordered if roles[item_id] not in WORK_ROLES],
            }
        )
    if any(len(values) != 1 for values in topic_lookup.values()):
        raise ValueError("every current item must belong to exactly one topic")

    works: list[dict] = []
    resources: list[dict] = []
    source_editions: list[dict] = []
    translations: list[dict] = []
    translation_ids: dict[str, list[str]] = {item_id: [] for item_id in kept_ids}

    for entry in kept:
        item_id = entry["id"]
        ids = evidence_ids(entry)
        is_openlogic = item_id == "openlogic-core"
        is_work = entry["catalog_role"] in WORK_ROLES
        source_id = f"{item_id}-source"
        work_unresolved = unresolved_work(entry)
        locator_present = any(
            entry.get(key) is not None
            for key in ("source_url", "source_repo", "source_commit", "source_tree")
        )
        if is_openlogic:
            ids = ["openlogic-root", "openlogic-build"]
            gates = {
                "work_identity": gate("pass", "The public upstream work and creator identity are pinned.", ["openlogic-root"]),
                "source_edition_identity": gate("pass", "The exact root commit, tree, and 792 Git blobs were replayed.", ["openlogic-root"]),
                "immutable_source": gate("pass", "Every included blob, byte length, hash, and file mode is bound by the source receipt.", ["openlogic-root"]),
                "translation_permission": gate("pass", "CC BY 4.0 permits translated adaptations with attribution.", ["openlogic-root"]),
                "component_rights": gate("pass", "Included notices were censused; the unneeded wiki gitlink is pinned and excluded.", ["openlogic-root"]),
                "editable_source": gate("pass", "The exact source is editable LaTeX with its localization guide.", ["openlogic-root"]),
                "baseline_build": gate("pass", "Both root readers passed an independent no-Git cold build.", ["openlogic-build"]),
            }
            identity_state = "frozen"
            readiness = "runnable"
            source_language = language("en", "English")
            rights = {
                "state": "verified_translation_allowed",
                "work_license": {
                    "name": "CC BY 4.0",
                    "url": "https://creativecommons.org/licenses/by/4.0/",
                    "scope": "Open Logic Project authored content",
                },
                "derivative_translation_allowed": True,
                "distribution_class": "open_license",
                "distribution_note": "An open license is named for the source; follow its attribution and component notices.",
                "component_notices": [
                    {"path": "sty/bussproofs-extra.sty", "license": "LPPL notice preserved"},
                    {"path": "bib/natbib-oup.bst", "license": "LPPL notice preserved"},
                    {"path": "NOTICE.md", "license": "packet rights and component boundary"},
                ],
                "evidence_ids": ["openlogic-root"],
            }
            components = {
                "included": "All 792 root-tree blobs, including unmodified build assets and notices.",
                "excluded": "The pinned doc wiki gitlink is not a build input and is excluded because wiki-wide redistribution permission was not established.",
                "receipt": "catalog/receipts/openlogic.json",
            }
            source_label = "Complete pinned LaTeX source tree"
            next_action = "Download the public packet, verify its byte length and SHA-256, then select the exact target language and written standard."
            workflow_startability = "source_bound_packet"
            workflow_mode = "source_bound_packet"
            workflow_note = "A self-contained source packet is published with release, byte, SHA-256, and public-readback evidence."
        else:
            gates = {
                "work_identity": gate("unknown", "The public work identity has not been independently replayed." if not work_unresolved else "The exact work title or volume remains unresolved.", ids),
                "source_edition_identity": gate("unknown", "No independently replayed source edition is bound.", ids),
                "immutable_source": gate("unknown", "No immutable source archive or complete Git-tree replay is bound.", ids),
                "translation_permission": gate("fail" if entry.get("derivative_allowed") is False else "unknown", "The planning snapshot does not independently close translation rights.", ids),
                "component_rights": gate("unknown", "Component and media rights have not been independently censused.", ids),
                "editable_source": gate("unknown", "Editable-source closure has not been independently replayed.", ids),
                "baseline_build": gate("unknown", "No exact baseline build receipt is bound.", ids),
            }
            identity_state = "reported_locator" if locator_present else "unresolved"
            readiness = "reference_only" if entry["translation_readiness"] == "not_standalone" else ("identity_unresolved" if work_unresolved else "listed")
            source_language = language(None, None)
            rights = {
                "state": "reported_unverified",
                "work_license": {
                    "name": entry.get("license"),
                    "url": None,
                    "scope": "Reported planning metadata; not independently replayed",
                },
                "derivative_translation_allowed": entry.get("derivative_allowed"),
                "distribution_class": "terms_unclassified",
                "distribution_note": "The current catalog does not normalize the source's distribution terms.",
                "component_notices": [],
                "evidence_ids": ids,
            }
            components = {
                "included": None,
                "excluded": None,
                "receipt": None,
            }
            source_label = entry["source_format"]
            next_action = "Choose a target language, obtain the cited source edition, and return a cumulative translation checkpoint with the source and distribution note."
            if entry["catalog_role"] not in WORK_ROLES or readiness == "reference_only":
                workflow_startability = "reference_only"
                workflow_mode = "reference_only"
                workflow_note = "This row is a component, collection, or reference; use it to scope a separate work rather than as a standalone job."
            elif work_unresolved:
                workflow_startability = "starter_available"
                workflow_mode = "generic_starter"
                workflow_note = "The translation workflow can start with the generic starter; identify the exact work or edition and record the source before the first bounded translation unit."
            else:
                workflow_startability = "starter_available"
                workflow_mode = "generic_starter"
                workflow_note = "The translation workflow can start with the generic starter; supply or obtain the exact source and record its distribution note before the first bounded translation unit."

        item = {
            "id": item_id,
            "kind": entry["catalog_role"],
            "title": "Open Logic Text" if is_openlogic else entry["title"],
            "creators": ["The Open Logic Project"] if is_openlogic else entry["authors"],
            "creators_note": None if is_openlogic else entry["authors_note"],
            "topic_ids": topic_lookup[item_id],
            "curricular_role": entry["curricular_role"],
            "pages": 1013 if is_openlogic else entry["pages"],
            "page_note": "At this commit, the complete reader cold-built to 1,013 pages and the debug reader to 962 pages." if is_openlogic else entry["page_note"],
            "coverage_note": "A public Portuguese repository is pinned below. A separate Indonesian edition is retained only as an unresolved historical report. Coverage in other languages is unknown, not absent." if is_openlogic else entry["coverage_note"],
            "why_listed": "The exact CC BY 4.0 LaTeX source is frozen, buildable, and suitable for independent target-language translation." if is_openlogic else entry["why_listed"],
            "source_edition_ids": [source_id],
            "translation_edition_ids": [],
            "job_ids": ["openlogic-v1"] if is_openlogic else [],
            "evidence_ids": ids,
        }
        (works if is_work else resources).append(item)

        source_editions.append(
            {
                "id": source_id,
                "item_id": item_id,
                "item_type": "work" if is_work else "resource",
                "identity_state": identity_state,
                "label": source_label,
                "source_language": source_language,
                "locator": {
                    "url": entry["source_url"],
                    "repository": entry["source_repo"],
                    "commit": entry["source_commit"],
                    "tree": entry["source_tree"],
                    "archive": None,
                },
                "rights": rights,
                "components": components,
                "evidence_checks": gates,
                "readiness": readiness,
                "workflow_startability": workflow_startability,
                "workflow_mode": workflow_mode,
                "workflow_note": workflow_note,
                "next_action": next_action,
                "evidence_ids": ids,
            }
        )

        for known in entry["known_editions"]:
            tag = known["language_tag"]
            edition_id = f"{item_id}-{safe_tag(tag)}-reported-20260821"
            if edition_id in {row["id"] for row in translations}:
                raise ValueError(f"translation identity collision: {edition_id}")
            translation_ids[item_id].append(edition_id)
            translations.append(
                {
                    "id": edition_id,
                    "work_id": item_id,
                    "source_edition_id": None,
                    "identity_state": "unverified_report",
                    "target_language": language(tag, known["language_name"]),
                    "progress_state": HISTORICAL_PROGRESS[known["state"]],
                    "review_state": "unknown",
                    "scope_note": "Unverified report recorded 2026-08-21; date, public edition identity, exact scope, and review state are unavailable.",
                    "owner": None,
                    "overlap": {"mode": "unknown", "related_edition_ids": [], "purpose": None},
                    "evidence": {
                        "status": "non_public_historical_report",
                        "observed_at": None,
                        "recorded_at": RECORDED,
                        "public_url": None,
                        "commit": None,
                        "tree": None,
                        "evidence_ids": [PLANNING_ACTIVITY],
                    },
                }
            )

    indonesian_id = "openlogic-id-reported-20260821"
    translation_ids["openlogic-core"].append(indonesian_id)
    translations.append(
        {
            "id": indonesian_id,
            "work_id": "openlogic-core",
            "source_edition_id": None,
            "identity_state": "unverified_report",
            "target_language": language("id", "Indonesian"),
            "progress_state": "historical_report_complete_at_recording",
            "review_state": "unknown",
            "scope_note": "Unverified report recorded 2026-08-21; public edition identity, exact scope, and review state are unavailable.",
            "owner": None,
            "overlap": {"mode": "unknown", "related_edition_ids": [], "purpose": None},
            "evidence": {
                "status": "non_public_historical_report",
                "observed_at": None,
                "recorded_at": RECORDED,
                "public_url": None,
                "commit": None,
                "tree": None,
                "evidence_ids": [PLANNING_ACTIVITY],
            },
        }
    )
    portuguese_id = "openlogic-pt-openlogicpt"
    translation_ids["openlogic-core"].append(portuguese_id)
    translations.append(
        {
            "id": portuguese_id,
            "work_id": "openlogic-core",
            "source_edition_id": None,
            "identity_state": "public_repository_verified",
            "target_language": language("pt", "Portuguese"),
            "progress_state": "repository_available",
            "review_state": "not_independently_assessed",
            "scope_note": "The pinned repository describes a Portuguese translation. Whole-work completion and its exact source-base relationship were not independently established.",
            "owner": "Pedro Lima",
            "overlap": {"mode": "none_known", "related_edition_ids": [], "purpose": "Reuse or contribute to this public lineage where appropriate; declare any independent parallel edition."},
            "evidence": {
                "status": "public_repository_identity_verified",
                "observed_at": UPDATED,
                "recorded_at": UPDATED,
                "public_url": "https://github.com/OpenLogicProject/OpenLogic-pt",
                "commit": "51c227190f56bae45d19a85747fc031de430bd3c",
                "tree": "5083d9763a3b6de3718e8400950f43e1eb4bd955",
                "evidence_ids": ["openlogic-pt"],
            },
        }
    )

    for item in [*works, *resources]:
        item["translation_edition_ids"] = translation_ids[item["id"]]

    jobs = [
        {
            "id": "openlogic-v1",
            "work_id": "openlogic-core",
            "source_edition_id": "openlogic-core-source",
            "title": "Translate the Open Logic Text",
            "target_mode": "contributor_selects",
            "state": "runnable",
            "release_tag": "translate-openlogic-v1",
            "release_url": "https://github.com/KokunoYumeto/mathematics-commons-pilot/releases/tag/translate-openlogic-v1",
            "assets": public_assets,
            "asset_manifest": "catalog/assets/openlogic.json",
            "source_receipt": "catalog/receipts/openlogic.json",
            "public_readback": {
                "receipt": "catalog/openlogic-rb.json",
                "observed_date": readback["observed_date"],
                "assets": public_assets,
            },
            "start_files": {"local": "LOCAL.md", "web": "WEB.md"},
            "evidence_ids": ["openlogic-root", "openlogic-build"],
        }
    ]

    catalog = {
        "schema": "math-commons-translation-catalog/v8",
        "updated_at": UPDATED,
        "scope": {
            "non_exhaustive": True,
            "other_open_works_welcome": True,
            "description": "A non-exclusive directory of mathematical works and resources for translation outside maintained project lanes. Each row gives a readable work identity, language evidence, distribution class, and practical next action.",
            "coverage_rule": "A non-reference work may be workflow-startable without a self-contained public packet. Readiness reports packet/evidence state; jobs[].state=runnable reports a packaged release with public readback. Unknown coverage means unknown, not absence.",
        },
        "language_priority": old["language_priority"],
        "distribution_legend": {
            "open_license": "Open license named; follow the stated terms.",
            "noncommercial_only": "Non-commercial distribution only; not for commercial distribution.",
            "mixed_components": "Mixed or incomplete component terms; use the named notices.",
            "terms_unclassified": "Distribution terms are not normalized in the current row.",
            "no_derivatives": "No derivative edition is claimed; reference use only.",
            "reference_only": "Reference or component entry; not a standalone translation job.",
        },
        "separate_archive": old_choices["catalogs"]["separate_manuscript_archive"],
        "evidence": [
            {
                "id": PLANNING_CANDIDATES,
                "kind": "historical_nonpublic_snapshot",
                "recorded_at": RECORDED,
                "artifact": {"sha256": old["evidence"]["sources"][0]["sha256"].upper(), "availability": "not_public"},
                "note": "Historical candidate-selection evidence. It does not establish a current public source or activity state.",
            },
            {
                "id": PLANNING_ACTIVITY,
                "kind": "historical_nonpublic_snapshot",
                "recorded_at": RECORDED,
                "artifact": {"sha256": old["evidence"]["sources"][1]["sha256"].upper(), "availability": "not_public"},
                "note": "Historical activity reports. They are preserved as unverified reports and never derive current activity.",
            },
            {
                "id": "openlogic-root",
                "kind": "public_git_replay",
                "observed_at": UPDATED,
                "url": "https://github.com/OpenLogicProject/OpenLogic/tree/1e960beff9ed7835bf3e3f1335e21af3439cd107",
                "repository": "https://github.com/OpenLogicProject/OpenLogic",
                "commit": "1e960beff9ed7835bf3e3f1335e21af3439cd107",
                "tree": "45cad6b3bf0dd96985a7b3d1dc5c343984b0e1c8",
                "note": "Exact root Git-object inventory, rights boundary, component census, and packet-source receipt.",
            },
            {
                "id": "openlogic-build",
                "kind": "same_commit_receipt",
                "observed_at": UPDATED,
                "path": "catalog/receipts/openlogic.json",
                "bytes": len(receipt_data),
                "sha256": hashlib.sha256(receipt_data).hexdigest().upper(),
                "note": "Final cold-build and packet-admission receipt.",
            },
            {
                "id": "openlogic-pt",
                "kind": "public_git_replay",
                "observed_at": UPDATED,
                "url": "https://github.com/OpenLogicProject/OpenLogic-pt/tree/51c227190f56bae45d19a85747fc031de430bd3c",
                "repository": "https://github.com/OpenLogicProject/OpenLogic-pt",
                "commit": "51c227190f56bae45d19a85747fc031de430bd3c",
                "tree": "5083d9763a3b6de3718e8400950f43e1eb4bd955",
                "note": "Public Portuguese repository identity and README claim boundary; not a whole-edition QA certification or source-lineage proof.",
            },
        ],
        "page_accounting": {
            "aggregate_pages": None,
            "rule": "Pages are recorded only for independently identified source editions; no aggregate is claimed.",
        },
        "topics": topics,
        "works": works,
        "resources": resources,
        "source_editions": source_editions,
        "translation_editions": translations,
        "jobs": jobs,
        "exclusions": old["exclusions"],
    }
    catalog_data = write(ROOT / CATALOG_PATH, catalog)

    choices = {
        "schema": "math-commons-translation-choices/v8",
        "updated_at": UPDATED,
        "rule": "Choose a topic, then a non-reference work and target language. A work with workflow_startability=starter_available or source_bound_packet can be started with the generic kit; use the separately published packet when source_bound_packet is available. A packaged job with public readback is represented separately by jobs[].state=runnable. Each row states its distribution class and license note; unknown coverage never means absence.",
        "catalog": {"path": CATALOG_PATH, "bytes": len(catalog_data), "sha256": hashlib.sha256(catalog_data).hexdigest().upper()},
        "separate_archive": catalog["separate_archive"],
        "topics": topics,
        "works": [
            {"id": row["id"], "title": row["title"], "topic_ids": row["topic_ids"], "source_edition_ids": row["source_edition_ids"], "translation_edition_ids": row["translation_edition_ids"], "job_ids": row["job_ids"]}
            for row in works
        ],
        "resources": [
            {"id": row["id"], "title": row["title"], "kind": row["kind"], "topic_ids": row["topic_ids"], "source_edition_ids": row["source_edition_ids"]}
            for row in resources
        ],
        "source_editions": [
            {"id": row["id"], "item_id": row["item_id"], "item_type": row["item_type"], "readiness": row["readiness"], "workflow_startability": row["workflow_startability"], "workflow_mode": row["workflow_mode"], "workflow_note": row["workflow_note"], "distribution_class": row["rights"]["distribution_class"], "distribution_note": row["rights"]["distribution_note"]}
            for row in source_editions
        ],
        "translation_editions": [
            {"id": row["id"], "work_id": row["work_id"], "language": row["target_language"], "identity_state": row["identity_state"], "progress_state": row["progress_state"], "review_state": row["review_state"]}
            for row in translations
        ],
        "jobs": jobs,
        "language_priority": old["language_priority"],
        "distribution_legend": {
            "open_license": "Open license named; follow the stated terms.",
            "noncommercial_only": "Non-commercial distribution only; not for commercial distribution.",
            "mixed_components": "Mixed or incomplete component terms; use the named notices.",
            "terms_unclassified": "Distribution terms are not normalized in the current row.",
            "no_derivatives": "No derivative edition is claimed; reference use only.",
            "reference_only": "Reference or component entry; not a standalone translation job."
        },
    }
    write(ROOT / WORKS_PATH, choices)
    write_internal_manifest(ROOT / "kits" / "translate")
    replay_internal_manifest(ROOT / "kits" / "translate")
    print(
        json.dumps(
            {
                "works": len(works),
                "resources": len(resources),
                "source_editions": len(source_editions),
                "translation_editions": len(translations),
                "jobs": len(jobs),
                "topics": len(topics),
            },
            separators=(",", ":"),
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
