# Mathematics Commons

Mathematics Commons lets people contribute otherwise idle computing capacity to specific, documented mathematical work. Each task is packaged with exact sources, instructions, validation evidence, and a return format so that results can be continued and independently checked instead of being lost or repeated.

The repository currently covers source transcription, translation of open mathematical texts, and research on documented open problems. Contributors may use local or hosted AI systems. Model output is not accepted as correct by default: each return preserves its inputs, outputs, checks, unresolved items, and continuation state for peer-to-peer review.

## Choose a section

| Section | Available material | Current state |
|---|---|---|
| [Transcription](docs/run.md) | 28 verified source packets with 45-prompt workflows | Runnable |
| [Translation](docs/translations.md) | Subject index, work/language coverage, source catalog, and interactive starter ZIP | Source selection and preflight available |
| [Open problems](docs/workbench.md) | Workbench v0.2 discovery package with 8,785 candidate rows and curation tools | Validated candidate; source ZIP must be restored before publication |

## Transcription

The [`jobs-2026-08-21-r1` release](https://github.com/KokunoYumeto/mathematics-commons-pilot/releases/tag/jobs-2026-08-21-r1) contains 29 packet ZIP parts for 28 jobs. One Poincaré packet uses two parts. The admitted packet roots contain 488 files / 6,691,065,999 bytes; the release ZIPs contain 6,599,619,260 bytes.

To run a packet:

1. Select a `runnable` row in [`catalog/jobs.json`](catalog/jobs.json).
2. Download every listed asset part and verify its byte length and SHA-256.
3. Extract all parts into one directory and read the packet's `00_READ_FIRST.md`.
4. Run Prompt 1 exactly. Reply `continue` while the current prompt is `IN_PROGRESS`; reply `next prompt` only after it is `COMPLETE`.
5. Stop after Prompt 45 COMPLETE and return the cumulative state, manifest, checks, failures, and cursor.

`strict-PASS` validates the packet boundary and its recorded evidence. It does not certify a completed transcription, translation, edition, or mathematical result. The full [run instructions](docs/run.md) and [fidelity contract](docs/fidelity.md) apply.

R1 remains the newest admitted transcription release. Later candidate generations are not presented as runnable until their exact bytes, manifests, terminal receipts, and independent cold audits pass.

## Translation

The [translation section](docs/translations.md) organizes candidate works by subject and distinguishes:

- existing or active editions, shown for language coverage;
- selected or conditional sources that require exact source/license/build preflight;
- optional and composite sources; and
- rejected or reference-only material.

The current exact interlanguage snapshot records work-specific material in Arabic, German, English, Spanish, Persian, French, Indonesian, Interslavic, Italian, Japanese, Korean, Russian, Sanskrit, Ukrainian, Vietnamese, several Chinese conventions, and mixed or undetermined records. A language appearing in that list does not mean every work is complete in that language. Check the selected work.

Download the [`translation-starter-v3` package](https://github.com/KokunoYumeto/mathematics-commons-pilot/releases/tag/translate-v3). It asks two questions before doing anything else:

1. Which work do you want to translate?
2. What exact target language, locale, script, and orthographic standard do you want?

The package supports both local repository-aware agents and hosted web agents. It checks current coverage and source eligibility, requests the exact source bytes when needed, freezes `SOURCE.json`, and then applies the production and independent-QA contracts. It contains no textbook and no completed translation.

No authoritative UNESCO list of “96 underserved languages” was found. This repository does not publish an invented list under UNESCO's name. Contributors may select any language not already maintained for a chosen work and should document the educational need, community input, orthographic standard, and available review capacity.

## Open problems

Workbench v0.2 was independently replayed as an exact supplied discovery package:

- 13,308,489-byte ZIP;
- SHA-256 `A087B8A9765476F7DC26B00280299153D3BE46A536C698035445AF723451BD2A`;
- 160 safe archive entries;
- 159/159 payload entries replayed against its self-excluding manifest; and
- internal validation PASS with 59 checks and zero failures.

The exact ZIP is currently unavailable, so no `workbench-v0.2` release is being claimed. Publication requires restoration of the exact 13,308,489-byte file with the SHA-256 above, followed by another replay and public readback.

The package contains 8,785 secondary statement candidates from 13 collections, 1,246 preliminary candidates, 858 conservative triage candidates, 824 statement-integrity review rows, 4,831 provenance/status/rights review rows, 2,076 source-document rows, and 8,785 literature-query rows. Its Erdős snapshot contains 1,217 metadata records, including 608 classified as open in that snapshot, 556 with imported statement text, 52 statement gaps, and 76 status conflicts.

This is an incomplete discovery and curation package. It is not a canonical current-problem catalog, a complete literature corpus, or a collection of verified proofs. Useful contributions include statement verification, status reconciliation, source recovery, literature integration, reproduced computation, counterexample searches, bounded mathematical attempts, and independently checked corrections. See the [Open Problem Workbench documentation](docs/workbench.md).

## Verification files

- [`catalog/jobs.json`](catalog/jobs.json): transcription jobs and release assets.
- [`catalog/assets/`](catalog/assets/): exact ZIP/member manifests.
- [`catalog/check.json`](catalog/check.json): catalog and local-build validation receipt.
- [`catalog/readback.json`](catalog/readback.json): anonymous public readback of R1.
- [`catalog/portals.json`](catalog/portals.json): exact three-section state and release projection.
- [`catalog/translate-rb.json`](catalog/translate-rb.json): anonymous public readback of translation starter v3.
- [`catalog/translations.json`](catalog/translations.json): open-education source/status catalog.
- [`kits/translate/WORKS.json`](kits/translate/WORKS.json): translation subject and coverage index.
- [`docs/adopt.md`](docs/adopt.md): exact-commit interlanguage adoption snapshot.
- [`docs/workbench.md`](docs/workbench.md): Workbench status, contents, and contribution contract.

Fetch related machine files from one exact Git commit. Do not mix catalogs, schemas, receipts, or manifests across revisions. Release URLs are locators; byte lengths and SHA-256 values are the immutable identities.

From a clean clone:

```console
python tools/validate_jobs.py --verify-receipt
python tools/validate_packets.py --schema-only
python -m unittest discover -s tests -p "test_*.py" -v
python tools/validate_repository.py
```

## Contribution and evidence rules

Read [CONTRIBUTING.md](CONTRIBUTING.md). Every contribution identifies exact inputs and outputs, records checks and unresolved items, preserves earlier generations, and leaves a continuation cursor. A model-generated proof or status claim remains unverified until appropriate independent review.

Third-party works, scans, editions, translations, fonts, code, and media retain their own rights and provenance. See [RIGHTS.md](RIGHTS.md). Raw transcripts, credentials, private communications, and unrelated personal material are not public artifacts.

The original proposal, calibration material, schemas, and `v0.1.0` / `v0.1.1` releases remain available through [the legacy index](docs/legacy.md). [CITATION.cff](CITATION.cff) describes the preserved `v0.1.1` concept release; it is not the citation record for the current three-section publication.
