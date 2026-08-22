#!/usr/bin/env python3
"""Create an anonymous, non-persisting readback receipt for a jobs release.

Release assets are expected from the exact identities declared by the jobs
catalog and observed through the public GitHub release.  Commit-pinned raw
files are read twice through independent public GitHub surfaces: the Contents
API supplies the expected identity and raw.githubusercontent.com supplies the
observed identity.  Large response bodies are hashed incrementally and are
never stored on disk.
"""

from __future__ import annotations

import argparse
from datetime import date
import hashlib
import json
import os
import re
import ssl
import sys
import tempfile
from pathlib import Path, PurePosixPath
from typing import Any, BinaryIO, NoReturn
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlsplit
from urllib.request import (
    HTTPRedirectHandler,
    HTTPSHandler,
    ProxyHandler,
    Request,
    build_opener,
)


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schemas" / "release-readback.schema.json"
COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")
SHA256_RE = re.compile(r"^[0-9A-F]{64}$")
REPOSITORY_RE = re.compile(
    r"^[A-Za-z0-9](?:[A-Za-z0-9-]{0,38})/"
    r"[A-Za-z0-9._-]{1,100}$"
)
TAG_RE = re.compile(r"^jobs-[0-9]{4}-[0-9]{2}-[0-9]{2}-r[0-9]+$")
ASSET_NAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
JSON_LIMIT = 32 * 1024 * 1024
CHUNK_SIZE = 4 * 1024 * 1024
TIMEOUT_SECONDS = 120
USER_AGENT = "mathematics-commons-release-readback/1"


class ReadbackError(RuntimeError):
    """A concise fail-closed readback error."""


def fail(message: str) -> NoReturn:
    raise ReadbackError(message)


def reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ReadbackError(f"duplicate JSON key: {key!r}")
        result[key] = value
    return result


def load_json_bytes(data: bytes, label: str) -> Any:
    try:
        return json.loads(
            data.decode("utf-8", errors="strict"),
            object_pairs_hook=reject_duplicate_keys,
        )
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ReadbackError(f"{label} is not strict UTF-8 JSON: {exc}") from exc


def load_json_file(path: Path, label: str) -> Any:
    try:
        data = path.read_bytes()
    except OSError as exc:
        raise ReadbackError(f"cannot read {label}: {exc}") from exc
    return load_json_bytes(data, label)


def is_allowed_github_host(hostname: str | None) -> bool:
    if hostname is None:
        return False
    host = hostname.lower().rstrip(".")
    return host in {"api.github.com", "github.com", "raw.githubusercontent.com"} or host.endswith(
        ".githubusercontent.com"
    )


def require_public_https(url: str, label: str) -> None:
    parsed = urlsplit(url)
    if (
        parsed.scheme != "https"
        or not is_allowed_github_host(parsed.hostname)
        or parsed.username is not None
        or parsed.password is not None
    ):
        fail(f"{label} is not an allowed anonymous GitHub HTTPS URL")


class HttpsOnlyRedirectHandler(HTTPRedirectHandler):
    """Reject redirects away from anonymous HTTPS GitHub infrastructure."""

    def redirect_request(  # type: ignore[override]
        self,
        request: Request,
        file_pointer: BinaryIO,
        code: int,
        message: str,
        headers: Any,
        new_url: str,
    ) -> Request | None:
        require_public_https(new_url, "redirect target")
        redirected = super().redirect_request(
            request, file_pointer, code, message, headers, new_url
        )
        if redirected is not None:
            for forbidden in ("Authorization", "Cookie", "Proxy-Authorization"):
                redirected.remove_header(forbidden)
                redirected.unredirected_hdrs.pop(forbidden, None)
                redirected.unredirected_hdrs.pop(forbidden.lower(), None)
        return redirected


# An explicit empty proxy map prevents environment-provided proxy credentials
# from adding authorization to a readback represented as anonymous.
OPENER = build_opener(
    ProxyHandler({}),
    HTTPSHandler(context=ssl.create_default_context()),
    HttpsOnlyRedirectHandler(),
)


def request(url: str, *, accept: str) -> Request:
    require_public_https(url, "request URL")
    headers = {
        "Accept": accept,
        "Accept-Encoding": "identity",
        "User-Agent": USER_AGENT,
    }
    if urlsplit(url).hostname == "api.github.com":
        headers["X-GitHub-Api-Version"] = "2022-11-28"
    result = Request(url, headers=headers, method="GET")
    for forbidden in ("Authorization", "Cookie", "Proxy-Authorization"):
        if result.has_header(forbidden):
            fail(f"internal error: anonymous request contains {forbidden}")
    return result


def open_response(url: str, *, accept: str, label: str) -> Any:
    try:
        response = OPENER.open(
            request(url, accept=accept), timeout=TIMEOUT_SECONDS
        )
    except HTTPError as exc:
        raise ReadbackError(f"{label}: HTTP {exc.code}") from exc
    except (URLError, TimeoutError, OSError) as exc:
        raise ReadbackError(f"{label}: HTTPS request failed: {exc}") from exc
    try:
        status = response.getcode()
        require_public_https(response.geturl(), f"{label} final URL")
        if status != 200:
            fail(f"{label}: unexpected HTTP status {status}")
        encoding = response.headers.get("Content-Encoding", "identity").lower()
        if encoding not in {"", "identity"}:
            fail(f"{label}: unexpected content encoding {encoding!r}")
        return response
    except Exception:
        response.close()
        raise


def fetch_json(url: str, label: str) -> Any:
    response = open_response(
        url, accept="application/vnd.github+json", label=label
    )
    try:
        declared = response.headers.get("Content-Length")
        if declared is not None:
            try:
                declared_size = int(declared)
            except ValueError as exc:
                raise ReadbackError(f"{label}: invalid Content-Length") from exc
            if declared_size > JSON_LIMIT:
                fail(f"{label}: JSON response exceeds the safety limit")
        data = response.read(JSON_LIMIT + 1)
    finally:
        response.close()
    if len(data) > JSON_LIMIT:
        fail(f"{label}: JSON response exceeds the safety limit")
    return load_json_bytes(data, label)


def stream_identity(url: str, *, accept: str, label: str) -> tuple[int, str]:
    response = open_response(url, accept=accept, label=label)
    digest = hashlib.sha256()
    size = 0
    try:
        while True:
            block = response.read(CHUNK_SIZE)
            if not block:
                break
            size += len(block)
            digest.update(block)
        declared = response.headers.get("Content-Length")
        if declared is not None:
            try:
                declared_size = int(declared)
            except ValueError as exc:
                raise ReadbackError(f"{label}: invalid Content-Length") from exc
            if declared_size != size:
                fail(
                    f"{label}: Content-Length {declared_size} differs from "
                    f"the streamed {size} bytes"
                )
    except (URLError, TimeoutError, OSError) as exc:
        raise ReadbackError(f"{label}: stream failed: {exc}") from exc
    finally:
        response.close()
    return size, digest.hexdigest().upper()


def api_base(repository: str) -> str:
    owner, name = repository.split("/", 1)
    return f"https://api.github.com/repos/{quote(owner, safe='')}/{quote(name, safe='')}"


def validate_commit(value: str, label: str) -> str:
    if COMMIT_RE.fullmatch(value) is None:
        fail(f"{label} must be one lowercase 40-character Git commit ID")
    return value


def validate_git_object(value: Any, label: str) -> tuple[str, str]:
    if not isinstance(value, dict):
        fail(f"{label}: malformed Git object")
    object_type = value.get("type")
    sha = value.get("sha")
    if object_type not in {"commit", "tag"} or not isinstance(sha, str):
        fail(f"{label}: malformed Git object identity")
    validate_commit(sha, f"{label} SHA")
    return object_type, sha


def dereference_git_object(
    repository: str, value: Any, label: str
) -> str:
    object_type, sha = validate_git_object(value, label)
    seen: set[str] = set()
    for depth in range(9):
        if object_type == "commit":
            return sha
        if sha in seen:
            fail(f"{label}: annotated-tag cycle")
        seen.add(sha)
        if depth == 8:
            fail(f"{label}: annotated-tag chain is too deep")
        document = fetch_json(
            f"{api_base(repository)}/git/tags/{sha}",
            f"{label} annotated tag {sha}",
        )
        if not isinstance(document, dict):
            fail(f"{label}: malformed annotated-tag response")
        object_type, sha = validate_git_object(
            document.get("object"), f"{label} annotated tag {sha}"
        )
    fail(f"{label}: annotated-tag chain did not resolve")


def resolve_ref(repository: str, ref_path: str, label: str) -> str:
    document = fetch_json(
        f"{api_base(repository)}/git/ref/{ref_path}", label
    )
    if not isinstance(document, dict):
        fail(f"{label}: malformed ref response")
    return dereference_git_object(repository, document.get("object"), label)


def canonical_release_url(repository: str, tag: str) -> str:
    return f"https://github.com/{repository}/releases/tag/{tag}"


def canonical_asset_url(repository: str, tag: str, name: str) -> str:
    return (
        f"https://github.com/{repository}/releases/download/"
        f"{quote(tag, safe='')}/{quote(name, safe='')}"
    )


def positive_integer(value: Any, label: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < 1:
        fail(f"{label} must be a positive integer")
    return value


def collect_catalog_assets(
    catalog: Any, repository: str, tag: str
) -> list[dict[str, Any]]:
    if not isinstance(catalog, dict):
        fail("catalog root is not an object")
    if catalog.get("repository") != f"https://github.com/{repository}":
        fail("catalog repository differs from --repository")
    release = catalog.get("release")
    if not isinstance(release, dict):
        fail("catalog release is not an object")
    if release.get("tag") != tag:
        fail("catalog release tag differs from --tag")
    if release.get("url") != canonical_release_url(repository, tag):
        fail("catalog release URL is not canonical")

    sources: list[Any] = []
    jobs = catalog.get("jobs")
    if not isinstance(jobs, list):
        fail("catalog jobs is not an array")
    for index, job in enumerate(jobs):
        if not isinstance(job, dict) or not isinstance(job.get("assets"), list):
            fail(f"catalog job {index} has no asset array")
        sources.append(job["assets"])
    kit = catalog.get("translation_kit")
    if not isinstance(kit, dict) or not isinstance(kit.get("assets"), list):
        fail("catalog translation_kit has no asset array")
    sources.append(kit["assets"])

    result: list[dict[str, Any]] = []
    seen: set[str] = set()
    for source in sources:
        for asset in source:
            if not isinstance(asset, dict):
                fail("catalog contains a malformed asset row")
            name = asset.get("name")
            size = asset.get("zip_bytes")
            digest = asset.get("zip_sha256")
            url = asset.get("url")
            if not isinstance(name, str) or ASSET_NAME_RE.fullmatch(name) is None:
                fail("catalog contains an unsafe asset name")
            if name in seen:
                fail(f"catalog contains duplicate asset name {name!r}")
            seen.add(name)
            size = positive_integer(size, f"catalog asset {name} zip_bytes")
            if not isinstance(digest, str) or SHA256_RE.fullmatch(digest) is None:
                fail(f"catalog asset {name} has an invalid SHA-256")
            expected_url = canonical_asset_url(repository, tag, name)
            if url != expected_url:
                fail(f"catalog asset {name} URL is not canonical")
            result.append(
                {
                    "name": name,
                    "url": expected_url,
                    "bytes": size,
                    "sha256": digest,
                }
            )
    if not result:
        fail("catalog declares no release assets")
    return result


def fetch_release_assets(repository: str, release_id: int) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for page in range(1, 101):
        document = fetch_json(
            f"{api_base(repository)}/releases/{release_id}/assets"
            f"?per_page=100&page={page}",
            f"release-assets page {page}",
        )
        if not isinstance(document, list):
            fail(f"release-assets page {page} is not an array")
        for row in document:
            if not isinstance(row, dict):
                fail(f"release-assets page {page} contains a malformed row")
            result.append(row)
        if len(document) < 100:
            return result
    fail("release-assets pagination exceeded 100 pages")


def validate_raw_paths(paths: list[str]) -> list[str]:
    if not paths:
        fail("at least one --raw-file is required by the receipt schema")
    result: list[str] = []
    seen: set[str] = set()
    for path in paths:
        if (
            not path
            or path.startswith("/")
            or path.endswith("/")
            or "\\" in path
            or any(ord(character) < 32 or ord(character) == 127 for character in path)
        ):
            fail(f"unsafe raw-file path: {path!r}")
        pure = PurePosixPath(path)
        if pure.as_posix() != path or any(part in {"", ".", ".."} for part in pure.parts):
            fail(f"non-canonical raw-file path: {path!r}")
        if path in seen:
            fail(f"duplicate raw-file path: {path!r}")
        seen.add(path)
        result.append(path)
    return result


def raw_urls(repository: str, commit: str, path: str) -> tuple[str, str]:
    owner, name = repository.split("/", 1)
    encoded_path = "/".join(quote(part, safe="") for part in path.split("/"))
    contents_url = (
        f"{api_base(repository)}/contents/{encoded_path}?ref={commit}"
    )
    raw_url = (
        "https://raw.githubusercontent.com/"
        f"{quote(owner, safe='')}/{quote(name, safe='')}/{commit}/{encoded_path}"
    )
    return contents_url, raw_url


def release_metadata(
    repository: str, tag: str, commit: str
) -> tuple[dict[str, Any], list[dict[str, Any]], str]:
    encoded_tag = quote(tag, safe="")
    release = fetch_json(
        f"{api_base(repository)}/releases/tags/{encoded_tag}",
        "release metadata",
    )
    if not isinstance(release, dict):
        fail("release metadata is not an object")
    if release.get("tag_name") != tag:
        fail("release metadata tag differs from --tag")
    if release.get("draft") is not False:
        fail("release is not publicly published")
    release_id = positive_integer(release.get("id"), "release id")
    expected_release_url = canonical_release_url(repository, tag)
    if release.get("html_url") != expected_release_url:
        fail("release metadata URL is not canonical")

    tag_commit = resolve_ref(
        repository, f"tags/{encoded_tag}", "release tag ref"
    )
    if tag_commit != commit:
        fail(
            f"release tag resolves to {tag_commit}, not the requested commit {commit}"
        )
    main_commit = resolve_ref(repository, "heads/main", "main ref")
    return release, fetch_release_assets(repository, release_id), main_commit


def compare_release_asset_set(
    declared: list[dict[str, Any]],
    observed: list[dict[str, Any]],
    repository: str,
    tag: str,
) -> list[str]:
    errors: list[str] = []
    by_name: dict[str, dict[str, Any]] = {}
    duplicates: set[str] = set()
    for row in observed:
        name = row.get("name")
        if not isinstance(name, str):
            errors.append("release metadata contains an asset without a string name")
            continue
        if name in by_name:
            duplicates.add(name)
        by_name[name] = row
    for name in sorted(duplicates, key=lambda value: value.encode("utf-8")):
        errors.append(f"release metadata contains duplicate asset {name}")

    expected_names = {str(row["name"]) for row in declared}
    observed_names = set(by_name)
    for name in sorted(expected_names - observed_names, key=lambda value: value.encode("utf-8")):
        errors.append(f"release is missing declared asset {name}")
    for name in sorted(observed_names - expected_names, key=lambda value: value.encode("utf-8")):
        errors.append(f"release contains undeclared asset {name}")

    for expected in declared:
        name = str(expected["name"])
        actual = by_name.get(name)
        if actual is None:
            continue
        if actual.get("state") != "uploaded":
            errors.append(f"release asset {name} is not in uploaded state")
        if actual.get("size") != expected["bytes"]:
            errors.append(f"release metadata size differs for {name}")
        canonical = canonical_asset_url(repository, tag, name)
        if actual.get("browser_download_url") != canonical:
            errors.append(f"release metadata download URL differs for {name}")
    return errors


def readback_assets(
    declared: list[dict[str, Any]], errors: list[str]
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for expected in declared:
        name = str(expected["name"])
        try:
            observed_bytes, observed_sha256 = stream_identity(
                str(expected["url"]),
                accept="application/octet-stream",
                label=f"release asset {name}",
            )
        except ReadbackError as exc:
            errors.append(str(exc))
            continue
        match = (
            observed_bytes == expected["bytes"]
            and observed_sha256 == expected["sha256"]
        )
        if not match:
            errors.append(f"release asset identity mismatch for {name}")
        rows.append(
            {
                "name": name,
                "url": expected["url"],
                "expected_bytes": expected["bytes"],
                "observed_bytes": observed_bytes,
                "expected_sha256": expected["sha256"],
                "observed_sha256": observed_sha256,
                "match": match,
            }
        )
    return rows


def readback_raw_files(
    repository: str, commit: str, paths: list[str], errors: list[str]
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in paths:
        contents_url, raw_url = raw_urls(repository, commit, path)
        try:
            expected_bytes, expected_sha256 = stream_identity(
                contents_url,
                accept="application/vnd.github.raw+json",
                label=f"commit Contents API file {path}",
            )
            observed_bytes, observed_sha256 = stream_identity(
                raw_url,
                accept="application/octet-stream",
                label=f"commit raw file {path}",
            )
        except ReadbackError as exc:
            errors.append(str(exc))
            continue
        match = (
            observed_bytes == expected_bytes
            and observed_sha256 == expected_sha256
        )
        if not match:
            errors.append(f"commit-pinned raw-file identity mismatch for {path}")
        rows.append(
            {
                "path": path,
                "name": PurePosixPath(path).name,
                "url": raw_url,
                "expected_bytes": expected_bytes,
                "observed_bytes": observed_bytes,
                "expected_sha256": expected_sha256,
                "observed_sha256": observed_sha256,
                "match": match,
            }
        )
    return rows


def validate_readback_row(row: Any, *, raw: bool) -> None:
    expected_keys = {
        "name",
        "url",
        "expected_bytes",
        "observed_bytes",
        "expected_sha256",
        "observed_sha256",
        "match",
    }
    if raw:
        expected_keys.add("path")
    if not isinstance(row, dict) or set(row) != expected_keys:
        fail("generated receipt row does not match the readback schema")
    if not isinstance(row["name"], str) or not row["name"]:
        fail("generated receipt has an invalid row name")
    require_public_https(row["url"], "generated receipt row URL")
    positive_integer(row["expected_bytes"], "generated expected_bytes")
    positive_integer(row["observed_bytes"], "generated observed_bytes")
    if (
        not isinstance(row["expected_sha256"], str)
        or SHA256_RE.fullmatch(row["expected_sha256"]) is None
        or not isinstance(row["observed_sha256"], str)
        or SHA256_RE.fullmatch(row["observed_sha256"]) is None
        or not isinstance(row["match"], bool)
    ):
        fail("generated receipt has an invalid digest or match value")
    if raw:
        validate_raw_paths([row["path"]])


def validate_receipt_contract(
    receipt: dict[str, Any], schema: dict[str, Any]
) -> None:
    expected_top = {
        "schema",
        "status",
        "observed_date",
        "subject",
        "transport",
        "assets",
        "aggregate",
        "raw_files",
        "raw_aggregate",
        "errors",
    }
    if set(receipt) != expected_top:
        fail("generated receipt top-level fields differ from the schema")
    schema_const = schema.get("properties", {}).get("schema", {}).get("const")
    repository_const = (
        schema.get("properties", {})
        .get("subject", {})
        .get("properties", {})
        .get("repository", {})
        .get("const")
    )
    if receipt["schema"] != schema_const:
        fail("generated receipt schema differs from the schema contract")
    observed_date = receipt.get("observed_date")
    try:
        parsed_date = date.fromisoformat(observed_date)
    except (TypeError, ValueError):
        fail("generated receipt observed_date is not an ISO calendar date")
    if parsed_date.isoformat() != observed_date:
        fail("generated receipt observed_date is not canonical")
    status = receipt.get("status")
    errors = receipt.get("errors")
    if (
        status not in {"PASS", "FAIL"}
        or not isinstance(errors, list)
        or any(not isinstance(item, str) or not item for item in errors)
        or (status == "PASS" and errors)
        or (status == "FAIL" and not errors)
    ):
        fail("generated receipt status/error relation differs from the schema")
    subject = receipt.get("subject")
    if not isinstance(subject, dict) or set(subject) != {
        "repository",
        "commit",
        "main_commit_at_readback",
        "tag",
        "tag_commit",
        "release_id",
        "release_url",
    }:
        fail("generated receipt subject differs from the schema")
    if subject["repository"] != repository_const:
        fail("generated receipt repository differs from the schema")
    validate_commit(subject["commit"], "generated subject commit")
    validate_commit(subject["main_commit_at_readback"], "generated main commit")
    validate_commit(subject["tag_commit"], "generated tag commit")
    if not isinstance(subject["tag"], str) or TAG_RE.fullmatch(subject["tag"]) is None:
        fail("generated receipt tag differs from the schema")
    positive_integer(subject["release_id"], "generated release id")
    if subject["release_url"] != canonical_release_url(
        subject["repository"], subject["tag"]
    ):
        fail("generated receipt release URL differs from the schema")
    if receipt.get("transport") != {
        "method": "anonymous_https",
        "authorization": "none",
        "cookies": "none",
        "persistence": "none",
    }:
        fail("generated receipt transport differs from the schema")
    assets = receipt.get("assets")
    raw_files = receipt.get("raw_files")
    if not isinstance(assets, list) or not assets:
        fail("generated receipt requires at least one asset row")
    if not isinstance(raw_files, list) or not raw_files:
        fail("generated receipt requires at least one raw-file row")
    for row in assets:
        validate_readback_row(row, raw=False)
    for row in raw_files:
        validate_readback_row(row, raw=True)

    aggregate = receipt.get("aggregate")
    raw_aggregate = receipt.get("raw_aggregate")
    if not isinstance(aggregate, dict) or set(aggregate) != {
        "expected_assets",
        "observed_assets",
        "matched_assets",
        "expected_bytes",
        "observed_bytes",
        "mismatches",
    }:
        fail("generated receipt asset aggregate differs from the schema")
    if not isinstance(raw_aggregate, dict) or set(raw_aggregate) != {
        "expected_files",
        "observed_files",
        "matched_files",
        "mismatches",
    }:
        fail("generated receipt raw aggregate differs from the schema")
    for label, values in (("asset aggregate", aggregate), ("raw aggregate", raw_aggregate)):
        for key, value in values.items():
            if not isinstance(value, int) or isinstance(value, bool) or value < 0:
                fail(f"generated {label} field {key} is not a nonnegative integer")


def write_receipt(path: Path, receipt: dict[str, Any]) -> None:
    data = (
        json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=False) + "\n"
    ).encode("utf-8")
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_name: str | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="wb", prefix=f".{path.name}.", suffix=".tmp", dir=path.parent, delete=False
        ) as handle:
            temporary_name = handle.name
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_name, path)
        temporary_name = None
    finally:
        if temporary_name is not None:
            try:
                Path(temporary_name).unlink()
            except FileNotFoundError:
                pass


def build_receipt(args: argparse.Namespace) -> tuple[dict[str, Any], bool]:
    schema = load_json_file(SCHEMA_PATH, "release-readback schema")
    if not isinstance(schema, dict):
        fail("release-readback schema root is not an object")
    repository_const = (
        schema.get("properties", {})
        .get("subject", {})
        .get("properties", {})
        .get("repository", {})
        .get("const")
    )
    observed_date = date.today().isoformat()
    if args.repository != repository_const:
        fail(
            f"--repository must be {repository_const!r} for the current receipt schema"
        )
    if REPOSITORY_RE.fullmatch(args.repository) is None:
        fail("--repository must be one owner/name token")
    if TAG_RE.fullmatch(args.tag) is None:
        fail("--tag does not match the jobs-release tag contract")
    commit = validate_commit(args.commit, "--commit")
    raw_paths = validate_raw_paths(args.raw_file)

    catalog_path = args.catalog
    if not catalog_path.is_absolute():
        catalog_path = ROOT / catalog_path
    catalog_path = catalog_path.resolve()
    catalog = load_json_file(catalog_path, "jobs catalog")
    declared_assets = collect_catalog_assets(catalog, args.repository, args.tag)

    release, observed_assets, main_commit = release_metadata(
        args.repository, args.tag, commit
    )
    release_id = positive_integer(release.get("id"), "release id")
    errors = compare_release_asset_set(
        declared_assets, observed_assets, args.repository, args.tag
    )
    asset_rows = readback_assets(declared_assets, errors)
    raw_rows = readback_raw_files(args.repository, commit, raw_paths, errors)

    asset_matches = sum(1 for row in asset_rows if row["match"])
    raw_matches = sum(1 for row in raw_rows if row["match"])
    status = "PASS" if not errors else "FAIL"
    receipt = {
        "schema": "math-commons-release-readback/v1",
        "status": status,
        "observed_date": observed_date,
        "subject": {
            "repository": args.repository,
            "commit": commit,
            "main_commit_at_readback": main_commit,
            "tag": args.tag,
            "tag_commit": commit,
            "release_id": release_id,
            "release_url": canonical_release_url(args.repository, args.tag),
        },
        "transport": {
            "method": "anonymous_https",
            "authorization": "none",
            "cookies": "none",
            "persistence": "none",
        },
        "assets": asset_rows,
        "aggregate": {
            "expected_assets": len(declared_assets),
            "observed_assets": len(asset_rows),
            "matched_assets": asset_matches,
            "expected_bytes": sum(int(row["bytes"]) for row in declared_assets),
            "observed_bytes": sum(int(row["observed_bytes"]) for row in asset_rows),
            "mismatches": len(declared_assets) - asset_matches,
        },
        "raw_files": raw_rows,
        "raw_aggregate": {
            "expected_files": len(raw_paths),
            "observed_files": len(raw_rows),
            "matched_files": raw_matches,
            "mismatches": len(raw_paths) - raw_matches,
        },
        "errors": errors,
    }
    validate_receipt_contract(receipt, schema)
    return receipt, status == "PASS"


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Stream and verify a public jobs release and write its anonymous "
            "readback receipt without persisting payloads."
        )
    )
    parser.add_argument("--repository", required=True, help="GitHub owner/name")
    parser.add_argument("--tag", required=True, help="immutable jobs release tag")
    parser.add_argument("--commit", required=True, help="exact lowercase tag commit")
    parser.add_argument("--catalog", required=True, type=Path, help="jobs catalog JSON")
    parser.add_argument("--output", required=True, type=Path, help="receipt JSON path")
    parser.add_argument(
        "--raw-file",
        action="append",
        default=[],
        help="commit-relative raw path; repeat for each public file to read back",
    )
    return parser.parse_args(argv)


def required_output_path(tag: str) -> Path:
    """Return the tag-derived receipt path without exposing R1 to overwrite."""

    if TAG_RE.fullmatch(tag) is None:
        fail("--tag is not a canonical jobs release tag")
    generation = int(tag.rsplit("-r", 1)[1])
    return (ROOT / "catalog" / f"readback-r{generation}.json").resolve()


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    output = args.output
    if not output.is_absolute():
        output = ROOT / output
    output = output.resolve()
    args.output = output
    try:
        expected_output = required_output_path(args.tag)
        if output == (ROOT / "catalog" / "readback.json").resolve():
            fail("catalog/readback.json is the immutable R1 receipt")
        if output != expected_output:
            fail(
                "--output must match the release generation: "
                f"{expected_output.relative_to(ROOT).as_posix()}"
            )
        receipt, passed = build_receipt(args)
        write_receipt(output, receipt)
    except ReadbackError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    except OSError as exc:
        print(f"ERROR: filesystem operation failed: {exc}", file=sys.stderr)
        return 2
    if not passed:
        print(f"FAIL: public readback mismatches recorded in {output}", file=sys.stderr)
        return 1
    print(f"PASS: anonymous public readback recorded in {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
