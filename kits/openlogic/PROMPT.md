# Open Logic production contract

Produce one inspectable, standalone target-language edition from the exact source in `source/`. `source/` is immutable evidence. Translation work belongs in `target/`.

## Required order

1. Replay `MANIFEST.sha256` and the source identity in `JOB.json`.
2. Record the target language, locale, script, written standard, intended learners, known editions, declared overlap, and reviewers in `SOURCE.json`.
3. Copy `source/` to a disposable `baseline/` directory and reproduce the unmodified build there. Record the exact toolchain, commands, warnings, outputs, and failures. A missing local dependency is a repair task, not permission to alter source bytes. Reverify every `source/` byte after the build.
4. Copy the still-clean `source/` tree to `target/`. Preserve paths, formulas, stable identifiers, cross-references, theorem structure, exercises, hints, solutions, figures, bibliography, code, and accessibility semantics.
5. Translate one complete representative unit. Check its mathematics, terminology, references, layout, and build before scaling.
6. Continue in source order. Never summarize, skip, silently modernize, weaken hypotheses, invent text, or bypass a difficult passage.
7. Build a standalone monolingual target-language reader. Do not substitute a bilingual or facing-page reader.
8. Maintain append-only terminology, decision, correction, and unresolved-item ledgers.
9. After every bounded unit, return the complete cumulative package defined by `RETURN.md` and update the exact continuation cursor.
10. Before release, require a fresh reviewer to inspect the frozen candidate without patching it during review.

Keep third-party notices intact. Attribute the Open Logic Project, identify the translation and all material changes, and do not imply upstream endorsement.
