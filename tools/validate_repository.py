#!/usr/bin/env python3
"""Fail-closed structural checks for the public concept repository."""

from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import unquote


ROOT = Path(__file__).resolve().parents[1]
REQUIRED = {
    "README.md",
    "STATUS.md",
    "WHITE_PAPER.md",
    "LEIDEN_ALIGNMENT.md",
    "GITHUB_PILOT_GUIDE.md",
    "START_HERE_FOR_HUMANS.md",
    "START_HERE_FOR_AGENTS.md",
    "CONTRIBUTING.md",
    "RIGHTS.md",
    "LICENSE",
    "CITATION.cff",
}

PRIVATE_PATTERNS = (
    re.compile(r"C:\\Users\\", re.IGNORECASE),
    re.compile(r"/Users/[^/]+/"),
    re.compile(r"github_pat_[A-Za-z0-9_]+"),
    re.compile(r"(?i)zenodo[_-]?token\s*[:=]\s*[^\s]+"),
)

MARKDOWN_LINK = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")


def markdown_files() -> list[Path]:
    return sorted(
        path
        for path in ROOT.rglob("*.md")
        if ".git" not in path.parts
    )


def check_required(errors: list[str]) -> None:
    for name in sorted(REQUIRED):
        if not (ROOT / name).is_file():
            errors.append(f"missing required file: {name}")


def check_private_patterns(errors: list[str]) -> None:
    for path in markdown_files() + [ROOT / "CITATION.cff"]:
        text = path.read_text(encoding="utf-8")
        for pattern in PRIVATE_PATTERNS:
            if pattern.search(text):
                errors.append(f"private or credential-like text in {path.relative_to(ROOT)}")


def check_relative_links(errors: list[str]) -> None:
    for path in markdown_files():
        text = path.read_text(encoding="utf-8")
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
    citation = (ROOT / "CITATION.cff").read_text(encoding="utf-8")
    if "CC0 1.0" not in rights or "pre-existing third-party" not in rights:
        errors.append("RIGHTS.md lacks the CC0 modulo third-party-rights rule")
    if "self-assessed" not in readme:
        errors.append("README.md lacks the self-assessed Leiden-alignment qualification")
    if "license: CC0-1.0" not in citation:
        errors.append("CITATION.cff does not declare CC0-1.0")


def main() -> int:
    errors: list[str] = []
    check_required(errors)
    if not errors:
        check_private_patterns(errors)
        check_relative_links(errors)
        check_policy(errors)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("PASS: public concept repository structural checks")
    return 0


if __name__ == "__main__":
    sys.exit(main())

