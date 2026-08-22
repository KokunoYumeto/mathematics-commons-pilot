#!/usr/bin/env python3
"""Cold-build an exact extracted Open Logic packet and write a bounded receipt."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import zipfile
from collections import Counter
from pathlib import Path, PurePosixPath
from typing import Any


JOB_ID = "openlogic-v1"
ROOT_COMMIT = "1e960beff9ed7835bf3e3f1335e21af3439cd107"
ROOT_TREE = "45cad6b3bf0dd96985a7b3d1dc5c343984b0e1c8"
DOC_COMMIT = "b46686df0e06f302a7b75a74b379c802f7c7b565"
SOURCE_FILES = 792
SOURCE_BYTES = 4_302_140
SOURCE_MODES = {"100644": 773, "100755": 19}
FIXED_TIME = (1980, 1, 1, 0, 0, 0)
COMMAND = (
    "latexmk",
    "-g",
    "-pdf",
    "-dvi-",
    "-ps-",
    "-interaction=nonstopmode",
    "-halt-on-error",
)
TARGETS = ("open-logic-debug.tex", "open-logic-complete.tex")
GENERATED_SUFFIXES = {
    ".aux", ".bbl", ".bcf", ".blg", ".brf", ".ent", ".fdb_latexmk",
    ".fls", ".idx", ".ilg", ".ind", ".loa", ".lof", ".log", ".lot",
    ".nav", ".out", ".pcr", ".prb", ".run.xml", ".snm", ".synctex.gz",
    ".thm", ".toc", ".vrb", ".xdv",
}
FATAL = re.compile(
    r"(?:Fatal error|Emergency stop|!pdfTeX error|LaTeX Error|^! )",
    re.MULTILINE,
)
HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9A-F]{64}$")
ROOT_LABEL = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]*$")


class DuplicateKey(ValueError):
    """Raised when JSON contains a duplicate object key."""


def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateKey(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        while block := handle.read(1024 * 1024):
            value.update(block)
    return value.hexdigest().upper()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def git_object_oid(kind: str, data: bytes) -> str:
    framed = f"{kind} {len(data)}\0".encode("ascii") + data
    return hashlib.sha1(framed).hexdigest()


def git_blob_oid(data: bytes) -> str:
    return git_object_oid("blob", data)


def command_text(parts: tuple[str, ...]) -> str:
    return " ".join(parts)


def version(command: list[str]) -> str:
    result = subprocess.run(
        command,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    lines = result.stdout.splitlines()
    if not lines:
        raise ValueError(f"version command returned no text: {command!r}")
    return lines[0].strip()


def pages(pdf: Path) -> int:
    result = subprocess.run(
        ["pdfinfo", os.fspath(pdf)],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    for line in result.stdout.splitlines():
        if line.startswith("Pages:"):
            return int(line.split(":", 1)[1].strip())
    raise ValueError(f"pdfinfo supplied no page count: {pdf}")


def safe_path(value: str) -> bool:
    parsed = PurePosixPath(value)
    parts = parsed.parts
    return bool(
        value
        and value == parsed.as_posix()
        and not parsed.is_absolute()
        and "\\" not in value
        and len(value.encode("utf-8")) <= 500
        and parts
        and all(
            part not in {"", ".", ".."}
            and len(part.encode("utf-8")) <= 255
            and not part.endswith((" ", "."))
            and not any(char in '<>:"|?*' for char in part)
            for part in parts
        )
        and not any(ord(char) < 32 for char in value)
    )


def enumerate_files(root: Path) -> dict[str, Path]:
    if not root.is_dir():
        raise ValueError(f"directory is missing: {root}")
    result: dict[str, Path] = {}
    portable: dict[str, str] = {}
    for candidate in sorted(root.rglob("*"), key=lambda item: item.as_posix()):
        if candidate.is_symlink():
            raise ValueError(f"symbolic link is not allowed: {candidate}")
        if not candidate.is_file():
            continue
        relative = candidate.relative_to(root).as_posix()
        if not safe_path(relative):
            raise ValueError(f"unsafe relative path: {relative!r}")
        parts = PurePosixPath(relative).parts
        for index in range(1, len(parts) + 1):
            prefix = "/".join(parts[:index])
            folded = prefix.casefold()
            prior = portable.get(folded)
            if prior is not None and prior != prefix:
                raise ValueError(
                    f"case-insensitive path collision: {prior!r} / {prefix!r}"
                )
            portable[folded] = prefix
        result[relative] = candidate
    return result


def reconstruct_root_tree(rows: dict[str, dict[str, object]]) -> str:
    root: dict[str, Any] = {}
    for path, row in rows.items():
        parts = PurePosixPath(path).parts
        node = root
        for part in parts[:-1]:
            prior = node.get(part)
            if prior is None:
                child: dict[str, Any] = {}
                node[part] = child
                node = child
            elif isinstance(prior, dict):
                node = prior
            else:
                raise ValueError(f"Git path is both file and directory: {path}")
        leaf = parts[-1]
        if leaf in node:
            raise ValueError(f"duplicate or conflicting Git path: {path}")
        node[leaf] = (str(row["mode"]), str(row["git_blob"]))
    if "doc" in root:
        raise ValueError("root source unexpectedly contains the excluded doc gitlink")
    root["doc"] = ("160000", DOC_COMMIT)

    def tree_oid(node: dict[str, Any]) -> str:
        entries: list[tuple[bytes, bytes, str]] = []
        for name, value in node.items():
            name_bytes = name.encode("utf-8")
            if isinstance(value, dict):
                mode = "40000"
                oid = tree_oid(value)
                key = name_bytes + b"/"
            else:
                mode, oid = value
                key = name_bytes
            prefix = f"{mode} {name}".encode("utf-8") + b"\0"
            entries.append((key, prefix, oid))
        body = b"".join(
            prefix + bytes.fromhex(oid)
            for _, prefix, oid in sorted(entries, key=lambda item: item[0])
        )
        return git_object_oid("tree", body)

    return tree_oid(root)


def load_source_rows(packet_root: Path) -> dict[str, dict[str, object]]:
    receipt = packet_root / "SOURCE_TREE.tsv"
    raw = receipt.read_bytes()
    if raw.startswith(b"\xef\xbb\xbf") or b"\r" in raw or not raw.endswith(b"\n"):
        raise ValueError("SOURCE_TREE.tsv must be UTF-8, LF-only, no BOM, with final LF")
    lines = raw.decode("utf-8")[:-1].split("\n")
    if not lines or lines[0] != "path\tmode\tbytes\tgit_blob\tsha256":
        raise ValueError("SOURCE_TREE.tsv header differs")
    if len(lines) - 1 != SOURCE_FILES:
        raise ValueError(f"source receipt row count differs: {len(lines) - 1}")
    rows: dict[str, dict[str, object]] = {}
    ordered_paths: list[str] = []
    mode_counts: Counter[str] = Counter()
    total_bytes = 0
    for line in lines[1:]:
        fields = line.split("\t")
        if len(fields) != 5:
            raise ValueError("malformed SOURCE_TREE.tsv row")
        path, mode, size_text, oid, sha = fields
        if not safe_path(path):
            raise ValueError(f"unsafe source receipt path: {path!r}")
        if path in rows:
            raise ValueError(f"duplicate source receipt path: {path}")
        if mode not in SOURCE_MODES:
            raise ValueError(f"unsupported Git mode: {path}: {mode}")
        if re.fullmatch(r"0|[1-9][0-9]*", size_text) is None:
            raise ValueError(f"noncanonical source byte count: {path}")
        if HEX40.fullmatch(oid) is None or HEX64.fullmatch(sha) is None:
            raise ValueError(f"malformed source identity: {path}")
        size = int(size_text)
        candidate = packet_root / "source" / Path(*PurePosixPath(path).parts)
        if not candidate.is_file() or candidate.is_symlink():
            raise ValueError(f"source receipt member missing or not regular: {path}")
        data = candidate.read_bytes()
        if len(data) != size or sha256_bytes(data) != sha:
            raise ValueError(f"source receipt byte/SHA-256 mismatch: {path}")
        if git_blob_oid(data) != oid:
            raise ValueError(f"source receipt Git blob mismatch: {path}")
        rows[path] = {
            "path": path,
            "mode": mode,
            "bytes": size,
            "git_blob": oid,
            "sha256": sha,
        }
        ordered_paths.append(path)
        mode_counts[mode] += 1
        total_bytes += size
    if ordered_paths != sorted(ordered_paths):
        raise ValueError("SOURCE_TREE.tsv paths are not in ordinal order")
    if total_bytes != SOURCE_BYTES:
        raise ValueError(f"source receipt byte total differs: {total_bytes}")
    if dict(mode_counts) != SOURCE_MODES:
        raise ValueError(f"source Git mode census differs: {dict(mode_counts)}")
    observed_tree = reconstruct_root_tree(rows)
    if observed_tree != ROOT_TREE:
        raise ValueError(f"reconstructed root tree differs: {observed_tree}")
    verify_source_tree(packet_root / "source", rows, reject_extras=True)
    return rows


def verify_source_tree(
    source_root: Path,
    rows: dict[str, dict[str, object]],
    *,
    reject_extras: bool,
) -> list[str]:
    actual = enumerate_files(source_root)
    expected_paths = set(rows)
    actual_paths = set(actual)
    missing = sorted(expected_paths - actual_paths)
    extra = sorted(actual_paths - expected_paths)
    if missing or (reject_extras and extra):
        raise ValueError(
            f"source path set differs: missing={missing[:10]!r}; extra={extra[:10]!r}"
        )
    for path, row in rows.items():
        data = actual[path].read_bytes()
        if (
            len(data) != row["bytes"]
            or sha256_bytes(data) != row["sha256"]
            or git_blob_oid(data) != row["git_blob"]
        ):
            raise ValueError(f"source changed during replay: {path}")
    return extra


def load_json(path: Path) -> tuple[dict[str, Any], bytes]:
    raw = path.read_bytes()
    value = json.loads(raw.decode("utf-8"), object_pairs_hook=unique_object)
    if not isinstance(value, dict):
        raise ValueError(f"JSON root is not an object: {path}")
    return value, raw


def validate_internal_manifest(
    packet_root: Path, packet_rows: dict[str, dict[str, object]]
) -> None:
    path = packet_root / "MANIFEST.sha256"
    if "MANIFEST.sha256" not in packet_rows or not path.is_file():
        raise ValueError("packet internal manifest is missing")
    expected = "".join(
        f"{row['sha256']}\t{row['bytes']}\t{member_path}\n"
        for member_path, row in packet_rows.items()
        if member_path != "MANIFEST.sha256"
    ).encode("utf-8")
    if path.read_bytes() != expected:
        raise ValueError("packet internal manifest does not replay")


def validate_packet_binding(
    packet_root: Path,
    packet_zip: Path,
    asset_manifest: Path,
    source_rows: dict[str, dict[str, object]],
) -> dict[str, object]:
    manifest, manifest_raw = load_json(asset_manifest)
    if (
        manifest.get("schema") != "math-commons-job-asset/v1"
        or manifest.get("job_id") != JOB_ID
        or manifest.get("wrapper_directory") != JOB_ID
        or packet_zip.name != f"{JOB_ID}.zip"
    ):
        raise ValueError("asset manifest job/wrapper identity differs")
    members_value = manifest.get("members")
    if not isinstance(members_value, list) or not members_value:
        raise ValueError("asset manifest members are missing")
    members: dict[str, dict[str, object]] = {}
    ordered_paths: list[str] = []
    for value in members_value:
        if not isinstance(value, dict):
            raise ValueError("asset manifest contains a malformed member row")
        path = value.get("path")
        size = value.get("bytes")
        sha = value.get("sha256")
        mode = value.get("mode", "100644")
        if (
            not isinstance(path, str)
            or not safe_path(path)
            or path in members
            or not isinstance(size, int)
            or isinstance(size, bool)
            or size < 0
            or not isinstance(sha, str)
            or HEX64.fullmatch(sha) is None
            or mode not in {"100644", "100755"}
        ):
            raise ValueError(f"invalid asset-manifest member: {path!r}")
        row = {"path": path, "bytes": size, "sha256": sha, "mode": mode}
        members[path] = row
        ordered_paths.append(path)
    if ordered_paths != sorted(ordered_paths):
        raise ValueError("asset-manifest members are not in ordinal order")
    canonical_stream = "".join(
        f"{row['path']}\t{row['bytes']}\t{row['sha256']}\n"
        for row in members.values()
    ).encode("utf-8")
    if (
        manifest.get("source_files") != len(members)
        or manifest.get("source_bytes")
        != sum(int(row["bytes"]) for row in members.values())
        or manifest.get("canonical_stream_bytes") != len(canonical_stream)
        or manifest.get("source_tree_sha256") != sha256_bytes(canonical_stream)
    ):
        raise ValueError("asset manifest aggregate identity differs")
    actual_packet = enumerate_files(packet_root)
    if set(actual_packet) != set(members):
        raise ValueError("extracted packet path set differs from the asset manifest")
    for path, row in members.items():
        candidate = actual_packet[path]
        if candidate.stat().st_size != row["bytes"] or digest(candidate) != row["sha256"]:
            raise ValueError(f"extracted packet member differs: {path}")
    validate_internal_manifest(packet_root, members)
    for path, source_row in source_rows.items():
        packet_path = f"source/{path}"
        packet_row = members.get(packet_path)
        if packet_row is None or any(
            packet_row[key] != source_row[key] for key in ("bytes", "sha256", "mode")
        ):
            raise ValueError(f"asset manifest does not bind source identity/mode: {path}")
    assets = manifest.get("assets")
    if not isinstance(assets, list):
        raise ValueError("asset manifest asset list is missing")
    if manifest.get("asset_count") != len(assets):
        raise ValueError("asset manifest asset count differs")
    matching = [
        row
        for row in assets
        if isinstance(row, dict) and row.get("name") == packet_zip.name
    ]
    if len(matching) != 1:
        raise ValueError("packet ZIP has no unique matching asset row")
    asset_row = matching[0]
    if (
        asset_row.get("source_files") != len(members)
        or asset_row.get("source_bytes")
        != sum(int(row["bytes"]) for row in members.values())
        or asset_row.get("first_path") != ordered_paths[0]
        or asset_row.get("last_path") != ordered_paths[-1]
    ):
        raise ValueError("packet ZIP asset-row member aggregate differs")
    checks = manifest.get("checks")
    if not isinstance(checks, dict) or (
        checks.get("source_hash_replay") != f"{len(members)}/{len(members)}"
        or checks.get("zip_member_replay") != f"{len(members)}/{len(members)}"
        or any(
            checks.get(key) != 0
            for key in (
                "crc_errors",
                "missing",
                "extra",
                "byte_mismatches",
                "hash_mismatches",
            )
        )
    ):
        raise ValueError("asset manifest replay counters differ")
    zip_bytes = packet_zip.stat().st_size
    zip_sha = digest(packet_zip)
    if asset_row.get("zip_bytes") != zip_bytes or asset_row.get("zip_sha256") != zip_sha:
        raise ValueError("packet ZIP identity differs from its asset row")
    with zipfile.ZipFile(packet_zip, "r") as archive:
        if archive.testzip() is not None or archive.comment != b"":
            raise ValueError("packet ZIP CRC/comment replay failed")
        names = archive.namelist()
        expected_names = [f"{JOB_ID}/{path}" for path in ordered_paths]
        if names != expected_names:
            raise ValueError("packet ZIP path set/order differs from the asset manifest")
        for path, name in zip(ordered_paths, names, strict=True):
            row = members[path]
            info = archive.getinfo(name)
            expected_mode = stat.S_IFREG | (
                0o755 if row["mode"] == "100755" else 0o644
            )
            expected_flag = 0x800 if not name.isascii() else 0
            if (
                info.date_time != FIXED_TIME
                or info.compress_type != zipfile.ZIP_DEFLATED
                or info.create_system != 3
                or info.external_attr >> 16 != expected_mode
                or info.extra != b""
                or info.comment != b""
                or info.flag_bits != expected_flag
                or info.create_version != 20
                or info.extract_version != 20
                or info.internal_attr != 0
                or info.file_size != row["bytes"]
            ):
                raise ValueError(f"packet ZIP metadata differs: {name}")
            value = hashlib.sha256()
            with archive.open(info, "r") as handle:
                while block := handle.read(1024 * 1024):
                    value.update(block)
            if value.hexdigest().upper() != row["sha256"]:
                raise ValueError(f"packet ZIP member hash differs: {name}")
    return {
            "state": "cold_audit_input_replay_pass",
            "role": "Exact input packet used for this cold build replay; the published release asset is bound separately by the external admission receipt and public readback.",
        "asset_manifest": {
            "name": asset_manifest.name,
            "bytes": len(manifest_raw),
            "sha256": sha256_bytes(manifest_raw),
        },
        "packet_zip": {
            "name": packet_zip.name,
            "bytes": zip_bytes,
            "sha256": zip_sha,
            "members": len(members),
        },
    }


def parse_toolchain_roots(values: list[str]) -> list[tuple[str, Path]]:
    roots: list[tuple[str, Path]] = []
    labels: set[str] = set()
    for value in values:
        if "=" not in value:
            raise ValueError("--toolchain-root must use LABEL=ABSOLUTE_PATH")
        label, raw_path = value.split("=", 1)
        if ROOT_LABEL.fullmatch(label) is None or label in labels:
            raise ValueError(f"invalid or duplicate toolchain-root label: {label!r}")
        supplied_path = Path(raw_path)
        if not supplied_path.is_absolute():
            raise ValueError(f"toolchain root is not absolute: {label}")
        path = supplied_path.resolve()
        if not path.is_dir() or path.parent == path:
            raise ValueError(f"toolchain root is missing, relative, or too broad: {label}")
        labels.add(label)
        roots.append((label, path))
    if not roots:
        raise ValueError("at least one explicit --toolchain-root is required")
    return sorted(roots, key=lambda item: (-len(item[1].parts), item[0]))


def under(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


def warning_counts(log_text: str) -> dict[str, int]:
    patterns = {
        "latex": r"LaTeX Warning:",
        "package": r"Package [^\r\n]+ Warning:",
        "class": r"Class [^\r\n]+ Warning:",
        "pdftex": r"pdfTeX warning:",
        "overfull": r"Overfull \\[hv]box",
        "underfull": r"Underfull \\[hv]box",
        "undefined_reference_mentions": r"undefined (?:on input|references)",
        "undefined_citation_mentions": r"undefined (?:on input|citations)",
        "multiply_defined_mentions": r"multiply defined",
    }
    return {
        name: len(re.findall(pattern, log_text, flags=re.IGNORECASE))
        for name, pattern in patterns.items()
    }


def input_closure(
    source_root: Path,
    source_paths: set[str],
    fls: Path,
    toolchain_roots: list[tuple[str, Path]],
) -> dict[str, object]:
    raw_inputs: set[str] = set()
    for line in fls.read_text(encoding="utf-8", errors="replace").splitlines():
        if line.startswith("INPUT "):
            raw_inputs.add(line[6:])
    included: set[str] = set()
    generated: set[str] = set()
    external: dict[str, set[str]] = {label: set() for label, _ in toolchain_roots}
    unknown_external: set[str] = set()
    unbound: set[str] = set()
    doc_inputs: set[str] = set()
    root_resolved = source_root.resolve()
    for raw in raw_inputs:
        path = Path(raw)
        resolved = (source_root / path).resolve() if not path.is_absolute() else path.resolve()
        try:
            relative = resolved.relative_to(root_resolved).as_posix()
        except ValueError:
            for label, allowed_root in toolchain_roots:
                if under(resolved, allowed_root):
                    external[label].add(os.path.normcase(os.fspath(resolved)))
                    break
            else:
                unknown_external.add(os.fspath(resolved))
            continue
        if relative == "doc" or relative.startswith("doc/"):
            doc_inputs.add(relative)
        if relative in source_paths:
            included.add(relative)
        elif any(relative.endswith(suffix) for suffix in GENERATED_SUFFIXES):
            generated.add(relative)
        else:
            unbound.add(relative)
    if unknown_external:
        raise ValueError(
            "build read inputs outside the enumerated toolchain roots: "
            + repr(sorted(unknown_external)[:10])
        )
    classes = [
        {"class": label, "inputs": len(external[label])}
        for label, _ in sorted(toolchain_roots, key=lambda item: item[0])
        if external[label]
    ]
    return {
        "unique_inputs": len(raw_inputs),
        "included_source_inputs": len(included),
        "generated_inputs": len(generated),
        "external_toolchain_inputs": sum(len(paths) for paths in external.values()),
        "external_input_classes": classes,
        "unbound_repo_relative_inputs": sorted(unbound),
        "excluded_doc_inputs": sorted(doc_inputs),
        "closed": not unbound and not doc_inputs,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--packet-root", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--log-dir", required=True, type=Path)
    parser.add_argument(
        "--toolchain-root",
        action="append",
        default=[],
        metavar="LABEL=ABSOLUTE_PATH",
        help="Explicit allowed root for external TeX/toolchain INPUT records; repeatable.",
    )
    parser.add_argument("--dependency-repair-note", action="append", default=[])
    parser.add_argument("--packet-zip", type=Path)
    parser.add_argument("--asset-manifest", type=Path)
    args = parser.parse_args()

    packet_root = args.packet_root.resolve()
    source_root = packet_root / "source"
    output = args.output.resolve()
    log_dir = args.log_dir.resolve()
    if not source_root.is_dir() or (source_root / ".git").exists():
        raise ValueError("packet source is missing or contains Git metadata")
    if under(output, packet_root) or under(log_dir, packet_root):
        raise ValueError("output and log directory must be outside the packet root")
    if bool(args.packet_zip) != bool(args.asset_manifest):
        raise ValueError("--packet-zip and --asset-manifest must be supplied together")
    packet_zip = args.packet_zip.resolve() if args.packet_zip else None
    asset_manifest = args.asset_manifest.resolve() if args.asset_manifest else None
    if packet_zip is not None and asset_manifest is not None:
        if output in {packet_zip, asset_manifest}:
            raise ValueError("output must not overwrite packet binding evidence")
        if not packet_zip.is_file() or not asset_manifest.is_file():
            raise ValueError("packet ZIP or asset manifest is missing")

    toolchain_roots = parse_toolchain_roots(args.toolchain_root)
    source_rows = load_source_rows(packet_root)
    binding: dict[str, object] = {"state": "not_requested"}
    if packet_zip is not None and asset_manifest is not None:
        binding = validate_packet_binding(
            packet_root, packet_zip, asset_manifest, source_rows
        )
    log_dir.mkdir(parents=True, exist_ok=True)
    results: list[dict[str, object]] = []
    closures: list[dict[str, object]] = []
    for target in TARGETS:
        stem = Path(target).stem
        with tempfile.TemporaryDirectory(prefix=f"mc-{stem}-") as temporary:
            build_root = Path(temporary) / "source"
            shutil.copytree(source_root, build_root, copy_function=shutil.copy2)
            verify_source_tree(build_root, source_rows, reject_extras=True)
            for suffix in (".pdf", ".log", ".fls"):
                candidate = build_root / f"{stem}{suffix}"
                if candidate.exists():
                    raise ValueError(f"fresh target output unexpectedly exists: {candidate.name}")
            result = subprocess.run(
                [*COMMAND, target],
                cwd=build_root,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            )
            transcript = log_dir / f"{stem}.stdout.txt"
            transcript.write_bytes(result.stdout)
            pdf = build_root / f"{stem}.pdf"
            tex_log = build_root / f"{stem}.log"
            fls = build_root / f"{stem}.fls"
            if result.returncode != 0 or not pdf.is_file() or pdf.stat().st_size <= 0:
                raise ValueError(f"cold build failed: {target}: exit {result.returncode}")
            if not tex_log.is_file() or not fls.is_file():
                raise ValueError(f"cold build omitted log or recorder file: {target}")
            log_text = tex_log.read_text(encoding="utf-8", errors="replace")
            if FATAL.search(log_text):
                raise ValueError(f"fatal marker survived successful build: {target}")
            closure = input_closure(
                build_root, set(source_rows), fls, toolchain_roots
            )
            if not closure["closed"]:
                raise ValueError(f"input closure failed: {target}: {closure}")
            extra_outputs = verify_source_tree(
                build_root, source_rows, reject_extras=False
            )
            verify_source_tree(source_root, source_rows, reject_extras=True)
            saved_log = log_dir / f"{stem}.log"
            saved_fls = log_dir / f"{stem}.fls"
            shutil.copyfile(tex_log, saved_log)
            shutil.copyfile(fls, saved_fls)
            warnings = warning_counts(log_text)
            closures.append(closure)
            results.append(
                {
                    "target": target,
                    "command": command_text((*COMMAND, target)),
                    "exit_code": result.returncode,
                    "fresh_isolated_source_copy": True,
                    "tracked_source_post_build_replay": f"{SOURCE_FILES}/{SOURCE_FILES}",
                    "generated_paths_after_build": len(extra_outputs),
                    "pdf": {
                        "path": pdf.name,
                        "bytes": pdf.stat().st_size,
                        "sha256": digest(pdf),
                        "pages": pages(pdf),
                    },
                    "log": {
                        "name": saved_log.name,
                        "bytes": saved_log.stat().st_size,
                        "sha256": digest(saved_log),
                        "warnings": warnings,
                        "fatal_markers": 0,
                    },
                    "recorder": {
                        "name": saved_fls.name,
                        "bytes": saved_fls.stat().st_size,
                        "sha256": digest(saved_fls),
                    },
                    "stdout": {
                        "name": transcript.name,
                        "bytes": transcript.stat().st_size,
                        "sha256": digest(transcript),
                    },
                    "input_closure": closure,
                }
            )
    verify_source_tree(source_root, source_rows, reject_extras=True)
    class_totals: Counter[str] = Counter()
    for closure in closures:
        for row in closure["external_input_classes"]:
            class_totals[str(row["class"])] += int(row["inputs"])
    warning_total = sum(
        sum(int(value) for value in result["log"]["warnings"].values())
        for result in results
    )
    state = (
        "cold_replay_pass_with_observed_warnings"
        if warning_total
        else "cold_replay_pass"
    )
    receipt = {
        "schema": "math-commons-translation-build/v1",
        "job_id": JOB_ID,
        "source_materialization": "exact Git blob bytes",
        "source_commit": ROOT_COMMIT,
        "source_tree": ROOT_TREE,
        "source_files": SOURCE_FILES,
        "source_bytes": SOURCE_BYTES,
        "source_git_modes": SOURCE_MODES,
        "source_verification": {
            "tsv_rows": SOURCE_FILES,
            "unique_safe_paths": SOURCE_FILES,
            "sha256_replay": f"{SOURCE_FILES}/{SOURCE_FILES}",
            "git_blob_oid_replay": f"{SOURCE_FILES}/{SOURCE_FILES}",
            "root_tree_reconstruction": ROOT_TREE,
            "missing": 0,
            "extra": 0,
            "post_build_replay": f"{len(results) * SOURCE_FILES}/{len(results) * SOURCE_FILES}",
        },
        "packet_binding": binding,
        "state": state,
        "environment": {
            "platform": sys.platform,
            "platform_release": platform.release(),
            "python": sys.version.split()[0],
            "latexmk": version(["latexmk", "-version"]),
            "pdftex": version(["pdflatex", "--version"]),
            "bibtex": version(["bibtex", "--version"]),
            "pdfinfo": version(["pdfinfo", "-v"]),
        },
        "dependency_repairs": [
            {"note": note, "provenance": "caller-supplied; not executed by this audit"}
            for note in args.dependency_repair_note
        ],
        "targets": results,
        "input_closure": {
            "targets": len(closures),
            "all_closed": all(bool(row["closed"]) for row in closures),
            "excluded_doc_inputs": 0,
            "unbound_repo_relative_inputs": 0,
            "unknown_external_inputs": 0,
            "external_input_classes": [
                {"class": label, "inputs_across_targets": class_totals[label]}
                for label in sorted(class_totals)
            ],
        },
        "interpretation": "Both root readers were forced through isolated fresh copies of the independently reconstructed Git tree. Observed nonfatal warnings are recorded and are not represented as linguistic or mathematical certification.",
    }
    data = (json.dumps(receipt, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary_output = output.with_suffix(output.suffix + ".tmp")
    temporary_output.write_bytes(data)
    os.replace(temporary_output, output)
    print(
        json.dumps(
            {
                "state": receipt["state"],
                "targets": len(results),
                "bytes": len(data),
                "sha256": sha256_bytes(data),
            },
            separators=(",", ":"),
        )
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (
        OSError,
        ValueError,
        UnicodeError,
        json.JSONDecodeError,
        DuplicateKey,
        subprocess.CalledProcessError,
        zipfile.BadZipFile,
    ) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
