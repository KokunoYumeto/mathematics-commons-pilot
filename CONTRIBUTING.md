# Contributing

Contributions are accepted through Transcription, Translation, and Open problems. Each contribution must identify exact inputs, outputs, checks, unresolved items, and a continuation cursor.

## Transcription

1. Choose a `runnable` entry in [`catalog/jobs.json`](catalog/jobs.json).
2. Verify and extract every listed asset part.
3. Follow the exact [`continue` / `next prompt` workflow](docs/run.md).
4. Preserve every cumulative checkpoint.
5. Return an immutable result, manifest, checks, failures, and cursor through [Return a packet result](https://github.com/KokunoYumeto/mathematics-commons-pilot/issues/new?template=job_return.yml).

Packet integrity is not edition certification. Preserve the diplomatic source edition, separate monolingual target edition, restrained apparatus, figures, page topology, build receipts, and cold-audit boundary.

## Translation

1. Choose a work from the [subject index](docs/translations.md) or the exact [interlanguage adoption snapshot](docs/adopt.md).
2. State the exact target language, locale, script, and orthographic standard.
3. Report existing editions and active work for that exact scope.
4. Freeze the immutable source, derivative license, component inventory, and baseline build.
5. Use the [translation starter](kits/translate/README.md) and return a standalone monolingual edition with cumulative state and independent QA.

Open a [translation issue](https://github.com/KokunoYumeto/mathematics-commons-pilot/issues/new?template=translation.yml) to declare the scope. Current production and complete rows are coverage information, not permission to overwrite another edition. Candidate status does not waive source or rights preflight. No-Derivatives, free-to-read-only, rights-unknown, donor, reference, and rejected sources are not translation assignments.

## Open problems

Valid contributions include:

- canonical-statement or variant corrections;
- status corrections supported by exact sources;
- source recovery and rights/access metadata;
- bounded literature and claim-graph additions;
- reproduced computations or counterexample searches;
- failed approaches with enough detail to avoid repetition;
- sharper bounds or new lemmas marked unverified; and
- suspected proofs or refutations clearly marked `CLAIMED_UNVERIFIED`.

Use [Propose an established open problem](https://github.com/KokunoYumeto/mathematics-commons-pilot/issues/new?template=open_problem.yml) or [Submit a literature lead](https://github.com/KokunoYumeto/mathematics-commons-pilot/issues/new?template=literature_lead.yml). Do not send raw model output to list maintainers or mathematicians. Return a concise evidence-backed delta with exact citations, code/data identities, checks, contradictions, and next steps.

## Required handback fields

- exact work, source, edition, language or problem ID;
- immutable input identities;
- public result commit or versioned URL;
- manifest path, bytes, and SHA-256;
- checks actually run and their receipts;
- every failure, correction, reversal, and unresolved item; and
- exact terminal or continuation cursor.

## Credit, privacy, and repository discipline

Record human contributors, public pseudonyms, source leads, reviewers, correctors, and material tools by role. Models are tools, not authors. Third-party rights remain attached as described in [RIGHTS.md](RIGHTS.md).

Do not publish raw transcripts, credentials, private communications, chain-of-thought, or unrelated local data. Keep names short and trees shallow. Do not rewrite producer bytes or erase prior generations. Large packet ZIPs belong in versioned GitHub Releases, not Git history.
