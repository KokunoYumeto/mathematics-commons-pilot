# Mathematics Commons: GitHub Pilot Implementation Guide

**Status:** Technical design for the first proof-of-concept  
**Date:** 6 August 2026  
**Audience:** Initial stewards and contributors who can already operate an AI coding/research agent but may not know GitHub administration

> **Privacy presumption:** ordinary AI interactions and local working context are private by default. This workflow publishes only a contributor-approved, data-minimized evidence bundle. It does not require raw prompt histories, transcripts, chain-of-thought, credentials, personal data, unpublished communications, or unrelated local files. Disclosure remains proportionate to ordinary mathematical, academic, institutional, and destination-venue integrity requirements.

“Private by default” describes the Commons' own collection and publication boundary. It is not a promise about a chosen model provider's retention, training, account, or legal terms; those must be assessed separately and any material limitation disclosed.

## 1. The short answer

Do not begin by building a custom peer-to-peer network.

Begin with one public GitHub organization and one protected pilot repository. Contributors work in their own forks or clones, so the work and compute are already distributed. Pull requests provide a visible integration queue. Independent mirrors and archived releases prevent the central GitHub repository from becoming the only durable copy.

The pilot is decentralized in the ways that matter first:

- many people control their own working copies and agents;
- every clone contains the Git history;
- scientific state is stored in portable files rather than only in GitHub pages;
- review is performed by independently operated nodes;
- another host can mirror the repository;
- releases are archived outside GitHub; and
- no model provider receives mathematical authority from supplying compute.

GitHub is the meeting place, not the owner of the mathematics and not the source of truth about whether a theorem is correct.

## 2. Five Git concepts in ordinary language

| Term | Meaning in this project |
|---|---|
| Repository | The project folder plus its complete version history. |
| Clone | A full local copy. A clone can survive even if GitHub disappears, although GitHub-only issues and discussions are not included. |
| Branch | A temporary line of work for one bounded packet. It prevents an unfinished attempt from altering the accepted record. |
| Pull request | A proposal to merge one branch into the protected accepted record. It is a review interface, not proof of correctness. |
| Fork | A contributor's GitHub-hosted copy of the repository. It lets someone propose work without receiving write access to the central repository. |

An **issue** coordinates a task. A **Research Packet** is the durable task specification committed as immutable snapshots connected by exact events. If an issue disappears, the packet history, evidence, and review records must remain reconstructible from a clone.

## 3. What to create

### 3.1 One repository now; one neutral organization when ownership is ready

The public bootstrap repository currently lives under one pseudonymous maintainer account. That makes a shareable proof of concept possible, but it is a disclosed continuity risk rather than the intended mature ownership model. Do not transfer it merely to make the topology look complete.

Once two trusted humans have tested access, 2FA recovery, roles, and migration, move the pilot to a neutral GitHub organization. Keep owner membership small, require the reviewed security policy, and preserve the old URL through GitHub's redirect plus the documented mirror and DOI records.

The project initially needs only one public repository:

```text
mathematics-commons-pilot
```

Do not create one repository per conjecture. Repository sprawl makes standards, search, review, and backup harder before the workflow is stable.

### 3.2 One repository tree

```text
mathematics-commons-pilot/
├── README.md
├── START_HERE_FOR_HUMANS.md
├── START_HERE_FOR_AGENTS.md
├── CONTRIBUTING.md
├── CITATION.cff
├── LICENSE
├── RIGHTS.md
├── LEIDEN_ALIGNMENT.md
├── PILOT_OPERATIONS.md
├── problems/
├── packets/
├── transitions/
├── sources/
├── runs/
├── evidence/
├── reviews/
├── work/
│   └── <packet-id>/
├── schemas/
├── tools/
├── examples/
├── releases/
└── .github/
    ├── ISSUE_TEMPLATE/
    ├── pull_request_template.md
    ├── CODEOWNERS
    └── workflows/
```

GitHub issue forms can provide friendly structured intake, but accepted scientific state must be converted into the files above. GitHub documents issue forms under `.github/ISSUE_TEMPLATE/` and supports required fields and automatic labels. See [GitHub's issue-form syntax](https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/syntax-for-issue-forms).

## 4. Human roles for the pilot

Start with roles, not a complicated constitution.

| Role | GitHub access | Responsibility |
|---|---|---|
| Organization owners | Owner; ideally two people | Account recovery, security, and organization settings. Not automatic mathematical authority. |
| Stewards | Maintain or write | Triage intake, create packets, manage leases, enforce process, assemble releases. |
| Reviewers | Usually triage or write as needed | Review exact artifacts within a declared scope. |
| Contributors | Read; work through forks | Claim packets and propose evidence bundles through pull requests. |
| Responsible claimants | No special GitHub permission required | Accept responsibility for a particular promoted mathematical claim. |

The repository includes `.github/CODEOWNERS` for the workflow, schemas, validators, tests, and the ownership file itself. During the one-maintainer bootstrap it identifies the present human trust boundary and requests review, but it cannot turn self-review into independent review. Expand these owners and enable required code-owner approval when an independent steward joins. GitHub permits CODEOWNERS in public repositories and can require their approval before merge. See [GitHub's CODEOWNERS documentation](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners).

## 5. The durable objects

The operational MVP uses seven record types. Each record has a stable ID for the continuing object, a record version for one immutable snapshot, and a complete normalized digest when another record references it.

| Record | What it freezes |
|---|---|
| Problem | Exact statement, variants, provenance, dated status, source graph, rights boundary, and what would count as resolution. |
| Research Packet | One bounded task snapshot: scope, lease, inputs, outputs, acceptance tests, capabilities, risks, review path, rights, and publication boundary. |
| Packet transition | One append-only event from an exact packet snapshot to another exact snapshot. |
| Source | Identity, authority, locators, hashes where available, component-level rights, and permitted uses. |
| Run | Sanitized material tool/process disclosure, exact packet snapshot, inputs, outputs, resources, checks, and limitations. |
| Evidence | One exact artifact or claim-support bundle, its checks, status, and packet snapshot. |
| Review | The exact evidence, artifacts, packet snapshot, commit, review facet, findings, checks, and limits inspected by an independent lane. |

Coexisting versions are expected. The validator derives one no-fork current packet head from exact transition events; it does not overwrite the earlier packet file. Runs, evidence, and reviews stay attached to the historical packet snapshot they actually used.

### 5.1 Problem

A problem record states:

- stable ID and exact formulation;
- source and provenance;
- definitions and conventions;
- current status and date checked;
- known partial results and relevant literature;
- what would count as a solution or counterexample;
- residual uncertainty; and
- responsible maintainer.

For an Erdős problem, the record links the exact erdosproblems.com entry and primary literature. It never assumes that the website's status is infallible or current.

### 5.2 Research Packet

A packet snapshot fixes one bounded task: exact question and exclusions; stop conditions; problem and source references; declared output paths; mandatory and optional acceptance criteria; tool, time, spend, CPU, RAM, GPU, storage, upload, network, and execution bounds; risk classes; required review facets; formalization and correspondence requirements; public/private submission boundary; component rights; steward; credit roles; and limitations.

The normative fields are the [Research Packet schema](schemas/research-packet.schema.json), and the complete mechanics example lives under [`examples/calibration/`](examples/calibration/). Do not copy an illustrative prose fragment into the live queue. Start from a reviewed current schema and validate the complete record graph.

### 5.3 Run

A run records, in sanitized and proportionate form, what a person and their tools materially did: functional task specification, model/tool versions and dates, material human interventions, commands or queries needed for evaluation, approved inputs and outputs, hashes, resources, checks, limitations, and material disclosure gaps. It is not a dump of the person's private interaction history. A prompt or transcript is not proof; optional excerpts remain contributor-controlled and receive privacy, confidentiality, security, and rights review.

### 5.4 Evidence

An evidence record identifies one exact submitted artifact or support bundle, binds it to the historical packet snapshot and producer run, records exact checks and limitations, and states only the status the bytes support. Mathematical, literature, computation, and formalization facets remain distinct; there is no single confidence score.

### 5.5 Review

A review names the exact packet snapshot, evidence version, artifacts, and commit and states what was checked, how, by whom, with which tools, and what was not checked. Favorable AI commentary is not self-authenticating; the reviewer remains responsible for the recommendation.

## 6. The actual contribution cycle

### Step 1: propose and triage

A contributor opens one of four issue forms:

- propose an established open problem;
- propose a community conjecture;
- submit a literature lead;
- report an error or attribution concern.

A steward checks that the item is stated precisely enough to become a record. A raw model answer is not yet a packet.

### Step 2: freeze the problem record

The steward commits the exact statement, sources, conventions, current status, predecessor reference, and unresolved questions. Changing it later creates a new immutable version linked to the exact previous snapshot; no-fork lineage makes one current problem head derivable without silently changing the target.

### Step 3: create small packets

Split the work into independently useful tasks. Typical first-pilot packets are:

- open-status and literature audit;
- primary-source citation verification;
- independent problem restatement and edge-case audit;
- search for small counterexamples;
- proof attempt on one named lemma;
- exact computation or replay;
- adversarial review of a submitted proof;
- Lean/Coq/Isabelle feasibility or formalization;
- human-readable synthesis of accepted evidence.

### Step 4: claim a packet

During the pilot, claiming can be simple:

1. request `claim` on the linked issue;
2. a steward creates a new packet snapshot with the claimant, exact base commit, branch, start, expiry, and incremented lease generation;
3. the steward commits the exact `lease_update` or lifecycle event connecting the old and new snapshots;
4. the contributor creates the recorded branch from the exact handoff commit; and
5. the operator independently records the steward-approved full current-head SHA as `<HANDOFF_COMMIT>`, and `python tools/commons.py agent-brief --packet-root packets <PACKET_ID> --expected-handoff-commit <HANDOFF_COMMIT> --approve-safety` must pass before the agent receives authority to work.

Leases should expire. Expiry is checked at operational handoff time rather than making a frozen commit's static validity change with the wall clock. Releasing or renewing a lease creates another exact snapshot and event; it never rewrites the claimed snapshot.

### Step 5: let the local agent orient itself

The contributor opens the clone or download in Codex, Claude Code, or another chosen workflow and says:

> Read `START_HERE_FOR_AGENTS.md` and packet `<ID>`. Work only within its scope. Run its acceptance checks and package the required evidence. Do not promote the claim yourself.

The packet, not a clever improvised prompt, carries the durable instructions.

That local interaction remains private by default. Before submission, the contributor or agent assembles only the packet's allowlisted outputs and shows an exact publication preview; unrelated conversation and local state stay outside the bundle.

### Step 6: submit an evidence bundle

The submission includes only the packet-owned `work/<packet-id>/` outputs, a sanitized run record, sources, hashes, limitations, and self-check receipts. Every public non-infrastructure artifact needs an exact problem, source, or evidence manifest covering its repository path, byte size, SHA-256, allowlist, rights, redaction, publication preview, retention, and redistribution status. Readable strict-UTF-8/no-NUL bytes are scanned for bounded secret and private-path signatures regardless of their filename extension; opaque media remains exact-manifest and human-preview gated rather than being decoded lossily. The signature scan is a bounded defense, not a proof that an artifact is private-data-free or rights-cleared. The agent brief treats resource caps as human-enforced obligations rather than pretending they form an operating-system sandbox. A validator rejects missing fields and unexpected private or undeclared files before mathematical reviewers spend time on it. Raw transcripts and complete prompt histories are not required.

### Step 7: independent review

The system creates separate review packets. A literature reviewer opens the cited sources. A mathematical reviewer tries to reconstruct or break the argument. A computation reviewer replays the artifact. A formal reviewer checks the trust base and statement correspondence.

No node accepts its own work. Reviewers see the exact submitted packet, evidence, artifacts, and commit. A substantive revision creates new snapshots and requires new review; an old review never floats to the current head.

### Step 8: disposition and release

A human steward records an allowed lifecycle event such as revision, acceptance of the bounded packet evidence, rejection, challenge, withdrawal, supersession, or closure. Mathematical status, literature status, formalization, publication, and responsibility remain separate evidence facets rather than invented packet statuses. “Accepted as bounded packet evidence” and “network-checked” are never represented as journal peer review or proof merely by model consensus.

## 7. Capability envelopes

Use coarse, changeable labels rather than product prices in durable records.

| Envelope | Typical packet | Approximate shape |
|---|---|---|
| `light` | Verify one citation, inspect one case, summarize one primary paper | Minutes to two hours; small context; little or no code. |
| `standard` | Bounded literature audit, lemma attempt, small exact computation | A few hours; ordinary paid-agent context and tools. |
| `extended` | Multi-paper synthesis, long proof audit, substantial formalization | Larger context/budget; explicit checkpoints and stop conditions. |
| `specialized` | Lean/Coq/Isabelle, OCR, GPU, certified numerics, large search | Named tool or hardware requirement; isolated execution. |

A small subscription should receive a smaller coherent packet, not a lower evidentiary standard. A larger subscription should receive larger scope, not authority. During the pilot, people choose from filtered labels; automatic routing can come later.

## 8. GitHub settings that matter

Protect the default `main` branch with a repository ruleset or branch protection:

- changes through pull requests only;
- at least one independent approval;
- required validation checks;
- no force pushes;
- no branch deletion;
- stale approvals dismissed when reviewed files change; and
- maintainer bypass limited and recorded.

During a one-maintainer bootstrap, requiring one approval would make every release impossible. The current repository therefore requires the pull-request path and public validation check but temporarily requires zero approvals. This is an explicit human trust boundary: a contributor can propose changes to the same workflow, validators, schemas, or tests that produce the green check, so the named maintainer must manually review those diffs against protected `main`; CI is not self-authenticating. The checked-in CODEOWNERS file makes that boundary visible. Raise the count to one, require code-owner approval, and require last-push approval as soon as an independent write collaborator is recruited; the bootstrap exception is not the intended pilot review standard.

Organization-level rulesets are a later convenience and some features depend on the GitHub plan. Repository-level protection is enough for the pilot. GitHub documents the available [repository rulesets](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets).

Create one organization-level GitHub Project only if the group finds the board helpful. It can show packet status, type, capability envelope, problem family, and reviewer need across issues and pull requests. It is a dashboard, not the scientific database. See [GitHub Projects](https://docs.github.com/en/issues/planning-and-tracking-with-projects/learning-about-projects/about-projects).

## 9. Security rules

Public pull requests contain untrusted input.

- Use GitHub-hosted runners for cheap schema and text checks.
- Give workflow tokens read-only permissions unless a specific job needs more.
- Pin third-party Actions to full commit hashes.
- Do not use a privileged `pull_request_target` workflow to check out and run contributor code.
- Never connect a personal persistent machine containing credentials as a runner for arbitrary public pull requests.
- Triage code before running expensive or specialized jobs in an isolated, disposable environment with no secrets.
- Treat PDFs, archives, solver files, prompts, and generated source as untrusted.
- Give every module an explicit privacy boundary: allowlisted inputs and destinations, public/private/restricted/temporary classifications, a retention rule, and an exact pre-publication preview. Deny unrelated local context by default.

GitHub recommends keeping self-hosted runners away from untrusted public fork workflows because a pull request can execute hostile code. Its workflow syntax also allows an explicit read-only `GITHUB_TOKEN`. See GitHub's [runner-access warning](https://docs.github.com/en/actions/how-tos/manage-runners/self-hosted-runners/manage-access) and [workflow-permissions documentation](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax#permissions).

### 9.1 Two-factor authentication continuity

GitHub currently uses TOTP or SMS for initial 2FA enrollment and recommends TOTP; a passkey or security key then provides a strong backup. The Commons recommends TOTP, a backup on a separate failure domain, and securely stored one-time recovery codes. Enabling 2FA does not revoke existing PAT or OAuth tokens, change SSH authentication, or add TOTP prompts to ordinary authenticated Git operations.

Local agents must use the configured credential helper without retrieving or logging its credential. Prefer the repository-scoped built-in Actions token for same-repository workflows and GitHub Apps for unattended cross-repository automation. At least one week before organization-level enforcement, appoint two tested owners and audit members, billing managers, outside collaborators, and bot or service accounts. Review OAuth-app and PAT policies separately: those controls can interrupt access even though 2FA enrollment does not. Follow [GITHUB_2FA_CONTINUITY.md](GITHUB_2FA_CONTINUITY.md) for the official behavior, project recommendations, credential-storage check, smoke tests, rotation, and lockout recovery.

## 10. Mirroring without creating chaos

Every ordinary clone already contains the Git history. A formal mirror adds an independently controlled destination that is kept synchronized. The pilot uses one-way synchronization only; it does not automatically merge changes back from two hosts.

Follow the [one-way mirror runbook](MIRROR_RUNBOOK.md). It separates the primary and destination remotes, requires a dedicated empty destination, makes the destructive deletion semantics of `git push --mirror` explicit, requires a dry run and human approval, and records read-back verification. If the primary fails, the stewards can explicitly promote a verified mirror. No independent mirror destination is claimed until that procedure has actually passed.

GitHub's official [repository duplication guide](https://docs.github.com/en/repositories/creating-and-managing-repositories/duplicating-a-repository) documents bare and mirrored clones. Git mirroring does not preserve GitHub issues, project boards, or review comments, which is why mathematically material state must also be committed as files.

For releases:

1. freeze a version;
2. run validation from a clean clone;
3. sign or otherwise protect the release tag;
4. generate a checksum manifest and reader/evidence bundle;
5. create a GitHub release;
6. archive it through Zenodo; and
7. verify the public files, DOI metadata, and hashes.

Zenodo can ingest enabled GitHub releases and assign durable records; see [Zenodo's GitHub integration](https://help.zenodo.org/docs/github/) and [repository-enablement guide](https://help.zenodo.org/docs/github/enable-repository/).

## 11. What to put in the first pilot

Start with approximately six to ten problem records, not hundreds.

- three or four selected Erdős or comparable established open problems with bounded, plausible subquestions;
- two or three rigorously stated community conjectures;
- one item whose “open” status is deliberately uncertain, to test literature and source reconciliation;
- one known theorem accompanied by a plausible flawed proof, to test whether review catches it.

Selection criteria:

- exact public statement and stable source;
- enough surrounding literature to evaluate progress;
- bounded subproblems accessible to the available contributors;
- outputs that remain useful without a full solution;
- no obvious safety, privacy, or rights problem;
- at least one plausible independent reviewer; and
- diversity of packet kinds rather than a single theorem-solving leaderboard.

An “open-door” problem is a project label, not a claim that a problem is easy. It means the problem offers bounded literature, experiment, special-case, or formalization work that can produce useful evidence within the pilot.

## 12. Thirty-day operating order

### Days 1–4: ratify the existing repository and rules

- retain the disclosed personal-account bootstrap or migrate only after two tested organization owners are ready;
- appoint the initial stewards and reserve independent review capacity;
- review and ratify the existing start files, policies, seven schemas, templates, validator, and CLI;
- verify protected `main`, read-only default Actions permissions, 2FA continuity, and recovery from a clean clone; and
- establish and test the independently controlled one-way mirror destination before accepting irreplaceable work.

### Days 5–9: calibration

- add the uncertain-status and deliberately flawed calibration items;
- create the first packet tree;
- have every initial contributor complete one small packet;
- revise instructions wherever people improvise around them.

### Days 10–20: real pilot work

- add selected Erdős and community records;
- run independent literature and mathematical lanes;
- keep active work below available review capacity;
- preserve failures, objections, and exact continuation cursors.

### Days 21–26: adversarial review

- source-audit citations;
- reconstruct or attack the strongest claims;
- replay computations in clean environments;
- formalize a proportionate component where useful;
- request external help for anything potentially significant.

### Days 27–30: release and retrospective

- freeze and validate the pilot release;
- mirror and archive it;
- publish a plain-language summary with exact status labels;
- document false positives, caught errors, reviewer time, compute cost, Git friction, and changes required for the next cycle.

The pilot succeeds if it produces durable, independently reviewable work and identifies failure modes. Solving an open problem is welcome but not a success criterion.

## 13. Explicitly later, not part of this build

- a polished one-click Node Kit for people unfamiliar with agents or Git;
- automatic routing from live subscription and hardware profiles;
- archival scan recovery, diplomatic transcription, canonical editions, and Stacks-style integration as additional project-tree variants;
- language packs and translation queues prioritized by marginal intelligibility gain;
- a geographically and linguistically broad public onboarding program;
- bidirectional multi-forge federation;
- volunteered local CPU/GPU workloads; and
- genuinely local peer-to-peer model inference or training on rights-cleared corpora.

The pilot should preserve compatibility with those ideas through open schemas, stable IDs, packet boundaries, mirrors, and rights metadata. It should not pretend to have implemented them.

## 14. Decisions needed before the live pilot or organization migration

Only a few human choices cannot be made by the technical design:

1. whether and when the current public repository should migrate to an organization;
2. the two initial organization owners before that migration;
3. the initial stewards and reviewer pool;
4. ratification of the CC0 Commons rule plus the third-party component and exception inventory;
5. which six to ten records from the audited docket enter the capacity-backed live set; and
6. the independent mirror destination.

The current personal-account repository can host the concept and technical calibration. The live collaborative pilot should not depend on an organization migration until those continuity choices are made.
