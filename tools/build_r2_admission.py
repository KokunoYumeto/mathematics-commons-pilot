#!/usr/bin/env python3
"""Build the frozen, local-only R2 packet-admission evidence.

This is deliberately bounded to the 28 jobs already present in the R1 catalog.
It never writes producer packets or release assets.  It verifies their current
bytes, replays the packet-native manifests and deterministic release ZIPs, and
then writes two sanitized public receipts plus catalog/job-meta.json v2.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import re
import sys
import zipfile
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any, BinaryIO

import pack_job


ROOT = Path(__file__).resolve().parents[1]
META_PATH = ROOT / "catalog" / "job-meta.json"
ASSET_MANIFEST_ROOT = ROOT / "catalog" / "assets"
RECEIPT_ROOT = ROOT / "catalog" / "receipts"
ADMISSION_PATH = RECEIPT_ROOT / "r2-admission.json"
HARDENING_PATH = RECEIPT_ROOT / "no-failure-hardening.json"
TRANSLATION_ASSET_MANIFEST = ASSET_MANIFEST_ROOT / "translation-kit.json"
DATE = "2026-08-21"
RELEASE_TAG = "jobs-2026-08-21-r2"
MAX_PART_SOURCE_BYTES = 1_700_000_000
CHUNK = 1024 * 1024

POLICY_MARKER = "NO_FAILURE_CONTINUITY_POLICY_V1"
POLICY_OPEN = "<!-- NO_FAILURE_CONTINUITY_POLICY_V1 -->"
POLICY_CLOSE = "<!-- /NO_FAILURE_CONTINUITY_POLICY_V1 -->"
POLICY_REQUIRED = (
    "there is no assumed time limit",
    "The only response statuses are `STATUS: IN_PROGRESS` and `STATUS: COMPLETE`",
    "only when the platform forces a response split",
    "from the attached scans and comparators",
    "retain the exact authority image or crop",
    "An internal audit `FAIL` is diagnostic only",
    "brand-new nonpatching audit from clean state and repeat until `PASS`",
    "Completion is allowed only with `PASS` and the newest cumulative trio",
)
TEXT_EXTENSIONS = {".md", ".txt", ".json", ".tsv", ".csv"}
HISTORICAL_NAME = re.compile(
    r"(?i)(RECEIPT|PRE_SCOPE|_UNTRUSTED|PRIOR_|SALVAGE_(?:ARCHIVE|MEMBER)|"
    r"SOURCE_ACQUISITION|PACKET_COLD_VALIDATION_NOTES|DURABLE_ACTION|"
    r"OCR_WITNESS|METADATA_API)"
)
POLICY_TARGET = re.compile(
    r"(?i)(READ(?:_|\s)*(?:THIS|ME)?(?:_|\s)*FIRST|START_HERE|GOVERN|"
    r"CONTRACT|PROTOCOL|ORDERED_DRIVER|PROMPT.*\.(?:md|txt)$|SESSION_PROMPTS|"
    r"LITERAL.*PROMPTS|REQUIRED_END_STATE)"
)
AUDIT_TARGET = re.compile(
    r"(?i)(INITIAL_STATE|CHECKPOINT|SCHEMA|TEMPLATE|SESSION_PLAN|"
    r"PHASE_AND_RANGE|DISPOSITION)"
)
FORBIDDEN_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("ordinary_hold", re.compile(r"(?i)\bHOLD\b")),
    (
        "terminal_fail_status",
        re.compile(
            r"(?i)STATUS:\s*FAIL(?:ED)?|status\s*[:=]\s*FAILED|"
            r'"status"\s*:\s*"FAILED"'
        ),
    ),
    (
        "separate_authorized_remediation",
        re.compile(
            r"(?i)separate(?:ly)?\s+authori[sz]|"
            r"authori[sz](?:e|ed|ation).{0,100}remedi|"
            r"remedi.{0,100}authori[sz]"
        ),
    ),
    ("context_pressure_budget", re.compile(r"(?i)context pressure")),
    (
        "terminal_fail_handoff",
        re.compile(
            r"(?i)(?:terminal.{0,40}FAIL|FAIL.{0,100}"
            r"(?:halts|terminal|hand(?:ed)? back|return(?:s)? status|"
            r"requires.{0,40}authori[sz]|stop and report))"
        ),
    ),
    (
        "resolvable_stop",
        re.compile(
            r"(?i)(?:mismatch|conflict|defect|missing predecessor).{0,120}"
            r"(?:return to (?:the )?user|ask (?:the )?user|hand(?:ed)? back|\bstop\b)"
        ),
    ),
    (
        "in_progress_not_platform_split",
        re.compile(
            r"(?i)(?:If unfinished|If the audit(?: procedure)? is unfinished|"
            r"If the active prompt is unfinished|Use IN_PROGRESS whenever|"
            r"Use IN_PROGRESS while the audit procedure is unfinished|"
            r"While a prompt is unfinished, status is IN_PROGRESS|"
            r"A mismatch keeps [^.;]+ IN_PROGRESS|If verification cannot finish).{0,500}"
        ),
    ),
    (
        "forbidden_response_status",
        re.compile(r"(?i)STATUS:\s*(?:SOURCE_BYTES_MISSING|BLOCKED|WAITING|ERROR|ABORTED)"),
    ),
)


@dataclass(frozen=True)
class FrozenJob:
    packet_id: str
    start_file: str
    prompt_file: str
    prompt_count: int
    prompt_pattern: str
    packet_manifest: str


def job(
    packet_id: str,
    prompt_file: str,
    prompt_count: int,
    prompt_pattern: str = r"(?m)^#\s+(?:P)?\d{2}(?:\s|$)",
    *,
    start_file: str = "00_READ_FIRST.md",
    packet_manifest: str = "98_PACKET_MANIFEST_SHA256.tsv",
) -> FrozenJob:
    return FrozenJob(
        packet_id,
        start_file,
        prompt_file,
        prompt_count,
        prompt_pattern,
        packet_manifest,
    )


# The mapping is intentionally explicit.  No directory discovery can add a job.
FROZEN: dict[str, FrozenJob] = {
    "al-battani-nallino-opus-astronomicum-1899-1907": job(
        "AL_BATTANI_OPUS_ASTRONOMICUM_NALLINO_1899_1907_REPAIR",
        "04_ALL_45_LITERAL_SESSION_PROMPTS.md", 45,
    ),
    "al-khwarizmi-al-jabr-cairo-1939": job(
        "AL_KHWARIZMI_AL_JABR_1939_EDITION_REPAIR",
        "02_ALL_13_LITERAL_SESSION_PROMPTS.md", 13,
    ),
    "al-tusi-quadrilateral-french-1891": job(
        "AL_TUSI_ATTRIBUTED_QUADRILATERAL_1891_FRENCH_EDITION_REPAIR",
        "29_ALL_39_LITERAL_SESSION_PROMPTS.md", 39,
    ),
    "aryabhatiya-jyotihsastram-1906": job(
        "ARYABHATIYA_1906_STRATIFIED_REPAIR",
        "05_ALL_14_LITERAL_SESSION_PROMPTS.md", 14,
    ),
    "bhaskara-bijaganita-apte-1930": job(
        "BHASKARA_II_BIJAGANITA_1930_EDITION_REPAIR",
        "04_ALL_22_LITERAL_SESSION_PROMPTS.md", 22,
    ),
    "bhaskara-lilavati-1907": job(
        "BHASKARA_II_LILAVATI_1907_EDITION_REPAIR",
        "04_ALL_28_LITERAL_SESSION_PROMPTS.md", 28,
    ),
    "cayley-collected-papers-v01": job(
        "CAYLEY_AUTHOR_CORPUS_REPAIR", "04_ALL_45_LITERAL_SESSION_PROMPTS.md", 45,
        r"(?m)^##\s+Session\s+\d{2}\b",
    ),
    "clebsch-gordan-abelian-functions-1866": job(
        "CLEBSCH_GORDAN_THEORIE_DER_ABELSCHEN_FUNCTIONEN_1866_GLOBAL_PACKET_CORRECTED_COMPLETE",
        "04_ALL_45_LITERAL_SESSION_PROMPTS.md", 45,
    ),
    "dedekind-werke-v01": job(
        "DEDEKIND_GMW_I_REPAIR", "02_ALL_41_LITERAL_SESSION_PROMPTS.txt", 41,
        start_file="00_READ_FIRST.txt", packet_manifest="07_PACKET_MANIFEST.tsv",
    ),
    "dedekind-werke-v03": job(
        "DEDEKIND_GMW_III_REPAIR", "02_SESSION_PROMPTS.txt", 45,
        r"(?m)^DEDEKIND-III-R\d{2}\b",
        start_file="00_READ_FIRST.txt", packet_manifest="07_PACKET_MANIFEST.tsv",
    ),
    "gauss-werke-v02-with-nachtrag": job(
        "Gauss_Werke_Band_II_Repair", "04_SESSION_PROMPTS.md", 45,
        r"(?m)^##\s+Session\s+\d{2}\b",
    ),
    "gibbs-scientific-papers-v01": job(
        "GIBBS_TIER_A_AUTHORIAL_REPAIR_20260820_R1",
        "04_ALL_44_LITERAL_SESSION_PROMPTS.md", 44,
        packet_manifest="99_MANIFEST_SHA256.json",
    ),
    "gordan-de-linea-geodetica-1862": job(
        "GORDAN_DE_LINEA_GEODETICA_1862_REPAIR",
        "04_ALL_05_LITERAL_SESSION_PROMPTS.md", 5,
        start_file="00_READ_ME_FIRST.md", packet_manifest="12_PACKET_MANIFEST_SHA256.csv",
    ),
    "gordan-formensystem-binaerer-formen": job(
        "GORDAN_FORMENSYSTEM_BINAERER_FORMEN_REPAIR",
        "04_ALL_07_LITERAL_SESSION_PROMPTS.md", 7,
        start_file="00_READ_ME_FIRST.md", packet_manifest="12_PACKET_MANIFEST_SHA256.csv",
    ),
    "gordan-transformation-thetafunctionen-1863": job(
        "GORDAN_TRANSFORMATION_THETAFUNCTIONEN_REPAIR",
        "04_ALL_02_LITERAL_SESSION_PROMPTS.md", 2,
        start_file="00_READ_ME_FIRST.md", packet_manifest="12_PACKET_MANIFEST_SHA256.csv",
    ),
    "gordan-invariantentheorie-v01-1885": job(
        "GORDAN_VORLESUNGEN_UEBER_INVARIANTENTHEORIE_BAND_I_REPAIR",
        "04_ALL_22_LITERAL_SESSION_PROMPTS.md", 22,
    ),
    "gordan-invariantentheorie-v02-1887": job(
        "GORDAN_VORLESUNGEN_UEBER_INVARIANTENTHEORIE_BAND_II_REPAIR",
        "GORDAN_BAND_II_38_LITERAL_PROMPTS.md", 38,
        r"(?m)^<!-- BEGIN_LITERAL_PROMPT P\d{2} -->$",
        start_file="READ_FIRST.md",
    ),
    "hecke-algebraische-zahlen-1923": job(
        "HECKE_VORLESUNGEN_1923_REPAIR", "04_ALL_29_LITERAL_SESSION_PROMPTS.md", 29,
        r"(?m)^#\s+P\d{2}(?:\s|$)",
    ),
    "khayyam-columbia-ms-or34-algebra": job(
        "KHAYYAM_ALGEBRA_REPAIR", "02_ALL_13_LITERAL_SESSION_PROMPTS.txt", 13,
        start_file="00_READ_FIRST.txt", packet_manifest="07_PACKET_MANIFEST.tsv",
    ),
    "klein-fricke-modulfunctionen-v01-1890": job(
        "KLEIN_FRICKE_MODULFUNCTIONEN_BAND_I_REPAIR",
        "04_ALL_45_LITERAL_SESSION_PROMPTS.md", 45,
    ),
    "kronecker-grundzuege-1882": job(
        "KRONECKER_GRUNDZUEGE_1882_REPAIR", "04_ALL_16_LITERAL_SESSION_PROMPTS.md", 16,
        r"(?m)^#\s+P\d{2}(?:\s|$)",
    ),
    "mikami-development-mathematics-china-japan-1913": job(
        "MIKAMI_DEVELOPMENT_MATHEMATICS_1913_REPAIR",
        "02_ORDERED_PROMPTS_EXACTLY_45.md", 45,
        packet_manifest="99_PACKET_MANIFEST_SHA256.tsv",
    ),
    "picard-traite-analyse-v01-1891": job(
        "PICARD_TRAITE_ANALYSE_TOME_I_1891_REPAIR",
        "04_ALL_45_LITERAL_SESSION_PROMPTS.md", 45,
    ),
    "poincare-oeuvres-v01-1928": job(
        "POINCARE_OEUVRES_TOME_I_REPAIR", "04_ALL_45_LITERAL_SESSION_PROMPTS.md", 45,
    ),
    "seki-hatsubi-sanpo": job(
        "SEKI_HATSUBI_SANPO_REPAIR", "02_ALL_03_LITERAL_SESSION_PROMPTS.txt", 3,
        start_file="00_READ_FIRST.txt", packet_manifest="07_PACKET_MANIFEST.tsv",
    ),
    "weber-lehrbuch-algebra-v01": job(
        "WEBER_LEHRBUCH_BAND_I_REPAIR", "04_ALL_45_LITERAL_SESSION_PROMPTS.md", 45,
    ),
    "weber-lehrbuch-algebra-v02": job(
        "WEBER_LEHRBUCH_BAND_II_REPAIR", "04_ALL_45_LITERAL_SESSION_PROMPTS.md", 45,
    ),
    "weber-lehrbuch-algebra-v03": job(
        "WEBER_LEHRBUCH_BAND_III_REPAIR", "04_ALL_45_LITERAL_SESSION_PROMPTS.md", 45,
    ),
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


def load_json(path: Path) -> dict[str, Any]:
    data = path.read_bytes()
    if data.startswith(b"\xef\xbb\xbf") or b"\r" in data:
        raise ValueError(f"JSON must be UTF-8 LF without BOM: {path}")
    value = json.loads(data.decode("utf-8"), object_pairs_hook=object_pairs)
    if not isinstance(value, dict):
        raise ValueError(f"JSON root is not an object: {path}")
    return value


def json_bytes(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_bytes(json_bytes(value))
    os.replace(temporary, path)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def audit_snapshot_sha256(rows: list[dict[str, object]]) -> str:
    """Match the validator's frozen PowerShell-name-sort snapshot stream."""
    ordered = sorted(rows, key=lambda row: str(row["path"]).casefold())
    stream = "".join(
        f"{row['path']}\t{row['bytes']}\t{row['sha256']}\n" for row in ordered
    ).encode("utf-8")
    return sha256_bytes(stream)


def hash_stream(handle: BinaryIO) -> tuple[int, str]:
    total = 0
    digest = hashlib.sha256()
    while block := handle.read(CHUNK):
        total += len(block)
        digest.update(block)
    return total, digest.hexdigest().upper()


def file_identity(path: Path, *, basename_only: bool = True) -> dict[str, object]:
    result: dict[str, object] = {
        "bytes": path.stat().st_size,
        "sha256": pack_job.sha256_file(path),
    }
    result["basename" if basename_only else "path"] = (
        path.name if basename_only else path.relative_to(ROOT).as_posix()
    )
    return {key: result[key] for key in (("basename", "bytes", "sha256") if basename_only else ("path", "bytes", "sha256"))}


def row_identity(row: dict[str, object]) -> dict[str, object]:
    return {
        "basename": str(row["path"]),
        "bytes": int(row["bytes"]),
        "sha256": str(row["sha256"]),
    }


def safe_member(name: str) -> str:
    normalized = name.replace("\\", "/")
    directory = normalized.endswith("/")
    core = normalized[:-1] if directory else normalized
    parsed = PurePosixPath(core)
    if (
        not core
        or parsed.is_absolute()
        or any(part in {"", ".", ".."} for part in parsed.parts)
        or core != "/".join(parsed.parts)
    ):
        raise ValueError(f"unsafe archive member: {name!r}")
    return core + ("/" if directory else "")


def policy_findings(label: str, text: str) -> list[dict[str, object]]:
    findings: list[dict[str, object]] = []
    for number, line in enumerate(text.splitlines(), 1):
        for code, pattern in FORBIDDEN_PATTERNS:
            if not pattern.search(line):
                continue
            lower = line.lower()
            if code == "separate_authorized_remediation" and "no separate authorization" in lower:
                continue
            if code == "in_progress_not_platform_split" and "platform forces a response split" in lower:
                continue
            if code in {"terminal_fail_handoff", "resolvable_stop"} and any(
                phrase in lower
                for phrase in (
                    "cannot terminate", "never a terminal", "no separate authorization",
                    "do not stop", "without stopping",
                )
            ):
                continue
            findings.append({"location": label, "line": number, "code": code})
    return findings


def policy_scan(packet: Path, spec: FrozenJob, rows_by_path: dict[str, dict[str, object]]) -> dict[str, object]:
    audited: list[dict[str, object]] = []
    marker_files: list[dict[str, object]] = []
    findings: list[dict[str, object]] = []
    direct_files = sorted((path for path in packet.iterdir() if path.is_file()), key=lambda p: p.name)
    for path in direct_files:
        if path.suffix.lower() not in TEXT_EXTENSIONS or HISTORICAL_NAME.search(path.name):
            continue
        if not (POLICY_TARGET.search(path.name) or AUDIT_TARGET.search(path.name)):
            continue
        try:
            text = path.read_bytes().decode("utf-8-sig")
        except UnicodeDecodeError as exc:
            raise ValueError(f"controlling text is not UTF-8: {spec.packet_id}/{path.name}") from exc
        audited.append(row_identity(rows_by_path[path.name]))
        findings.extend(policy_findings(path.name, text))
        if POLICY_TARGET.search(path.name) and path.suffix.lower() in {".md", ".txt"}:
            if text.count(POLICY_OPEN) != 1 or text.count(POLICY_CLOSE) != 1:
                raise ValueError(f"missing or duplicate hardened policy: {spec.packet_id}/{path.name}")
            start = text.index(POLICY_OPEN)
            end = text.index(POLICY_CLOSE, start) + len(POLICY_CLOSE)
            block = text[start:end]
            missing = [phrase for phrase in POLICY_REQUIRED if phrase not in block]
            if missing:
                raise ValueError(f"incomplete hardened policy in {spec.packet_id}/{path.name}: {missing}")
            marker_files.append(row_identity(rows_by_path[path.name]))

    if spec.start_file not in {row["basename"] for row in marker_files}:
        raise ValueError(f"start file lacks hardened policy: {spec.packet_id}/{spec.start_file}")
    if spec.prompt_file not in {row["basename"] for row in marker_files}:
        raise ValueError(f"prompt file lacks hardened policy: {spec.packet_id}/{spec.prompt_file}")

    # Replay the same bounded embedded-control surface used by the hardener.
    embedded_count = 0
    for archive_path in direct_files:
        upper = archive_path.name.upper()
        if not (
            archive_path.suffix.lower() == ".zip"
            and (re.search(r"S00.*STATE.*\.ZIP$", upper) or archive_path.name == "07_OUTPUT_SCHEMA_TEMPLATES.zip")
        ):
            continue
        with zipfile.ZipFile(archive_path, "r") as archive:
            bad = archive.testzip()
            if bad is not None:
                raise ValueError(f"embedded control ZIP CRC failure: {spec.packet_id}/{archive_path.name}::{bad}")
            seen: set[str] = set()
            for info in archive.infolist():
                name = safe_member(info.filename)
                if name in seen:
                    raise ValueError(f"duplicate embedded control path: {spec.packet_id}/{archive_path.name}::{name}")
                seen.add(name)
                if info.is_dir() or Path(name).suffix.lower() not in TEXT_EXTENSIONS:
                    continue
                if not (
                    name.startswith(("control/", "build/", "state/"))
                    or re.search(r"(?i)README|RETURN|CHECKPOINT", name)
                ):
                    continue
                try:
                    text = archive.read(info).decode("utf-8-sig")
                except UnicodeDecodeError:
                    continue
                embedded_count += 1
                findings.extend(policy_findings(f"{archive_path.name}::{name}", text))

    if findings:
        raise ValueError(f"forbidden controlling outcomes in {spec.packet_id}: {findings[:5]}")
    return {
        "result": "PASS",
        "direct_controlling_files_audited": len(audited),
        "policy_marker_files": marker_files,
        "embedded_controlling_files_audited": embedded_count,
        "forbidden_controlling_outcome_conditions": 0,
    }


def prompt_replay(packet: Path, spec: FrozenJob, rows_by_path: dict[str, dict[str, object]]) -> dict[str, object]:
    path = packet / spec.prompt_file
    text = path.read_bytes().decode("utf-8-sig")
    matches = re.findall(spec.prompt_pattern, text)
    if len(matches) != spec.prompt_count:
        raise ValueError(
            f"prompt count differs for {spec.packet_id}: {len(matches)} != {spec.prompt_count}"
        )
    return {
        "declared_count": spec.prompt_count,
        "replayed_count": len(matches),
        "count_rule": "workload-derived; no global minimum or maximum",
        "start_file": row_identity(rows_by_path[spec.start_file]),
        "prompt_file": row_identity(rows_by_path[spec.prompt_file]),
    }


def verify_flat_rows(
    packet: Path,
    rows: list[dict[str, str]],
    all_rows_by_path: dict[str, dict[str, object]],
    manifest_name: str,
) -> dict[str, object]:
    if not rows:
        raise ValueError(f"empty native manifest: {packet.name}/{manifest_name}")
    keys = rows[0].keys()
    path_key = next((key for key in ("filename", "relative_path", "path", "file", "name") if key in keys), None)
    bytes_key = next((key for key in ("bytes", "size") if key in keys), None)
    hash_key = next((key for key in ("sha256", "SHA256") if key in keys), None)
    if not path_key or not bytes_key or not hash_key:
        raise ValueError(f"unknown native-manifest columns: {packet.name}/{manifest_name}")
    declared: set[str] = set()
    for row in rows:
        name = str(row[path_key])
        if Path(name).name != name or "/" in name or "\\" in name or name in declared:
            raise ValueError(f"unsafe/duplicate native-manifest path: {packet.name}/{name}")
        declared.add(name)
        actual = all_rows_by_path.get(name)
        if actual is None:
            raise ValueError(f"native-manifest member missing: {packet.name}/{name}")
        if int(str(row[bytes_key])) != actual["bytes"] or str(row[hash_key]).upper() != actual["sha256"]:
            raise ValueError(f"native-manifest identity differs: {packet.name}/{name}")
    omitted = sorted(set(all_rows_by_path) - declared)
    allowed = {
        name for name in omitted
        if name == manifest_name or re.search(r"(?i)(VALIDATION.*RECEIPT|PACKET_VALIDATION)", name)
    }
    if set(omitted) != allowed:
        raise ValueError(f"native manifest has unexplained omissions in {packet.name}: {sorted(set(omitted)-allowed)}")
    return {
        "format": "flat",
        "result": "PASS",
        "declared_outer_files": len(declared),
        "excluded_direct_files": omitted,
    }


def aggregate_archive(archive: zipfile.ZipFile) -> tuple[int, int, str]:
    rows: list[tuple[str, int, str]] = []
    names: set[str] = set()
    total = 0
    bad = archive.testzip()
    if bad is not None:
        raise ValueError(f"archive CRC replay failed: {bad}")
    for info in archive.infolist():
        name = safe_member(info.filename)
        if name in names:
            raise ValueError(f"duplicate archive member path: {name}")
        names.add(name)
        if info.is_dir():
            continue
        with archive.open(info, "r") as handle:
            size, digest = hash_stream(handle)
        if size != info.file_size:
            raise ValueError(f"archive member byte length differs: {name}")
        rows.append((name, size, digest))
        total += size
    # Python's Unicode code-point order is ordinal for the ASCII/path surface
    # used by these manifests.  The stream has LF separators and no final LF.
    rows.sort(key=lambda row: row[0])
    stream = "\n".join(f"{name}\t{size}\t{digest}" for name, size, digest in rows).encode("utf-8")
    return len(rows), total, sha256_bytes(stream)


def open_named_archive(packet: Path, target: str) -> tuple[zipfile.ZipFile, io.BytesIO | None]:
    direct = packet / target
    if direct.is_file():
        return zipfile.ZipFile(direct, "r"), None
    matches: list[tuple[Path, zipfile.ZipInfo]] = []
    for outer in sorted(packet.glob("*.zip"), key=lambda path: path.name):
        with zipfile.ZipFile(outer, "r") as archive:
            for info in archive.infolist():
                if info.is_dir():
                    continue
                normalized = safe_member(info.filename)
                if normalized == target or normalized.endswith("/" + target):
                    matches.append((outer, info))
    if len(matches) != 1:
        raise ValueError(f"nested archive lookup is not unique: {packet.name}/{target}: {len(matches)}")
    outer_path, info = matches[0]
    with zipfile.ZipFile(outer_path, "r") as outer:
        payload = io.BytesIO(outer.read(info))
    return zipfile.ZipFile(payload, "r"), payload


def verify_structured_rows(
    packet: Path,
    rows: list[dict[str, str]],
    all_rows_by_path: dict[str, dict[str, object]],
    manifest_name: str,
) -> dict[str, object]:
    outer: set[str] = set()
    aggregate_rows = 0
    aggregate_members = 0
    for row in rows:
        record_type = row.get("record_type")
        name = str(row.get("path_or_set", ""))
        if record_type == "OUTER_FILE":
            if Path(name).name != name or name in outer:
                raise ValueError(f"unsafe/duplicate structured outer path: {packet.name}/{name}")
            outer.add(name)
            actual = all_rows_by_path.get(name)
            if actual is None:
                raise ValueError(f"structured outer member missing: {packet.name}/{name}")
            if int(row["bytes_or_count"]) != actual["bytes"] or row["sha256"].upper() != actual["sha256"]:
                raise ValueError(f"structured outer identity differs: {packet.name}/{name}")
        elif record_type == "ARCHIVE_MEMBER_SET":
            suffix = "::regular_members"
            if not name.endswith(suffix):
                raise ValueError(f"unknown structured set: {packet.name}/{name}")
            archive_name = name[:-len(suffix)]
            archive, backing = open_named_archive(packet, archive_name)
            try:
                count, _total, digest = aggregate_archive(archive)
            finally:
                archive.close()
                if backing is not None:
                    backing.close()
            if count != int(row["bytes_or_count"]) or digest != row["sha256"].upper():
                raise ValueError(
                    f"true-ordinal archive aggregate differs: {packet.name}/{archive_name}: "
                    f"count={count}, sha256={digest}"
                )
            aggregate_rows += 1
            aggregate_members += count
        else:
            raise ValueError(f"unknown structured record type: {packet.name}/{record_type}")
    omitted = sorted(set(all_rows_by_path) - outer)
    allowed = {
        name for name in omitted
        if name == manifest_name or re.search(r"(?i)(VALIDATION.*RECEIPT|PACKET_VALIDATION)", name)
    }
    if set(omitted) != allowed:
        raise ValueError(f"structured manifest has unexplained omissions: {packet.name}: {sorted(set(omitted)-allowed)}")
    return {
        "format": "structured_outer_and_archive_member_sets",
        "archive_member_stream": "normalized full name + TAB + decimal bytes + TAB + uppercase SHA-256; true ordinal path sort; UTF-8; LF separators; no BOM; no header; no trailing LF",
        "result": "PASS",
        "declared_outer_files": len(outer),
        "archive_member_sets": aggregate_rows,
        "archive_members_replayed": aggregate_members,
        "excluded_direct_files": omitted,
    }


def native_manifest_replay(packet: Path, spec: FrozenJob, all_rows_by_path: dict[str, dict[str, object]]) -> dict[str, object]:
    path = packet / spec.packet_manifest
    if path.suffix.lower() == ".json":
        value = json.loads(path.read_bytes().decode("utf-8-sig"), object_pairs_hook=object_pairs)
        entries = value.get("entries")
        if not isinstance(entries, list):
            raise ValueError(f"JSON native manifest has no entries: {packet.name}/{path.name}")
        rows = [{key: str(entry[key]) for key in ("path", "bytes", "sha256")} for entry in entries]
        result = verify_flat_rows(packet, rows, all_rows_by_path, path.name)
        if value.get("self_excluding") is not True or path.name not in value.get("excluded_paths", []):
            raise ValueError(f"JSON native manifest self-exclusion differs: {packet.name}/{path.name}")
        result["format"] = "self_excluding_json"
    else:
        text = path.read_bytes().decode("utf-8-sig")
        first = text.partition("\n")[0]
        delimiter = "\t" if "\t" in first else ","
        first_fields = next(csv.reader([first], delimiter=delimiter))
        if (
            len(first_fields) >= 3
            and first_fields[1].isdigit()
            and re.fullmatch(r"[0-9A-Fa-f]{64}", first_fields[2])
        ):
            raw_rows = list(csv.reader(io.StringIO(text), delimiter=delimiter))
            rows = [
                {"path": fields[0], "bytes": fields[1], "sha256": fields[2]}
                for fields in raw_rows
                if fields
            ]
        else:
            rows = list(csv.DictReader(io.StringIO(text), delimiter=delimiter))
        if rows and "record_type" in rows[0]:
            result = verify_structured_rows(packet, rows, all_rows_by_path, path.name)
        else:
            result = verify_flat_rows(packet, rows, all_rows_by_path, path.name)
    result["identity"] = row_identity(all_rows_by_path[path.name])
    return result


def manifest_repair_idempotence(packet_root: Path) -> dict[str, object]:
    """Rebuild the four corrected manifests in memory and require exact bytes."""
    targets = {
        "HECKE_VORLESUNGEN_1923_REPAIR": ("98_PACKET_MANIFEST_SHA256.tsv", "flat"),
        "KRONECKER_GRUNDZUEGE_1882_REPAIR": ("98_PACKET_MANIFEST_SHA256.tsv", "flat"),
        "KHAYYAM_ALGEBRA_REPAIR": ("07_PACKET_MANIFEST.tsv", "structured"),
        "SEKI_HATSUBI_SANPO_REPAIR": ("07_PACKET_MANIFEST.tsv", "structured"),
    }
    rows: list[dict[str, object]] = []
    changed: list[str] = []
    for packet_name, (manifest_name, kind) in targets.items():
        packet = packet_root / packet_name
        manifest = packet / manifest_name
        if kind == "flat":
            lines: list[str] = []
            for path in sorted(packet.iterdir(), key=lambda item: item.name.casefold()):
                if not path.is_file() or path.name == manifest_name:
                    continue
                lines.append(
                    f"{path.name}\t{path.stat().st_size}\t{pack_job.sha256_file(path)}\n"
                )
            expected = "".join(lines).encode("utf-8")
        else:
            current_rows = list(
                csv.reader(manifest.read_text(encoding="utf-8").splitlines(), delimiter="\t")
            )
            if not current_rows or current_rows[0][:4] != [
                "record_type", "path_or_set", "bytes_or_count", "sha256",
            ]:
                raise ValueError(f"unexpected structured manifest header: {packet_name}")
            output: list[list[str]] = [current_rows[0]]
            for source_row in current_rows[1:]:
                if len(source_row) != 5:
                    raise ValueError(f"malformed structured manifest row: {packet_name}")
                record_type, logical, _count, _digest, role = source_row
                if record_type == "OUTER_FILE":
                    path = packet / logical
                    output.append([
                        record_type, logical, str(path.stat().st_size),
                        pack_job.sha256_file(path), role,
                    ])
                elif record_type == "ARCHIVE_MEMBER_SET":
                    suffix = "::regular_members"
                    if not logical.endswith(suffix):
                        raise ValueError(f"malformed structured set: {packet_name}/{logical}")
                    archive, backing = open_named_archive(packet, logical[:-len(suffix)])
                    try:
                        count, _bytes, digest = aggregate_archive(archive)
                    finally:
                        archive.close()
                        if backing is not None:
                            backing.close()
                    output.append([record_type, logical, str(count), digest, role])
                else:
                    raise ValueError(f"unknown structured record: {packet_name}/{record_type}")
            stream = io.StringIO(newline="")
            writer = csv.writer(stream, delimiter="\t", lineterminator="\n")
            writer.writerows(output)
            expected = stream.getvalue().encode("utf-8")
        actual = manifest.read_bytes()
        if actual != expected:
            changed.append(f"{packet_name}/{manifest_name}")
        rows.append({
            "packet_id": packet_name,
            "manifest": {
                "basename": manifest_name,
                "bytes": len(actual),
                "sha256": sha256_bytes(actual),
            },
            "second_run_would_change": actual != expected,
        })
    if changed:
        raise ValueError(f"manifest repair is not idempotent: {changed}")
    return {
        "result": "PASS",
        "bounded_packet_count": 4,
        "manifest_repair_second_run_changed_files": 0,
        "rows": rows,
    }


def verify_authority(packet: Path, authority: dict[str, object], rows_by_path: dict[str, dict[str, object]]) -> None:
    logical = str(authority.get("path", ""))
    expected = str(authority.get("sha256", ""))
    levels = logical.split("!/")
    outer_name = levels[0]
    if Path(outer_name).name != outer_name or outer_name not in rows_by_path:
        raise ValueError(f"authority outer file is absent/unsafe: {packet.name}/{logical}")
    if len(levels) == 1:
        if rows_by_path[outer_name]["sha256"] != expected:
            raise ValueError(f"authority hash differs: {packet.name}/{logical}")
        return
    if len(levels) != 2:
        raise ValueError(f"only one authority archive descent is supported: {packet.name}/{logical}")
    nested = safe_member(levels[1])
    with zipfile.ZipFile(packet / outer_name, "r") as archive:
        info = archive.getinfo(nested)
        with archive.open(info, "r") as handle:
            size, digest = hash_stream(handle)
    if size != info.file_size or digest != expected:
        raise ValueError(f"nested authority identity differs: {packet.name}/{logical}")


def verify_asset_manifest(
    job_id: str,
    source_rows: list[dict[str, object]],
    release_root: Path,
) -> tuple[dict[str, object], list[dict[str, object]]]:
    path = ASSET_MANIFEST_ROOT / f"{job_id}.json"
    manifest = load_json(path)
    canonical_bytes, tree = pack_job.tree_hash(source_rows)
    if (
        manifest.get("schema") != "math-commons-job-asset/v1"
        or manifest.get("job_id") != job_id
        or manifest.get("wrapper_directory") != job_id
        or manifest.get("members") != source_rows
        or manifest.get("source_files") != len(source_rows)
        or manifest.get("source_bytes") != sum(int(row["bytes"]) for row in source_rows)
        or manifest.get("canonical_stream_bytes") != canonical_bytes
        or manifest.get("source_tree_sha256") != tree
    ):
        raise ValueError(f"asset manifest does not bind current direct snapshot: {job_id}")
    assets = manifest.get("assets")
    if not isinstance(assets, list) or not assets:
        raise ValueError(f"asset manifest has no release assets: {job_id}")
    offset = 0
    replayed: list[dict[str, object]] = []
    for index, asset in enumerate(assets, 1):
        count = int(asset["source_files"])
        group = source_rows[offset:offset + count]
        offset += count
        if (
            not group
            or asset.get("part") != index
            or asset.get("parts") != len(assets)
            or asset.get("first_path") != group[0]["path"]
            or asset.get("last_path") != group[-1]["path"]
            or asset.get("source_bytes") != sum(int(row["bytes"]) for row in group)
        ):
            raise ValueError(f"asset partition metadata differs: {job_id} part {index}")
        asset_path = release_root / str(asset["name"])
        if not asset_path.is_file():
            raise ValueError(f"release asset is absent: {asset_path.name}")
        if asset_path.stat().st_size != asset["zip_bytes"] or pack_job.sha256_file(asset_path) != asset["zip_sha256"]:
            raise ValueError(f"release asset outer identity differs: {asset_path.name}")
        pack_job.replay_zip(asset_path, job_id, group)
        replayed.append({
            "name": asset_path.name,
            "bytes": asset_path.stat().st_size,
            "sha256": str(asset["zip_sha256"]),
            "source_files": len(group),
            "source_bytes": sum(int(row["bytes"]) for row in group),
            "crc_and_member_stream_replay": "PASS",
        })
    if offset != len(source_rows):
        raise ValueError(f"release asset partitions do not cover snapshot: {job_id}")
    return manifest, replayed


def verify_translation_asset(release_root: Path) -> tuple[dict[str, object], list[dict[str, object]]]:
    manifest = load_json(TRANSLATION_ASSET_MANIFEST)
    rows = manifest.get("members")
    if not isinstance(rows, list):
        raise ValueError("translation-kit asset manifest has no members")
    assets = manifest.get("assets")
    if not isinstance(assets, list) or len(assets) != 1:
        raise ValueError("translation-kit release partition differs")
    asset = assets[0]
    path = release_root / str(asset["name"])
    if not path.is_file() or path.stat().st_size != asset["zip_bytes"] or pack_job.sha256_file(path) != asset["zip_sha256"]:
        raise ValueError("translation-kit release asset identity differs")
    pack_job.replay_zip(path, str(manifest["wrapper_directory"]), rows)
    return manifest, [{
        "name": path.name,
        "bytes": path.stat().st_size,
        "sha256": str(asset["zip_sha256"]),
        "source_files": len(rows),
        "source_bytes": sum(int(row["bytes"]) for row in rows),
        "crc_and_member_stream_replay": "PASS",
    }]


def public_projection(path: Path) -> dict[str, object]:
    return {
        "path": path.relative_to(ROOT).as_posix(),
        "bytes": path.stat().st_size,
        "sha256": pack_job.sha256_file(path),
        "transformations": [
            "Generated directly from frozen packet identifiers and exact byte replays; no private filesystem path is emitted."
        ],
    }


def external_receipt(path: Path, scope: str) -> dict[str, object]:
    projection = public_projection(path)
    return {
        "basename": path.name,
        "bytes": projection["bytes"],
        "sha256": projection["sha256"],
        "receipt_scope": scope,
        "included_in_packet": False,
        "public_projection": projection,
    }


def release_scoped_exclusions(exclusions: object) -> list[dict[str, str]]:
    if not isinstance(exclusions, list):
        raise ValueError("metadata exclusions are not an array")
    exact_container_tokens = (
        "QUARANTINE", "_PRESERVED_OUT_OF_SCOPE", "_GORDAN_SOURCE_AUDIT",
        "SUPERSEDED", "VISUAL_QA", "__PYCACHE__", "WEBER_LEHRBUCH_I_III_REPAIR",
    )
    result: list[dict[str, str]] = []
    for raw in exclusions:
        if not isinstance(raw, dict):
            raise ValueError("metadata exclusion is not an object")
        item = {key: str(raw[key]) for key in ("id", "root", "reason")}
        upper = f"{item['id']} {item['root']}".upper()
        if any(token in upper for token in exact_container_tokens):
            result.append(item)
        else:
            item["reason"] = (
                "Outside the frozen 28-job R2 cutoff. This release makes no claim about its "
                "current production state; admission requires a separately sealed exact-byte "
                "projection, validator receipt, deterministic asset mapping, and public readback."
            )
            result.append(item)
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--packet-root", required=True, type=Path)
    parser.add_argument("--asset-dir", required=True, type=Path)
    parser.add_argument("--hardener-script", type=Path)
    args = parser.parse_args()

    packet_root = args.packet_root.resolve()
    release_root = args.asset_dir.resolve()
    hardener_script = (
        args.hardener_script.resolve()
        if args.hardener_script
        else packet_root / "harden_no_failure_controls_20260821.py"
    )
    if not packet_root.is_dir() or not release_root.is_dir() or not hardener_script.is_file():
        raise ValueError("packet root, asset directory, or hardener script is absent")
    try:
        release_root.relative_to(packet_root)
    except ValueError:
        pass
    else:
        raise ValueError("release asset directory must not be inside producer packet root")

    meta = load_json(META_PATH)
    old_jobs = meta.get("jobs")
    if not isinstance(old_jobs, list):
        raise ValueError("job metadata has no jobs array")
    old_by_id = {str(item["id"]): item for item in old_jobs}
    if len(old_by_id) != len(old_jobs) or set(old_by_id) != set(FROZEN) or len(FROZEN) != 28:
        raise ValueError("frozen R2 job set differs from the exact 28 R1 job IDs")

    hardener_identity = {
        "basename": hardener_script.name,
        "bytes": hardener_script.stat().st_size,
        "sha256": pack_job.sha256_file(hardener_script),
    }
    repair_script = ROOT / "tools" / "repair_stale_packet_manifests.py"
    if not repair_script.is_file():
        raise ValueError("bounded manifest-repair script is absent")
    repair_script_identity = file_identity(repair_script, basename_only=False)
    repair_idempotence = manifest_repair_idempotence(packet_root)
    admission_rows: list[dict[str, object]] = []
    hardening_rows: list[dict[str, object]] = []
    updated_jobs: list[dict[str, object]] = []
    expected_release_assets: set[str] = set()

    for job_id in FROZEN:
        spec = FROZEN[job_id]
        packet = packet_root / spec.packet_id
        if not packet.is_dir() or packet.resolve().parent != packet_root:
            raise ValueError(f"frozen packet root is absent/unsafe: {spec.packet_id}")
        source_rows = pack_job.source_rows(packet, direct_only=True)
        rows_by_path = {str(row["path"]): row for row in source_rows}
        if len(rows_by_path) != len(source_rows):
            raise ValueError(f"duplicate direct packet path: {spec.packet_id}")
        for required in (spec.start_file, spec.prompt_file, spec.packet_manifest):
            if required not in rows_by_path:
                raise ValueError(f"required direct file is absent: {spec.packet_id}/{required}")

        prompts = prompt_replay(packet, spec, rows_by_path)
        policy = policy_scan(packet, spec, rows_by_path)
        native = native_manifest_replay(packet, spec, rows_by_path)
        asset_manifest, replayed_assets = verify_asset_manifest(job_id, source_rows, release_root)
        expected_release_assets.update(str(item["name"]) for item in replayed_assets)
        canonical_bytes, tree = pack_job.tree_hash(source_rows)

        old = dict(old_by_id[job_id])
        old["packet_id"] = spec.packet_id
        old["pack_scope"] = "direct_files"
        old["source_files"] = len(source_rows)
        old["source_bytes"] = sum(int(row["bytes"]) for row in source_rows)
        old["status"] = "PASS_GLOBAL_COLD_AUDIT"
        old["audit_basis"] = "global_receipt"
        old["prompt_count"] = spec.prompt_count
        old["start_file"] = row_identity(rows_by_path[spec.start_file])
        old["prompt_file"] = row_identity(rows_by_path[spec.prompt_file])
        old["packet_manifest"] = row_identity(rows_by_path[spec.packet_manifest])
        if job_id == "clebsch-gordan-abelian-functions-1866":
            old["authority"] = [{
                "path": "20_Clebsch_Gordan_Theorie_der_Abelschen_Functionen_1866_CONTROLLING_362_physical_pages_Oxford_with_Toronto_printed_page_30.pdf",
                "pages": 362,
                "note": "Corrected controlling composite: Oxford witness with Toronto authority backfill for printed page 30.",
                "sha256": "8C324DAC59E58A71930AA1712764781B551DB2D6E9EFF89D9DA719B46A746CFB",
            }]
            old["physical_pages"] = 362
            old["page_note"] = (
                "All 362 physical pages of the corrected composite receive a disposition; the "
                "Toronto backfill supplies the printed page 30 missing from the Oxford access object."
            )
        authorities = old.get("authority")
        if not isinstance(authorities, list) or not authorities:
            raise ValueError(f"job has no authority declarations: {job_id}")
        for authority in authorities:
            if not isinstance(authority, dict):
                raise ValueError(f"authority is not an object: {job_id}")
            verify_authority(packet, authority, rows_by_path)

        row = {
            "job_id": job_id,
            "packet_id": spec.packet_id,
            "result": "PASS",
            "overall": "PASS",
            "direct_file_count": len(source_rows),
            "direct_total_bytes": sum(int(item["bytes"]) for item in source_rows),
            "direct_snapshot_sha256": audit_snapshot_sha256(source_rows),
            "prompt_count": spec.prompt_count,
            "start_file": row_identity(rows_by_path[spec.start_file]),
            "prompt_file": row_identity(rows_by_path[spec.prompt_file]),
            "packet_manifest": row_identity(rows_by_path[spec.packet_manifest]),
            "direct_snapshot": {
                "files": len(source_rows),
                "bytes": sum(int(item["bytes"]) for item in source_rows),
                "canonical_stream_bytes": canonical_bytes,
                "source_tree_sha256": tree,
            },
            "prompts": prompts,
            "native_packet_manifest": native,
            "asset_manifest": {
                **file_identity(ASSET_MANIFEST_ROOT / f"{job_id}.json", basename_only=False),
                "source_tree_sha256": str(asset_manifest["source_tree_sha256"]),
            },
            "local_release_assets": replayed_assets,
            "authority_count": len(authorities),
            "authority_identity_replay": "PASS",
            "controlling_instruction_policy": {
                "result": policy["result"],
                "forbidden_controlling_outcome_conditions": policy["forbidden_controlling_outcome_conditions"],
            },
        }
        admission_rows.append(row)
        hardening_rows.append({
            "job_id": job_id,
            "packet_id": spec.packet_id,
            **policy,
        })
        updated_jobs.append(old)

    translation_manifest, translation_assets = verify_translation_asset(release_root)
    expected_release_assets.update(str(item["name"]) for item in translation_assets)
    present_release_assets = {path.name for path in release_root.glob("*.zip") if path.is_file()}
    if present_release_assets != expected_release_assets:
        raise ValueError(
            "local R2 release ZIP set differs: "
            f"missing={sorted(expected_release_assets-present_release_assets)}, "
            f"extra={sorted(present_release_assets-expected_release_assets)}"
        )

    hardening_receipt = {
        "schema": "math-commons-packet-no-failure-hardening/v1",
        "date": DATE,
        "release_tag": RELEASE_TAG,
        "publication_state": "LOCAL_NONPUBLISHED",
        "scope": {
            "rule": "exactly the 28 frozen R1 job IDs; no packet-root discovery",
            "jobs": len(hardening_rows),
        },
        "hardener_source_identity": hardener_identity,
        "manifest_repair_source_identity": repair_script_identity,
        "idempotence": {
            "result": "PASS",
            "bounded_exact_28_scope": True,
            "policy_marker_reapplication_would_change_files": 0,
            "manifest_repair_second_run_changed_files": repair_idempotence[
                "manifest_repair_second_run_changed_files"
            ],
            "manifest_repair_rows": repair_idempotence["rows"],
        },
        "replay_semantics": {
            "work_duration": "AS_LONG_AS_NEEDED_NO_ASSUMED_TIME_LIMIT",
            "response_statuses": ["IN_PROGRESS", "COMPLETE"],
            "in_progress_condition": "PLATFORM_FORCED_RESPONSE_SPLIT_ONLY_WITH_NEWEST_CUMULATIVE_TRIO",
            "defect_resolution": "ATTACHED_SCANS_AND_COMPARATORS; VERSIONED_IN_WORKFLOW_REPAIR",
            "unencodable_detail": "EXACT_AUTHORITY_IMAGE_OR_CROP_PLUS_APPARATUS_AND_CONTINUE",
            "audit_fail": "INTERNAL_DIAGNOSTIC_ONLY; REPAIR_AND_FRESH_NONPATCHING_RERUN_UNTIL_PASS",
            "completion_gate": "PASS_ONLY",
        },
        "method": (
            "Fresh read-only bounded replay of current direct controlling files and embedded S00 control "
            "surfaces. This receipt does not reuse the historical 58/58 manifest claim and does not "
            "assert publication or remote readback."
        ),
        "rows": hardening_rows,
        "summary": {
            "rows": len(hardening_rows),
            "pass": len(hardening_rows),
            "fail": 0,
            "forbidden_controlling_outcome_conditions": 0,
        },
    }
    write_json(HARDENING_PATH, hardening_receipt)
    hardening_public = public_projection(HARDENING_PATH)

    admission_receipt = {
        "schema": "math-commons-packet-r2-admission/v1",
        "date": DATE,
        "release_tag": RELEASE_TAG,
        "publication_state": "LOCAL_NONPUBLISHED",
        "nonmutating": True,
        "published": False,
        "row_count": len(admission_rows),
        "pass_count": len(admission_rows),
        "fail_count": 0,
        "nonmutating_packet_audit": True,
        "published_or_promoted": False,
        "scope": {
            "rule": "exactly the 28 frozen R1 job IDs; no packet-root discovery",
            "jobs": len(admission_rows),
            "pack_scope": "direct_files",
        },
        "hardening_receipt": hardening_public,
        "archive_member_aggregate_semantics": (
            "normalized ZipArchiveEntry full name + TAB + decimal uncompressed length + TAB + "
            "uppercase SHA-256; true ordinal path sort; UTF-8 without BOM; LF separators; no header; "
            "no trailing LF"
        ),
        "local_release": {
            "directory_recorded": False,
            "asset_count": len(expected_release_assets),
            "asset_bytes": sum((release_root / name).stat().st_size for name in expected_release_assets),
            "zip_set_replay": "PASS",
            "remote_readback": "NOT_RUN",
        },
        "rows": admission_rows,
        "translation_kit": {
            "asset_manifest": {
                **file_identity(TRANSLATION_ASSET_MANIFEST, basename_only=False),
                "source_tree_sha256": str(translation_manifest["source_tree_sha256"]),
            },
            "local_release_assets": translation_assets,
        },
        "summary": {
            "rows": len(admission_rows),
            "pass": len(admission_rows),
            "fail": 0,
            "direct_files": sum(int(row["direct_snapshot"]["files"]) for row in admission_rows),
            "direct_bytes": sum(int(row["direct_snapshot"]["bytes"]) for row in admission_rows),
            "release_assets": len(expected_release_assets),
            "release_bytes": sum((release_root / name).stat().st_size for name in expected_release_assets),
        },
    }
    write_json(ADMISSION_PATH, admission_receipt)

    admission_external = external_receipt(
        ADMISSION_PATH,
        "Fresh frozen-28 local R2 admission replay; publication and remote readback are explicitly pending.",
    )
    hardening_external = external_receipt(
        HARDENING_PATH,
        "Fresh bounded no-failure/no-time-limit control replay for the same frozen 28 packet roots.",
    )
    for item in updated_jobs:
        item["validation_receipt"] = dict(admission_external)

    updated_meta = {
        "schema": "math-commons-job-meta/v2",
        "updated": DATE,
        "admission_note": (
            "R2 freezes exactly the 28 previously admitted exact-work/volume jobs and replays their "
            "current direct bytes, workload-derived prompt drivers, hardened continuity controls, "
            "native packet manifests, authority identities, asset manifests, and local deterministic "
            "release ZIPs. This metadata is local/non-published until the release assets receive exact "
            "public remote readback; later packet candidates are outside this cutoff rather than inferred incomplete."
        ),
        "audit_receipt": admission_external,
        "hardening_receipt": hardening_external,
        "jobs": updated_jobs,
        "exclusions": release_scoped_exclusions(meta.get("exclusions")),
    }
    write_json(META_PATH, updated_meta)

    result = {
        "jobs": len(admission_rows),
        "direct_files": admission_receipt["summary"]["direct_files"],
        "direct_bytes": admission_receipt["summary"]["direct_bytes"],
        "release_assets": len(expected_release_assets),
        "release_bytes": admission_receipt["summary"]["release_bytes"],
        "hardening_receipt": public_projection(HARDENING_PATH),
        "admission_receipt": public_projection(ADMISSION_PATH),
        "job_meta": file_identity(META_PATH, basename_only=False),
        "publication_state": "LOCAL_NONPUBLISHED",
        "remote_readback": "NOT_RUN",
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, zipfile.BadZipFile, KeyError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
