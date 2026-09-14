# Propp 7: focused Split-Zero proof attempt

**Turn 1 of the requested 10–20-turn research attempt.** Continuation dated 15 September 2026. The objective is the full original benzel existence problem, not merely a finite computation or a reformulation. No completion date or successful resolution is promised.

## Target and source status

For admissible `(a,b)`, construct a tiling by right stones and all three bone orientations whenever the original Conway–Lagarias invariant is nonnegative. Propp's author page still lists Problem 7 as open, but expressly gives a June-2025 status horizon. A bounded search for later benzel/P7 resolutions did not establish a later resolution; this is not an exhaustive literature or novelty audit.

- Original Problem 7: https://www.samuelfhopkins.com/OPAC/files/proceedings/propp.pdf
- Author status: https://faculty.uml.edu/jpropp/benzels.html
- Original cell count and invariant: https://arxiv.org/html/2209.05717v2

## Completed in this turn

[PROOF.md](PROOF.md) specifies two explicit positive collar lifts. For every integer `d>=3`, it constructs type-103 tilings of `(d+3,2d+3)` and `(d+6,2d+6)`. The second gives `(n,2n-6)` for every `n>=9`. The coordinate maps, tile families, containment, disjointness, coverage, reflection and counts are all written out. No finite search is used by the final constructors.

The accompanying finite-jet map sends every bone boundary to zero and every right stone to the nonzero class `e+f` in `F_3[e,f]/(e^2,ef,f^2)`. An unmodified collar has class `-(e+f)`. Each construction cancels it with an actual source stone and supplies a positive integral boundary preimage. The proof retains the original support diagrams and the explicit bone/type-103 cohomology comparison kernel.

Exploration produced the tile tables; the written argument verifies their full parameter range. The finite-jet calculation identifies the exact obstruction canceled by those tables. It is not evidence that an arbitrary zero jet has a positive tiling lift. No first-discovery claim for these subfamilies or the general collar method is made. The first collar overlaps the P6 family already present in the source-status ledger.

## Replay

From this directory, using the Python standard library:

```sh
python check.py --max-d 100 --output evidence/normal.json
python -O check.py --max-d 100 --output evidence/optimized.json
```

Both recorded runs passed: 98 parameter values, 294 full tilings, 196 collar incidence identities and 546,546 tile placements. The checker independently compares two cell-set implementations and verifies every tile, cell multiplicity, invariant count and jet value. The written all-parameter proof is not replaced by these finite tests. No Lean build or independent specialist acceptance is claimed. GitHub stores the compact receipt and the reproducing checker; the offline package also includes both full run receipts, sample tilings and all 13 fixed-source obstruction certificates. Running the commands above regenerates these evidence files.

## Precise next problem

The current residual interior is `d>=3,1<=h<=binom(d,2)-1` in `(a,b)=(d+3h,2d+3h)`. The two constructions handle `h=1,2`; the full Problem 7 remains unresolved by this work.

At `d=3,h=2`, every one of the 13 containing translations leaves a cell with no allowed bone through it when the old bones are frozen and only the remaining stone is removed. The certificate rules out exactly that frozen-source recurrence. The endpoint itself is already tileable by the published invariant-zero construction.

The next target is a repair that moves old bones, with its actual support maps and positive integer coefficients, followed by a repeatable construction for the remaining `h`. A public claim of solving Problem 7 is not authorized by the present subfamily result.

## Provenance

Parent workbench commit: `ea0cf71f7af213f6e25dd0669e2e67cc024bd0dc` in `KokunoYumeto/mathematics-commons-pilot`.

Split-Zero input: `KokunoYumeto/zeta-function-research-reader@1c8ec52c85c173adc9f8403a8a26914955e2f5a9`, `workbenches/splitzero-tandem/tex/support_diagrams.tex`, D1–D8. The exact maps used here are given in PROOF.md, section 6. Third-party manuscripts and formal source corpora are not bundled. Historical discovery records and canonical Commons counts are unchanged.
