# Bounded search record and continuation

15 September 2026. This record does not promote a solver status to a mathematical impossibility theorem.

## Narrow translated d-growth

The exact cell map is `(x,y)->(x+1,y)` from `W_h(d)` into `W_h(d+1)`, also given by `Phi_(d+1)=Phi_d+(1,0)`. For `(d,h)=(3,2),(4,2),(5,2)`, the respective set differences have 27, 30 and 33 cells. An original-tile exact-cover search exhausted its search in 9, 10 and 11 recursive states, respectively, without a positive cover. No independently audited infeasibility certificate is supplied; these entries remain search observations. In particular they do not rule out moving old tiles or using a different source map.

For the same narrow inclusion at h=0 and h=1, earlier bounded searches found covers for d=3,4,5. No uniform h theorem is claimed from either outcome.

## Constant invariant

The original zero-translation inclusion `W_h(d)` into `W_(h+d)(d+1)` has the same right-minus-left invariant by the displayed identity in PROOF.md. The three positive bone-only certificates for `(3,0),(3,1),(4,0)` are included in fixtures.py and replay to exact original-cell partitions. The larger exploratory cases `(4,1),(4,2),(5,0)` reached search budgets; that is not an infeasibility result.

## Sixth collar

The retained delta certificates are for d=4,5,6,7,8 only. Each is replayed against the constructed T5 with its actual translation, old generators, removed source stone and positive new bones. Search-selected release counts are not proved minimum counts. No infeasibility or optimality result enters the fifth-family proof.

## Source of the fifth table

The previous full-cell witnesses for d=5..8 led to one common affine table. The acceptance is the all-parameter argument in PROOF.md and certify.py, not the fitting step. That same literal table passes for d=4 and releases 16 old bones. The previously retained d=4 witness releases 22; fixtures.py restores it byte-for-byte for comparison and preserves its different original tiling.

Next: work on the all-phase polygon incidence map with variable h and positive source changes. The general coordinate map has already been proved; a general positive section has not.
