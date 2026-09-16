# Propp 7 — fifth-collar continuation (turn 3)

Recorded 15 September 2026. Additive continuation for review and later integration; the earlier `turn2/` and `TURN2.md` are unchanged.

## Completed scope

[PROOF.md](PROOF.md) constructs original type-103 tilings of `V(d+15,2d+15)` for every integer `d>=4`, and reflected pairs. Equivalently, `V(n,2n-15)` for `n>=19`. Each has `binom(d,2)-5` right stones and `15d+75` bones. A single indexed repair releases 16 old bones for every `d>=4`, including the earlier exceptional test value `d=4`. No optimality or priority claim is made.

The proof retains every original cell, tile, release, source preimage, support label and positive coefficient. It gives both inverse maps for the patch-containing tiling fibres and the exact affine/cochain comparison. The accompanying original-cell/three-polygon bijection and all 12 tile-phase maps hold for every `d>=3,h>=0`. These maps do not assert a general tiling algorithm.

The complete preceding four tables are included and replayed, not counted as newly discovered here. The base tiling and area polynomial are derived from the explicit cell bijection. This directory is self-contained for its finite and all-parameter checks.

## Replay from a clean checkout

```sh
cd workbenches/splitzero-nonzeta/sprints/benzel-p7/turn3
python fixtures.py
python check.py --max-d 100 --output evidence/normal.json
python -O check.py --max-d 100 --output evidence/optimized.json
```

`fixtures.py` stores the actual placed-tile anchors. Its inverse expansion uses the original offsets and restores three JSON evidence files byte-for-byte, checking their SHA-256 values. Existing different evidence is never overwritten. The full offline package already includes those expanded files.

`certify.py` enumerates every pair of affine families and offsets, reconstructs their original collision constraints and verifies a nonnegative rational contradiction. It also checks the original source preimages, all intervening removals, containment, symbolic source intersection and area identities. The generated `evidence/all-parameter-certificates.json` contains all 8,919 explicit certificates; 5,049 concern the fifth table. This unbounded-parameter calculation does not infer its conclusion from the separate finite replay.

Both recorded Python modes passed: 194 fifth-family tilings including reflections for `d=4..100`, 498,192 tile placements, 97 cochain and positive inverse identities, 972 original tile/polygon incidence squares, 3,750 inverse-cell checks, 61,383 polygon membership checks and seven rejection tests. Five sixth-level tilings for `d=4..8` and three bone-only annuli are checked as bounded certificates only.

## Integration and provenance

Base: `KokunoYumeto/mathematics-commons-pilot@038ed02bb524e60e9c2bd20c3a0aa02365f4001d`, the inspected head of draft PR #23. This contribution is prepared as a separate stacked PR targeting `workbench/splitzero-nonzeta-20260914`; it does not change main or erase concurrent work.

Upstream method: `KokunoYumeto/zeta-function-research-reader@1c8ec52c85c173adc9f8403a8a26914955e2f5a9`, `workbenches/splitzero-tandem/tex/support_diagrams.tex`, D1–D8. Exact original problem and literature links remain in PROOF.md. No third-party source corpus is redistributed.

The full numbered Problem 7 remains unresolved by this work. The fifth subfamily has a written, exact-certificate-assisted proof; independent specialist review, novelty certification and a Lean build have not been performed. No agents or paid compute were launched.

## Next mathematical work

Use the all-phase polygon incidence map to construct a positive lift with variable `h`, rather than assuming the five collar tables repeat. The saved sixth-level patches and invariant-preserving annuli are original starting configurations. The status and exact continuation cursor are in [STATE.json](STATE.json).
