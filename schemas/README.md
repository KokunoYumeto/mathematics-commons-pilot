# Pilot record schemas

This directory contains both the practical packet-library contracts and the preserved pilot record contracts. All use **Draft 2020-12 JSON Schema**. Passing validation proves declared structure and exact identities; it does not by itself establish source rights, mathematical correctness, linguistic quality, or independent certification.

## Practical packet-library schemas

| File | Purpose |
|---|---|
| `job-meta.schema.json` | Generator input for the exact admitted packet metadata and explicit exclusions. |
| `job-catalog.schema.json` | Public 28-job release catalog, interaction contract, assets, and hashes. |
| `job-asset.schema.json` | Exact ZIP-part and source-member manifest for one job or the translation kit. |
| `translation-catalog.schema.json` | Open-education source, license, state, QA, and language-adoption catalog. |
| `formalization-intake.schema.json` | Exact external Lean/source snapshots and separate build, placeholder, statement-correspondence, Mathlib-audit, and packet-admission states. |
| `portal-catalog.schema.json` | Exact Transcription, Translation, and Open-problems section index with release asset identities and limitations. |
| `catalog-check.schema.json` | Generated replay receipt binding the catalogs, schemas, asset-manifest tree, counts, bytes, and ZIP-member validation state. |
| `release-readback.schema.json` | Anonymous HTTPS post-publication receipt for one immutable release, its exact asset set, and commit-pinned raw files. |

The executable validator is `tools/validate_jobs.py`. Consumers should fetch the related catalogs, schemas, receipts, and manifests from one exact Git commit. Release asset identities are byte length plus SHA-256; a mutable URL or filename is not sufficient. `catalog/readback.json` records the independently observed public bytes for its immutable subject commit and release. Its expected and observed fields must agree exactly with the job catalog, and the catalog check binds the receipt by path, byte length, and SHA-256.

## Preserved pilot record schemas

The original pilot contract is version **`0.1.0`**. It remains deliberately small, strict, and provisional.

## Schema inventory

| File | Authoritative `record_type` | Purpose |
|---|---|---|
| `problem-record.schema.json` | `problem_record` | Freezes one durable mathematical subject and its exact no-fork predecessor: statement artifact, definitions, provenance, source-bound dated status assessment, steward, publication boundary, rights, and limitations. |
| `research-packet.schema.json` | `research_packet` | Freezes one immutable full snapshot of a bounded task, its state, sources, outputs, acceptance criteria, risks, capability envelope, privacy and rights boundaries, and required review path. |
| `packet-transition.schema.json` | `packet_transition` | Records one append-only event between exact immutable packet snapshots, with event kind, sequence, from/to state, actor, UTC time, state-basis commit, reason, next owner, and optional exact evidence/review references. |
| `source-record.schema.json` | `source_record` | Records exact source identity, bytes, provenance, authority checks, layered third-party rights, permitted uses, and redistribution status. |
| `run-record.schema.json` | `run_record` | Gives a sanitized functional account of material tools, human interventions, inputs, outputs, checks, resources, and disclosure gaps. |
| `evidence-record.schema.json` | `evidence_record` | Manifests one exact evidence artifact with path, size, SHA-256 digest, dependencies, checks, reproducibility state, formalization state, rights, and limitations. |
| `review-record.schema.json` | `review_record` | Binds an independent review to an exact version, digest, Git commit, and path; records what was and was not checked, findings, disposition, and the formal-review lane. |

Every one of the seven instance schemas has a canonical `$id`, requires `record_type`, and fixes `schema_version` to `0.1.0`. Dispatch by `record_type`; do not guess a schema from a filename.

## Public submission boundary

These schemas implement privacy by allowlist:

- The root object and bounded nested objects use `additionalProperties: false`. A submitted JSON record may contain only declared fields.
- `submission_boundary.allowlisted_artifact_ids` is the file-level allowlist. A local file is not part of a submission merely because a tool could access it.
- `private_by_default` and `schema_fields_are_public_allowlist` are fixed to `true`.
- Raw transcripts, prompt histories, chain-of-thought, private notes, unpublished communications, personal context, credentials, and unrelated local files are explicitly excluded by default.
- `raw_interaction_records_required` is fixed to `false`. The run record asks for a sanitized functional task specification, material tool roles, human interventions, evidence, checks, limitations, and disclosure gaps—not the private interaction history.
- Redaction and exact publication-preview states are explicit. A record should not be released while either remains pending or failed.

Schema validation cannot detect private data hidden inside an otherwise allowed string. The contributor and reviewer must still inspect the exact proposed JSON and artifact bundle. If privacy, confidentiality, security, or third-party rights prevent proportionate disclosure, record a disclosure gap and narrow the claim; do not compel unrelated private material.

## CC0 and third-party rights

`submission_rights` applies CC0 1.0 only at the intentional submission boundary:

- The new Commons record and named Commons-originated submitted components use `dedication: "CC0-1.0"`.
- `dedication_scope` makes clear that the dedication does not sweep in an underlying transcript, private context, or unsubmitted file.
- `third_party_rights_preserved` is fixed to `true`, and incorporated sources are named by stable source IDs.
- Redistribution is always explicit: `permitted`, `restricted`, `unresolved`, or `metadata_only`.

`metadata_only` permits a record that contains locator, provenance, and digest metadata without redistributing the described bytes. It is not sufficient when the collection checks in and publishes the artifact bytes themselves; release-ready checked-in records and artifacts require `permitted` redistribution.

The source schema is stricter because a CC0 metadata record may describe a non-CC0 work. It fixes `described_source_content_dedicated_under_cc0` to `false` and records separate rights layers for the original work, edition, scan, translation, annotation, figure, dataset, software, or other component. Copying, extraction, translation, redistribution, and model-training permissions are separate fields; freely accessible is not treated as openly licensed.

For this MVP, a checked-in problem statement must use `exactness: "canonical_project_statement"`: Commons-originated canonical wording with its own exact artifact hash. Verbatim or normalized third-party wording is not silently swept into CC0; supporting it requires a later explicit origin and per-statement rights contract.

These fields record a reviewed assertion and its uncertainty. They do not themselves grant permission, erase a right, or replace jurisdiction-specific legal review.

## Identity, versions, and hashes

- Stable IDs are public identifiers. Do not place a private email address, credential, or unnecessary identity linkage in one. A durable public pseudonym is acceptable.
- `schema_version` identifies this contract. Exact record identity is the triple `(record_type, stable ID, record_version)`. Distinct versions of one stable ID may coexist; duplicate exact triples are rejected.
- Change `record_version` whenever serialized public content changes. Preserve the old complete record bytes and add a new version; never overwrite an earlier reviewed or referenced snapshot.
- Artifact integrity digests are lowercase SHA-256 values over the exact referenced bytes.
- Record-reference digests bind the complete UTF-8 JSON serialization after normalizing CRLF and bare CR line endings to LF. Key order, whitespace other than line endings, and all values remain significant. This explicit policy keeps record references stable across Git `core.autocrlf` settings without pretending that semantically equivalent JSON has one canonical byte form.
- Record references carry the target stable ID, record version, and full normalized-record digest. Resolution uses all three identity fields and the complete digest, never a mutable-field-excluding projection. A review additionally fixes the Git commit and artifact path. Any substantive serialized change makes the prior review stale; CRLF/LF conversion alone does not.
- A problem record separately binds its exact statement artifact path, version, byte count, and exact-byte SHA-256 digest. Every packet `subject_id` must also have one matching `problem_record` dependency carrying the exact problem-record version and normalized digest. The semantic validator resolves that dependency and verifies the problem's statement artifact and source references.
- Every non-root problem version carries `previous_problem_ref` with its predecessor's exact ID, version, and full normalized digest. The validator requires one root, no forks or cycles, a strictly later successor timestamp, complete connectivity, and one unambiguous problem head. Historical packets remain bound to the exact older problem version they used.
- A record does not contain a self-referential hash of its own complete JSON. Release or bundle manifests should hash the finished record file after serialization.

Canonical semantic serialization is not defined in `0.1.0`. Producers must preserve the reviewed serialization; only line-ending normalization is part of the record-reference hash policy.

## Bounded work and explicit state

A Research Packet is ready only when it has:

- an exact question, included work, excluded work, stop conditions, and continuation cursor;
- a durable lease that records claim state, public claimant ID, expiry, exact base commit, branch, and monotonically increasing generation;
- versioned and hashed source inputs with permitted uses;
- named expected outputs and machine-addressable acceptance criteria;
- a bounded time/tool/network/execution envelope and six-axis risk classification;
- when an operational handoff is requested, output paths confined to `work/<packet-id>/...`, acceptance commands expressed as a direct argument vector plus an existing repository-relative `cwd` (never a shell string), and maximum paid-spend, CPU, RAM, GPU, storage, and upload budgets; omission means empty allowlists and zero budgets, not unlimited access;
- a version-bound independent review plan in which the producer cannot accept their own work; and
- explicit privacy, CC0, third-party-rights, responsibility, credit, status, and limitations fields.

Every applicable instance record requires its schema-defined status fields and a structured `limitations` object. Use `known` with concrete items when there are gaps, `not_assessed` when the check has not occurred, and `none_identified` only after an appropriate check. “None identified” is not a guarantee that none exist.

### Lease invariant

An `unclaimed` packet has generation `0` and null claimant, timestamps, base commit, and branch. Every claimed or historical lease state has generation at least `1` and preserves all five concrete values. Increment the generation whenever a new claim or lease epoch is created; packet ID plus generation is the optimistic-concurrency key. `claimant_id` is a public project identifier or public pseudonym, not a demand for private identity data.

The portable semantic validator checks static lease timestamp ordering and packet/lease state compatibility without consulting the wall clock, so a frozen historical collection remains reproducible. Repository-aware node handoff performs the live-time expiry check and additionally checks the current branch, a clean initial worktree, `git check-ref-format`, and whether `base_commit` exists and is an ancestor; those checks cannot be expressed by portable JSON Schema alone.

### Append-only transition invariant

Each Research Packet version is a complete immutable snapshot. A transition contains exact `from_packet_ref` and `to_packet_ref` objects, each binding the same stable packet ID plus one record version and full normalized-record digest. Adding a later snapshot/event must not alter any earlier snapshot or event bytes. The validator requires one draft root, complete connectivity, no cycles, forks, or multiple predecessors, continuous sequence numbers beginning at `1`, strictly increasing UTC event times, and one unambiguous head. CLI listing, display, and handoff select that derived head rather than guessing from filename, modification time, status, or semantic-version order.

`event_kind` distinguishes three diff classes. `state_transition` must change status along the legal lifecycle graph and may alter only lifecycle state, lease, version, update time, and the continuation cursor. `lease_update` preserves status and may alter only lease, version, and update time. `record_revision` preserves status and lease and is the only content-changing event; it is prohibited once a packet is submitted, under review, accepted, rejected, challenged, or terminal, so reviewed work cannot silently inherit old acceptance after changing criteria, dependencies, outputs, or scope. Terminal states cannot acquire an ordinary state transition.

Every `record_revision` starts a new task epoch identified by its position in the exact transition chain, not merely by the resulting field values. Acceptance evidence, its producer run, every accepting review, and every review run must bind snapshots at or after the latest revision epoch inherited by the accepted snapshot and must share that snapshot's version-bound task-content projection. Revising a task and later restoring byte-for-byte equivalent task fields therefore does not revive evidence or reviews from before the revision. After changes are requested, first return the packet to `in_progress`, record the task revision there, and produce fresh evidence and review for the new epoch.

An evidence record's `status: "complete"` means only that its producer finished and froze the artifact. Evidence cannot declare itself accepted. Network acceptance exists only as a collection-level predicate: an exact state transition into `accepted` must co-bind the exact complete evidence versions and exact completed independent review versions, and all packet, output, criterion, reviewer, rights, formalization, correspondence, reproduction, and revision-epoch gates must pass on those bound records. This applies to every evidence reference on the acceptance transition, including packet outputs marked optional; optional means the transition may omit the output, not that it may accept a partial, failed, restricted, or rejecting-review version. The complete acceptance gate runs against every accepted snapshot even if a later head becomes challenged, closed, or superseded. Stable-ID-only evidence mentions inside review criteria are resolved through that exact acceptance-event evidence set and must identify one version. Likewise, an evidence record's reproduction-review ID is resolved through the exact evidence/review pairing in a transition; absent or ambiguous pairings fail. This one-directional event binding avoids an impossible content-hash cycle between evidence and a review that itself hashes that evidence.

`git_commit` means the exact repository state the actor used as the event's basis. It is not represented as the impossible hash of a commit that already contains its own literal hash. The later Git commit that first adds the transition file remains independently visible in repository history. A production steward must ensure that the recorded basis commit exists and is appropriate; the portable collection validator checks its shape but does not fetch or rewrite Git history.

Repository-backed review therefore uses two protected integration phases. Phase A freezes and merges the submitted packet snapshot, producer run, complete evidence, artifacts, and preceding history. Only after that protected-main commit exists may an independent reviewer bind `reviewed_subject.git_commit` to its exact evidence blob. Phase B, based on that immutable ancestor, adds the review run, completed review, under-review and accepted snapshots, and acceptance transition. The Phase B transition co-binds the unchanged Phase A evidence and the new review. Do not squash these phases together, rewrite Phase A, or place both behind a merge method that changes the reviewed commit identity; doing so destroys the claimed reviewed-subject provenance.

CI supplies the trusted protected-base commit to repository-aware validation. The gate preserves every authoritative record and record-declared artifact already present there byte-for-byte, while deliberately excluding schemas and invalid test fixtures from scientific immutability. It requires every transition basis, non-null packet lease base, Git-backed run workspace revision, and reviewed-subject commit to be a real full commit on the trusted lineage and to exist before the event or work it supports. An accepting review must have a completed run whose exact input reference binds the reviewed evidence artifact; the reviewed-subject commit must be an ancestor of that run's workspace revision. In the Phase B freeze this forces the independent run to use the exact protected Phase A state. The review must also bind the exact LF-normalized evidence-record blob stored at that commit.

## Formalization is not statement correspondence

The schemas keep two checks distinct:

1. **Formal acceptance** asks whether the formal artifact compiles or is accepted by its declared trust base and whether placeholders or unapproved axioms remain.
2. **Statement correspondence** asks whether the formal statement actually matches the intended informal theorem, definitions, quantifiers, assumptions, and conventions.

When a packet expects formalization, its plan requires both review types and fixes `separate_reviews_required` to `true`. An evidence record fixes `formal_acceptance_establishes_statement_correspondence` to `false`. A review record may occupy exactly one formal lane; its `oneOf` constraints force the other lane to remain `not_reviewed` and require a separate review. Non-formal review types must use the `not_applicable` lane.

## Validation

Validate the schema set and resolve every local `$ref` without network access:

```console
python tools/validate_packets.py --schema-only
```

Validate one record, multiple records, or directories:

```console
python tools/validate_packets.py path/to/record.json
python tools/validate_packets.py packets/ runs/ evidence/ reviews/
```

With no paths, the command validates the default discovered collection across every standard record directory and the published examples. That is a development and regression check, not the live-pilot launch gate. For Day 1, exclude examples and require at least one complete live collection:

```console
python tools/validate_packets.py --require-live
python tools/commons.py validate --require-live
```

Both commands fail when only `examples/**` exists. The live gate is content-aware as well as path-aware: published example project/problem/packet identities and exact example statement bytes are reserved; `calibration` problems, `calibration_designation` status records, and live records that point back into `examples/**` are rejected. At least one current packet must have an actionable non-draft head reached through its exact transition history. A bona fide `known_result` remains eligible for verification, translation, consolidation, or rediscovery work. `--schema-only` cannot be combined with record paths or `--require-live`; explicit paths cannot be combined with `--require-live`. Discovery proves repository containment before traversal, never follows symbolic links, and enforces file-count, byte-size, total-size, and directory-depth ceilings.

The repository validator intentionally supports a fail-closed subset of Draft 2020-12: exact local-ID or document-local `$ref` and `$defs`, primitive types, required/properties/additional-properties controls, constants and enumerations, bounded safe patterns and collections/numbers, `oneOf`/`anyOf`/`allOf`, and the date/date-time/URI formats used here. It meta-validates keyword value shapes, rejects filename-aliased remote references and unsafe regex constructs, and treats an unsupported validation keyword as an error rather than silently ignoring it. Python 3.10 or newer is required.

Collection validation additionally reconciles exact-triple record identities; no-fork problem-version lineage; problem subjects and exact statement artifacts; immutable packet snapshots, append-only event chains, and derived heads; requested source uses with aggregate and selected-component permissions; historical packet bindings for runs, evidence, and reviews; allowlists and submitted components; output declarations with evidence bytes; explicit packet resource ceilings with reported ended-run usage; and every historical acceptance with its exact evidence/review material, mandatory criteria, distinct reviewer, review type, serious finding, conflict, formal status, correspondence status, and reproduction status.

## What requires a later semantic or human check

JSON Schema validates one document's structure, and the dependency-free semantic validator enforces the deterministic cross-record rules above. Repository-aware tooling or a human reviewer must still check:

- a lease's claimant, branch, and base commit agree with the actual Git repository at handoff;
- source permission assertions have a sufficient factual and legal basis, not merely a schema-valid value;
- an allowlisted artifact contains no private, secret, unsafe, or undeclared material;
- public contributor IDs truly identify distinct producers/reviewers and disclosed conflicts are accurate;
- formal system, trust-base, placeholder, replay, and correspondence claims match their receipts; and
- no network-check status is described as journal peer review or as proof by model agreement.

Future schema changes must preserve old citable records. A breaking change receives a new `schema_version`, updated canonical schema identifiers, migration notes, fixtures, and validator tests; existing `0.1.0` instances remain governed by these exact schema bytes.
