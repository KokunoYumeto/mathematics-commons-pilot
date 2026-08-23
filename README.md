# Mathematics Commons

Mathematics Commons organizes specific mathematical jobs that people can run with spare computing capacity. The aim is to turn compute that would otherwise sit idle into useful, inspectable work: transcribing source texts, translating open mathematical works, researching documented open problems, and converting machine-readable mathematics into reviewed formal statements and proofs.

Each job has a bounded scope, exact inputs, instructions, expected outputs, validation rules, and a resumable checkpoint format. Contributors may use local or hosted AI systems. They return the complete working state rather than a summary, so another contributor can replay the inputs, inspect or correct the output, and continue from the recorded checkpoint.

The repository is written for both people and software. Its catalogs expose each job's scope, state, files, checks, unresolved items, and continuation cursor in machine-readable form. Results remain provisional until they survive peer-to-peer review; an AI-generated answer is not accepted as correct merely because a model produced it.

## Choose a portal

| Portal | Available material | Current state |
|---|---|---|
| [Transcription](docs/run.md) | 28 admitted jobs in 30 packet ZIP parts, with exact release assets and workload-derived prompt files | Runnable |
| [Translation](docs/translations.md) | One self-contained Open Logic packet, 29 workflow-startable works, nine public Indonesian reader PDFs, other edition evidence, and a distribution-labeled translation starter | Translation workflow available; one self-contained packet published |
| [Open problems](docs/workbench.md) | Documentation and recorded replay results for Workbench v0.2; the ZIP is currently unavailable | No runnable problem packets |

The cross-cutting [formalization intake](docs/formalize.md) records three pinned external snapshots—two distinct generations of one public Lean repository plus one archived sidecar set—and 19 bounded review items, including Desargues and the S-named material found in the built parent snapshot. It contains no runnable formalization packet and makes no claim that a transcribed result is absent from Mathlib.

## Transcription

The [`jobs-2026-08-21-r2` release](https://github.com/KokunoYumeto/mathematics-commons-pilot/releases/tag/jobs-2026-08-21-r2) contains 30 packet ZIP parts for 28 jobs. The Clebsch–Gordan and Poincaré packets each use two parts. The admitted packet roots contain 538 files / 8,922,333,939 bytes; the packet ZIPs contain 8,808,377,826 bytes. The release also preserves R1's unchanged 3,443-byte historical translation kit for release continuity, for 31 assets / 8,808,381,269 bytes in total. Translation uses separate source-bound and generic releases described below.

To run a packet:

1. Select a `runnable` row in [`catalog/jobs.json`](catalog/jobs.json).
2. Download every listed asset part and verify its byte length and SHA-256.
3. Extract all parts into one directory and open the exact `start_file` declared by that catalog row.
4. Use that row's exact `prompt_count`; do not assume every job has 45 prompts. Execute Prompt 1 from the declared `prompt_file`.
5. If a response says `STATUS: IN_PROGRESS`, preserve its cumulative state and reply only `continue`. If it says `STATUS: COMPLETE` and the current prompt number is less than `prompt_count`, preserve its cumulative state and reply only `next prompt`.
6. Prompt `prompt_count` is terminal only when it completes after PASS and requests no successor. Never invent another prompt; return the cumulative state, manifest, checks, failures, and cursor.

`strict-PASS` validates the packet boundary and its recorded evidence. It does not certify a completed transcription, translation, edition, or mathematical result. The full [run instructions](docs/run.md) and [fidelity contract](docs/fidelity.md) apply.

R2 is the newest admitted transcription release. R1 remains immutable history. Later candidate generations are not presented as runnable until their exact bytes, manifests, terminal receipts, and independent cold audits pass.

## Translation

The [translation portal](docs/translations.md) is a non-exclusive set of useful open-mathematics work scopes. Contributors may start any non-reference work marked `workflow_startability=starter_available` or `source_bound_packet`, or propose another mathematical work with a public source and a recorded distribution note. It distinguishes:

- individual works and series;
- reported but unverified editions, recorded per exact language;
- composite curriculum ideas; and
- supporting components, infrastructure, references, and excluded sources.

Public choices use titles and readable semantic keys such as `openstax-prealgebra-2e`.

The [Open Logic source packet](https://github.com/KokunoYumeto/mathematics-commons-pilot/releases/tag/translate-openlogic-v1) is the first source-bound job. Its exact source snapshot, included rights material, baseline builds, ZIP identity, admission receipt, and anonymous readback are recorded in the catalog. It contains no completed translation.

The separate [`translation-starter-v9` release](https://github.com/KokunoYumeto/mathematics-commons-pilot/releases/tag/translate-v9-complete) is a generic work-selection workflow. It asks two questions before doing anything else:

1. Which work do you want to translate?
2. What exact target language, locale, script, and orthographic standard do you want?

The generic package supports both local repository-aware agents and hosted web agents. It reads work-specific public evidence and dated historical reports, records the source's distribution class and license note, requests exact source bytes when needed, and then applies the production and independent-QA contracts. It contains no textbook, source work, or completed translation, but it is a runnable translation workflow: a contributor supplies or obtains the exact source and begins a bounded edition.

The live catalog also records nine Indonesian reader PDFs in a public Figshare collection. Their DOI, filename, byte length, SHA-256, and anonymous readback are exact. They are usable public readers, but the current evidence does not by itself establish whole-work coverage, source lineage, or independent translation QA. The v8 starter remains immutable history; the v9 starter and live catalog carry the current workflow distinction and distribution labels.

Translations into any language are welcome, especially where communities have limited university-level mathematical material. UNESCO estimates that up to 40% of people lack education in a language they speak or understand. Separately, a UNESCO Institute for Statistics report cites a 48-country literacy study covering 96 alphabetic-script assessment languages. Those 96 labels are concrete communities contributors may consider; they are not an official priority list and are not the source of the 40% estimate. Contributors should document intended learners, the exact written standard, existing work-specific coverage, and available reviewers.

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
- [`catalog/readback-r2.json`](catalog/readback-r2.json): anonymous public readback of the current transcription release.
- [`catalog/readback.json`](catalog/readback.json): preserved anonymous public readback of R1.
- [`catalog/portals.json`](catalog/portals.json): exact three-section state and release projection.
- [`catalog/openlogic-rb.json`](catalog/openlogic-rb.json): anonymous public readback of the source-bound Open Logic job.
- [`catalog/translate-rb-v9.json`](catalog/translate-rb-v9.json): anonymous public readback of the current corrected generic v9 starter.
- [`catalog/translations.json`](catalog/translations.json): open-education source/status catalog.
- [`catalog/receipts/id-readers.json`](catalog/receipts/id-readers.json): exact public readback for nine Indonesian reader PDFs.
- [`catalog/formalize.json`](catalog/formalize.json): pinned formalization sources and per-result intake state.
- [`schemas/formalization-intake.schema.json`](schemas/formalization-intake.schema.json): fail-closed formalization intake contract.
- [`kits/translate/WORKS.json`](kits/translate/WORKS.json): subject, language, and distribution snapshot shipped in the current starter.
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
