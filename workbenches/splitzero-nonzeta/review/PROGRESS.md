# Checked status and A-tier mathematics

14 September 2026 continuation of draft Commons PR 23, based on `5644a4ebb53e324b97a98d0e978c931c28eb82ba`.

## Status changes

P14 now routes as a **published resolution**, with DLPY Theorem 1.1 matching the exact original domain. The old author-page label is retained in the status history. The proof notes include an explicit residue construction and uniqueness argument, checked on 150 parameter pairs.

AIM chip-firing Q14 and matrix-spectrum Section 3 Q6 are added as published-result controls. The former is the Perkinson–Yang–Yu parking-function/tree bijection; the latter is Bai's Grone–Merris theorem. A third control records Shitov's complex zero-pattern 2n counterexample with its exact field and pattern scope. It does not retire the real-sign or positive-characteristic problems.

P4 and P6 now have pinned public formal-source locators and concrete finite checks. They remain **CLAIMED_UNVERIFIED**: no Lean executable or complete independent source replay was available here.

## Completed mathematics

[Full arguments](notes/proofs.md) contain the P14 construction, exact P7 residual parameter maps, the weighted-count/finite-jet factorization for P15–P18, integral move-graph contractions for a finite P19 family, an original-deck/truncated-word-algebra comparison with a reproduced collision family, and a complete two-by-two coefficient-map section inside its actual sign chamber.

The P7 new-construction queue now retains the interior parameters `(a,b)=(d+3h,2d+3h)`, `d>=3`, `1<=h<=binom(d,2)-1`, after the displayed maps to published subfamilies. This is a scope reduction, not a new full P7 proof.

## Exact checks actually run

The checker returns PASS in ordinary and optimized Python. It uses only the standard library and explicit exceptions, never removable `assert` checks.

| Check | Executed scope |
|---|---|
| Literal benzel generators and complete covers | 17 unordered pairs, 2<=a<=b<=7; barycentric generation versus exhaustive axial three-cell classification |
| P19 move-graph contractions | 6,492 tilings; 28,314 edges; integral root-path certificates for all 17 regions |
| Weighted finite-jet observations | 408 congruences, precisions 1 through 24; full integer weight polynomials retained |
| P14 residue construction | All 150 admissible ordered residue-one pairs with 2<=a,b<=30 |
| P4/P7 finite existence | 9 nonpositive and 38 nonnegative unordered pairs with a,b<=12; every witness checked |
| P6 formula | n=5,...,11; exact counts 2,21,168,1224,8550,58443,394680 |
| Binary subsequence decks | 32,738 exhaustive word/deck cases, n<=12,k<=4; two implementations |
| Recursive word collisions | k=1,...,7; first surviving coefficient checked |
| Matrix coefficient section | 441 target pairs and three rational conjugation coordinates per pair |
| Published matrix controls | Two Shitov matrices, exact determinants; 29 exact Grone–Merris graph-spectrum cases |
| Published DFS bijection | 43 graph cases, including all connected labelled four-vertex graphs; 1,569 parking-function instances; both inverse laws |

## Portal coverage and next work

Read all 42 numbered chip-firing statements and all 24 numbered matrix-spectrum statements (10+8+6), while auditing selected matching results. Statement reading is not a current-status audit of all 66 problems. The old 32-problem matching collection, other AIM/AMR destinations and the missing historical Commons archive remain in the intake ledger.

The next A-tier work is the P7 interior construction, uniform control of the minority-stone moments, extension of integral move contractions beyond the certified regions, and new realizable deck-kernel fibres beyond reproduced controls. The exact mathematical obligations and no-repeat instructions live in `catalog/progress.json`.

## Reproduce

    python tools/check_progress.py
    python -O tools/check_progress.py

This regenerates the complete finite evidence, including `evidence/benzel-small-certificates.json`. Full generated certificates accompany the offline package; GitHub stores the source and compact receipts. No upstream Lean result, independent specialist acceptance, new full open-problem resolution, automatic publication or downstream agent launch is claimed.
