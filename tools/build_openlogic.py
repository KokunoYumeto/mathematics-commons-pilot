#!/usr/bin/env python3
"""Build the exact Open Logic translation packet from pinned Git objects."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import zipfile
from pathlib import Path, PurePosixPath

from pack_job import (
    FIXED_TIME,
    build_zip,
    replay_zip,
    sha256_file,
    source_rows,
    tree_hash,
    write_json,
)


ROOT = Path(__file__).resolve().parents[1]
JOB_ID = "openlogic-v1"
ROOT_COMMIT = "1e960beff9ed7835bf3e3f1335e21af3439cd107"
ROOT_TREE = "45cad6b3bf0dd96985a7b3d1dc5c343984b0e1c8"
DOC_COMMIT = "b46686df0e06f302a7b75a74b379c802f7c7b565"
DOC_TREE = "0ca22cd55cde601a1f1f1c33c5757a5777164959"
CONTROL_FILES = (
    "BUILD.json",
    "CHECKPOINT.json",
    "JOB.json",
    "LOCAL.md",
    "NOTICE.md",
    "PROMPT.md",
    "QA.json",
    "QA.md",
    "RETURN.md",
    "README.md",
    "SOURCE.json",
    "START.md",
    "WEB.md",
)
HEX40 = re.compile(r"^[0-9a-f]{40}$")


def git(repo: Path, *args: str) -> bytes:
    result = subprocess.run(
        ["git", "-C", os.fspath(repo), *args],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return result.stdout


def exact_revision(repo: Path, commit: str, tree: str) -> None:
    if not repo.is_dir():
        raise ValueError(f"Git repository is missing: {repo}")
    observed_commit = git(repo, "rev-parse", commit).decode("ascii").strip()
    observed_tree = git(repo, "rev-parse", f"{commit}^{{tree}}").decode("ascii").strip()
    if observed_commit != commit or observed_tree != tree:
        raise ValueError(
            f"Git identity mismatch for {repo}: {observed_commit}/{observed_tree}"
        )


def tree_entries(repo: Path, commit: str) -> tuple[list[dict[str, object]], list[dict[str, str]]]:
    raw = git(repo, "ls-tree", "-r", "-z", "-l", commit)
    blobs: list[dict[str, object]] = []
    links: list[dict[str, str]] = []
    for record in raw.split(b"\0"):
        if not record:
            continue
        head, path_raw = record.split(b"\t", 1)
        mode, kind, oid, size_raw = head.decode("ascii").split(" ", 3)
        path = path_raw.decode("utf-8")
        parsed = PurePosixPath(path)
        if parsed.is_absolute() or any(part in {"", ".", ".."} for part in parsed.parts):
            raise ValueError(f"unsafe Git path: {path!r}")
        if kind == "commit":
            links.append({"mode": mode, "oid": oid, "path": path})
            continue
        if kind != "blob" or mode not in {"100644", "100755"} or HEX40.fullmatch(oid) is None:
            raise ValueError(f"unsupported Git entry: {record!r}")
        size = int(size_raw)
        blobs.append({"mode": mode, "oid": oid, "bytes": size, "path": path})
    blobs.sort(key=lambda row: str(row["path"]))
    links.sort(key=lambda row: row["path"])
    return blobs, links


def write_blob(repo: Path, oid: str, path: Path, expected_size: int) -> tuple[int, str]:
    data = git(repo, "cat-file", "blob", oid)
    if len(data) != expected_size:
        raise ValueError(f"Git blob size mismatch: {oid}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return len(data), hashlib.sha256(data).hexdigest().upper()


def internal_manifest(stage: Path) -> None:
    rows = source_rows(stage)
    lines = [
        f"{row['sha256']}\t{row['bytes']}\t{row['path']}\n"
        for row in rows
        if row["path"] != "MANIFEST.sha256"
    ]
    (stage / "MANIFEST.sha256").write_bytes("".join(lines).encode("utf-8"))


def mode_hash(rows: list[dict[str, object]]) -> tuple[int, str]:
    stream = "".join(
        f"{row['path']}\t{row.get('mode', '100644')}\t{row['bytes']}\t{row['sha256']}\n"
        for row in rows
    ).encode("utf-8")
    return len(stream), hashlib.sha256(stream).hexdigest().upper()


def release_controls(controls: Path, allow_pending: bool) -> None:
    try:
        job = json.loads((controls / "JOB.json").read_text(encoding="utf-8"))
        build = json.loads((controls / "BUILD.json").read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise ValueError(f"malformed Open Logic control JSON: {exc}") from exc
    if not isinstance(job, dict) or not isinstance(build, dict):
        raise ValueError("Open Logic control JSON roots must be objects")
    if allow_pending:
        return
    if job.get("state") != "source_packet_ready":
        raise ValueError("JOB.json is not finalized for release")
    if build.get("state") != "cold_replay_pass_with_observed_warnings":
        raise ValueError("BUILD.json does not contain a passing cold replay")
    if (
        build.get("source_commit") != ROOT_COMMIT
        or build.get("source_tree") != ROOT_TREE
        or build.get("source_files") != 792
        or build.get("source_bytes") != 4_302_140
        or len(build.get("targets", [])) != 2
    ):
        raise ValueError("BUILD.json source or target boundary differs")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root-repo", required=True, type=Path)
    parser.add_argument("--doc-repo", required=True, type=Path)
    parser.add_argument("--stage", required=True, type=Path)
    parser.add_argument("--asset", required=True, type=Path)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--allow-pending", action="store_true")
    args = parser.parse_args()

    root_repo = args.root_repo.resolve()
    doc_repo = args.doc_repo.resolve()
    stage = args.stage.resolve()
    asset = args.asset.resolve()
    manifest_path = args.manifest.resolve()
    if stage.exists():
        raise ValueError(f"stage already exists: {stage}")
    if asset.name != f"{JOB_ID}.zip":
        raise ValueError(f"asset must be named {JOB_ID}.zip")
    for label, path in (("asset", asset), ("manifest", manifest_path)):
        try:
            path.relative_to(stage)
        except ValueError:
            pass
        else:
            raise ValueError(f"{label} must be outside the stage")

    exact_revision(root_repo, ROOT_COMMIT, ROOT_TREE)
    exact_revision(doc_repo, DOC_COMMIT, DOC_TREE)
    controls = ROOT / "kits" / "openlogic"
    release_controls(controls, args.allow_pending)
    root_blobs, root_links = tree_entries(root_repo, ROOT_COMMIT)
    doc_blobs, doc_links = tree_entries(doc_repo, DOC_COMMIT)
    if root_links != [{"mode": "160000", "oid": DOC_COMMIT, "path": "doc"}]:
        raise ValueError(f"unexpected root gitlinks: {root_links}")
    if doc_links:
        raise ValueError(f"unexpected wiki gitlinks: {doc_links}")
    if len(root_blobs) != 792 or sum(int(row["bytes"]) for row in root_blobs) != 4_302_140:
        raise ValueError("root blob aggregate differs from the reviewed boundary")
    if len(doc_blobs) != 18 or sum(int(row["bytes"]) for row in doc_blobs) != 58_769:
        raise ValueError("wiki blob aggregate differs from the reviewed boundary")

    stage.mkdir(parents=True)
    source_rows_tsv = ["path\tmode\tbytes\tgit_blob\tsha256\n"]
    for row in root_blobs:
        relative = str(row["path"])
        size, digest = write_blob(
            root_repo,
            str(row["oid"]),
            stage / "source" / Path(relative),
            int(row["bytes"]),
        )
        source_rows_tsv.append(
            f"{relative}\t{row['mode']}\t{size}\t{row['oid']}\t{digest}\n"
        )
    (stage / "SOURCE_TREE.tsv").write_bytes("".join(source_rows_tsv).encode("utf-8"))

    for name in CONTROL_FILES:
        source = controls / name
        if not source.is_file():
            raise ValueError(f"packet control is missing: {source}")
        shutil.copyfile(source, stage / name)

    internal_manifest(stage)
    rows = source_rows(stage)
    source_modes = {f"source/{row['path']}": row["mode"] for row in root_blobs}
    for row in rows:
        if row["path"] in source_modes:
            row["mode"] = source_modes[row["path"]]
    canonical_bytes, represented_tree = tree_hash(rows)
    mode_stream_bytes, mode_tree = mode_hash(rows)
    build_zip(stage, JOB_ID, asset, rows)
    replay_zip(asset, JOB_ID, rows)
    manifest = {
        "schema": "math-commons-job-asset/v1",
        "job_id": JOB_ID,
        "wrapper_directory": JOB_ID,
        "source_files": len(rows),
        "source_bytes": sum(int(row["bytes"]) for row in rows),
        "canonical_stream_bytes": canonical_bytes,
        "source_tree_sha256": represented_tree,
        "mode_stream_bytes": mode_stream_bytes,
        "mode_tree_sha256": mode_tree,
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
                "root_blobs": len(root_blobs),
                "root_bytes": sum(int(row["bytes"]) for row in root_blobs),
                "wiki_blobs_pinned_excluded": len(doc_blobs),
                "packet_files": len(rows),
                "packet_bytes": manifest["source_bytes"],
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
    except (OSError, ValueError, subprocess.CalledProcessError, zipfile.BadZipFile) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
