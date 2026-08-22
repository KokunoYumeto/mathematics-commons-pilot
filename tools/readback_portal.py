#!/usr/bin/env python3
"""Anonymously stream and verify one small portal release."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


REPOSITORY = "KokunoYumeto/mathematics-commons-pilot"
ROOT = Path(__file__).resolve().parents[1]
TAG = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
HEX40 = re.compile(r"^[0-9a-f]{40}$")
CHUNK = 1024 * 1024
MAX_ASSET_BYTES = 512 * 1024 * 1024
RELEASE_CONTRACTS = {
    "openlogic-v1": ("translate-openlogic-v1", "openlogic-rb.json"),
    "translation-starter-v7": ("translate-v7", "translate-rb-v7.json"),
}


def request(url: str) -> urllib.request.Request:
    return urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "mathematics-commons-public-readback",
            "X-GitHub-Api-Version": "2022-11-28",
        },
        method="GET",
    )


def get_json(url: str) -> dict:
    with urllib.request.urlopen(request(url), timeout=60) as response:
        if response.status != 200:
            raise ValueError(f"public API returned HTTP {response.status}: {url}")
        value = json.loads(response.read().decode("utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"public API response is not an object: {url}")
    return value


def load_manifest(path: Path) -> dict:
    raw = path.read_bytes()
    if raw.startswith(b"\xef\xbb\xbf") or b"\r" in raw:
        raise ValueError("asset manifest must be UTF-8 LF-only without BOM")
    value = json.loads(raw.decode("utf-8"))
    if not isinstance(value, dict) or value.get("schema") != "math-commons-job-asset/v1":
        raise ValueError("asset manifest schema differs")
    assets = value.get("assets")
    if not isinstance(assets, list) or not assets:
        raise ValueError("asset manifest has no assets")
    return value


def resolve_tag(repository: str, tag: str) -> tuple[str, str]:
    base = f"https://api.github.com/repos/{repository}"
    ref = get_json(f"{base}/git/ref/tags/{urllib.parse.quote(tag, safe='')}")
    target = ref.get("object")
    if not isinstance(target, dict):
        raise ValueError("tag ref has no target object")
    kind = target.get("type")
    sha = target.get("sha")
    for _ in range(4):
        if kind == "commit" and isinstance(sha, str) and HEX40.fullmatch(sha):
            commit = get_json(f"{base}/git/commits/{sha}")
            tree = commit.get("tree")
            if not isinstance(tree, dict) or not isinstance(tree.get("sha"), str):
                raise ValueError("tag commit has no tree")
            return sha, tree["sha"]
        if kind != "tag" or not isinstance(sha, str) or HEX40.fullmatch(sha) is None:
            break
        tag_object = get_json(f"{base}/git/tags/{sha}")
        target = tag_object.get("object")
        if not isinstance(target, dict):
            break
        kind = target.get("type")
        sha = target.get("sha")
    raise ValueError("tag did not resolve to one commit")


def stream_identity(url: str, expected_bytes: int) -> tuple[int, str]:
    if expected_bytes <= 0 or expected_bytes > MAX_ASSET_BYTES:
        raise ValueError("asset byte boundary is unsafe")
    digest = hashlib.sha256()
    total = 0
    with urllib.request.urlopen(request(url), timeout=120) as response:
        if response.status != 200:
            raise ValueError(f"asset returned HTTP {response.status}")
        while block := response.read(CHUNK):
            total += len(block)
            if total > expected_bytes:
                raise ValueError("asset exceeded its declared byte boundary")
            digest.update(block)
    return total, digest.hexdigest().upper()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tag", required=True)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--repository", default=REPOSITORY)
    args = parser.parse_args()
    if TAG.fullmatch(args.tag) is None or args.repository != REPOSITORY:
        raise ValueError("repository or release tag is outside the approved boundary")
    manifest = load_manifest(args.manifest.resolve())
    job_id = manifest.get("job_id")
    contract = RELEASE_CONTRACTS.get(job_id)
    if contract is None or contract[0] != args.tag:
        raise ValueError("asset manifest job and release tag are outside the approved contract")
    output = args.output.resolve()
    if output != ROOT / "catalog" / contract[1]:
        raise ValueError("readback output path is outside the approved contract")
    if output.exists():
        raise ValueError("readback output already exists; preserve prior evidence explicitly")
    expected = {row["name"]: row for row in manifest["assets"]}
    release = get_json(
        f"https://api.github.com/repos/{args.repository}/releases/tags/"
        + urllib.parse.quote(args.tag, safe="")
    )
    if release.get("tag_name") != args.tag or release.get("draft") or release.get("prerelease"):
        raise ValueError("release identity or publication state differs")
    public_assets = release.get("assets")
    if not isinstance(public_assets, list):
        raise ValueError("release asset list is missing")
    by_name = {row.get("name"): row for row in public_assets if isinstance(row, dict)}
    if set(by_name) != set(expected):
        raise ValueError("release asset set differs from the manifest")
    target_commit, target_tree = resolve_tag(args.repository, args.tag)
    rows: list[dict[str, object]] = []
    for name, expected_row in expected.items():
        public = by_name[name]
        expected_bytes = int(expected_row["zip_bytes"])
        expected_sha = str(expected_row["zip_sha256"])
        if public.get("size") != expected_bytes:
            raise ValueError(f"release metadata byte mismatch: {name}")
        url = public.get("browser_download_url")
        if not isinstance(url, str) or not url.startswith("https://github.com/"):
            raise ValueError(f"release download URL differs: {name}")
        observed_bytes, observed_sha = stream_identity(url, expected_bytes)
        if observed_bytes != expected_bytes or observed_sha != expected_sha:
            raise ValueError(f"public asset byte/hash mismatch: {name}")
        rows.append(
            {
                "id": public.get("id"),
                "name": name,
                "url": url,
                "expected_bytes": expected_bytes,
                "observed_bytes": observed_bytes,
                "expected_sha256": expected_sha,
                "observed_sha256": observed_sha,
                "match": True,
            }
        )
    receipt = {
        "schema": "math-commons-portal-readback/v1",
        "status": "PASS",
        "observed_date": datetime.now(timezone.utc).date().isoformat(),
        "repository": args.repository,
        "release": {
            "id": release.get("id"),
            "tag": args.tag,
            "url": release.get("html_url"),
            "target_commit": target_commit,
            "target_tree": target_tree,
        },
        "transport": {
            "method": "anonymous_https",
            "authorization": False,
            "cookies": False,
            "payload_persisted": False,
        },
        "assets": rows,
        "summary": {
            "assets": len(rows),
            "bytes": sum(int(row["observed_bytes"]) for row in rows),
            "matches": len(rows),
            "mismatches": 0,
            "errors": [],
        },
    }
    data = (json.dumps(receipt, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_suffix(output.suffix + ".tmp")
    temporary.write_bytes(data)
    os.replace(temporary, output)
    print(
        json.dumps(
            {
                "status": "PASS",
                "release_id": receipt["release"]["id"],
                "target_commit": target_commit,
                "target_tree": target_tree,
                "assets": len(rows),
                "bytes": receipt["summary"]["bytes"],
            },
            separators=(",", ":"),
        )
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, UnicodeError, json.JSONDecodeError, urllib.error.URLError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
