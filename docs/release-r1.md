# Runnable packet release R1

Tag: `jobs-2026-08-21-r1`

This release is the first practical Mathematical Commons packet library: 28 bounded jobs represented by 29 packet assets, plus one reusable open-textbook translation kit.

## Exact scope

- admitted packet roots: 28
- admitted source files: 488
- admitted source bytes: 6,691,065,999
- packet assets: 29
- translation-kit assets: 1
- total release assets: 30
- total release ZIP bytes: 6,599,622,703
- largest asset: 1,552,442,187 bytes

Poincaré’s *Oeuvres*, Tome I is the only multipart job. Both parts belong to one catalog row and must be uploaded together.

## Trust boundary

The package builder used deterministic member names, fixed ZIP timestamps, bounded parts, and exact source hashes. The validator independently reopened every ZIP and replayed every member, CRC, byte count, and SHA-256. [`catalog/readback.json`](../catalog/readback.json) records anonymous HTTPS readback of all 30 assets and 6,599,622,703 bytes with zero mismatches or errors.

Input readiness is not output certification. Every job starts an edition workflow; none of its requested editions becomes correct merely by being packaged.

## Exclusions

The catalog preserves 27 explicit exclusion records, including HOLD, incomplete, quarantine, superseded, placeholder-bearing, QA-only, out-of-lane, and root-unverified material. In particular, ten Frobenius candidates remain excluded until their literal generator placeholders are corrected and a fresh independent packet replay passes.

See [`catalog/jobs.json`](../catalog/jobs.json) for every exact job, asset, validation receipt, and exclusion reason.
