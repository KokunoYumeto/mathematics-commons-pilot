# Translation

This portal helps people use local or hosted AI systems to produce inspectable monolingual translations of open mathematical works. The catalog is a non-exclusive set of useful suggestions, not a fixed curriculum. You may choose a listed work or propose any other mathematical work whose exact source and permission for translation derivatives can be verified.

No listed title is automatically ready to translate. Before production, the source edition, immutable bytes or commit, license, third-party components, editable source, and unchanged baseline build must be recorded. Unknown language coverage means unknown; it never means that no translation exists.

## Start a project

1. Choose a work by title, creator, or semantic key in [`catalog/translations.json`](../catalog/translations.json), or propose another openly licensed mathematical work.
2. Check that exact work for verified editions and reported but unverified editions. Do not use aggregate language counts as work-level coverage.
3. Download the [`translation-starter-v5` release](https://github.com/KokunoYumeto/mathematics-commons-pilot/releases/tag/translate-v5).
4. For a local agent, paste `LOCAL.md`. For a hosted web agent, upload the ZIP and paste `WEB.md`.
5. State the exact target language, locale, script, orthographic standard, intended learners, and available reviewers.
6. Translation begins only after the agent completes the source, rights, component, and baseline-build preflight in `SOURCE.json`.

The starter contains no textbook or completed translation. Each bounded unit returns cumulative source, reader, ledgers, checkpoint, and manifest so that another contributor can inspect, replay, correct, or continue the work.

## How the catalog is organized

The public key is a readable semantic slug such as `openstax-prealgebra-2e` or `openlogic-core`. Older `R…` and `O…` values survive only as `legacy_id` provenance from a non-public planning snapshot. They are not work identifiers and are not used in the tables below.

Each machine row separates facts that the previous catalog conflated:

- `catalog_role`: individual work, series, composite curriculum idea, component, course, reference, infrastructure, source project, or adaptation;
- `known_editions`: work-specific language, state, scope, and evidence status;
- `source_evidence_status`: whether the public source boundary was independently replayed or merely reported;
- `translation_readiness`: whether source preflight is required or the row is not a standalone translation job; and
- `preflight_needed`: the exact remaining source, rights, component, or build work.

There is no `current production` label. Earlier uses of that phrase described reported Indonesian task activity in one coordination snapshot; they did not describe all translations of a work.

## Reported Indonesian activity

These reports come from a non-public coordination snapshot. They are useful leads, but their public edition identities have not been independently verified here. Other language coverage is unknown, not absent.

| Work | Reported language | Reported state | Public evidence state |
|---|---|---|---|
| OpenStax *Prealgebra 2e* | Indonesian | active | coordination report only |
| OpenStax *Elementary Algebra 2e* | Indonesian | active | coordination report only |
| OpenStax *Intermediate Algebra 2e* | Indonesian | active | coordination report only |
| CLP Calculus series and problem books | Indonesian | active | coordination report only |
| DMOI4 | Indonesian | complete/public reported | exact edition and license unresolved |
| Hefferon, *Linear Algebra* | Indonesian | active | coordination report only |
| Lebl analysis volume, exact title unresolved | Indonesian | active | coordination report only |
| Lebl ordinary differential equations volume, exact title unresolved | Indonesian | planned in the same lane | coordination report only |
| Lebl complex analysis volume, exact title unresolved | Indonesian | planned in the same lane | coordination report only |
| Judson, *Abstract Algebra* | Indonesian (`id-ID` reported) | active | coordination report only |
| Grinstead–Snell probability text | Indonesian | active | coordination report only |
| *Tea Time Numerical Analysis* | Indonesian | active | coordination report only |
| Open Logic, exact Indonesian edition unresolved | Indonesian | complete/public reported | exact edition, source, and license unresolved |

This table does not reserve these works or languages. A contributor may declare an independently useful parallel edition, but must preserve the other generation rather than overwrite it.

## Suggested individual works and source projects

These are suggestions only. `Preflight required` means that at least one source, rights, component, or build identity is still open; it is not a ban on adopting the work.

| Work | Creator or project | What is publicly recorded | Next useful step |
|---|---|---|---|
| OpenStax *Prealgebra 2e* | OpenStax | reported Indonesian activity; no exact public source/license bound here | freeze the exact edition, license, assets, and baseline build |
| OpenStax *Elementary Algebra 2e* | OpenStax | reported Indonesian activity; no exact public source/license bound here | freeze the exact edition, license, assets, and baseline build |
| OpenStax *Intermediate Algebra 2e* | OpenStax | reported Indonesian activity; media-rights questions recorded | freeze the exact edition and resolve every media component |
| OpenStax *Precalculus 2e* | OpenStax | repository handle recorded; full source/component boundary unresolved | verify the public repository, license, assets, and build |
| CLP Calculus 1–4 and problem books | CLP project | reported Indonesian activity; exact upstream and rights unresolved | freeze each volume and support book as a separately identified source |
| DMOI4 | exact expanded title/creators unresolved | Indonesian edition reported public | identify the work and exact edition before any new-language project |
| *Linear Algebra* | Jim Hefferon | reported Indonesian activity; exact upstream/license unresolved | bind textbook, answer book, labs, license, and build |
| Lebl analysis volume | Jiří Lebl; exact title unresolved | reported Indonesian activity | resolve the exact volume before treating it as a work choice |
| Lebl ordinary differential equations volume | Jiří Lebl; exact title unresolved | Indonesian planning report | resolve title, edition, source, and license |
| Lebl complex analysis volume | Jiří Lebl; exact title unresolved | Indonesian planning report | resolve title, edition, source, and license |
| *Abstract Algebra* | Thomas W. Judson | Indonesian locale work reported | bind exact upstream, license, diagrams, and baseline build |
| Probability text | Charles Grinstead and J. Laurie Snell | reported Indonesian activity | bind exact edition, source, license, exercises, and build |
| *OpenIntro Statistics* | OpenIntro | repository commit reported | independently replay source, data, figures, license, and build |
| *Applied Combinatorics* | Mitch Keller and contributors | repository commit and PreTeXt source reported | independently replay license, includes, assets, and build |
| *Yet Another Introductory Number Theory Textbook* | Jonathan Poritz | author-controlled download page recorded | hash the exact source assets and establish the derivative license |
| *Tea Time Numerical Analysis* | creators unresolved in current evidence | reported Indonesian activity and backend counts | identify the exact version, creators, source, license, and build |
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

UNESCO's [2025 multilingual-education report announcement](https://www.unesco.org/en/articles/new-unesco-report-calls-multilingual-education-unlock-learning-and-inclusion) reports that 40% of people lack access to education in a language they speak and understand fluently, more than a quarter-billion learners are affected, and only 351 of roughly 7,000 spoken or signed languages are used as a medium of instruction.

No official UNESCO list of 96 underserved languages was identified. The 96 figure appears to come from a different UNESCO statistic: roughly 3% of the world's population speaks 96% of its languages. The Commons will not label a numbered list as UNESCO's without an exact source. A Commons-maintained priority list is appropriate if it publishes its criteria and evidence for each language.

## Separate older-manuscript archive

The [interlanguage adoption snapshot](adopt.md) covers 78 rows of older mathematical manuscripts and research editions. Its aggregate tags include Arabic, German, English, Spanish, Persian, French, Indonesian, Interslavic, Italian, Japanese, Korean, Russian, Sanskrit, Ukrainian, Vietnamese, several Chinese conventions, mixed, and undetermined records.

Those counts are row presence in a separate corpus. They do not describe the educational works above and do not establish whole-work completion. Read the selected manuscript's own map before starting or duplicating work.

## Review and handback

Produce a standalone target-language edition, never a facing-page substitute. Preserve formulas, theorem structure, exercises, figures, code, stable identifiers, and accessibility semantics. Return cumulative source, reader, ledgers, checkpoint, manifest, build evidence, unresolved items, and continuation cursor after every bounded unit.

Another contributor should be able to obtain the same source bytes, replay the build and checks, compare the translation against the source, record exact defects, and continue from the checkpoint. Model agreement is not independent review.
