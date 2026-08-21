# Catalog

`portals.json` is the three-section index. `jobs.json` is the runnable transcription catalog. `translations.json` is the open-education translation-source catalog. `check.json` is the generated validation receipt. `assets/*.json` binds release ZIPs and represented source members.

`receipts/` preserves the R1 audit projections and exposes the R2 frozen-28 admission and no-failure hardening receipts. R2 binds every job to one external admission projection, including its exact start file, workload-derived prompt file/count, native manifest, direct-byte snapshot, deterministic release part or parts, and bounded control-policy replay.

Consumers must fetch related catalog, schema, validation, and manifest files from one exact Git commit. Verify release assets by both byte length and SHA-256; never trust a filename alone.

Regenerate the job catalog and assets only from the exact admitted packet roots:

```console
python tools/build_jobs.py --packet-root <exact-root> --output <release-dir>
python tools/build_r2_admission.py --packet-root <exact-root> --asset-dir <release-dir> --hardener-script <exact-hardener.py>
python tools/validate_jobs.py --asset-dir <release-dir> --output catalog/check.json --json
python tools/validate_jobs.py --verify-receipt
```

The packet root is intentionally not recorded as a public machine path. The public catalog records source members, bytes, hashes, authority identities, scope, and receipts instead.
