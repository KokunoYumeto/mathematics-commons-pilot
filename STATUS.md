# Current status

**Release stage:** concept draft / pre-pilot  
**Protocol version:** 0.1.0  
**Date:** 6 August 2026

## Completed

- The complete Leiden Declaration has been mapped to durable workflow requirements.
- A white paper discussion draft describes the scientific, governance, and technical concept.
- A GitHub-native pilot architecture has been specified.
- The current pilot has been separated from later archival, translation, one-click onboarding, and fully local peer-to-peer compute ideas.
- The public GitHub repository, structured issue forms, and open concept discussion are live.
- `main` is protected, public validation has passed, and repository-level immutable releases are enabled.
- Zenodo version DOI `10.5281/zenodo.21828563` is reserved in an unpublished project-specific draft.
- A GitHub 2FA continuity runbook covers human logins, local Git/CLI authentication, automation, organization migration, and lockout recovery.
- A privacy-by-default rule now separates sanitized tool/process disclosure from private prompt histories, raw transcripts, personal context, and unrelated local state; every future module must declare and minimize its publication boundary.
- A deterministic exact-ref release builder produces a strict USTAR archive, commit/tree/file manifest, reader files, and byte-exact SHA-256 checksums through an atomic no-overwrite publication step; adversarial local audit has passed.

## Not yet completed

- The pilot problem set has not been selected.
- Research Packet JSON Schemas and validators have not been implemented.
- Reviewers and stewards have not been formally recruited.
- No problem is represented here as solved or network-checked.
- No external journal or community peer review has occurred.
- Reserved DOI `10.5281/zenodo.21828563` does not resolve until the preflighted draft is published.
- The first DOI-bearing concept release has not yet been tagged, archived, or published.

## Immediate next milestone

Freeze and archive the first DOI-bearing concept release. After that, recruit the initial steward/reviewer group, choose six to ten calibration records, implement the minimal schemas and validation workflow, and run one 30-day review-and-release cycle.

## How feedback will be handled

Substantive proposals and objections are tracked through public issues. Accepted changes land in version-controlled files. Rejected proposals receive a recorded reason. Older releases remain citable and are superseded rather than silently rewritten.
