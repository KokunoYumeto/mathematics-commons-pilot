# Bootstrap prompt for a local agent

You are operating the Mathematics Commons translation starter. Do not translate anything yet.

Read `README.md`, `START.md`, `WORKS.json`, `LANGS.md`, `SOURCE.json`, `PROMPT.md`, `QA.md`, and `RETURN.md`. Then ask the user exactly these two questions before taking any other project action:

1. Which mathematical work do you want to translate? Give its title and, if available, its public source URL or semantic catalog key.
2. What exact target language, locale, script, and orthographic standard do you want?

After the user answers:

1. Locate the work by semantic key or title in the catalog sources recorded in `WORKS.json`. If it is not listed, treat it as a proposed additional open work and perform the same preflight.
2. Report its exact source state, license state, build state, work-specific verified editions, reported but unverified editions, and any declared overlap. Never treat unknown coverage as absence.
3. If the requested work or language is already active, ask whether the user wants a different language or an explicitly declared independent edition. Never overwrite another edition.
4. If immutable source, derivative permission, component rights, or a baseline build is missing, stop translation and propose a bounded source-preflight job.
5. If the source is eligible, obtain or request the exact source bytes, verify them, and complete `SOURCE.json` without inventing any field.
6. Only after the intake freeze and baseline build, follow `PROMPT.md` in source order.
7. Return the cumulative files specified in `RETURN.md` after every bounded unit.

Do not infer completion from a title, language tag, filename, or catalog category. Do not use a private machine path as a public source identity.
