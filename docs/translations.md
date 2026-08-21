# Translation

This portal helps people use local or hosted AI systems to produce inspectable monolingual translations of open mathematical works. The catalog is a non-exclusive set of useful suggestions, not a fixed curriculum. You may choose a listed work or propose any other mathematical work whose exact source and permission for translation derivatives can be verified.

No listed title is automatically ready to translate. Before production, the source edition, immutable bytes or commit, license, third-party components, editable source, and unchanged baseline build must be recorded. Unknown language coverage means unknown; it never means that no translation exists.

## Start a project

1. Choose a work by title, creator, or semantic key in [`catalog/translations.json`](../catalog/translations.json), or propose another openly licensed mathematical work.
2. Check that exact work for verified editions and reported but unverified editions. Do not use aggregate language counts as work-level coverage.
3. Download the [`translation-starter-v6` release](https://github.com/KokunoYumeto/mathematics-commons-pilot/releases/tag/translate-v6).
4. For a local agent, paste `LOCAL.md`. For a hosted web agent, upload the ZIP and paste `WEB.md`.
5. State the exact target language, locale, script, orthographic standard, intended learners, and available reviewers.
6. Translation begins only after the agent completes the source, rights, component, and baseline-build preflight in `SOURCE.json`.

The starter contains no textbook or completed translation. Each bounded unit returns cumulative source, reader, ledgers, checkpoint, and manifest so that another contributor can inspect, replay, correct, or continue the work.

## How the catalog is organized

The public key is a readable semantic slug such as `openstax-prealgebra-2e` or `openlogic-core`. Historical planning keys survive only as machine provenance. They are not public work labels and are not used in the tables below.

Each machine row separates facts that the previous catalog conflated:

- `catalog_role`: individual work, series, composite curriculum idea, component, course, reference, infrastructure, source project, or adaptation;
- `known_editions`: work-specific language, state, scope, and evidence status;
- `source_evidence_status`: whether the public source boundary was independently replayed or merely reported;
- `translation_readiness`: whether source preflight is required or the row is not a standalone translation job; and
- `preflight_needed`: the exact remaining source, rights, component, or build work.

Unverified edition reports remain in the machine catalog so existing work is not silently lost or overwritten. They are not presented as a public production-status table. Recheck the selected work's current public editions before beginning, and preserve independently useful parallel generations when overlap is declared.

## Suggested individual works and source projects

These are suggestions only. `Preflight required` means that at least one source, rights, component, or build identity is still open; it is not a ban on adopting the work.

| Work | Creator or project | What is publicly recorded | Next useful step |
|---|---|---|---|
| OpenStax *Prealgebra 2e* | OpenStax | no exact public source/license boundary is bound here | freeze the exact edition, license, assets, and baseline build |
| OpenStax *Elementary Algebra 2e* | OpenStax | no exact public source/license boundary is bound here | freeze the exact edition, license, assets, and baseline build |
| OpenStax *Intermediate Algebra 2e* | OpenStax | exact source unresolved; media-rights questions recorded | freeze the exact edition and resolve every media component |
| OpenStax *Precalculus 2e* | OpenStax | repository handle recorded; full source/component boundary unresolved | verify the public repository, license, assets, and build |
| CLP Calculus 1–4 and problem books | CLP project | exact upstream and rights unresolved | freeze each volume and support book as a separately identified source |
| DMOI4 | exact expanded title/creators unresolved | work identity, source, and license unresolved | identify the work and exact edition before any new-language project |
| *Linear Algebra* | Jim Hefferon | exact upstream and license unresolved | bind textbook, answer book, labs, license, and build |
| Lebl analysis volume | Jiří Lebl; exact title unresolved | exact volume unresolved | resolve the exact volume before treating it as a work choice |
| Lebl ordinary differential equations volume | Jiří Lebl; exact title unresolved | title, edition, source, and license unresolved | resolve title, edition, source, and license |
| Lebl complex analysis volume | Jiří Lebl; exact title unresolved | title, edition, source, and license unresolved | resolve title, edition, source, and license |
| *Abstract Algebra* | Thomas W. Judson | exact upstream, license, diagrams, and build not yet bound | bind exact upstream, license, diagrams, and baseline build |
| Probability text | Charles Grinstead and J. Laurie Snell | exact edition, source, and license unresolved | bind exact edition, source, license, exercises, and build |
| *OpenIntro Statistics* | OpenIntro | repository commit reported | independently replay source, data, figures, license, and build |
| *Applied Combinatorics* | Mitch Keller and contributors | repository commit and PreTeXt source reported | independently replay license, includes, assets, and build |
| *Yet Another Introductory Number Theory Textbook* | Jonathan Poritz | author-controlled download page recorded | hash the exact source assets and establish the derivative license |
| *Tea Time Numerical Analysis* | creators unresolved in current evidence | exact version, creators, source, license, and build unresolved | identify the exact version, creators, source, license, and build |
| *Open Optimization Book 1* | Open Optimization project | repository commit; CC BY-SA text/figures and MIT code reported | replay components/build and replace or exclude commercial-only paths |
| *Mathematics in Lean* | Lean community | repository commit reported | freeze license, toolchain, dependencies, and an unchanged build |
| Open Logic core | Open Logic Project | exact root commit/tree and CC BY 4.0 independently verified | finish the submodule/component census and baseline build |
| *Topology: An Inquiry-Based Approach* | Steven Schlicker | public repository/commit and license reported | replay source, component licenses, and build |
| *Euclidean Plane and Its Relatives* | Anton Petrunin | public repository/commit and CC BY-SA 4.0 reported | replay source, components, fonts, and build |
| *Functional Analysis and Operator Algebras: An Introduction* | John M. Erdman | official title page verified; public source ZIP and CC BY-SA 4.0 reported | freeze ZIP bytes and close solution/production policy |
| *Partial Differential Equations* | Victor Ivrii | public source location and CC BY-SA 4.0 reported | freeze exact source, scope, figures, and build |
| *AlgebraicTopology2019* | David Michael Roberts | repository commit/tree and CC BY 4.0 reported | replay source, scope, components, and build |
| *Methods of Algebra*, Volumes 1 and 2 | Wen-Wei Li | commits and CC BY 4.0 reported; repository locator absent | identify the public repository, replay each volume, and freeze builds separately |
| MIT OCW 6.253 | MIT OpenCourseWare | course package and CC BY-NC-SA 4.0 reported | verify editable source and exact component boundary |

## Composite curriculum ideas

These are possible combinations, not single works. A contributor may adopt one component or propose a different combination. Each component needs its own source, license, and build record.

- Mathematical Python plus *Research Software Engineering with Python*.
- Sayama plus ModSimPy and an open ordinary-differential-equations project.
- Dunn–Axelsen distribution theory plus Spiegler statistical methods.
- Axler's *Measure, Integration & Real Analysis* plus Fubini–Tonelli and Gautam Iyer notes.
- Imperial or MIT measure-theoretic probability and stochastic-process materials.
- Smooth-manifold and differential-geometry materials from several open sources.
- Brenner plus MIT 18.725 as an algebraic-geometry bridge.
- MIT 18.821 plus selected reproducible-research materials.

The exact components, reported licenses, caveats, and suggested preflights are in the machine catalog.

## Supporting material, tools, and references

The Fubini–Tonelli component, Stacks Project reference, cross-corpus assessment design, and open-solver laboratory are useful supporting rows. They are not standalone cover-to-cover translation assignments. The Stacks Project should be linked semantically at selected tags rather than translated wholesale.

## Language choice

Translations into any language are welcome. Contributors are especially encouraged to choose languages for which communities document limited access to university-level mathematical material and can identify intended learners, a written standard, and reviewers.

UNESCO's [multilingual-education evidence](https://www.unesco.org/en/languages-education/need-know) repeats an estimate that up to 40% of people lack access to education in a language they speak or understand, says more than a quarter-billion learners are affected, and reports that only 351 of roughly 7,000 languages in current use serve as media of instruction.

A separate [UNESCO Institute for Statistics report](https://www.uis.unesco.org/sites/default/files/medias/fichiers/2025/09/GAML11_2.2_UIS-Benchmarking-by-Language-Group-2025.04.28.pdf) cites a 48-country literacy study covering 96 languages using alphabetic writing systems. It describes 75% of the assessments as conducted in a local or national language and 25% in English, French, Spanish, or Portuguese. The exact 96 labels from the cited study's Table S1 are recorded in `catalog/translations.json` under `language_priority.uis_96_language_study.language_labels`.

Those 96 labels are a useful concrete source of candidate language communities. They are not a ranking, a closed queue, or a finding that every listed language is underserved. Before starting, verify current educational need, the intended learners, the exact written standard, work-specific coverage, and available reviewers. Any other language remains welcome.

## Separate older-manuscript archive

The [interlanguage adoption snapshot](adopt.md) covers older mathematical manuscripts and research editions as a separate corpus. Its aggregate language tags are not coverage for the educational works above and do not establish whole-work completion. Read the selected manuscript's own map before starting or duplicating work.

## Review and handback

Produce a standalone target-language edition, never a facing-page substitute. Preserve formulas, theorem structure, exercises, figures, code, stable identifiers, and accessibility semantics. Return cumulative source, reader, ledgers, checkpoint, manifest, build evidence, unresolved items, and continuation cursor after every bounded unit.

Another contributor should be able to obtain the same source bytes, replay the build and checks, compare the translation against the source, record exact defects, and continue from the checkpoint. Model agreement is not independent review.
