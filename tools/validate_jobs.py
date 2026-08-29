#!/usr/bin/env python3
"""Validate job/translation catalogs and optional local release ZIPs."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import stat
import sys
import tempfile
import zipfile
from pathlib import Path, PurePosixPath
from typing import Any


TOOLS = Path(__file__).resolve().parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from validate_packets import (  # noqa: E402
    SchemaDocument,
    SchemaSet,
    iter_schema_nodes,
    lint_schema,
    validate_instance,
)


ROOT = Path(__file__).resolve().parents[1]
HEX64 = re.compile(r"^[0-9A-F]{64}$")
SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
ASSET_NAME = re.compile(r"^[a-z0-9][a-z0-9.-]*\.zip$")
RELEASE_TAG = re.compile(r"^jobs-[0-9]{4}-[0-9]{2}-[0-9]{2}-r[0-9]+$")
ADMITTED_STATUSES = {
    "PASS_COLD_PACKET_VALIDATION",
    "PASS_FINAL_NONPATCHING",
    "PASS_GLOBAL_COLD_AUDIT",
}
PRACTICAL_SCHEMAS = {
    "job_meta": "job-meta.schema.json",
    "jobs": "job-catalog.schema.json",
    "asset": "job-asset.schema.json",
    "translations": "translation-catalog.schema.json",
    "translation_choices": "translation-choices.schema.json",
    "translation_source": "translation-source.schema.json",
    "translation_build": "translation-build.schema.json",
    "education": "edu.schema.json",
    "formalization": "formalization-intake.schema.json",
    "check": "catalog-check.schema.json",
    "readback": "release-readback.schema.json",
    "portals": "portal-catalog.schema.json",
    "portal_readback": "portal-readback.schema.json",
}
CHUNK = 1024 * 1024
FIXED_TIME = (1980, 1, 1, 0, 0, 0)
REGULAR_0644 = 0o100644
READBACK_COMMIT = "6c0c7bbd368cb554d4d9ab9133881a5d4bf56a75"
READBACK_MAIN_AT_OBSERVATION = "5bd7983daf8d540b12409dab077d688c41df2666"
READBACK_TAG = "jobs-2026-08-21-r2"
READBACK_RELEASE_ID = 374540343
READBACK_REPOSITORY = "KokunoYumeto/mathematics-commons-pilot"
READBACK_DATE = "2026-08-22"
PORTAL_V1_BYTES = 3_326
PORTAL_V1_SHA256 = "DC365E3C156D97ECA18F0B8154C160E0C5A42938D0C3E09F86B21793235C40D4"
TRANSLATE_V9_CATALOG_BYTES = 241_565
TRANSLATE_V9_CATALOG_SHA256 = "C4C5E04BD72116607619E1B3F6FEB7DE4EED28ACE56AF4BB98B0B87260614941"
TRANSLATE_V9_TAG = "translate-v9-final"
READBACK_RAW_FILES = (
    ("README.md", 8025, "5BAEEBBBADBC59F2039D6CF20ADD0971E3931084B6F1C810526E1BC2FD9BD16D"),
    ("docs/workbench.md", 13833, "63382D0B67B5BB030609AC4DFDD519E4F621349562DBD6B5E82F854C7E8255F0"),
    ("docs/roadmap.md", 2011, "E486DFCFBB7F0CFC3FA853E6A95B0BFBFBCF688EBF50A3E8AD04E8FB15E4F9B3"),
    ("catalog/jobs.json", 131843, "81C83746817B82F71BBCE337B338D87A95E8240693D4F645F78888F88B3AABD5"),
    ("catalog/check.json", 5388, "EA4FE70EE87478BFF119A2AD58222BDFE85AB9CBE4070F976D016ECF6D5E46C2"),
    ("schemas/catalog-check.schema.json", 7083, "6656074028A7DB28A15CCFCA2759059707DA54EC468EABF850DC43EA13690265"),
    ("tools/validate_jobs.py", 67554, "5EBA8A6638378D1FDA605DD25F82415414B98978EE8BD8D7B9BFB1F12872C549"),
    ("catalog/receipts/r2-admission.json", 88449, "C6D7B5F02DEBF227A61DBD1B611AD79F7AC1F3F0AC3A1634EC18DA8B759F40EC"),
    ("catalog/receipts/no-failure-hardening.json", 28430, "1961AF0B9EA3A0719ACE87F55F6195E8F07AE8CA453880A8BBDA241A40647D66"),
)


class DuplicateKey(ValueError):
    pass


def pairs(values: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in values:
        if key in result:
            raise DuplicateKey(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def load(path: Path) -> tuple[dict[str, Any], bytes]:
    data = path.read_bytes()
    if data.startswith(b"\xef\xbb\xbf") or b"\r" in data:
        raise ValueError(f"JSON must be UTF-8 LF without BOM: {path}")
    value = json.loads(data.decode("utf-8"), object_pairs_hook=pairs)
    if not isinstance(value, dict):
        raise ValueError(f"JSON root is not an object: {path}")
    return value, data


_SCHEMA_SET: SchemaSet | None = None


def practical_schema_set() -> SchemaSet:
    global _SCHEMA_SET
    if _SCHEMA_SET is not None:
        return _SCHEMA_SET
    documents: list[SchemaDocument] = []
    for name in PRACTICAL_SCHEMAS.values():
        path = ROOT / "schemas" / name
        body, _ = load(path)
        documents.append(SchemaDocument(path=path, body=body))
    schema_set = SchemaSet(documents)
    schema_errors: list[str] = []
    for document in documents:
        schema_errors.extend(lint_schema(document))
        for _, node in iter_schema_nodes(document.body):
            if isinstance(node, dict) and isinstance(node.get("$ref"), str):
                try:
                    schema_set.resolve(node["$ref"], document)
                except ValueError as exc:
                    schema_errors.append(str(exc))
    if schema_errors:
        raise ValueError("practical schema contract failed:\n" + "\n".join(schema_errors))
    _SCHEMA_SET = schema_set
    return schema_set


def validate_schema(
    instance: dict[str, Any], schema_key: str, label: str, errors: list[str]
) -> None:
    schema_set = practical_schema_set()
    document = schema_set.by_name[PRACTICAL_SCHEMAS[schema_key]]
    for error in validate_instance(instance, document.body, schema_set, document):
        errors.append(f"{label}: {error}")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while block := handle.read(CHUNK):
            digest.update(block)
    return digest.hexdigest().upper()


def input_identity(path: Path) -> dict[str, object]:
    data = path.read_bytes()
    return {
        "path": path.relative_to(ROOT).as_posix(),
        "bytes": len(data),
        "sha256": sha256(data),
    }


def manifest_set_identity() -> dict[str, object]:
    rows = []
    for path in sorted((ROOT / "catalog" / "assets").glob("*.json")):
        item = input_identity(path)
        rows.append(item)
    stream = "".join(
        f"{row['path']}\t{row['bytes']}\t{row['sha256']}\n" for row in rows
    ).encode("utf-8")
    return {
        "files": len(rows),
        "bytes": sum(int(row["bytes"]) for row in rows),
        "canonical_stream_bytes": len(stream),
        "tree_sha256": sha256(stream),
    }


def audit_snapshot_sha256(members: list[dict[str, Any]]) -> str:
    """Replay the producer audit's PowerShell Sort-Object Name stream."""
    ordered = sorted(members, key=lambda row: str(row.get("path", "")).casefold())
    stream = "".join(
        f"{row['path']}\t{row['bytes']}\t{row['sha256']}\n" for row in ordered
    ).encode("utf-8")
    return sha256(stream)


def safe_path(value: Any) -> bool:
    if (
        not isinstance(value, str)
        or not value
        or len(value.encode("utf-8")) > 500
        or "\\" in value
        or any(ord(char) < 32 for char in value)
    ):
        return False
    path = PurePosixPath(value)
    parts = path.parts
    if (
        path.is_absolute()
        or not parts
        or value != "/".join(parts)
        or any(part in {"", ".", ".."} for part in parts)
        or any(len(part.encode("utf-8")) > 255 for part in parts)
        or any(part.endswith((" ", ".")) for part in parts)
        or any(any(char in '<>:"|?*' for char in part) for part in parts)
    ):
        return False
    return True


def expect(condition: bool, errors: list[str], message: str) -> None:
    if not condition:
        errors.append(message)


def validate_openlogic_build(
    value: dict[str, Any], label: str, errors: list[str]
) -> None:
    targets = value.get("targets")
    expected = [
        ("open-logic-debug.tex", "open-logic-debug.pdf", 962),
        ("open-logic-complete.tex", "open-logic-complete.pdf", 1013),
    ]
    expect(
        isinstance(targets, list)
        and len(targets) == len(expected)
        and [row.get("target") for row in targets if isinstance(row, dict)]
        == [row[0] for row in expected],
        errors,
        f"{label}: exact target order and uniqueness",
    )
    if not isinstance(targets, list) or len(targets) != len(expected):
        return
    for index, (target_name, pdf_name, pages) in enumerate(expected):
        row = targets[index]
        if not isinstance(row, dict):
            errors.append(f"{label}: target {index} is not an object")
            continue
        expect(
            row.get("target") == target_name
            and row.get("exit_code") == 0
            and row.get("fresh_isolated_source_copy") is True
            and row.get("tracked_source_post_build_replay") == "792/792"
            and row.get("pdf", {}).get("path") == pdf_name
            and row.get("pdf", {}).get("pages") == pages
            and row.get("log", {}).get("fatal_markers") == 0
            and row.get("input_closure", {}).get("closed") is True
            and row.get("input_closure", {}).get("unbound_repo_relative_inputs") == []
            and row.get("input_closure", {}).get("excluded_doc_inputs") == [],
            errors,
            f"{label}: {target_name} successful closed build",
        )
    expect(
        value.get("input_closure", {}).get("targets") == 2
        and value.get("input_closure", {}).get("all_closed") is True
        and value.get("input_closure", {}).get("excluded_doc_inputs") == 0
        and value.get("input_closure", {}).get("unbound_repo_relative_inputs") == 0
        and value.get("input_closure", {}).get("unknown_external_inputs") == 0,
        errors,
        f"{label}: aggregate input closure",
    )


def verify_repo_identity(declared: Any, label: str, errors: list[str]) -> None:
    projection = declared.get("public_projection") if isinstance(declared, dict) else None
    if not isinstance(projection, dict) or not safe_path(projection.get("path")):
        errors.append(f"{label}: missing safe public projection path")
        return
    path = (ROOT / projection["path"]).resolve()
    try:
        path.relative_to(ROOT.resolve())
    except ValueError:
        errors.append(f"{label}: public path escapes repository")
        return
    if not path.is_file():
        errors.append(f"{label}: public file missing")
        return
    expect(path.stat().st_size == projection.get("bytes"), errors, f"{label}: public bytes")
    expect(sha256_file(path) == projection.get("sha256"), errors, f"{label}: public SHA-256")


def bind_declared_member(
    members_by_path: dict[str, dict[str, Any]],
    declared: Any,
    label: str,
    errors: list[str],
) -> None:
    if not isinstance(declared, dict):
        errors.append(f"{label}: identity is not an object")
        return
    basename = declared.get("basename")
    if not isinstance(basename, str) or Path(basename).name != basename:
        errors.append(f"{label}: unsafe basename")
        return
    row = members_by_path.get(basename)
    if row is None:
        errors.append(f"{label}: member missing")
        return
    expect(row.get("bytes") == declared.get("bytes"), errors, f"{label}: member bytes")
    expect(row.get("sha256") == declared.get("sha256"), errors, f"{label}: member SHA-256")


def valid_prompt_count(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value >= 1


def bind_job_control_members(
    job: dict[str, Any],
    members_by_path: dict[str, dict[str, Any]],
    errors: list[str],
) -> None:
    job_id = str(job.get("id"))
    for field, label in (
        ("start_file", "start file"),
        ("prompt_file", "prompt file"),
        ("packet_manifest", "packet manifest"),
    ):
        bind_declared_member(
            members_by_path,
            job.get(field),
            f"{job_id}: {label}",
            errors,
        )


def binds_global_admission_projection(
    catalog: dict[str, Any], job: dict[str, Any], receipt: Any
) -> bool:
    admission = catalog.get("admission")
    audit_receipt = admission.get("audit_receipt") if isinstance(admission, dict) else None
    return (
        isinstance(receipt, dict)
        and isinstance(audit_receipt, dict)
        and receipt.get("included_in_packet") is False
        and job.get("audit_basis") == "global_receipt"
        and receipt.get("public_projection")
        == audit_receipt.get("public_projection")
    )


def validate_hardening_projection(
    meta: dict[str, Any], packet_ids: list[str], errors: list[str]
) -> None:
    declared = meta.get("hardening_receipt")
    projection = declared.get("public_projection") if isinstance(declared, dict) else None
    path = ROOT / str(projection.get("path", "") if isinstance(projection, dict) else "")
    try:
        receipt, _ = load(path)
    except (OSError, UnicodeError, json.JSONDecodeError, DuplicateKey, ValueError) as exc:
        errors.append(f"no-failure hardening receipt: cannot parse projection: {exc}")
        return
    rows = receipt.get("rows")
    expect(
        receipt.get("schema") == "math-commons-packet-no-failure-hardening/v1",
        errors,
        "no-failure hardening schema",
    )
    expect(
        isinstance(rows, list)
        and len(rows) == len(packet_ids)
        and {str(row.get("packet_id")) for row in rows if isinstance(row, dict)}
        == set(packet_ids),
        errors,
        "no-failure hardening packet projection",
    )
    expect(
        isinstance(rows, list)
        and all(
            isinstance(row, dict)
            and row.get("result") == "PASS"
            and row.get("forbidden_controlling_outcome_conditions") == 0
            for row in rows
        ),
        errors,
        "no-failure hardening row result",
    )
    summary = receipt.get("summary")
    expect(
        isinstance(summary, dict)
        and summary.get("rows") == len(packet_ids)
        and summary.get("pass") == len(packet_ids)
        and summary.get("fail") == 0
        and summary.get("forbidden_controlling_outcome_conditions") == 0,
        errors,
        "no-failure hardening summary",
    )
    idempotence = receipt.get("idempotence")
    expect(
        isinstance(idempotence, dict)
        and idempotence.get("result") == "PASS"
        and idempotence.get("bounded_exact_28_scope") is True
        and idempotence.get("policy_marker_reapplication_would_change_files") == 0
        and idempotence.get("manifest_repair_second_run_changed_files") == 0,
        errors,
        "no-failure hardening idempotence",
    )
    repair = receipt.get("manifest_repair_source_identity")
    expected_repair = input_identity(ROOT / "tools" / "repair_stale_packet_manifests.py")
    expect(repair == expected_repair, errors, "manifest-repair script identity")
    hardener = receipt.get("hardener_source_identity")
    expect(
        isinstance(hardener, dict)
        and hardener.get("basename") == "harden_no_failure_controls_20260821.py"
        and hardener.get("bytes") == 68969
        and hardener.get("sha256")
        == "60CABC6A375067F553F562CB006A61494A3D3F6F83708D67B8275F74D109BB56",
        errors,
        "bounded hardener source identity",
    )


def validate_terminal_sidecar(
    job: dict[str, Any], manifest: dict[str, Any], errors: list[str]
) -> None:
    job_id = str(job.get("id"))
    receipt = job.get("validation_receipt")
    projection = receipt.get("public_projection") if isinstance(receipt, dict) else None
    if not isinstance(projection, dict) or not safe_path(projection.get("path")):
        errors.append(f"{job_id}: terminal sidecar projection missing")
        return
    path = ROOT / projection["path"]
    members = {
        str(row["path"]): row
        for row in manifest.get("members", [])
        if isinstance(row, dict) and isinstance(row.get("path"), str)
    }
    if job_id == "mikami-development-mathematics-china-japan-1913":
        try:
            sidecar, _ = load(path)
        except (OSError, UnicodeError, json.JSONDecodeError, DuplicateKey, ValueError) as exc:
            errors.append(f"{job_id}: cannot parse terminal sidecar: {exc}")
            return
        expect(
            sidecar.get("schema") == "mikami-1913-web-intake-packet-cold-validation-v1"
            and sidecar.get("verdict") == "PASS_COLD_PACKET_VALIDATION",
            errors,
            f"{job_id}: sidecar verdict",
        )
        expect(job.get("status") == "PASS_COLD_PACKET_VALIDATION", errors, f"{job_id}: status")
        expect(sidecar.get("direct_file_count") == job.get("source_files"), errors, f"{job_id}: sidecar files")
        expect(sidecar.get("direct_total_bytes") == job.get("source_bytes"), errors, f"{job_id}: sidecar bytes")
        expect(sidecar.get("prompt_count") == 45, errors, f"{job_id}: sidecar prompt count")
        expect(sidecar.get("prompt_contract_failures") == [], errors, f"{job_id}: sidecar prompt failures")
        expect(sidecar.get("blockers") == [], errors, f"{job_id}: sidecar blockers")
        packet_manifest = sidecar.get("packet_manifest", {})
        expect(
            isinstance(packet_manifest, dict)
            and packet_manifest.get("rows") == job.get("source_files") - 1
            and packet_manifest.get("sha256") == job.get("packet_manifest", {}).get("sha256")
            and packet_manifest.get("mismatches") == [],
            errors,
            f"{job_id}: sidecar manifest",
        )
        precursor = sidecar.get("packet_validation_receipt", {})
        precursor_name = Path(str(precursor.get("path", ""))).name
        precursor_row = members.get(precursor_name)
        expect(
            precursor_row is not None
            and precursor_row.get("bytes") == precursor.get("bytes")
            and precursor_row.get("sha256") == precursor.get("sha256"),
            errors,
            f"{job_id}: sidecar precursor receipt",
        )
        sidecar_authority = sidecar.get("authority", {})
        declared_authorities = job.get("authority", [])
        expect(
            isinstance(sidecar_authority, dict)
            and isinstance(declared_authorities, list)
            and len(declared_authorities) == 1
            and sidecar_authority.get("sha256") == declared_authorities[0].get("sha256")
            and sidecar_authority.get("pages") == declared_authorities[0].get("pages"),
            errors,
            f"{job_id}: sidecar authority",
        )
        return
    if job_id == "gordan-invariantentheorie-v02-1887":
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            errors.append(f"{job_id}: cannot read terminal sidecar: {exc}")
            return
        required_lines = (
            "FINAL_NONPATCHING_PASS:\n  result: PASS",
            "literal_ordered_prompt_blocks: 45 (P01-P45)",
            "disjoint_production_canvas_cover: 376 (exactly 1-376)",
            "unsafe_or_duplicate_member_paths: 0",
            "RESULT: PASS\n",
        )
        expect(all(line in text for line in required_lines), errors, f"{job_id}: sidecar PASS contract")
        expect(job.get("status") == "PASS_FINAL_NONPATCHING", errors, f"{job_id}: status")
        expected_hashes = {
            "GORDAN_BAND_II_S00_CUMULATIVE_FULL_STATE.zip": "1EF2FF082DE016A3B7C4C4D1EF7F11BAC294102E332E6513A06138FEC875B08C",
            "GORDAN_BAND_II_S00_CUMULATIVE_CHECKPOINT.json": "A60A59EB0C7B54B65C2C1E212673D5D4D46F4907D757C2FCD237FC390612734A",
            "GORDAN_BAND_II_S00_CUMULATIVE_MANIFEST.tsv": "277BDDC2998932E0076603A0DD387FC07FD24C78FDA51462693120A604DB70DB",
        }
        for name, expected_hash in expected_hashes.items():
            row = members.get(name)
            expect(
                row is not None
                and row.get("sha256") == expected_hash
                and f"SHA256 {expected_hash}" in text,
                errors,
                f"{job_id}: sidecar trio {name}",
            )
        expect(
            job.get("packet_manifest", {}).get("sha256")
            == expected_hashes["GORDAN_BAND_II_S00_CUMULATIVE_MANIFEST.tsv"],
            errors,
            f"{job_id}: sidecar packet manifest",
        )
        return
    errors.append(f"{job_id}: unrecognized terminal sidecar job")


def validate_asset_manifest(
    path: Path, expected_job_id: str, errors: list[str]
) -> tuple[dict[str, Any], bytes]:
    try:
        manifest, data = load(path)
    except (OSError, UnicodeError, json.JSONDecodeError, DuplicateKey, ValueError) as exc:
        errors.append(f"cannot load asset manifest {path}: {exc}")
        return {}, b""
    prefix = f"asset manifest {expected_job_id}"
    validate_schema(manifest, "asset", prefix, errors)
    expect(manifest.get("schema") == "math-commons-job-asset/v1", errors, f"{prefix}: schema")
    expect(manifest.get("job_id") == expected_job_id, errors, f"{prefix}: job ID")
    expect(manifest.get("wrapper_directory") == expected_job_id, errors, f"{prefix}: wrapper")
    members = manifest.get("members")
    if not isinstance(members, list) or not members:
        errors.append(f"{prefix}: members missing")
        return manifest, data
    paths = [row.get("path") for row in members if isinstance(row, dict)]
    expect(len(paths) == len(members), errors, f"{prefix}: malformed member row")
    expect(paths == sorted(paths), errors, f"{prefix}: member order")
    expect(len(paths) == len(set(paths)), errors, f"{prefix}: duplicate member path")
    expect(all(safe_path(item) for item in paths), errors, f"{prefix}: unsafe member path")
    portable_prefixes: dict[str, str] = {}
    for member_path in paths:
        if not isinstance(member_path, str) or not safe_path(member_path):
            continue
        parts = PurePosixPath(member_path).parts
        for index in range(1, len(parts) + 1):
            path_prefix = "/".join(parts[:index])
            folded = path_prefix.casefold()
            prior = portable_prefixes.get(folded)
            if prior is not None and prior != path_prefix:
                errors.append(
                    f"{prefix}: case-insensitive path collision: {prior!r} / {path_prefix!r}"
                )
            portable_prefixes[folded] = path_prefix
    expect(
        all(
            isinstance(row.get("bytes"), int)
            and not isinstance(row.get("bytes"), bool)
            and row["bytes"] >= 0
            for row in members
            if isinstance(row, dict)
        ),
        errors,
        f"{prefix}: member bytes",
    )
    expect(all(isinstance(row.get("sha256"), str) and HEX64.fullmatch(row["sha256"]) for row in members), errors, f"{prefix}: member hash")
    expect(
        all(
            "mode" not in row or row.get("mode") in {"100644", "100755"}
            for row in members
            if isinstance(row, dict)
        ),
        errors,
        f"{prefix}: member mode",
    )
    if len(paths) != len(members) or not all(
        isinstance(row, dict)
        and isinstance(row.get("path"), str)
        and isinstance(row.get("bytes"), int)
        and not isinstance(row.get("bytes"), bool)
        and isinstance(row.get("sha256"), str)
        for row in members
    ):
        return manifest, data
    stream = "".join(
        f"{row['path']}\t{row['bytes']}\t{row['sha256']}\n" for row in members
    ).encode("utf-8")
    expect(manifest.get("source_files") == len(members), errors, f"{prefix}: source file count")
    expect(manifest.get("source_bytes") == sum(row["bytes"] for row in members), errors, f"{prefix}: source bytes")
    expect(manifest.get("canonical_stream_bytes") == len(stream), errors, f"{prefix}: stream bytes")
    expect(manifest.get("source_tree_sha256") == sha256(stream), errors, f"{prefix}: tree hash")
    if "mode_stream_bytes" in manifest or "mode_tree_sha256" in manifest:
        mode_stream = "".join(
            f"{row['path']}\t{row.get('mode', '100644')}\t{row['bytes']}\t{row['sha256']}\n"
            for row in members
        ).encode("utf-8")
        expect(
            manifest.get("mode_stream_bytes") == len(mode_stream),
            errors,
            f"{prefix}: mode stream bytes",
        )
        expect(
            manifest.get("mode_tree_sha256") == sha256(mode_stream),
            errors,
            f"{prefix}: mode tree hash",
        )
    assets = manifest.get("assets")
    if not isinstance(assets, list) or not assets:
        errors.append(f"{prefix}: assets missing")
        return manifest, data
    expect(manifest.get("asset_count") == len(assets), errors, f"{prefix}: asset count")
    expect(all(isinstance(asset, dict) for asset in assets), errors, f"{prefix}: malformed asset row")
    offset = 0
    for index, asset in enumerate(assets, start=1):
        if not isinstance(asset, dict):
            continue
        expect(asset.get("part") == index, errors, f"{prefix}: part order {index}")
        expect(asset.get("parts") == len(assets), errors, f"{prefix}: part total {index}")
        name = asset.get("name")
        expect(
            isinstance(name, str)
            and Path(name).name == name
            and ASSET_NAME.fullmatch(name) is not None,
            errors,
            f"{prefix}: asset name {index}",
        )
        count = asset.get("source_files")
        if not isinstance(count, int) or isinstance(count, bool) or count <= 0:
            errors.append(f"{prefix}: asset file count {index}")
            continue
        expected_members = members[offset : offset + count]
        expect(len(expected_members) == count, errors, f"{prefix}: asset slice {index}")
        if expected_members:
            expect(
                asset.get("first_path") == expected_members[0]["path"],
                errors,
                f"{prefix}: first path {index}",
            )
            expect(
                asset.get("last_path") == expected_members[-1]["path"],
                errors,
                f"{prefix}: last path {index}",
            )
            expect(
                asset.get("source_bytes")
                == sum(int(row["bytes"]) for row in expected_members),
                errors,
                f"{prefix}: asset byte slice {index}",
            )
        offset += count
        expect(
            isinstance(asset.get("zip_bytes"), int)
            and not isinstance(asset.get("zip_bytes"), bool)
            and 0 < asset["zip_bytes"] < 2 * 1024**3,
            errors,
            f"{prefix}: GitHub asset size {index}",
        )
        expect(
            isinstance(asset.get("zip_sha256"), str)
            and HEX64.fullmatch(asset["zip_sha256"]) is not None,
            errors,
            f"{prefix}: ZIP hash {index}",
        )
    expect(offset == len(members), errors, f"{prefix}: asset file partition")
    expect(
        sum(
            asset.get("source_bytes", 0)
            for asset in assets
            if isinstance(asset, dict)
            and isinstance(asset.get("source_bytes"), int)
            and not isinstance(asset.get("source_bytes"), bool)
        )
        == manifest.get("source_bytes"),
        errors,
        f"{prefix}: asset byte partition",
    )
    checks = manifest.get("checks", {})
    expect(checks.get("source_hash_replay") == f"{len(members)}/{len(members)}", errors, f"{prefix}: source replay")
    expect(checks.get("zip_member_replay") == f"{len(members)}/{len(members)}", errors, f"{prefix}: ZIP replay")
    expect(all(checks.get(key) == 0 for key in ("crc_errors", "missing", "extra", "byte_mismatches", "hash_mismatches")), errors, f"{prefix}: error counters")
    return manifest, data


def replay_zip(
    asset_dir: Path,
    job_id: str,
    manifest: dict[str, Any],
    errors: list[str],
) -> None:
    members = manifest["members"]
    offset = 0
    for asset in manifest["assets"]:
        path = asset_dir / asset["name"]
        prefix = f"local asset {asset['name']}"
        if not path.is_file():
            errors.append(f"{prefix}: missing")
            continue
        expect(path.stat().st_size == asset["zip_bytes"], errors, f"{prefix}: bytes")
        expect(sha256_file(path) == asset["zip_sha256"], errors, f"{prefix}: SHA-256")
        count = asset["source_files"]
        expected = members[offset : offset + count]
        offset += count
        try:
            with zipfile.ZipFile(path, "r") as archive:
                expect(archive.testzip() is None, errors, f"{prefix}: CRC")
                expect(archive.comment == b"", errors, f"{prefix}: archive comment")
                names = archive.namelist()
                expected_names = [f"{job_id}/{row['path']}" for row in expected]
                expect(names == expected_names, errors, f"{prefix}: member paths/order")
                for row, name in zip(expected, names):
                    info = archive.getinfo(name)
                    expected_mode = (
                        (stat.S_IFREG | 0o755)
                        if row.get("mode") == "100755"
                        else REGULAR_0644
                    )
                    expect(info.date_time == FIXED_TIME, errors, f"{prefix}: member time {name}")
                    expect(
                        info.compress_type == zipfile.ZIP_DEFLATED,
                        errors,
                        f"{prefix}: compression {name}",
                    )
                    expect(info.create_system == 3, errors, f"{prefix}: create system {name}")
                    expect(
                        info.external_attr >> 16 == expected_mode,
                        errors,
                        f"{prefix}: mode {name}",
                    )
                    expect(info.extra == b"", errors, f"{prefix}: extra metadata {name}")
                    expect(info.comment == b"", errors, f"{prefix}: member comment {name}")
                    expect(
                        info.flag_bits == (0x800 if not name.isascii() else 0),
                        errors,
                        f"{prefix}: flag bits {name}",
                    )
                    expect(info.create_version == 20, errors, f"{prefix}: create version {name}")
                    expect(info.extract_version == 20, errors, f"{prefix}: extract version {name}")
                    expect(info.internal_attr == 0, errors, f"{prefix}: internal attrs {name}")
                    expect(info.file_size == row["bytes"], errors, f"{prefix}: member bytes {name}")
                    digest = hashlib.sha256()
                    with archive.open(info, "r") as handle:
                        while block := handle.read(CHUNK):
                            digest.update(block)
                    expect(digest.hexdigest().upper() == row["sha256"], errors, f"{prefix}: member hash {name}")
        except (OSError, zipfile.BadZipFile, KeyError) as exc:
            errors.append(f"{prefix}: {exc}")


def replay_nested_authority(
    asset_dir: Path,
    job_id: str,
    manifest: dict[str, Any],
    authority: dict[str, Any],
    errors: list[str],
) -> bool:
    levels = str(authority.get("path", "")).split("!/")
    if len(levels) != 2:
        return False
    outer_path, inner_path = levels
    wrapped_outer = f"{job_id}/{outer_path}"
    found = 0
    matched = False
    for asset in manifest["assets"]:
        release_path = asset_dir / asset["name"]
        if not release_path.is_file():
            continue
        prefix = f"{job_id}: nested authority {outer_path}!/{inner_path}"
        try:
            with zipfile.ZipFile(release_path, "r") as release:
                try:
                    outer_info = release.getinfo(wrapped_outer)
                except KeyError:
                    continue
                found += 1
                with tempfile.TemporaryFile(mode="w+b") as staged:
                    with release.open(outer_info, "r") as source:
                        while block := source.read(CHUNK):
                            staged.write(block)
                    staged.seek(0)
                    with zipfile.ZipFile(staged, "r") as outer_archive:
                        inner_info = outer_archive.getinfo(inner_path)
                        expect(not inner_info.is_dir(), errors, f"{prefix}: target is a file")
                        digest = hashlib.sha256()
                        with outer_archive.open(inner_info, "r") as source:
                            while block := source.read(CHUNK):
                                digest.update(block)
                        matched = digest.hexdigest().upper() == authority.get("sha256")
                        expect(matched, errors, f"{prefix}: SHA-256")
        except (OSError, RuntimeError, zipfile.BadZipFile, KeyError) as exc:
            errors.append(f"{prefix}: {exc}")
    expect(found == 1, errors, f"{job_id}: nested authority outer occurrence")
    return found == 1 and matched


def validate_job_meta(catalog: dict[str, Any], errors: list[str]) -> None:
    meta, _ = load(ROOT / "catalog" / "job-meta.json")
    validate_schema(meta, "job_meta", "job metadata", errors)
    expect(meta.get("schema") == "math-commons-job-meta/v2", errors, "job metadata schema")
    meta_jobs = meta.get("jobs")
    public_jobs = catalog.get("jobs")
    if not isinstance(meta_jobs, list) or not isinstance(public_jobs, list):
        errors.append("job metadata or public jobs are not arrays")
        return
    expect(len(meta_jobs) == len(public_jobs), errors, "job metadata count")
    generated = {"catalog_status", "asset_manifest", "assets"}
    expected_rows = [
        {key: value for key, value in row.items() if key not in generated}
        for row in public_jobs
    ]
    expect(meta_jobs == expected_rows, errors, "job metadata projection")
    expect(meta.get("exclusions") == catalog.get("exclusions"), errors, "job metadata exclusions")
    expect(
        meta.get("audit_receipt") == catalog.get("admission", {}).get("audit_receipt"),
        errors,
        "job metadata audit receipt",
    )
    expect(
        meta.get("hardening_receipt")
        == catalog.get("admission", {}).get("hardening_receipt"),
        errors,
        "job metadata hardening receipt",
    )
    verify_repo_identity(meta.get("audit_receipt"), "R2 admission receipt", errors)
    verify_repo_identity(meta.get("hardening_receipt"), "no-failure hardening receipt", errors)
    audit_projection = meta.get("audit_receipt", {}).get("public_projection", {})
    audit_path = ROOT / str(audit_projection.get("path", ""))
    try:
        global_audit, _ = load(audit_path)
    except (OSError, UnicodeError, json.JSONDecodeError, DuplicateKey, ValueError) as exc:
        errors.append(f"R2 admission receipt: cannot parse public projection: {exc}")
        global_audit = {}
    audit_rows = global_audit.get("rows") if isinstance(global_audit, dict) else None
    if not isinstance(audit_rows, list):
        errors.append("R2 admission receipt: rows missing")
        rows_by_packet: dict[str, dict[str, Any]] = {}
    else:
        expect(
            global_audit.get("schema") == "math-commons-packet-r2-admission/v1",
            errors,
            "R2 admission receipt schema",
        )
        expect(global_audit.get("row_count") == len(audit_rows), errors, "R2 audit row count")
        expect(global_audit.get("pass_count") == len(audit_rows), errors, "R2 audit pass count")
        expect(global_audit.get("fail_count") == 0, errors, "R2 audit fail count")
        expect(
            global_audit.get("nonmutating_packet_audit") is True
            and global_audit.get("published_or_promoted") is False,
            errors,
            "R2 audit boundary",
        )
        expected_release_assets = sum(
            len(job.get("assets", []))
            for job in public_jobs
            if isinstance(job, dict) and isinstance(job.get("assets"), list)
        ) + len(catalog.get("translation_kit", {}).get("assets", []))
        expected_release_bytes = sum(
            int(asset.get("zip_bytes", 0))
            for job in public_jobs
            if isinstance(job, dict)
            for asset in job.get("assets", [])
            if isinstance(asset, dict)
        ) + sum(
            int(asset.get("zip_bytes", 0))
            for asset in catalog.get("translation_kit", {}).get("assets", [])
            if isinstance(asset, dict)
        )
        expect(
            global_audit.get("local_release")
            == {
                "directory_recorded": False,
                "asset_count": expected_release_assets,
                "asset_bytes": expected_release_bytes,
                "zip_set_replay": "PASS",
                "remote_readback": "NOT_RUN",
            },
            errors,
            "R2 frozen local release replay",
        )
        packet_ids = [
            row.get("packet_id") for row in audit_rows if isinstance(row, dict)
        ]
        expect(len(packet_ids) == len(audit_rows), errors, "R2 audit malformed row")
        expect(len(packet_ids) == len(set(packet_ids)), errors, "R2 audit duplicate packet")
        expect(
            all(isinstance(row, dict) and row.get("overall") == "PASS" for row in audit_rows),
            errors,
            "R2 audit non-PASS row",
        )
        rows_by_packet = {
            str(row["packet_id"]): row
            for row in audit_rows
            if isinstance(row, dict) and isinstance(row.get("packet_id"), str)
        }
    meta_packet_ids = [
        str(job.get("packet_id")) for job in meta_jobs if isinstance(job, dict)
    ]
    expect(len(meta_packet_ids) == len(meta_jobs), errors, "R2 malformed metadata row")
    expect(
        len(meta_packet_ids) == len(set(meta_packet_ids)),
        errors,
        "R2 duplicate metadata packet",
    )
    expect(
        set(rows_by_packet) == set(meta_packet_ids),
        errors,
        "R2 admission packet projection",
    )
    validate_hardening_projection(meta, meta_packet_ids, errors)
    public_by_id = {
        str(job.get("id")): job for job in public_jobs if isinstance(job, dict)
    }
    for job in meta_jobs:
        if not isinstance(job, dict):
            continue
        job_id = str(job.get("id"))
        packet_id = job.get("packet_id")
        expect(job.get("audit_basis") == "global_receipt", errors, f"{job_id}: R2 audit basis")
        row = rows_by_packet.get(str(packet_id))
        if row is None:
            errors.append(f"{job_id}: missing R2 admission row")
            continue
        expect(job.get("status") == "PASS_GLOBAL_COLD_AUDIT", errors, f"{job_id}: R2 status")
        expect(row.get("job_id") == job_id, errors, f"{job_id}: R2 job identity")
        expect(row.get("direct_file_count") == job.get("source_files"), errors, f"{job_id}: R2 file count")
        expect(row.get("direct_total_bytes") == job.get("source_bytes"), errors, f"{job_id}: R2 byte count")
        expect(row.get("prompt_count") == job.get("prompt_count"), errors, f"{job_id}: R2 prompt count")
        public_job = public_by_id.get(job_id, {})
        expected_local_assets = [
            {
                "name": asset.get("name"),
                "bytes": asset.get("zip_bytes"),
                "sha256": asset.get("zip_sha256"),
                "source_files": asset.get("source_files"),
                "source_bytes": asset.get("source_bytes"),
                "crc_and_member_stream_replay": "PASS",
            }
            for asset in public_job.get("assets", [])
            if isinstance(asset, dict)
        ]
        expect(
            row.get("local_release_assets") == expected_local_assets,
            errors,
            f"{job_id}: R2 local ZIP replay projection",
        )
        authorities = job.get("authority")
        expect(
            isinstance(authorities, list)
            and row.get("authority_count") == len(authorities)
            and row.get("authority_identity_replay") == "PASS",
            errors,
            f"{job_id}: R2 authority replay projection",
        )
        for field in ("start_file", "prompt_file", "packet_manifest"):
            declared = job.get(field, {})
            row_identity = row.get(field, {})
            expect(
                isinstance(declared, dict)
                and isinstance(row_identity, dict)
                and row_identity.get("basename") == declared.get("basename")
                and row_identity.get("bytes") == declared.get("bytes")
                and row_identity.get("sha256") == declared.get("sha256"),
                errors,
                f"{job_id}: R2 {field} identity",
            )
        validation_receipt = job.get("validation_receipt")
        expect(
            isinstance(validation_receipt, dict)
            and validation_receipt.get("included_in_packet") is False
            and validation_receipt.get("public_projection")
            == meta.get("audit_receipt", {}).get("public_projection"),
            errors,
            f"{job_id}: R2 receipt binding",
        )
        manifest_path = ROOT / "catalog" / "assets" / f"{job_id}.json"
        try:
            asset_manifest, _ = load(manifest_path)
        except (OSError, UnicodeError, json.JSONDecodeError, DuplicateKey, ValueError) as exc:
            errors.append(f"{job_id}: cannot replay R2 snapshot against asset manifest: {exc}")
        else:
            members = asset_manifest.get("members")
            if not isinstance(members, list) or not all(isinstance(item, dict) for item in members):
                errors.append(f"{job_id}: asset members unavailable for R2 snapshot replay")
            else:
                expect(
                    row.get("direct_snapshot_sha256") == audit_snapshot_sha256(members),
                    errors,
                    f"{job_id}: R2 direct snapshot SHA-256",
                )
    expect(
        sum(row.get("source_files", 0) for row in meta_jobs)
        == catalog.get("admission", {}).get("source_files"),
        errors,
        "job metadata source-file aggregate",
    )
    expect(
        sum(row.get("source_bytes", 0) for row in meta_jobs)
        == catalog.get("admission", {}).get("source_bytes"),
        errors,
        "job metadata source-byte aggregate",
    )
    kit_assets = catalog.get("translation_kit", {}).get("assets", [])
    expected_kit_assets = [
        {
            "name": asset.get("name"),
            "bytes": asset.get("zip_bytes"),
            "sha256": asset.get("zip_sha256"),
            "source_files": asset.get("source_files"),
            "source_bytes": asset.get("source_bytes"),
            "crc_and_member_stream_replay": "PASS",
        }
        for asset in kit_assets
        if isinstance(asset, dict)
    ]
    expect(
        isinstance(global_audit, dict)
        and global_audit.get("translation_kit", {}).get("local_release_assets")
        == expected_kit_assets,
        errors,
        "R2 translation-kit local ZIP replay projection",
    )


def validate_jobs(
    asset_dir: Path | None, errors: list[str]
) -> tuple[int, int, int, int, int, int, int]:
    catalog_path = ROOT / "catalog" / "jobs.json"
    catalog, _ = load(catalog_path)
    validate_schema(catalog, "jobs", "job catalog", errors)
    expect(catalog.get("schema") == "math-commons-job-catalog/v2", errors, "job catalog schema")
    validate_job_meta(catalog, errors)
    jobs = catalog.get("jobs")
    if not isinstance(jobs, list) or not jobs:
        errors.append("job catalog has no jobs")
        return 0, 0, 0, 0, 0, 0
    expect(catalog.get("admission", {}).get("packet_count") == len(jobs), errors, "job catalog packet count")
    ids = [job.get("id") for job in jobs]
    expect(len(ids) == len(set(ids)), errors, "job IDs are not unique")
    expect(all(isinstance(item, str) and SLUG.fullmatch(item) for item in ids), errors, "job ID syntax")
    source_files = 0
    source_bytes = 0
    asset_count = 0
    asset_names: list[str] = []
    nested_authorities = 0
    release = catalog.get("release", {})
    release_tag = release.get("tag") if isinstance(release, dict) else None
    expect(
        isinstance(release_tag, str) and RELEASE_TAG.fullmatch(release_tag) is not None,
        errors,
        "job catalog release tag",
    )
    expect(
        isinstance(release, dict)
        and release.get("url")
        == f"https://github.com/KokunoYumeto/mathematics-commons-pilot/releases/tag/{release_tag}",
        errors,
        "job catalog release URL",
    )
    for job in jobs:
        if not isinstance(job, dict):
            errors.append("job catalog has a malformed job row")
            continue
        job_id = job["id"]
        expect(job.get("catalog_status") == "runnable", errors, f"{job_id}: status")
        expect(job.get("status") in ADMITTED_STATUSES, errors, f"{job_id}: terminal PASS status")
        expect(
            valid_prompt_count(job.get("prompt_count")),
            errors,
            f"{job_id}: prompt count",
        )
        expect(job.get("pack_scope") == "direct_files", errors, f"{job_id}: pack scope")
        identity = job.get("asset_manifest", {})
        expect(
            isinstance(identity, dict)
            and identity.get("path") == f"catalog/assets/{job_id}.json",
            errors,
            f"{job_id}: manifest path",
        )
        manifest_path = ROOT / str(identity.get("path", ""))
        manifest, data = validate_asset_manifest(manifest_path, job_id, errors)
        if not manifest:
            continue
        expect(identity.get("bytes") == len(data), errors, f"{job_id}: manifest bytes")
        expect(identity.get("sha256") == sha256(data), errors, f"{job_id}: manifest SHA-256")
        expect(job.get("source_files") == manifest.get("source_files"), errors, f"{job_id}: source files")
        expect(job.get("source_bytes") == manifest.get("source_bytes"), errors, f"{job_id}: source bytes")
        members_by_path = {
            str(row["path"]): row
            for row in manifest.get("members", [])
            if isinstance(row, dict) and isinstance(row.get("path"), str)
        }
        bind_job_control_members(job, members_by_path, errors)
        receipt = job.get("validation_receipt")
        if isinstance(receipt, dict) and receipt.get("included_in_packet", True) is False:
            basename = receipt.get("basename")
            expect(
                isinstance(basename, str) and basename not in members_by_path,
                errors,
                f"{job_id}: external receipt is unexpectedly a packet member",
            )
            verify_repo_identity(receipt, f"{job_id}: public validation receipt", errors)
            expect(
                binds_global_admission_projection(catalog, job, receipt),
                errors,
                f"{job_id}: global admission receipt projection",
            )
        else:
            bind_declared_member(
                members_by_path,
                receipt,
                f"{job_id}: validation receipt",
                errors,
            )
        authorities = job.get("authority")
        if not isinstance(authorities, list) or not authorities:
            errors.append(f"{job_id}: authority identities missing")
        else:
            for authority_index, authority in enumerate(authorities):
                if not isinstance(authority, dict) or not isinstance(authority.get("path"), str):
                    errors.append(f"{job_id}: malformed authority {authority_index}")
                    continue
                logical_path = authority["path"]
                levels = logical_path.split("!/")
                expect(
                    len(levels) in {1, 2}
                    and Path(levels[0]).name == levels[0]
                    and levels[0] in members_by_path,
                    errors,
                    f"{job_id}: authority outer member {authority_index}",
                )
                if len(levels) == 1 and levels[0] in members_by_path:
                    expect(
                        members_by_path[levels[0]].get("sha256") == authority.get("sha256"),
                        errors,
                        f"{job_id}: authority SHA-256 {authority_index}",
                    )
                if len(levels) == 2:
                    nested_authorities += 1
                    expect(
                        safe_path(levels[1])
                        and isinstance(authority.get("sha256"), str)
                        and HEX64.fullmatch(authority["sha256"]) is not None,
                        errors,
                        f"{job_id}: nested authority identity {authority_index}",
                    )
        public_assets = job.get("assets")
        expected_assets = []
        proposed_base = job.get("proposed_asset_base_name")
        expect(
            isinstance(proposed_base, str) and SLUG.fullmatch(proposed_base) is not None,
            errors,
            f"{job_id}: proposed asset basename",
        )
        for index, asset in enumerate(manifest["assets"], start=1):
            expected_name = (
                f"{proposed_base}.zip"
                if len(manifest["assets"]) == 1
                else f"{proposed_base}.part{index:02d}.zip"
            )
            expect(asset.get("name") == expected_name, errors, f"{job_id}: asset name {index}")
            row = dict(asset)
            row["url"] = f"https://github.com/KokunoYumeto/mathematics-commons-pilot/releases/download/{release_tag}/{asset['name']}"
            expected_assets.append(row)
        expect(public_assets == expected_assets, errors, f"{job_id}: public asset projection")
        source_files += manifest["source_files"]
        source_bytes += manifest["source_bytes"]
        asset_count += len(manifest["assets"])
        asset_names.extend(asset["name"] for asset in manifest["assets"])
        if asset_dir is not None:
            replay_zip(asset_dir, job_id, manifest, errors)
            for authority in authorities if isinstance(authorities, list) else []:
                if (
                    isinstance(authority, dict)
                    and isinstance(authority.get("path"), str)
                    and "!/" in authority["path"]
                ):
                    replay_nested_authority(asset_dir, job_id, manifest, authority, errors)

    kit = catalog.get("translation_kit", {})
    kit_identity = kit.get("asset_manifest", {})
    expect(
        isinstance(kit_identity, dict)
        and kit_identity.get("path") == "catalog/assets/translation-kit.json",
        errors,
        "translation kit manifest path",
    )
    kit_path = ROOT / str(kit_identity.get("path", ""))
    kit_manifest, kit_data = validate_asset_manifest(kit_path, "open-textbook-translation-kit", errors)
    if kit_manifest:
        expect(kit_identity.get("bytes") == len(kit_data), errors, "translation kit manifest bytes")
        expect(kit_identity.get("sha256") == sha256(kit_data), errors, "translation kit manifest hash")
        expected = []
        for asset in kit_manifest["assets"]:
            row = dict(asset)
            row["url"] = f"https://github.com/KokunoYumeto/mathematics-commons-pilot/releases/download/{release_tag}/{asset['name']}"
            expected.append(row)
        expect(kit.get("assets") == expected, errors, "translation kit public asset projection")
        asset_names.extend(asset["name"] for asset in kit_manifest["assets"])
        if asset_dir is not None:
            replay_zip(asset_dir, "open-textbook-translation-kit", kit_manifest, errors)
    expect(len(asset_names) == len(set(asset_names)), errors, "release asset names are not unique")
    if asset_dir is not None and asset_dir.is_dir():
        observed_assets = sorted(path.name for path in asset_dir.iterdir() if path.is_file())
        expect(
            observed_assets == sorted(asset_names),
            errors,
            "local release directory has missing or unexpected files",
        )
    admission = catalog.get("admission", {})
    expect(admission.get("source_files") == source_files, errors, "catalog source-file aggregate")
    expect(admission.get("source_bytes") == source_bytes, errors, "catalog source-byte aggregate")
    kit_assets = len(kit_manifest.get("assets", [])) if kit_manifest else 0
    kit_files = kit_manifest.get("source_files", 0) if kit_manifest else 0
    kit_source_bytes = kit_manifest.get("source_bytes", 0) if kit_manifest else 0
    release_asset_bytes = sum(
        asset["zip_bytes"] for job in jobs for asset in job.get("assets", [])
    ) + sum(asset["zip_bytes"] for asset in kit.get("assets", []))
    return (
        len(jobs),
        asset_count + kit_assets,
        source_files,
        source_bytes,
        release_asset_bytes,
        source_files + kit_files,
        nested_authorities,
    )


def validate_translations(errors: list[str]) -> int:
    catalog, _ = load(ROOT / "catalog" / "translations.json")
    validate_schema(catalog, "translations", "translation catalog", errors)
    if not isinstance(catalog, dict):
        errors.append("translation catalog root is not an object")
        return 0
    expect(
        catalog.get("schema") == "math-commons-translation-catalog/v8",
        errors,
        "translation catalog schema",
    )

    collection_names = (
        "topics",
        "works",
        "resources",
        "source_editions",
        "translation_editions",
        "jobs",
        "evidence",
    )
    collections: dict[str, list[dict]] = {}
    for name in collection_names:
        value = catalog.get(name)
        if not isinstance(value, list) or any(not isinstance(row, dict) for row in value):
            errors.append(f"translation {name} is not an object array")
            collections[name] = []
        else:
            collections[name] = value
    if not collections["works"]:
        errors.append("translation catalog has no works")
    if not collections["source_editions"]:
        errors.append("translation catalog has no source editions")

    maps: dict[str, dict[str, dict]] = {}
    for name, rows in collections.items():
        ids = [row.get("id") for row in rows]
        expect(
            all(isinstance(value, str) and SLUG.fullmatch(value) is not None for value in ids),
            errors,
            f"translation {name} semantic IDs",
        )
        expect(len(ids) == len(set(ids)), errors, f"translation {name} IDs are not unique")
        maps[name] = {
            str(row.get("id")): row
            for row in rows
            if isinstance(row.get("id"), str)
        }

    works = maps["works"]
    resources = maps["resources"]
    sources = maps["source_editions"]
    translations = maps["translation_editions"]
    jobs = maps["jobs"]
    evidence = maps["evidence"]
    topics = maps["topics"]
    expect(not (set(works) & set(resources)), errors, "translation work/resource IDs overlap")

    reader_receipt, _ = load(ROOT / "catalog" / "receipts" / "id-readers.json")
    reader_rows = reader_receipt.get("readers") if isinstance(reader_receipt, dict) else None
    if not isinstance(reader_rows, list) or any(not isinstance(row, dict) for row in reader_rows):
        errors.append("Indonesian reader receipt rows are malformed")
        reader_rows = []
    reader_by_id = {
        str(row.get("id")): row
        for row in reader_rows
        if isinstance(row.get("id"), str)
    }
    expect(
        reader_receipt.get("schema") == "math-commons-reader-receipt/v1"
        and reader_receipt.get("observed_at") == "2026-08-22T18:54:26Z"
        and reader_receipt.get("collection", {}).get("doi")
        == "10.6084/m9.figshare.c.8668413.v25"
        and reader_receipt.get("collection", {}).get("reader_count") == 9
        and reader_receipt.get("collection", {}).get("reader_bytes")
        == sum(int(row.get("bytes", 0)) for row in reader_rows)
        and len(reader_by_id) == len(reader_rows) == 9,
        errors,
        "Indonesian reader receipt boundary",
    )

    for evidence_id, row in evidence.items():
        if row.get("kind") != "same_commit_receipt":
            continue
        relative = row.get("path")
        safe = False
        receipt_path: Path | None = None
        if isinstance(relative, str) and "\\" not in relative:
            pure = PurePosixPath(relative)
            safe = not pure.is_absolute() and ".." not in pure.parts
            if safe:
                receipt_path = ROOT.joinpath(*pure.parts)
                try:
                    safe = receipt_path.resolve().is_relative_to(ROOT.resolve())
                except OSError:
                    safe = False
        expect(safe and receipt_path is not None, errors, f"translation evidence {evidence_id}: safe receipt path")
        if not safe or receipt_path is None:
            continue
        expect(receipt_path.is_file(), errors, f"translation evidence {evidence_id}: receipt exists")
        if not receipt_path.is_file():
            continue
        identity = input_identity(receipt_path)
        expect(
            row.get("bytes") == identity["bytes"]
            and row.get("sha256") == identity["sha256"],
            errors,
            f"translation evidence {evidence_id}: receipt identity",
        )
    expect(
        all(row.get("kind") in {"work", "series", "course", "source_project"} for row in works.values()),
        errors,
        "translation works contain resource kinds",
    )
    expect(
        all(row.get("kind") in {"adaptation", "component", "composite", "infrastructure", "reference"} for row in resources.values()),
        errors,
        "translation resources contain work kinds",
    )
    item_ids = set(works) | set(resources)

    topic_memberships: dict[str, list[str]] = {item_id: [] for item_id in item_ids}
    for topic_id, topic in topics.items():
        work_ids = topic.get("work_ids")
        resource_ids = topic.get("resource_ids")
        if not isinstance(work_ids, list) or not isinstance(resource_ids, list):
            errors.append(f"translation topic {topic_id}: malformed member arrays")
            continue
        expect(len(work_ids) == len(set(work_ids)), errors, f"translation topic {topic_id}: duplicate works")
        expect(len(resource_ids) == len(set(resource_ids)), errors, f"translation topic {topic_id}: duplicate resources")
        expect(set(work_ids).issubset(works), errors, f"translation topic {topic_id}: unknown works")
        expect(set(resource_ids).issubset(resources), errors, f"translation topic {topic_id}: unknown resources")
        for item_id in [*work_ids, *resource_ids]:
            if item_id in topic_memberships:
                topic_memberships[item_id].append(topic_id)
    expect(
        all(len(value) == 1 for value in topic_memberships.values()),
        errors,
        "every translation item must belong to exactly one topic",
    )

    source_ids_by_item: dict[str, list[str]] = {item_id: [] for item_id in item_ids}
    translation_ids_by_work: dict[str, list[str]] = {work_id: [] for work_id in works}
    job_ids_by_work: dict[str, list[str]] = {work_id: [] for work_id in works}
    check_names = {
        "work_identity",
        "source_edition_identity",
        "immutable_source",
        "translation_permission",
        "component_rights",
        "editable_source",
        "baseline_build",
    }
    for source_id, source in sources.items():
        item_id = source.get("item_id")
        item_type = source.get("item_type")
        expect(item_id in item_ids, errors, f"translation source {source_id}: item FK")
        expect(
            (item_type == "work" and item_id in works)
            or (item_type == "resource" and item_id in resources),
            errors,
            f"translation source {source_id}: item type",
        )
        if item_id in source_ids_by_item:
            source_ids_by_item[item_id].append(source_id)
        source_evidence = source.get("evidence_ids")
        expect(
            isinstance(source_evidence, list) and set(source_evidence).issubset(evidence),
            errors,
            f"translation source {source_id}: evidence FKs",
        )
        checks = source.get("evidence_checks")
        if not isinstance(checks, dict) or set(checks) != check_names:
            errors.append(f"translation source {source_id}: exact evidence checks")
            gate_states: list[str] = []
        else:
            gate_states = []
            for gate_name, row in checks.items():
                if not isinstance(row, dict):
                    errors.append(f"translation source {source_id}: malformed {gate_name} gate")
                    continue
                gate_states.append(str(row.get("state")))
                refs = row.get("evidence_ids")
                expect(
                    isinstance(refs, list) and refs and set(refs).issubset(evidence),
                    errors,
                    f"translation source {source_id}: {gate_name} evidence",
                )
        all_pass = len(gate_states) == len(check_names) and set(gate_states) == {"pass"}
        readiness = source.get("readiness")
        expect(
            readiness in {"identity_unresolved", "listed", "reference_only", "packet_prepared", "runnable"},
            errors,
            f"translation source {source_id}: readiness",
        )
        workflow_startability = source.get("workflow_startability")
        workflow_mode = source.get("workflow_mode")
        workflow_note = source.get("workflow_note")
        expect(
            workflow_startability in {"starter_available", "source_bound_packet", "reference_only"}
            and workflow_mode in {"generic_starter", "source_bound_packet", "reference_only"}
            and isinstance(workflow_note, str)
            and bool(workflow_note),
            errors,
            f"translation source {source_id}: workflow startability fields",
        )
        if source.get("item_type") == "resource" or readiness == "reference_only":
            expect(
                workflow_startability == "reference_only"
                and workflow_mode == "reference_only",
                errors,
                f"translation source {source_id}: reference workflow state",
            )
        elif readiness == "runnable":
            expect(
                workflow_startability == "source_bound_packet"
                and workflow_mode == "source_bound_packet",
                errors,
                f"translation source {source_id}: source-bound workflow state",
            )
        else:
            expect(
                workflow_startability == "starter_available"
                and workflow_mode == "generic_starter",
                errors,
                f"translation source {source_id}: generic workflow state",
            )
        if readiness in {"packet_prepared", "runnable"}:
            expect(all_pass, errors, f"translation source {source_id}: packet checks")
        if readiness in {"packet_prepared", "runnable"}:
            locator = source.get("locator")
            rights = source.get("rights")
            components = source.get("components")
            immutable_locator = False
            if isinstance(locator, dict):
                immutable_locator = (
                    isinstance(locator.get("url"), str)
                    and (
                        (
                            re.fullmatch(r"[0-9a-f]{40}", str(locator.get("commit")))
                            is not None
                            and re.fullmatch(r"[0-9a-f]{40}", str(locator.get("tree")))
                            is not None
                        )
                        or isinstance(locator.get("archive"), str)
                    )
                )
            license_row = rights.get("work_license") if isinstance(rights, dict) else None
            expect(
                source.get("identity_state") == "frozen"
                and immutable_locator
                and isinstance(rights, dict)
                and rights.get("state") == "verified_translation_allowed"
                and rights.get("derivative_translation_allowed") is True
                and isinstance(license_row, dict)
                and isinstance(license_row.get("name"), str)
                and isinstance(license_row.get("url"), str)
                and isinstance(license_row.get("scope"), str)
                and isinstance(rights.get("component_notices"), list)
                and isinstance(rights.get("evidence_ids"), list)
                and bool(rights.get("evidence_ids"))
                and set(rights.get("evidence_ids", [])).issubset(evidence)
                and isinstance(components, dict)
                and isinstance(components.get("included"), str)
                and isinstance(components.get("excluded"), str)
                and isinstance(components.get("receipt"), str),
                errors,
                f"translation source {source_id}: publication-ready source/rights/components",
            )
        if source.get("identity_state") == "frozen":
            locator = source.get("locator")
            rights = source.get("rights")
            expect(
                isinstance(locator, dict)
                and isinstance(locator.get("url"), str)
                and isinstance(locator.get("commit"), str)
                and re.fullmatch(r"[0-9a-f]{40}", locator["commit"]) is not None
                and isinstance(locator.get("tree"), str)
                and re.fullmatch(r"[0-9a-f]{40}", locator["tree"]) is not None,
                errors,
                f"translation source {source_id}: frozen source identity",
            )
            expect(
                isinstance(rights, dict)
                and rights.get("state") == "verified_translation_allowed"
                and rights.get("derivative_translation_allowed") is True,
                errors,
                f"translation source {source_id}: frozen rights",
            )

    for translation_id, edition in translations.items():
        work_id = edition.get("work_id")
        expect(work_id in works, errors, f"translation edition {translation_id}: work FK")
        if work_id in translation_ids_by_work:
            translation_ids_by_work[work_id].append(translation_id)
        source_id = edition.get("source_edition_id")
        expect(
            source_id is None
            or (
                source_id in sources
                and sources[source_id].get("item_type") == "work"
                and sources[source_id].get("item_id") == work_id
            ),
            errors,
            f"translation edition {translation_id}: source FK",
        )
        target = edition.get("target_language")
        expect(
            isinstance(target, dict)
            and isinstance(target.get("tag"), str)
            and isinstance(target.get("name"), str),
            errors,
            f"translation edition {translation_id}: target language",
        )
        edition_evidence = edition.get("evidence")
        if not isinstance(edition_evidence, dict):
            errors.append(f"translation edition {translation_id}: malformed evidence")
        else:
            refs = edition_evidence.get("evidence_ids")
            expect(
                isinstance(refs, list) and refs and set(refs).issubset(evidence),
                errors,
                f"translation edition {translation_id}: evidence FKs",
            )
            if edition.get("identity_state") == "unverified_report":
                expect(
                    edition.get("progress_state")
                    in {
                        "historical_report_active_at_recording",
                        "historical_report_complete_at_recording",
                        "historical_report_planned_at_recording",
                    }
                    and edition.get("review_state") == "unknown"
                    and edition_evidence.get("status") == "non_public_historical_report"
                    and edition_evidence.get("observed_at") is None
                    and edition_evidence.get("public_url") is None
                    and edition_evidence.get("commit") is None
                    and edition_evidence.get("tree") is None,
                    errors,
                    f"translation edition {translation_id}: unverified report boundary",
                )
            if edition.get("identity_state") == "public_repository_verified":
                expect(
                    edition.get("progress_state") == "repository_available"
                    and edition.get("review_state") == "not_independently_assessed"
                    and edition_evidence.get("status") == "public_repository_identity_verified"
                    and isinstance(edition_evidence.get("observed_at"), str)
                    and isinstance(edition_evidence.get("public_url"), str)
                    and re.fullmatch(r"[0-9a-f]{40}", str(edition_evidence.get("commit"))) is not None
                    and re.fullmatch(r"[0-9a-f]{40}", str(edition_evidence.get("tree"))) is not None,
                    errors,
                    f"translation edition {translation_id}: public repository evidence",
                )
            if edition.get("identity_state") == "public_edition_verified":
                expect(
                    edition.get("progress_state")
                    in {
                        "public_reader_available_scope_unassessed",
                        "verified_active",
                        "verified_complete",
                        "inactive",
                    }
                    and edition.get("review_state")
                    in {"not_independently_assessed", "in_review", "passed"}
                    and edition_evidence.get("status") == "public_bytes_verified"
                    and isinstance(edition_evidence.get("observed_at"), str)
                    and isinstance(edition_evidence.get("public_url"), str),
                    errors,
                    f"translation edition {translation_id}: public edition evidence",
                )
                if edition.get("progress_state") == "public_reader_available_scope_unassessed":
                    reader = reader_by_id.get(translation_id)
                    expect(
                        isinstance(reader, dict)
                        and reader.get("work_id") == work_id
                        and edition.get("review_state") == "not_independently_assessed"
                        and edition_evidence.get("observed_at")
                        == reader_receipt.get("observed_at")
                        and edition_evidence.get("recorded_at")
                        == reader_receipt.get("observed_at")
                        and edition_evidence.get("public_url")
                        == "https://doi.org/" + str(reader.get("doi"))
                        and edition_evidence.get("commit") is None
                        and edition_evidence.get("tree") is None
                        and edition_evidence.get("doi") == reader.get("doi")
                        and edition_evidence.get("file") == reader.get("file")
                        and edition_evidence.get("bytes") == reader.get("bytes")
                        and edition_evidence.get("sha256") == reader.get("sha256")
                        and edition_evidence.get("download_url")
                        == reader.get("download_url")
                        and edition_evidence.get("collection_doi")
                        == reader_receipt.get("collection", {}).get("doi")
                        and edition_evidence.get("receipt_path")
                        == "catalog/receipts/id-readers.json"
                        and edition_evidence.get("evidence_ids")
                        == ["figshare-id-readers-20260822"],
                        errors,
                        f"translation edition {translation_id}: exact public reader receipt",
                    )
            if edition.get("identity_state") == "frozen_complete":
                expect(
                    edition.get("source_edition_id") is not None
                    and edition.get("progress_state") in {"verified_complete", "inactive"}
                    and edition.get("review_state") == "passed"
                    and edition_evidence.get("status") == "public_bytes_verified"
                    and isinstance(edition_evidence.get("observed_at"), str)
                    and isinstance(edition_evidence.get("public_url"), str),
                    errors,
                    f"translation edition {translation_id}: frozen-complete evidence",
                )
    expect(
        {
            translation_id
            for translation_id, edition in translations.items()
            if edition.get("progress_state")
            == "public_reader_available_scope_unassessed"
        }
        == set(reader_by_id),
        errors,
        "Indonesian reader receipt/edition projection",
    )
    same_language: dict[tuple[str, str], list[str]] = {}
    for translation_id, edition in translations.items():
        target = edition.get("target_language")
        if isinstance(target, dict) and isinstance(target.get("tag"), str):
            same_language.setdefault((str(edition.get("work_id")), target["tag"].lower()), []).append(translation_id)
    for key, edition_ids in same_language.items():
        if len(edition_ids) > 1:
            for edition_id in edition_ids:
                overlap = translations[edition_id].get("overlap")
                expect(
                    isinstance(overlap, dict)
                    and overlap.get("mode") in {"declared_parallel", "supersedes", "superseded"}
                    and bool(set(overlap.get("related_edition_ids", [])) & (set(edition_ids) - {edition_id})),
                    errors,
                    f"translation edition {edition_id}: same-language overlap declaration",
                )

    for job_id, job in jobs.items():
        work_id = job.get("work_id")
        source_id = job.get("source_edition_id")
        expect(work_id in works, errors, f"translation job {job_id}: work FK")
        expect(
            source_id in sources
            and sources[source_id].get("item_id") == work_id
            and sources[source_id].get("item_type") == "work",
            errors,
            f"translation job {job_id}: source FK",
        )
        if work_id in job_ids_by_work:
            job_ids_by_work[work_id].append(job_id)
        refs = job.get("evidence_ids")
        expect(
            isinstance(refs, list) and refs and set(refs).issubset(evidence),
            errors,
            f"translation job {job_id}: evidence FKs",
        )
        referenced_receipts = {
            evidence[evidence_id].get("path")
            for evidence_id in refs or []
            if evidence_id in evidence
            and evidence[evidence_id].get("kind") == "same_commit_receipt"
        }
        expect(
            job.get("source_receipt") in referenced_receipts,
            errors,
            f"translation job {job_id}: source receipt is evidence-bound",
        )
        manifest_path = job.get("asset_manifest")
        manifest: dict[str, Any] = {}
        if isinstance(manifest_path, str):
            manifest, _ = validate_asset_manifest(ROOT / manifest_path, job_id, errors)
        member_paths = {
            str(row.get("path"))
            for row in manifest.get("members", [])
            if isinstance(row, dict) and isinstance(row.get("path"), str)
        }
        start_files = job.get("start_files")
        expect(
            isinstance(start_files, dict)
            and isinstance(start_files.get("local"), str)
            and isinstance(start_files.get("web"), str)
            and start_files.get("local") in member_paths
            and start_files.get("web") in member_paths,
            errors,
            f"translation job {job_id}: start files exist in packet manifest",
        )
        state = job.get("state")
        assets = job.get("assets")
        readback = job.get("public_readback")
        if state == "runnable":
            release_tag = job.get("release_tag")
            release_url = job.get("release_url")
            expected_release_url = (
                "https://github.com/KokunoYumeto/mathematics-commons-pilot/releases/tag/"
                + str(release_tag)
            )
            expected_assets = [
                {
                    "name": row.get("name"),
                    "bytes": row.get("zip_bytes"),
                    "sha256": row.get("zip_sha256"),
                    "url": (
                        "https://github.com/KokunoYumeto/mathematics-commons-pilot/releases/download/"
                        + str(release_tag)
                        + "/"
                        + str(row.get("name"))
                    ),
                }
                for row in manifest.get("assets", [])
                if isinstance(row, dict)
            ]
            expect(
                isinstance(release_tag, str)
                and release_url == expected_release_url
                and assets == expected_assets
                and bool(expected_assets)
                and isinstance(readback, dict)
                and readback.get("assets") == expected_assets
                and source_id in sources
                and sources[source_id].get("readiness") == "runnable",
                errors,
                f"translation job {job_id}: runnable public-readback contract",
            )
        elif state == "prepared_not_published":
            expect(
                job.get("release_tag") is None
                and job.get("release_url") is None
                and assets == []
                and readback is None
                and source_id in sources
                and sources[source_id].get("readiness") == "packet_prepared",
                errors,
                f"translation job {job_id}: prepared contract",
            )
        elif state == "retired":
            expect(
                isinstance(job.get("release_tag"), str)
                and isinstance(job.get("release_url"), str)
                and isinstance(assets, list)
                and bool(assets)
                and isinstance(readback, dict),
                errors,
                f"translation job {job_id}: retired-history contract",
            )

    for item_id, item in {**works, **resources}.items():
        expect(
            item.get("topic_ids") == topic_memberships[item_id],
            errors,
            f"translation item {item_id}: topic inverse",
        )
        expect(
            item.get("source_edition_ids") == source_ids_by_item[item_id],
            errors,
            f"translation item {item_id}: source inverse",
        )
        expected_translations = translation_ids_by_work[item_id] if item_id in works else []
        expected_jobs = job_ids_by_work[item_id] if item_id in works else []
        expect(
            item.get("translation_edition_ids") == expected_translations,
            errors,
            f"translation item {item_id}: edition inverse",
        )
        expect(
            item.get("job_ids") == expected_jobs,
            errors,
            f"translation item {item_id}: job inverse",
        )

    scope = catalog.get("scope")
    expect(
        isinstance(scope, dict)
        and scope.get("non_exhaustive") is True
        and scope.get("other_open_works_welcome") is True,
        errors,
        "translation catalog non-exclusive scope",
    )
    priority = catalog.get("language_priority")
    language_study = (
        priority.get("uis_96_language_study") if isinstance(priority, dict) else None
    )
    language_labels = (
        language_study.get("language_labels")
        if isinstance(language_study, dict)
        else None
    )
    expect(
        isinstance(priority, dict)
        and priority.get("any_language_welcome") is True
        and priority.get("unesco_fixed_translation_priority_list") is False
        and isinstance(priority.get("education_access_source"), dict)
        and isinstance(language_study, dict)
        and language_study.get("country_count") == 48
        and language_study.get("alphabetic_language_count") == 96
        and isinstance(language_labels, list)
        and len(language_labels) == 96
        and len(set(language_labels)) == 96,
        errors,
        "translation catalog language-priority contract",
    )
    choices, _ = load(ROOT / "kits" / "translate" / "WORKS.json")
    if not isinstance(choices, dict):
        errors.append("translation chooser root is not an object")
        return len(item_ids)
    validate_schema(choices, "translation_choices", "translation chooser", errors)
    expect(
        choices.get("schema") == "math-commons-translation-choices/v8",
        errors,
        "translation chooser schema",
    )
    expect(
        choices.get("language_priority") == priority,
        errors,
        "translation chooser language-priority projection",
    )
    catalog_identity = choices.get("catalog")
    expect(
        isinstance(catalog_identity, dict)
        and catalog_identity.get("path") == "catalog/translations.json"
        and catalog_identity.get("bytes") == TRANSLATE_V9_CATALOG_BYTES
        and catalog_identity.get("sha256") == TRANSLATE_V9_CATALOG_SHA256,
        errors,
        "translation chooser current catalog identity",
    )
    expect(
        choices.get("separate_archive") == catalog.get("separate_archive")
        and choices.get("jobs") == catalog.get("jobs"),
        errors,
        "translation chooser frozen archive/job projections",
    )

    choice_works = choices.get("works") if isinstance(choices.get("works"), list) else []
    choice_resources = (
        choices.get("resources") if isinstance(choices.get("resources"), list) else []
    )
    choice_sources = (
        choices.get("source_editions")
        if isinstance(choices.get("source_editions"), list)
        else []
    )
    choice_editions = (
        choices.get("translation_editions")
        if isinstance(choices.get("translation_editions"), list)
        else []
    )
    choice_work_ids = {
        str(row.get("id")) for row in choice_works if isinstance(row, dict)
    }
    choice_resource_ids = {
        str(row.get("id")) for row in choice_resources if isinstance(row, dict)
    }
    choice_source_ids = {
        str(row.get("id")) for row in choice_sources if isinstance(row, dict)
    }
    choice_edition_ids = {
        str(row.get("id")) for row in choice_editions if isinstance(row, dict)
    }
    expected_work_projection = [
        {
            "id": row["id"],
            "title": row["title"],
            "topic_ids": row["topic_ids"],
            "source_edition_ids": row["source_edition_ids"],
            "translation_edition_ids": [
                edition_id
                for edition_id in row["translation_edition_ids"]
                if edition_id in choice_edition_ids
            ],
            "job_ids": row["job_ids"],
        }
        for row in collections["works"]
        if row["id"] in choice_work_ids
    ]
    expected_resource_projection = [
        {
            "id": row["id"],
            "title": row["title"],
            "kind": row["kind"],
            "topic_ids": row["topic_ids"],
            "source_edition_ids": row["source_edition_ids"],
        }
        for row in collections["resources"]
        if row["id"] in choice_resource_ids
    ]
    expected_source_projection = [
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
        for row in collections["source_editions"]
        if row["id"] in choice_source_ids
    ]
    expected_translation_projection = [
        {
            "id": row["id"],
            "work_id": row["work_id"],
            "language": row["target_language"],
            "identity_state": row["identity_state"],
            "progress_state": row["progress_state"],
            "review_state": row["review_state"],
        }
        for row in collections["translation_editions"]
        if row["id"] in choice_edition_ids
    ]
    current_topics = {
        row["id"]: row for row in collections["topics"] if isinstance(row, dict)
    }
    choice_topics = choices.get("topics") if isinstance(choices.get("topics"), list) else []
    expected_topic_projection = [
        {
            "id": row["id"],
            "title": current_topics[row["id"]]["title"],
            "work_ids": [
                work_id
                for work_id in current_topics[row["id"]]["work_ids"]
                if work_id in choice_work_ids
            ],
            "resource_ids": [
                resource_id
                for resource_id in current_topics[row["id"]]["resource_ids"]
                if resource_id in choice_resource_ids
            ],
        }
        for row in choice_topics
        if isinstance(row, dict) and row.get("id") in current_topics
    ]
    expect(
        len(choice_topics) == len(expected_topic_projection)
        and choice_topics == expected_topic_projection,
        errors,
        "translation chooser frozen topic projection",
    )
    expect(
        choice_works == expected_work_projection,
        errors,
        "translation chooser frozen work projection",
    )
    expect(
        choice_resources == expected_resource_projection,
        errors,
        "translation chooser frozen resource projection",
    )
    expect(
        choice_sources == expected_source_projection,
        errors,
        "translation chooser frozen source projection",
    )
    expect(
        choice_editions == expected_translation_projection,
        errors,
        "translation chooser frozen edition projection",
    )

    generic_source, _ = load(ROOT / "kits" / "translate" / "SOURCE.json")
    openlogic_source_state, _ = load(ROOT / "kits" / "openlogic" / "SOURCE.json")
    openlogic_job_state, _ = load(ROOT / "kits" / "openlogic" / "JOB.json")
    openlogic_build_state, _ = load(ROOT / "kits" / "openlogic" / "BUILD.json")
    openlogic_receipt, _ = load(ROOT / "catalog" / "receipts" / "openlogic.json")
    validate_schema(generic_source, "translation_source", "generic translation source state", errors)
    validate_schema(openlogic_source_state, "translation_source", "Open Logic source state", errors)
    validate_schema(openlogic_build_state, "translation_build", "Open Logic embedded build receipt", errors)
    validate_schema(openlogic_receipt, "translation_build", "Open Logic admission receipt", errors)

    validate_openlogic_build(
        openlogic_build_state, "Open Logic embedded build receipt", errors
    )
    validate_openlogic_build(openlogic_receipt, "Open Logic admission receipt", errors)
    expect(
        generic_source.get("state") == "source_intake"
        and generic_source.get("work", {}).get("work_id") is None
        and generic_source.get("source", {}).get("commit") is None,
        errors,
        "generic translation work-selection boundary",
    )
    expect(
        openlogic_source_state.get("state") == "awaiting_target_selection"
        and openlogic_source_state.get("work", {}).get("work_id") == "openlogic-core"
        and openlogic_source_state.get("source", {}).get("commit") == "1e960beff9ed7835bf3e3f1335e21af3439cd107"
        and openlogic_source_state.get("source", {}).get("tree") == "45cad6b3bf0dd96985a7b3d1dc5c343984b0e1c8"
        and openlogic_source_state.get("source", {}).get("files") == 792
        and openlogic_source_state.get("source", {}).get("bytes") == 4_302_140,
        errors,
        "Open Logic translation source state",
    )
    final_binding = openlogic_receipt.get("packet_binding", {})
    manifest_identity = input_identity(ROOT / "catalog" / "assets" / "openlogic.json")
    expect(
        openlogic_job_state.get("state") == "source_packet_ready"
        and openlogic_build_state.get("state")
        == "cold_replay_pass_with_observed_warnings"
        and openlogic_receipt.get("state")
        == "cold_replay_pass_with_observed_warnings"
        and final_binding.get("state") == "cold_audit_input_replay_pass"
        and final_binding.get("asset_manifest")
        == {
            "name": "openlogic.json",
            "bytes": manifest_identity["bytes"],
            "sha256": manifest_identity["sha256"],
        }
        and final_binding.get("packet_zip")
        == {
            "name": "openlogic-v1.zip",
            "bytes": 1921531,
            "sha256": "C91EFD16C6DCF22DAEAFDBDC7F544A9E07C9B9C3BA04CE000BFCD933B52E9B8A",
            "members": 807,
        },
        errors,
        "Open Logic final admission binding",
    )

    openlogic = works.get("openlogic-core")
    openlogic_source = sources.get("openlogic-core-source")
    openlogic_job = jobs.get("openlogic-v1")
    expect(
        isinstance(openlogic, dict)
        and isinstance(openlogic_source, dict)
        and isinstance(openlogic_job, dict)
        and openlogic_source.get("locator", {}).get("commit") == "1e960beff9ed7835bf3e3f1335e21af3439cd107"
        and openlogic_source.get("locator", {}).get("tree") == "45cad6b3bf0dd96985a7b3d1dc5c343984b0e1c8",
        errors,
        "Open Logic exact source/job boundary",
    )
    portuguese = translations.get("openlogic-pt-openlogicpt")
    expect(
        isinstance(portuguese, dict)
        and portuguese.get("target_language", {}).get("tag") == "pt"
        and portuguese.get("target_language", {}).get("locale") is None
        and portuguese.get("source_edition_id") is None,
        errors,
        "Open Logic Portuguese claim boundary",
    )
    return len(item_ids)


def validate_formalization(errors: list[str]) -> int:
    catalog, _ = load(ROOT / "catalog" / "formalize.json")
    validate_schema(catalog, "formalization", "formalization intake", errors)
    expect(
        catalog.get("schema") == "math-commons-formalization-intake/v1",
        errors,
        "formalization intake schema",
    )
    expect(catalog.get("status") == "scaffold", errors, "formalization intake status")

    sources = catalog.get("sources")
    items = catalog.get("items")
    if not isinstance(sources, list) or not sources:
        errors.append("formalization intake has no sources")
        return 0
    if not isinstance(items, list) or not items:
        errors.append("formalization intake has no items")
        return 0

    source_ids = [row.get("id") for row in sources if isinstance(row, dict)]
    expect(len(source_ids) == len(sources), errors, "formalization source rows")
    expect(len(source_ids) == len(set(source_ids)), errors, "formalization source IDs")
    source_by_id = {
        row.get("id"): row for row in sources if isinstance(row, dict)
    }
    pass_states = {
        "default_target_replay_pass",
        "selected_files_replay_pass",
        "all_files_replay_pass",
    }

    for source in sources:
        if not isinstance(source, dict):
            continue
        source_id = source.get("id")
        prefix = f"formalization source {source_id}"
        expect(
            isinstance(source_id, str) and SLUG.fullmatch(source_id) is not None,
            errors,
            f"{prefix}: semantic ID",
        )
        expect(
            isinstance(source.get("url"), str) and source["url"].startswith("https://"),
            errors,
            f"{prefix}: HTTPS source URL",
        )
        snapshot = source.get("snapshot", {})
        kind = source.get("kind")
        if kind == "git_repository":
            expect(
                snapshot.get("state") == "inventoried"
                and isinstance(snapshot.get("commit"), str)
                and re.fullmatch(r"[0-9a-f]{40}", snapshot["commit"]) is not None
                and isinstance(snapshot.get("tree"), str)
                and re.fullmatch(r"[0-9a-f]{40}", snapshot["tree"]) is not None
                and snapshot.get("revision") == snapshot.get("commit")
                and snapshot.get("doi") is None
                and snapshot.get("concept_doi") is None
                and snapshot.get("version") is None
                and snapshot.get("publication_date") is None,
                errors,
                f"{prefix}: pinned Git snapshot",
            )
            expect(
                source.get("rights", {}).get("state") == "license_file_checked",
                errors,
                f"{prefix}: Git license evidence state",
            )
        elif kind == "zenodo_record":
            expect(
                snapshot.get("state") == "inventoried"
                and snapshot.get("commit") is None
                and snapshot.get("tree") is None
                and isinstance(snapshot.get("doi"), str)
                and snapshot.get("revision") == snapshot.get("doi")
                and isinstance(snapshot.get("concept_doi"), str)
                and isinstance(snapshot.get("version"), str)
                and isinstance(snapshot.get("publication_date"), str),
                errors,
                f"{prefix}: pinned Zenodo snapshot",
            )
            expect(
                source.get("rights", {}).get("state")
                == "license_metadata_checked",
                errors,
                f"{prefix}: Zenodo license evidence state",
            )
        else:
            errors.append(f"{prefix}: unknown source kind")

        rights = source.get("rights", {})
        expect(
            isinstance(rights.get("evidence"), str)
            and rights["evidence"].startswith("https://"),
            errors,
            f"{prefix}: HTTPS rights evidence",
        )
        inventory = source.get("inventory", {})
        files = inventory.get("files")
        lean_files = inventory.get("lean_files")
        expect(
            isinstance(files, int)
            and isinstance(lean_files, int)
            and 0 <= lean_files <= files,
            errors,
            f"{prefix}: Lean/source file counts",
        )
        archive = inventory.get("archive", {})
        expect(
            isinstance(archive.get("url"), str)
            and archive["url"].startswith("https://"),
            errors,
            f"{prefix}: HTTPS archive URL",
        )
        expect(
            archive.get("member_files") == files
            and archive.get("member_bytes") == inventory.get("bytes"),
            errors,
            f"{prefix}: archive member aggregate",
        )
        replay = archive.get("replay", {})
        verified = replay.get("verified_files")
        advertised = replay.get("advertised_files")
        exclusions = replay.get("excluded_members")
        expect(
            isinstance(verified, int)
            and isinstance(advertised, int)
            and verified == advertised
            and 0 <= verified <= archive.get("member_files", -1),
            errors,
            f"{prefix}: archive replay counts",
        )
        expect(
            isinstance(exclusions, list)
            and all(
                isinstance(row, dict) and safe_path(row.get("path"))
                for row in exclusions
            )
            and len({row.get("path") for row in exclusions if isinstance(row, dict)})
            == len(exclusions)
            and verified + len(exclusions) == archive.get("member_files"),
            errors,
            f"{prefix}: archive replay exclusions",
        )

        pins = source.get("toolchain", {}).get("other_pins")
        expect(
            isinstance(pins, list) and len(pins) == len(set(pins)),
            errors,
            f"{prefix}: dependency pins",
        )
        build = source.get("build", {})
        build_state = build.get("state")
        scope = build.get("scope")
        compiled = build.get("compiled_files")
        total_lean = build.get("total_lean_files")
        expect(total_lean == lean_files, errors, f"{prefix}: build source coverage")
        expect(
            isinstance(compiled, int)
            and isinstance(total_lean, int)
            and 0 <= compiled <= total_lean,
            errors,
            f"{prefix}: build compiled-file coverage",
        )
        expected_scope = {
            "not_run": "not_run",
            "default_target_replay_pass": "default_targets",
            "selected_files_replay_pass": "selected_files",
            "all_files_replay_pass": "all_lean_files",
        }.get(build_state)
        if expected_scope is not None:
            expect(scope == expected_scope, errors, f"{prefix}: build scope/state")
        if build_state in pass_states:
            expect(
                isinstance(build.get("evidence_date"), str)
                and isinstance(build.get("commands"), list)
                and bool(build["commands"]),
                errors,
                f"{prefix}: replay evidence",
            )
        if build_state == "all_files_replay_pass":
            expect(compiled == total_lean, errors, f"{prefix}: all-file replay coverage")
        if build_state == "default_target_replay_pass":
            expect(compiled < total_lean, errors, f"{prefix}: default-target partial coverage")
        for command in build.get("commands", []):
            if not isinstance(command, dict):
                errors.append(f"{prefix}: malformed build command")
                continue
            if command.get("result") == "pass":
                expect(command.get("exit_code") == 0, errors, f"{prefix}: passing command exit")
            else:
                expect(
                    isinstance(command.get("exit_code"), int)
                    and command.get("exit_code") != 0,
                    errors,
                    f"{prefix}: nonpassing command exit",
                )

        for field, tokens in (
            ("placeholders", {"sorry", "admit"}),
            ("trust_markers", {"axiom", "unsafe"}),
        ):
            scan = build.get(field, {})
            occurrences = scan.get("occurrences")
            count = scan.get("count")
            status = scan.get("status")
            expect(
                isinstance(occurrences, list) and count == len(occurrences),
                errors,
                f"{prefix}: {field} count",
            )
            expect(
                (status == "none_found" and count == 0)
                or (status == "present" and isinstance(count, int) and count > 0)
                or (
                    status == "not_assessed"
                    and count == 0
                    and scan.get("scan_scope") == "none"
                    and scan.get("scanned_files") == 0
                ),
                errors,
                f"{prefix}: {field} status",
            )
            expect(
                isinstance(scan.get("scanned_files"), int)
                and 0 <= scan.get("scanned_files", -1) <= lean_files,
                errors,
                f"{prefix}: {field} scan coverage",
            )
            if scan.get("scan_scope") == "all_source_files":
                expect(
                    scan.get("scanned_files") == lean_files,
                    errors,
                    f"{prefix}: {field} all-source coverage",
                )
            for occurrence in occurrences if isinstance(occurrences, list) else []:
                expect(
                    isinstance(occurrence, dict)
                    and safe_path(occurrence.get("path"))
                    and occurrence.get("token") in tokens,
                    errors,
                    f"{prefix}: {field} occurrence",
                )
        exclusions = build.get("excluded_modules")
        expect(
            isinstance(exclusions, list)
            and all(
                isinstance(row, dict) and safe_path(row.get("path"))
                for row in exclusions
            ),
            errors,
            f"{prefix}: excluded modules",
        )

    item_ids = [row.get("id") for row in items if isinstance(row, dict)]
    expect(len(item_ids) == len(items), errors, "formalization item rows")
    expect(len(item_ids) == len(set(item_ids)), errors, "formalization item IDs")
    for item in items:
        if not isinstance(item, dict):
            continue
        item_id = item.get("id")
        prefix = f"formalization item {item_id}"
        expect(
            isinstance(item_id, str) and SLUG.fullmatch(item_id) is not None,
            errors,
            f"{prefix}: semantic ID",
        )
        source = source_by_id.get(item.get("source_id"))
        expect(source is not None, errors, f"{prefix}: source reference")
        expect(safe_path(item.get("source_path")), errors, f"{prefix}: source path")
        declarations = item.get("declarations")
        expect(
            isinstance(declarations, list)
            and len(declarations) == len(set(declarations)),
            errors,
            f"{prefix}: declaration identities",
        )
        if item.get("evidence_kind") == "citation_only":
            expect(
                declarations == []
                and item.get("build_relation") == "citation_only"
                and item.get("placeholder_relation") == "citation_only"
                and item.get("intake_state") != "review_candidate",
                errors,
                f"{prefix}: citation-only boundary",
            )
        else:
            expect(bool(declarations), errors, f"{prefix}: named Lean declaration")
        if item.get("intake_state") == "review_candidate":
            expect(
                item.get("build_relation")
                in {"included_in_passing_build", "targeted_replay_pass"}
                and item.get("placeholder_relation") == "none_in_named_declarations",
                errors,
                f"{prefix}: review-candidate boundary",
            )
        if isinstance(source, dict):
            source_build = source.get("build", {})
            if item.get("build_relation") == "included_in_passing_build":
                expect(
                    source_build.get("state")
                    in {"default_target_replay_pass", "all_files_replay_pass"},
                    errors,
                    f"{prefix}: source build relation",
                )
                excluded_paths = {
                    row.get("path")
                    for row in source_build.get("excluded_modules", [])
                    if isinstance(row, dict)
                }
                expect(
                    item.get("source_path") not in excluded_paths,
                    errors,
                    f"{prefix}: excluded source module",
                )
            if item.get("build_relation") == "targeted_replay_pass":
                expect(
                    source_build.get("state")
                    in {"selected_files_replay_pass", "all_files_replay_pass"},
                    errors,
                    f"{prefix}: targeted source build relation",
                )

        correspondence = item.get("statement_correspondence", {})
        correspondence_state = correspondence.get("state")
        correspondence_evidence = correspondence.get("evidence")
        if correspondence_state in {"reviewed_match", "reviewed_mismatch"}:
            expect(
                isinstance(correspondence_evidence, list)
                and bool(correspondence_evidence),
                errors,
                f"{prefix}: statement-review evidence",
            )
        audit = item.get("mathlib_audit", {})
        audit_state = audit.get("state")
        if audit_state == "not_started":
            expect(
                audit.get("commit") is None
                and audit.get("relation") == "unassessed"
                and audit.get("evidence") == [],
                errors,
                f"{prefix}: unopened Mathlib audit",
            )
        elif audit_state in {"in_progress", "complete"}:
            expect(
                isinstance(audit.get("commit"), str)
                and re.fullmatch(r"[0-9a-f]{40}", audit["commit"]) is not None,
                errors,
                f"{prefix}: pinned Mathlib audit",
            )
        if audit_state == "complete":
            expect(
                audit.get("relation") != "unassessed"
                and isinstance(audit.get("evidence"), list)
                and bool(audit["evidence"]),
                errors,
                f"{prefix}: completed Mathlib audit evidence",
            )
        packet = item.get("packet", {})
        packet_state = packet.get("state")
        if packet_state == "not_started":
            expect(
                packet.get("asset") is None and packet.get("readback") is None,
                errors,
                f"{prefix}: unopened packet",
            )
        if packet_state == "runnable":
            asset = packet.get("asset")
            expect(
                correspondence_state == "reviewed_match"
                and audit_state == "complete"
                and item.get("placeholder_relation") == "none_in_named_declarations"
                and item.get("build_relation")
                in {"included_in_passing_build", "targeted_replay_pass"}
                and isinstance(asset, dict)
                and isinstance(asset.get("url"), str)
                and asset["url"].startswith("https://")
                and isinstance(packet.get("readback"), str)
                and packet["readback"].startswith("https://"),
                errors,
                f"{prefix}: runnable admission gate",
            )

    summary = catalog.get("summary", {})
    expected_summary = {
        "sources": len(sources),
        "items": len(items),
        "runnable_packets": sum(
            1 for item in items if item.get("packet", {}).get("state") == "runnable"
        ),
        "build_replay_pass_sources": sum(
            1 for source in sources if source.get("build", {}).get("state") in pass_states
        ),
        "placeholder_scan_clean_sources": sum(
            1
            for source in sources
            if source.get("build", {}).get("placeholders", {}).get("status")
            == "none_found"
        ),
        "statement_reviews_complete": sum(
            1
            for item in items
            if item.get("statement_correspondence", {}).get("state")
            in {"reviewed_match", "reviewed_mismatch"}
        ),
        "mathlib_audits_complete": sum(
            1 for item in items if item.get("mathlib_audit", {}).get("state") == "complete"
        ),
    }
    expect(summary == expected_summary, errors, "formalization summary projection")
    return len(items)


def portal_has_release(catalog: dict[str, Any], tag: str) -> bool:
    for section in catalog.get("sections", []):
        if not isinstance(section, dict):
            continue
        for key in ("release", "starter"):
            release = section.get(key)
            if isinstance(release, dict) and release.get("tag") == tag:
                return True
    return False


def portal_requires_translation_readback(catalog: dict[str, Any]) -> bool:
    if catalog.get("schema") == "math-commons-portal-catalog/v2":
        return True
    return (
        portal_has_release(catalog, "translate-v7")
        or portal_has_release(catalog, "translate-v8")
        or portal_has_release(catalog, TRANSLATE_V9_TAG)
    )


def portal_requires_v7_readback(catalog: dict[str, Any]) -> bool:
    """Whether the immutable v7 readback is the declared current starter."""
    return portal_has_release(catalog, "translate-v7")


def portal_requires_v8_readback(catalog: dict[str, Any]) -> bool:
    """Whether the v8 starter is the declared current starter."""
    return portal_has_release(catalog, "translate-v8")


def portal_requires_v9_readback(catalog: dict[str, Any]) -> bool:
    """Whether the v9 starter is the declared current starter."""
    return portal_has_release(catalog, TRANSLATE_V9_TAG)


def validate_portals_v1(
    catalog: dict[str, Any], data: bytes, errors: list[str]
) -> int:
    expect(
        len(data) == PORTAL_V1_BYTES and sha256(data) == PORTAL_V1_SHA256,
        errors,
        "legacy portal catalog frozen identity",
    )
    v7_readback = ROOT / "catalog" / "translate-rb-v7.json"
    expect(
        not v7_readback.exists() and not v7_readback.is_symlink(),
        errors,
        "legacy portal catalog has no undeclared v7 readback",
    )
    sections = catalog.get("sections")
    if not isinstance(sections, list):
        errors.append("portal catalog sections are not an array")
        return 0
    expect(
        [row.get("id") for row in sections if isinstance(row, dict)]
        == ["transcription", "translation", "open-problems"],
        errors,
        "portal catalog exact section order",
    )
    for row in sections:
        if not isinstance(row, dict):
            errors.append("portal catalog has a malformed section")
            continue
        docs = row.get("docs")
        expect(
            isinstance(docs, str) and (ROOT / docs).is_file(),
            errors,
            f"portal {row.get('id')}: documentation path",
        )
        catalog_path = row.get("catalog")
        expect(
            catalog_path is None
            or (isinstance(catalog_path, str) and (ROOT / catalog_path).is_file()),
            errors,
            f"portal {row.get('id')}: catalog path",
        )
        supplementary_catalogs = row.get("supplementary_catalogs", [])
        expect(
            isinstance(supplementary_catalogs, list)
            and all(
                isinstance(path, str) and (ROOT / path).is_file()
                for path in supplementary_catalogs
            ),
            errors,
            f"portal {row.get('id')}: supplementary catalog paths",
        )

    by_id = {
        row.get("id"): row for row in sections if isinstance(row, dict)
    }
    jobs_catalog, _ = load(ROOT / "catalog" / "jobs.json")
    transcription = by_id.get("transcription", {})
    trans_release = transcription.get("release", {})
    packet_assets = [
        asset
        for job in jobs_catalog.get("jobs", [])
        if isinstance(job, dict)
        for asset in job.get("assets", [])
        if isinstance(asset, dict)
    ]
    expect(
        trans_release.get("asset_count") == len(packet_assets),
        errors,
        "portal transcription asset count",
    )
    expect(
        trans_release.get("asset_bytes")
        == sum(int(asset.get("zip_bytes", 0)) for asset in packet_assets),
        errors,
        "portal transcription asset bytes",
    )

    translation = by_id.get("translation", {})
    translate_release = translation.get("release", {})
    translate_manifest, _ = validate_asset_manifest(
        ROOT / "catalog" / "assets" / "translate-v6.json",
        "translation-starter-v6",
        errors,
    )
    expected_translate_assets = [
        {
            "name": asset.get("name"),
            "bytes": asset.get("zip_bytes"),
            "sha256": asset.get("zip_sha256"),
        }
        for asset in translate_manifest.get("assets", [])
        if isinstance(asset, dict)
    ]
    expect(
        translate_release.get("assets") == expected_translate_assets,
        errors,
        "portal translation asset projection",
    )
    expect(
        translate_release.get("asset_count") == len(expected_translate_assets),
        errors,
        "portal translation asset count",
    )
    expect(
        translate_release.get("asset_bytes")
        == sum(int(asset["bytes"]) for asset in expected_translate_assets),
        errors,
        "portal translation asset bytes",
    )
    expect(
        translation.get("state") == "starter_available"
        and translation.get("catalog") == "catalog/translations.json"
        and translate_release.get("tag") == "translate-v6"
        and translate_release.get("url")
        == "https://github.com/KokunoYumeto/mathematics-commons-pilot/releases/tag/translate-v6"
        and translate_release.get("asset_catalog")
        == "catalog/assets/translate-v6.json"
        and translate_release.get("readback") == "catalog/translate-rb-v6.json",
        errors,
        "portal translation release contract",
    )

    translate_readback, _ = load(ROOT / "catalog" / "translate-rb-v6.json")
    validate_schema(
        translate_readback,
        "portal_readback",
        "translation starter public readback",
        errors,
    )
    expect(
        translate_readback.get("release")
        == {
            "id": 374661017,
            "tag": "translate-v6",
            "url": "https://github.com/KokunoYumeto/mathematics-commons-pilot/releases/tag/translate-v6",
            "target_commit": "5ffcef8dcc239566955a41a12c2a29246d23c427",
            "target_tree": "255b4a71be675e82ff98ea748a1a831000b26be9",
        },
        errors,
        "translation starter readback subject",
    )
    expect(
        translate_readback.get("assets")
        == [
            {
                "id": 524223289,
                "name": "translation-starter-v6.zip",
                "url": "https://github.com/KokunoYumeto/mathematics-commons-pilot/releases/download/translate-v6/translation-starter-v6.zip",
                "expected_bytes": 15520,
                "observed_bytes": 15520,
                "expected_sha256": "3DE94A6D0D9AF6D1568FC391C729A8AAA37C48D9974967B7E24FDCA0D0C65787",
                "observed_sha256": "3DE94A6D0D9AF6D1568FC391C729A8AAA37C48D9974967B7E24FDCA0D0C65787",
                "match": True,
            }
        ],
        errors,
        "translation starter readback exact asset",
    )
    expect(
        [
            {
                "name": row.get("name"),
                "bytes": row.get("observed_bytes"),
                "sha256": row.get("observed_sha256"),
            }
            for row in translate_readback.get("assets", [])
            if isinstance(row, dict)
        ]
        == expected_translate_assets,
        errors,
        "translation starter readback asset projection",
    )
    expect(
        translate_readback.get("status") == "PASS"
        and translate_readback.get("transport")
        == {
            "method": "anonymous_https",
            "authorization": False,
            "cookies": False,
            "payload_persisted": False,
        }
        and translate_readback.get("summary")
        == {
            "assets": 1,
            "bytes": 15520,
            "matches": 1,
            "mismatches": 0,
            "errors": [],
        },
        errors,
        "translation starter readback result",
    )

    expect(
        transcription.get("state") == "runnable"
        and transcription.get("catalog") == "catalog/jobs.json"
        and trans_release.get("tag") == "jobs-2026-08-21-r2"
        and trans_release.get("url")
        == "https://github.com/KokunoYumeto/mathematics-commons-pilot/releases/tag/jobs-2026-08-21-r2"
        and trans_release.get("asset_catalog") == "catalog/jobs.json"
        and trans_release.get("readback") == "catalog/readback-r2.json",
        errors,
        "portal transcription release contract",
    )

    problems = by_id.get("open-problems", {})
    problem_release = problems.get("release", {})
    expect(
        problem_release
        == {
            "tag": None,
            "url": None,
            "asset_count": 0,
            "asset_bytes": 0,
            "asset_catalog": None,
            "readback": None,
            "assets": [],
        },
        errors,
        "portal Workbench publication state",
    )
    expect(
        problems.get("state") == "source_recovery_required"
        and problems.get("catalog") is None,
        errors,
        "portal Workbench recovery state",
    )
    expect(
        problems.get("expected_asset")
        == {
            "name": "Mathematical_Commons_Open_Problem_Workbench_v0.2_2026-08-21.zip",
            "bytes": 13308489,
            "sha256": "A087B8A9765476F7DC26B00280299153D3BE46A536C698035445AF723451BD2A",
        },
        errors,
        "portal Workbench expected asset identity",
    )
    return len(sections)


def validate_portals(errors: list[str]) -> int:
    catalog, data = load(ROOT / "catalog" / "portals.json")
    validate_schema(catalog, "portals", "portal catalog", errors)
    if catalog.get("schema") == "math-commons-portal-catalog/v1":
        return validate_portals_v1(catalog, data, errors)
    expect(
        catalog.get("schema") == "math-commons-portal-catalog/v2",
        errors,
        "portal catalog schema",
    )
    sections = catalog.get("sections")
    if not isinstance(sections, list):
        errors.append("portal catalog sections are not an array")
        return 0
    expect(
        [row.get("id") for row in sections if isinstance(row, dict)]
        == ["transcription", "translation", "open-problems"],
        errors,
        "portal catalog exact section order",
    )
    for row in sections:
        if not isinstance(row, dict):
            errors.append("portal catalog has a malformed section")
            continue
        docs = row.get("docs")
        expect(
            isinstance(docs, str) and (ROOT / docs).is_file(),
            errors,
            f"portal {row.get('id')}: documentation path",
        )
        catalog_path = row.get("catalog")
        expect(
            catalog_path is None
            or (isinstance(catalog_path, str) and (ROOT / catalog_path).is_file()),
            errors,
            f"portal {row.get('id')}: catalog path",
        )
        supplementary_catalogs = row.get("supplementary_catalogs", [])
        expect(
            isinstance(supplementary_catalogs, list)
            and all(
                isinstance(path, str) and (ROOT / path).is_file()
                for path in supplementary_catalogs
            ),
            errors,
            f"portal {row.get('id')}: supplementary catalog paths",
        )

    by_id = {
        row.get("id"): row for row in sections if isinstance(row, dict)
    }
    jobs_catalog, _ = load(ROOT / "catalog" / "jobs.json")
    transcription = by_id.get("transcription", {})
    trans_release = transcription.get("release", {})
    packet_assets = [
        asset
        for job in jobs_catalog.get("jobs", [])
        if isinstance(job, dict)
        for asset in job.get("assets", [])
        if isinstance(asset, dict)
    ]
    transcription_readback, _ = load(ROOT / "catalog" / "readback-r2.json")
    release_assets = [
        asset
        for asset in transcription_readback.get("assets", [])
        if isinstance(asset, dict)
    ]
    expect(
        trans_release.get("asset_count") == len(release_assets),
        errors,
        "portal transcription total release asset count",
    )
    expect(
        trans_release.get("asset_bytes")
        == sum(int(asset.get("observed_bytes", 0)) for asset in release_assets),
        errors,
        "portal transcription total release asset bytes",
    )
    expect(
        trans_release.get("runnable_asset_count") == len(packet_assets),
        errors,
        "portal transcription runnable asset count",
    )
    expect(
        trans_release.get("runnable_asset_bytes")
        == sum(int(asset.get("zip_bytes", 0)) for asset in packet_assets),
        errors,
        "portal transcription runnable asset bytes",
    )

    def validate_portal_release(
        release: dict,
        *,
        label: str,
        tag: str,
        manifest_path: str,
        job_id: str,
        readback_path: str,
    ) -> tuple[list[dict[str, object]], dict]:
        manifest, _ = validate_asset_manifest(ROOT / manifest_path, job_id, errors)
        expected_assets = [
            {
                "name": asset.get("name"),
                "bytes": asset.get("zip_bytes"),
                "sha256": asset.get("zip_sha256"),
            }
            for asset in manifest.get("assets", [])
            if isinstance(asset, dict)
        ]
        release_url = (
            "https://github.com/KokunoYumeto/mathematics-commons-pilot/releases/tag/"
            + tag
        )
        expect(
            release.get("tag") == tag
            and release.get("url") == release_url
            and re.fullmatch(r"[0-9a-f]{40}", str(release.get("target_commit")))
            is not None
            and re.fullmatch(r"[0-9a-f]{40}", str(release.get("target_tree")))
            is not None
            and release.get("asset_catalog") == manifest_path
            and release.get("readback") == readback_path
            and release.get("assets") == expected_assets
            and release.get("asset_count") == len(expected_assets)
            and release.get("asset_bytes")
            == sum(int(asset["bytes"]) for asset in expected_assets),
            errors,
            f"{label} release projection",
        )
        readback_file = ROOT / readback_path
        if not readback_file.is_file():
            errors.append(f"{label} public readback is missing: {readback_path}")
            return expected_assets, {}
        readback, _ = load(readback_file)
        validate_schema(readback, "portal_readback", f"{label} public readback", errors)
        readback_release = readback.get("release", {})
        observed_date_ok = re.fullmatch(
            r"\d{4}-\d{2}-\d{2}", str(readback.get("observed_date"))
        ) is not None
        if tag in {"translate-v8", TRANSLATE_V9_TAG}:
            observed_date_ok = (
                observed_date_ok
                and isinstance(catalog.get("updated"), str)
                and readback.get("observed_date") <= catalog.get("updated")
            )
        else:
            # Older release readbacks are immutable historical observations and
            # need not be rewritten when the portal catalog advances.
            observed_date_ok = observed_date_ok and readback.get("observed_date") == READBACK_DATE
        expect(
            readback_release.get("tag") == tag
            and readback_release.get("url") == release_url
            and readback_release.get("target_commit") == release.get("target_commit")
            and readback_release.get("target_tree") == release.get("target_tree")
            and observed_date_ok,
            errors,
            f"{label} readback subject",
        )
        expected_readback_assets = [
            {
                "name": asset["name"],
                "url": (
                    "https://github.com/KokunoYumeto/mathematics-commons-pilot/releases/download/"
                    + tag
                    + "/"
                    + str(asset["name"])
                ),
                "expected_bytes": asset["bytes"],
                "observed_bytes": asset["bytes"],
                "expected_sha256": asset["sha256"],
                "observed_sha256": asset["sha256"],
                "match": True,
            }
            for asset in expected_assets
        ]
        expect(
            [
                {
                    "name": row.get("name"),
                    "url": row.get("url"),
                    "expected_bytes": row.get("expected_bytes"),
                    "observed_bytes": row.get("observed_bytes"),
                    "expected_sha256": row.get("expected_sha256"),
                    "observed_sha256": row.get("observed_sha256"),
                    "match": row.get("match"),
                }
                for row in readback.get("assets", [])
                if isinstance(row, dict)
            ]
            == expected_readback_assets,
            errors,
            f"{label} readback asset projection",
        )
        expect(
            readback.get("status") == "PASS"
            and readback.get("transport", {}).get("method")
            in {"anonymous_https", "anonymous_https_and_git"}
            and readback.get("transport", {}).get("authorization") is False
            and readback.get("transport", {}).get("cookies") is False
            and readback.get("transport", {}).get("payload_persisted") is False
            and readback.get("summary")
            == {
                "assets": len(expected_assets),
                "bytes": sum(int(asset["bytes"]) for asset in expected_assets),
                "matches": len(expected_assets),
                "mismatches": 0,
                "errors": [],
            },
            errors,
            f"{label} readback result",
        )
        return expected_assets, readback

    translation = by_id.get("translation", {})
    openlogic_release = translation.get("release", {})
    starter_release = translation.get("starter", {})
    expected_openlogic_assets, openlogic_readback = validate_portal_release(
        openlogic_release,
        label="Open Logic translation job",
        tag="translate-openlogic-v1",
        manifest_path="catalog/assets/openlogic.json",
        job_id="openlogic-v1",
        readback_path="catalog/openlogic-rb.json",
    )
    starter_specs = {
        "translate-v8": (
            "catalog/assets/translate-v8.json",
            "translation-starter-v8",
            "catalog/translate-rb-v8.json",
        ),
        "translate-v9-corrected": (
            "catalog/assets/translate-v9.json",
            "translation-starter-v9",
            "catalog/translate-rb-v9.json",
        ),
        "translate-v9-complete": (
            "catalog/assets/translate-v9-complete.json",
            "translation-starter-v9",
            "catalog/translate-rb-v9-complete.json",
        ),
        TRANSLATE_V9_TAG: (
            "catalog/assets/translate-v9-complete.json",
            "translation-starter-v9",
            "catalog/translate-rb-v9-final.json",
        ),
    }
    starter_tag = starter_release.get("tag")
    if starter_tag not in starter_specs:
        errors.append("generic translation starter tag is not supported")
        expected_starter_assets = []
    else:
        starter_manifest, starter_job, starter_readback_path = starter_specs[starter_tag]
        expected_starter_assets, _ = validate_portal_release(
            starter_release,
            label="generic translation starter",
            tag=starter_tag,
            manifest_path=starter_manifest,
            job_id=starter_job,
            readback_path=starter_readback_path,
        )
    expect(
        translation.get("state") == "runnable"
        and translation.get("catalog") == "catalog/translations.json"
        and translation.get("supplementary_catalogs") == ["catalog/edu.json"]
        and openlogic_release.get("admission_receipt")
        == "catalog/receipts/openlogic.json"
        and starter_release.get("admission_receipt") is None,
        errors,
        "portal translation two-release contract",
    )
    expect(
        starter_release.get("workflow_state") == "runnable_workflow"
        and isinstance(starter_release.get("workflow_note"), str)
        and starter_release.get("workflow_note"),
        errors,
        "generic translation starter workflow contract",
    )
    translation_catalog, _ = load(ROOT / "catalog" / "translations.json")
    openlogic_job = next(
        (
            row
            for row in translation_catalog.get("jobs", [])
            if isinstance(row, dict) and row.get("id") == "openlogic-v1"
        ),
        {},
    )
    expect(
        openlogic_job.get("state") == "runnable"
        and openlogic_job.get("release_tag") == "translate-openlogic-v1"
        and openlogic_job.get("release_url") == openlogic_release.get("url")
        and [
            {
                "name": row.get("name"),
                "bytes": row.get("bytes"),
                "sha256": row.get("sha256"),
            }
            for row in openlogic_job.get("assets", [])
            if isinstance(row, dict)
        ]
        == expected_openlogic_assets
        and next(
            (
                row.get("url")
                for row in openlogic_job.get("assets", [])
                if isinstance(row, dict)
            ),
            None,
        )
        == "https://github.com/KokunoYumeto/mathematics-commons-pilot/releases/download/translate-openlogic-v1/openlogic-v1.zip"
        and openlogic_job.get("asset_manifest") == "catalog/assets/openlogic.json"
        and openlogic_job.get("source_receipt") == "catalog/receipts/openlogic.json"
        and openlogic_job.get("public_readback", {}).get("receipt")
        == "catalog/openlogic-rb.json"
        and [
            {
                "name": row.get("name"),
                "bytes": row.get("bytes"),
                "sha256": row.get("sha256"),
            }
            for row in openlogic_job.get("public_readback", {}).get("assets", [])
            if isinstance(row, dict)
        ]
        == expected_openlogic_assets
        and [
            {
                "name": row.get("name"),
                "bytes": row.get("observed_bytes"),
                "sha256": row.get("observed_sha256"),
            }
            for row in openlogic_readback.get("assets", [])
            if isinstance(row, dict)
        ]
        == expected_openlogic_assets,
        errors,
        "Open Logic catalog-to-public-release binding",
    )

    expect(
        transcription.get("state") == "runnable"
        and transcription.get("catalog") == "catalog/jobs.json"
        and trans_release.get("tag") == "jobs-2026-08-21-r2"
        and trans_release.get("url")
        == "https://github.com/KokunoYumeto/mathematics-commons-pilot/releases/tag/jobs-2026-08-21-r2"
        and trans_release.get("asset_catalog") == "catalog/jobs.json"
        and trans_release.get("readback") == "catalog/readback-r2.json",
        errors,
        "portal transcription release contract",
    )

    problems = by_id.get("open-problems", {})
    problem_release = problems.get("release", {})
    expect(
        problem_release
        == {
            "tag": None,
            "url": None,
            "asset_count": 0,
            "asset_bytes": 0,
            "asset_catalog": None,
            "readback": None,
            "assets": [],
        },
        errors,
        "portal Workbench publication state",
    )
    expect(
        problems.get("state") == "source_recovery_required"
        and problems.get("catalog") is None,
        errors,
        "portal Workbench recovery state",
    )
    expect(
        problems.get("expected_asset")
        == {
            "name": "Mathematical_Commons_Open_Problem_Workbench_v0.2_2026-08-21.zip",
            "bytes": 13308489,
            "sha256": "A087B8A9765476F7DC26B00280299153D3BE46A536C698035445AF723451BD2A",
        },
        errors,
        "portal Workbench expected asset identity",
    )
    return len(sections)


def expected_readback_assets(catalog: dict[str, Any]) -> list[dict[str, Any]]:
    assets: list[dict[str, Any]] = []
    sources = [
        job.get("assets", [])
        for job in catalog.get("jobs", [])
        if isinstance(job, dict)
    ]
    kit = catalog.get("translation_kit", {})
    if isinstance(kit, dict):
        sources.append(kit.get("assets", []))
    for source in sources:
        if not isinstance(source, list):
            continue
        for asset in source:
            if not isinstance(asset, dict):
                continue
            assets.append(
                {
                    "name": asset.get("name"),
                    "url": asset.get("url"),
                    "expected_bytes": asset.get("zip_bytes"),
                    "observed_bytes": asset.get("zip_bytes"),
                    "expected_sha256": asset.get("zip_sha256"),
                    "observed_sha256": asset.get("zip_sha256"),
                    "match": True,
                }
            )
    return assets


def expected_readback_raw_files() -> list[dict[str, Any]]:
    base = (
        "https://raw.githubusercontent.com/"
        f"{READBACK_REPOSITORY}/{READBACK_COMMIT}/"
    )
    return [
        {
            "path": path,
            "name": PurePosixPath(path).name,
            "url": f"{base}{path}",
            "expected_bytes": size,
            "observed_bytes": size,
            "expected_sha256": digest,
            "observed_sha256": digest,
            "match": True,
        }
        for path, size, digest in READBACK_RAW_FILES
    ]


def failed_readback_contract() -> dict[str, Any]:
    return {
        "status": "FAIL",
        "subject_commit": READBACK_COMMIT,
        "release_tag": READBACK_TAG,
        "release_id": READBACK_RELEASE_ID,
        "transport": "anonymous_https",
        "observed_date": READBACK_DATE,
        "release_assets": 0,
        "release_asset_bytes": 0,
        "raw_files": 0,
        "mismatches": 0,
        "errors": 1,
    }


def validate_public_readback_projection(
    catalog: dict[str, Any], receipt: dict[str, Any], errors: list[str]
) -> dict[str, Any]:
    before = len(errors)
    release_url = (
        "https://github.com/KokunoYumeto/mathematics-commons-pilot/"
        f"releases/tag/{READBACK_TAG}"
    )
    expected_subject = {
        "repository": READBACK_REPOSITORY,
        "commit": READBACK_COMMIT,
        "main_commit_at_readback": READBACK_MAIN_AT_OBSERVATION,
        "tag": READBACK_TAG,
        "tag_commit": READBACK_COMMIT,
        "release_id": READBACK_RELEASE_ID,
        "release_url": release_url,
    }
    expected_transport = {
        "method": "anonymous_https",
        "authorization": "none",
        "cookies": "none",
        "persistence": "none",
    }
    assets = expected_readback_assets(catalog)
    asset_bytes = sum(
        int(row["expected_bytes"])
        for row in assets
        if isinstance(row.get("expected_bytes"), int)
        and not isinstance(row.get("expected_bytes"), bool)
    )
    expected_aggregate = {
        "expected_assets": len(assets),
        "observed_assets": len(assets),
        "matched_assets": len(assets),
        "expected_bytes": asset_bytes,
        "observed_bytes": asset_bytes,
        "mismatches": 0,
    }
    raw_files = expected_readback_raw_files()
    expected_raw_aggregate = {
        "expected_files": len(raw_files),
        "observed_files": len(raw_files),
        "matched_files": len(raw_files),
        "mismatches": 0,
    }
    expect(
        catalog.get("release", {}).get("tag") == READBACK_TAG,
        errors,
        "public readback: catalog release tag",
    )
    expect(
        catalog.get("release", {}).get("url") == release_url,
        errors,
        "public readback: catalog release URL",
    )
    expect(
        receipt.get("schema") == "math-commons-release-readback/v1",
        errors,
        "public readback: schema",
    )
    expect(receipt.get("status") == "PASS", errors, "public readback: status")
    expect(
        receipt.get("observed_date") == READBACK_DATE,
        errors,
        "public readback: observed date",
    )
    expect(receipt.get("errors") == [], errors, "public readback: errors")
    expect(receipt.get("subject") == expected_subject, errors, "public readback: subject")
    expect(
        receipt.get("transport") == expected_transport,
        errors,
        "public readback: anonymous transport",
    )
    expect(receipt.get("assets") == assets, errors, "public readback: exact asset projection")
    expect(
        receipt.get("aggregate") == expected_aggregate,
        errors,
        "public readback: asset aggregate",
    )
    expect(
        receipt.get("raw_files") == raw_files,
        errors,
        "public readback: exact raw-file projection",
    )
    expect(
        receipt.get("raw_aggregate") == expected_raw_aggregate,
        errors,
        "public readback: raw-file aggregate",
    )
    new_errors = len(errors) - before
    return {
        "status": "PASS" if new_errors == 0 else "FAIL",
        "subject_commit": READBACK_COMMIT,
        "release_tag": READBACK_TAG,
        "release_id": READBACK_RELEASE_ID,
        "transport": "anonymous_https",
        "observed_date": READBACK_DATE,
        "release_assets": len(assets),
        "release_asset_bytes": asset_bytes,
        "raw_files": len(raw_files),
        "mismatches": 0,
        "errors": new_errors,
    }


def validate_public_readback(errors: list[str]) -> dict[str, Any]:
    catalog, _ = load(ROOT / "catalog" / "jobs.json")
    receipt, _ = load(ROOT / "catalog" / "readback-r2.json")
    validate_schema(receipt, "readback", "public release readback", errors)
    return validate_public_readback_projection(catalog, receipt, errors)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--asset-dir", type=Path)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--verify-receipt", action="store_true")
    args = parser.parse_args()
    errors: list[str] = []
    public_readback = failed_readback_contract()
    try:
        (
            jobs,
            assets,
            source_files,
            source_bytes,
            asset_bytes,
            member_files,
            nested_authorities,
        ) = validate_jobs(args.asset_dir.resolve() if args.asset_dir else None, errors)
        validate_translations(errors)
        translation_catalog, _ = load(ROOT / "catalog" / "translations.json")
        education_catalog, _ = load(ROOT / "catalog" / "edu.json")
        validate_schema(
            education_catalog,
            "education",
            "education translation catalog",
            errors,
        )
        formalization = validate_formalization(errors)
        portals = validate_portals(errors)
        portal_catalog, _ = load(ROOT / "catalog" / "portals.json")
        translation_section = next(
            (
                row
                for row in portal_catalog.get("sections", [])
                if isinstance(row, dict) and row.get("id") == "translation"
            ),
            {},
        )
        translation_releases = [
            translation_section.get("release", {}),
            translation_section.get("starter", {}),
        ]
        translation_summary = {
            "topics": len(translation_catalog.get("topics", [])),
            "works": len(translation_catalog.get("works", [])),
            "resources": len(translation_catalog.get("resources", [])),
            "source_editions": len(translation_catalog.get("source_editions", [])),
            "translation_editions": len(translation_catalog.get("translation_editions", [])),
            "jobs": len(translation_catalog.get("jobs", [])),
            "workflow_startable_works": sum(
                1
                for row in translation_catalog.get("source_editions", [])
                if isinstance(row, dict)
                and row.get("item_type") == "work"
                and row.get("workflow_startability")
                in {"starter_available", "source_bound_packet"}
            ),
            "packaged_runnable_jobs": sum(
                1
                for row in translation_catalog.get("jobs", [])
                if isinstance(row, dict) and row.get("state") == "runnable"
            ),
            "runnable_jobs": sum(
                1
                for row in translation_catalog.get("jobs", [])
                if isinstance(row, dict) and row.get("state") == "runnable"
            ),
            "runnable_jobs_scope": "self_contained_public_packets_only",
            "public_release_assets": sum(
                int(row.get("asset_count", 0))
                for row in translation_releases
                if isinstance(row, dict)
            ),
            "public_release_bytes": sum(
                int(row.get("asset_bytes", 0))
                for row in translation_releases
                if isinstance(row, dict)
            ),
        }
        public_readback = validate_public_readback(errors)
    except (OSError, UnicodeError, json.JSONDecodeError, DuplicateKey, ValueError) as exc:
        errors.append(str(exc))
        portal_catalog = {}
        jobs = assets = source_files = source_bytes = asset_bytes = member_files = 0
        nested_authorities = formalization = portals = 0
        translation_summary = {
            "topics": 0,
            "works": 0,
            "resources": 0,
            "source_editions": 0,
            "translation_editions": 0,
            "jobs": 0,
            "workflow_startable_works": 0,
            "packaged_runnable_jobs": 0,
            "runnable_jobs": 0,
            "runnable_jobs_scope": "self_contained_public_packets_only",
            "public_release_assets": 0,
            "public_release_bytes": 0,
        }
    try:
        inputs = {
            "job_meta": input_identity(ROOT / "catalog" / "job-meta.json"),
            "jobs": input_identity(ROOT / "catalog" / "jobs.json"),
            "translations": input_identity(ROOT / "catalog" / "translations.json"),
            "education": input_identity(ROOT / "catalog" / "edu.json"),
            "translation_choices": input_identity(ROOT / "kits" / "translate" / "WORKS.json"),
            "translation_source": input_identity(ROOT / "kits" / "translate" / "SOURCE.json"),
            "openlogic_source": input_identity(ROOT / "kits" / "openlogic" / "SOURCE.json"),
            "openlogic_job": input_identity(ROOT / "kits" / "openlogic" / "JOB.json"),
            "openlogic_build": input_identity(ROOT / "kits" / "openlogic" / "BUILD.json"),
            "formalization": input_identity(ROOT / "catalog" / "formalize.json"),
            "portals": input_identity(ROOT / "catalog" / "portals.json"),
            "readback": input_identity(ROOT / "catalog" / "readback.json"),
            "readback_r2": input_identity(ROOT / "catalog" / "readback-r2.json"),
            "translate_readback": input_identity(ROOT / "catalog" / "translate-rb-v6.json"),
            "openlogic_readback": input_identity(ROOT / "catalog" / "openlogic-rb.json"),
            "translate_v7_readback": (
                input_identity(ROOT / "catalog" / "translate-rb-v7.json")
                if portal_requires_v7_readback(portal_catalog)
                else None
            ),
            "translate_v8_readback": (
                input_identity(ROOT / "catalog" / "translate-rb-v8.json")
                if portal_requires_v8_readback(portal_catalog)
                else None
            ),
            "translate_v9_readback": (
                input_identity(ROOT / "catalog" / "translate-rb-v9-final.json")
                if portal_requires_v9_readback(portal_catalog)
                else None
            ),
            "openlogic_asset_manifest": input_identity(ROOT / "catalog" / "assets" / "openlogic.json"),
            "translate_v7_asset_manifest": input_identity(ROOT / "catalog" / "assets" / "translate-v7.json"),
            "translate_v8_asset_manifest": input_identity(ROOT / "catalog" / "assets" / "translate-v8.json"),
            "translate_v9_asset_manifest": input_identity(ROOT / "catalog" / "assets" / "translate-v9-complete.json"),
            "global_receipt": input_identity(ROOT / "catalog" / "receipts" / "global.json"),
            "gordan2_receipt": input_identity(ROOT / "catalog" / "receipts" / "gordan2.txt"),
            "mikami_receipt": input_identity(ROOT / "catalog" / "receipts" / "mikami.json"),
            "r2_admission_receipt": input_identity(ROOT / "catalog" / "receipts" / "r2-admission.json"),
            "no_failure_hardening_receipt": input_identity(ROOT / "catalog" / "receipts" / "no-failure-hardening.json"),
            "openlogic_receipt": input_identity(ROOT / "catalog" / "receipts" / "openlogic.json"),
            "id_readers_receipt": input_identity(ROOT / "catalog" / "receipts" / "id-readers.json"),
            "job_meta_schema": input_identity(ROOT / "schemas" / "job-meta.schema.json"),
            "job_schema": input_identity(ROOT / "schemas" / "job-catalog.schema.json"),
            "translation_schema": input_identity(ROOT / "schemas" / "translation-catalog.schema.json"),
            "translation_choices_schema": input_identity(ROOT / "schemas" / "translation-choices.schema.json"),
            "translation_source_schema": input_identity(ROOT / "schemas" / "translation-source.schema.json"),
            "translation_build_schema": input_identity(ROOT / "schemas" / "translation-build.schema.json"),
            "education_schema": input_identity(ROOT / "schemas" / "edu.schema.json"),
            "formalization_schema": input_identity(ROOT / "schemas" / "formalization-intake.schema.json"),
            "portal_schema": input_identity(ROOT / "schemas" / "portal-catalog.schema.json"),
            "asset_schema": input_identity(ROOT / "schemas" / "job-asset.schema.json"),
            "readback_schema": input_identity(ROOT / "schemas" / "release-readback.schema.json"),
            "portal_readback_schema": input_identity(ROOT / "schemas" / "portal-readback.schema.json"),
            "check_schema": input_identity(ROOT / "schemas" / "catalog-check.schema.json"),
            "schema_validator": input_identity(ROOT / "tools" / "validate_packets.py"),
            "packer": input_identity(ROOT / "tools" / "pack_job.py"),
            "builder": input_identity(ROOT / "tools" / "build_jobs.py"),
            "admission_builder": input_identity(ROOT / "tools" / "build_r2_admission.py"),
            "manifest_repair": input_identity(ROOT / "tools" / "repair_stale_packet_manifests.py"),
            "readback_tool": input_identity(ROOT / "tools" / "readback_jobs_release.py"),
            "openlogic_builder": input_identity(ROOT / "tools" / "build_openlogic.py"),
            "openlogic_auditor": input_identity(ROOT / "tools" / "audit_openlogic_build.py"),
            "translation_builder": input_identity(ROOT / "tools" / "build_translate.py"),
            "translation_migrator": input_identity(ROOT / "tools" / "migrate_translations_v7.py"),
            "translation_reader_updater": input_identity(ROOT / "tools" / "add_id_readers.py"),
            "portal_readback_tool": input_identity(ROOT / "tools" / "readback_portal.py"),
            "validator": input_identity(ROOT / "tools" / "validate_jobs.py"),
        }
        asset_manifests = manifest_set_identity()
    except (OSError, UnicodeError, json.JSONDecodeError, DuplicateKey, ValueError) as exc:
        print(f"ERROR: cannot bind validator inputs: {exc}", file=sys.stderr)
        return 1
    result = {
        "schema": "math-commons-catalog-check/v3",
        "status": "PASS" if not errors else "FAIL",
        "inputs": inputs,
        "asset_manifests": asset_manifests,
        "jobs": jobs,
        "release_assets": assets,
        "release_asset_bytes": asset_bytes,
        "packet_source_files": source_files,
        "packet_source_bytes": source_bytes,
        "zip_member_files_replayed": member_files,
        "nested_authorities_replayed": nested_authorities,
        "asset_mode": (
            "local_zip_replay"
            if args.asset_dir
            else "admission_receipt_plus_public_readback"
        ),
        "translation": translation_summary,
        "formalization_entries": formalization,
        "portal_sections": portals,
        "public_readback": public_readback,
        "errors": errors,
    }
    if args.verify_receipt:
        try:
            receipt, _ = load(ROOT / "catalog" / "check.json")
            validate_schema(receipt, "check", "tracked catalog receipt", errors)
            expect(receipt.get("schema") == result["schema"], errors, "tracked receipt schema")
            expect(receipt.get("status") == "PASS", errors, "tracked receipt status")
            expect(receipt.get("errors") == [], errors, "tracked receipt errors")
            expect(receipt.get("inputs") == result["inputs"], errors, "tracked receipt input identities")
            expect(receipt.get("asset_manifests") == result["asset_manifests"], errors, "tracked receipt asset-manifest identity")
            for key in (
                "jobs",
                "release_assets",
                "release_asset_bytes",
                "packet_source_files",
                "packet_source_bytes",
                "translation",
                "formalization_entries",
                "portal_sections",
                "public_readback",
            ):
                expect(receipt.get(key) == result[key], errors, f"tracked receipt {key}")
            expected_mode = (
                "local_zip_replay"
                if args.asset_dir
                else "admission_receipt_plus_public_readback"
            )
            expect(receipt.get("asset_mode") == expected_mode, errors, "tracked receipt asset mode")
            expect(receipt.get("zip_member_files_replayed") == member_files, errors, "tracked receipt member replay")
            expect(
                receipt.get("nested_authorities_replayed") == nested_authorities,
                errors,
                "tracked receipt nested-authority replay",
            )
        except (OSError, UnicodeError, json.JSONDecodeError, DuplicateKey, ValueError) as exc:
            errors.append(f"cannot verify tracked receipt: {exc}")
        result["status"] = "PASS" if not errors else "FAIL"
        result["errors"] = errors
    result["status"] = "PASS" if not errors else "FAIL"
    result["errors"] = list(errors)
    schema_errors: list[str] = []
    validate_schema(result, "check", "generated catalog receipt", schema_errors)
    if schema_errors:
        errors.extend(schema_errors)
        result["status"] = "FAIL"
        result["errors"] = list(errors)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_bytes(
            (json.dumps(result, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
        )
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
    else:
        print(
            f"PASS: {jobs} jobs, {assets} release assets, "
            f"{translation_summary['works']} translation works, "
            f"{translation_summary['resources']} translation resources, "
            f"{translation_summary['workflow_startable_works']} workflow-startable translation works, "
            f"{translation_summary['packaged_runnable_jobs']} self-contained runnable translation packets, "
            f"{portals} portal sections, "
            f"{formalization} formalization entries"
        )
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
