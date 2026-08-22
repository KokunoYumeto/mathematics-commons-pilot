# Runnable packet release R2

Tag: `jobs-2026-08-21-r2`

R2 republishes the same 28 bounded transcription jobs as R1 with their current sealed packet bytes, expanded direct-file coverage, corrected manifests, and hardened interaction controls. R1 remains immutable historical evidence; R2 does not rewrite its tag, assets, catalogs, or receipts.

## Exact scope

- admitted packet roots: 28
- admitted source files: 538
- admitted source bytes: 8,922,333,939
- packet assets: 30
- translation-kit assets: 1
- total release assets: 31
- largest asset: 1,573,636,853 bytes

The 3,443-byte translation-kit asset is preserved unchanged from R1 for release continuity. It is not the current Translation portal starter; that is published separately as `translate-v6`.

Clebsch–Gordan's *Theorie der Abelschen Functionen* and Poincaré's *Oeuvres*, Tome I are multipart jobs. Every listed part belongs to its single catalog row and must be downloaded and extracted into one job directory. The other 26 transcription jobs use one packet asset each.

Exact asset byte lengths, SHA-256 values, member boundaries, and download URLs are authoritative in [`catalog/jobs.json`](../catalog/jobs.json) and [`catalog/assets/`](../catalog/assets/). Do not infer an asset identity from this prose.

## Interaction changes

R2 removes the R1-wide assumption of 45 prompts. Each job declares its own workload-derived `prompt_count`, exact `start_file`, and exact `prompt_file`; there is no global minimum or maximum. Start with the declared start file, execute every prompt in the declared prompt file in order, reply `continue` only to a platform-forced `IN_PROGRESS` split, and reply `next prompt` after a prompt completes.

No assumed time, runtime, token, response-count, or effort cap applies. Every response returns the newest cumulative full-state ZIP, checkpoint, and manifest. Repairable defects must be resolved from the attached authority bytes, recorded, and followed by a fresh nonpatching audit until PASS. Ordinary `HOLD` or terminal `FAIL` is not a completion state. When content cannot be encoded safely, an exact authority crop plus a separate apparatus note preserves it without guessing or omission.

## Admission boundary

R2 binds each job's direct-file snapshot, start file, prompt file, native packet manifest, deterministic release asset or assets, and workload-specific prompt count. The path-neutral admission and no-failure hardening projections are published under [`catalog/receipts/`](../catalog/receipts/), and their identities are bound by the catalog.

Deterministic packaging and local ZIP replay are necessary but not sufficient. [`catalog/readback-r2.json`](../catalog/readback-r2.json) is the release-level record for anonymous HTTPS byte and SHA-256 replay after publication; the older [`catalog/readback.json`](../catalog/readback.json) remains the immutable R1 receipt. Packet admission proves that the attached authority and workflow boundary are runnable; it does not certify the editions that contributors will produce.
