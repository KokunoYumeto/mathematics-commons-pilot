#!/usr/bin/env python3
"""Fail-closed structural checks for the public concept repository."""

from __future__ import annotations

import codecs
import hashlib
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import unquote

import validate_packets


ROOT = Path(__file__).resolve().parents[1]
R1_READBACK_BYTES = 19_125
R1_READBACK_SHA256 = "60EF221B444E27FDF98C1A618DE5B556DBB8D718A526930A332B078E528F83FC"
REQUIRED = {
    ".gitattributes",
    "README.md",
    "STATUS.md",
    "WHITE_PAPER.md",
    "LEIDEN_ALIGNMENT.md",
    "GITHUB_PILOT_GUIDE.md",
    "GITHUB_2FA_CONTINUITY.md",
    "PILOT_OPERATIONS.md",
    "PILOT_LAUNCH.md",
    "PILOT_CANDIDATES.md",
    "MIRROR_RUNBOOK.md",
    "NODE_HANDOFF.md",
    "RELEASE_NOTES_v0.1.0.md",
    "RELEASE_NOTES_v0.1.1.md",
    "START_HERE_FOR_HUMANS.md",
    "START_HERE_FOR_AGENTS.md",
    "CONTRIBUTING.md",
    "RIGHTS.md",
    "LICENSE",
    "CITATION.cff",
    "schemas/README.md",
    "schemas/job-meta.schema.json",
    "schemas/job-catalog.schema.json",
    "schemas/job-asset.schema.json",
    "schemas/translation-catalog.schema.json",
    "schemas/translation-choices.schema.json",
    "schemas/translation-source.schema.json",
    "schemas/translation-build.schema.json",
    "schemas/formalization-intake.schema.json",
    "schemas/portal-catalog.schema.json",
    "schemas/portal-readback.schema.json",
    "schemas/catalog-check.schema.json",
    "schemas/release-readback.schema.json",
    "schemas/problem-record.schema.json",
    "schemas/research-packet.schema.json",
    "schemas/packet-transition.schema.json",
    "schemas/source-record.schema.json",
    "schemas/run-record.schema.json",
    "schemas/evidence-record.schema.json",
    "schemas/review-record.schema.json",
    "tools/build_release_archive.py",
    "tools/pack_job.py",
    "tools/build_jobs.py",
    "tools/build_r2_admission.py",
    "tools/repair_stale_packet_manifests.py",
    "tools/readback_jobs_release.py",
    "tools/build_openlogic.py",
    "tools/audit_openlogic_build.py",
    "tools/build_translate.py",
    "tools/normalize_translation_catalog.py",
    "tools/update_translation_kit_v8.py",
    "tools/migrate_translations_v7.py",
    "tools/readback_portal.py",
    "tools/validate_jobs.py",
    "tools/commons.py",
    "tools/validate_packets.py",
    "tests/test_validate_packets.py",
    "tests/test_validator_hardening.py",
    "tests/test_commons_cli_hardening.py",
    "tests/test_record_contracts.py",
    "tests/test_validate_repository.py",
    "tests/test_job_catalog.py",
    "tests/test_language_evidence.py",
    "tests/test_openlogic_source.py",
    "tests/test_formalization_intake.py",
    "catalog/README.md",
    "catalog/job-meta.json",
    "catalog/jobs.json",
    "catalog/receipts/r2-admission.json",
    "catalog/receipts/no-failure-hardening.json",
    "catalog/receipts/openlogic.json",
    "catalog/receipts/global.json",
    "catalog/receipts/gordan2.txt",
    "catalog/receipts/mikami.json",
    "catalog/translations.json",
    "catalog/formalize.json",
    "catalog/portals.json",
    "catalog/readback.json",
    "catalog/readback-r2.json",
    "catalog/translate-rb.json",
    "catalog/translate-rb-v4.json",
    "catalog/translate-rb-v5.json",
    "catalog/translate-rb-v6.json",
    "catalog/openlogic-rb.json",
    "catalog/check.json",
    "docs/run.md",
    "docs/fidelity.md",
    "docs/formalize.md",
    "docs/translations.md",
    "docs/adopt.md",
    "docs/legacy.md",
    "docs/release-r1.md",
    "docs/release-r2.md",
    "docs/release-translate-v2.md",
    "docs/release-translate-v3.md",
    "docs/release-translate-v4.md",
    "docs/release-translate-v5.md",
    "docs/release-translate-v6.md",
    "docs/openlogic-v1.md",
    "docs/translate-v7.md",
    "docs/translate-v8.md",
    "docs/translate-v9.md",
    "docs/release-workbench-v0.2.md",
    "docs/roadmap.md",
    "docs/workbench.md",
    "kits/translate/README.md",
    "kits/translate/START.md",
    "kits/translate/LOCAL.md",
    "kits/translate/WEB.md",
    "kits/translate/LANGS.md",
    "kits/translate/WORKS.json",
    "kits/translate/KIT.json",
    "kits/translate/MANIFEST.sha256",
    "kits/translate/PROMPT.md",
    "kits/translate/QA.md",
    "kits/translate/RETURN.md",
    "kits/translate/SOURCE.json",
    "kits/openlogic/BUILD.json",
    "kits/openlogic/CHECKPOINT.json",
    "kits/openlogic/JOB.json",
    "kits/openlogic/LOCAL.md",
    "kits/openlogic/NOTICE.md",
    "kits/openlogic/PROMPT.md",
    "kits/openlogic/QA.json",
    "kits/openlogic/QA.md",
    "kits/openlogic/README.md",
    "kits/openlogic/RETURN.md",
    "kits/openlogic/SOURCE.json",
    "kits/openlogic/START.md",
    "kits/openlogic/WEB.md",
    "kits/translate-r1/README.md",
    "kits/translate-r1/PROMPT.md",
    "kits/translate-r1/QA.md",
    "kits/translate-r1/SOURCE.json",
    "catalog/assets/translate-v2.json",
    "catalog/assets/translate-v3.json",
    "catalog/assets/translate-v4.json",
    "catalog/assets/translate-v5.json",
    "catalog/assets/translate-v6.json",
    "catalog/assets/openlogic.json",
    "catalog/assets/translate-v7.json",
    "catalog/assets/translate-v8.json",
    "catalog/assets/translate-v9.json",
    "catalog/assets/translate-v9-complete.json",
    ".github/CODEOWNERS",
    ".github/workflows/validate.yml",
    ".github/ISSUE_TEMPLATE/pilot_volunteer.yml",
    ".github/ISSUE_TEMPLATE/job_return.yml",
    ".github/ISSUE_TEMPLATE/translation.yml",
}

PRIVATE_PATTERNS = (
    # Split detector literals so this public validator can scan its own source
    # without mistaking the detector definitions for leaked values.
    re.compile(
        r"[A-Za-z]:[\\/]" + "(?:Users|Documents and Settings)" + r"[\\/]",
        re.IGNORECASE,
    ),
    re.compile("/" + "Users/" + r"[^/\s]+/"),
    re.compile("/" + "home/" + r"[^/\s]+/"),
    re.compile("github" + r"_pat_[A-Za-z0-9_]{20,}"),
    re.compile("gh" + r"[pousr]_[A-Za-z0-9]{20,}"),
    re.compile(r"\b" + "AK" + r"IA[0-9A-Z]{16}\b"),
    re.compile("-----BEGIN " + r"(?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(r"\bsk-" + r"[A-Za-z0-9_-]{20,}\b"),
    re.compile(r"(?i)zenodo" + r"[_-]?token\s*[:=]\s*[^\s]+"),
)

MARKDOWN_LINK = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
IGNORED_TOP_LEVEL = {".git", "dist"}
IGNORED_LOCAL_BUILD_DIRECTORIES = {"__pycache__"}
MAX_SCAN_FILE_BYTES = 2 * 1024 * 1024
MAX_PUBLIC_FILE_BYTES = 256 * 1024 * 1024
MAX_TOTAL_PUBLIC_BYTES = 512 * 1024 * 1024
MAX_TRACKED_LIST_BYTES = 16 * 1024 * 1024
MAX_PUBLIC_FILES = 100_000
FILE_READ_CHUNK_BYTES = 64 * 1024
BINARY_SUFFIXES = {
    ".7z",
    ".avi",
    ".docx",
    ".gif",
    ".gz",
    ".ico",
    ".jpeg",
    ".jpg",
    ".mov",
    ".mp3",
    ".mp4",
    ".pdf",
    ".png",
    ".pptx",
    ".pyc",
    ".tar",
    ".webp",
    ".xlsx",
    ".zip",
}
INFRASTRUCTURE_ROOT_FILES = {
    name for name in REQUIRED if "/" not in name
} | {
    ".gitignore",
    "AGENTS.md",
    "MATHEMATICS_COMMONS_DURABLE_REQUIREMENTS.md",
    "PROJECT_LOGBOOK.md",
    "SESSION_RECOVERY.md",
}
INFRASTRUCTURE_DIRECTORY_PREFIXES = {
    ".github",
    "catalog",
    "docs",
    "kits",
    "schemas",
    "tools",
    "tests",
}
ARTIFACT_MANIFEST_RECORD_PREFIXES = set(validate_packets.DEFAULT_INSTANCE_DIRS)

PHASE_A_C0 = "3fd7a29560e78ac3ecaa131707b61727c25ae9fd"
PHASE_A_C0_TIME = datetime(2026, 8, 6, 23, 32, 42, tzinfo=timezone.utc)
PHASE_A_RECORD_PATHS = {
    "examples/calibration/source-record.json",
    "examples/calibration/problem-record.json",
    "examples/calibration/research-packet-01-draft.json",
    "examples/calibration/research-packet-02-ready.json",
    "examples/calibration/research-packet-03-claimed.json",
    "examples/calibration/research-packet-04-in-progress.json",
    "examples/calibration/research-packet-05-submitted.json",
    "examples/calibration/packet-transition-01-draft-ready.json",
    "examples/calibration/packet-transition-02-ready-claimed.json",
    "examples/calibration/packet-transition-03-claimed-in-progress.json",
    "examples/calibration/packet-transition-04-in-progress-submitted.json",
    "examples/calibration/producer-run.json",
    "examples/calibration/evidence-record.json",
}
PHASE_A_ARTIFACT_PATHS = {
    "examples/calibration/artifacts/odd-sum-statement.md",
    "work/CAL-PACKET-001/odd-sum-proof.md",
}
PHASE_A_PACKET_EXPECTATIONS = {
    "research-packet-01-draft.json": ("1.0.0", "draft", None),
    "research-packet-02-ready.json": ("1.1.0", "ready", None),
    "research-packet-03-claimed.json": ("1.2.0", "claimed", PHASE_A_C0),
    "research-packet-04-in-progress.json": ("1.3.0", "in_progress", PHASE_A_C0),
    "research-packet-05-submitted.json": ("1.4.0", "submitted", PHASE_A_C0),
}
PHASE_A_TRANSITION_EXPECTATIONS = {
    "packet-transition-01-draft-ready.json": (1, "draft", "ready"),
    "packet-transition-02-ready-claimed.json": (2, "ready", "claimed"),
    "packet-transition-03-claimed-in-progress.json": (3, "claimed", "in_progress"),
    "packet-transition-04-in-progress-submitted.json": (4, "in_progress", "submitted"),
}


@dataclass(frozen=True)
class ArtifactDeclaration:
    """One repository artifact declaration extracted from a record."""

    record_path: Path
    record: dict[str, Any]
    record_type: str
    artifact_path: str
    artifact_id: str | None
    byte_size: Any
    hashes: Any


@dataclass(frozen=True)
class PublicFileInspection:
    """Bounded byte-level facts used to classify a public file."""

    byte_size: int
    sha256: str
    has_nul: bool
    valid_utf8: bool


def is_public_repository_path(path: Path) -> bool:
    """Return whether a path belongs to source content, not local build output."""

    relative = path.relative_to(ROOT)
    return bool(relative.parts) and relative.parts[0] not in IGNORED_TOP_LEVEL


def public_repository_files(errors: list[str]) -> list[Path]:
    """Enumerate tracked and local public files without following symlinks."""

    candidates: set[Path] = set()
    if (ROOT / ".git").exists():
        try:
            completed = subprocess.run(
                ["git", "ls-files", "-z"],
                cwd=ROOT,
                check=False,
                capture_output=True,
                timeout=10,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            errors.append(f"could not enumerate tracked files safely: {exc}")
            completed = None
        if completed is not None:
            if completed.returncode != 0:
                errors.append("could not enumerate tracked files safely")
            elif len(completed.stdout) > MAX_TRACKED_LIST_BYTES:
                errors.append("tracked-file listing exceeds the bounded scan limit")
            else:
                raw_paths = [item for item in completed.stdout.split(b"\0") if item]
                if len(raw_paths) > MAX_PUBLIC_FILES:
                    errors.append(
                        f"tracked-file listing exceeds {MAX_PUBLIC_FILES} entries"
                    )
                for raw_path in raw_paths[:MAX_PUBLIC_FILES]:
                    try:
                        relative = raw_path.decode("utf-8")
                    except UnicodeDecodeError:
                        errors.append("tracked path is not valid UTF-8")
                        continue
                    candidates.add(ROOT / relative)

    # Include local untracked public files as well; CI sees these as tracked, but
    # local validation must not create a blind spot before the first commit.
    walked = 0
    for directory, directory_names, file_names in os.walk(ROOT, followlinks=False):
        directory_path = Path(directory)
        if directory_path == ROOT:
            directory_names[:] = [
                name for name in directory_names if name not in IGNORED_TOP_LEVEL
            ]
        directory_names[:] = [
            name
            for name in directory_names
            if name not in IGNORED_LOCAL_BUILD_DIRECTORIES
        ]
        for name in list(directory_names):
            child = directory_path / name
            if child.is_symlink():
                candidates.add(child)
                directory_names.remove(name)
        for name in file_names:
            walked += 1
            if walked > MAX_PUBLIC_FILES:
                errors.append(f"repository walk exceeds {MAX_PUBLIC_FILES} files")
                break
            candidates.add(directory_path / name)
        if walked > MAX_PUBLIC_FILES:
            break

    safe_files: list[Path] = []
    resolved_root = ROOT.resolve()
    for path in sorted(candidates):
        try:
            relative = path.relative_to(ROOT)
        except ValueError:
            errors.append(f"public path escapes repository: {path}")
            continue
        if not relative.parts or relative.parts[0] in IGNORED_TOP_LEVEL:
            continue
        if path.is_symlink():
            errors.append(f"public symbolic link is not permitted: {relative.as_posix()}")
            continue
        try:
            resolved = path.resolve()
            resolved.relative_to(resolved_root)
        except (OSError, ValueError):
            errors.append(f"public path resolves outside repository: {relative.as_posix()}")
            continue
        if resolved.is_file():
            safe_files.append(path)
    return safe_files


def read_public_text(path: Path, errors: list[str]) -> str | None:
    """Read any bounded strict-UTF-8/no-NUL payload for leakage scanning.

    Extensions are not a content trust boundary: readable text renamed ``.png``
    must still pass the same credential/private-path scan.  NUL-containing and
    non-UTF-8 media are never decoded with a lossy codec; their publication
    eligibility is decided separately from exact manifests and byte hashes.
    """

    relative = path.relative_to(ROOT).as_posix()
    try:
        size = path.stat().st_size
    except OSError as exc:
        errors.append(f"cannot inspect public file {relative}: {exc}")
        return None
    if size > MAX_SCAN_FILE_BYTES:
        errors.append(
            f"public text candidate exceeds {MAX_SCAN_FILE_BYTES} bytes: {relative}"
        )
        return None
    try:
        payload = path.read_bytes()
    except OSError as exc:
        errors.append(f"cannot read public file {relative}: {exc}")
        return None
    if b"\0" in payload:
        return None
    try:
        return payload.decode("utf-8")
    except UnicodeDecodeError:
        return None


def inspect_public_file(path: Path) -> PublicFileInspection:
    """Hash and classify one size-bounded file without retaining its contents."""

    digest = hashlib.sha256()
    decoder = codecs.getincrementaldecoder("utf-8")("strict")
    has_nul = False
    valid_utf8 = True
    byte_size = 0
    with path.open("rb") as handle:
        while True:
            chunk = handle.read(FILE_READ_CHUNK_BYTES)
            if not chunk:
                break
            byte_size += len(chunk)
            digest.update(chunk)
            if b"\0" in chunk:
                has_nul = True
            if valid_utf8:
                try:
                    decoder.decode(chunk, final=False)
                except UnicodeDecodeError:
                    valid_utf8 = False
        if valid_utf8:
            try:
                decoder.decode(b"", final=True)
            except UnicodeDecodeError:
                valid_utf8 = False
    return PublicFileInspection(
        byte_size=byte_size,
        sha256=digest.hexdigest(),
        has_nul=has_nul,
        valid_utf8=valid_utf8,
    )


def artifact_declaration_from_record(
    record_path: Path,
    record: dict[str, Any],
) -> ArtifactDeclaration | None:
    """Extract the single public-artifact slot supported by a record type."""

    record_type = record.get("record_type")
    artifact_path: Any
    artifact_id: Any = None
    byte_size: Any
    hashes: Any
    if record_type == "problem_record":
        statement = record.get("statement")
        if not isinstance(statement, dict):
            return None
        artifact_path = statement.get("artifact_path")
        artifact_id = statement.get("artifact_id")
        byte_size = statement.get("byte_size")
        hashes = statement.get("hashes")
    elif record_type == "source_record":
        locator = record.get("locator")
        integrity = record.get("integrity")
        if (
            not isinstance(locator, dict)
            or locator.get("reference_kind") != "repository_artifact"
            or not isinstance(integrity, dict)
        ):
            return None
        artifact_path = locator.get("canonical_reference")
        byte_size = integrity.get("byte_size")
        hashes = integrity.get("hashes")
    elif record_type == "evidence_record":
        artifact_path = record.get("artifact_path")
        artifact_id = record.get("artifact_id")
        byte_size = record.get("byte_size")
        hashes = record.get("hashes")
    else:
        return None
    if not isinstance(artifact_path, str):
        return None
    return ArtifactDeclaration(
        record_path=record_path,
        record=record,
        record_type=record_type,
        artifact_path=artifact_path,
        artifact_id=artifact_id if isinstance(artifact_id, str) else None,
        byte_size=byte_size,
        hashes=hashes,
    )


def collect_artifact_declarations(
    files: list[Path],
) -> dict[str, list[ArtifactDeclaration]]:
    """Index parseable problem/source/evidence declarations by exact path."""

    declarations: dict[str, list[ArtifactDeclaration]] = {}
    for path in files:
        if path.suffix.lower() != ".json":
            continue
        relative = path.relative_to(ROOT)
        if (
            not relative.parts
            or relative.parts[0] not in ARTIFACT_MANIFEST_RECORD_PREFIXES
        ):
            continue
        try:
            if path.stat().st_size > MAX_SCAN_FILE_BYTES:
                continue
            record = validate_packets.load_json(path)
        except (OSError, ValueError):
            continue
        if not isinstance(record, dict):
            continue
        declaration = artifact_declaration_from_record(path, record)
        if declaration is not None:
            declarations.setdefault(declaration.artifact_path, []).append(declaration)
    return declarations


def declared_sha256(hashes: Any) -> str | None:
    """Return one exact lowercase SHA-256 declaration, otherwise fail closed."""

    if not isinstance(hashes, list):
        return None
    values = [
        item.get("digest")
        for item in hashes
        if isinstance(item, dict) and item.get("algorithm") == "sha256"
    ]
    if (
        len(values) != 1
        or not isinstance(values[0], str)
        or re.fullmatch(r"[a-f0-9]{64}", values[0]) is None
    ):
        return None
    return values[0]


def artifact_manifest_issues(
    declaration: ArtifactDeclaration,
    inspection: PublicFileInspection,
    schema_set: validate_packets.SchemaSet,
) -> list[str]:
    """Return publication-gate defects in one matching artifact manifest."""

    issues: list[str] = []
    schema_document = schema_set.by_record_type.get(declaration.record_type)
    if schema_document is None:
        schema_errors = ["unknown manifest record type"]
    else:
        schema_errors = validate_packets.validate_instance(
            declaration.record,
            schema_document.body,
            schema_set,
            schema_document,
        )
    if schema_errors:
        issues.append("record is not schema-valid")

    if (
        isinstance(declaration.byte_size, bool)
        or not isinstance(declaration.byte_size, int)
        or declaration.byte_size != inspection.byte_size
    ):
        issues.append("byte_size does not match exact artifact bytes")
    if declared_sha256(declaration.hashes) != inspection.sha256:
        issues.append("SHA-256 does not match exact artifact bytes")

    boundary = declaration.record.get("submission_boundary")
    if not isinstance(boundary, dict):
        issues.append("submission_boundary is missing")
        boundary = {}
    if boundary.get("redaction_status") != "passed":
        issues.append("redaction_status is not passed")
    if boundary.get("publication_preview_status") != "approved":
        issues.append("publication_preview_status is not approved")
    if boundary.get("retention_rule") != "approved_submission_only":
        issues.append("retention_rule is not approved_submission_only")
    allowlisted = boundary.get("allowlisted_artifact_ids")
    if not isinstance(allowlisted, list):
        allowlisted = []

    rights = declaration.record.get("submission_rights")
    if not isinstance(rights, dict):
        issues.append("submission_rights is missing")
        rights = {}
    if rights.get("commons_originated_record") is not True:
        issues.append("Commons-originated record status is not affirmed")
    if rights.get("dedication") != "CC0-1.0":
        issues.append("Commons dedication is not CC0-1.0")
    if rights.get("third_party_rights_preserved") is not True:
        issues.append("third-party rights preservation is not affirmed")
    if rights.get("redistribution_status") != "permitted":
        issues.append("submission redistribution is not permitted")
    submitted = rights.get("submitted_component_ids")
    if not isinstance(submitted, list):
        submitted = []

    if declaration.record_type in {"problem_record", "evidence_record"}:
        if declaration.artifact_id not in allowlisted:
            issues.append("artifact ID is absent from the public allowlist")
        if declaration.artifact_id not in submitted:
            issues.append("artifact ID is absent from submitted components")
    else:
        if not allowlisted:
            issues.append("source artifact allowlist is empty")
        elif not set(allowlisted).issubset(set(submitted)):
            issues.append("source artifact allowlist is not fully submitted")
        assessment = declaration.record.get("rights_assessment")
        if not isinstance(assessment, dict):
            issues.append("source rights assessment is missing")
            assessment = {}
        if assessment.get("review_status") != "reviewed":
            issues.append("source rights assessment is not reviewed")
        if assessment.get("redistribution_status") != "permitted":
            issues.append("source redistribution is not permitted")
        permissions = assessment.get("permissions")
        if not isinstance(permissions, dict) or permissions.get(
            "redistribution"
        ) != "permitted":
            issues.append("source redistribution permission is not permitted")
        components = declaration.record.get("third_party_components")
        if not isinstance(components, list) or not components:
            issues.append("source component rights are missing")
        else:
            for component in components:
                if not isinstance(component, dict):
                    issues.append("source component rights are malformed")
                    break
                component_permissions = component.get("permissions")
                if (
                    component.get("redistribution_status") != "permitted"
                    or not isinstance(component_permissions, dict)
                    or component_permissions.get("redistribution") != "permitted"
                ):
                    issues.append("a source component is not redistributable")
                    break
    return issues


def is_project_infrastructure_file(
    path: Path,
    schema_set: validate_packets.SchemaSet,
) -> bool:
    """Return whether a UTF-8 file is an explicitly allowed project surface."""

    relative = path.relative_to(ROOT)
    relative_posix = relative.as_posix()
    if len(relative.parts) == 1 and relative_posix in INFRASTRUCTURE_ROOT_FILES:
        return True
    if relative.parts and relative.parts[0] in INFRASTRUCTURE_DIRECTORY_PREFIXES:
        return True
    if (
        path.suffix.lower() == ".json"
        and relative.parts
        and relative.parts[0] in ARTIFACT_MANIFEST_RECORD_PREFIXES
    ):
        return not validate_packets.validate_record_file(path, schema_set)
    return False


def check_public_artifact_manifests(errors: list[str], files: list[Path]) -> None:
    """Require exact reviewed manifests for every public artifact surface.

    Explicit project infrastructure may be ordinary UTF-8 text without an
    artifact record.  Every other file, including UTF-8 artifacts, must have an
    exact manifest.  Known-binary, NUL-containing, and non-UTF-8 files always
    require one, even beneath an infrastructure directory.  The check never
    searches opaque bytes for credential-like substrings: it records only byte
    count, SHA-256, NUL presence, and strict UTF-8 validity before evaluating
    public record and rights declarations.
    """

    total_bytes = 0
    sizes: dict[Path, int] = {}
    for path in files:
        relative = path.relative_to(ROOT).as_posix()
        try:
            size = path.stat().st_size
        except OSError as exc:
            errors.append(f"cannot inspect public file {relative}: {exc}")
            continue
        sizes[path] = size
        total_bytes += size
        if total_bytes > MAX_TOTAL_PUBLIC_BYTES:
            errors.append(
                f"public repository files exceed the bounded {MAX_TOTAL_PUBLIC_BYTES}-byte scan"
            )
            return

    try:
        schema_set = validate_packets.load_schema_set()
    except ValueError as exc:
        errors.append(f"cannot load artifact-manifest schemas safely: {exc}")
        return
    declarations = collect_artifact_declarations(files)

    for path in files:
        relative = path.relative_to(ROOT).as_posix()
        size = sizes.get(path)
        if size is None:
            continue
        if size > MAX_PUBLIC_FILE_BYTES:
            errors.append(
                f"public file exceeds the {MAX_PUBLIC_FILE_BYTES}-byte artifact limit: {relative}"
            )
            continue
        try:
            inspection = inspect_public_file(path)
        except OSError as exc:
            errors.append(f"cannot inspect public file {relative}: {exc}")
            continue
        try:
            post_read_size = path.stat().st_size
        except OSError as exc:
            errors.append(f"cannot re-inspect public file {relative}: {exc}")
            continue
        if inspection.byte_size != size or post_read_size != size:
            errors.append(f"public file changed during inspection: {relative}")
            continue
        opaque_reasons: list[str] = []
        if path.suffix.lower() in BINARY_SUFFIXES:
            opaque_reasons.append("known-binary extension")
        if inspection.has_nul:
            opaque_reasons.append("NUL-containing bytes")
        if not inspection.valid_utf8:
            opaque_reasons.append("non-UTF-8 bytes")
        if not opaque_reasons and is_project_infrastructure_file(path, schema_set):
            continue
        manifest_reasons = opaque_reasons or [
            "path is outside the explicit project-infrastructure allowlist"
        ]

        candidates = declarations.get(relative, [])
        if not candidates:
            errors.append(
                "public artifact lacks an exact problem/source/evidence "
                f"manifest: {relative} ({', '.join(manifest_reasons)})"
            )
            continue
        candidate_failures: list[str] = []
        for declaration in candidates:
            issues = artifact_manifest_issues(declaration, inspection, schema_set)
            if not issues:
                candidate_failures = []
                break
            record_relative = declaration.record_path.relative_to(ROOT).as_posix()
            candidate_failures.append(f"{record_relative}: {'; '.join(issues)}")
        if candidate_failures:
            errors.append(
                f"public artifact has no valid manifest: {relative} "
                f"({' | '.join(candidate_failures)})"
            )


def check_phase_a_freeze(errors: list[str]) -> None:
    """Pin the first protected publication to its exact submitted-state graph."""

    calibration_root = ROOT / "examples" / "calibration"
    actual_records = {
        path.relative_to(ROOT).as_posix()
        for path in calibration_root.glob("*.json")
        if path.is_file()
    }
    if actual_records != PHASE_A_RECORD_PATHS:
        missing = sorted(PHASE_A_RECORD_PATHS - actual_records)
        extra = sorted(actual_records - PHASE_A_RECORD_PATHS)
        if missing:
            errors.append(f"Phase A calibration records are missing: {missing}")
        if extra:
            errors.append(f"Phase A contains undeclared calibration records: {extra}")

    artifact_roots = (
        calibration_root / "artifacts",
        ROOT / "work" / "CAL-PACKET-001",
    )
    actual_artifacts = {
        path.relative_to(ROOT).as_posix()
        for root in artifact_roots
        if root.is_dir()
        for path in root.rglob("*")
        if path.is_file()
    }
    if actual_artifacts != PHASE_A_ARTIFACT_PATHS:
        missing = sorted(PHASE_A_ARTIFACT_PATHS - actual_artifacts)
        extra = sorted(actual_artifacts - PHASE_A_ARTIFACT_PATHS)
        if missing:
            errors.append(f"Phase A calibration artifacts are missing: {missing}")
        if extra:
            errors.append(f"Phase A contains undeclared calibration artifacts: {extra}")

    records: dict[str, dict[str, Any]] = {}
    for relative in sorted(PHASE_A_RECORD_PATHS & actual_records):
        try:
            records[Path(relative).name] = validate_packets.load_json(ROOT / relative)
        except (OSError, UnicodeError, ValueError) as exc:
            errors.append(f"cannot read Phase A record {relative}: {exc}")
    if len(records) != len(PHASE_A_RECORD_PATHS):
        return

    for name, (version, status, base_commit) in PHASE_A_PACKET_EXPECTATIONS.items():
        packet = records[name]
        actual = (
            packet.get("record_version"),
            packet.get("status"),
            packet.get("lease", {}).get("base_commit"),
        )
        expected = (version, status, base_commit)
        if actual != expected:
            errors.append(
                f"Phase A packet {name} must be {expected}, found {actual}"
            )

    for name, (sequence, from_status, to_status) in PHASE_A_TRANSITION_EXPECTATIONS.items():
        transition = records[name]
        actual = (
            transition.get("sequence"),
            transition.get("from_status"),
            transition.get("to_status"),
            transition.get("git_commit"),
        )
        expected = (sequence, from_status, to_status, PHASE_A_C0)
        if actual != expected:
            errors.append(
                f"Phase A transition {name} must be {expected}, found {actual}"
            )

    producer = records["producer-run.json"]
    if producer.get("workspace_revision", {}).get("revision") != PHASE_A_C0:
        errors.append("Phase A producer run must bind the protected C0 revision")
    evidence = records["evidence-record.json"]
    if evidence.get("status") != "complete":
        errors.append("Phase A evidence producer status must be complete")
    if evidence.get("reproducibility", {}).get("independently_reproduced") is not False:
        errors.append(
            "Phase A evidence must remain not-yet-independently-reproduced"
        )

    exact_times = {
        "research-packet-01-draft.json": {
            "created_at": "2026-08-07T17:00:00Z",
            "updated_at": "2026-08-07T17:00:00Z",
        },
        "research-packet-02-ready.json": {
            "created_at": "2026-08-07T17:00:00Z",
            "updated_at": "2026-08-07T17:05:00Z",
        },
        "research-packet-03-claimed.json": {
            "created_at": "2026-08-07T17:00:00Z",
            "updated_at": "2026-08-07T17:10:00Z",
        },
        "research-packet-04-in-progress.json": {
            "created_at": "2026-08-07T17:00:00Z",
            "updated_at": "2026-08-07T17:20:00Z",
        },
        "research-packet-05-submitted.json": {
            "created_at": "2026-08-07T17:00:00Z",
            "updated_at": "2026-08-07T17:40:00Z",
        },
        "packet-transition-01-draft-ready.json": {
            "occurred_at": "2026-08-07T17:05:00Z"
        },
        "packet-transition-02-ready-claimed.json": {
            "occurred_at": "2026-08-07T17:10:00Z"
        },
        "packet-transition-03-claimed-in-progress.json": {
            "occurred_at": "2026-08-07T17:20:00Z"
        },
        "packet-transition-04-in-progress-submitted.json": {
            "occurred_at": "2026-08-07T17:40:00Z"
        },
        "producer-run.json": {
            "started_at": "2026-08-07T17:20:00Z",
            "recorded_at": "2026-08-07T17:35:00Z",
        },
        "evidence-record.json": {"created_at": "2026-08-07T17:36:00Z"},
    }
    for name, expected_fields in exact_times.items():
        record = records[name]
        for field, expected in expected_fields.items():
            if record.get(field) != expected:
                errors.append(
                    f"Phase A {name} {field} must be {expected!r}, "
                    f"found {record.get(field)!r}"
                )
            parsed = validate_packets.parse_timestamp(record.get(field))
            if parsed is None or parsed <= PHASE_A_C0_TIME:
                errors.append(f"Phase A {name} {field} must occur after C0")

    for name in (
        "research-packet-03-claimed.json",
        "research-packet-04-in-progress.json",
        "research-packet-05-submitted.json",
    ):
        lease = records[name].get("lease", {})
        if lease.get("claimed_at") != "2026-08-07T17:10:00Z":
            errors.append(f"Phase A {name} has the wrong lease claim time")
        if lease.get("expires_at") != "2026-08-07T19:10:00Z":
            errors.append(f"Phase A {name} has the wrong lease expiry time")


def check_required_file(name: str, errors: list[str]) -> None:
    path = ROOT / name
    if not path.is_file():
        errors.append(f"missing required file: {name}")
    elif path.is_symlink():
        errors.append(f"required file cannot be a symbolic link: {name}")
    else:
        try:
            path.resolve().relative_to(ROOT.resolve())
        except (OSError, ValueError):
            errors.append(f"required file resolves outside repository: {name}")


def portal_requires_translation_readbacks(catalog: dict[str, Any]) -> bool:
    if catalog.get("schema") == "math-commons-portal-catalog/v2":
        return True
    for section in catalog.get("sections", []):
        if not isinstance(section, dict):
            continue
        for key in ("release", "starter"):
            release = section.get(key)
            if isinstance(release, dict) and release.get("tag") in {"translate-v7", "translate-v8", "translate-v9-corrected", "translate-v9-complete"}:
                return True
    return False


def check_required(errors: list[str]) -> None:
    for name in sorted(REQUIRED):
        check_required_file(name, errors)

    portal_path = ROOT / "catalog" / "portals.json"
    if not portal_path.is_file() or portal_path.is_symlink():
        return
    try:
        portal = validate_packets.load_json(portal_path)
    except (OSError, UnicodeError, ValueError) as exc:
        errors.append(f"cannot inspect portal catalog requirements: {exc}")
        return
    if not isinstance(portal, dict):
        errors.append("portal catalog root must be an object")
        return
    if portal_requires_translation_readbacks(portal):
        check_required_file("catalog/translate-rb-v7.json", errors)
        if any(
            isinstance(section, dict)
            and any(
                isinstance(section.get(key), dict)
                and section[key].get("tag") == "translate-v8"
                for key in ("release", "starter")
            )
            for section in portal.get("sections", [])
        ):
            check_required_file("catalog/translate-rb-v8.json", errors)
        if any(
            isinstance(section, dict)
            and any(
                isinstance(section.get(key), dict)
                and section[key].get("tag") == "translate-v9-complete"
                for key in ("release", "starter")
            )
            for section in portal.get("sections", [])
        ):
            check_required_file("catalog/translate-rb-v9-complete.json", errors)
        if any(
            isinstance(section, dict)
            and any(
                isinstance(section.get(key), dict)
                and section[key].get("tag") == "translate-v9-corrected"
                for key in ("release", "starter")
            )
            for section in portal.get("sections", [])
        ):
            check_required_file("catalog/translate-rb-v9.json", errors)
    elif portal.get("schema") == "math-commons-portal-catalog/v1":
        v7_readback = ROOT / "catalog" / "translate-rb-v7.json"
        if v7_readback.exists() or v7_readback.is_symlink():
            errors.append(
                "undeclared v7 readback exists under legacy portal catalog: "
                "catalog/translate-rb-v7.json"
            )


def check_immutable_r1_readback(errors: list[str]) -> None:
    path = ROOT / "catalog" / "readback.json"
    if not path.is_file() or path.is_symlink():
        return
    try:
        inspection = inspect_public_file(path)
    except OSError as exc:
        errors.append(f"cannot inspect immutable R1 readback: {exc}")
        return
    if inspection.byte_size != R1_READBACK_BYTES:
        errors.append(
            "immutable R1 readback byte length changed: "
            f"{inspection.byte_size} != {R1_READBACK_BYTES}"
        )
    if inspection.sha256.upper() != R1_READBACK_SHA256:
        errors.append("immutable R1 readback SHA-256 changed")


def check_ignored_output_not_tracked(errors: list[str]) -> None:
    """Allow local release output while refusing tracked content hidden there."""

    if not (ROOT / ".git").exists():
        return
    try:
        completed = subprocess.run(
            ["git", "ls-files", "-z", "--", "dist"],
            cwd=ROOT,
            check=False,
            capture_output=True,
            timeout=10,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        errors.append(f"could not verify whether ignored dist/ output is tracked: {exc}")
        return
    if completed.returncode != 0:
        errors.append("could not verify whether ignored dist/ output is tracked")
        return
    tracked = [path for path in completed.stdout.split(b"\0") if path]
    if tracked:
        errors.append("tracked files are not allowed beneath ignored dist/ output")


def check_private_patterns(errors: list[str], files: list[Path]) -> None:
    for path in files:
        text = read_public_text(path, errors)
        if text is None:
            continue
        for pattern in PRIVATE_PATTERNS:
            if pattern.search(text):
                errors.append(
                    "private or credential-like text in "
                    f"{path.relative_to(ROOT).as_posix()}"
                )


def check_relative_links(errors: list[str], files: list[Path]) -> None:
    for path in files:
        if path.suffix.lower() != ".md":
            continue
        text = read_public_text(path, errors)
        if text is None:
            continue
        for match in MARKDOWN_LINK.finditer(text):
            target = match.group(1).strip()
            if (
                not target
                or target.startswith(("http://", "https://", "mailto:", "#"))
            ):
                continue
            target = target.split("#", 1)[0]
            if not target:
                continue
            resolved = (path.parent / unquote(target)).resolve()
            try:
                resolved.relative_to(ROOT.resolve())
            except ValueError:
                errors.append(f"relative link escapes repository in {path.relative_to(ROOT)}: {target}")
                continue
            if not resolved.exists():
                errors.append(f"broken relative link in {path.relative_to(ROOT)}: {target}")


def check_policy(errors: list[str]) -> None:
    rights = (ROOT / "RIGHTS.md").read_text(encoding="utf-8")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    alignment = (ROOT / "LEIDEN_ALIGNMENT.md").read_text(encoding="utf-8")
    citation = (ROOT / "CITATION.cff").read_text(encoding="utf-8")
    two_factor = (ROOT / "GITHUB_2FA_CONTINUITY.md").read_text(encoding="utf-8")
    if "CC0 1.0" not in rights or "pre-existing third-party" not in rights:
        errors.append("RIGHTS.md lacks the CC0 modulo third-party-rights rule")
    for heading in ("## Transcription", "## Translation", "## Open problems"):
        if heading not in readme:
            errors.append(f"README.md lacks current section: {heading}")
    if (
        "private by default" not in alignment
        or "does not require publication of prompt histories or raw AI transcripts" not in alignment
        or "data minimization" not in alignment
    ):
        errors.append("LEIDEN_ALIGNMENT.md lacks the privacy-by-default disclosure boundary")
    if "license: CC0-1.0" not in citation:
        errors.append("CITATION.cff does not declare CC0-1.0")
    if "10.5281/zenodo.21830229" not in citation:
        errors.append("CITATION.cff does not contain the v0.1.1 version DOI")
    if "10.5281/zenodo.21828562" not in citation:
        errors.append("CITATION.cff does not contain the all-versions concept DOI")
    if "recovery codes" not in two_factor or "GitHub Apps" not in two_factor:
        errors.append("GitHub 2FA continuity runbook lacks recovery or automation guidance")


def main() -> int:
    errors: list[str] = []
    check_required(errors)
    check_immutable_r1_readback(errors)
    check_ignored_output_not_tracked(errors)
    check_phase_a_freeze(errors)
    if not errors:
        public_files = public_repository_files(errors)
        if not errors:
            check_public_artifact_manifests(errors, public_files)
        if not errors:
            check_private_patterns(errors, public_files)
            check_relative_links(errors, public_files)
        if not errors:
            check_policy(errors)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("PASS: Mathematics Commons repository structural checks")
    return 0


if __name__ == "__main__":
    sys.exit(main())
