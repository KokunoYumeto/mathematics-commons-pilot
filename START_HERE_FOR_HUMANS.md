# Start here

Mathematics Commons lists bounded mathematical jobs that can be run with spare compute on a local or hosted AI system. Each job includes exact inputs, instructions, checks, and a resumable return format. Returned work remains provisional until another contributor can inspect and replay it.

Choose one portal.

## Transcription

Select one of the [28 runnable packet envelopes](catalog/jobs.json), download every listed asset part, verify the hashes, and execute every prompt in that row's declared prompt file. Use the row's exact `prompt_count`; do not assume every job has 45 prompts. Reply `continue` only when the current response is `STATUS: IN_PROGRESS`. Reply `next prompt` only when the current response is `STATUS: COMPLETE` and its prompt number is less than `prompt_count`. Never invent a prompt after the declared final prompt. Admission replay verifies the envelope and its declared inputs; it does not certify the requested transcription output. Return the cumulative result, manifest, checks, failures, and continuation cursor.

## Translation

For a self-contained source packet, download the [Open Logic packet](https://github.com/KokunoYumeto/mathematics-commons-pilot/releases/tag/translate-openlogic-v1) and verify its recorded byte length and SHA-256. To start any other workflow-startable work, browse the [29 work scopes and their evidence](docs/translations.md), including nine public Indonesian reader PDFs, then download the [generic v9 translation starter](https://github.com/KokunoYumeto/mathematics-commons-pilot/releases/tag/translate-v9-corrected). Each row states its workflow startability, distribution class, and source note. You may also propose another mathematical work with a public source and recorded terms.

- Local agent: open the extracted package and paste `LOCAL.md`.
- Hosted web agent: upload the package and paste `WEB.md`.

The generic starter first asks which work and which exact target language you want. It records the source, distribution note, component boundary, and baseline build as the work proceeds. It contains no source work or translation, but it is the runnable workflow for starting or continuing a listed work. Its v9 work index is the current compact catalog projection.

## Open problems

Read the [Workbench v0.2 status and contribution guide](docs/workbench.md). The previously supplied package passed an independent replay, but its exact ZIP must be restored before the curation tools can be published. After restoration, contributors can work on source, statement, status, literature, and reproducibility review. Bounded mathematical attempts begin only after a specific problem packet passes admission.

## Formalization intake

Formalization is a cross-cutting workstream rather than a fourth portal. The [current intake](docs/formalize.md) connects machine-readable transcriptions and external Lean work to source-to-statement review and pinned Mathlib gap audits. Its catalog contains Desargues and result-level S-named candidates, but no formalization packet is runnable yet.

Packet validation proves the stated input boundary, not the correctness or completion of the requested output. Earlier proposal and calibration material is indexed under [legacy material](docs/legacy.md).
