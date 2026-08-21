# Mathematics Commons

Not everyone has unlimited compute. The Mathematics Commons turns spare human–AI compute into bounded, inspectable work that can help build a global open mathematical library.

This repository is the practical front door: download one exact job, run its fixed workflow, preserve every cumulative state, and return an immutable result that another contributor can inspect. Parallel mirrors are welcome when they are declared and independently useful.

## Start a job

1. Open the [runnable-job catalog](catalog/jobs.json) or the [human run guide](docs/run.md).
2. Choose one of the **28 strict-PASS transcription packets**.
3. Download every checksum-pinned asset part listed for that job from the [`jobs-2026-08-21-r1` release](https://github.com/KokunoYumeto/mathematics-commons-pilot/releases/tag/jobs-2026-08-21-r1).
4. Verify every part's byte length and SHA-256, then extract all parts into one job directory.
5. Upload every extracted job file to one capable long-context research or coding agent and run Prompt 1 exactly.
6. Reply `continue` while that prompt reports `IN_PROGRESS`. Reply `next prompt` only after it reports `COMPLETE`. Stop after Prompt 45 COMPLETE.
7. Preserve and return the newest cumulative state ZIP, checkpoint, manifest, checks, failures, and continuation cursor.

The first release contains **29 packet assets** for 28 jobs (one large Poincaré job has two parts), plus one reusable translation-kit asset. The admitted packet roots contain **488 source files / 6,691,065,999 bytes**; the 30 downloadable ZIPs total **6,599,622,703 bytes**. Every asset and member is bound in a checked-in manifest.

`strict-PASS` means that the packet boundary, authority files, manifests, workflow, and validation receipt replayed exactly. It does **not** mean that the requested transcription, translation, mathematics, or edition is already complete or certified.

## What is available

- [Runnable transcription jobs](catalog/jobs.json) — exact author/work/language/scope, pages, authority, difficulty, planning heuristic, validation receipt, assets, bytes, and SHA-256.
- [Asset manifests](catalog/assets/) — exact ZIP parts and every represented source member.
- [Catalog validation receipt](catalog/check.json) — machine-replayed catalog, manifest, member, and release-size invariants.
- [Public release readback](catalog/readback.json) — post-publication anonymous HTTPS verification of all 30 R1 assets and seven principal raw files at the delivered commit.
- [Fidelity contract](docs/fidelity.md) — diplomatic source edition, separate monolingual target edition, restrained apparatus, exact figures, cumulative state, and cold audit.
- [Open-textbook translation lane](docs/translations.md) — 40 bounded discovery/status rows and eight explicit exclusions, including one exact public Open Logic source boundary while non-public snapshot claims remain clearly distinguished.
- [Translation kit](kits/translate/README.md) — a model-agnostic prompt, QA contract, and source-freeze template for a useful language not yet served.
- [Interlanguage adoption board](docs/adopt.md) — an exact-commit interface to 78 author/work scopes in the source archive: 9 active, 64 open for adoption, and 5 future-evidence scopes.

Jobs currently include complete bounded packets for works by Al-Battani, al-Khwarizmi, al-Tusi, Aryabhata, Bhāskara II, Cayley, Clebsch and Gordan, Dedekind, Gauss, Gibbs, Hecke, Khayyam, Klein and Fricke, Kronecker, Mikami, Picard, Poincaré, Seki, and Weber. Excluded HOLD, incomplete, quarantined, superseded, placeholder-bearing, and root-unverified candidates remain listed with exact reasons; they are not silently presented as runnable.

## The fidelity rule

These jobs produce inspectable editions, not summaries.

- Use the named highest-resolution complete authority and account for every physical page.
- Do not summarize, skip, silently normalize, modernize, invent ranges, or drop formulas, figures, tables, footnotes, or indexes.
- Produce a symbol-level diplomatic source-language edition and a separate standalone English or target-language edition—never a facing-page substitute.
- Put corrections and modern mathematical observations only in a separate restrained apparatus.
- Preserve an untouched authority crop plus a separately named conservative derivative when editable reconstruction cannot be exact.
- Return cumulative full state on every response so interruption never forces reconstruction from memory or a summary.
- Finish with deterministic integration and a fresh, non-patching cold audit.

See the complete [fidelity contract](docs/fidelity.md).

## Translate an open textbook

The translation lane is designed for university-grade and pre-university open educational resources in languages that learners and educators actually need. It includes Open Logic and carefully screened open textbooks in logic, algebra, analysis, combinatorics, geometry, probability, topology, numerical analysis, optimization, and formal mathematics. Its first catalog is a bounded discovery projection, not an independently replayable license or production receipt.

Independently freeze an entry's exact public source, edition, component boundary, and derivative rights; then declare one language and one bounded edition and use the [translation kit](kits/translate/README.md). Preserve stable identifiers, formulas, exercises, solutions, assets, component licenses, build receipts, terminology decisions, and a monolingual reader. A work that is merely free to read, No-Derivatives, rights-unknown, or reference-only is not a runnable translation source.

## Machine interface

The public contract is deliberately small and inspectable:

- [`catalog/jobs.json`](catalog/jobs.json)
- [`schemas/job-catalog.schema.json`](schemas/job-catalog.schema.json)
- [`catalog/translations.json`](catalog/translations.json)
- [`schemas/translation-catalog.schema.json`](schemas/translation-catalog.schema.json)
- [`catalog/check.json`](catalog/check.json)
- [`catalog/readback.json`](catalog/readback.json)
- [`schemas/release-readback.schema.json`](schemas/release-readback.schema.json)
- [`catalog/assets/`](catalog/assets/)

Fetch all related files from one exact Git commit. Do not mix a catalog, schema, validation receipt, or asset manifest across revisions. Release URLs are stable locators; byte length and SHA-256 are the immutable asset identities.

From a clean clone:

```console
python tools/validate_jobs.py --verify-receipt
python tools/validate_packets.py --schema-only
python -m unittest discover -s tests -p "test_*.py" -v
python tools/validate_repository.py
```

Release construction additionally requires the exact private packet roots named by the project coordinator; ordinary consumers do not need or receive those machine paths.

## Future concept: Open Problem Workbench

The [Open Problem Workbench](docs/workbench.md) is an Erdős-first concept for downloadable conjecture packets: exact statements and variants, maintained-list provenance, bounded literature, claim graphs, reproducible computations, cumulative attempts, failed-path preservation, and independent status/proof review. Its dated exploratory atlas now identifies concrete list families—from Erdős, Green, Kourovka, TOPP, Propp, and specialist dynamics collections to deliberately oversized famous problems—without treating a secondary import as a clean catalog. Oversized entries such as the Riemann Hypothesis must declare a sampled or partitioned corpus instead of claiming false completeness.

This remains a roadmap stub with zero admitted or runnable conjecture packets, not a live conjecture collection. See the [current/future roadmap](docs/roadmap.md).

## Contribute or review

Read [CONTRIBUTING.md](CONTRIBUTING.md). A useful handback identifies exact inputs and outputs, records bytes and hashes, preserves errors and reversals, declares overlap, and leaves a precise continuation cursor. Model fluency and model agreement are not proof.

The project’s Leiden alignment is self-assessed. The Leiden working group, International Mathematical Union, upstream authors, publishers, repositories, and source providers have not certified or endorsed this project.

## Rights, privacy, and history

Commons-created metadata, schemas, validators, documentation, and workflow material are CC0 where their contributors can dedicate them. Historical works, editions, scans, translations, fonts, code, and media retain their own rights and provenance. See [RIGHTS.md](RIGHTS.md).

Raw model transcripts, credentials, private communications, and unrelated personal material are not published. Any future transcript-derived reproducibility layer requires a separate proposed redaction diff and explicit approval.

The original Leiden/pilot proposal, calibration collection, schemas, frozen releases, and governance documents remain intact and citable. They are preserved as the [legacy concept and calibration layer](docs/legacy.md), not presented as the current run interface.

## Citation

[CITATION.cff](CITATION.cff) describes the preserved `v0.1.1` concept release. Earlier immutable concept deposits remain discoverable under concept DOI [`10.5281/zenodo.21828562`](https://doi.org/10.5281/zenodo.21828562); this GitHub maintenance does not mutate external DOI records.
