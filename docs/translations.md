# Translation

This section lists mathematical works that may support new monolingual translations. It separates existing or active editions from unclaimed source candidates and rejects sources whose derivative rights are unsuitable or unknown.

## Start

1. Choose a [subject](#subjects) and a work.
2. Check the work's full row in [`catalog/translations.json`](../catalog/translations.json) or the exact [interlanguage adoption snapshot](adopt.md).
3. Check work-specific existing language coverage and active ownership.
4. Download the [`translation-starter-v2` release](https://github.com/KokunoYumeto/mathematics-commons-pilot/releases/tag/translate-v2).
5. For a local agent, paste `LOCAL.md`. For a hosted web agent, upload the ZIP and paste `WEB.md`.
6. Answer the work and target-language questions. Translation begins only after the source and license preflight passes.

The starter contains no textbook and no completed translation. It provides the chooser, exact source-freeze template, production rules, cumulative return contract, and independent QA.

## Subjects

- [Foundations and school algebra](#foundations-and-school-algebra)
- [Calculus, analysis, and differential equations](#calculus-analysis-and-differential-equations)
- [Linear algebra, abstract algebra, and number theory](#linear-algebra-abstract-algebra-and-number-theory)
- [Probability and statistics](#probability-and-statistics)
- [Discrete mathematics and combinatorics](#discrete-mathematics-and-combinatorics)
- [Logic and formal mathematics](#logic-and-formal-mathematics)
- [Geometry, topology, manifolds, and algebraic geometry](#geometry-topology-manifolds-and-algebraic-geometry)
- [Numerical mathematics, computing, optimization, and modeling](#numerical-mathematics-computing-optimization-and-modeling)
- [Functional analysis and operator theory](#functional-analysis-and-operator-theory)
- [Research and assessment infrastructure](#research-and-assessment-infrastructure)

Status meanings:

- `current_production` or `existing_edition`: coverage information; do not overwrite it.
- `selected_start`: named source of interest; public source/license/build preflight may still be required.
- `conditional_candidate`: promising source with a recorded blocking preflight.
- `candidate` or `optional`: not translation-ready without the listed source/component/build work.
- `donor`, `reference`, or `infrastructure`: not a standalone translation assignment.

### Foundations and school algebra

| ID | Work | State |
|---|---|---|
| R001a | OpenStax Prealgebra 2e | current production |
| R001b | OpenStax Elementary Algebra 2e | current production |
| R001c | OpenStax Intermediate Algebra 2e | current production |
| R002 | OpenStax Precalculus 2e | selected start |

### Calculus, analysis, and differential equations

| ID | Work | State |
|---|---|---|
| R003 | CLP Calculus 1–4 and problem books | current production |
| R006 | Lebl analysis corpus | current production; exact volume identity still required |
| R007 | Lebl ODE corpus | current production; exact volume identity still required |
| R008 | Lebl complex-analysis corpus | current production; exact volume identity still required |
| O007 | Measure, Integration & Real Analysis composite | candidate |
| O010 | Partial Differential Equations | conditional candidate |

### Linear algebra, abstract algebra, and number theory

| ID | Work | State |
|---|---|---|
| R005 | Hefferon Linear Algebra | current production |
| R009 | Judson Abstract Algebra | current production |
| R014 | Yet Another Introductory Number Theory Textbook | selected start |
| O013 | Methods of Algebra, Volume 1 | optional |
| O014 | Methods of Algebra, Volume 2 | optional |

### Probability and statistics

| ID | Work | State |
|---|---|---|
| R010 | Grinstead–Snell Probability | current production |
| R011 | OpenIntro Statistics | selected start |
| O006 | Distribution theory and statistical methods composite | candidate |
| O009 | Measure-theoretic probability and stochastic-processes composite | candidate |

### Discrete mathematics and combinatorics

| ID | Work | State |
|---|---|---|
| R004 | DMOI4 | existing edition |
| R012 | Applied Combinatorics | selected start |

### Logic and formal mathematics

| ID | Work | State |
|---|---|---|
| R013 | Open Logic configured Indonesian edition | existing edition reported; exact public edition still unverified |
| R018 | Mathematics in Lean | selected start |
| R020 | Open Logic core source | conditional candidate |

R020 is pinned to Open Logic commit `1e960beff9ed7835bf3e3f1335e21af3439cd107` and tree `45cad6b3bf0dd96985a7b3d1dc5c343984b0e1c8`. Its CC BY 4.0 license, root README, `.gitmodules`, and `doc` gitlink have been verified. The `doc` submodule census and unchanged baseline build have not yet passed, so R020 is a source-preflight assignment, not a runnable translation.

### Geometry, topology, manifolds, and algebraic geometry

| ID | Work | State |
|---|---|---|
| O003 | Topology: An Inquiry-Based Approach | conditional candidate |
| O004 | Euclidean Plane and Its Relatives | conditional candidate |
| O011 | Smooth manifolds and differential geometry composite | optional |
| O012 | AlgebraicTopology2019 | optional |
| O016 | Algebraic-geometry bridge composite | optional |
| R019 | Stacks Project | reference only |

### Numerical mathematics, computing, optimization, and modeling

| ID | Work | State |
|---|---|---|
| R015 | Tea Time Numerical Analysis | current production |
| R017 | Open Optimization Book 1 | selected start |
| O002 | Mathematical Python plus Research Software Engineering with Python | candidate |
| O005 | Modeling and nonlinear-dynamics composite | candidate |
| O015 | MIT OCW 6.253 | optional; editable-source gate open |
| O018 | Open-solver operations-research lab | infrastructure |

### Functional analysis and operator theory

| ID | Work | State |
|---|---|---|
| R016 | Fubini–Tonelli real/functional-analysis source | donor only |
| O008 | Functional Analysis and Operator Algebras | conditional candidate |

### Research and assessment infrastructure

| ID | Work | State |
|---|---|---|
| O001 | Cross-corpus mastery, hints, solutions, and alternate assessment | infrastructure |
| O017 | Research reading, exposition, and reproducibility composite | candidate |

## Existing language coverage

The exact interlanguage snapshot is commit [`7a00b564ace8230c57309df2d66325e57d1c4043`](https://github.com/KokunoYumeto/modern-latex-manuscripts/tree/7a00b564ace8230c57309df2d66325e57d1c4043), tree `e3d53eb3216a2d6e99cce32a358ecd06377e3115`. Its 78 work rows contain the following language-tag presence counts:

| Tag | Rows | Tag | Rows | Tag | Rows |
|---|---:|---|---:|---|---:|
| ar | 6 | de | 26 | en | 44 |
| es | 1 | fa-IR | 1 | fr | 9 |
| id | 1 | isv | 1 | it | 1 |
| ja | 1 | ko | 3 | mul | 1 |
| ru | 1 | sa | 1 | uk | 2 |
| vi | 1 | zh | 7 | zh-Hans-CN | 2 |
| zh-Hant-controlled | 1 | und | 8 |  |  |

These are row-presence counts, not whole-language completion. Complete-class rows include bounded Noether material in Spanish, French, Russian, Ukrainian, Interslavic, Korean, Simplified Chinese, controlled Traditional Chinese, Japanese, Indonesian, and Vietnamese; represented EGA English; FGA French/English; and bounded Dedekind/Dirichlet German/English items. Read the exact row and map before selecting a target language.

The snapshot has 16 complete, 2 active, 16 partial, 6 scattered, 14 source-only, 21 weak, and 3 unworked scopes. Parallel editions are allowed when declared; active or complete material is not an invitation to overwrite an existing generation.

## Choosing a target language

Choose any language not already maintained for the selected work. Record the exact locale, script, and orthographic standard. Explain the educational use and identify who can review the mathematics and language.

No authoritative UNESCO list of “96 underserved languages” was found. The project therefore does not publish such a list under UNESCO's name. UNESCO does report that many learners do not receive education in a language they speak or understand; contributors should use documented community needs and work-specific coverage instead of a fabricated ranking.

## Source eligibility

Translation begins only when all of the following are recorded:

- exact public edition or source boundary;
- immutable commit, tag, tree, or archive hash;
- explicit permission for translation derivatives;
- component-rights and notice inventory;
- complete editable source;
- unchanged baseline-build attempt and receipt;
- exact source language and target language; and
- work-specific existing-edition and ownership review.

“Free to read” is not derivative permission. No-Derivatives, rights-unknown, donor, reference-only, and rejected rows are not translation assignments. If a candidate fails one of these conditions, contribute the missing source preflight instead.

## Production and return

Produce a standalone target-language edition, not a bilingual or facing-page substitute. Preserve formulas, theorem structure, identifiers, references, exercises, solutions, figures, code, build semantics, component licenses, and accessibility information. Return cumulative source, reader, ledgers, checkpoint, and manifest after each bounded unit. Independent cold QA is required before a release claim.
