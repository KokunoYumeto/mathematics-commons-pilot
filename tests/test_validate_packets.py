#!/usr/bin/env python3
"""Regression tests for the dependency-free pilot record validator."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_PATH = ROOT / "tools" / "validate_packets.py"
SPEC = importlib.util.spec_from_file_location("validate_packets", VALIDATOR_PATH)
if SPEC is None or SPEC.loader is None:  # pragma: no cover - import bootstrap guard
    raise RuntimeError(f"cannot import {VALIDATOR_PATH}")
validate_packets = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = validate_packets
SPEC.loader.exec_module(validate_packets)


class PilotRecordValidationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.schema_set = validate_packets.load_schema_set(ROOT / "schemas")

    def test_every_published_example_is_valid(self) -> None:
        paths = sorted((ROOT / "examples").rglob("*.json"))
        self.assertTrue(paths, "expected at least one published example record")
        failures: list[str] = []
        for path in paths:
            failures.extend(validate_packets.validate_record_file(path, self.schema_set))
        if not failures:
            failures.extend(validate_packets.validate_collection(paths, self.schema_set))
        self.assertEqual([], failures, "\n".join(failures))

    def test_calibration_artifact_metadata_matches_exact_bytes(self) -> None:
        source = json.loads(
            (ROOT / "examples/calibration/source-record.json").read_text(
                encoding="utf-8"
            )
        )
        evidence = json.loads(
            (ROOT / "examples/calibration/evidence-record.json").read_text(
                encoding="utf-8"
            )
        )
        declarations = [
            (
                source["locator"]["canonical_reference"],
                source["integrity"]["byte_size"],
                source["integrity"]["hashes"],
            ),
            (
                evidence["artifact_path"],
                evidence["byte_size"],
                evidence["hashes"],
            ),
        ]
        for relative_path, declared_size, hashes in declarations:
            artifact = ROOT / relative_path
            payload = artifact.read_bytes()
            declared_digest = next(
                item["digest"] for item in hashes if item["algorithm"] == "sha256"
            )
            self.assertEqual(declared_size, len(payload), relative_path)
            self.assertEqual(
                declared_digest,
                hashlib.sha256(payload).hexdigest(),
                relative_path,
            )

    def test_example_records_do_not_declare_their_own_hash(self) -> None:
        def declared_digests(value: object) -> list[str]:
            if isinstance(value, dict):
                found = []
                if value.get("algorithm") == "sha256" and isinstance(
                    value.get("digest"), str
                ):
                    found.append(value["digest"])
                for child in value.values():
                    found.extend(declared_digests(child))
                return found
            if isinstance(value, list):
                found = []
                for child in value:
                    found.extend(declared_digests(child))
                return found
            return []

        for path in sorted((ROOT / "examples").rglob("*.json")):
            payload = path.read_bytes()
            record = json.loads(payload.decode("utf-8"))
            self.assertNotIn(
                hashlib.sha256(payload).hexdigest(),
                declared_digests(record),
                f"self-referential hash in {path}",
            )

    def test_invalid_fixtures_fail_for_the_recorded_reason(self) -> None:
        fixture_dir = ROOT / "tests" / "fixtures" / "invalid"
        paths = sorted(fixture_dir.glob("*.json"))
        self.assertTrue(paths, "expected deliberately invalid regression fixtures")
        for path in paths:
            expected_path = path.with_suffix(".error.txt")
            self.assertTrue(expected_path.is_file(), f"missing {expected_path.name}")
            expected = expected_path.read_text(encoding="utf-8").strip()
            errors = validate_packets.validate_record_file(path, self.schema_set)
            self.assertTrue(errors, f"{path.name} unexpectedly passed")
            rendered = "\n".join(errors)
            self.assertIn(expected, rendered, f"wrong failure for {path.name}:\n{rendered}")

    def test_invalid_collections_fail_for_the_recorded_reason(self) -> None:
        fixture_root = ROOT / "tests" / "fixtures" / "invalid_collections"
        case_dirs = sorted(path for path in fixture_root.iterdir() if path.is_dir())
        self.assertTrue(case_dirs, "expected deliberately invalid collection fixtures")
        base_paths = sorted((ROOT / "examples").rglob("*.json"))

        for case_dir in case_dirs:
            expected_path = case_dir / "expected-error.txt"
            self.assertTrue(expected_path.is_file(), f"missing {expected_path}")
            expected = expected_path.read_text(encoding="utf-8").strip()

            omit_path = case_dir / "omit-base.txt"
            omitted = (
                {
                    line.strip()
                    for line in omit_path.read_text(encoding="utf-8").splitlines()
                    if line.strip()
                }
                if omit_path.is_file()
                else set()
            )
            selected_base = [
                path
                for path in base_paths
                if path.relative_to(ROOT).as_posix() not in omitted
            ]
            fixture_paths = sorted(case_dir.glob("*.json"))
            self.assertTrue(fixture_paths, f"missing JSON fixture in {case_dir}")
            paths = selected_base + fixture_paths

            schema_errors: list[str] = []
            for path in paths:
                schema_errors.extend(
                    validate_packets.validate_record_file(path, self.schema_set)
                )
            self.assertEqual(
                [],
                schema_errors,
                f"{case_dir.name} must be schema-valid before semantic validation:\n"
                + "\n".join(schema_errors),
            )

            errors = validate_packets.validate_collection(paths, self.schema_set)
            self.assertTrue(errors, f"{case_dir.name} unexpectedly passed")
            rendered = "\n".join(errors)
            self.assertIn(
                expected,
                rendered,
                f"wrong semantic failure for {case_dir.name}:\n{rendered}",
            )

    def test_duplicate_json_keys_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "duplicate.json"
            path.write_text(
                '{"record_type":"run_record","record_type":"review_record"}',
                encoding="utf-8",
            )
            errors = validate_packets.validate_record_file(path, self.schema_set)
        self.assertTrue(any("duplicate key" in error for error in errors), errors)

    def test_unknown_record_type_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "unknown.json"
            path.write_text(
                json.dumps(
                    {"record_type": "wishful_consensus", "schema_version": "0.1.0"}
                ),
                encoding="utf-8",
            )
            errors = validate_packets.validate_record_file(path, self.schema_set)
        self.assertTrue(any("unknown record_type" in error for error in errors), errors)

    def test_validator_has_exactly_one_schema_per_public_record_type(self) -> None:
        expected = {
            "research_packet",
            "problem_record",
            "source_record",
            "run_record",
            "evidence_record",
            "review_record",
            "packet_transition",
        }
        self.assertEqual(expected, set(self.schema_set.by_record_type))


if __name__ == "__main__":
    unittest.main()
