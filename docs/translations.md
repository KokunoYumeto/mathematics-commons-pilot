# Translation

This portal organizes open mathematical works that contributors can translate with local or hosted AI systems and then inspect through human and independent review. It separates individual works, supporting resources, exact source editions, known public translations, and downloadable jobs.

The catalog is a set of suggestions, not a restriction. Contributors may propose any other mathematical work when its exact source and the right to publish a translation can be verified. Unknown language coverage means unknown; it does not mean that no translation exists.

## Ready jobs

| Work | Status | What the status means |
|---|---|---|
| Open Logic Text | **Runnable** | [Download `openlogic-v1.zip`](https://github.com/KokunoYumeto/mathematics-commons-pilot/releases/download/translate-openlogic-v1/openlogic-v1.zip) and verify 1,921,531 bytes / SHA-256 `C91EFD16C6DCF22DAEAFDBDC7F544A9E07C9B9C3BA04CE000BFCD933B52E9B8A`. The exact source, admission receipt, and anonymous readback are recorded below. |

A job becomes **runnable** only when its public download, byte length, SHA-256 identity, and public readback are present in the machine catalog. The separate [generic v7 starter](translate-v7.md) helps with work selection and source preflight; it contains no source work and is not a runnable translation job. Its release is not complete until the public asset and anonymous readback exist.

## Browse the 27 works

The topics below are navigation aids. They do not imply a curriculum, priority order, or exclusive claim on a work.

| Topic | Works |
|---|---|
| Foundations and school algebra | OpenStax *Prealgebra 2e*; OpenStax *Elementary Algebra 2e*; OpenStax *Intermediate Algebra 2e*; OpenStax *Precalculus 2e* |
| Calculus, analysis, and differential equations | CLP Calculus 1–4 and problem books; Lebl analysis volume (exact title unresolved); Lebl ordinary differential equations volume (exact title unresolved); Lebl complex analysis volume (exact title unresolved); Victor Ivrii, *Partial Differential Equations* |
| Linear algebra, abstract algebra, and number theory | Hefferon, *Linear Algebra*; Judson, *Abstract Algebra*; *Yet Another Introductory Number Theory Textbook*; Wen-Wei Li, *Methods of Algebra*, Volume 1; Wen-Wei Li, *Methods of Algebra*, Volume 2 |
| Probability and statistics | Grinstead–Snell, *Probability*; *OpenIntro Statistics* |
| Discrete mathematics and combinatorics | DMOI4; *Applied Combinatorics* |
| Logic and formal mathematics | *Open Logic Text*; *Mathematics in Lean* |
| Geometry, topology, manifolds, and algebraic geometry | Steven Schlicker, *Topology: An Inquiry-Based Approach*; Anton Petrunin, *Euclidean Plane and Its Relatives*; *AlgebraicTopology2019* |
| Numerical mathematics, computing, optimization, and modeling | *Tea Time Numerical Analysis*; *Open Optimization Book 1*; MIT OpenCourseWare 6.253 |
| Functional analysis and operator theory | John M. Erdman, *Functional Analysis and Operator Algebras: An Introduction* |
| Research and assessment infrastructure | No individual work is currently listed; see the resources below. |

Most works still need source preflight. Their inclusion means that they may be useful translation candidates, not that their source packets or translations are complete.

## The 12 resources and collections

These entries are references, components, infrastructure, or proposed combinations. They are listed separately because they are not presently bounded cover-to-cover translation jobs.

| Topic | Resource or collection |
|---|---|
| Calculus, analysis, and differential equations | *Measure, Integration & Real Analysis* with Fubini–Tonelli material and Gautam Iyer's Math 720 notes |
| Probability and statistics | Dunn–Axelsen distribution theory with Spiegler statistical methods; Imperial probability notes with Siegrist, or MIT 6.436J with MIT 18.445 |
| Geometry, topology, manifolds, and algebraic geometry | Manifolds and differential-geometry collection; algebraic-geometry bridge using Brenner and MIT 18.725; Stacks Project reference |
| Numerical mathematics, computing, optimization, and modeling | Mathematical Python with *Research Software Engineering with Python*; nonlinear-dynamics and modeling collection; open-solver operations-research laboratory |
| Functional analysis and operator theory | Fubini–Tonelli real/functional-analysis source component |
| Research and assessment infrastructure | Cross-corpus assessment infrastructure; research-reading and reproducibility collection |

Each component must acquire its own exact source, license, component-rights record, and reproducible build before it can become part of a runnable job. The Stacks Project is a semantic reference, not a proposal to translate it wholesale.

## Known public translation editions

This table includes dated public evidence. A repository identity establishes that an edition exists; it does not establish whole-work completion, exact source lineage, or independent QA.

| Work | Language | Public evidence | What has and has not been verified |
|---|---|---|---|
| Open Logic Text | Portuguese | [OpenLogic-pt](https://github.com/OpenLogicProject/OpenLogic-pt), observed 2026-08-22 at commit [`51c2271`](https://github.com/OpenLogicProject/OpenLogic-pt/tree/51c227190f56bae45d19a85747fc031de430bd3c) | The repository identity and its description as a Portuguese translation were verified. Whole-work completion, its exact relationship to a particular source edition, and independent translation QA were not established. |

Parallel translations are welcome when contributors identify them clearly and declare overlap. A repository identity is evidence that an edition exists; it is not by itself evidence of completeness or review.

### Historical reports without public identities

Thirteen Indonesian-edition reports were recorded on 21 August 2026. They are retained to prevent accidental silent duplication, but their public identities, exact scopes, dates of observation, owners, and review states were not established. “Active,” “complete,” and “planned” below describe only the report at the recording date; they are not current status claims.

| Reported state at recording | Works |
|---|---|
| Reported active | OpenStax *Prealgebra 2e*, *Elementary Algebra 2e*, and *Intermediate Algebra 2e*; CLP Calculus series; Hefferon *Linear Algebra*; unresolved Lebl analysis volume; Judson *Abstract Algebra*; Grinstead–Snell *Probability*; *Tea Time Numerical Analysis* |
| Reported complete | DMOI4; *Open Logic Text* |
| Reported planned | Unresolved Lebl ordinary-differential-equations volume; unresolved Lebl complex-analysis volume |

The exact per-work rows and evidence limitations are in `translation_editions` in the machine catalog. No row above establishes a current production lane or a reusable public edition.

## Choose a language

Any language is welcome. A useful choice starts with a documented community need, an exact locale and script, a written or orthographic standard, intended learners, and people able to review the result.

UNESCO reported in 2025 that [40% of people globally lack access to education in a language they speak and understand fluently](https://www.unesco.org/en/articles/new-unesco-report-calls-multilingual-education-unlock-learning-and-inclusion). This is an education-language access estimate.

Separately, a [UNESCO Institute for Statistics report](https://www.uis.unesco.org/sites/default/files/medias/fichiers/2025/09/GAML11_2.2_UIS-Benchmarking-by-Language-Group-2025.04.28.pdf) cites a literacy study covering 96 alphabetic-script languages across 48 low- and middle-income countries. Those 96 assessment languages are useful concrete communities to consider, but they are not an official UNESCO translation-priority list and they are not the source of the 40% estimate. The exact labels, source, and limitations are recorded in the machine catalog.

Before starting, check whether a suitable edition already exists and whether a parallel effort would still be independently useful. Do not infer work-level coverage from a general language list.

## Source-preflight states

- **Identity unresolved:** the exact work or edition has not been identified.
- **Source preflight needed:** at least one required source, rights, component, editable-source, or baseline-build check remains open.
- **Supporting resource:** the entry is useful context or infrastructure but is not a standalone job.
- **Prepared, not public:** a packet has been assembled but does not yet have a verified public release.
- **Runnable:** the public packet and its readback are recorded and all required preflight gates pass.

The seven preflight checks are exact work identity, exact source-edition identity, immutable source bytes, permission to publish translations, rights for included components, editable source, and an unchanged baseline build. A title or repository URL alone does not pass these checks.

## Run a published job

1. Select a job whose status is **runnable** in the machine catalog.
2. Download its ZIP from the recorded release and verify its byte length and SHA-256 value.
3. For local use, extract the ZIP and follow `START.md` and `LOCAL.md`. For hosted use, upload the ZIP and follow `WEB.md`.
4. State the target language, locale, script, orthographic standard, intended learners, and available reviewers.
5. Preserve the source exactly. Produce a standalone target-language edition, not a facing-page substitute.
6. Return cumulative editable source, a readable build, terminology and correction ledgers, checkpoint state, manifest, QA evidence, unresolved items, and the exact continuation point.
7. Have another person or system replay the source, build, and checks. Agreement between models is not independent review.

Any system capable of preserving the files and following the ordered contract may be used. The output format and evidence requirements do not depend on one vendor.

## Machine interface

- [Translation catalog](../catalog/translations.json): authoritative works, resources, topics, source editions, translation editions, jobs, evidence, and exclusions.
- [Compact work index](../kits/translate/WORKS.json): work and resource projection for a downloaded translation kit.
- [Catalog schema](../schemas/translation-catalog.schema.json): machine-validation contract.
- [Choice schema](../schemas/translation-choices.schema.json) and [source-state schema](../schemas/translation-source.schema.json): downloaded workflow contracts.
- [Open Logic asset manifest](../catalog/assets/openlogic.json), [admission receipt](../catalog/receipts/openlogic.json), and [public readback](../catalog/openlogic-rb.json): exact runnable-job evidence.

Consumers should read status from the catalog, not infer it from prose, filenames, or the existence of a release page.

## Other Commons portals

- [Transcription jobs](run.md): verified bounded source packets for diplomatic transcription and separate modern editions.
- [Formalization](formalize.md): intake and review for converting mathematical statements into checkable formal developments.
- [Open Problem Workbench](workbench.md): source and evidence organization for conjectures and open problems; no problem packet is currently admitted as runnable.

The [older-manuscript adoption board](adopt.md) is a separate archive and coordination surface. Its aggregate language tags do not establish coverage for the educational works listed here.
