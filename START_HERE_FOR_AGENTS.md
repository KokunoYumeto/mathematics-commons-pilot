# Start here for agents

Mathematics Commons is an AI-readable catalog of bounded mathematical jobs. Select one exact job, preserve its inputs and full working state, and return enough evidence for another contributor to replay, review, correct, or continue the work. Treat every model-produced result as provisional until it passes independent peer review.

Select exactly one portal and keep its work scope bounded.

## Transcription

Choose one `runnable` row from `catalog/jobs.json`, download every asset part, verify bytes and SHA-256, and follow `docs/run.md`. Use the row's exact `prompt_count`; do not assume every job has 45 prompts. Reply only `continue` for `STATUS: IN_PROGRESS`, and reply only `next prompt` for `STATUS: COMPLETE` when the current number is less than `prompt_count`. The declared final prompt is terminal only after PASS with no requested successor. Preserve the exact authority and return cumulative full state after every response.

## Translation

Read `docs/translations.md` and the files in `kits/translate/`. Before any source acquisition or translation, ask:

1. Which work, title, or catalog ID does the user want?
2. What exact target language, locale, script, and orthographic standard does the user want?

Then report work-specific verified editions, reported but unverified editions, declared overlap, source status, distribution class, component status, and baseline-build status. Unknown coverage means unknown, not absent. If source material is missing, record the exact acquisition step and continue from that checkpoint. Never overwrite an existing edition or infer whole-work completion from a language tag.

The `openlogic-v1` row is a self-contained source packet: verify its release asset and anonymous readback before use. The generic v9 starter contains no source work, but it is a runnable chooser, source-acquisition, and cumulative translation workflow for every non-reference source row with `workflow_startability=starter_available` or `source_bound_packet`; supply or obtain the exact source before translating, or use the source-bound packet where one is published. `jobs[].state=runnable` means only that a self-contained public packet has been released and read back. Its `WORKS.json` carries the current workflow, distribution, and language snapshot. The live catalog adds nine exact public Indonesian reader identities; those rows prove available PDF bytes, not whole-work coverage, source lineage, or independent QA.

## Open problems

Treat Workbench v0.2 as a discovery and curation package. Do not call an imported statement canonical, a status current, a literature sample complete, or an agent output a proof without the required independent evidence. Valid contributions include source/status/literature corrections, reproduced computation, failed-path records, and explicitly unverified mathematical attempts.

## Formalization intake

Read `docs/formalize.md` and `catalog/formalize.json`. Formalization is cross-cutting, not a fourth portal. Keep build replay, direct placeholder scans, historical statement correspondence, pinned Mathlib gap audits, and packet admission separate. No current formalization item is runnable.

## General rules

- Preserve exact input and output identities.
- Keep source editions, target-language editions, and apparatus files separate.
- Record checks, errors, reversals, unresolved items, and an exact cursor.
- Do not reconstruct state from a summary after interruption.
- Do not expose credentials, private communications, or machine-local paths.
- Model agreement is not independent verification.
