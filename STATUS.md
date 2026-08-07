# Current status

**Release stage:** published concept / operational MVP Phase A submitted freeze; independent review pending; live pilot not launched
**Protocol version:** 0.1.1
**Pilot schema version:** 0.1.0
**Date:** 7 August 2026

## Completed

- The complete Leiden Declaration has been mapped to durable workflow requirements.
- A white paper discussion draft describes the scientific, governance, and technical concept.
- A GitHub-native pilot architecture has been specified.
- The current pilot has been separated from later archival, translation, one-click onboarding, and fully local peer-to-peer compute ideas.
- The public GitHub repository, structured issue forms, and open concept discussion are live.
- `main` is protected, public validation has passed, and repository-level immutable releases are enabled.
- Frozen `v0.1.0` is published as an immutable GitHub release and Zenodo record; all ten assets passed anonymous byte-for-byte readback.
- The all-versions concept DOI is `10.5281/zenodo.21828562`; the frozen `v0.1.0` version DOI is `10.5281/zenodo.21828563`.
- Citation/status follow-up `v0.1.1` is published and anonymously verified on both GitHub and Zenodo. Its immutable version DOI is `10.5281/zenodo.21830229`; it changes no mathematical claim from `v0.1.0`.
- A GitHub 2FA continuity runbook covers human logins, local Git/CLI authentication, automation, organization migration, and lockout recovery.
- A privacy-by-default rule now separates sanitized tool/process disclosure from private prompt histories, raw transcripts, personal context, and unrelated local state; every future module must declare and minimize its publication boundary.
- A deterministic exact-ref release builder produces a strict USTAR archive, commit/tree/file manifest, reader files, and byte-exact SHA-256 checksums through an atomic no-overwrite publication step; adversarial local audit has passed.
- The operational MVP includes strict versioned record schemas, a standard-library semantic validator, a fail-closed manual packet/agent CLI, valid and adversarial fixtures, and a no-novelty elementary Phase A calibration collection.
- Phase A freezes exactly 13 records: five packet snapshots through `submitted`, four transitions, a problem and source, one producer run, and one complete evidence record. The evidence explicitly remains not independently reproduced and not accepted.
- Local integration checks cover schema shape and references, cross-record rights and acceptance semantics, statement/evidence hashes, packet transitions, resource limits, formalization/correspondence gates, repository-aware handoff state, and structural policy checks. These checks establish process conformance, not mathematical truth.
- A dated source audit produced a nine-record candidate docket: seven established-problem records and two provisionally shortlisted community-originated status-reconciliation records. None has yet been admitted to the live queue.
- A pre-launch board and structured volunteer intake make the missing stewardship, review, source-audit, formalization, infrastructure, rights, and access capacity explicit.

## Not yet completed

- The active seven-record pilot set has not been frozen from the nine-record docket; two capacity-dependent reserves remain proposed.
- Reviewers and stewards have not been formally recruited.
- The independent reconstruction, review record, under-review and accepted snapshots, and acceptance transition belong to Phase B and do not exist in this freeze.
- No live `packets/` queue exists, and the manual handoff has not yet completed a real multi-contributor review cycle.
- No Commons submission or live-pilot claim is represented as newly solving or network-checking a problem. The docket does include sourced solved/known results as calibration and status-reconciliation candidates.
- No external journal or community peer review has occurred.

## Immediate next milestone

Merge the exact Phase A submitted freeze through protected validation, independently reconstruct its immutable evidence, add the review and acceptance records only in Phase B, then recruit the initial steward/reviewer group through the [launch board](PILOT_LAUNCH.md), freeze a capacity-backed six-to-ten-record set from the [candidate docket](PILOT_CANDIDATES.md), and run one bounded 30-day review-and-release cycle.

## How feedback will be handled

Substantive proposals and objections are tracked through public issues. Accepted changes land in version-controlled files. Rejected proposals receive a recorded reason. Older releases remain citable and are superseded rather than silently rewritten.
