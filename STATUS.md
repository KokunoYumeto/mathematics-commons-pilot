# Current status

**Scope:** transcription, translation, and open-problem research

**Date:** 21 August 2026

**Output certification:** none implied

## Transcription

- Release: [`jobs-2026-08-21-r1`](https://github.com/KokunoYumeto/mathematics-commons-pilot/releases/tag/jobs-2026-08-21-r1)
- Runnable jobs: 28
- Packet asset parts: 29
- Admitted packet files: 488
- Admitted packet bytes: 6,691,065,999
- Packet ZIP bytes: 6,599,619,260
- Workflow: 45 ordered prompts with cumulative state returned after every response
- Public readback: 29/29 packet assets plus the R1 predecessor translation-kit asset matched, for 30/30 assets and 6,599,622,703/6,599,622,703 bytes

R1 remains the newest admitted transcription release. Later candidate generations remain excluded until their exact bytes, manifests, terminal receipts, and independent cold audits pass.

## Translation

- Open-education discovery/status rows: 40
- Explicit exclusions: 8
- Subject groups in the starter: 10
- Exact interlanguage discovery snapshot: 78 work rows at commit `7a00b564ace8230c57309df2d66325e57d1c4043`
- Current translation starter: [`translate-v3`](https://github.com/KokunoYumeto/mathematics-commons-pilot/releases/tag/translate-v3)

The starter asks for the work and exact target language before acting. It contains source-selection, language-identification, source-freeze, production, return, and independent-QA instructions. It contains no textbook and no completed translation.

Most open-education rows are discovery metadata and require an independent public source/license/component/build freeze. Open Logic R020 has an exact root repository commit, tree, license, README, `.gitmodules`, and `doc` gitlink, but its component census and baseline build remain incomplete. It is not yet a runnable translation source.

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

Mechanical PASS establishes the declared file and validation boundary only. It does not establish completed scholarship or mathematical correctness. New transcription packets require their own independent cold audit. Translation sources require exact derivative rights and baseline-build closure. Problem records require independent statement, status, source, literature, and mathematical review.

The original proposal, calibration, record schemas, and immutable `v0.1.0` / `v0.1.1` releases remain indexed under [legacy material](docs/legacy.md).
