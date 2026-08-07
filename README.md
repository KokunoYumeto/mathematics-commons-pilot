# Mathematics Commons Pilot

> A Leiden-led proposal for distributed, AI-integrated mathematical work using bounded Research Packets and peer-to-peer review.

**Status:** published concept plus the operational-MVP Phase A submitted freeze under protected review. Independent reconstruction and acceptance remain pending; the live 30-day pilot has not started. No mathematical result is claimed merely because it appears here or passes a validator.

**Privacy:** ordinary AI interactions are private by default. Contributions publish a sanitized, contributor-approved evidence bundle—not raw prompt histories, transcripts, chain-of-thought, personal context, credentials, or unrelated local files. A prompt is provenance, not proof.

## What this is

The Mathematics Commons is a proposed workflow in which independently operated human–AI nodes work on exact, bounded mathematical tasks and review one another's artifacts against shared standards of proof, provenance, attribution, openness, and human responsibility.

The first experiment is intentionally small: use one protected and mirrored GitHub repository to coordinate selected Erdős/open-problem records and carefully stated community conjectures. Issue literature, proof, counterexample, computation, exposition, and formalization packets. Preserve the evidence and the failures. Test whether the review protocol works.

The long-term concept is broader—translation, transcription, archival recovery, mathematical integration, and possibly volunteered local compute—but those are future directions, not features claimed by the first pilot.

## Read this first

1. [Current status](STATUS.md)
2. [White paper discussion draft](WHITE_PAPER.md)
3. [Leiden-led durable requirements](LEIDEN_ALIGNMENT.md)
4. [Technical GitHub pilot guide](GITHUB_PILOT_GUIDE.md)
5. [Thirty-day pilot operations](PILOT_OPERATIONS.md)
6. [First-pilot launch board](PILOT_LAUNCH.md)
7. [Source-audited candidate docket](PILOT_CANDIDATES.md)
8. [Manual local-agent handoff](NODE_HANDOFF.md)
9. [Versioned record-schema contract](schemas/README.md)
10. [GitHub 2FA continuity runbook](GITHUB_2FA_CONTINUITY.md)
11. [One-way Git mirror runbook](MIRROR_RUNBOOK.md)
12. [How to contribute](CONTRIBUTING.md)

## Try the calibration MVP

Python 3.10 or newer is required; the tooling otherwise uses only the standard library. From a clean clone, run:

```powershell
python --version
python tools/validate_packets.py --schema-only
python -m unittest discover -s tests -p 'test_*.py'
python tools/commons.py validate
python tools/commons.py list --packet-root examples/calibration
python tools/commons.py show --packet-root examples/calibration CAL-PACKET-001
python tools/validate_repository.py
```

The 13-record Phase A example is the elementary identity that the first `n` positive odd integers sum to `n²`. Five immutable packet snapshots and four exact transition events exercise the no-rewrite history from draft through the current `submitted` head; the problem, source, producer-run, and complete evidence records bind the exact historical snapshots and artifacts they used. The evidence has not yet been independently reconstructed or accepted. It is a no-novelty mechanics calibration, not evidence about open-problem research. The manual CLI derives the unique packet head after validating the complete repository record collection. It deliberately refuses to emit an agent brief for a submitted packet, an expired or mismatched lease, a wrong or dirty branch, untracked or non-HEAD inputs, a missing base commit, paths outside the packet-owned work directory, absent operational limits, or missing explicit safety approval.

There is no live `packets/` queue yet. Once stewards publish and claim a reviewed packet, follow [NODE_HANDOFF.md](NODE_HANDOFF.md); do not improvise a packet from an issue comment or prompt.

The actual launch checks deliberately fail at this pre-live stage:

```powershell
python tools/validate_packets.py --require-live
python tools/commons.py validate --require-live
```

Those commands exclude `examples/**`. A complete calibration example can test the machinery, but it cannot masquerade as an operating pilot.

## Comment or contribute

Start with the open discussion: **[Read the concept and break it: what would make this workflow work?](https://github.com/KokunoYumeto/mathematics-commons-pilot/discussions/1)**

You can:

- open **Concept feedback** to criticize or extend the proposal;
- propose an established open problem;
- propose a precisely stated community conjecture;
- submit a literature or prior-art lead;
- report a mathematical, attribution, rights, or workflow error; or
- [volunteer for a bounded production, review, stewardship, access, or infrastructure lane](https://github.com/KokunoYumeto/mathematics-commons-pilot/issues/new?template=pilot_volunteer.yml).

Use the repository's issue forms for structured proposals and challenges. Discussion is welcome; agreement is not required. Specific objections are especially useful.

## Leading framework

The project is designed to operationalize the complete [Leiden Declaration on Artificial Intelligence and Mathematics](https://leidendeclaration.ai/). Leiden is treated as enabling infrastructure for doing AI-assisted mathematics well, not as a prohibition on doing it.

This is a self-assessed alignment claim. The Leiden working group and the International Mathematical Union have not certified or endorsed this project.

## Rights

Commons-originated material is dedicated to the public domain under **CC0 1.0**, modulo pre-existing third-party copyright and other rights. Scientific attribution, academic authorship, provenance, priority, and human responsibility remain mandatory project norms even where copyright does not require them. Later publication may not enclose or remove the CC0 Commons record. See [RIGHTS.md](RIGHTS.md).

## Citation

The repository includes [CITATION.cff](CITATION.cff). Use the **concept DOI [`10.5281/zenodo.21828562`](https://doi.org/10.5281/zenodo.21828562)** for the evolving project and a version DOI when citing exact bytes:

- frozen `v0.1.0`: [`10.5281/zenodo.21828563`](https://doi.org/10.5281/zenodo.21828563);
- frozen citation/status follow-up `v0.1.1`: [`10.5281/zenodo.21830229`](https://doi.org/10.5281/zenodo.21830229).

The concept DOI and version DOIs are deliberately distinct: the first follows the latest archived version, while each version DOI identifies one immutable deposit.
