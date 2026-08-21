#!/usr/bin/env python3
"""Validate job/translation catalogs and optional local release ZIPs."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
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
    "check": "catalog-check.schema.json",
    "readback": "release-readback.schema.json",
    "portals": "portal-catalog.schema.json",
}
CHUNK = 1024 * 1024
FIXED_TIME = (1980, 1, 1, 0, 0, 0)
REGULAR_0644 = 0o100644
READBACK_COMMIT = "049a2c9c351e827c85e69f21c2ebd0c3a98db705"
READBACK_TAG = "jobs-2026-08-21-r1"
READBACK_RELEASE_ID = 374306971
READBACK_REPOSITORY = "KokunoYumeto/mathematics-commons-pilot"
READBACK_DATE = "2026-08-21"
READBACK_RAW_FILES = (
    ("README.md", 9024, "1995D1D472156E9B783526A8F61215AEEBDCBA315387C7498D53F5AE5F86092E"),
    ("docs/workbench.md", 13375, "49680CCC16A4455EF14FC9294546F72E1C8CCD048E2A16D17B8A85874BE1A88D"),
    ("docs/roadmap.md", 1316, "844C76C2B104B845C6C6695BD2022FB078631BC835D86C98F11973AE58D913B1"),
    ("catalog/jobs.json", 105768, "2441250EA70F194B87CBC8AEB338DBFFBEE45419B82C7CAE95DBB75770B72BCB"),
    ("catalog/check.json", 3226, "A9594073F93DF814FB43348A7D2F9B55688766DA0F7187552B2AFB9E5FE983FD"),
    ("schemas/catalog-check.schema.json", 4729, "81ADBFA1C22FE336DBC2031B905617CB818291E709BC77B204BD5096AC087D28"),
    ("tools/validate_jobs.py", 47343, "353D08F3ADF1736D703B2D2B0BAFD8767C80349333F5AABB74B73DE31A1FDA97"),
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
            and row["bytes"] > 0
            for row in members
            if isinstance(row, dict)
        ),
        errors,
        f"{prefix}: member bytes",
    )
    expect(all(isinstance(row.get("sha256"), str) and HEX64.fullmatch(row["sha256"]) for row in members), errors, f"{prefix}: member hash")
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
                    expect(info.date_time == FIXED_TIME, errors, f"{prefix}: member time {name}")
                    expect(
                        info.compress_type == zipfile.ZIP_DEFLATED,
                        errors,
                        f"{prefix}: compression {name}",
                    )
                    expect(info.create_system == 3, errors, f"{prefix}: create system {name}")
                    expect(
                        info.external_attr >> 16 == REGULAR_0644,
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
    expect(meta.get("schema") == "math-commons-job-meta/v1", errors, "job metadata schema")
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
    verify_repo_identity(meta.get("audit_receipt"), "global admission receipt", errors)
    audit_projection = meta.get("audit_receipt", {}).get("public_projection", {})
    audit_path = ROOT / str(audit_projection.get("path", ""))
    try:
        global_audit, _ = load(audit_path)
    except (OSError, UnicodeError, json.JSONDecodeError, DuplicateKey, ValueError) as exc:
        errors.append(f"global admission receipt: cannot parse public projection: {exc}")
        global_audit = {}
    audit_rows = global_audit.get("rows") if isinstance(global_audit, dict) else None
    if not isinstance(audit_rows, list):
        errors.append("global admission receipt: rows missing")
        rows_by_packet: dict[str, dict[str, Any]] = {}
    else:
        expect(
            global_audit.get("schema") == "strict-current-lane-independent-cold-audit/v1",
            errors,
            "global admission receipt schema",
        )
        expect(global_audit.get("row_count") == len(audit_rows), errors, "global audit row count")
        expect(global_audit.get("pass_count") == len(audit_rows), errors, "global audit pass count")
        expect(global_audit.get("fail_count") == 0, errors, "global audit fail count")
        expect(
            global_audit.get("nonmutating_packet_audit") is True
            and global_audit.get("published_or_promoted") is False,
            errors,
            "global audit boundary",
        )
        packet_ids = [
            row.get("packet_id") for row in audit_rows if isinstance(row, dict)
        ]
        expect(len(packet_ids) == len(audit_rows), errors, "global audit malformed row")
        expect(len(packet_ids) == len(set(packet_ids)), errors, "global audit duplicate packet")
        expect(
            all(isinstance(row, dict) and row.get("overall") == "PASS" for row in audit_rows),
            errors,
            "global audit non-PASS row",
        )
        rows_by_packet = {
            str(row["packet_id"]): row
            for row in audit_rows
            if isinstance(row, dict) and isinstance(row.get("packet_id"), str)
        }
    for job in meta_jobs:
        if not isinstance(job, dict):
            continue
        job_id = str(job.get("id"))
        packet_id = job.get("packet_id")
        basis = job.get("audit_basis")
        if basis == "global_receipt":
            row = rows_by_packet.get(str(packet_id))
            if row is None:
                errors.append(f"{job_id}: missing global audit row")
                continue
            expect(job.get("status") == "PASS_GLOBAL_COLD_AUDIT", errors, f"{job_id}: global status")
            expect(row.get("direct_file_count") == job.get("source_files"), errors, f"{job_id}: global file count")
            packet_manifest = job.get("packet_manifest", {})
            validation_receipt = job.get("validation_receipt", {})
            expect(
                isinstance(packet_manifest, dict)
                and row.get("manifest_file") == packet_manifest.get("basename")
                and row.get("manifest_sha256") == packet_manifest.get("sha256"),
                errors,
                f"{job_id}: global manifest identity",
            )
            expect(
                isinstance(validation_receipt, dict)
                and validation_receipt.get("included_in_packet", True) is True
                and row.get("receipt_file") == validation_receipt.get("basename")
                and row.get("receipt_sha256") == validation_receipt.get("sha256"),
                errors,
                f"{job_id}: global receipt identity",
            )
            manifest_path = ROOT / "catalog" / "assets" / f"{job_id}.json"
            try:
                asset_manifest, _ = load(manifest_path)
            except (OSError, UnicodeError, json.JSONDecodeError, DuplicateKey, ValueError) as exc:
                errors.append(f"{job_id}: cannot replay global snapshot against asset manifest: {exc}")
            else:
                members = asset_manifest.get("members")
                if not isinstance(members, list) or not all(isinstance(item, dict) for item in members):
                    errors.append(f"{job_id}: asset members unavailable for global snapshot replay")
                else:
                    expect(
                        row.get("direct_snapshot_sha256") == audit_snapshot_sha256(members),
                        errors,
                        f"{job_id}: global direct snapshot SHA-256",
                    )
        elif basis == "terminal_sidecar":
            expect(str(packet_id) not in rows_by_packet, errors, f"{job_id}: ambiguous audit basis")
            receipt = job.get("validation_receipt")
            expect(
                isinstance(receipt, dict)
                and receipt.get("included_in_packet") is False
                and isinstance(receipt.get("public_projection"), dict),
                errors,
                f"{job_id}: terminal sidecar binding",
            )
        else:
            errors.append(f"{job_id}: unknown audit basis")
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


def validate_jobs(
    asset_dir: Path | None, errors: list[str]
) -> tuple[int, int, int, int, int, int, int]:
    catalog_path = ROOT / "catalog" / "jobs.json"
    catalog, _ = load(catalog_path)
    validate_schema(catalog, "jobs", "job catalog", errors)
    expect(catalog.get("schema") == "math-commons-job-catalog/v1", errors, "job catalog schema")
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
        expect(job.get("prompt_count") == 45, errors, f"{job_id}: prompt count")
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
        bind_declared_member(
            members_by_path,
            job.get("packet_manifest"),
            f"{job_id}: packet manifest",
            errors,
        )
        receipt = job.get("validation_receipt")
        if isinstance(receipt, dict) and receipt.get("included_in_packet", True) is False:
            basename = receipt.get("basename")
            expect(
                isinstance(basename, str) and basename not in members_by_path,
                errors,
                f"{job_id}: external receipt is unexpectedly a packet member",
            )
            verify_repo_identity(receipt, f"{job_id}: public validation receipt", errors)
            validate_terminal_sidecar(job, manifest, errors)
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
    expect(catalog.get("schema") == "math-commons-translation-catalog/v1", errors, "translation catalog schema")
    entries = catalog.get("entries")
    if not isinstance(entries, list) or not entries:
        errors.append("translation catalog has no entries")
        return 0
    ids = [entry.get("id") for entry in entries]
    expect(len(ids) == len(set(ids)), errors, "translation IDs are not unique")
    for entry in entries:
        if not isinstance(entry, dict):
            errors.append("translation catalog has a malformed entry row")
            continue
        entry_id = entry.get("id")
        expect(entry.get("adoption_state") in {"candidate", "conditional_candidate", "current_production", "donor", "existing_edition", "infrastructure", "optional", "reference", "selected_start"}, errors, f"translation {entry_id}: state")
        url = entry.get("source_url")
        expect(url is None or (isinstance(url, str) and url.startswith("https://")), errors, f"translation {entry_id}: source URL")
        commit = entry.get("source_commit")
        expect(commit is None or (isinstance(commit, str) and re.fullmatch(r"[0-9a-f]{40}", commit)), errors, f"translation {entry_id}: commit")
    evidence = catalog.get("evidence")
    expect(
        isinstance(evidence, dict)
        and evidence.get("public_evidence_included") is False,
        errors,
        "translation catalog evidence boundary",
    )
    return len(entries)


def validate_portals(errors: list[str]) -> int:
    catalog, _ = load(ROOT / "catalog" / "portals.json")
    validate_schema(catalog, "portals", "portal catalog", errors)
    expect(
        catalog.get("schema") == "math-commons-portal-catalog/v1",
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
        ROOT / "catalog" / "assets" / "translate-v3.json",
        "translation-starter-v3",
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
        and translate_release.get("tag") == "translate-v3"
        and translate_release.get("url")
        == "https://github.com/KokunoYumeto/mathematics-commons-pilot/releases/tag/translate-v3"
        and translate_release.get("asset_catalog")
        == "catalog/assets/translate-v3.json",
        errors,
        "portal translation release contract",
    )

    expect(
        transcription.get("state") == "runnable"
        and transcription.get("catalog") == "catalog/jobs.json"
        and trans_release.get("tag") == "jobs-2026-08-21-r1"
        and trans_release.get("url")
        == "https://github.com/KokunoYumeto/mathematics-commons-pilot/releases/tag/jobs-2026-08-21-r1"
        and trans_release.get("asset_catalog") == "catalog/jobs.json",
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
        "main_commit_at_readback": READBACK_COMMIT,
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
    receipt, _ = load(ROOT / "catalog" / "readback.json")
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
        translations = validate_translations(errors)
        portals = validate_portals(errors)
        public_readback = validate_public_readback(errors)
    except (OSError, UnicodeError, json.JSONDecodeError, DuplicateKey, ValueError) as exc:
        errors.append(str(exc))
        jobs = assets = source_files = source_bytes = asset_bytes = member_files = 0
        nested_authorities = translations = portals = 0
    result = {
        "schema": "math-commons-catalog-check/v1",
        "status": "PASS" if not errors else "FAIL",
        "inputs": {
            "job_meta": input_identity(ROOT / "catalog" / "job-meta.json"),
            "jobs": input_identity(ROOT / "catalog" / "jobs.json"),
            "translations": input_identity(ROOT / "catalog" / "translations.json"),
            "portals": input_identity(ROOT / "catalog" / "portals.json"),
            "readback": input_identity(ROOT / "catalog" / "readback.json"),
            "global_receipt": input_identity(ROOT / "catalog" / "receipts" / "global.json"),
            "gordan2_receipt": input_identity(ROOT / "catalog" / "receipts" / "gordan2.txt"),
            "mikami_receipt": input_identity(ROOT / "catalog" / "receipts" / "mikami.json"),
            "job_meta_schema": input_identity(ROOT / "schemas" / "job-meta.schema.json"),
            "job_schema": input_identity(ROOT / "schemas" / "job-catalog.schema.json"),
            "translation_schema": input_identity(ROOT / "schemas" / "translation-catalog.schema.json"),
            "portal_schema": input_identity(ROOT / "schemas" / "portal-catalog.schema.json"),
            "asset_schema": input_identity(ROOT / "schemas" / "job-asset.schema.json"),
            "readback_schema": input_identity(ROOT / "schemas" / "release-readback.schema.json"),
            "check_schema": input_identity(ROOT / "schemas" / "catalog-check.schema.json"),
            "schema_validator": input_identity(ROOT / "tools" / "validate_packets.py"),
            "packer": input_identity(ROOT / "tools" / "pack_job.py"),
            "builder": input_identity(ROOT / "tools" / "build_jobs.py"),
            "validator": input_identity(ROOT / "tools" / "validate_jobs.py"),
        },
        "asset_manifests": manifest_set_identity(),
        "jobs": jobs,
        "release_assets": assets,
        "release_asset_bytes": asset_bytes,
        "packet_source_files": source_files,
        "packet_source_bytes": source_bytes,
        "zip_member_files_replayed": member_files if args.asset_dir else 0,
        "nested_authorities_replayed": nested_authorities if args.asset_dir else 0,
        "asset_mode": "local_zip_replay" if args.asset_dir else "catalog_only",
        "translation_entries": translations,
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
                "translation_entries",
                "portal_sections",
                "public_readback",
            ):
                expect(receipt.get(key) == result[key], errors, f"tracked receipt {key}")
            expect(receipt.get("asset_mode") == "local_zip_replay", errors, "tracked receipt asset mode")
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
            f"{translations} translation entries, {portals} portal sections"
        )
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
