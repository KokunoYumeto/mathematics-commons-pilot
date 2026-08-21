#!/usr/bin/env python3
"""Regenerate the four explicitly identified stale packet manifests.

The script is intentionally bounded: it accepts one packet base directory and
touches only the four named packet manifests. Historical validation receipts
remain immutable packet members; the new Commons R2 admission receipt supplies
the fresh independent validation boundary.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import os
import zipfile
from pathlib import Path


CHUNK = 1024 * 1024
FLAT_TARGETS = {
    "HECKE_VORLESUNGEN_1923_REPAIR": "98_PACKET_MANIFEST_SHA256.tsv",
    "KRONECKER_GRUNDZUEGE_1882_REPAIR": "98_PACKET_MANIFEST_SHA256.tsv",
}
STRUCTURED_TARGETS = {
    "KHAYYAM_ALGEBRA_REPAIR": "07_PACKET_MANIFEST.tsv",
    "SEKI_HATSUBI_SANPO_REPAIR": "07_PACKET_MANIFEST.tsv",
}


def sha256_stream(handle: object) -> str:
    digest = hashlib.sha256()
    while block := handle.read(CHUNK):
        digest.update(block)
    return digest.hexdigest().upper()


def sha256_file(path: Path) -> str:
    with path.open("rb") as handle:
        return sha256_stream(handle)


def atomic_write(path: Path, data: bytes) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_bytes(data)
    os.replace(temporary, path)


def regenerate_flat(packet: Path, manifest_name: str) -> None:
    manifest = packet / manifest_name
    rows: list[str] = []
    for path in sorted(packet.iterdir(), key=lambda item: item.name.casefold()):
        if not path.is_file() or path.name == manifest_name:
            continue
        rows.append(f"{path.name}\t{path.stat().st_size}\t{sha256_file(path)}\n")
    atomic_write(manifest, "".join(rows).encode("utf-8"))


def nested_zip_bytes(packet: Path, archive_name: str) -> bytes:
    direct = packet / archive_name
    if direct.is_file():
        return direct.read_bytes()
    found: list[bytes] = []
    for outer in sorted(packet.glob("*.zip"), key=lambda item: item.name.casefold()):
        with zipfile.ZipFile(outer, "r") as archive:
            for info in archive.infolist():
                if not info.is_dir() and Path(info.filename).name == archive_name:
                    found.append(archive.read(info))
    if len(found) != 1:
        raise ValueError(
            f"{packet.name}: expected one nested {archive_name}, observed {len(found)}"
        )
    return found[0]


def member_set(packet: Path, archive_name: str) -> tuple[int, str]:
    payload = nested_zip_bytes(packet, archive_name)
    rows: list[tuple[str, int, str]] = []
    with zipfile.ZipFile(io.BytesIO(payload), "r") as archive:
        seen: set[str] = set()
        for info in archive.infolist():
            if info.is_dir():
                continue
            if info.filename in seen:
                raise ValueError(f"{packet.name}: duplicate member {info.filename}")
            seen.add(info.filename)
            with archive.open(info, "r") as handle:
                rows.append((info.filename, info.file_size, sha256_stream(handle)))
    # Python's Unicode string order is the advertised ordinal order.  The
    # canonical aggregate has LF separators but deliberately no final LF.
    rows.sort(key=lambda row: row[0])
    stream = "\n".join(f"{name}\t{size}\t{digest}" for name, size, digest in rows)
    return len(rows), hashlib.sha256(stream.encode("utf-8")).hexdigest().upper()


def regenerate_structured(packet: Path, manifest_name: str) -> None:
    manifest = packet / manifest_name
    original = manifest.read_text(encoding="utf-8").splitlines()
    parsed = list(csv.reader(original, delimiter="\t"))
    if not parsed or parsed[0][:4] != [
        "record_type",
        "path_or_set",
        "bytes_or_count",
        "sha256",
    ]:
        raise ValueError(f"{packet.name}: unexpected structured manifest header")
    output: list[list[str]] = [parsed[0]]
    for row in parsed[1:]:
        if len(row) != 5:
            raise ValueError(f"{packet.name}: malformed manifest row")
        record_type, logical, _count, _digest, role = row
        if record_type == "OUTER_FILE":
            path = packet / logical
            if not path.is_file():
                raise ValueError(f"{packet.name}: missing outer file {logical}")
            output.append(
                [record_type, logical, str(path.stat().st_size), sha256_file(path), role]
            )
        elif record_type == "ARCHIVE_MEMBER_SET":
            suffix = "::regular_members"
            if not logical.endswith(suffix):
                raise ValueError(f"{packet.name}: malformed archive set {logical}")
            archive_name = logical[: -len(suffix)]
            count, digest = member_set(packet, archive_name)
            output.append([record_type, logical, str(count), digest, role])
        else:
            raise ValueError(f"{packet.name}: unknown record type {record_type}")
    stream = io.StringIO(newline="")
    writer = csv.writer(stream, delimiter="\t", lineterminator="\n")
    writer.writerows(output)
    atomic_write(manifest, stream.getvalue().encode("utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--packet-root", required=True, type=Path)
    args = parser.parse_args()
    packet_root = args.packet_root.resolve()
    for packet_name, manifest_name in FLAT_TARGETS.items():
        regenerate_flat(packet_root / packet_name, manifest_name)
    for packet_name, manifest_name in STRUCTURED_TARGETS.items():
        regenerate_structured(packet_root / packet_name, manifest_name)
    for packet_name, manifest_name in {**FLAT_TARGETS, **STRUCTURED_TARGETS}.items():
        path = packet_root / packet_name / manifest_name
        print(
            f"PASS {packet_name}: {manifest_name} / {path.stat().st_size} / "
            f"{sha256_file(path)}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
