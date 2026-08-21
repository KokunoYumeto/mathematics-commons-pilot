# Start here

The fastest useful contribution is one bounded job.

1. Browse [`catalog/jobs.json`](catalog/jobs.json).
2. Pick a job with `catalog_status: runnable`.
3. Download and hash-check every release asset part listed for that job, then extract all parts into one job directory.
4. Follow [`docs/run.md`](docs/run.md) through Prompt 45.
5. Return the immutable result, manifest, checks, failures, and cursor.

If you want to translate an open textbook, browse [`catalog/translations.json`](catalog/translations.json) and use the [translation kit](kits/translate/README.md). If you want to adopt or independently mirror an author/work already mapped in the interlanguage archive, use the [adoption board](docs/adopt.md).

Do not infer completion from a filename or from `strict-PASS`: that status validates the input job, not the requested output. Read the [fidelity contract](docs/fidelity.md) before spending compute.

The older proposal, 30-day pilot, calibration, and governance documents remain available through [`docs/legacy.md`](docs/legacy.md). They are history and reusable infrastructure, not the current front page.
