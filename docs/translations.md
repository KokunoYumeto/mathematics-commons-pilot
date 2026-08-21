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

The machine catalog separates reported current production, existing editions, source-ready candidates, optional specializations, donors, references, and rejected sources. Most rows derive from two hash-identified extraction snapshots that are not public in this repository, so they remain discovery/status metadata until their source, license, edition, components, and build are independently frozen. R020 is different: its Open Logic repository, commit, tree, CC BY 4.0 license file, root README, `.gitmodules`, and `doc` gitlink have been independently verified against public upstream bytes. R020 still is not runnable because its submodule/component census and baseline build have not closed.

R020 does not verify or replace R013. R013 preserves a separate snapshot report that a configured Indonesian edition already exists; its exact public edition identity remains unverified.

Particularly reusable public foundations include:

- Open Logic core source (R020), pinned at commit `1e960beff9ed7835bf3e3f1335e21af3439cd107` and tree `45cad6b3bf0dd96985a7b3d1dc5c343984b0e1c8`, whose configurable LaTeX root is a strong modular candidate once its pinned `doc` submodule and baseline build are fully replayed;
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
