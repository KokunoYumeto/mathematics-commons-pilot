#!/usr/bin/env python3
"""Build and replay the versioned generic translation starter."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import zipfile
from pathlib import Path

from pack_job import build_zip, replay_zip, sha256_file, source_rows, tree_hash, write_json


ROOT = Path(__file__).resolve().parents[1]
JOB_ID = "translation-starter-v8"
FILES = {
    "KIT.json",
    "LANGS.md",
    "LOCAL.md",
    "MANIFEST.sha256",
    "PROMPT.md",
    "QA.md",
    "README.md",
    "RETURN.md",
    "SOURCE.json",
    "START.md",
    "WEB.md",
    "WORKS.json",
}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def load_object(path: Path) -> dict:
    raw = path.read_bytes()
    if raw.startswith(b"\xef\xbb\xbf") or b"\r" in raw:
        raise ValueError(f"JSON must be UTF-8 LF-only without BOM: {path.name}")
    value = json.loads(raw.decode("utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON root must be an object: {path.name}")
    return value


def write_internal_manifest(source: Path) -> None:
    actual = {path.name for path in source.iterdir() if path.is_file()}
    if actual != FILES:
        raise ValueError(
            f"translation starter file set differs: missing={sorted(FILES - actual)!r}; "
            f"extra={sorted(actual - FILES)!r}"
        )
    rows: list[str] = []
    for name in sorted(FILES - {"MANIFEST.sha256"}):
        data = (source / name).read_bytes()
        rows.append(f"{digest(data)}\t{len(data)}\t{name}\n")
    (source / "MANIFEST.sha256").write_bytes("".join(rows).encode("utf-8"))


def replay_internal_manifest(source: Path) -> None:
    raw = (source / "MANIFEST.sha256").read_bytes()
    if raw.startswith(b"\xef\xbb\xbf") or b"\r" in raw or not raw.endswith(b"\n"):
        raise ValueError("translation starter internal manifest encoding differs")
    observed: list[str] = []
    for line in raw.decode("utf-8")[:-1].split("\n"):
        sha, size_text, name = line.split("\t")
        if name == "MANIFEST.sha256" or name not in FILES:
            raise ValueError(f"unexpected internal-manifest member: {name}")
        data = (source / name).read_bytes()
        if str(len(data)) != size_text or digest(data) != sha:
            raise ValueError(f"internal-manifest replay differs: {name}")
        observed.append(name)
    if observed != sorted(FILES - {"MANIFEST.sha256"}):
        raise ValueError("internal-manifest member order or set differs")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--asset", required=True, type=Path)
    parser.add_argument("--manifest", required=True, type=Path)
    args = parser.parse_args()
    source = ROOT / "kits" / "translate"
    asset = args.asset.resolve()
    manifest_path = args.manifest.resolve()
    if asset.name != f"{JOB_ID}.zip":
        raise ValueError(f"asset must be named {JOB_ID}.zip")
    if asset == manifest_path:
        raise ValueError("asset and manifest paths must differ")

    kit = load_object(source / "KIT.json")
    works = load_object(source / "WORKS.json")
    source_state = load_object(source / "SOURCE.json")
    if (
        kit.get("schema") != "math-commons-translation-starter/v8"
        or works.get("schema") != "math-commons-translation-choices/v8"
        or source_state.get("schema") != "math-commons-translation-source/v5"
    ):
        raise ValueError("translation starter controls are not v8")
    prose = b"\n".join(
        (source / name).read_bytes()
        for name in sorted(FILES)
        if name.endswith(".md")
    ).decode("utf-8")
    for forbidden in ("STATUS: BLOCKED", "STATUS: FAIL", "ordinary HOLD"):
        if forbidden in prose:
            raise ValueError(f"terminal early-stop wording remains: {forbidden}")

    write_internal_manifest(source)
    replay_internal_manifest(source)
    rows = source_rows(source, direct_only=True)
    canonical_bytes, represented_tree = tree_hash(rows)
    build_zip(source, JOB_ID, asset, rows)
    replay_zip(asset, JOB_ID, rows)
    manifest = {
        "schema": "math-commons-job-asset/v1",
        "job_id": JOB_ID,
        "wrapper_directory": JOB_ID,
        "source_files": len(rows),
        "source_bytes": sum(int(row["bytes"]) for row in rows),
        "canonical_stream_bytes": canonical_bytes,
        "source_tree_sha256": represented_tree,
        "asset_count": 1,
        "assets": [
            {
                "name": asset.name,
                "part": 1,
                "parts": 1,
                "source_files": len(rows),
                "source_bytes": sum(int(row["bytes"]) for row in rows),
                "first_path": rows[0]["path"],
                "last_path": rows[-1]["path"],
                "zip_bytes": asset.stat().st_size,
                "zip_sha256": sha256_file(asset),
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
    write_json(manifest_path, manifest)
    print(
        json.dumps(
            {
                "job_id": JOB_ID,
                "source_files": len(rows),
                "source_bytes": manifest["source_bytes"],
                "zip_bytes": asset.stat().st_size,
                "zip_sha256": sha256_file(asset),
            },
            separators=(",", ":"),
        )
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, UnicodeError, ValueError, json.JSONDecodeError, zipfile.BadZipFile) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
