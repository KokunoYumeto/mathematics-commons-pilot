# Target-language selection

Choose one exact language and record its locale, script, and orthographic standard. A broad label such as “Chinese,” “Arabic,” or “Serbo-Croatian” is insufficient when the intended edition depends on region, script, or standard.

Check the selected work's own edition records before treating a language as covered. Aggregate tags from other corpora do not establish coverage for this work. Missing data means unknown, not absent.

Translations into any language are welcome. Give priority to languages for which communities document limited access to university-level mathematical material, and record the intended learners and available reviewers. UNESCO reports that up to 40% of people lack access to education in a language they speak or understand; more than a quarter-billion learners are affected, and only 351 of roughly 7,000 languages in current use serve as media of instruction.

A separate [UNESCO Institute for Statistics report](https://www.uis.unesco.org/sites/default/files/medias/fichiers/2025/09/GAML11_2.2_UIS-Benchmarking-by-Language-Group-2025.04.28.pdf) cites a 48-country literacy study covering 96 alphabetic-script languages. The report describes 75% of the assessments as conducted in a local or national language and 25% in English, French, Spanish, or Portuguese. `WORKS.json` preserves the exact 96 Table S1 labels under `language_priority.uis_96_language_study.language_labels`.

Use that study set as a concrete source of possible language communities, not as a ranking or a closed queue. The source labels are not normalized ISO identifiers. Resolve the current language name, locale, script, written standard, educational need, and reviewers with the intended community.

A valid target may be any language not already maintained for the selected work. Declared independent overlap is also allowed when it has a clear review or edition purpose.
