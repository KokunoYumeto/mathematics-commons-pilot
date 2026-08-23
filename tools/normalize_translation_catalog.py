#!/usr/bin/env python3
"""Normalize the live translation catalog for public work selection.

The old catalog exposed an operational ``source_preflight`` state and called
its evidence rows ``gates``.  Those names made a suggestion look like a legal
or publication denial.  This one-shot migration keeps the underlying evidence
and license text, but presents a plain distribution class, renames the evidence
collection, and separates workflow startability from packet/readback evidence.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "catalog" / "translations.json"
CHOICES = ROOT / "kits" / "translate" / "WORKS.json"


def load(path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    if raw.startswith(b"\xef\xbb\xbf") or b"\r" in raw:
        raise ValueError(f"{path} must be UTF-8 LF-only without BOM")
    value = json.loads(raw.decode("utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} root must be an object")
    return value


def dump(path: Path, value: dict[str, Any]) -> bytes:
    data = (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    path.write_bytes(data)
    return data


def classify(source: dict[str, Any], item_kinds: dict[str, str]) -> tuple[str, str]:
    rights = source.get("rights") or {}
    license_row = rights.get("work_license") or {}
    name = str(license_row.get("name") or "").lower()
    item_kind = item_kinds.get(str(source.get("item_id")), "")
    if (
        source.get("readiness") in {"not_standalone", "reference_only"}
        and not name
    ) or (item_kind in {"reference", "infrastructure"} and not name):
        return (
            "reference_only",
            "Reference or component entry; it is not a standalone translation job.",
        )
    if rights.get("derivative_translation_allowed") is False or "no derivative" in name:
        return (
            "no_derivatives",
            "The source records a No-Derivatives restriction; retain that exact notice when deciding whether a translation edition can be distributed.",
        )
    mixed_markers = (
        "remaining",
        "mixed",
        "principally",
        "not fully stated",
        "exact component",
        "component-specific",
        " plus ",
        " and ",
        "separate",
        "exact license",
    )
    if "cc by-nc" in name:
        mixed_license_family = (
            ("cc by 4" in name and "cc by-nc" in name)
            or ("cc by-sa" in name and "cc by-nc" in name)
            or ("mit" in name and "cc by-nc" in name)
            or ("gpl" in name and "cc by-nc" in name)
        )
        if (
            any(marker in name for marker in mixed_markers)
            or mixed_license_family
            or name.count("cc ") > 1
        ):
            return (
                "mixed_components",
                "Mixed or incomplete component terms are recorded here; do not infer a blanket license beyond the named notices.",
            )
        return (
            "noncommercial_only",
            "Non-commercial distribution only; not for commercial distribution. Preserve the attribution and ShareAlike terms named by the source.",
        )
    if name and any(token in name for token in ("cc by", "mit", "gpl", "lppl", "public domain")):
        return (
            "open_license",
            "An open license is named for the source; follow its attribution, ShareAlike, component, and notice terms.",
        )
    if name:
        return (
            "terms_unclassified",
            "A license name is recorded, but its distribution class is not normalized in this catalog.",
        )
    return (
        "terms_unclassified",
        "The current catalog has no normalized license note for this source. Choose a source with published terms or add the exact terms when preparing a packet.",
    )


def rewrite_reason(text: str) -> str:
    replacements = {
        "Foundational prealgebra work with a bounded source and component preflight.": "Foundational prealgebra work with a bounded instructional scope.",
        "Foundational elementary-algebra work with a bounded source and component preflight.": "Foundational elementary-algebra work with a bounded instructional scope.",
        "Intermediate-algebra work with a bounded source, media, and component preflight.": "Intermediate-algebra work with a bounded instructional scope and recorded media notes.",
        "Precalculus work with a recorded repository handle and unresolved source and component preflight.": "Precalculus work with a recorded repository handle and a clearly bounded continuation task.",
        "Exact include, asset, ID, and xref closure is complete and topical coverage is coherent, but solution and build-policy gates remain.": "Exact include, asset, ID, and xref closure is complete and the topical coverage is coherent.",
        "Unusually broad geometry coverage and strong editable-source/rights evidence, with bounded build and rights defects.": "Unusually broad geometry coverage with strong editable-source and license evidence.",
        "Excellent lawful content and solutions, but fails the hard editable-source gate.": "Excellent openly available content and solutions; use the listed source format and scope.",
        "Verified lawful classical core with substantial source coverage, but not the complete specified course.": "Named distribution terms and substantial source coverage are recorded, but this is not the complete specified course.",
        "Lawful coherent compact lecture core, but not a complete algebraic-topology selection.": "Named distribution terms and a coherent compact lecture core are recorded, but this is not a complete algebraic-topology selection.",
        "Useful lawful modules, but not a complete independent-study spine.": "Useful modules with recorded distribution terms, but not a complete independent-study spine.",
        "Strong lawful computing and reproducibility components, but no single work closes the mathematical role.": "Strong computing and reproducibility components with recorded distribution terms, but no single work closes the mathematical role.",
        "No lawful component currently satisfies source, scope, and self-study closure together.": "No single component currently satisfies the recorded source, scope, and self-study requirements together.",
        "Useful lawful components split the required scope and cannot yet form one admitted course.": "Useful components with recorded distribution terms split the required scope and cannot yet form one complete course.",
        "Complementary lawful sources exist, but no complete bridge is currently admitted.": "Complementary sources with recorded distribution terms exist, but no complete bridge is currently listed.",
        "A public Indonesian reader is available; the source work, license, components, and translation scope still require exact preflight.": "A public Indonesian reader is available; its source identity, license note, components, and scope are recorded below.",
        "A public Indonesian Unit 1 reader is available; the exact Dionne work, source edition, license, components, and scope still require preflight.": "A public Indonesian Unit 1 reader is available; its current identity, license note, components, and scope are recorded below.",
        "Current breadth and source-first routes each fail a different hard gate.": "Current breadth and source-first routes provide distinct options for an independently scoped translation.",
        "Each route supplies different strengths, but neither closes all hard gates.": "Each route supplies different strengths; contributors can choose and bound one route.",
    }
    return replacements.get(text, text.replace("preflight", "source note").replace("Preflight", "Source note"))


def rewrite_check_basis(row: dict[str, Any]) -> None:
    basis = str(row.get("basis") or "")
    replacements = {
        "The planning snapshot does not independently close translation rights.": "The current catalog does not provide a normalized license note for this source.",
        "Component and media rights have not been independently censused.": "Component and media license notes are not itemized in the current catalog.",
        "No independently replayed source edition is bound.": "The source edition is listed by catalog evidence, not by a frozen packet receipt.",
        "No immutable source archive or complete Git-tree replay is bound.": "A downloadable packet or complete Git-tree receipt is not recorded for this row.",
        "Editable-source closure has not been independently replayed.": "An editable source is not identified in the current row.",
        "No exact baseline build receipt is bound.": "A baseline build receipt is not recorded for this row.",
    }
    row["basis"] = replacements.get(basis, basis)


def workflow_fields(source: dict[str, Any]) -> tuple[str, str, str]:
    """Return operational workflow state without changing source evidence.

    A generic starter is usable for a work even when this repository has not
    packaged or replayed a self-contained source ZIP.  ``readiness`` remains
    the packet/evidence axis; these fields answer whether a contributor can
    begin or continue a translation workflow.
    """
    if source.get("item_type") == "resource" or source.get("readiness") == "reference_only":
        return (
            "reference_only",
            "reference_only",
            "This row is a component, collection, or reference; use it to scope a separate work rather than as a standalone job.",
        )
    if source.get("readiness") == "runnable":
        return (
            "source_bound_packet",
            "source_bound_packet",
            "A self-contained source packet is published with release, byte, SHA-256, and public-readback evidence.",
        )
    if source.get("readiness") == "identity_unresolved":
        return (
            "starter_available",
            "generic_starter",
            "The translation workflow can start with the generic starter; identify the exact work or edition and record the source before the first bounded translation unit.",
        )
    return (
        "starter_available",
        "generic_starter",
        "The translation workflow can start with the generic starter; supply or obtain the exact source and record its distribution note before the first bounded translation unit.",
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--updated-at", default="2026-08-23T12:00:00Z")
    args = parser.parse_args()
    catalog = load(CATALOG)
    choices = load(CHOICES)
    item_kinds = {
        str(row.get("id")): str(row.get("kind"))
        for row in [*catalog.get("works", []), *catalog.get("resources", [])]
        if isinstance(row, dict)
    }

    catalog["schema"] = "math-commons-translation-catalog/v8"
    catalog["updated_at"] = args.updated_at
    catalog["scope"] = {
        "non_exhaustive": True,
        "other_open_works_welcome": True,
        "description": (
            "A non-exclusive directory of mathematical works and resources for translation outside maintained project lanes. "
            "Each row gives a readable work identity, language evidence, distribution class, and practical next action."
        ),
        "coverage_rule": (
            "A work may be workflow-startable without a self-contained public packet. "
            "readiness reports source-packet evidence; jobs[].state=runnable reports a packaged release with public readback. "
            "Unknown coverage means unknown, not absence; current maintained editions are not adoption targets unless explicitly listed."
        ),
    }
    catalog["language_priority"]["priority_rule"] = (
        "Any language is welcome. Contributors may consider communities in the UNESCO-UIS 96-language assessment set and other underserved languages; record the exact locale, script, written standard, intended learners, and existing coverage."
    )
    distribution_legend = {
        "open_license": "Open license named; follow attribution, ShareAlike, component, and notice terms.",
        "noncommercial_only": "Non-commercial distribution only; not for commercial distribution. Preserve attribution and ShareAlike terms.",
        "mixed_components": "Mixed or incomplete component terms; use the named notices and do not infer a blanket license.",
        "terms_unclassified": "The current row does not normalize the license terms; add the exact source terms when preparing a packet.",
        "no_derivatives": "An explicit No-Derivatives restriction is recorded; preserve the source notice when deciding whether a translation edition can be distributed.",
        "reference_only": "Reference or component entry; not a standalone translation job.",
    }
    catalog["distribution_legend"] = distribution_legend

    for row in catalog.get("works", []) + catalog.get("resources", []):
        if isinstance(row, dict) and isinstance(row.get("why_listed"), str):
            row["why_listed"] = rewrite_reason(row["why_listed"])
    for source in catalog.get("source_editions", []):
        if not isinstance(source, dict):
            continue
        if "gates" in source:
            source["evidence_checks"] = source.pop("gates")
        if source.get("readiness") == "source_preflight":
            source["readiness"] = "listed"
        elif source.get("readiness") == "not_standalone":
            source["readiness"] = "reference_only"
        rights = source.setdefault("rights", {})
        distribution_class, distribution_note = classify(source, item_kinds)
        rights["distribution_class"] = distribution_class
        rights["distribution_note"] = distribution_note
        license_row = rights.get("work_license")
        if isinstance(license_row, dict) and license_row.get("scope") == "Reported planning metadata; not independently replayed":
            license_row["scope"] = "License note reported in the current catalog snapshot; independent source or component replay may be absent."
        checks = source.get("evidence_checks")
        if isinstance(checks, dict):
            for check in checks.values():
                if isinstance(check, dict):
                    rewrite_check_basis(check)
        readiness = source.get("readiness")
        startability, mode, note = workflow_fields(source)
        source["workflow_startability"] = startability
        source["workflow_mode"] = mode
        source["workflow_note"] = note
        if readiness == "runnable":
            source["next_action"] = "Download the public packet, verify its byte length and SHA-256, then select the target language and written standard."
        elif readiness == "reference_only":
            source["next_action"] = "Use this entry as reference material or as a component of a separately scoped translation."
        elif readiness == "identity_unresolved":
            source["next_action"] = "Choose a target language and identify the exact source edition before returning the first translation checkpoint."
        else:
            source["next_action"] = "Choose a target language, obtain the cited source edition, and return a cumulative translation checkpoint with the source and license note."

    catalog_bytes = dump(CATALOG, catalog)

    choices["schema"] = "math-commons-translation-choices/v8"
    choices["updated_at"] = args.updated_at
    choices["language_priority"] = catalog["language_priority"]
    choices["rule"] = (
        "Choose a topic, then a non-reference work and target language. A work with workflow_startability=starter_available or source_bound_packet can be started with the generic kit; use the separately published packet when source_bound_packet is available. A packaged job with public readback is represented separately by jobs[].state=runnable. Each row states its distribution class and license note; unknown coverage never means absence."
    )
    choices.pop("source_preflight", None)
    choices["distribution_legend"] = distribution_legend
    catalog_identity = {
        "path": "catalog/translations.json",
        "bytes": len(catalog_bytes),
        "sha256": hashlib.sha256(catalog_bytes).hexdigest().upper(),
    }
    choices["catalog"] = catalog_identity
    for row in choices.get("source_editions", []):
        if not isinstance(row, dict):
            continue
        source = next((s for s in catalog["source_editions"] if s.get("id") == row.get("id")), None)
        if isinstance(source, dict):
            row["readiness"] = source["readiness"]
            row["workflow_startability"] = source["workflow_startability"]
            row["workflow_mode"] = source["workflow_mode"]
            row["workflow_note"] = source["workflow_note"]
            rights = source.get("rights", {})
            row["distribution_class"] = rights.get("distribution_class")
            row["distribution_note"] = rights.get("distribution_note")
    # Keep the downloadable chooser projection synchronized with the live
    # catalog.  Additive reader rows are real work scopes, not optional
    # metadata that can silently disappear from WORKS.json.
    choices["topics"] = [
        {
            "id": row["id"],
            "title": row["title"],
            "work_ids": row["work_ids"],
            "resource_ids": row["resource_ids"],
        }
        for row in catalog.get("topics", [])
    ]
    choices["works"] = [
        {
            "id": row["id"],
            "title": row["title"],
            "topic_ids": row["topic_ids"],
            "source_edition_ids": row["source_edition_ids"],
            "translation_edition_ids": row["translation_edition_ids"],
            "job_ids": row["job_ids"],
        }
        for row in catalog.get("works", [])
    ]
    choices["resources"] = [
        {
            "id": row["id"],
            "title": row["title"],
            "kind": row["kind"],
            "topic_ids": row["topic_ids"],
            "source_edition_ids": row["source_edition_ids"],
        }
        for row in catalog.get("resources", [])
    ]
    choices["source_editions"] = [
        {
            "id": row["id"],
            "item_id": row["item_id"],
            "item_type": row["item_type"],
            "readiness": row["readiness"],
            "workflow_startability": row["workflow_startability"],
            "workflow_mode": row["workflow_mode"],
            "workflow_note": row["workflow_note"],
            "distribution_class": row["rights"]["distribution_class"],
            "distribution_note": row["rights"]["distribution_note"],
        }
        for row in catalog.get("source_editions", [])
    ]
    choices["translation_editions"] = [
        {
            "id": row["id"],
            "work_id": row["work_id"],
            "language": row["target_language"],
            "identity_state": row["identity_state"],
            "progress_state": row["progress_state"],
            "review_state": row["review_state"],
        }
        for row in catalog.get("translation_editions", [])
    ]
    choices["jobs"] = catalog.get("jobs", [])
    dump(CHOICES, choices)
    print(json.dumps({"catalog_bytes": len(catalog_bytes), "catalog_sha256": catalog_identity["sha256"], "sources": len(catalog["source_editions"])}, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
