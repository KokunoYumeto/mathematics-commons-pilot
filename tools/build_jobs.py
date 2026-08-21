#!/usr/bin/env python3
"""Build admitted job assets and generate the public catalog."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import zipfile
from pathlib import Path
from typing import Any

import pack_job


ROOT = Path(__file__).resolve().parents[1]
META = ROOT / "catalog" / "job-meta.json"
ASSET_MANIFESTS = ROOT / "catalog" / "assets"
CATALOG = ROOT / "catalog" / "jobs.json"
REPOSITORY = "KokunoYumeto/mathematics-commons-pilot"
SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
RELEASE_TAG = re.compile(r"^jobs-[0-9]{4}-[0-9]{2}-[0-9]{2}-r[0-9]+$")
ADMITTED_STATUSES = {
    "PASS_COLD_PACKET_VALIDATION",
    "PASS_FINAL_NONPATCHING",
    "PASS_GLOBAL_COLD_AUDIT",
}


class DuplicateKey(ValueError):
    pass


def object_pairs(values: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in values:
        if key in result:
            raise DuplicateKey(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def load_json(path: Path) -> dict[str, object]:
    data = path.read_bytes()
    if data.startswith(b"\xef\xbb\xbf") or b"\r" in data:
        raise ValueError(f"JSON must be UTF-8 LF without BOM: {path}")
    value = json.loads(data.decode("utf-8"), object_pairs_hook=object_pairs)
    if not isinstance(value, dict):
        raise ValueError(f"JSON root is not an object: {path}")
    return value


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def identity(path: Path) -> dict[str, object]:
    data = path.read_bytes()
    return {
        "path": path.relative_to(ROOT).as_posix(),
        "bytes": len(data),
        "sha256": sha256_bytes(data),
    }


def verify_named_file(
    source: Path,
    rows_by_path: dict[str, dict[str, object]],
    declared: object,
    label: str,
) -> None:
    if not isinstance(declared, dict):
        raise ValueError(f"{label}: identity is not an object")
    basename = declared.get("basename")
    if (
        not isinstance(basename, str)
        or not basename
        or Path(basename).name != basename
        or "/" in basename
        or "\\" in basename
    ):
        raise ValueError(f"{label}: unsafe or missing basename")
    row = rows_by_path.get(basename)
    if row is None:
        raise ValueError(f"{label}: declared file is absent: {basename}")
    if row.get("bytes") != declared.get("bytes"):
        raise ValueError(f"{label}: byte length differs: {basename}")
    if row.get("sha256") != declared.get("sha256"):
        raise ValueError(f"{label}: SHA-256 differs: {basename}")
    if not (source / basename).is_file():
        raise ValueError(f"{label}: declared path is not a regular file: {basename}")


def validate_receipt_binding(
    source: Path,
    rows_by_path: dict[str, dict[str, object]],
    declared: object,
    label: str,
) -> None:
    if not isinstance(declared, dict):
        raise ValueError(f"{label}: identity is not an object")
    if declared.get("included_in_packet", True) is True:
        verify_named_file(source, rows_by_path, declared, label)
        return
    if declared.get("included_in_packet") is not False:
        raise ValueError(f"{label}: malformed inclusion state")
    basename = declared.get("basename")
    if (
        not isinstance(basename, str)
        or not basename
        or Path(basename).name != basename
        or basename in rows_by_path
        or not isinstance(declared.get("bytes"), int)
        or declared["bytes"] <= 0
        or not isinstance(declared.get("sha256"), str)
        or re.fullmatch(r"[0-9A-F]{64}", declared["sha256"]) is None
        or not isinstance(declared.get("receipt_scope"), str)
        or not declared["receipt_scope"].strip()
        or not isinstance(declared.get("public_projection"), dict)
    ):
        raise ValueError(f"{label}: invalid external sidecar identity")
    projection = declared["public_projection"]
    public_path = (ROOT / str(projection.get("path", ""))).resolve()
    try:
        public_path.relative_to(ROOT.resolve())
    except ValueError as exc:
        raise ValueError(f"{label}: public sidecar escapes the repository") from exc
    if (
        not public_path.is_file()
        or public_path.stat().st_size != projection.get("bytes")
        or pack_job.sha256_file(public_path) != projection.get("sha256")
    ):
        raise ValueError(f"{label}: public sidecar identity differs")


def hash_stream(handle: object) -> str:
    digest = hashlib.sha256()
    while block := handle.read(1024 * 1024):
        digest.update(block)
    return digest.hexdigest().upper()


def verify_authority(
    source: Path,
    rows_by_path: dict[str, dict[str, object]],
    authority: dict[str, object],
    label: str,
) -> None:
    logical_path = authority.get("path")
    declared_hash = authority.get("sha256")
    if (
        not isinstance(logical_path, str)
        or not logical_path
        or not isinstance(declared_hash, str)
        or re.fullmatch(r"[0-9A-F]{64}", declared_hash) is None
    ):
        raise ValueError(f"{label}: malformed authority identity")
    levels = logical_path.split("!/")
    outer = levels[0]
    if Path(outer).name != outer or "/" in outer or "\\" in outer:
        raise ValueError(f"{label}: unsafe outer authority path")
    row = rows_by_path.get(outer)
    if row is None:
        raise ValueError(f"{label}: outer authority is absent: {outer}")
    if len(levels) == 1:
        if row.get("sha256") != declared_hash:
            raise ValueError(f"{label}: authority SHA-256 differs: {outer}")
        return
    if len(levels) != 2:
        raise ValueError(f"{label}: only one archive descent is supported")
    nested = levels[1]
    if (
        not nested
        or "\\" in nested
        or nested.startswith("/")
        or ".." in Path(nested).parts
    ):
        raise ValueError(f"{label}: unsafe nested authority path")
    try:
        with zipfile.ZipFile(source / outer, "r") as archive:
            info = archive.getinfo(nested)
            if info.is_dir():
                raise ValueError(f"{label}: nested authority is a directory")
            with archive.open(info, "r") as handle:
                actual_hash = hash_stream(handle)
    except (KeyError, OSError, zipfile.BadZipFile) as exc:
        raise ValueError(f"{label}: cannot replay nested authority: {exc}") from exc
    if actual_hash != declared_hash:
        raise ValueError(f"{label}: nested authority SHA-256 differs")


def validate_source_lock(
    source: Path,
    job: dict[str, object],
    rows: list[dict[str, object]],
    expected_manifest: dict[str, object],
) -> None:
    job_id = str(job["id"])
    if job.get("prompt_count") != 45 or job.get("pack_scope") != "direct_files":
        raise ValueError(f"{job_id}: prompt or packet-scope contract differs")
    if job.get("status") not in {
        "PASS_COLD_PACKET_VALIDATION",
        "PASS_FINAL_NONPATCHING",
        "PASS_GLOBAL_COLD_AUDIT",
    }:
        raise ValueError(f"{job_id}: status is not an admitted terminal PASS")
    expected_basis = (
        "global_receipt"
        if job.get("status") == "PASS_GLOBAL_COLD_AUDIT"
        else "terminal_sidecar"
    )
    if job.get("audit_basis") != expected_basis:
        raise ValueError(f"{job_id}: audit basis differs from terminal status")
    packet_id = str(job.get("packet_id", ""))
    if (
        not packet_id
        or Path(packet_id).name != packet_id
        or "/" in packet_id
        or "\\" in packet_id
        or any(token in packet_id.upper() for token in ("HOLD", "QUARANTINE", "SUPERSEDED"))
    ):
        raise ValueError(f"{job_id}: unsafe or forbidden packet root identity")

    canonical_bytes, represented_tree = pack_job.tree_hash(rows)
    if expected_manifest.get("schema") != "math-commons-job-asset/v1":
        raise ValueError(f"{job_id}: expected asset-manifest schema differs")
    if expected_manifest.get("job_id") != job_id:
        raise ValueError(f"{job_id}: expected asset-manifest job differs")
    if expected_manifest.get("members") != rows:
        raise ValueError(f"{job_id}: exact admitted member set differs")
    if expected_manifest.get("source_files") != len(rows):
        raise ValueError(f"{job_id}: admitted source-file count differs")
    if expected_manifest.get("source_bytes") != sum(int(row["bytes"]) for row in rows):
        raise ValueError(f"{job_id}: admitted source-byte count differs")
    if expected_manifest.get("canonical_stream_bytes") != canonical_bytes:
        raise ValueError(f"{job_id}: admitted canonical-stream length differs")
    if expected_manifest.get("source_tree_sha256") != represented_tree:
        raise ValueError(f"{job_id}: admitted source-tree SHA-256 differs")

    rows_by_path = {str(row["path"]): row for row in rows}
    verify_named_file(source, rows_by_path, job.get("packet_manifest"), f"{job_id} packet manifest")
    validate_receipt_binding(
        source,
        rows_by_path,
        job.get("validation_receipt"),
        f"{job_id} validation receipt",
    )
    authorities = job.get("authority")
    if not isinstance(authorities, list) or not authorities:
        raise ValueError(f"{job_id}: no authority identity")
    for index, authority in enumerate(authorities):
        if not isinstance(authority, dict):
            raise ValueError(f"{job_id}: malformed authority row {index}")
        verify_authority(source, rows_by_path, authority, f"{job_id} authority {index}")


def build_one(
    packet_root: Path,
    output_root: Path,
    job: dict[str, object],
    maximum_part_bytes: int,
) -> None:
    job_id = str(job["id"])
    packet_id = str(job["packet_id"])
    proposed_base = job.get("proposed_asset_base_name")
    if SLUG.fullmatch(job_id) is None:
        raise ValueError(f"{job_id}: invalid job ID")
    if Path(packet_id).name != packet_id or "/" in packet_id or "\\" in packet_id:
        raise ValueError(f"{job_id}: unsafe packet root identity")
    if not isinstance(proposed_base, str) or SLUG.fullmatch(proposed_base) is None:
        raise ValueError(f"{job_id}: unsafe proposed asset basename")
    packet_root = packet_root.resolve()
    source = (packet_root / packet_id).resolve()
    try:
        source.relative_to(packet_root)
    except ValueError as exc:
        raise ValueError(f"{job_id}: packet root escapes the approved base") from exc
    rows = pack_job.source_rows(source, direct_only=True)
    actual_files = len(rows)
    actual_bytes = sum(int(row["bytes"]) for row in rows)
    if actual_files != job["source_files"] or actual_bytes != job["source_bytes"]:
        raise ValueError(
            f"{job_id}: direct packet differs: "
            f"{actual_files}/{actual_bytes} != "
            f"{job['source_files']}/{job['source_bytes']}"
        )
    canonical_bytes, represented_tree = pack_job.tree_hash(rows)
    manifest_path = ASSET_MANIFESTS / f"{job_id}.json"
    if not manifest_path.is_file():
        raise ValueError(f"{job_id}: no reviewed source/asset lock exists")
    expected_manifest = load_json(manifest_path)
    validate_source_lock(source, job, rows, expected_manifest)
    output_root = output_root.resolve()
    base_asset = output_root / f"{proposed_base}.zip"
    groups = pack_job.partitions(rows, maximum_part_bytes)
    assets: list[dict[str, object]] = []
    for index, group in enumerate(groups, start=1):
        output = pack_job.part_path(base_asset, index, len(groups))
        pack_job.build_zip(source, job_id, output, group)
        pack_job.replay_zip(output, job_id, group)
        assets.append(
            {
                "name": output.name,
                "part": index,
                "parts": len(groups),
                "source_files": len(group),
                "source_bytes": sum(int(row["bytes"]) for row in group),
                "first_path": group[0]["path"],
                "last_path": group[-1]["path"],
                "zip_bytes": output.stat().st_size,
                "zip_sha256": pack_job.sha256_file(output),
            }
        )
    manifest = {
        "schema": "math-commons-job-asset/v1",
        "job_id": job_id,
        "wrapper_directory": job_id,
        "source_files": actual_files,
        "source_bytes": actual_bytes,
        "canonical_stream_bytes": canonical_bytes,
        "source_tree_sha256": represented_tree,
        "asset_count": len(assets),
        "assets": assets,
        "members": rows,
        "checks": {
            "source_hash_replay": f"{actual_files}/{actual_files}",
            "zip_member_replay": f"{actual_files}/{actual_files}",
            "crc_errors": 0,
            "missing": 0,
            "extra": 0,
            "byte_mismatches": 0,
            "hash_mismatches": 0,
        },
    }
    if manifest != expected_manifest:
        raise ValueError(f"{job_id}: rebuilt release manifest differs from reviewed lock")
    print(
        f"PASS {job_id}: {actual_files} files / {actual_bytes} bytes / "
        f"{len(assets)} asset(s)",
        flush=True,
    )


def build_translation_kit(output_root: Path, maximum_part_bytes: int) -> None:
    job_id = "open-textbook-translation-kit"
    source = ROOT / "kits" / "translate"
    rows = pack_job.source_rows(source, direct_only=True)
    expected_manifest = load_json(ASSET_MANIFESTS / "translation-kit.json")
    canonical_bytes, represented_tree = pack_job.tree_hash(rows)
    output = output_root / f"{job_id}.zip"
    groups = pack_job.partitions(rows, maximum_part_bytes)
    if len(groups) != 1:
        raise ValueError("translation kit unexpectedly requires multiple assets")
    pack_job.build_zip(source, job_id, output, rows)
    pack_job.replay_zip(output, job_id, rows)
    manifest = {
        "schema": "math-commons-job-asset/v1",
        "job_id": job_id,
        "wrapper_directory": job_id,
        "source_files": len(rows),
        "source_bytes": sum(int(row["bytes"]) for row in rows),
        "canonical_stream_bytes": canonical_bytes,
        "source_tree_sha256": represented_tree,
        "asset_count": 1,
        "assets": [
            {
                "name": output.name,
                "part": 1,
                "parts": 1,
                "source_files": len(rows),
                "source_bytes": sum(int(row["bytes"]) for row in rows),
                "first_path": rows[0]["path"],
                "last_path": rows[-1]["path"],
                "zip_bytes": output.stat().st_size,
                "zip_sha256": pack_job.sha256_file(output),
            }
        ],
        "members": rows,
        "checks": {
            "source_hash_replay": f"{len(rows)}/{len(rows)}",
            "zip_member_replay": f"{len(rows)}/{len(rows)}",
            "crc_errors": 0,
            "missing": 0,
            "extra": 0,
            "byte_mismatches": 0,
            "hash_mismatches": 0,
        },
    }
    if manifest != expected_manifest:
        raise ValueError("translation kit rebuilt manifest differs from reviewed lock")
    print(f"PASS {job_id}", flush=True)


def public_assets(
    manifest: dict[str, object], release_tag: str
) -> list[dict[str, object]]:
    result: list[dict[str, object]] = []
    for asset in manifest["assets"]:
        row = dict(asset)
        row["url"] = (
            f"https://github.com/{REPOSITORY}/releases/download/"
            f"{release_tag}/{asset['name']}"
        )
        result.append(row)
    return result


def generate_catalog(release_tag: str) -> None:
    if RELEASE_TAG.fullmatch(release_tag) is None:
        raise ValueError(f"unsafe release tag: {release_tag!r}")
    meta = load_json(META)
    jobs: list[dict[str, object]] = []
    for source_job in meta["jobs"]:
        job = dict(source_job)
        job_id = job.get("id")
        if not isinstance(job_id, str) or SLUG.fullmatch(job_id) is None:
            raise ValueError(f"unsafe catalog job ID: {job_id!r}")
        proposed_base = job.get("proposed_asset_base_name")
        if not isinstance(proposed_base, str) or SLUG.fullmatch(proposed_base) is None:
            raise ValueError(f"{job_id}: unsafe proposed asset basename")
        if job.get("status") not in ADMITTED_STATUSES:
            raise ValueError(f"{job_id}: status is not an admitted terminal PASS")
        if job.get("audit_basis") not in {"global_receipt", "terminal_sidecar"}:
            raise ValueError(f"{job_id}: invalid audit basis")
        manifest_path = ASSET_MANIFESTS / f"{job_id}.json"
        if not manifest_path.is_file():
            raise ValueError(f"missing asset manifest: {manifest_path}")
        manifest = load_json(manifest_path)
        if manifest["job_id"] != job_id:
            raise ValueError(f"asset manifest ID differs: {job_id}")
        if (
            manifest["source_files"] != job["source_files"]
            or manifest["source_bytes"] != job["source_bytes"]
        ):
            raise ValueError(f"asset manifest scope differs: {job_id}")
        job["catalog_status"] = "runnable"
        job["asset_manifest"] = identity(manifest_path)
        job["assets"] = public_assets(manifest, release_tag)
        jobs.append(job)

    kit_manifest_path = ASSET_MANIFESTS / "translation-kit.json"
    kit_manifest = load_json(kit_manifest_path)
    catalog = {
        "schema": "math-commons-job-catalog/v1",
        "updated": "2026-08-21",
        "repository": f"https://github.com/{REPOSITORY}",
        "release": {
            "tag": release_tag,
            "url": f"https://github.com/{REPOSITORY}/releases/tag/{release_tag}",
            "asset_limit": "Each asset is below GitHub's 2 GiB per-file limit; multipart assets preserve one job when needed.",
        },
        "interaction": {
            "prompt_count": 45,
            "in_progress_reply": "continue",
            "complete_reply": "next prompt",
            "terminal": "Prompt 45 COMPLETE",
            "state_rule": "Every response returns the newest cumulative full-state ZIP, checkpoint, and manifest.",
        },
        "admission": {
            "rule": "Only root-replayed, coherent, strict-PASS packets without HOLD, placeholder, quarantine, supersession, or incomplete-source defects are runnable.",
            "packet_count": len(jobs),
            "source_files": sum(int(job["source_files"]) for job in jobs),
            "source_bytes": sum(int(job["source_bytes"]) for job in jobs),
            "audit_receipt": meta["audit_receipt"],
        },
        "translation_kit": {
            "asset_manifest": identity(kit_manifest_path),
            "assets": public_assets(kit_manifest, release_tag),
        },
        "jobs": jobs,
        "exclusions": meta["exclusions"],
    }
    pack_job.write_json(CATALOG, catalog)
    print(
        f"PASS catalog: {len(jobs)} jobs / "
        f"{sum(len(job['assets']) for job in jobs)} packet assets",
        flush=True,
    )


def verify_output_set(output_root: Path) -> None:
    expected: set[str] = set()
    for path in sorted(ASSET_MANIFESTS.glob("*.json")):
        manifest = load_json(path)
        for asset in manifest.get("assets", []):
            if not isinstance(asset, dict) or not isinstance(asset.get("name"), str):
                raise ValueError(f"malformed reviewed asset row: {path}")
            expected.add(asset["name"])
    observed = {path.name for path in output_root.iterdir() if path.is_file()}
    if observed != expected:
        missing = sorted(expected - observed)
        extra = sorted(observed - expected)
        raise ValueError(f"release output set differs; missing={missing}, extra={extra}")


def reject_output_inside_sources(
    output_root: Path, source_roots: tuple[tuple[str, Path], ...]
) -> None:
    for label, source_root in source_roots:
        try:
            output_root.relative_to(source_root)
        except ValueError:
            continue
        raise ValueError(f"release output must not be inside the {label}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--packet-root", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--release-tag", default="jobs-2026-08-21-r1")
    parser.add_argument("--max-part-bytes", type=int, default=1_700_000_000)
    parser.add_argument("--job", action="append", default=[])
    parser.add_argument("--catalog-only", action="store_true")
    args = parser.parse_args()

    if RELEASE_TAG.fullmatch(args.release_tag) is None:
        raise ValueError(f"unsafe release tag: {args.release_tag!r}")

    packet_root = args.packet_root.resolve()
    output_root = args.output.resolve()
    if not args.catalog_only:
        reject_output_inside_sources(
            output_root,
            (
                ("producer packet root", packet_root),
                ("translation-kit source", (ROOT / "kits" / "translate").resolve()),
            ),
        )

    meta = load_json(META)
    requested = set(args.job)
    known = {str(job["id"]) for job in meta["jobs"]}
    unknown = sorted(requested - known)
    if unknown:
        raise ValueError(f"unknown job IDs: {unknown}")
    if not args.catalog_only:
        output_root.mkdir(parents=True, exist_ok=True)
        ASSET_MANIFESTS.mkdir(parents=True, exist_ok=True)
        for job in meta["jobs"]:
            if requested and job["id"] not in requested:
                continue
            build_one(
                packet_root,
                output_root,
                job,
                args.max_part_bytes,
            )
        if not requested:
            build_translation_kit(output_root, args.max_part_bytes)
            verify_output_set(output_root)
    if not requested:
        generate_catalog(args.release_tag)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, json.JSONDecodeError, DuplicateKey) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
