# Translation starter v8

This package helps select and start one mathematical translation project. It contains a catalog and workflow, but no source work or completed translation. The catalog is a non-exclusive list of useful suggestions; you may instead propose any mathematical work with a public source and a recorded distribution note.

Choose how you are working:

- Local Codex or another repository-aware agent: open this directory and paste [`LOCAL.md`](LOCAL.md).
- Web or hosted agent: upload this ZIP and paste [`WEB.md`](WEB.md).

The agent must first ask which work and which target language you want. It then reads the work-specific edition and distribution notes. Empty coverage means unknown, not that no translation exists. Record the exact source, license note, component boundary, and baseline build in `SOURCE.json` as the work proceeds; if a source is not attached, return the exact public locator and the next acquisition step in the cumulative checkpoint.

Use [`WORKS.json`](WORKS.json) for the subject index and current catalog locators. Use [`LANGS.md`](LANGS.md) to choose and identify a language precisely. The production rules are in [`PROMPT.md`](PROMPT.md); independent review is defined in [`QA.md`](QA.md).
