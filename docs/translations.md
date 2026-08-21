# Global open-textbook translation lane

Open mathematical education is unevenly distributed by language. This lane turns lawful, source-available university and pre-university textbooks into bounded translation jobs that a contributor can run with any capable local or hosted agent.

The aim is not to prescribe one language or one model. Choose a useful language that does not yet have a maintained edition, explain the educational need, and preserve an exact source and license boundary. Local educators and learners are better evidence of priority than raw speaker counts alone.

## What qualifies

A translation candidate needs all of the following:

- a distinct curricular role;
- official editable semantic source, not only a PDF;
- explicit permission for derivative translations;
- a reproducible build path;
- a bounded edition and component inventory; and
- enough exercises, examples, and supporting material for its declared teaching role.

“Free to read” is not a license. `ND` material is not translated. CC BY, BY-SA, BY-NC-SA, GFDL, Apache, MIT, and mixed-component works keep their own notices and restrictions; they are never flattened into one blanket license. Teacher-gated solutions and unlicensed third-party media stay excluded.

## Strong current starting points

The machine catalog separates reported current production, existing editions, source-ready candidates, optional specializations, donors, references, and rejected sources. Its two extraction snapshots are hash-identified but not public in this repository, so every row is discovery/status metadata until its source, license, edition, components, and build are independently frozen. Particularly reusable public foundations include:

- Open Logic, whose configurable LaTeX build and existing language editions provide a strong modular pattern;
- *Applied Combinatorics* (PreTeXt, CC BY-SA 4.0);
- *Yet Another Introductory Number Theory Textbook* (LaTeX, CC BY-SA with retained upstream attribution);
- *Open Optimization Book 1* (LaTeX/TikZ/Python, CC BY-SA text and MIT code);
- *Mathematics in Lean* (Lean and generated readers, Apache-2.0);
- GVSU's inquiry-based topology text, Petrunin's geometry text, and Erdman's functional-analysis text after their recorded build and component gates close; and
- other selected OpenStax, CLP, Hefferon, Lebl, Judson, Grinstead–Snell, OpenIntro, and numerical-analysis works under their exact per-title license boundaries.

The Stacks Project remains a downstream reference and synchronization target, not a cover-to-cover translation assignment.

## Workflow

1. Freeze the exact repository URL, commit/tag/tree, archive and reader hashes, license version, included assets, toolchain, and baseline build.
2. Census chapters, pages, exercises, hints, answers, figures, code, identifiers, cross-references, and third-party components.
3. Declare one target language, one bounded edition, a first complete unit, and a public continuation cursor.
4. Translate in source order while preserving stable IDs, formula semantics, exercises, solutions, assets, code, and logical force.
5. Maintain a terminology ledger with preferred, variant, and rejected terms plus scope and evidence.
6. Keep source, mathematical, language, exercise, build, accessibility, and visual QA separate.
7. Build a standalone monolingual edition. HTML, EPUB, print, audio, and accessibility derivatives are additive; a bilingual reader is not the primary edition.
8. Return cumulative state and exact manifests at every boundary.
9. Run an independent cold audit, record failures and reversals, and publish only a coherent versioned checkpoint.

Download the reusable translation kit from the current Commons job-library release. It is model-agnostic and deliberately separates source intake, production, QA, and release evidence.
