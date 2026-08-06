# Agent recovery and operating instructions

These instructions apply to every task in this repository.

## Context-loss protocol

After any context compaction, handoff, restart, or uncertainty about prior work, do not mutate files or external systems until you have:

1. read `SESSION_RECOVERY.md` completely;
2. read `PROJECT_LOGBOOK.md` completely;
3. read `STATUS.md`, `RIGHTS.md`, and `START_HERE_FOR_AGENTS.md` completely;
4. checked `git status`, the current branch, remotes, and recent commits;
5. checked the active durable goal, if the environment provides one;
6. verified the live GitHub and Zenodo state before creating, publishing, or repeating anything; and
7. appended a recovery entry to `PROJECT_LOGBOOK.md` stating what was verified.

Treat a compacted summary as a pointer to the durable record, not as a substitute for it.

## Logging rule

Append every material decision, correction, scope change, publication action, DOI action, failed external operation, and unresolved blocker to `PROJECT_LOGBOOK.md`. Update `SESSION_RECOVERY.md` whenever the exact next action or external state changes.

Never log credentials, access tokens, private identity linkage, private conversations, or unnecessary personal data.

## Governing boundaries

- Current goal: publish and verify the public concept repository and its first citable release.
- Current pilot: a small GitHub-native conjecture/literature/proof-review workflow for the initial AI-literate group.
- Future only: broad one-click onboarding, archival/translation project trees, marginal-intelligibility translation at scale, volunteered local CPU/GPU work, and genuinely local peer-to-peer model inference.
- Leiden is the leading framework, interpreted as enabling trustworthy AI-assisted mathematics.
- AI interactions and local context are private by default. Publish only the packet's sanitized, contributor-approved evidence bundle; never demand raw prompts, transcripts, chain-of-thought, personal data, credentials, unpublished communications, or unrelated local files.
- Commons-originated material is CC0 modulo pre-existing third-party rights.
- Academic authorship, credit, priority, and responsibility remain distinct from copyright.
- Do not claim official Leiden certification, journal peer review, a solved problem, or implemented future infrastructure.
