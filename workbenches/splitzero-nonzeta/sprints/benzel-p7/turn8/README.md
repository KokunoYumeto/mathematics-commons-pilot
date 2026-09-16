# Benzel P7, turn 8 — every deletion count q=3k

**Written constructive research result; independent review pending.**

The constructor covers every integer triple

    k>=1, m>=3k+2, d>=m,
    Delta=m(m-1)/2-3k,
    h=d(d-1)/2-m(m-1)/2+3k.

It tiles the original benzel `V(d+3h,2d+3h)` by `Delta` right stones and
`3h(h+d)` bones. This extends the previous fixed deletion tables to **all positive
multiples of three**, with both parameters retained in the proof. Reflection
supplies the original reversed-parameter family. Full Propp Problem 7 is not
claimed resolved; the other two deletion residue classes are not certified by
this constructor.

Read [PROOF.md](PROOF.md). The original source indices, finite-tail inverse map,
complete long-strip/corner formulas, exact bivariate Laurent identity, positive
partition, integer matching-comparison kernel, cell duals, and genuine Split-Zero
support complexes are all supplied. `families.json` is shared by the positive
constructor and symbolic proof. No solver is used for reproduction.

## Reproduce

```sh
python bivariate_certificate.py
python verify.py --max-k 15 --output evidence/normal.json
python -O verify.py --max-k 15 --output evidence/optimized.json
```

The first command verifies the formal identity before choosing either m or k.
The second and third commands additionally check the separately stated finite
original-cell and cohomology windows. The `-O` run retains all validation.

`construction.complete(d,m,k)` returns the actual placed tiles and their three
original cells. `cohomology.MatchingKernel` gives the full integer kernel basis,
its coordinate inverse and original-cell duals; it does not replace the whole
kernel by the one distinguished class. `Supports` and `Total` implement the
actual augmented support transitions and supported-zero operations.

## History and source scope

This is additive work over the confirmed PR25 head
`6fe012fd1facd564e07e1fa052ad219debdd8278`. No existing workbench source or canonical
Commons catalog is overwritten. The retained stable-packing proof is
`sources/turn6-PROOF.md`; `packing.py` is its original source code. The local
parent fixed-q controls are recorded by exact hashes in `SOURCES.json`; they
are not counted as new results.

The method input remains the user's Split-Zero programme at
`zeta-function-research-reader@1c8ec52c85c173adc9f8403a8a26914955e2f5a9`, especially
`support_diagrams.tex` D1–D8 and `SplitZeroComplex.lean`. Original objects and
maps are instantiated in PROOF §§6–8. No analytic zeta estimate or fresh Lean
certificate is substituted for this construction.

`EXPLORATION.md` records the unfinished residue-1/residue-2 continuation and
why isolated corner repairs require actual transport. The explicit band
homotopies are proved; their unrestricted positive endpoint completions are not.
No first-discovery claim, independent specialist acceptance, full P7 resolution,
agent launch, paid compute or automatic merge is asserted.
