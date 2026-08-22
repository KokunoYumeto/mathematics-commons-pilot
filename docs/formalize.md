# Formalization from transcribed mathematics

Status: intake scaffold. Two exact external source snapshots and 19 bounded items are cataloged; no formalization packet is currently runnable.

This is a cross-cutting Mathematics Commons workstream, not a fourth main portal. It connects the transcription and translation collections to formal proof work: select one exact result, compare its machine-readable source with a Lean statement, audit the pinned Mathlib version for existing coverage, and return a reproducible formalization or source-to-library map. The external Lean work below demonstrates that this workflow is practical while also showing why compilation alone is not enough.

There are two separate conversions. Converting a scan into verified LaTeX exposes mathematical text and structure that software can search, quote, compare, and parse; the scan alone exposes only page images. Converting that LaTeX mathematics into checked Lean statements and proofs is a later formalization task and is not mechanical. The LaTeX nevertheless makes definitions, theorem statements, proofs, notation, cross-references, and source locations available to a person or AI system for dependency analysis, library comparison, and bounded Lean work.

Possible source corpora include transcribed works by Emmy Noether, James Joseph Sylvester, and other authors represented in the source archive. Naming a corpus is not a claim that its results are absent from Mathlib. Every proposed theorem first needs a gap audit against one exact Mathlib commit.

The machine-readable intake is [`catalog/formalize.json`](../catalog/formalize.json), validated by [`schemas/formalization-intake.schema.json`](../schemas/formalization-intake.schema.json). Its build state, source correspondence, Mathlib audit, and packet admission are separate fields. No generic “verified” label is used to collapse those checks.

## Current external intake

| Source | Exact snapshot | What was reproduced | Material limitation |
|---|---|---|---|
| [`sneed-and-feed/lean-theorems-1`](https://github.com/sneed-and-feed/lean-theorems-1) | Commit `6cf9ce44c1a8281699fa2f3128a764e0c347e7f6`; tree `eee97092915b388bf4b30bcdf60c5ad2201af133`; 36 Git-tree files / 592,129 bytes | The default target covers 29 of 30 Lean files under Lean `v4.34.0-rc1` and Mathlib `20bc12820422504f9e52ee6caebf8182a9015336` | Four `sorry` tokens exist. `ColorfulHelly.lean` is excluded from the default target and fails targeted compilation. The upstream claim that the core build has no incomplete goals is therefore false. |
| [Classical Mathematics Lean 4 Formalization Sidecars](https://zenodo.org/records/21129946) | DOI `10.5281/zenodo.21129946`; ZIP 9,834 bytes; SHA-256 `E9E494210774F814505CEC76F5AA5F2D6C8309EC46EA8B1A70CB77B070691FA9` | All four downloaded Lean sidecars compile individually under Lean `v4.31.0` and Mathlib `fabf563a7c95a166b8d7b6efca11c8b4dc9d911f`; the 13 advertised non-self member hashes replay | These are small Noether, Steinitz, Weber, and Jordan anchors. They contain no Desargues or Sylvester material and no historical statement-correspondence review. |

### Desargues intake

- `desargues_vector` is a review candidate: it compiles without a placeholder in the named declaration, but proves an algebraic identity for stipulated vectors rather than the full geometric side-intersection and collinearity statement.
- `DesarguesProjective.desargues_projective_plane` unwraps an `IsDesarguesian` assumption; it does not establish Desargues's theorem from more primitive plane axioms.
- `DesarguesProjective.desargues_dual_projective_plane` ends in `sorry`. The projective item is unfinished and cannot become runnable.

### S-named intake found in the snapshot

The catalog records separate rows for Sylvester–Gallai, Schur, Sperner in dimensions 1–3, Erdős–Szekeres, Sarkaria–Tverberg, the Erdős–Rényi–Sós friendship and windmill results, Székely's crossing-lemma amplification, Szemerédi–Trotter, the Schoenberg-linked Cauchy arm lemma, Suk and Szekeres–Peters literature leads, and the Steinitz sidecar. Sylvester–Gallai is the strongest direct candidate for the first source-to-statement review. The other rows retain their actual restrictions, assumed intermediate bounds, citation-only status, or missing correspondence checks.

## Proposed workflow

1. Select one exact theorem, lemma, definition cluster, or short dependency chain from a verified transcription. Record the author, work, edition, section, source-language text, translation when used, and exact file hashes.
2. State the mathematical content in current terminology without erasing the historical statement. Record every change of notation, hypothesis, scope, or level of generality.
3. Search the pinned Mathlib documentation and source. Classify the item as already present, present in greater generality, missing a prerequisite, suitable for a standalone project, or a plausible Mathlib contribution.
4. Create a small Lean project pinned to an exact Lean toolchain and Mathlib commit. Formalize dependencies before the target result and keep each declaration traceable to its source location.
5. Compile the project, run relevant linters and tests, and record the exact commands, commits, toolchain, imports, warnings, and results.
6. Require a person who understands both the mathematics and the Lean code to review the statement, dependency choices, proof, attribution, and library integration. Model agreement is not independent review.
7. If the result fits Mathlib, discuss a substantial new theory with the community before opening a pull request. Otherwise retain it in a clearly maintained standalone repository that depends on Mathlib.

## Proposed packet contents

A runnable packet should contain:

- an exact source receipt and the relevant machine-readable LaTeX excerpts;
- a theorem inventory with source locations and dependency edges;
- a gap report tied to one Mathlib commit, including possible existing declarations and generalizations;
- a pinned Lean project with one bounded target;
- statement, proof, build, lint, and test receipts;
- a ledger separating source mathematics, modern restatement, formal statement, implementation choices, unresolved interpretation, and reviewer findings; and
- cumulative checkpoints so another contributor can reproduce or continue the work.

The gap report matters even when no new theorem is added. Finding that a historical result already exists under a different name or in greater generality produces a useful source-to-library map and prevents duplicate formalization.

## Mathlib contribution route

Mathlib accepts contributions through GitHub pull requests. Its current contributor guide recommends using a fork, developing on a branch, building the affected files, and following its naming, style, and documentation rules. Larger or uncertain proposals should be discussed in the `#mathlib` Lean Zulip channel; material outside Mathlib's scope may be better maintained in a standalone repository that uses Mathlib as a dependency.

The official guidance also sets a strict boundary for AI-assisted contributions:

- the human contributor must understand and be able to justify all submitted mathematics, design decisions, and Lean code;
- AI use must be disclosed in the pull-request description, with the prescribed `LLM-generated` label when substantial;
- GitHub and Zulip discussion must be written by the contributor rather than generated by an AI system; and
- unreviewed model output must not be sent upstream in bulk.

The Commons should therefore treat upstream submission as the last optional step, not the automatic destination of every packet. A locally verified formalization may still be useful even when it is historical, author-specific, incomplete, or unsuitable for Mathlib.

Official references:

- [Contributing to Mathlib](https://leanprover-community.github.io/contribute/index.html)
- [Git guide for Mathlib contributors](https://leanprover-community.github.io/contribute/git.html)
- [Mathlib repository and build instructions](https://github.com/leanprover-community/mathlib4)
- [Mathlib pull-request review guide](https://leanprover-community.github.io/contribute/pr-review.html)

## Next implementation task

The intake schema and fail-closed catalog validator now exist. The next step is one small pilot with a short dependency chain and an independently checked transcription—preferably Sylvester–Gallai or one Noether anchor. It must complete source tracing, a pinned Mathlib gap audit, Lean compilation, statement-correspondence review, and cumulative handback before any packet is labeled runnable. It should not begin with an author-wide corpus or advertise an upstream contribution before the gap and fit reviews are complete.
