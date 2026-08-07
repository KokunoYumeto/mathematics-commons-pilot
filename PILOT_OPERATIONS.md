# Mathematics Commons pilot operations

**Status:** pre-live operating playbook for one small 30-day calibration cycle
**Date:** 7 August 2026
**Scope:** selected Erdős or comparable open-problem records and precisely stated community conjectures

This document turns the [white paper](WHITE_PAPER.md) and [GitHub pilot design](GITHUB_PILOT_GUIDE.md) into a bounded operating sequence. It does not claim that the live pilot, automatic routing, or one-click Node Kit already exists. Packet schemas and validation tooling are pilot-build components: their presence and a passing check establish structural conformance, not mathematical correctness. The repository remains at the stage described in [STATUS.md](STATUS.md).

The public [launch board](PILOT_LAUNCH.md) records the missing capacity and gates. The [candidate docket](PILOT_CANDIDATES.md) is a researched shortlist for steward review, not the live queue.

The pilot succeeds if it produces durable evidence, catches errors, and reveals where the protocol fails. It does not need to solve an open problem.

## 1. Operating boundary and launch gate

### Available now

- a public, DOI-bearing concept repository and protected pull-request workflow;
- the Leiden-led scientific, privacy, attribution, and rights rules;
- strict versioned records for problems, packets, packet transitions, sources, runs, evidence, and independent reviews;
- a dependency-free semantic validator, adversarial regression suite, and repository structural check;
- a fail-closed manual packet/agent interface at `tools/commons.py`;
- one elementary, explicitly non-novel calibration collection; and
- issue and discussion surfaces for proposals and criticism.

These components form an operational MVP, not a live network. Structural and semantic checks can reject malformed or internally inconsistent records; they do **not** establish mathematical correctness, source truth, reviewer independence in fact, novelty, or legal permission. The examples alone cannot satisfy the live-record launch gate.

### Required before Day 1 of a live pilot

The stewards record all of the following as complete:

- [ ] two humans can maintain repository continuity, or the documented one-maintainer bootstrap risk has been explicitly accepted for this cycle;
- [ ] at least two stewards are named, even if one has limited repository permissions;
- [ ] every selected record has an exact statement, stable source, current status label, and responsible record steward;
- [ ] problem, packet, packet-transition, source, run, evidence, and review schemas exist and match the intended live record set;
- [ ] `python tools/validate_packets.py --schema-only` passes for the versioned schema set;
- [ ] `python -m unittest discover -s tests -p 'test_*.py'` passes for valid examples and deliberately invalid fixtures;
- [ ] `python tools/validate_packets.py --require-live` passes for the live pilot record instances, and every packet names any additional artifact-specific checks;
- [ ] each active packet has an independent reviewer or reviewer slot reserved before it is offered;
- [ ] resource limits, allowed inputs, allowed outputs, and stop conditions are explicit;
- [ ] a safe publication-preview and rights check has been dry-run on a dummy bundle;
- [ ] a one-way backup or mirror plan exists before irreplaceable work is accepted; and
- [ ] contributors have tested the manual handoff in [NODE_HANDOFF.md](NODE_HANDOFF.md) on one non-sensitive calibration packet.

If a gate is missing, the group may run a labeled process dry-run, but it must not describe the result as accepted pilot evidence or as network-checked mathematics.

## 2. Roles and separation of duties

One person may hold several roles in a small group, except that a producer may not independently approve their own packet.

| Role | Minimum responsibility | May not do alone |
|---|---|---|
| Pilot coordinator | Maintains the 30-day calendar, capacity board, and retrospective. | Decide mathematical correctness merely from schedule pressure. |
| Steward | Triages proposals, freezes records, creates packets, manages leases, and records dispositions. | Treat process authority as mathematical authority. |
| Record steward | Maintains one exact problem statement, provenance trail, and status history. | Silently change the statement or open-status claim. |
| Contributor or node operator | Works one bounded packet and submits only its allowlisted evidence. | Promote their own output or expand scope without approval. |
| Citation reviewer | Opens primary sources and checks what they actually establish. | Infer novelty from failure to find a source. |
| Mathematical skeptic | Reconstructs or attacks the exact argument, including edge cases and hidden assumptions. | Count model agreement as independent proof. |
| Computation reviewer | Replays exact artifacts in a clean, bounded environment. | Generalize beyond the certified computational scope. |
| Formalization reviewer | Checks the trust base and whether the formal statement matches the intended statement. | Treat a compiling theorem as proof of statement correspondence. |
| Responsible claimant | A human who accepts responsibility for an exact promoted claim and can explain its core argument and limitations. | Delegate responsibility to an AI system. |
| Release curator | Freezes exact commits, manifests, reader files, and correction links. | Decide claim status without the required reviews. |

Every review states its scope, exact commit, tools used, conflicts of interest, and what was not checked. Reviewers own only that declared scope.

## 3. Selecting six to ten calibration records

A **record** is the durable statement and status history. A **packet** is one bounded task concerning that record. One record may generate several packets, but active packets must stay within review capacity.

### Required gates for every record

Accept a record only when all of these are true:

1. The statement can be frozen with exact quantifiers, conventions, and edge cases.
2. A stable public source or an authorized source record exists.
3. The current status is dated and qualified; a website label alone is not treated as authoritative.
4. At least one useful output is possible without resolving the whole problem.
5. Work can be decomposed into `light`, `standard`, `extended`, or named `specialized` packets.
6. At least one plausible independent reviewer is available for the first packet.
7. Source access, redistribution, computation, and model-use rights are understood well enough for the planned public bundle.
8. The work requires no private personal data, confidential communication, unsafe access, or unbounded compute.
9. A negative result, failed method, literature correction, or exact reproduction would still be worth preserving.
10. Public wording can avoid hype, priority races, and unsupported claims of openness or novelty.

Defer records with ambiguous statements, unresolved publication rights, no review capacity, or a task that is useful only if a major theorem is solved in one jump.

### Target composition

Choose six to ten records as a set, not as a leaderboard:

- one apparently open or uncertain-status item for literature reconciliation;
- one known theorem with a clearly labeled calibration proof containing a deliberate defect;
- three or four selected Erdős or comparable established open problems with bounded literature, special-case, experiment, exposition, or formalization work;
- two or three precisely stated community conjectures; and
- across the set, at least one exact computation or replay packet and one formal-statement-correspondence or formalization-feasibility packet.

The deliberately flawed proof is a calibration artifact, never an accepted claim. Reviewers may be asked to locate the defect without being told where it is, but the artifact must be visibly labeled as a calibration exercise and must never be released as genuine evidence.

### Capacity rule

Do not open more submitted or in-review packets than the declared independent-review slots. As a default, each contributor holds one active packet, and each record has no more than two active packets. Stewards pause intake rather than allow generated work to outrun review.

## 4. Packet lifecycle

The durable state is the committed immutable packet snapshots, exact transition events, and review records—not an issue comment or a moved filename. The stable packet ID names the continuing task; every state below is a complete version-and-digest-bound snapshot. The event graph must have one root, no fork, and one derivable current head.

| State | Entry condition | Required action | Typical next state |
|---|---|---|---|
| Intake, not yet a packet state | An issue or steward note identifies a possible bounded task. | Check statement, provenance, rights, safety, utility, and reviewer capacity. | Create a `draft`, or leave the intake deferred/rejected with a reason. |
| `draft` | A packet record exists but one or more readiness fields or decisions remain open. | Complete scope, dependencies, inputs, outputs, checks, budget, boundary, and review plan. An intake rejected before readiness stays outside the packet queue with a recorded reason. | `ready` or `withdrawn`. |
| `ready` | Every launch field and reviewer lane is complete. | Offer the committed packet to compatible contributors. | `claimed`. |
| `claimed` | A steward records contributor, base commit, lease start, and expiry. | Contributor creates one packet branch. | `in_progress`, `ready` after lease release, or `withdrawn`. |
| `in_progress` | Work is occurring inside the lease and resource envelope. | Preserve checkpoints and stop at the packet's boundaries. | `submitted`, `blocked`, or `withdrawn`. |
| `blocked` | A stated dependency, permission, reviewer, resource, or scope condition prevents safe progress. | Record the minimal non-sensitive blocker and required decision. | `in_progress`, `ready`, or `withdrawn`. |
| `submitted` | Allowlisted evidence and validation receipts are tied to an exact commit. | Freeze that commit and assign required reviewers. | `under_review`. |
| `under_review` | Required reviewers have the exact submitted commit. | Review assigned facets. A changes-requested recommendation first creates a `state_transition` back to `in_progress`; any task-content change then creates a same-status `record_revision` before resubmission. | `accepted`, `rejected`, `challenged`, `in_progress`, or `withdrawn`. |
| `accepted` | All bounded packet acceptance gates pass. | Record exactly what the evidence supports; update mathematical, literature, computation, formalization, responsibility, and publication facets separately. | `closed`, or `challenged` if contrary evidence appears. |
| `rejected` | The submitted bundle fails a non-corrected gate or does not support its claimed scope. | Preserve the reason and useful negative evidence. | `closed`, or a new packet with a new scope. |
| `challenged` | New evidence disputes an accepted artifact. | Freeze promotion, open correction review, and preserve the challenged version. An upheld challenge returns through `under_review` before a new accepted snapshot is recorded. | `under_review`, `rejected`, `superseded`, `withdrawn`, or `closed`. |
| `superseded`, `withdrawn`, or `closed` | A replacement exists, work is withdrawn, or the lifecycle is complete. | Preserve history and link any replacement or correction. | Terminal for that packet version. |

Every transition records exact from/to snapshot references, event kind, actor, UTC date, basis commit, reason, and next owner. A `state_transition` changes only lifecycle fields, a `lease_update` changes only lease fields, and a pre-review `record_revision` is the only event allowed to alter task content. The schema's exact status enumeration controls the durable packet value; phrases such as “changes requested” and “useful negative result” are review dispositions or explanations, not invented packet statuses. Runs, evidence, and reviews bind the historical snapshot they actually used, and every event entering `accepted` preserves its exact evidence/review references even if a later snapshot is challenged or closed.

A `record_revision` begins a new task epoch even if a later revision restores identical-looking task content. Evidence, producer runs, reviews, and review runs from before the latest revision position cannot be reused for acceptance. They must be recreated against a snapshot in the current epoch with the same version-bound task contract as the accepted snapshot. This positional rule prevents a change-then-revert sequence from laundering stale review into a new acceptance.

### Leases

Suggested initial leases are three days for `light`, seven days for `standard`, and a steward-approved maximum of fourteen days for `extended` or `specialized` work. A contributor may request one renewal by posting a sanitized checkpoint. Operational handoff checks the current time; static validation remains time-deterministic so old commits do not decay. Expiry, renewal, release, or reassignment creates a new exact snapshot and event without deleting useful work or shaming the contributor.

## 5. Triage procedure

Within the group's declared triage window, a steward performs this sequence:

1. **Identify the object.** Distinguish an exact problem, a literature lead, a candidate argument, a computation, and a workflow suggestion.
2. **Freeze the target.** Record exact wording, definitions, source version, status date, and what would count as progress.
3. **Check provenance.** Credit the problem origin, source lead, prior attempts, and materially influential public ideas without seeking private transcripts or deanonymizing pseudonymous contributors.
4. **Check publication boundaries.** List allowed inputs and outputs, third-party rights, private-by-default material, external provider limitations, and retention.
5. **Check safety and feasibility.** Reject secret-bearing, privileged, unbounded, or legally unclear work. Select the smallest adequate resource envelope.
6. **Decompose.** Create a packet whose output remains useful even if the main conjecture stays open.
7. **Reserve review.** Name the independent review type and verify capacity before setting `ready`.
8. **Record a disposition.** Leave an incomplete intake outside the packet queue or create a `draft`; use `ready` only when every gate passes, and preserve a short reason for deferral, rejection, or withdrawal.

No triage decision may call a problem open solely because a tracker says so, or novel solely because a search returned nothing.

## 6. Thirty-day operating calendar

### Days 1–4: readiness and ownership

- complete the launch gate;
- name stewards, reviewers, record owners, and repository-continuity contacts;
- freeze the lifecycle vocabulary and minimal object templates;
- confirm branch protection and read-only public validation; and
- run `python tools/validate_packets.py --schema-only`, `python -m unittest discover -s tests -p 'test_*.py'`, `python tools/validate_packets.py --require-live`, `python tools/commons.py validate --require-live`, and `python tools/validate_repository.py` on a dummy live-record set from a clean clone.

**Exit gate:** one dummy packet can advance through exact immutable snapshots and events from `ready` through review to `closed` without relying on private chat history or unrecorded GitHub comments.

### Days 5–9: choose and freeze the calibration set

- evaluate candidate records against every selection gate;
- select six to ten records with the required mix;
- source-audit each statement and date its open-status assessment;
- create only the first bounded packet or two for each record; and
- reserve reviewer slots before setting packets to `ready`.

**Exit gate:** every ready packet has a responsible steward, exact base commit, resource envelope, publication boundary, outputs, checks, stop conditions, and review route.

### Days 10–14: first node runs

- have each contributor follow [NODE_HANDOFF.md](NODE_HANDOFF.md);
- start with `light` packets before `extended` or `specialized` work;
- keep prover and skeptic or literature lanes separate where feasible;
- preserve failed searches and exact continuation points; and
- revise instructions whenever two contributors make the same reasonable mistake.

**Exit gate:** at least one literature packet, one exact replay, and the flawed-proof calibration have been submitted as versioned evidence bundles.

### Days 15–20: independent review and revision

- open every cited primary source used for a material claim;
- attempt reconstruction or falsification of candidate mathematics;
- replay computational artifacts in a clean, bounded environment;
- check formal trust bases and informal-to-formal statement correspondence where applicable; and
- record a changes-requested review, return correctable work to `in_progress`, and make old reviews stale after changes.

**Exit gate:** the planted defect is found and explained, or the pilot records a review-system failure; every accepted bundle has an independent version-bound review.

### Days 21–26: disposition and correction drill

- separate packet acceptance from problem-status changes;
- record correctness, literature, computation, formalization, responsibility, and publication facets independently;
- run one deliberate challenge against an accepted calibration artifact;
- practice `upheld`, `corrected`, `superseded`, or `withdrawn` without deleting history; and
- reconstruct at least one accepted bundle from a clean clone.

**Exit gate:** no accepted status depends only on model consensus, self-review, inaccessible evidence, or an unrepeatable computation.

### Days 27–30: freeze and retrospective

- stop new intake and resolve or explicitly carry forward every active packet;
- create a reader that distinguishes accepted evidence, negative results, open challenges, and unresolved work;
- run repository, packet, link, privacy, rights, citation, and artifact checks;
- create or update the planned independent mirror and archive only if the release process is ready; and
- publish a retrospective before announcing mathematical significance.

**Exit gate:** the exact pilot state is reproducible from committed files, or the retrospective identifies precisely why it is not. A release may be deferred without calling the pilot a failure.

## 7. Evidence-bundle gate

The packet names the exact files. At minimum, a submission must make the following inspectable without the contributor's private conversation:

- exact packet snapshot ID, version, digest, path, base commit, and submitted commit;
- the exact problem-record reference—ID, version, digest, and path—and complete packet-transition history;
- the mathematical, bibliographic, computational, expository, or formal artifact;
- a sanitized run record identifying material tools, dates, task conditions, human interventions, resources, checks, limitations, and disclosure gaps;
- primary-source references with exact versions and enough notes to verify what is attributed to them;
- source and artifact hashes where the packet requires them;
- a rights manifest distinguishing Commons-originated CC0 material from third-party material and restrictions;
- failed approaches or known gaps relevant to evaluation;
- repository and packet-specific validation receipts; and
- an exact publication preview listing every file proposed for submission.

Raw prompts, full transcripts, chain-of-thought, private notes, personal context, credentials, unpublished communications, and unrelated local files are excluded by default. The contributor may voluntarily include a reviewed excerpt only when it is necessary, lawful, and explicitly allowlisted.

## 8. Review and acceptance

Acceptance is a sequence, not a vote:

1. **Scope gate:** outputs answer the frozen packet and do not smuggle in a broader claim.
2. **Structural gate:** repository and packet validators pass on the submitted commit.
3. **Privacy and rights gate:** only allowlisted files are present and every third-party component has a lawful public basis.
4. **Source gate:** material citations are opened and checked against exact claims.
5. **Method gate:** the appropriate independent reviewer reconstructs, attacks, or replays the work.
6. **Correspondence gate:** if formalization is used, a human checks that the formal statement matches the intended one.
7. **Disposition gate:** a human steward records what the evidence supports and what remains unchecked.

Git-backed acceptance has two protected integration phases because a record cannot honestly cite a commit that does not yet exist:

1. **Freeze submission (Phase A).** Merge the exact submitted packet snapshot, artifacts, producer run, and evidence with producer status `complete`. That status is not acceptance and must not claim an independent reconstruction that has not happened.
2. **Review the immutable ancestor.** The independent reviewer checks the exact Phase A evidence blob and records that protected-main commit in `reviewed_subject.git_commit`.
3. **Record acceptance (Phase B).** From Phase A, add the review run, completed review, under-review and accepted snapshots, and the transition that co-binds the unchanged evidence and exact review. Repository-aware validation must find the Phase A commit as an ancestor and reproduce its reviewed blob.

Phase A and Phase B must remain distinct protected-history phases. Squashing them, rewriting Phase A, or using an integration method that changes the cited Phase A identity invalidates the provenance and requires a new freeze and review.

Passing a packet means **the bounded evidence bundle met its stated acceptance tests**. It does not by itself mean the underlying problem is solved, the work is novel, or a journal has peer-reviewed it.

Packet status uses the versioned schema vocabulary. Mathematical, literature, computation, formalization, responsibility, and external-publication facets belong in the appropriate problem, run, evidence, review, and release records rather than in an invented combined score or unsupported “claim” object. In explanatory prose, “accepted” must expand to “accepted as bounded packet evidence.” If the project describes work as network-checked after its declared independent checks, it must still state that this is not journal peer review.

A potentially important new proof, disproof, or priority claim leaves the ordinary fast path. Freeze the exact artifact, label it preliminary, add specialist and prior-art review, avoid publicity, and seek an appropriate external venue. No steward or model may bypass this escalation because the 30-day clock is ending.

## 9. Corrections and incidents

For an ordinary mathematical or bibliographic correction:

1. identify the exact claim, packet, commit, and release;
2. supply the smallest public evidence needed to reproduce the concern;
3. mark the affected status `challenged` without deleting the old version;
4. assign a reviewer who did not approve the disputed point where feasible;
5. record whether the review disposition was upheld, corrected, superseded, or withdrawn, then emit only the packet snapshot and transition permitted by the schema; and
6. issue a new version with bidirectional links to the earlier record.

A secret, private-data disclosure, malicious file, or rights complaint is an incident, not an ordinary public challenge. Stop publication and notify a steward privately with minimal details. Rotate exposed credentials immediately through the relevant provider. Do not copy sensitive material into an issue to prove it exists. Git history is not assumed to erase a disclosure.

## 10. Measures for the retrospective

Record quantities that improve the protocol, not a model leaderboard:

- records proposed, accepted, deferred, and rejected;
- packets by type and resource envelope;
- completion, expiry, withdrawal, and revision counts;
- contributor time, reviewer time, and queue delay;
- citations corrected, prior results found, and statement defects found;
- candidate arguments rejected and exact failure reasons;
- computations replayed and replay failures;
- formal statements compiled and correspondence defects found;
- privacy, rights, security, and validation failures caught before publication;
- Git or onboarding steps that required steward help; and
- work that remained useful without solving an open problem.

The retrospective must report the planted-proof outcome and any false positive. Honest negative results and caught defects count as pilot successes.

## 11. Current, pilot-build, and future limits

| Layer | Honest status |
|---|---|
| Published and available candidate | DOI-bearing concept documents, rights and privacy rules, public intake, Git history, protected integration, versioned operational records, semantic and structural validators, adversarial tests, manual packet/agent CLI, operations and handoff guides, and an elementary calibration collection. |
| Launch gates still unmet | Selected six-to-ten-record set, live packet instances and transition histories, named steward/reviewer roster, independent-review capacity, a real claimed-packet handoff drill, publication-preview drill, and tested mirror/release path for pilot evidence. |
| Manual pilot operation | Forks or clones, one branch per packet, steward assignment, explicit resource envelopes, human publication preview, pull requests, version-bound reviews, and human disposition. |
| Future only | Polished one-click Node Kit, automatic capability routing, non-Git mass onboarding, bidirectional forge federation, broad archival and translation trees, volunteered local CPU/GPU routing, and genuinely local peer-to-peer inference or training. |

No current command automatically selects a packet, verifies mathematics, routes compute, sanitizes private context, assigns reviewers, or publishes an accepted result. Those steps remain explicit and human-supervised during the pilot.

## 12. End-of-cycle deliverables

At Day 30, deliver:

- the frozen list of six to ten records and their source/status receipts;
- every immutable packet snapshot and append-only packet-transition event tied to exact commits;
- accepted evidence, closed negative work, challenges, and correction records;
- reviewer scope declarations and version-bound dispositions;
- a sanitized tool/resource and reviewer-load summary;
- a clean-clone reconstruction receipt for at least one accepted artifact;
- a release or a documented reason release was deferred; and
- the retrospective with concrete protocol changes for a second cycle.

Do not convert an unfinished or challenged artifact into a success claim for the sake of completing the calendar.
