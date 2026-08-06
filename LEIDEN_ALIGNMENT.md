# Mathematics Commons: Durable Requirements

**Status:** Normative working specification for the white paper and minimum viable system  
**Version:** 2026-08-06.3
**Leading framework:** [Leiden Declaration on Artificial Intelligence and Mathematics](https://leidendeclaration.ai/), 2 June 2026, DOI [10.5281/zenodo.20302944](https://doi.org/10.5281/zenodo.20302944)

## 1. Purpose and interpretation

The Mathematics Commons exists to help people and automated systems do mathematics well. It treats the Leiden Declaration as its leading scientific and ethical framework because the Declaration turns long-standing mathematical norms into an explicit community-backed response to AI-assisted research.

Leiden alignment is enabling rather than prohibitory. The project does not use rigor, authorship, attribution, review, openness, or ethics as reasons to avoid AI-assisted mathematics. It builds those requirements into the infrastructure so that exploration can expand without making the mathematical record less trustworthy.

The Commons may publicly describe itself as **designed to align with the Leiden Declaration** only while it maintains the traceability matrix in this document. It MUST NOT describe itself as “Leiden certified,” endorsed by the Declaration's working group, or endorsed by the International Mathematical Union unless such an endorsement is separately obtained.

The key words **MUST**, **MUST NOT**, **SHOULD**, **SHOULD NOT**, and **MAY** are normative. A requirement may be waived only by a recorded decision naming the requirement, reason, scope, responsible human, and expiry or review date. A waiver cannot convert an inadequately supported mathematical claim into an established result.

### 1.1 Privacy presumption and proportional disclosure

All requirements below operate subject to legitimate privacy, confidentiality, security, copyright, third-party-rights, and legal constraints. Ordinary AI interactions are private by default. Contributing a mathematical artifact does not grant the Commons general access to, or permission to publish, the contributor's prompt history, raw transcripts, hidden reasoning or chain-of-thought, private working notes, unpublished communications, personal context, credentials, or unrelated local data.

The Leiden Declaration asks contributors to disclose material automated-tool use and to make mathematical arguments independently understandable and verifiable. It does not require publication of prompt histories or raw AI transcripts. Its reference to “proprietary knowledge or equipment” concerns whether the mathematics can be independently understood; **“proprietary prompts” is not wording from the Declaration and is not a Commons disclosure requirement**.

The public record MUST contain only the proportionate, sanitized information reasonably needed under ordinary mathematical, academic, institutional, and destination-venue integrity standards: which material tools were used and for what role, a functional task specification, material human interventions, supporting sources and artifacts, checks performed, known limitations, and any relevant disclosure gap. Raw interaction records MAY be published only by the contributor's specific affirmative choice, after privacy, confidentiality, security, and rights review. If a material detail cannot appropriately be shared, the limitation MUST be stated and the associated claim narrowed when necessary.

A prompt or transcript is process provenance, not proof, authorship, or a magical causal explanation of theorem-level work. A mathematical claim must stand on independently checkable arguments and evidence. A distinct empirical claim about a system's autonomy or performance may require a more detailed experimental protocol, but even then the default is a sanitized protocol and appropriately qualified claim, not coerced publication of private conversations.

Every module, packet, runner, and evidence bundle MUST apply data minimization: declare what is public, private, restricted, temporary, or prohibited; access only the files and services required for its bounded task; exclude unrelated local state and conversations by default; and retain no private material merely because it might later be convenient.

“Private by default” defines the Commons' own collection and publication boundary. It is not a guarantee about a chosen provider's retention, training, account, or legal terms; those MUST be assessed separately and any material limitation disclosed.

### 1.2 Current implementation goal

The immediate goal is a small, GitHub-native proof-of-concept operated by an initial group already comfortable with AI-assisted work. It will:

- maintain a versioned list of selected Erdős and other approachable open problems;
- include a small lane for rigorously stated community conjectures;
- issue bounded literature-search, open-status, proof, counterexample, computation, exposition, and formalization packets;
- route those packets manually or through simple labels according to available time and compute;
- collect submissions as portable evidence bundles and pull requests;
- run independent peer-to-peer review and explicit promotion gates; and
- publish one mirrored, archived pilot release and a candid workflow retrospective.

The pilot tests whether the protocol produces reviewable mathematics and catches errors. It does not need to solve an open problem to succeed.

### 1.3 Future conceptual directions, not current deliverables

The protocol is intentionally extensible to archival transcription, canonical editions, multilingual translation, Stacks-style semantic integration, non-Git public onboarding, automatic capability routing, one-click donated-agent workflows, and a genuinely local volunteer CPU/GPU or model network. These directions are recorded so the pilot does not create incompatible infrastructure. They MUST NOT be represented as features of the first release.

## 2. Scope distinctions

The white paper and implementation MUST keep four related ideas distinct.

### 2.1 Accessibility and inclusion

The Commons SHOULD reduce barriers arising from language, disability, geography, cost, institutional status, technical background, and unequal access to proprietary tools. It SHOULD support multilingual interfaces and releases, persistent pseudonymous participation where compatible with publication rules, low-bandwidth workflows, and contribution paths that do not require Git expertise.

This is a genuine inclusion commitment.

### 2.2 Broad integrability of contributions

The protocol MUST accept many kinds of bounded, reviewable mathematical work: source recovery, rights checking, transcription, translation, terminology review, diagram reconstruction, citation audit, literature search, problem-status audit, proof search, counterexample search, computation, formalization, statement-correspondence review, adversarial review, synthesis, semantic integration, release engineering, and archival preservation.

Authority attaches to evidence for a particular artifact, not to biography, credentials, compute ownership, model tier, or a generalized score of intelligence.

### 2.3 Present-day decentralization

For the minimum viable system, decentralization means that independently operated human–AI nodes can obtain bounded packets, work locally, submit portable evidence, independently review other nodes, mirror the scientific record, and leave the initial coordination platform without losing the mathematics. The underlying model MAY still be proprietary or remotely hosted.

### 2.4 Future fully local peer-to-peer compute

A federation of locally hosted models and volunteered CPU/GPU resources is a compatible future program, not a dependency of the minimum viable system. Possible uses include OCR, layout recovery, transcription, translation, embedding and index construction, formal-library search, and training rights-cleared specialist models on historical corpora. This future program MUST satisfy the same source-rights, consent, security, resource, attribution, review, and environmental requirements as the present system.

The suggestion to train rights-cleared specialist models on historical mathematical corpora is credited to Reddit user [u/UmbrellaCorp_HR](https://www.reddit.com/user/UmbrellaCorp_HR/), cited solely by the public pseudonym supplied for attribution.

## 3. Foundational scientific requirements

| ID | Normative requirement | Required evidence or control |
|---|---|---|
| `SCI-001` | A promoted mathematical result MUST contain a human-readable account of its central argument, not only a model transcript, solver verdict, formal term, or press summary. | Reader-facing statement and argument tied to an exact version. |
| `SCI-002` | Proof remains the highest evidence for theorem claims; the system MUST distinguish proof, computation, experiment, heuristic, analogy, and conjecture. | Typed claim and evidence fields; promotion rules by claim type. |
| `SCI-003` | Every review MUST identify the exact artifact version, the scope checked, methods used, limitations, and reviewer. | Version-bound review record. |
| `SCI-004` | A promoted claim MUST be independently verifiable from its public mathematical argument and shareable evidence. Private interaction history, secret model state, or inaccessible equipment MUST NOT serve as its sole justification; this does not make those private materials publishable. | Open argument or certificate and shareable evidence; material inaccessible dependencies disclosed at a functional level. |
| `SCI-005` | Formal verification MUST be used when proportionate and feasible for high-risk or central claims, but formal acceptance MUST NOT substitute for checking that the encoded statement matches the intended mathematics. Formal artifacts MUST disclose their trust base, including toolchain, library revision, axioms, oracles, generated code, and placeholders. | Kernel/build receipt, trust-base manifest, and a separate statement-correspondence review. |
| `SCI-006` | Theoretical and computational conclusions MUST be cross-checked when both are material to a claim. | Independent replay, exact certificate, certified bounds, or documented comparison. |
| `SCI-007` | Claim status, literature status, proof review, computation status, formalization status, and publication status MUST remain separate. | Faceted status record; no bare `verified` badge. |
| `SCI-008` | The system MUST preserve failed attempts, objections, counterexamples, corrections, reversals, and withdrawals when they are useful to the scientific record. | Append-only disposition and supersession history. |
| `SCI-009` | Major or unusually consequential claims MUST receive enhanced review before promotion: statement freeze, source audit, independent domain review, adversarial review, and external pre-submission review. | Major-claim review bundle and named human disposition. |
| `SCI-010` | Review capacity MUST constrain publication throughput. Generation queues SHOULD slow or pause when adequate independent review is unavailable. | Queue-health metrics and a documented overload rule. |
| `SCI-011` | The Commons MUST support evaluation of depth, difficulty, significance, and residual open questions independently of whether AI was used. | Significance assessment written by humans with relevant expertise. |
| `SCI-012` | Research questions MUST NOT be prioritized merely because they are easy to automate, likely to produce publicity, or useful as product demonstrations. | Public selection rationale and conflict-of-interest disclosure. |
| `SCI-013` | The project MUST preserve space for human understanding, exposition, judgment, question formation, and autonomously chosen research. | Human synthesis and research-rationale fields in mature programs. |
| `SCI-014` | A significant release MUST include an understanding artifact explaining motivation, the central idea, why the method works, its relation to prior mathematics, limitations, and questions created by the result. | Versioned exposition reviewed separately from correctness. |

## 4. Human authorship, responsibility, and credit

| ID | Normative requirement | Required evidence or control |
|---|---|---|
| `HUM-001` | Automated systems MUST NOT be listed as authors or accountable signatories. | Authorship validation and tool-disclosure section. |
| `HUM-002` | Every result promoted beyond candidate status MUST name at least one human responsible for correctness, adequacy of exposition, and citation completeness. That person MUST be able to explain the central argument and limitations; responsibility cannot be rented as a signature for an unexamined artifact. | Version-specific responsible-claimant acceptance and comprehension statement. |
| `HUM-003` | A node operator who contributes compute is not automatically an author or responsible claimant. | Separate credit roles for operator, contributor, author, reviewer, and sponsor. |
| `HUM-004` | Credit MUST distinguish problem origin, discovery, proof development, computation, formalization, transcription, translation, prior-art identification, review, exposition, maintenance, and release work. | Contribution-role ledger, preferably compatible with CRediT-like role vocabularies while retaining mathematics-specific roles. |
| `HUM-005` | Reviewers are responsible only for the scope they explicitly checked; stewards are responsible for process integrity, not automatically for mathematical correctness. | Signed or attributable role-scoped review records. |
| `HUM-006` | Persistent pseudonyms MAY be used in the working network, but a promoted claim still requires an answerable human account and publication MUST follow the destination venue's rules. | Persistent identity record and publication handoff check. |
| `HUM-007` | The project MUST NOT use a scalar leaderboard, model tier, institutional affiliation, or compute contribution as a proxy for mathematical merit. | Role-specific records and claim-specific evidence only. |
| `HUM-008` | Academic authorship, priority, credit, responsibility, prizes, and professional recognition MUST be treated separately from copyright ownership. CC0 dedication does not make an AI an author and does not remove human responsibility. | Separate authorship/contribution and rights fields. |

## 5. Tool and computational-resource disclosure

| ID | Normative requirement | Required evidence or control |
|---|---|---|
| `TOOL-001` | Every research packet, run, review, and release MUST disclose material use of language models, machine learning, proof assistants, solvers, mathematical software, search systems, and OCR/translation tools. | Machine-readable run/review manifest and reader-facing release disclosure. |
| `TOOL-002` | Disclosure MUST record provider, model/tool name, version or dated identifier, mode, access date, a sanitized functional task specification, material human interventions, relevant compute, verification performed, reproducibility limits, nondeterminism, and material information that is unavailable. | `run.json` schema validation. |
| `TOOL-003` | AI interactions, prompt histories, raw transcripts, private working notes, personal data, credentials, and unrelated informal material MUST be treated as private by default. They MUST NOT be required or published without the contributor's specific affirmative choice and a privacy, confidentiality, security, and rights review. | Data-minimized disclosure; publication-consent field; redaction/privacy review; omitted categories described only when material. |
| `TOOL-004` | Tool choice MUST consider values alignment, source and training rights, privacy, openness, accessibility, energy and material cost, and whether a smaller or non-proprietary system suffices. | Tool-choice record for substantial runs. |
| `TOOL-005` | The capability router SHOULD prefer the least resource-intensive adequate tool and SHOULD expose cost and resource limits before work begins. | Declared resource envelope and routing rationale. |
| `TOOL-006` | A faster result MAY be delayed when the available tool or partnership would materially violate the project's scientific or ethical requirements. | Recorded refusal, deferral, or alternate-tool decision. |
| `TOOL-007` | Maintainers and reviewers MUST stay informed enough to revise threat models, disclosure fields, and validation policies as tools change. | Scheduled policy review and versioned compatibility registry. |
| `TOOL-008` | Reviewers MUST disclose material AI assistance in their review, follow the destination venue's confidentiality and tool rules, and remain responsible for every recommendation they make. | Reviewer tool disclosure and venue-policy attestation. |
| `TOOL-009` | Useful non-AI contribution and review paths MUST remain available, and contributors MAY decline a model, provider, task, or partnership without penalty. | Provider-choice controls and non-AI packet routes. |
| `TOOL-010` | A prompt or transcript MUST NOT be treated as proof, authorship, or a sufficient explanation of model capability. When particular instructions materially affect scientific evaluation, their functional content MUST be summarized in sanitized form; verbatim excerpts remain optional and contributor-controlled. | Sanitized task specification, optional approved excerpts, and claim qualification where details remain private. |
| `TOOL-011` | Empirical claims about model autonomy or performance MUST disclose a proportionate experimental protocol and evidence. They MUST be narrowed when private or unavailable details prevent evaluation, without converting raw-transcript publication into a default requirement. | Protocol summary, evaluation artifacts, disclosure gaps, and qualified claim language. |

## 6. Attribution, sources, licenses, and training consent

| ID | Normative requirement | Required evidence or control |
|---|---|---|
| `ATTR-001` | Novelty and open-status claims MUST be preceded by a documented literature search and direct inspection of material sources, including non-English sources when reasonably relevant. | Query ledger, languages, dates, identifiers, relevance decisions, coverage limits, and source citations. |
| `ATTR-002` | Citations SHOULD resolve to primary sources at theorem, page, section, or exact object level where possible. | Source ledger and citation audit. |
| `ATTR-003` | AI-generated citations and database matches are leads, not verified references. | Source-opened flag and reviewer receipt. |
| `ATTR-004` | If satisfactory attribution cannot be established, the uncertainty MUST be stated prominently rather than converted into a priority claim. | Attribution-gap flag and qualified public language. |
| `ATTR-005` | Every ingested source MUST record copyright status, redistribution permission, extraction permission where relevant, license, provenance, and integrity hash. | Rights and provenance manifest. |
| `ATTR-006` | Public availability MUST NOT be treated as consent for model training. A training job MUST use only material with recorded permission or a reviewed legal basis compatible with project policy. | Training-consent field and dataset allowlist. |
| `ATTR-007` | Contributors MUST be able to specify licenses and, where meaningful, machine-learning use preferences for their own material. | Submission form and release metadata. |
| `ATTR-008` | The project SHOULD develop or adopt plain-language licensing templates and seek qualified legal advice for uncertain, large-scale, or cross-jurisdictional uses. | Template register and escalation path. |
| `ATTR-009` | Attribution must have its own challenge, correction, and appeal path; correcting credit or locating prior art counts as a successful contribution. | Attribution objection and disposition records. |
| `ATTR-010` | All Commons-originated material MUST be released under CC0 1.0, modulo pre-existing third-party copyright and other rights. The Commons MUST NOT purport to waive rights it does not control. | Per-file provenance and rights manifest; third-party exception records. |
| `ATTR-011` | “Commons-originated” MUST include every newly created component submitted through the workflow, including proofs, computations, formalizations, code, metadata, reviews, corrections, translations, transcriptions, and exposition. Contributors dedicate any rights they control under CC0; absence of copyright and waiver of possible rights lead to the same open result. | Mandatory `origin`, `dedication`, third-party-component, and redistribution-status fields. |
| `ATTR-012` | Provenance MUST cover materially influential ideas and process contributions, not only incorporated files: problem nominations, workflow proposals, source leads, sanitized task specifications or voluntarily disclosed prompts, prior attempts, and conceptual suggestions retain their originator where the contributor has made that attribution lawfully publishable. Public pseudonyms MUST be credited without attempted deanonymization; attribution MUST NOT compel raw-transcript disclosure; uncertainty MUST be recorded rather than silently reassigned. | Idea-origin field, contribution-role ledger, stable public-handle citation where supplied, privacy/publication boundary, and attribution-gap record. |

## 7. Open science, review, publication, and public communication

| ID | Normative requirement | Required evidence or control |
|---|---|---|
| `OPEN-001` | Scientific state MUST be stored in portable, version-controlled files rather than only in platform-specific issues, chats, or dashboards. | Cloneable claims, reviews, decisions, and manifests. |
| `OPEN-002` | Mature releases SHOULD make lawful source, code, data, formal files, review records, and reproduction instructions openly available under explicit licenses. | Release inventory and license mapping. |
| `OPEN-003` | Artifacts MUST use stable identifiers, hashes, immutable versions, and durable archives where proportionate. | Signed tag, checksum manifest, DOI/archive receipt, and mirror readback. |
| `OPEN-004` | A GitHub release, network status, Reddit post, blog post, or press release MUST NOT be represented as a substitute for scholarly peer review. | Publication-status field and mandatory disclaimer. |
| `OPEN-005` | Significant results SHOULD be submitted to appropriate peer-reviewed journals, proceedings, books, or recognized formal-library review processes. | Publication plan or recorded reason for another route. |
| `OPEN-006` | Public communication MUST state the exact result, limitations, prior human foundations, degree of automation, review status, and residual open problem. | Communications checklist tied to release version. |
| `OPEN-007` | The project MUST NOT use mathematical tasks as unsupported benchmarks for general intelligence or model marketing. | Communications and partnership policy. |
| `OPEN-008` | Publicity MUST follow, not outrun, the evidence required for scientific evaluation. | Major-claim communications hold and review sign-off. |
| `OPEN-009` | Contributors and domain experts SHOULD participate in public explanation and serious science communication, including correction of misleading claims. | Public-context note or designated spokesperson for major releases. |
| `OPEN-010` | The Commons SHOULD cooperate with other research and creative communities facing related attribution, labor, access, and automation issues. | Partnership and interoperability record. |
| `OPEN-011` | Later scholarly publication MUST preserve the CC0 Commons artifact, complete provenance, AI disclosure, and correction record. Contributors MUST NOT grant exclusive rights over Commons-originated material or use a venue whose terms require its removal or restriction. | Publication-rights compatibility review. |

## 8. Accessibility and contribution integrability

| ID | Normative requirement | Required evidence or control |
|---|---|---|
| `ACCESS-001` | Core schemas MUST be language-neutral, Unicode-safe, and capable of linking multiple language realizations to the same semantic object without making English the mathematical authority. | Multilingual object schema and source-language provenance. |
| `ACCESS-002` | Core onboarding, contribution, correction, and review instructions SHOULD be available in multiple languages as capacity permits. | Translation status manifest. |
| `ACCESS-003` | Translation MUST be treated as substantive mathematical work requiring source alignment, terminology decisions, and independent review. | Translation packet and bilingual review record. |
| `ACCESS-004` | The corpus and intake strategy SHOULD actively include mathematical traditions, journals, archives, languages, and classification systems outside the dominant Anglophone and Western digital corpus. | Coverage audits and targeted source programs. |
| `ACCESS-005` | A contributor SHOULD be able to submit, claim, review, or correct a bounded task without knowing Git or command-line tools. | Web or desktop flow backed by the same durable packet format. |
| `ACCESS-006` | Interfaces SHOULD support low-bandwidth use, assistive technology, clear language, and downloadable offline packets where feasible. | Accessibility test and offline export. |
| `ACCESS-007` | Standards and practices MUST be explicit and teachable, with meaningful paths for contributors from other fields and for amateurs. | Public examples, calibration tasks, glossary, and review guidance. |
| `ACCESS-008` | The project MUST evaluate work by the evidence contributed, while preserving the distinction between participation, review competence, and responsibility for a promoted claim. | Role-scoped permissions and promotion gates. |
| `ACCESS-009` | The workflow SHOULD expose the distributed, cumulative nature of mathematics rather than reward a single-genius narrative. | Granular credit, dependency maps, and visible correction/review labor. |
| `ACCESS-010` | A public code of conduct and non-discrimination/accessibility policy SHOULD protect meaningful participation without weakening artifact-specific standards. | Versioned policy, reporting route, and appeals process. |
| `ACCESS-011` | A future translation program SHOULD prioritize work by auditable **marginal intelligibility gain**: expected additional mathematical access per unit of translation and review effort. Citation count MAY inform the estimate but MUST NOT dominate community need, foundational reach, pedagogical value, language scarcity, source authority, rights feasibility, and qualified review capacity. | Public prioritization factors, community nominations, language-coverage data, and recorded human decisions. |

## 9. Ethics, autonomy, partnerships, and funding

| ID | Normative requirement | Required evidence or control |
|---|---|---|
| `ETH-001` | Programs and consequential packets MUST consider plausible harmful applications, including warfare, oppression, mass surveillance, anti-democratic use, and other serious harms. | Proportionate ethics-impact field and escalation status. |
| `ETH-002` | Contributors MUST be free to decline or withdraw from harmful work without losing unrelated standing in the Commons. | Conscientious-refusal and withdrawal policy. |
| `ETH-003` | External partnerships MUST respect research independence, publication integrity, attribution, source rights, and freedom to discuss corporate policies and priorities. | Public partnership terms and conflict disclosures. |
| `ETH-004` | Material funding and infrastructure relationships MUST be disclosed, including constraints placed on publication, data, models, or research direction. | Funding and dependency register. |
| `ETH-005` | The Commons MUST preserve independent human choice over research questions and methods; sponsors and model providers MUST NOT silently control the agenda. | Program-selection record and governance protections. |
| `ETH-006` | Funding decisions within the Commons SHOULD consider compliance with these requirements rather than rewarding output volume alone. | Values-based funding rubric. |
| `ETH-007` | Collaborators facing industry asymmetry SHOULD have access to shared licensing guidance and, where possible, legal or institutional support. | Collaboration framework and referral list. |
| `ETH-008` | The project SHOULD measure and publish relevant compute, monetary, and environmental costs without turning rough estimates into false precision. | Resource report and methodology. |
| `ETH-009` | Volunteer resource use MUST be informed, bounded, revocable, and free of hidden telemetry, hidden training, or undisclosed redistribution. | Local consent receipt, resource caps, and auditable data-flow policy. |

## 10. Organizational preparedness and public-interest infrastructure

| ID | Normative requirement | Required evidence or control |
|---|---|---|
| `ORG-001` | The Commons MUST maintain current policies for disclosure, authorship, review, attribution, conduct, major claims, corrections, security, and publication. | Versioned policy set and scheduled audit. |
| `ORG-002` | A major-result response procedure MUST exist before a major claim appears. | Freeze, triage, expert review, communications, and external-review runbook. |
| `ORG-003` | Governance MUST include relevant mathematical, formal, archival, linguistic, security, ethical, and community expertise as the project grows. | Public responsibility map and identified gaps. |
| `ORG-004` | The Commons SHOULD support and advocate for university, national, international, cooperative, and other public-interest automated-mathematics infrastructure independent of a single company. | Infrastructure position and partnership criteria. |
| `ORG-005` | The project SHOULD publish evidence-based responses to exaggerated capability claims and SHOULD consult domain experts rather than relying on vendor announcements. | Case-study audit standard and correction log. |
| `ORG-006` | The project supports proportionate public oversight of AI systems and mathematical uses that present serious public harms. | Governance statement; external policy work remains optional. |
| `ORG-007` | The Commons SHOULD offer interoperable standards that organizations, funders, publishers, and public laboratories can adopt without surrendering their own governance. | Open specification, schemas, and conformance tests. |

## 11. Research Packet and capability router

Every contribution MUST enter the durable workflow as a versioned **Research Packet** or as an intake item that a steward converts into one. A packet is the smallest independently claimable and reviewable unit.

### 11.1 Required packet fields

Every packet MUST record:

- stable packet ID, schema version, task kind, project/program ID, and status;
- exact scope, exclusions, stopping conditions, dependencies, and continuation cursor;
- source identifiers, authority status, rights/license information, hashes, and permitted transformations;
- required inputs and outputs, including JSON metadata and human-readable or LaTeX artifacts where appropriate;
- acceptance tests and the kinds of independent review required;
- risk classification covering mathematical, security, privacy, rights, ethical, and publicity risk;
- disclosure requirements, data-minimization and publication boundary, retention/redaction decisions, and human responsibility state;
- a resource envelope and capability requirements;
- attribution and credit roles;
- lease, checkpoint, submission, objection, correction, and supersession information.

### 11.2 Capability profile

A contributor node MUST be able to declare a bounded profile without exposing unnecessary personal information:

- agent family and interface, without treating brand as authority;
- subscription or budget envelope;
- context and output limits;
- expected available time;
- CPU, RAM, GPU, storage, and network limits;
- available proof assistants, solvers, OCR, rendering, and language tools;
- human languages and mathematical/formal competencies offered;
- privacy, licensing, tool-provider, energy, and ethical preferences;
- willingness to run code and the required isolation level.

User-facing presets MAY resemble `light`, `standard`, `extended`, and `local-compute`, with adapters mapping current commercial subscriptions or local hardware to actual limits. Fixed price labels such as “$20 model” or “$200 model” MUST NOT appear in the durable schema because prices and products change. Model tier MUST NOT alter the evidentiary standard for the submitted claim.

### 11.3 Routing requirements

| ID | Normative requirement | Required evidence or control |
|---|---|---|
| `ROUTE-001` | The router MUST assign only packets whose declared resource, tool, rights, safety, and competence requirements fit the node profile. | Machine-checkable compatibility decision. |
| `ROUTE-002` | Large tasks SHOULD be decomposed into useful packets that lower-resource nodes can complete without producing incoherent fragments. | Dependency-aware packet tree and merge contract. |
| `ROUTE-003` | Higher spending or compute tiers MUST NOT confer priority, governance power, authorship, or reduced review. | Scheduler and governance tests. |
| `ROUTE-004` | The routing decision SHOULD prefer the smallest sufficient resource envelope and SHOULD avoid concentrating all valuable work in proprietary premium tiers. | Routing rationale and packet-distribution metrics. |
| `ROUTE-005` | The human operator MUST approve a clear permission envelope before work: files, network, code execution, compute, monetary budget, and maximum duration. | Consent receipt stored locally; public record contains only non-sensitive summary. |
| `ROUTE-006` | A packet MUST run in an isolated workspace and MUST NOT obtain secrets merely because its output will be submitted to the Commons. | Sandbox policy and automated security checks. |
| `ROUTE-007` | Self-checking is mandatory but never sufficient for promotion. Producer and accepting reviewer MUST be distinct roles. | Separate review packet and disposition. |
| `ROUTE-008` | A completed node run MUST return a portable evidence bundle rather than only a conversational answer. | Outputs, manifest, sanitized run summary, optional contributor-approved excerpts, hashes, and test receipts. |
| `ROUTE-009` | Leases and checkpoints MUST prevent silent overlap and permit safe continuation after interruption. | Lease record, cursor, and immutable checkpoint. |
| `ROUTE-010` | Project variants MAY expose different packet trees—such as archival transcription, corpus translation, Stacks-style integration, or conjecture research—while using the same packet and review protocol. | Common schema conformance test. |
| `ROUTE-011` | The interface MUST distinguish a locally operated agent client from genuinely local model inference. Remote providers, data flows, retention limits, and reproducibility constraints remain disclosed. | Capability profile and run disclosure. |
| `ROUTE-012` | Every module MUST declare and enforce its data boundary. It MUST collect and expose only what its bounded task requires, deny unrelated local context by default, and distinguish public, private, restricted, temporary, and prohibited material before execution or submission. | Per-module privacy class, allowlisted inputs and destinations, retention rule, redaction check, and publication preview. |

## 12. Peer-to-peer review requirements

Peer-to-peer review means that an artifact produced at one independently operated human–AI node is reproduced, challenged, source-checked, formalized, or integrated by other nodes against shared public standards.

Consensus is evidence-indexed, not vote-based. Agreement among models does not make a theorem true, and disagreement is not resolved by model count.

The review graph MUST support:

1. source and authority review;
2. transcription, translation, and semantic-fidelity review;
3. mathematical reconstruction and adversarial review;
4. computational reproduction and certificate checking;
5. proof-assistant checking and separate statement correspondence;
6. literature, attribution, and open-status review;
7. integration and relation-strength review;
8. release, rights, privacy, and archival review;
9. external scholarly review for significant claims.

The system MUST seek the highest standard of proof and checking reasonably available for the mathematics involved. When complete formalization is not presently feasible, the packet MUST record what was checked, what remains informal, which expert standards were applied, and what would strengthen the result.

## 13. Minimum viable GitHub pilot

The first deliverable is neither a custom platform nor a global decentralized compute fabric. It is a small GitHub-native research network that proves the scientific protocol with the initial AI-literate contributor group.

### 13.1 MVP components

1. **One public pilot repository.** It stores problem records, community conjectures, packets, claims, reviews, and status changes as cloneable files. GitHub issues and pull requests coordinate work but do not hold the only durable copy of scientific state.
2. **One small schema set.** JSON Schema defines problem, packet, run manifest, review, and disposition objects. A capability field records approximate budget, time, context, and tools without binding the protocol to current subscription prices.
3. **Agent-readable instructions.** `START_HERE_FOR_AGENTS.md` and a human quick start tell existing Codex, Claude Code, or comparable workflows how to select, claim, execute, check, and submit a packet.
4. **Two initial project lanes.** One lane covers selected Erdős or other established open problems; the other covers carefully stated community conjectures. Both can issue literature, proof, counterexample, computation, exposition, and formalization packets.
5. **Simple capability routing.** Labels and packet fields such as `light`, `standard`, and `extended` help people choose feasible work. Assignment may be manual during the pilot; no custom scheduler is required.
6. **Bounded leases and continuation.** Every assignment has exact inputs, scope, dependencies, resource envelope, cursor, and stopping conditions.
7. **Evidence-bundle submission.** A script validates and packages outputs, disclosures, sources, hashes, and test receipts for a pull request.
8. **Independent review routing.** Submitted work generates separate literature, mathematical, computational, formal, or communication review packets as appropriate.
9. **Promotion gates.** Candidate, network-checked, externally reviewed, published, challenged, superseded, and withdrawn remain explicit states.
10. **Open release and mirror.** The pilot produces one immutable release, one independent Git mirror, one external archive deposit, and one retrospective documenting failures as well as successes.

### 13.2 Pilot usability target

An initial contributor who already knows how to operate a local AI agent SHOULD be able to:

1. clone or download the pilot;
2. tell the agent to read the start file;
3. choose a packet matching the declared time and compute envelope;
4. claim it without overlapping another contributor;
5. let the agent work within the packet boundary;
6. inspect the result summary and disclosed limitations; and
7. submit a validated evidence bundle

with only minimal Git knowledge. Stewards may assist with branches and pull requests during the pilot.

One-click public onboarding, automatic subscription-aware routing, a polished desktop interface, and “donate spare compute” participation are follow-on goals after the packet and review protocol survives real use.

## 14. Future programs

### 14.1 Translation and marginal intelligibility

A future translation tree MAY distribute rights-cleared cornerstone texts and educational resources into language-specific packet queues. Each language pack SHOULD contain source-language authority metadata, a terminology and notation guide, target-language style guidance, translation packet JSON, build templates, and independent mathematical-language review instructions.

Prioritization SHOULD seek the greatest marginal intelligibility gain rather than simply translating already dominant material into additional dominant languages. A transparent heuristic may consider:

- unmet need and scarcity of reliable mathematical material in the target language;
- number and kinds of learners, educators, and researchers likely to gain practical access;
- foundational or downstream importance of the work;
- pedagogical clarity and suitability for translation;
- community requests and availability of target-language reviewers;
- source authority and whether a better canonical source exists;
- copyright, license, consent, and redistribution feasibility; and
- expected translation, typesetting, terminology, and review effort.

Raw citation counts reproduce historical visibility and corpus bias, so they are only one input. The final queue MUST remain inspectable and revisable by affected language communities. Machine translation remains a candidate layer until source alignment, mathematical notation, terminology, and independent review pass. The original and translation remain linked, and corrected translations supersede rather than erase earlier versions.

### 14.2 Volunteered local mathematical compute

After the MVP demonstrates safe packet execution and useful review throughput, a separate program MAY explore a genuinely local peer-to-peer compute fabric.

Candidate workloads include:

- rights-cleared scan segmentation, OCR, layout recovery, and symbol recognition;
- multilingual transcription and translation candidates;
- exact finite searches and independent certificate replay;
- local embedding and retrieval indexes over distributable corpora;
- formal-library search and bounded formalization attempts;
- training or fine-tuning specialist open models on explicitly permitted datasets.

This program MUST NOT assume that volunteer hardware, public scans, or open access implies permission for every use. It MUST include signed work units, dataset allowlists, sandboxing, resource and energy controls, result verification, poisoning resistance, privacy protection, and independent reproducibility. It remains a roadmap item until those controls and the core packet protocol are proven.

## 15. Leiden traceability matrix

This matrix prevents selective citation. “Project treatment” includes both enforceable internal controls and explicit public positions where the Declaration addresses actors outside the Commons.

| Leiden element | Project treatment |
|---|---|
| Proof, certainty, and understanding | `SCI-001`–`SCI-006`, peer-to-peer review layers. |
| Human attribution, credit, and correctness responsibility | `HUM-001`–`HUM-008`. |
| Transparency and independent verification without proprietary dependence | `SCI-003`–`SCI-005`, `OPEN-001`–`OPEN-003`. |
| Shared evaluation of depth, difficulty, and significance | `SCI-011`, `OPEN-006`, no scalar leaderboard. |
| Human expertise, judgment, question formation, and autonomous research | `SCI-012`–`SCI-013`, `ETH-005`. |
| Care for people and the environment | `TOOL-004`–`TOOL-006`, `ETH-001`–`ETH-008`. |
| Plausible but unreliable informal or formal AI output | `SCI-001`–`SCI-010`, review separation and correspondence checks. |
| Review-system overload | `SCI-010`, bounded generation and review routing. |
| Attribution failure, copyright, and exploitative training | `ATTR-001`–`ATTR-012`. |
| Distorted incentives and unequal access | `SCI-012`, `ACCESS-001`–`ACCESS-009`, `ROUTE-003`–`ROUTE-004`. |
| Market-timeline announcements and hype | `OPEN-004`–`OPEN-009`, `ORG-002`, `ORG-005`. |
| Loss of mathematical autonomy and understanding | `SCI-012`–`SCI-013`, `ETH-003`–`ETH-006`. |
| Wider harms involving warfare, surveillance, oppression, democracy, and environment | `ETH-001`–`ETH-008`, `ORG-006`. |
| Transparent disclosure of tools and resources | `TOOL-001`–`TOOL-003`, `TOOL-010`–`TOOL-011`. |
| Making AI-assisted work easier to review | `SCI-001`–`SCI-010`, packet acceptance checks. |
| Open science | `OPEN-001`–`OPEN-003`, `ACCESS-001`–`ACCESS-006`. |
| Human responsibility for arguments, adequacy, and citations | `HUM-002`, `ATTR-001`–`ATTR-004`. |
| Human authorship | `HUM-001`–`HUM-006`. |
| Proactive attribution and explicit uncertainty | `ATTR-001`–`ATTR-004`, `ATTR-009`, `ATTR-012`. |
| Serious public discourse and solidarity with other fields | `OPEN-006`–`OPEN-010`. |
| Staying informed about emerging tools | `TOOL-007`, `ORG-001`–`ORG-003`. |
| Welcoming new contributors while making standards accessible | `ACCESS-001`–`ACCESS-009`. |
| Careful tool choice, including open, small, and efficient alternatives | `TOOL-004`–`TOOL-006`, `ROUTE-004`. |
| Ethical evaluation and value-aligned partnerships | `ETH-001`–`ETH-008`. |
| Organizational expertise and strategic readiness | `ORG-001`–`ORG-003`. |
| Publishing and reviewing policies | `ORG-001`, `SCI-009`–`SCI-010`, `OPEN-004`–`OPEN-008`. |
| Heightened rigor for automated results | `SCI-001`–`SCI-010`. |
| Author rights and control of training use | `ATTR-005`–`ATTR-008`. |
| Appropriate peer-reviewed publication | `OPEN-004`–`OPEN-005`. |
| Independent public research laboratories and accessible infrastructure | `ORG-004`, current federation design, future local-compute program. |
| Frameworks for researchers facing industry asymmetry | `ETH-003`–`ETH-007`. |
| Funding aligned with mathematical values | `ETH-004`, `ETH-006`. |
| Legal protection of authors | `ATTR-005`–`ATTR-008`; the Commons also supports stronger public protection while not claiming to supply it itself. |
| Skepticism toward commercial overstatement | `OPEN-006`–`OPEN-008`, `ORG-005`. |
| Public oversight of harmful AI uses | `ETH-001`–`ETH-003`, `ORG-006`. |
| Investment in public computational infrastructure | `ORG-004`, open schemas, mirrors, and the future local-compute program. |
| Industry adherence to mathematical standards and freedom of conscience | `ETH-002`–`ETH-004`; required of Commons partnerships and advocated externally. |

## 16. Conformance and change control

Every public white-paper revision MUST be checked against this document. Every implementation release SHOULD publish a machine-readable conformance report with four possible states per requirement:

- `implemented`;
- `partially_implemented`;
- `policy_commitment`;
- `not_yet_implemented`.

No aggregate score may conceal failures. Any public “Leiden-aligned” badge MUST link to the versioned conformance report and state that alignment is self-assessed.

Changes to this specification MUST preserve requirement identifiers. Removed or superseded requirements remain in an append-only history with rationale. The official Declaration is the authority for what it says; this document is the Commons' operational interpretation and may impose stronger requirements.
