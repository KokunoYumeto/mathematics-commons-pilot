# Translation starter v9

`translate-v9-final` is the current generic translation workflow release (the package version is v9). It is a chooser and source-intake kit, not a textbook or a completed translation. It is usable for every non-reference work in `catalog/translations.json`, including rows marked `starter_available` and the `source_bound_packet` Open Logic row.

## Release identity

- Release tag: [`translate-v9-final`](https://github.com/KokunoYumeto/mathematics-commons-pilot/releases/tag/translate-v9-final)
- Release target commit: `e54ccca22127430d5537b66cec884558b045745f`
- Release target tree: `b8159464852c7439739be70457afa8bc151912f1`
- Asset: `translation-starter-v9.zip`
- Asset size: 17,558 bytes
- Asset SHA-256: `C8B0B9B65EDAB21CEB84D3825789D4C896F65410F2A28441192EEF4EA7069E73`
- Asset manifest: [`catalog/assets/translate-v9-complete.json`](../catalog/assets/translate-v9-complete.json)
- Included source files: 12 / 78,979 bytes
- Included members: `KIT.json`, `WORKS.json`, source/intake instructions, prompt, QA, return, and manifest files
- Anonymous readback: [`catalog/translate-rb-v9-final.json`](../catalog/translate-rb-v9-final.json), observed 2026-08-23, release id `375294316`

The release is immutable. The live portal records the exact commit, tree, asset manifest, and anonymous readback after publication. Fetch those related files from one pinned commit; do not mix revisions.

## What “startable” means

`workflow_startability` answers whether a contributor can begin or continue a translation workflow. `starter_available` means the contributor supplies or obtains the exact source and records its identity and distribution terms. `source_bound_packet` means the Commons also publishes a self-contained source packet; verify that packet before use. `reference_only` rows are components or references, not standalone jobs.

`jobs[].state=runnable` is narrower archive evidence: it means a self-contained packet has a public release, byte/SHA-256 identity, and anonymous readback. It does not decide whether a contributor may work on a listed source they already possess or can lawfully obtain.

## Use

1. Download the ZIP and verify its size and SHA-256.
2. Read `START.md` (local) or `WEB.md` (hosted web agent).
3. Select a work and state the exact target language, locale, script, and orthographic standard.
4. Supply or obtain the exact source, preserve its terms, and return cumulative checkpoints with source/output hashes and a continuation cursor.

The workflow is vendor-neutral and supports independent, non-exclusive editions. Existing work is not overwritten; parallel work is recorded as overlap.
