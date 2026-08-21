# Catalog

`portals.json` is the three-section index. `jobs.json` is the runnable transcription catalog. `translations.json` is the open-education translation-source catalog. `check.json` is the generated validation receipt. `assets/*.json` binds release ZIPs and represented source members.

`receipts/` exposes path-neutral public projections of the global admission audit and the two terminal sidecar audits that are not direct packet members. The catalogs retain each original receipt's byte length/SHA-256 and separately bind the public projection's path/bytes/SHA-256 plus every minimal path substitution.

Consumers must fetch related catalog, schema, validation, and manifest files from one exact Git commit. Verify release assets by both byte length and SHA-256; never trust a filename alone.

Regenerate the job catalog and assets only from the exact admitted packet roots:

```console
python tools/build_jobs.py --packet-root <exact-root> --output <release-dir>
python tools/validate_jobs.py --asset-dir <release-dir> --output catalog/check.json --json
python tools/validate_jobs.py --verify-receipt
```

The packet root is intentionally not recorded as a public machine path. The public catalog records source members, bytes, hashes, authority identities, scope, and receipts instead.
