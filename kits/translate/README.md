# Translation starter v2

This package starts one mathematical translation project. It does not include a textbook and does not make every catalog row translation-ready.

Choose how you are working:

- Local Codex or another repository-aware agent: open this directory and paste [`LOCAL.md`](LOCAL.md).
- Web or hosted agent: upload this ZIP and paste [`WEB.md`](WEB.md).

The agent must first ask which work and which target language you want. It then checks existing language coverage and source eligibility. Translation begins only after the exact source, license, component boundary, and baseline build are recorded in `SOURCE.json`.

Use [`WORKS.json`](WORKS.json) for the subject index and current catalog locators. Use [`LANGS.md`](LANGS.md) to choose and identify a language precisely. The production rules are in [`PROMPT.md`](PROMPT.md); independent review is defined in [`QA.md`](QA.md).
