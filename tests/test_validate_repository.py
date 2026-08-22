#!/usr/bin/env python3
"""Regression tests for public-repository structural validation."""

from __future__ import annotations

import contextlib
import hashlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import validate_repository  # noqa: E402


class RepositoryValidationTests(unittest.TestCase):
    def test_r1_release_readback_is_byte_pinned(self) -> None:
        errors: list[str] = []
        validate_repository.check_immutable_r1_readback(errors)
        self.assertEqual([], errors)

        with tempfile.TemporaryDirectory() as temporary:
            repository = Path(temporary)
            receipt = repository / "catalog" / "readback.json"
            receipt.parent.mkdir(parents=True)
            receipt.write_bytes(b"changed\n")
            errors = []
            with mock.patch.object(validate_repository, "ROOT", repository):
                validate_repository.check_immutable_r1_readback(errors)
            self.assertIn("byte length changed", "\n".join(errors))
            self.assertIn("SHA-256 changed", "\n".join(errors))

    def _write_evidence_manifest(
        self,
        repository: Path,
        artifact_path: str,
        payload: bytes,
        *,
        byte_size: int | None = None,
        digest: str | None = None,
        redaction_status: str = "passed",
        publication_preview_status: str = "approved",
        redistribution_status: str = "permitted",
    ) -> Path:
        record = json.loads(
            (ROOT / "examples" / "calibration" / "evidence-record.json").read_text(
                encoding="utf-8"
            )
        )
        artifact_id = "TEST-OPAQUE-ARTIFACT-001"
        record["artifact_id"] = artifact_id
        record["artifact_path"] = artifact_path
        record["media_type"] = "application/octet-stream"
        record["byte_size"] = len(payload) if byte_size is None else byte_size
        record["hashes"] = [
            {
                "algorithm": "sha256",
                "digest": digest or hashlib.sha256(payload).hexdigest(),
            }
        ]
        record["submission_boundary"]["allowlisted_artifact_ids"] = [artifact_id]
        record["submission_boundary"]["redaction_status"] = redaction_status
        record["submission_boundary"][
            "publication_preview_status"
        ] = publication_preview_status
        record["submission_rights"]["submitted_component_ids"] = [artifact_id]
        record["submission_rights"][
            "redistribution_status"
        ] = redistribution_status
        record_path = repository / "records" / "opaque-evidence.json"
        record_path.parent.mkdir(parents=True, exist_ok=True)
        record_path.write_text(
            json.dumps(record, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        return record_path

    def _check_public_artifacts(
        self,
        repository: Path,
    ) -> tuple[list[str], list[Path]]:
        errors: list[str] = []
        with mock.patch.object(validate_repository, "ROOT", repository):
            files = validate_repository.public_repository_files(errors)
            if not errors:
                validate_repository.check_public_artifact_manifests(errors, files)
        return errors, files

    def test_validator_safely_scans_its_own_source(self) -> None:
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            status = validate_repository.main()
        self.assertEqual(0, status, output.getvalue())
        self.assertIn("PASS:", output.getvalue())

    def test_v7_readback_is_required_only_after_portal_declaration(self) -> None:
        cases = (
            (
                {
                    "schema": "math-commons-portal-catalog/v1",
                    "sections": [{"id": "translation", "release": {"tag": "translate-v6"}}],
                },
                False,
            ),
            (
                {"schema": "math-commons-portal-catalog/v2", "sections": []},
                True,
            ),
            (
                {
                    "schema": "math-commons-portal-catalog/v1",
                    "sections": [{"id": "translation", "release": {"tag": "translate-v7"}}],
                },
                True,
            ),
        )
        for portal, should_require in cases:
            with self.subTest(portal=portal):
                with tempfile.TemporaryDirectory() as temporary:
                    repository = Path(temporary)
                    path = repository / "catalog" / "portals.json"
                    path.parent.mkdir(parents=True)
                    path.write_text(json.dumps(portal) + "\n", encoding="utf-8")
                    errors: list[str] = []
                    with (
                        mock.patch.object(validate_repository, "ROOT", repository),
                        mock.patch.object(
                            validate_repository,
                            "REQUIRED",
                            {"catalog/portals.json"},
                        ),
                    ):
                        validate_repository.check_required(errors)
                marker = "missing required file: catalog/translate-rb-v7.json"
                self.assertEqual(marker in errors, should_require, errors)

    def test_malformed_portal_cannot_silently_disable_v7_readback(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repository = Path(temporary)
            path = repository / "catalog" / "portals.json"
            path.parent.mkdir(parents=True)
            path.write_text('{"schema":', encoding="utf-8")
            errors: list[str] = []
            with (
                mock.patch.object(validate_repository, "ROOT", repository),
                mock.patch.object(
                    validate_repository,
                    "REQUIRED",
                    {"catalog/portals.json"},
                ),
            ):
                validate_repository.check_required(errors)
        self.assertIn("cannot inspect portal catalog requirements", "\n".join(errors))

    def test_legacy_portal_rejects_an_undeclared_v7_readback(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repository = Path(temporary)
            catalog = repository / "catalog"
            catalog.mkdir(parents=True)
            (catalog / "portals.json").write_text(
                json.dumps(
                    {
                        "schema": "math-commons-portal-catalog/v1",
                        "sections": [
                            {
                                "id": "translation",
                                "release": {"tag": "translate-v6"},
                            }
                        ],
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            (catalog / "translate-rb-v7.json").write_text("{}\n", encoding="utf-8")
            errors: list[str] = []
            with (
                mock.patch.object(validate_repository, "ROOT", repository),
                mock.patch.object(
                    validate_repository,
                    "REQUIRED",
                    {"catalog/portals.json"},
                ),
            ):
                validate_repository.check_required(errors)
        self.assertIn("undeclared v7 readback", "\n".join(errors))

    def test_leak_scan_covers_tracked_env_extensionless_and_secret_signatures(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repository = Path(temporary)
            subprocess.run(
                ["git", "init", "--quiet"], cwd=repository, check=True
            )
            samples = {
                ".env": "API_TOKEN=" + "gh" + "p_1234567890abcdefghij\n",
                "NOTICE": (
                    "local path /" + "home/private-user/project/file.txt\n"
                ),
                "credential.pem": (
                    "-----BEGIN " + "PRIVATE KEY-----\nnot-a-real-key\n"
                    "-----END PRIVATE KEY-----\n"
                ),
                "cloud.conf": "access_key=" + "AK" + "IAABCDEFGHIJKLMNOP\n",
                "windows.txt": "D:/" + "Users/private-user/secret.txt\n",
            }
            for name, content in samples.items():
                (repository / name).write_text(content, encoding="utf-8")
            subprocess.run(
                ["git", "add", "--", *samples], cwd=repository, check=True
            )
            errors: list[str] = []
            with mock.patch.object(validate_repository, "ROOT", repository):
                files = validate_repository.public_repository_files(errors)
                validate_repository.check_private_patterns(errors, files)
            rendered = "\n".join(errors)
            for name in samples:
                self.assertIn(name, rendered, rendered)

    def test_public_symlink_is_rejected_without_reading_escape_target(self) -> None:
        with tempfile.TemporaryDirectory() as temporary, tempfile.TemporaryDirectory() as outside:
            repository = Path(temporary)
            target = Path(outside) / "private.txt"
            target.write_text("outside-private-data", encoding="utf-8")
            link = repository / "public-link.txt"
            try:
                link.symlink_to(target)
            except OSError as exc:
                self.skipTest(f"symbolic links unavailable on this platform: {exc}")
            errors: list[str] = []
            with mock.patch.object(validate_repository, "ROOT", repository):
                files = validate_repository.public_repository_files(errors)
            self.assertEqual([], files)
            self.assertIn("public symbolic link is not permitted", "\n".join(errors))

    def test_non_markdown_text_artifact_stays_lf_with_autocrlf_enabled(self) -> None:
        payload = b"\\documentclass{article}\n\\begin{document}\nExact bytes.\n\\end{document}\n"
        expected = hashlib.sha256(payload).hexdigest()

        with tempfile.TemporaryDirectory() as temporary:
            temporary_root = Path(temporary)
            source = temporary_root / "source"
            checkout = temporary_root / "checkout"
            artifact = source / "artifacts" / "sample.tex"
            artifact.parent.mkdir(parents=True)
            (source / ".gitattributes").write_bytes(
                (ROOT / ".gitattributes").read_bytes()
            )
            artifact.write_bytes(payload)

            commands = [
                ["git", "init", "--quiet"],
                ["git", "config", "user.name", "Calibration"],
                ["git", "config", "user.email", "calibration@example.invalid"],
                ["git", "add", ".gitattributes", "artifacts/sample.tex"],
                ["git", "commit", "--quiet", "-m", "Add exact text artifact"],
            ]
            for command in commands:
                completed = subprocess.run(
                    command,
                    cwd=source,
                    check=False,
                    capture_output=True,
                    text=True,
                )
                self.assertEqual(
                    0,
                    completed.returncode,
                    completed.stdout + completed.stderr,
                )

            cloned = subprocess.run(
                [
                    "git",
                    "-c",
                    "core.autocrlf=true",
                    "clone",
                    "--quiet",
                    str(source),
                    str(checkout),
                ],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(0, cloned.returncode, cloned.stdout + cloned.stderr)

            checked_out = (checkout / "artifacts" / "sample.tex").read_bytes()
            blob = subprocess.run(
                ["git", "show", "HEAD:artifacts/sample.tex"],
                cwd=checkout,
                check=True,
                capture_output=True,
            ).stdout
            self.assertEqual(payload, blob)
            self.assertEqual(blob, checked_out)
            self.assertEqual(expected, hashlib.sha256(checked_out).hexdigest())

    def test_unmanifested_known_binary_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repository = Path(temporary)
            subprocess.run(["git", "init", "--quiet"], cwd=repository, check=True)
            artifact = repository / "artifacts" / "unmanifested.png"
            artifact.parent.mkdir(parents=True)
            artifact.write_bytes(b"plain UTF-8 bytes with a binary extension\n")
            subprocess.run(
                ["git", "add", "--", "artifacts/unmanifested.png"],
                cwd=repository,
                check=True,
            )

            errors, _ = self._check_public_artifacts(repository)
            rendered = "\n".join(errors)
            self.assertIn("lacks an exact problem/source/evidence manifest", rendered)
            self.assertIn("known-binary extension", rendered)

    def test_unmanifested_utf8_artifact_outside_infrastructure_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repository = Path(temporary)
            subprocess.run(["git", "init", "--quiet"], cwd=repository, check=True)
            artifact = repository / "work" / "PACKET-001" / "undeclared-proof.md"
            artifact.parent.mkdir(parents=True)
            artifact.write_text("A fully readable but undeclared proof.\n", encoding="utf-8")

            errors, _ = self._check_public_artifacts(repository)
            rendered = "\n".join(errors)
            self.assertIn("lacks an exact problem/source/evidence manifest", rendered)
            self.assertIn("outside the explicit project-infrastructure allowlist", rendered)

    def test_opaque_artifact_manifest_must_match_exact_bytes(self) -> None:
        payload = b"bounded\0opaque artifact"
        with tempfile.TemporaryDirectory() as temporary:
            repository = Path(temporary)
            subprocess.run(["git", "init", "--quiet"], cwd=repository, check=True)
            relative = "artifacts/mismatched.dat"
            artifact = repository / relative
            artifact.parent.mkdir(parents=True)
            artifact.write_bytes(payload)
            record = self._write_evidence_manifest(
                repository,
                relative,
                payload,
                byte_size=len(payload) + 1,
                digest="0" * 64,
            )
            subprocess.run(
                [
                    "git",
                    "add",
                    "--",
                    artifact.relative_to(repository).as_posix(),
                    record.relative_to(repository).as_posix(),
                ],
                cwd=repository,
                check=True,
            )

            errors, _ = self._check_public_artifacts(repository)
            rendered = "\n".join(errors)
            self.assertIn("no valid manifest", rendered)
            self.assertIn("byte_size does not match exact artifact bytes", rendered)
            self.assertIn("SHA-256 does not match exact artifact bytes", rendered)

    def test_test_fixture_record_cannot_authorize_public_artifact(self) -> None:
        payload = b"fixture-authority-test\0"
        with tempfile.TemporaryDirectory() as temporary:
            repository = Path(temporary)
            subprocess.run(["git", "init", "--quiet"], cwd=repository, check=True)
            relative = "artifacts/not-authorized.dat"
            artifact = repository / relative
            artifact.parent.mkdir(parents=True)
            artifact.write_bytes(payload)
            record = self._write_evidence_manifest(repository, relative, payload)
            fixture_record = repository / "tests" / "fixtures" / "evidence.json"
            fixture_record.parent.mkdir(parents=True)
            record.replace(fixture_record)

            errors, _ = self._check_public_artifacts(repository)
            rendered = "\n".join(errors)
            self.assertIn("lacks an exact problem/source/evidence manifest", rendered)
            self.assertIn(relative, rendered)

    def test_public_artifact_size_limit_is_enforced_before_manifest_use(self) -> None:
        payload = b"12345\0"
        with tempfile.TemporaryDirectory() as temporary:
            repository = Path(temporary)
            subprocess.run(["git", "init", "--quiet"], cwd=repository, check=True)
            relative = "artifacts/too-large.dat"
            artifact = repository / relative
            artifact.parent.mkdir(parents=True)
            artifact.write_bytes(payload)
            self._write_evidence_manifest(repository, relative, payload)

            with mock.patch.object(
                validate_repository,
                "MAX_PUBLIC_FILE_BYTES",
                len(payload) - 1,
            ):
                errors, _ = self._check_public_artifacts(repository)
            self.assertIn("artifact limit", "\n".join(errors))

    def test_exact_permitted_opaque_manifest_passes_without_byte_leak_scan(self) -> None:
        secret_like = "gh" + "p_1234567890abcdefghij"
        payload = b"\xff\xfe" + secret_like.encode("ascii")
        with tempfile.TemporaryDirectory() as temporary:
            repository = Path(temporary)
            subprocess.run(["git", "init", "--quiet"], cwd=repository, check=True)
            relative = "artifacts/permitted.blob"
            artifact = repository / relative
            artifact.parent.mkdir(parents=True)
            artifact.write_bytes(payload)
            self._write_evidence_manifest(repository, relative, payload)

            errors, files = self._check_public_artifacts(repository)
            self.assertEqual([], errors, "\n".join(errors))
            with mock.patch.object(validate_repository, "ROOT", repository):
                validate_repository.check_private_patterns(errors, files)
            self.assertEqual([], errors, "\n".join(errors))

    def test_exact_permitted_utf8_artifact_manifest_passes(self) -> None:
        payload = b"A bounded, intentionally public UTF-8 artifact.\n"
        with tempfile.TemporaryDirectory() as temporary:
            repository = Path(temporary)
            subprocess.run(["git", "init", "--quiet"], cwd=repository, check=True)
            relative = "work/PACKET-001/permitted-proof.md"
            artifact = repository / relative
            artifact.parent.mkdir(parents=True)
            artifact.write_bytes(payload)
            self._write_evidence_manifest(repository, relative, payload)

            errors, _ = self._check_public_artifacts(repository)
            self.assertEqual([], errors, "\n".join(errors))

    def test_utf8_payload_with_binary_extension_is_still_leak_scanned(self) -> None:
        secret_like = "gh" + "p_1234567890abcdefghij"
        payload = ("renamed readable secret: " + secret_like + "\n").encode("utf-8")
        with tempfile.TemporaryDirectory() as temporary:
            repository = Path(temporary)
            subprocess.run(["git", "init", "--quiet"], cwd=repository, check=True)
            relative = "artifacts/credential.png"
            artifact = repository / relative
            artifact.parent.mkdir(parents=True)
            artifact.write_bytes(payload)
            self._write_evidence_manifest(repository, relative, payload)

            errors, files = self._check_public_artifacts(repository)
            self.assertEqual([], errors, "\n".join(errors))
            with mock.patch.object(validate_repository, "ROOT", repository):
                validate_repository.check_private_patterns(errors, files)
            self.assertIn(relative, "\n".join(errors))

    def test_opaque_manifest_requires_approved_permitted_publication(self) -> None:
        payload = b"approved-boundary-test\0"
        with tempfile.TemporaryDirectory() as temporary:
            repository = Path(temporary)
            subprocess.run(["git", "init", "--quiet"], cwd=repository, check=True)
            relative = "artifacts/unapproved.dat"
            artifact = repository / relative
            artifact.parent.mkdir(parents=True)
            artifact.write_bytes(payload)
            self._write_evidence_manifest(
                repository,
                relative,
                payload,
                redaction_status="pending",
                publication_preview_status="pending",
                redistribution_status="unresolved",
            )

            errors, _ = self._check_public_artifacts(repository)
            rendered = "\n".join(errors)
            self.assertIn("redaction_status is not passed", rendered)
            self.assertIn("publication_preview_status is not approved", rendered)
            self.assertIn("submission redistribution is not permitted", rendered)


if __name__ == "__main__":
    unittest.main()
