# Benzel P7, turn 4: Split-Zero support computation

This is an additive continuation of PR 24, parent `d7cd069031536bea677ed31f7729ebdd4e9f97f6`, for review and later integration. It does not replace the original benzel sources or assert a full P7 resolution.

Read [PROOF.md](PROOF.md) and [SOURCES.json](SOURCES.json). The new calculation explicitly uses G(Z), its external zero and supported zero, reconstructed support-indexed complexes, the internal coequalizer and comparison kernel, and the Rees defect with its residue dual. A charge coordinate gives genuine linear transition maps for the original affine repair; charge-one nonnegative cycles are exactly the patch tilings.

For every integer d>=4, all 65,535 proper subsets of the parent's sixteen-bone fifth-repair dictionary have empty nonnegative real filling fibres. Sixteen exact dual cochains certify the maximal omissions. This is inclusion-minimality for that original dictionary/stone/translation, not a minimum over other source configurations. An explicit 24-cell signed identity gives an integral lift after the first 15 releases. The original residual class has a split integral Z through prefix 14, becomes its supported zero at 15, and has a positive lift at 16. The actual Rees inclusion is T^15 Z[T] w -> Z[T] w, with integral remainder basis, perfect residue pairing, and rationalized defect length 15.

## Replay

From this directory, in the same checkout as the exact parent `../turn3/`:

```sh
python verify.py --max-d 100 --output evidence/normal.json
python -O verify.py --max-d 100 --output evidence/optimized.json
```

Only the Python standard library is required. The source constructors and tables are hash-pinned before import. The all-parameter checker uses the original inequalities to partition the entire integer parameter domain, including its unbounded interval; it does not infer a theorem from `--max-d`. That argument is printed in PROOF.md. Finite tests supplement it. New cochains/certificates are regenerated from their listed coefficients; no optimization result is treated as a proof.

No new sixth-family construction, full Problem 7 resolution, Lean build, independent specialist acceptance, or priority claim is made. The next calculation has to change the available original support/source configuration; the classified proper subsets do not need another positive search.
