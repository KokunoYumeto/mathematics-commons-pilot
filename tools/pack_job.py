#!/usr/bin/env python3
"""Build and replay one deterministic GitHub Release job ZIP."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import stat
import sys
import zipfile
from pathlib import Path, PurePosixPath


FIXED_TIME = (1980, 1, 1, 0, 0, 0)
CHUNK = 1024 * 1024
SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
ASSET_NAME = re.compile(r"^[a-z0-9][a-z0-9.-]*\.zip$")
GITHUB_ASSET_LIMIT = 2 * 1024**3


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while block := handle.read(CHUNK):
            digest.update(block)
    return digest.hexdigest().upper()


def safe_rel(path: Path, root: Path) -> str:
    relative = path.relative_to(root).as_posix()
    parsed = PurePosixPath(relative)
    parts = parsed.parts
    if (
        not relative
        or len(relative.encode("utf-8")) > 500
        or parsed.is_absolute()
        or not parts
        or relative != "/".join(parts)
        or any(part in {"", ".", ".."} for part in parts)
        or any(len(part.encode("utf-8")) > 255 for part in parts)
        or any(part.endswith((" ", ".")) for part in parts)
        or any(any(char in '<>:"|?*' for char in part) for part in parts)
        or any(ord(char) < 32 for char in relative)
    ):
        raise ValueError(f"unsafe member path: {relative!r}")
    return relative


def source_rows(root: Path, direct_only: bool = False) -> list[dict[str, object]]:
    if not root.is_dir():
        raise ValueError(f"source is not a directory: {root}")
    rows: list[dict[str, object]] = []
    candidates = root.iterdir() if direct_only else root.rglob("*")
    portable_prefixes: dict[str, str] = {}
    for path in sorted(candidates, key=lambda item: item.as_posix()):
        if path.is_symlink():
            raise ValueError(f"symbolic links are not allowed: {path}")
        if not path.is_file():
            continue
        relative = safe_rel(path, root)
        parts = PurePosixPath(relative).parts
        for index in range(1, len(parts) + 1):
            prefix = "/".join(parts[:index])
            folded = prefix.casefold()
            prior = portable_prefixes.get(folded)
            if prior is not None and prior != prefix:
                raise ValueError(f"case-insensitive path collision: {prior!r} / {prefix!r}")
            portable_prefixes[folded] = prefix
        size = path.stat().st_size
        if size <= 0:
            raise ValueError(f"zero-byte source members are not allowed: {relative}")
        rows.append(
            {
                "path": relative,
                "bytes": size,
                "sha256": sha256_file(path),
            }
        )
    if not rows:
        raise ValueError("source packet is empty")
    return rows


def tree_hash(rows: list[dict[str, object]]) -> tuple[int, str]:
    stream = "".join(
        f"{row['path']}\t{row['bytes']}\t{row['sha256']}\n" for row in rows
    ).encode("utf-8")
    return len(stream), hashlib.sha256(stream).hexdigest().upper()


def build_zip(root: Path, job_id: str, output: Path, rows: list[dict[str, object]]) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_suffix(output.suffix + ".tmp")
    if temporary.exists():
        temporary.unlink()
    try:
        with zipfile.ZipFile(
            temporary,
            "w",
            compression=zipfile.ZIP_DEFLATED,
            compresslevel=1,
            allowZip64=True,
        ) as archive:
            for row in rows:
                relative = str(row["path"])
                source = root / Path(relative)
                info = zipfile.ZipInfo(f"{job_id}/{relative}", FIXED_TIME)
                info.compress_type = zipfile.ZIP_DEFLATED
                info.create_system = 3
                info.external_attr = (stat.S_IFREG | 0o644) << 16
                info.flag_bits |= 0x800
                with source.open("rb") as reader, archive.open(info, "w") as writer:
                    while block := reader.read(CHUNK):
                        writer.write(block)
        os.replace(temporary, output)
        if output.stat().st_size >= GITHUB_ASSET_LIMIT:
            output.unlink()
            raise ValueError(f"built ZIP exceeds GitHub's per-asset limit: {output}")
    finally:
        if temporary.exists():
            temporary.unlink()


def replay_zip(output: Path, job_id: str, rows: list[dict[str, object]]) -> None:
    expected_names = [f"{job_id}/{row['path']}" for row in rows]
    with zipfile.ZipFile(output, "r") as archive:
        if archive.testzip() is not None:
            raise ValueError("ZIP CRC replay failed")
        names = archive.namelist()
        if names != expected_names:
            raise ValueError("ZIP member order or path set differs")
        for row, name in zip(rows, names, strict=True):
            info = archive.getinfo(name)
            if archive.comment != b"":
                raise ValueError("ZIP archive comment differs")
            if (
                info.date_time != FIXED_TIME
                or info.compress_type != zipfile.ZIP_DEFLATED
                or info.create_system != 3
                or info.external_attr >> 16 != (stat.S_IFREG | 0o644)
                or info.extra != b""
                or info.comment != b""
                or info.flag_bits
                != (0x800 if not name.isascii() else 0)
                or info.create_version != 20
                or info.extract_version != 20
                or info.internal_attr != 0
            ):
                raise ValueError(f"ZIP metadata differs: {name}")
            if info.file_size != row["bytes"]:
                raise ValueError(f"ZIP byte mismatch: {name}")
            digest = hashlib.sha256()
            with archive.open(info, "r") as handle:
                while block := handle.read(CHUNK):
                    digest.update(block)
            if digest.hexdigest().upper() != row["sha256"]:
                raise ValueError(f"ZIP hash mismatch: {name}")


def partitions(
    rows: list[dict[str, object]], maximum_source_bytes: int
) -> list[list[dict[str, object]]]:
    if maximum_source_bytes <= 0:
        raise ValueError("maximum part size must be positive")
    groups: list[list[dict[str, object]]] = []
    current: list[dict[str, object]] = []
    current_bytes = 0
    for row in rows:
        size = int(row["bytes"])
        if size > maximum_source_bytes:
            raise ValueError(
                f"one source member exceeds the safe release-part limit: {row['path']}"
            )
        if current and current_bytes + size > maximum_source_bytes:
            groups.append(current)
            current = []
            current_bytes = 0
        current.append(row)
        current_bytes += size
    if current:
        groups.append(current)
    return groups


def part_path(base: Path, index: int, count: int) -> Path:
    if count == 1:
        return base
    return base.with_name(f"{base.stem}.part{index:02d}{base.suffix}")


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_bytes(data)
    os.replace(temporary, path)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--job-id", required=True)
    parser.add_argument("--asset", required=True, type=Path)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--max-part-bytes", type=int, default=1_700_000_000)
    parser.add_argument("--direct-only", action="store_true")
    args = parser.parse_args()

    if SLUG.fullmatch(args.job_id) is None:
        raise SystemExit("job ID must be a lowercase ASCII slug")
    if ASSET_NAME.fullmatch(args.asset.name) is None:
        raise SystemExit("asset filename must be a lowercase portable .zip name")

    source_root = args.source.resolve()
    asset_base = args.asset.resolve()
    manifest_path = args.manifest.resolve()
    for label, candidate in (("asset", asset_base), ("manifest", manifest_path)):
        try:
            candidate.relative_to(source_root)
        except ValueError:
            pass
        else:
            raise ValueError(f"{label} path must not be inside the source root")
    if asset_base == manifest_path:
        raise ValueError("asset and manifest paths must be distinct")

    rows = source_rows(source_root, direct_only=args.direct_only)
    canonical_bytes, represented_tree = tree_hash(rows)
    groups = partitions(rows, args.max_part_bytes)
    assets: list[dict[str, object]] = []
    for index, group in enumerate(groups, start=1):
        output = part_path(asset_base, index, len(groups))
        if output == manifest_path:
            raise ValueError("manifest path collides with a generated asset part")
        build_zip(source_root, args.job_id, output, group)
        replay_zip(output, args.job_id, group)
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
                "zip_sha256": sha256_file(output),
            }
        )
    manifest = {
        "schema": "math-commons-job-asset/v1",
        "job_id": args.job_id,
        "wrapper_directory": args.job_id,
        "source_files": len(rows),
        "source_bytes": sum(int(row["bytes"]) for row in rows),
        "canonical_stream_bytes": canonical_bytes,
        "source_tree_sha256": represented_tree,
        "asset_count": len(assets),
        "assets": assets,
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
                "job_id": manifest["job_id"],
                "source_files": manifest["source_files"],
                "source_bytes": manifest["source_bytes"],
                "assets": manifest["assets"],
            },
            separators=(",", ":"),
        )
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, zipfile.BadZipFile) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
