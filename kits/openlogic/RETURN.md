# Cumulative return

After every bounded unit, return one ZIP with this topology:

- `source/`: the unchanged packet source;
- `target/`: the complete current target-language source;
- `reader/`: the current standalone target-language PDF when buildable;
- `state/SOURCE.json`, `state/CHECKPOINT.json`, and `state/QA.json`;
- `state/TERMS.tsv`, `state/DECISIONS.md`, `state/CORRECTIONS.md`, and `state/ISSUES.md`;
- `state/BUILD.json`: baseline and current build receipts; and
- `MANIFEST.sha256`: a self-excluding manifest for every other returned file.

The manifest stream is UTF-8 with LF endings, sorted by ordinal relative path, one row per file:

`SHA256<TAB>bytes<TAB>path<LF>`

Name generations `openlogic-<language>-gNNNN.zip`. Never overwrite an earlier generation. `CHECKPOINT.json` must name completed units, current state, exact next source path or section, and the prior-generation hash.

