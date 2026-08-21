# Required cumulative return

After every bounded unit, return one cumulative package containing:

- the complete current source and standalone target-language edition;
- `SOURCE.json` and the exact source/license/component identities;
- the terminology, decision, correction, and unresolved-item ledgers;
- the baseline and current build receipts;
- a checkpoint with completed units and the exact next cursor;
- a self-excluding SHA-256 manifest covering every other returned file; and
- the most recent independent QA receipt, or an explicit `not_run` state.

Use `STATUS: IN_PROGRESS`, `STATUS: COMPLETE`, or `STATUS: BLOCKED`. A blocked return preserves all cumulative state and identifies the exact missing source, right, dependency, byte identity, reviewer, or decision.
