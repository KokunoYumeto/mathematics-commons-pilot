# Independent translation QA

Review a frozen candidate without editing it.

Check and report separately:

1. source archive, commit/tree, license, component inventory, and build replay;
2. complete source-order coverage and exact continuation cursor;
3. formulas, notation, stable IDs, links, theorem dependencies, exercises, hints, answers, and code;
4. terminology consistency, mathematical force, register, and untranslated residue;
5. figures, tables, alt text, layout, fonts, and reader navigation;
6. deterministic source/reader builds and byte-bound manifests;
7. append-only decisions, corrections, reversals, and unresolved issues; and
8. package contents, component notices, offline usability, and correction channel.

Return `PASS` only when every declared gate passes. Otherwise return `FAIL` with exact file/unit/page/ID locators. Do not repair the candidate during the cold audit.
