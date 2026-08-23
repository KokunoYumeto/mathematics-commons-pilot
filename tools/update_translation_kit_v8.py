#!/usr/bin/env python3
"""Apply the v8 wording pass to the mutable generic translation kit."""

from __future__ import annotations

import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
KIT = ROOT / "kits" / "translate"


REPLACEMENTS = {
    "The listed works are suggestions, not a closed curriculum. You may propose another mathematical work with a verifiable open source and derivative license. If a chosen work already has activity in the requested language, you may choose another language or declare an independently useful parallel edition. Do not overwrite another edition. If the source or derivative rights are incomplete, the valid job is source preflight—not translation.": "The listed works are suggestions, not a closed curriculum. You may propose another mathematical work with a public source and a recorded distribution note. If a chosen work already has activity in the requested language, you may choose another language or declare an independently useful parallel edition. Do not overwrite another edition. Keep attribution, ShareAlike, non-commercial, and component notices exactly as recorded; a missing source is an acquisition task, not a reason to discard the work.",
    "Work only on the current stage and bounded unit. End every response with `STATUS: SOURCE_PREFLIGHT`, `STATUS: IN_PROGRESS`, or `STATUS: COMPLETE`, followed by the exact cursor and returned cumulative package identity. While SOURCE_PREFLIGHT or IN_PROGRESS, the operator replies `continue`. After COMPLETE, the operator replies `next prompt`. SOURCE_PREFLIGHT preserves the full state, names the exact missing authority, right, source byte, dependency, reviewer, or decision, and continues with the next bounded verification action.": "Work only on the current stage and bounded unit. End every response with `STATUS: SOURCE_INTAKE`, `STATUS: IN_PROGRESS`, or `STATUS: COMPLETE`, followed by the exact cursor and returned cumulative package identity. While SOURCE_INTAKE or IN_PROGRESS, the operator replies `continue`. After COMPLETE, the operator replies `next prompt`. SOURCE_INTAKE preserves the full state, names the exact missing source byte, dependency, reviewer, or decision, and continues with the next bounded acquisition or verification action.",
    "Use `STATUS: SOURCE_PREFLIGHT`, `STATUS: IN_PROGRESS`, or `STATUS: COMPLETE`. A source-preflight return preserves all cumulative state, identifies the exact missing source, right, dependency, byte identity, reviewer, or decision, and records the next bounded verification action.": "Use `STATUS: SOURCE_INTAKE`, `STATUS: IN_PROGRESS`, or `STATUS: COMPLETE`. A source-intake return preserves all cumulative state, identifies the exact missing source, distribution note, dependency, byte identity, reviewer, or decision, and records the next bounded acquisition or verification action.",
    "Return `PASS` only when every declared gate passes.": "Return `PASS` only when every declared scope and evidence check passes.",
}


def rewrite(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    for old, new in REPLACEMENTS.items():
        text = text.replace(old, new)
    text = text.replace("source preflight", "source intake")
    text = text.replace("Source preflight", "Source intake")
    text = text.replace("source-preflight", "source-intake")
    text = text.replace("SOURCE_PREFLIGHT", "SOURCE_INTAKE")
    path.write_text(text, encoding="utf-8", newline="\n")


def main() -> int:
    for name in ("README.md", "START.md", "LOCAL.md", "WEB.md", "PROMPT.md", "RETURN.md", "QA.md"):
        rewrite(KIT / name)
    manifest_rows: list[str] = []
    names = sorted(path.name for path in KIT.iterdir() if path.is_file() and path.name != "MANIFEST.sha256")
    for name in names:
        data = (KIT / name).read_bytes()
        manifest_rows.append(f"{hashlib.sha256(data).hexdigest().upper()}\t{len(data)}\t{name}\n")
    (KIT / "MANIFEST.sha256").write_bytes("".join(manifest_rows).encode("utf-8"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
