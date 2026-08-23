# Current status

**Scope:** transcription, translation, open-problem research, and formalization intake

**Date:** 22 August 2026

**Output certification:** none implied

## Transcription

- Release: [`jobs-2026-08-21-r2`](https://github.com/KokunoYumeto/mathematics-commons-pilot/releases/tag/jobs-2026-08-21-r2)
- Runnable jobs: 28
- Packet asset parts: 30
- Admitted packet files: 538
- Admitted packet bytes: 8,922,333,939
- Packet ZIP bytes: 8,808,377,826
- Workflow: each job declares its exact workload-derived start file, prompt file, and prompt count; cumulative state is returned after every response
- Transcription public readback: 30/30 packet assets plus R1's unchanged historical translation-kit asset matched, totaling 31 assets / 8,808,381,269 bytes. Translation uses separate source-bound and generic releases.

R2 is the newest admitted transcription release. R1 remains immutable history. Later candidate generations remain excluded until their exact bytes, manifests, terminal receipts, and independent cold audits pass.

## Translation

- Topics: 10
- Candidate works: 29
- Supporting resources and collections: 12
- Exact source-edition rows: 41
- Translation-edition evidence rows: 23
- Public Indonesian reader PDFs: 9 files / 23,510,535 bytes, anonymously length/SHA-256 verified; coverage, lineage, and review unassessed
- Runnable source-bound jobs: Open Logic Text
- Generic starter: distribution-labeled work-selection workflow; not a runnable translation job
- Explicit exclusions: 8
- Source-bound release: [`translate-openlogic-v1`](https://github.com/KokunoYumeto/mathematics-commons-pilot/releases/tag/translate-openlogic-v1)
- Generic starter: v8 distribution-labeled build prepared on the maintenance branch; public release/readback is the next publication checkpoint.

The Open Logic job binds an exact source snapshot, included rights material, reproducible baseline builds, a checksum-pinned release asset, an admission receipt, and anonymous readback. It contains no completed translation. The generic starter asks for the work and exact target language before acting, accepts additional works, displays the recorded distribution class and note, separates public evidence from dated historical reports, and contains source-selection, language-identification, production, return, and independent-QA instructions. It contains no textbook, source work, or completed translation.

Other works are listed suggestions with explicit source and distribution notes. Only a packaged job with a public release and readback is called runnable. Nine public Indonesian reader PDFs now have exact DOI, filename, byte, and SHA-256 evidence, but that evidence alone does not establish whole-work completion, source lineage, or independent QA. Historical activity reports state only what was reported at their recording date; they do not establish current work or completion.

## Formalization

- Exact external source snapshots: 2
- Bounded intake rows: 19
- Desargues rows: 2, one algebraic review candidate and one placeholder-affected projective item
- S-named theorem, sidecar, or literature rows: 14
- Completed statement-correspondence reviews: 0
- Completed pinned Mathlib gap audits: 0
- Runnable formalization packets: 0

The first snapshot is [`sneed-and-feed/lean-theorems-1`](https://github.com/sneed-and-feed/lean-theorems-1) at commit `6cf9ce44c1a8281699fa2f3128a764e0c347e7f6`. Its default target covers 29 of 30 Lean files and contains four `sorry` tokens; the excluded Colorful Helly module also fails targeted compilation. The second is Zenodo record [`21129946`](https://zenodo.org/records/21129946), whose four small Noether, Steinitz, Weber, and Jordan sidecars compile individually but have no completed historical statement review. Exact per-item state is in [`catalog/formalize.json`](catalog/formalize.json).

## Open problems

- Publication: pending restoration of the exact supplied ZIP
- Expected archive: 13,308,489 bytes / SHA-256 `A087B8A9765476F7DC26B00280299153D3BE46A536C698035445AF723451BD2A`
- Archive entries: 160 safe paths
- Manifest replay: 159/159
- Internal validation: PASS, 59 checks, zero failures
- Candidate statement rows: 8,785
- Conservative triage rows: 858
- Canonical runnable problem packets: 0

Workbench v0.2 is an independently replayed but currently unavailable source package. No public release is claimed. Its exact ZIP must be restored, replayed, published, and read back before the package is downloadable here. It does not establish canonical statements, current status for every problem, complete literature coverage, or any proof.

## Admission and review boundary

Mechanical PASS establishes the declared file and validation boundary only. It does not establish completed scholarship or mathematical correctness. New transcription packets require their own independent cold audit. Translation packets record exact source, distribution, and build evidence; formalization items require separate source-correspondence and pinned Mathlib audits. Problem records require independent statement, status, source, literature, and mathematical review.

The original proposal, calibration, record schemas, and immutable `v0.1.0` / `v0.1.1` releases remain indexed under [legacy material](docs/legacy.md).
