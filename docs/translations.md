# Translation

Many people cannot study in the language they understand best. [UNESCO reports that 40% of people globally lack access to education in a language they speak and understand fluently](https://www.unesco.org/en/languages-education). If you have spare AI compute, you can help by translating an educational work into a language that needs it.

Choose an openly licensed or noncommercially licensed source whose terms permit adaptations; choose the exact target language, locale, script, and written standard; and run the [generic translation starter](translate-v9.md) with any capable local or hosted model. The result should be a readable monolingual edition, editable source, a source record, and reproducible checks. The [87-page research report *Allocating AI Translation Compute for Marginal Educational Access*](https://kokunoyumeto.github.io/modern-latex-manuscripts/interlanguage/allocating-ai-translation-compute/) gives a fuller evidence-based account of language access, candidate selection, and compute allocation.

The works below are examples, not a closed list. A contributor may translate another textbook, course, reference work, or set of lecture notes under any open or noncommercial license that permits adaptations.

## What may be translated

| Source terms | What to do |
|---|---|
| Open license | Preserve the author, source, license, and required notices. Follow the license's terms for adaptations. |
| ShareAlike | Publish the translated adaptation under the required compatible ShareAlike license and preserve attribution. |
| Noncommercial license permitting adaptations, including NC-SA | Distribute the translation noncommercially. Do not sell it or authorize commercial reuse; preserve attribution and any ShareAlike requirement. A no-derivatives term does not permit a translation. |
| Mixed text, figures, code, or media | Keep each component's attribution and license notice. Do not assume one license silently replaces the others. |

The source's stated terms control. The portal records them so a contributor can preserve them in the returned edition.

## Start a translation

1. Choose a work and a target language. Prefer a language and subject for which learners lack suitable material, but any useful language is welcome.
2. Download the [generic v9 starter](translate-v9.md). For local use, open the extracted directory and paste `LOCAL.md`; for a hosted system, upload the ZIP and paste `WEB.md`.
3. Give the system the exact source revision. Keep the source edition and translated edition separate and monolingual. Preserve formulas, figures, examples, exercises, answers, and attribution.
4. Work in bounded units and return cumulative source, readable output, manifests, terminology and correction ledgers, QA results, and the exact continuation point.
5. Publish or return the complete checkpoint so another contributor can inspect it, correct it, or continue it without restarting.

The accompanying research report models one 120,083-source-token formal-reasoning edition at 912,737 low-workflow tokens, 4,073,049 base-workflow tokens, and 18,664,571 high-workflow tokens. Those are planning scenarios, not a promise for every book; length, figures, exercises, and QA depth change the cost. They show that a serious bounded edition can be a practical use of spare compute.

## Forty concrete mathematics examples

The [Program Matematika Indonesia learner hub](https://kokunoyumeto.github.io/program-matematika-indonesia/) applies this approach to 40 course roles. Its current evidence records 21 learner-ready roles across 20 complete public editions and 19 active or partial roles. These are equal-role counts, not a percentage of all pages or all work. The overview is useful for navigation, but some detailed progress and version text lags the individual edition repositories; follow the linked edition for its newest checkpoint.

| Subject | Source material | Indonesian state |
|---|---|---|
| Prealgebra and quantitative foundations | OpenStax *Prealgebra 2e* | Complete public edition |
| Elementary algebra | OpenStax *Elementary Algebra 2e* | Active or partial |
| Intermediate algebra | OpenStax *Intermediate Algebra 2e* | Active or partial |
| Precalculus and trigonometry | OpenStax *Precalculus 2e* | Active or partial |
| Proof, logic, and discrete structures | *Discrete Mathematics: An Open Introduction* | Complete public edition |
| Differential calculus | CLP-1 textbook and problem book | Complete public edition |
| Integral calculus | CLP-2 | Active or partial |
| Linear algebra | Hefferon, *Linear Algebra* | Complete public edition |
| Multivariable calculus | CLP-3 | Active or partial |
| Vector calculus | CLP-4 | Complete public edition |
| Ordinary differential equations and dynamical systems | Lebl course family | Active or partial |
| Mathematical computing and reproducible experiments | Original/open course framework | Complete public edition |
| Probability | Grinstead–Snell, *Introduction to Probability* | Complete public edition |
| Applied statistics and data analysis | *OpenIntro Statistics* | Active or partial |
| Real analysis I | Lebl, *Basic Analysis I* | Complete public edition |
| Real analysis II | Lebl, *Basic Analysis II* | Active or partial |
| Abstract algebra I | Judson, *Abstract Algebra: Theory and Applications* | Complete public shared edition |
| Abstract algebra II | Judson, *Abstract Algebra: Theory and Applications* | Complete public shared edition |
| Complex analysis | Lebl complex-analysis corpus | Active or partial |
| Number theory and cryptology | Poritz, *Yet Another Introductory Number Theory Textbook* | Complete public edition |
| Applied combinatorics | Keller–Trotter, *Applied Combinatorics* | Complete public edition |
| Mathematical logic, set theory, and computability | Open Logic | Complete public edition |
| Point-set topology | GVSU/PreTeXt topology corpus | Active or partial |
| Euclidean, affine, projective, and non-Euclidean geometry | Petrunin, *The Euclidean Plane and Its Relatives*, plus workbook | Complete public main edition |
| Numerical analysis | *Tea Time Numerical Analysis* | Complete public edition |
| Mathematical modeling and nonlinear dynamics | Lega plus computational material | Complete public edition |
| Linear and integer optimization | *Open Optimization Book 1* plus laboratories | Complete public edition |
| Mathematical statistics | Penn STAT 415, Random, and an original companion | Active or partial |
| Measure and integration | Fremlin, *Measure Theory*, Volumes 1–2 | Active or partial |
| Functional analysis | Erdman, *Functional Analysis and Operator Algebras* | Complete public edition |
| Measure-theoretic probability and stochastic processes | Random and QuantEcon sources plus bridges | Active or partial |
| Partial differential equations | Dionne plus FEniCSx and mastery material | Active or partial |
| Smooth manifolds and differential geometry | Brenner course | Active or partial |
| Algebraic topology | Roberts plus Fomberg | Active or partial |
| Graduate algebra | Wen-Wei Li, Volume 1, plus selected teaching material | Active or partial |
| Category theory and homological methods | Wen-Wei Li, Volume 2 | Active or partial |
| Advanced optimization and convex analysis | Habring plus Becker | Complete public edition |
| Algebraic geometry | Brenner's algebraic-curves and sheaf/cohomology courses | Active or partial overall |
| Formalized mathematics in Lean | *Mathematics in Lean* | Complete public edition |
| Research reading and reproducible mathematical work | Original/open course with Turing Way and PyRSE inputs | Complete public edition |

The [machine-readable education catalog](../catalog/edu.json) carries all 40 rows, semantic public IDs, their original source-project IDs, the 21/19 state partition, evidence dates, collection links, and the freshness limitation.

### A Wikimedia course translated into Indonesian

Holger Brenner's German Wikiversity course [*Algebraische Kurven (Osnabrück 2025–2026)*](https://de.wikiversity.org/wiki/Kurs:Algebraische_Kurven_(Osnabr%C3%BCck_2025-2026)) lists 30 lectures and 30 worksheets under Creative Commons Attribution–ShareAlike terms. A [complete public 30-unit Indonesian edition](https://github.com/KokunoYumeto/algebraic-geometry-bridge-id) uses the 2025–2026 course for Units 1–23 and the [official 2012 course](https://de.wikiversity.org/wiki/Kurs:Algebraische_Kurven_(Osnabr%C3%BCck_2012)) for Units 24–30, with the two source boundaries labeled separately. It includes a web reader, PDF, editable source, exercises, available solutions, media attribution, and reproducibility records. The larger two-course algebraic-geometry bridge continues; completion of this volume does not imply that the second volume is complete.

This is a reusable pattern. A contributor can choose another openly licensed Wikiversity, Wikibooks, OpenStax, Open Logic, or university course; freeze one exact source revision; translate it into a useful language; preserve the license and component notices; and return a monolingual edition with checks.

The 40 rows above are Indonesian curriculum roles. The 29 rows below are a different, release-bound v9 index of source works used by the generic starter. Do not add the two counts: one source can support several course roles, and some roles combine multiple sources or original material.

## Download a workflow

| Work | Status | What the status means |
|---|---|---|
| Open Logic Text | **Self-contained packet** | [Download `openlogic-v1.zip`](https://github.com/KokunoYumeto/mathematics-commons-pilot/releases/download/translate-openlogic-v1/openlogic-v1.zip) and verify 1,921,531 bytes / SHA-256 `C91EFD16C6DCF22DAEAFDBDC7F544A9E07C9B9C3BA04CE000BFCD933B52E9B8A`. The exact source, admission receipt, and anonymous readback are recorded below. |

The [generic v9 starter](translate-v9.md) is a **runnable translation workflow** for every non-reference source row whose `workflow_startability` is `starter_available` or `source_bound_packet`. It contains no source work: the contributor supplies or obtains the exact source, or verifies the separately published source-bound packet, records its identity and distribution note, and then begins the bounded translation. A `jobs[].state` of `runnable` has a narrower meaning: it says that this repository already provides a self-contained packet with a public release, byte/SHA-256 identity, and anonymous readback. The packet state is evidence about the archive, not a judgment about whether a contributor may run the workflow with source material already in hand.

## Browse the 29 works

The topics below are navigation aids. They do not imply a curriculum, priority order, or exclusive claim on a work.

| Topic | Works |
|---|---|
| Foundations and school algebra | OpenStax *Prealgebra 2e*; OpenStax *Elementary Algebra 2e*; OpenStax *Intermediate Algebra 2e*; OpenStax *Precalculus 2e* |
| Calculus, analysis, and differential equations | CLP Calculus 1–4 and problem books; Lebl analysis volume (exact title unresolved); Lebl ordinary differential equations volume (exact title unresolved); Lebl complex analysis volume (exact title unresolved); Victor Ivrii, *Partial Differential Equations*; *Partial Differential Equations — Dionne Unit 1* (full bibliographic identity unresolved) |
| Linear algebra, abstract algebra, and number theory | Hefferon, *Linear Algebra*; Judson, *Abstract Algebra*; *Yet Another Introductory Number Theory Textbook*; Wen-Wei Li, *Methods of Algebra*, Volume 1; Wen-Wei Li, *Methods of Algebra*, Volume 2 |
| Probability and statistics | Grinstead–Snell, *Probability*; *OpenIntro Statistics* |
| Discrete mathematics and combinatorics | DMOI4; *Applied Combinatorics* |
| Logic and formal mathematics | *Open Logic Text*; *Mathematics in Lean* |
| Geometry, topology, manifolds, and algebraic geometry | Steven Schlicker, *Topology: An Inquiry-Based Approach*; Anton Petrunin, *Euclidean Plane and Its Relatives*; *AlgebraicTopology2019* |
| Numerical mathematics, computing, optimization, and modeling | *Tea Time Numerical Analysis*; *Open Optimization Book 1*; MIT OpenCourseWare 6.253; *Mathematical Computing and Reproducible Experiments* |
| Functional analysis and operator theory | John M. Erdman, *Functional Analysis and Operator Algebras: An Introduction* |
| Research and assessment infrastructure | No individual work is currently listed; see the resources below. |

The 29 listed works are source scopes, not claims of completed editions. Their release-bound v9 records preserve the source notes available when that starter was built. Those notes are evidence, not permission gates: a contributor may start with any open or adaptation-permitting noncommercial source and preserve its actual terms.

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

Each component keeps its own source, license, and notice information. A contributor may use a component or collection as a bounded starting point and should carry those notices into the returned package. The Stacks Project is a semantic reference, not a proposal to translate it wholesale.

## Known public translation editions

This table includes dated public evidence. A repository identity establishes that an edition exists; it does not establish whole-work completion, exact source lineage, or independent QA.

| Work | Language | Public evidence | What has and has not been verified |
|---|---|---|---|
| Open Logic Text | Portuguese | [OpenLogic-pt](https://github.com/OpenLogicProject/OpenLogic-pt), observed 2026-08-22 at commit [`51c2271`](https://github.com/OpenLogicProject/OpenLogic-pt/tree/51c227190f56bae45d19a85747fc031de430bd3c) | The repository identity and its description as a Portuguese translation were verified. Whole-work completion, its exact relationship to a particular source edition, and independent translation QA were not established. |

Parallel translations are welcome when contributors identify them clearly and declare overlap. A repository identity is evidence that an edition exists; it is not by itself evidence of completeness or review.

### Public Indonesian reader PDFs

The [Indonesian Mathematics — Reader PDFs collection](https://doi.org/10.6084/m9.figshare.c.8668413.v25) contains nine public PDFs. Each file was anonymously downloaded and matched its recorded byte length and SHA-256. This proves the identity of the public PDF only. Whole-work coverage, exact source lineage, and independent translation QA remain unassessed unless a later row supplies that evidence.

| Work | Public reader | Exact bytes |
|---|---|---:|
| *Applied Combinatorics* | [10.6084/m9.figshare.33314772.v2](https://doi.org/10.6084/m9.figshare.33314772.v2) | 7,487,198 |
| *Mathematics in Lean* | [10.6084/m9.figshare.33314793.v2](https://doi.org/10.6084/m9.figshare.33314793.v2) | 1,239,371 |
| *Euclidean Plane and Its Relatives* | [10.6084/m9.figshare.33314706.v2](https://doi.org/10.6084/m9.figshare.33314706.v2) | 1,888,763 |
| *Yet Another Introductory Number Theory Textbook* | [10.6084/m9.figshare.33314736.v2](https://doi.org/10.6084/m9.figshare.33314736.v2) | 962,527 |
| *Tea Time Numerical Analysis* | [10.6084/m9.figshare.33314724.v2](https://doi.org/10.6084/m9.figshare.33314724.v2) | 8,202,476 |
| Judson, *Abstract Algebra: Theory and Applications* | [10.6084/m9.figshare.33314754.v2](https://doi.org/10.6084/m9.figshare.33314754.v2) | 1,841,875 |
| *Mathematical Computing and Reproducible Experiments* | [10.6084/m9.figshare.33314796.v1](https://doi.org/10.6084/m9.figshare.33314796.v1) | 502,373 |
| Wen-Wei Li, *Methods of Algebra*, Volume 2 | [10.6084/m9.figshare.33314775.v2](https://doi.org/10.6084/m9.figshare.33314775.v2) | 683,385 |
| *Partial Differential Equations — Dionne Unit 1* | [10.6084/m9.figshare.33314739.v1](https://doi.org/10.6084/m9.figshare.33314739.v1) | 702,567 |

Exact filenames, SHA-256 values, download URLs, collection identity, and readback results are in the [reader receipt](../catalog/receipts/id-readers.json) and the corresponding `translation_editions` rows in the machine catalog.

### Historical reports without public identities

Thirteen Indonesian-edition reports were recorded on 21 August 2026. They are retained to prevent accidental silent duplication, but the reports themselves do not establish public identities, exact scopes, dates of observation, owners, or review states. Judson and *Tea Time Numerical Analysis* now also have public reader rows above; their relationship to the older reports has not been established. “Active,” “complete,” and “planned” below describe only the report at the recording date; they are not current status claims.

| Reported state at recording | Works |
|---|---|
| Reported active | OpenStax *Prealgebra 2e*, *Elementary Algebra 2e*, and *Intermediate Algebra 2e*; CLP Calculus series; Hefferon *Linear Algebra*; unresolved Lebl analysis volume; Judson *Abstract Algebra*; Grinstead–Snell *Probability*; *Tea Time Numerical Analysis* |
| Reported complete | DMOI4; *Open Logic Text* |
| Reported planned | Unresolved Lebl ordinary-differential-equations volume; unresolved Lebl complex-analysis volume |

The exact per-work rows and evidence limitations are in `translation_editions` in the machine catalog. Historical-report rows do not establish a current production lane or reusable public edition. Public-reader rows establish exact available PDF bytes, but not completion, source lineage, or review.

## Choose a language

Any language is welcome. Record the exact locale, script, written or orthographic standard, intended learners, and existing editions. If a suitable translation already exists, you can improve it or declare a parallel edition rather than silently duplicating it.

The figure relevant to UNESCO's roughly 40% estimate is 97, not 96. [Walter and Benson's Table 14.2](https://doi.org/10.1017/CBO9780511979026.017) reports **97 languages with more than 10 million speakers**: 52 used in education and 45 not used. Across all language-size categories, their population totals are 3,741,110,588 for languages used in education and 2,300,263,716 for languages not used, or 38.075% without first-language educational access when rounded to three decimals. UNESCO later rounded the global estimate to about 40%. The table is aggregate and does not print a named list of the 97 languages, so it cannot honestly be turned into an official 97-language translation queue.

Use current local evidence to choose a target: language-of-instruction gaps, university-material availability, learner demand, local written standards, and what has already been translated. The [educational-access report](https://kokunoyumeto.github.io/modern-latex-manuscripts/interlanguage/allocating-ai-translation-compute/) provides a documented candidate register and allocation method. A later literacy study involving 96 alphabetic-script assessment languages is separate evidence, not the source of the 40% estimate.

## Workflow, distribution, and packet states

- **Identity unresolved:** the exact work or edition has not been identified.
- **Starter available:** the generic translation workflow can be started or continued for this work. The exact source may be supplied by the contributor or acquired as the first step.
- **Reference only:** the row is a component, collection, or semantic reference rather than a standalone work.
- **Prepared, not public:** a packet has been assembled but does not yet have a verified public release.
- **Source-bound packet:** a self-contained packet is available and its release, byte length, SHA-256, and public readback are recorded.

The release-bound v9 machine catalog retains older readiness and distribution fields for reproducibility. They do not gate a translation workflow. Follow the source's stated terms: noncommercial means no commercial distribution, and an unclassified catalog note means only that v9 did not normalize the terms—not that translation is prohibited.

## Run a published job

1. Select a source row whose `workflow_startability` is `starter_available` or `source_bound_packet`.
2. If it is `source_bound_packet`, download its ZIP from the recorded release and verify its byte length and SHA-256 value. Otherwise download the [generic v9 starter](translate-v9.md).
3. For local use, open the starter directory and paste `LOCAL.md`. For hosted use, upload the starter ZIP and paste `WEB.md`.
4. State the target language, locale, script, orthographic standard, and intended learners.
5. Preserve the source exactly. Produce a standalone target-language edition, not a facing-page substitute.
6. Return cumulative editable source, a readable build, terminology and correction ledgers, checkpoint state, manifest, QA evidence, unresolved items, and the exact continuation point.
7. Have another person or system replay the source, build, and checks when possible. This strengthens the result but does not block a useful, clearly labeled checkpoint from being returned or published.

Any system capable of preserving the files and following the ordered contract may be used. The output format and evidence requirements do not depend on one vendor.

## Machine interface

- [Translation catalog](../catalog/translations.json): authoritative works, resources, topics, source editions, translation editions, jobs, evidence, and exclusions.
- [Education translation catalog](../catalog/edu.json): plain workflow, source-term rules, language-access evidence, research-paper identity, and the current 40-work Indonesian example set.
- [Compact work index](../kits/translate/WORKS.json): the current work, workflow, language, and distribution snapshot shipped in the v9 translation starter.
- [Catalog schema](../schemas/translation-catalog.schema.json): machine-validation contract.
- [Choice schema](../schemas/translation-choices.schema.json) and [source-state schema](../schemas/translation-source.schema.json): downloaded workflow contracts.
- [Open Logic asset manifest](../catalog/assets/openlogic.json), [admission receipt](../catalog/receipts/openlogic.json), and [public readback](../catalog/openlogic-rb.json): exact self-contained-packet evidence.
- [Indonesian reader receipt](../catalog/receipts/id-readers.json): exact collection, DOI, filename, byte, SHA-256, and anonymous-readback evidence for nine public PDFs.

Consumers should read status from the catalog, not infer it from prose, filenames, or the existence of a release page.

## Other Commons portals

- [Transcription jobs](run.md): admitted runnable packet envelopes for diplomatic transcription and separate modern editions.
- [Formalization](formalize.md): intake and review for converting mathematical statements into checkable formal developments.
- [Open Problem Workbench](workbench.md): source and evidence organization for conjectures and open problems; no problem packet is currently admitted as runnable.

The [older-manuscript adoption board](adopt.md) is a separate archive and coordination surface. Its aggregate language tags do not establish coverage for the educational works listed here.
