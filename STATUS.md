# Current status

**Release stage:** published concept / operational-pilot implementation
**Protocol version:** 0.1.1
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
- Citation/status follow-up `v0.1.1` records the concept DOI separately from its reserved version DOI `10.5281/zenodo.21830229`; it changes no mathematical claim from `v0.1.0`.
- A GitHub 2FA continuity runbook covers human logins, local Git/CLI authentication, automation, organization migration, and lockout recovery.
- A privacy-by-default rule now separates sanitized tool/process disclosure from private prompt histories, raw transcripts, personal context, and unrelated local state; every future module must declare and minimize its publication boundary.
- A deterministic exact-ref release builder produces a strict USTAR archive, commit/tree/file manifest, reader files, and byte-exact SHA-256 checksums through an atomic no-overwrite publication step; adversarial local audit has passed.

## Not yet completed

- The pilot problem set has not been selected.
- Research Packet schemas, semantic validation, node handoff, and adversarial fixtures are being implemented on a separate review branch and are not part of frozen `v0.1.0`.
- Reviewers and stewards have not been formally recruited.
- No problem is represented here as solved or network-checked.
- No external journal or community peer review has occurred.

## Immediate next milestone

Finish and review the operational MVP, recruit the initial steward/reviewer group, choose six to ten calibration records, and run one 30-day review-and-release cycle.

## How feedback will be handled

Substantive proposals and objections are tracked through public issues. Accepted changes land in version-controlled files. Rejected proposals receive a recorded reason. Older releases remain citable and are superseded rather than silently rewritten.
