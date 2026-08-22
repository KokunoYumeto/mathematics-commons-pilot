# Start here

Mathematics Commons lists bounded mathematical jobs that can be run with spare compute on a local or hosted AI system. Each job includes exact inputs, instructions, checks, and a resumable return format. Returned work remains provisional until another contributor can inspect and replay it.

Choose one portal.

## Transcription

Select one of the [28 runnable packet envelopes](catalog/jobs.json), download every listed asset part, verify the hashes, and execute every prompt in that row's declared prompt file. Admission replay verifies the envelope and its declared inputs; it does not certify the requested transcription output. Return the cumulative result, manifest, checks, failures, and continuation cursor.

## Translation

For an admitted source-bound job, download the [Open Logic packet](https://github.com/KokunoYumeto/mathematics-commons-pilot/releases/tag/translate-openlogic-v1), verify its recorded byte length and SHA-256, and choose the exact target language and written standard. To start another work, browse the [29 suggestions and work-specific edition evidence](docs/translations.md), including nine public Indonesian reader PDFs, then download the [generic v7 source-preflight starter](https://github.com/KokunoYumeto/mathematics-commons-pilot/releases/tag/translate-v7). You may also propose another mathematical work with a verifiable open source and derivative license.

- Local agent: open the extracted package and paste `LOCAL.md`.
- Hosted web agent: upload the package and paste `WEB.md`.

The generic starter first asks which work and which exact target language you want. It does not translate until the source, derivative license, component boundary, and baseline build are recorded. It contains no source work or translation and is not itself a runnable job. Its work index is the immutable v7 release snapshot, so check the live portal for evidence added after that release.

## Open problems

Read the [Workbench v0.2 status and contribution guide](docs/workbench.md). The previously supplied package passed an independent replay, but its exact ZIP must be restored before the curation tools can be published. After restoration, contributors can work on source, statement, status, literature, and reproducibility review. Bounded mathematical attempts begin only after a specific problem packet passes admission.

## Formalization intake

Formalization is a cross-cutting workstream rather than a fourth portal. The [current intake](docs/formalize.md) connects machine-readable transcriptions and external Lean work to source-to-statement review and pinned Mathlib gap audits. Its catalog contains Desargues and result-level S-named candidates, but no formalization packet is runnable yet.

Packet validation proves the stated input boundary, not the correctness or completion of the requested output. Earlier proposal and calibration material is indexed under [legacy material](docs/legacy.md).
