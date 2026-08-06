#!/usr/bin/env python3
"""Build and verify deterministic release assets from an exact Git commit.

The working tree is used only to locate this repository. Every released source
byte is read from a blob reachable from the resolved commit.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import NoReturn


ROOT = Path(__file__).resolve().parents[1]
PROJECT_NAME = "mathematics-commons-pilot"
REQUIRED_READER_FILES = (
    "README.md",
    "WHITE_PAPER.md",
    "LEIDEN_ALIGNMENT.md",
    "GITHUB_PILOT_GUIDE.md",
    "RIGHTS.md",
    "CITATION.cff",
)
MANIFEST_NAME = "RELEASE_MANIFEST.json"
CHECKSUMS_NAME = "SHA256SUMS.txt"

# SemVer 2.0.0, with an optional conventional leading "v".
VERSION_RE = re.compile(
    r"^v?"
    r"(0|[1-9][0-9]*)\."
    r"(0|[1-9][0-9]*)\."
    r"(0|[1-9][0-9]*)"
    r"(?:-((?:0|[1-9][0-9]*|[0-9A-Za-z-]*[A-Za-z-][0-9A-Za-z-]*)"
    r"(?:\.(?:0|[1-9][0-9]*|[0-9A-Za-z-]*[A-Za-z-][0-9A-Za-z-]*))*))?"
    r"(?:\+([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?$"
)
SAFE_REF_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._/@+\-/]*$")
ALLOWED_GIT_MODES = {"100644": 0o644, "100755": 0o755}
WINDOWS_RESERVED_BASENAMES = {
    "aux",
    "clock$",
    "con",
    "conin$",
    "conout$",
    "nul",
    "prn",
    *(f"com{number}" for number in (*range(1, 10), "¹", "²", "³")),
    *(f"lpt{number}" for number in (*range(1, 10), "¹", "²", "³")),
}
WINDOWS_FORBIDDEN_CHARACTERS = frozenset('<>:"|?*')


class ReleaseBuildError(RuntimeError):
    """A fail-closed release-build error suitable for concise CLI output."""


@dataclass(frozen=True)
class GitFile:
    path: str
    oid: str
    git_mode: str
    mode: int
    data: bytes
    sha256: str

    @property
    def size(self) -> int:
        return len(self.data)


def fail(message: str) -> NoReturn:
    raise ReleaseBuildError(message)


def git_environment() -> dict[str, str]:
    """Return an environment that cannot redirect Git away from this repo."""
    env = os.environ.copy()
    for name in (
        "GIT_ALTERNATE_OBJECT_DIRECTORIES",
        "GIT_COMMON_DIR",
        "GIT_DIR",
        "GIT_INDEX_FILE",
        "GIT_NAMESPACE",
        "GIT_OBJECT_DIRECTORY",
        "GIT_REPLACE_REF_BASE",
        "GIT_WORK_TREE",
    ):
        env.pop(name, None)
    env["GIT_NO_REPLACE_OBJECTS"] = "1"
    env["GIT_OPTIONAL_LOCKS"] = "0"
    return env


def run_git(arguments: list[str]) -> bytes:
    git = shutil.which("git")
    if git is None:
        fail("Git executable not found")
    process = subprocess.run(
        [git, "--no-replace-objects", "-C", str(ROOT), *arguments],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=git_environment(),
        check=False,
    )
    detail = process.stderr.decode("utf-8", errors="replace").strip()
    if process.returncode != 0:
        if len(detail) > 800:
            detail = detail[-800:]
        fail(f"Git command failed: {detail or 'no diagnostic returned'}")
    if detail:
        if len(detail) > 800:
            detail = detail[-800:]
        fail(f"Git command emitted an unexpected diagnostic: {detail}")
    return process.stdout


def git_text(arguments: list[str]) -> str:
    try:
        return run_git(arguments).decode("utf-8", errors="strict").strip()
    except UnicodeDecodeError as exc:
        raise ReleaseBuildError("Git returned non-UTF-8 control output") from exc


def validate_repository() -> tuple[str, Path, Path]:
    top_level = Path(git_text(["rev-parse", "--show-toplevel"])).resolve()
    if os.path.normcase(str(top_level)) != os.path.normcase(str(ROOT.resolve())):
        fail("script location does not match the Git repository top level")

    object_format = git_text(["rev-parse", "--show-object-format"])
    if object_format not in {"sha1", "sha256"}:
        fail(f"unsupported Git object format: {object_format!r}")

    git_dir = Path(git_text(["rev-parse", "--absolute-git-dir"])).resolve()
    common_text = git_text(["rev-parse", "--git-common-dir"])
    common_dir = Path(common_text)
    if not common_dir.is_absolute():
        common_dir = ROOT / common_dir
    return object_format, git_dir, common_dir.resolve()


def validate_version(version: str) -> str:
    if version != version.strip() or not version or len(version) > 64:
        fail("version must be a 1-64 character SemVer token")
    if VERSION_RE.fullmatch(version) is None:
        fail("version must be valid SemVer, optionally prefixed with 'v'")
    return version


def validate_ref(ref: str) -> str:
    if ref != ref.strip() or not ref or len(ref) > 256:
        fail("ref must be a non-empty exact Git ref of at most 256 characters")
    if SAFE_REF_RE.fullmatch(ref) is None:
        fail("ref contains whitespace, revision operators, or unsafe characters")
    if not ref.startswith("refs/"):
        fail("ref must be a fully qualified name under refs/")
    if (
        ref.startswith("-")
        or ref.endswith(("/", ".", ".lock"))
        or ".." in ref
        or "//" in ref
        or "@{" in ref
        or any(part in {"", ".", ".."} for part in ref.split("/"))
    ):
        fail("ref is not an exact, well-formed Git ref")
    run_git(["check-ref-format", ref])
    return ref


def resolve_commit(ref: str, object_format: str) -> str:
    referenced_oid = git_text(["show-ref", "--verify", "--hash", ref]).lower()
    expected_length = 40 if object_format == "sha1" else 64
    if (
        len(referenced_oid) != expected_length
        or any(c not in "0123456789abcdef" for c in referenced_oid)
    ):
        fail("exact ref did not resolve to one full object ID")
    commit = git_text(
        [
            "rev-parse",
            "--verify",
            "--end-of-options",
            f"{referenced_oid}^{{commit}}",
        ]
    ).lower()
    if len(commit) != expected_length or any(c not in "0123456789abcdef" for c in commit):
        fail("ref did not resolve to one full commit object ID")
    if git_text(["cat-file", "-t", commit]) != "commit":
        fail("resolved object is not a commit")
    return commit


def resolve_tree(commit: str, object_format: str) -> str:
    commit_data = run_git(["cat-file", "commit", commit])
    first_line = commit_data.split(b"\n", 1)[0]
    if not first_line.startswith(b"tree "):
        fail("commit object does not begin with a tree header")
    try:
        tree = first_line[5:].decode("ascii", errors="strict").lower()
    except UnicodeDecodeError as exc:
        raise ReleaseBuildError("commit tree object ID is not ASCII") from exc
    expected_length = 40 if object_format == "sha1" else 64
    if len(tree) != expected_length or any(c not in "0123456789abcdef" for c in tree):
        fail("commit does not contain one full tree object ID")
    if git_text(["cat-file", "-t", tree]) != "tree":
        fail("commit tree header does not identify a tree object")
    return tree


def validate_source_path(raw_path: bytes) -> str:
    try:
        path = raw_path.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        raise ReleaseBuildError("tracked path is not valid UTF-8") from exc
    if (
        not path
        or path.startswith("/")
        or path.endswith("/")
        or "\\" in path
        or any(ord(character) < 32 or ord(character) == 127 for character in path)
    ):
        fail(f"unsafe tracked path: {path!r}")
    pure = PurePosixPath(path)
    if pure.as_posix() != path or any(part in {"", ".", ".."} for part in pure.parts):
        fail(f"non-canonical tracked path: {path!r}")
    for part in pure.parts:
        if part.endswith((" ", ".")):
            fail(f"Windows-unsafe tracked path component: {part!r}")
        if any(character in WINDOWS_FORBIDDEN_CHARACTERS for character in part):
            fail(f"Windows-unsafe tracked path component: {part!r}")
        device_basename = part.split(".", 1)[0].rstrip(" ").casefold()
        if device_basename in WINDOWS_RESERVED_BASENAMES:
            fail(f"Windows-reserved tracked path component: {part!r}")
    return path


def verify_blob_oid(data: bytes, oid: str, object_format: str, path: str) -> None:
    digest = hashlib.new(object_format)
    digest.update(f"blob {len(data)}\0".encode("ascii"))
    digest.update(data)
    if digest.hexdigest() != oid:
        fail(f"Git blob identity mismatch for {path}")


def read_commit_files(commit: str, object_format: str) -> list[GitFile]:
    tree = run_git(["ls-tree", "-r", "-z", "--full-tree", commit])
    files: list[GitFile] = []
    seen: set[str] = set()
    portable_seen: dict[str, str] = {}
    for raw_entry in tree.split(b"\0"):
        if not raw_entry:
            continue
        try:
            header, raw_path = raw_entry.split(b"\t", 1)
            raw_mode, raw_type, raw_oid = header.split(b" ", 2)
            git_mode = raw_mode.decode("ascii", errors="strict")
            object_type = raw_type.decode("ascii", errors="strict")
            oid = raw_oid.decode("ascii", errors="strict").lower()
        except (ValueError, UnicodeDecodeError) as exc:
            raise ReleaseBuildError("malformed Git tree entry") from exc

        path = validate_source_path(raw_path)
        if path in seen:
            fail(f"duplicate tracked path: {path}")
        seen.add(path)
        portable_key = path.casefold()
        if portable_key in portable_seen:
            fail(
                "case-insensitive tracked-path collision: "
                f"{portable_seen[portable_key]!r} and {path!r}"
            )
        portable_seen[portable_key] = path
        if object_type != "blob" or git_mode not in ALLOWED_GIT_MODES:
            fail(
                f"unsupported tracked entry {path!r}: "
                f"type={object_type!r}, mode={git_mode!r}; links and gitlinks are forbidden"
            )

        data = run_git(["cat-file", "blob", oid])
        verify_blob_oid(data, oid, object_format, path)
        files.append(
            GitFile(
                path=path,
                oid=oid,
                git_mode=git_mode,
                mode=ALLOWED_GIT_MODES[git_mode],
                data=data,
                sha256=hashlib.sha256(data).hexdigest(),
            )
        )

    files.sort(key=lambda item: item.path.encode("utf-8"))
    return files


def release_notes_name(version: str) -> str:
    tag_version = version if version.startswith("v") else f"v{version}"
    return f"RELEASE_NOTES_{tag_version}.md"


def select_reader_files(files: list[GitFile], version: str) -> list[GitFile]:
    by_path = {item.path: item for item in files}
    missing = [name for name in REQUIRED_READER_FILES if name not in by_path]
    if missing:
        fail(f"required reader file absent from commit: {', '.join(missing)}")
    names = list(REQUIRED_READER_FILES)
    optional_notes = release_notes_name(version)
    if optional_notes in by_path:
        names.append(optional_notes)
    return [by_path[name] for name in names]


def is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


def resolve_output_dir(value: str, git_dir: Path, common_dir: Path) -> Path:
    if not value or "\0" in value:
        fail("output directory is empty or invalid")
    output = Path(value).expanduser()
    if not output.is_absolute():
        output = ROOT / output
    output = output.resolve(strict=False)
    if output == ROOT.resolve():
        fail("output directory must not be the repository root")
    if is_relative_to(output, git_dir) or is_relative_to(output, common_dir):
        fail("output directory must not be inside Git metadata")
    if output.exists():
        fail("output path already exists; choose a new dedicated directory")
    return output


def expected_output_names(
    archive_name: str, reader_files: list[GitFile]
) -> set[str]:
    return {
        archive_name,
        MANIFEST_NAME,
        CHECKSUMS_NAME,
        *(item.path for item in reader_files),
    }


def verify_output_set(directory: Path, expected: set[str], *, allow_missing: bool) -> None:
    if not directory.exists():
        if allow_missing:
            return
        fail(f"output directory does not exist: {directory}")
    actual: set[str] = set()
    for entry in directory.iterdir():
        actual.add(entry.name)
        if entry.is_symlink() or not entry.is_file():
            fail(f"unexpected non-file output: {entry.name}")
    unexpected = actual - expected
    missing = expected - actual
    if unexpected:
        fail(f"unexpected output present: {', '.join(sorted(unexpected))}")
    if missing and not allow_missing:
        fail(f"expected output missing: {', '.join(sorted(missing))}")


def write_exclusive(path: Path, data: bytes) -> None:
    with path.open("xb") as stream:
        stream.write(data)


def write_archive(path: Path, files: list[GitFile], top_level: str) -> None:
    with path.open("xb") as raw_stream:
        with tarfile.open(
            fileobj=raw_stream,
            mode="w",
            format=tarfile.USTAR_FORMAT,
            encoding="utf-8",
            errors="strict",
        ) as archive:
            for item in files:
                info = tarfile.TarInfo(name=f"{top_level}/{item.path}")
                info.mode = item.mode
                info.uid = 0
                info.gid = 0
                info.size = item.size
                info.mtime = 0
                info.type = tarfile.REGTYPE
                info.linkname = ""
                info.uname = ""
                info.gname = ""
                info.devmajor = 0
                info.devminor = 0
                info.pax_headers = {}
                try:
                    archive.addfile(info, io.BytesIO(item.data))
                except (ValueError, tarfile.TarError) as exc:
                    raise ReleaseBuildError(
                        f"path cannot be represented as strict USTAR: {item.path}"
                    ) from exc


def parse_octal(field: bytes, label: str) -> int:
    value = field.rstrip(b"\0 ").lstrip(b" ")
    if not value or any(byte not in b"01234567" for byte in value):
        fail(f"archive has invalid USTAR {label} field")
    return int(value, 8)


def verify_raw_ustar(path: Path, files: list[GitFile], top_level: str) -> None:
    raw = path.read_bytes()
    if len(raw) % tarfile.RECORDSIZE != 0:
        fail("archive length is not an integral USTAR record")
    offset = 0
    for item in files:
        header = raw[offset : offset + tarfile.BLOCKSIZE]
        if len(header) != tarfile.BLOCKSIZE or not any(header):
            fail(f"archive header missing for {item.path}")
        if header[257:263] != b"ustar\0" or header[263:265] != b"00":
            fail(f"archive member is not strict USTAR: {item.path}")
        if header[156:157] not in {b"0", b"\0"}:
            fail(f"archive member is not a regular file: {item.path}")

        stored_checksum = parse_octal(header[148:156], "checksum")
        calculated_checksum = sum(header[:148]) + (8 * 32) + sum(header[156:])
        if stored_checksum != calculated_checksum:
            fail(f"archive header checksum mismatch for {item.path}")

        raw_name = header[0:100].split(b"\0", 1)[0]
        raw_prefix = header[345:500].split(b"\0", 1)[0]
        combined = raw_prefix + (b"/" if raw_prefix else b"") + raw_name
        try:
            member_name = combined.decode("utf-8", errors="strict")
        except UnicodeDecodeError as exc:
            raise ReleaseBuildError("archive member name is not UTF-8") from exc
        expected_name = f"{top_level}/{item.path}"
        if member_name != expected_name:
            fail(f"archive member ordering/name mismatch at {item.path}")

        archived_size = parse_octal(header[124:136], "size")
        if archived_size != item.size:
            fail(f"archive size mismatch for {item.path}")
        offset += tarfile.BLOCKSIZE + (
            (item.size + tarfile.BLOCKSIZE - 1) // tarfile.BLOCKSIZE
        ) * tarfile.BLOCKSIZE

    trailer = raw[offset:]
    if len(trailer) < 2 * tarfile.BLOCKSIZE or any(trailer):
        fail("archive has a missing, malformed, or non-zero USTAR trailer")


def verify_archive(path: Path, files: list[GitFile], top_level: str) -> None:
    expected_names = [f"{top_level}/{item.path}" for item in files]
    try:
        with tarfile.open(
            path,
            mode="r:",
            encoding="utf-8",
            errors="strict",
        ) as archive:
            if archive.pax_headers:
                fail("archive unexpectedly contains global PAX metadata")
            members = archive.getmembers()
            if [member.name for member in members] != expected_names:
                fail("archive members are not the exact sorted tracked-file set")
            for member, item in zip(members, files, strict=True):
                if (
                    not member.isfile()
                    or member.type != tarfile.REGTYPE
                    or member.mode != item.mode
                    or member.uid != 0
                    or member.gid != 0
                    or member.uname != ""
                    or member.gname != ""
                    or member.mtime != 0
                    or member.size != item.size
                    or member.linkname != ""
                    or member.pax_headers
                ):
                    fail(f"archive metadata mismatch for {item.path}")
                extracted = archive.extractfile(member)
                if extracted is None or extracted.read() != item.data:
                    fail(f"archive content mismatch for {item.path}")
    except (tarfile.TarError, UnicodeError, OSError) as exc:
        raise ReleaseBuildError(f"archive verification failed: {exc}") from exc
    verify_raw_ustar(path, files, top_level)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def manifest_bytes(
    *,
    commit: str,
    tree: str,
    object_format: str,
    version: str,
    archive_path: Path,
    top_level: str,
    files: list[GitFile],
    reader_files: list[GitFile],
) -> bytes:
    document = {
        "archive": {
            "compression": "none",
            "format": "ustar",
            "name": archive_path.name,
            "sha256": sha256_file(archive_path),
            "size": archive_path.stat().st_size,
            "top_level": f"{top_level}/",
        },
        "commit": commit,
        "files": [
            {
                "archive_path": f"{top_level}/{item.path}",
                "git_mode": item.git_mode,
                "mode": f"{item.mode:04o}",
                "path": item.path,
                "sha256": item.sha256,
                "size": item.size,
            }
            for item in files
        ],
        "object_format": object_format,
        "project": PROJECT_NAME,
        "reader_files": [item.path for item in reader_files],
        "schema_version": 1,
        "tree": tree,
        "version": version,
    }
    return (
        json.dumps(document, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")


def write_checksums(directory: Path, names: set[str]) -> bytes:
    covered = sorted(names - {CHECKSUMS_NAME}, key=lambda name: name.encode("utf-8"))
    content = "".join(
        f"{sha256_file(directory / name)}  {name}\n" for name in covered
    ).encode("utf-8")
    write_exclusive(directory / CHECKSUMS_NAME, content)
    return content


def verify_checksums(directory: Path, expected_names: set[str]) -> None:
    checksum_path = directory / CHECKSUMS_NAME
    try:
        content = checksum_path.read_bytes()
    except OSError as exc:
        raise ReleaseBuildError("cannot read checksum file") from exc
    expected_covered = sorted(
        expected_names - {CHECKSUMS_NAME}, key=lambda name: name.encode("utf-8")
    )
    expected_content = "".join(
        f"{sha256_file(directory / name)}  {name}\n" for name in expected_covered
    ).encode("utf-8")
    if content != expected_content:
        fail("checksum file does not exactly cover every other output")


def verify_staged_release(
    directory: Path,
    expected_names: set[str],
    archive_name: str,
    files: list[GitFile],
    reader_files: list[GitFile],
    top_level: str,
    expected_manifest: bytes,
) -> None:
    verify_output_set(directory, expected_names, allow_missing=False)
    verify_archive(directory / archive_name, files, top_level)
    if (directory / MANIFEST_NAME).read_bytes() != expected_manifest:
        fail("release manifest bytes changed after generation")
    try:
        json.loads(expected_manifest.decode("utf-8"))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise ReleaseBuildError("release manifest is not valid UTF-8 JSON") from exc
    for item in reader_files:
        if (directory / item.path).read_bytes() != item.data:
            fail(f"reader copy differs from Git blob: {item.path}")
    verify_checksums(directory, expected_names)


def publish_staged_release(staging: Path, output: Path) -> None:
    if output.exists():
        fail("output path appeared during build; refusing non-atomic replacement")
    os.replace(staging, output)


def build_release(ref: str, version: str, output_value: str) -> tuple[Path, str]:
    object_format, git_dir, common_dir = validate_repository()
    ref = validate_ref(ref)
    version = validate_version(version)
    commit = resolve_commit(ref, object_format)
    tree = resolve_tree(commit, object_format)
    files = read_commit_files(commit, object_format)
    reader_files = select_reader_files(files, version)

    top_level = f"{PROJECT_NAME}-{version}"
    archive_name = f"{top_level}.tar"
    names = expected_output_names(archive_name, reader_files)
    output = resolve_output_dir(output_value, git_dir, common_dir)
    output.parent.mkdir(parents=True, exist_ok=True)

    staging = Path(
        tempfile.mkdtemp(prefix=f".{PROJECT_NAME}-release-", dir=output.parent)
    )
    try:
        archive_path = staging / archive_name
        write_archive(archive_path, files, top_level)
        verify_archive(archive_path, files, top_level)

        for item in reader_files:
            write_exclusive(staging / item.path, item.data)
        generated_manifest = manifest_bytes(
            commit=commit,
            tree=tree,
            object_format=object_format,
            version=version,
            archive_path=archive_path,
            top_level=top_level,
            files=files,
            reader_files=reader_files,
        )
        write_exclusive(staging / MANIFEST_NAME, generated_manifest)
        write_checksums(staging, names)
        verify_staged_release(
            staging,
            names,
            archive_name,
            files,
            reader_files,
            top_level,
            generated_manifest,
        )
        publish_staged_release(staging, output)
    finally:
        if staging.exists():
            shutil.rmtree(staging)

    verify_staged_release(
        output,
        names,
        archive_name,
        files,
        reader_files,
        top_level,
        generated_manifest,
    )
    return output, commit


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build verified deterministic USTAR release assets from Git objects."
    )
    parser.add_argument(
        "--ref",
        required=True,
        help="fully qualified exact ref (for example refs/tags/v0.1.0)",
    )
    parser.add_argument(
        "--version", required=True, help="SemVer token used verbatim in asset paths"
    )
    parser.add_argument(
        "--output-dir",
        required=True,
        help="dedicated output directory (relative paths are repository-relative)",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        output, commit = build_release(args.ref, args.version, args.output_dir)
    except ReleaseBuildError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    except OSError as exc:
        print(f"ERROR: filesystem operation failed: {exc}", file=sys.stderr)
        return 2

    print(f"PASS: deterministic release verified from commit {commit}")
    for path in sorted(output.iterdir(), key=lambda item: item.name.encode("utf-8")):
        print(f"{sha256_file(path)}  {path.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
