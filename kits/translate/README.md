# Translation starter v7

This package helps select and start one mathematical translation project. It contains a catalog and workflow, but no source work or completed translation. The catalog is a non-exclusive list of useful suggestions; you may instead propose any mathematical work whose exact source and permission for translation derivatives can be verified.

Choose how you are working:

- Local Codex or another repository-aware agent: open this directory and paste [`LOCAL.md`](LOCAL.md).
- Web or hosted agent: upload this ZIP and paste [`WEB.md`](WEB.md).

The agent must first ask which work and which target language you want. It then checks work-specific editions and source eligibility. Empty coverage means unknown, not that no translation exists. Until the exact source, license, component boundary, and baseline build are recorded in `SOURCE.json`, the project remains in source preflight and does not translate text.

Use [`WORKS.json`](WORKS.json) for the subject index and current catalog locators. Use [`LANGS.md`](LANGS.md) to choose and identify a language precisely. The production rules are in [`PROMPT.md`](PROMPT.md); independent review is defined in [`QA.md`](QA.md).
