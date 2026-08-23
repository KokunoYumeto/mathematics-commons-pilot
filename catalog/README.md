# Catalog

`portals.json` is the three-portal index. `jobs.json` is the runnable transcription catalog. `translations.json` is the live topic → work/resource → source edition → translation edition → packet catalog. It separates workflow startability from packet/readback evidence, public repository and reader evidence from dated non-public reports, language coverage from distribution notes, and work scopes from supporting resources. The starter's `WORKS.json` is the current compact projection; later evidence is added only to the live catalog. `formalize.json` is the cross-cutting formalization intake: exact external source snapshots, result-level candidates, build scope, placeholder state, source-correspondence state, Mathlib-audit state, and packet state. Its presence does not create a fourth portal or make any formalization runnable. `check.json` is the generated validation receipt. `assets/*.json` binds release ZIPs and represented source members.

`receipts/` preserves the R1 audit projections and exposes the R2 frozen-28 admission and no-failure hardening receipts. R2 binds every job to one external admission projection, including its exact start file, workload-derived prompt file/count, native manifest, direct-byte snapshot, deterministic release part or parts, and bounded control-policy replay. `receipts/id-readers.json` binds nine public Indonesian reader PDFs to exact collection, DOI, filename, byte, SHA-256, and anonymous-readback evidence without claiming completion, source lineage, or translation QA.

`readback-r2.json` is the current transcription release-level anonymous byte/SHA-256 replay. `readback.json` remains the immutable R1 readback rather than being overwritten by a successor. `openlogic-rb.json` binds the self-contained Open Logic translation packet. `translate-rb-v7.json` and `translate-rb-v8.json` are immutable historical starter replays; the current generic workflow uses the separately recorded v9 release and readback. The generic starter contains no mathematical source or completed translation, but it is runnable as a source-intake and translation workflow once a contributor supplies or obtains the exact source.

Consumers must fetch related catalog, schema, validation, and manifest files from one exact Git commit. Verify release assets by both byte length and SHA-256; never trust a filename alone.

Regenerate the job catalog and assets only from the exact admitted packet roots:

```console
python tools/build_jobs.py --packet-root <exact-root> --output <release-dir>
python tools/build_r2_admission.py --packet-root <exact-root> --asset-dir <release-dir> --hardener-script <exact-hardener.py>
python tools/validate_jobs.py --asset-dir <release-dir> --output catalog/check.json --json
python tools/validate_jobs.py --verify-receipt
```

To reproduce the additive Indonesian-reader catalog projection from the checked-out current catalog and the checked-in receipt (the updater is idempotent; v7 and v8 remain immutable history):

```console
python tools/add_id_readers.py
```

The packet root is intentionally not recorded as a public machine path. The public catalog records source members, bytes, hashes, authority identities, scope, and receipts instead.
