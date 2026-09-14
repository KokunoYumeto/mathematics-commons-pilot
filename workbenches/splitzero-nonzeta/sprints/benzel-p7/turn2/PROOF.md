# Moving a source stone and filling the third benzel collar

**Focused Propp-7 attempt, turn 2, 15 September 2026.** Parent: `90f23b04fbde1e25d07342e2b8a8c80d919402c5`. The constructions in §§1–4 and algebraic identifications in §§5–7 have complete written proofs below. Independent specialist review and Lean replay have not been performed. No full solution of Problem 7, first-discovery claim, or empirical probability of completion is asserted.

## 1. Original objects and constructed result

Keep exactly the original axial cells and tiles from [the turn-1 proof](../PROOF.md):

- `D0=j-i`, `D1=1-i-2j`, `D2=2i+j-1`;
- `W_h(d)={(i,j):1-d-3h <= D0,D1,D2 <= 2d+3h-1}`;
- `S(x,y)={(x,y),(x+1,y),(x,y+1)}`;
- bones `D(x,y)={(x+u,y-u):u=0,1,2}`, `H(x,y)={(x+u,y):u=0,1,2}`, and `V(x,y)={(x,y+u):u=0,1,2}`.

These are the actual type-103 prototiles. The inverse of the axial cell map is `(i,j)->(i,j,1-i-j)`. The parameter map to original benzels is

    (d,h) -> (a,b)=(d+3h,2d+3h),
    d=b-a, h=(2a-b)/3.

For every integer `d>=3`, we construct a type-103 tiling of `W_3(d)`. It has

    binom(d,2)-3 right stones and 9d+27 bones.

Equivalently this tiles every original `(n,2n-9)`-benzel for integers `n>=12`, and its reflected family. The constructor is given by formulas; its final execution performs no search. The `d=3` member is the known bone-only `(12,15)` endpoint, retained as a control rather than a new resolution.

The previous area formula gives

    |W_h(d)|=3 binom(d,2)+(9d-3)h+9h^2.

It is used only with its original parameters. Source attribution and the full original P7 target are retained in §9.

## 2. A positive nine-cell move, with both directions

For any integers `x,y`, define the following two lists of actual tiles:

    L(x,y) = {S(x,y), H(x+2,y), H(x+1,y+1)},
    R(x,y) = {H(x,y), H(x,y+1), S(x+3,y)}.                 (T1)

Each list partitions exactly the same nine cells:

    {(x+v,y):0<=v<=4} union {(x+v,y+1):0<=v<=3}.

Indeed L partitions the bottom row into lengths 2 and 3 and the top row into lengths 1 and 3. R partitions the bottom row into lengths 3 and 2 and the top row into lengths 3 and 1. These descriptions prove containment, disjointness and coverage, not just equality of areas.

On the free integer module on placed tiles, put

    kappa = [H(x,y)]+[H(x,y+1)]+[S(x+3,y)]
            -[S(x,y)]-[H(x+2,y)]-[H(x+1,y+1)].           (T2)

For the original incidence differential, `partial kappa=0`. On the set of tilings containing L, adding kappa replaces that exact subpatch by R. All removed coefficients were 1; the new patch is disjoint from every tile outside the common nine-cell support. This gives a tiling with coefficients 0 or 1. Subtraction of kappa is the inverse on the tilings containing R. Thus these are inverse maps between the two specified subsets of the original tiling fibre, not an assumed map between all tilings.

Linear extension on the free modules on those subsets gives inverse linear maps. They commute with the cell-incidence observation, since both send a full tiling to its original region vector. Inclusion of the nine-cell support into any larger finite support commutes with the replacement. Translation has its literal inverse translation, so (T1) also supplies all translated versions with the original coordinates attached.

## 3. Locate the move in the actual second tiling

Let `T2(d)` be the complete turn-1 second tiling, and translate it by

    t3=(1,-2).

Its three difference-coordinate increments are `(-3,3,0)`. Its region I is therefore contained in `W_3(d)` and has exact bounds

    D0 in [-d-8,2d+2],
    D1 in [-d-2,2d+8],
    D2 in [-d-5,2d+5].                                  (T3)

The translated source tiling contains

    S(d-2,0), H(d,0), H(d-1,1).                          (T4)

Here is their provenance inside the original construction. The three successive translations sum to zero: `(-2,1)+(1,1)+(1,-2)=(0,0)`. The stone in (T4) is the original base stone indexed by `r=s=0`; it is distinct from the two previously consumed corner stones for `d>=3`. The first-collar families `F_(d-1)` and `G_(d-2)`, translated by `(1,1)+(1,-2)=(2,-1)`, are respectively `H(d-1,1)` and `H(d,0)`. No second-collar step removed a bone.

Apply (T1) at `(x,y)=(d-2,0)`. This changes exactly the two old bones in (T4), and moves the source stone to

    S*=S(d+1,0).

Write T2* for the resulting tiling of I. In particular the old frozen-source obstruction has been addressed by an actual positive move of old tile generators.

## 4. Complete third-collar table and proof

Use the following bone family C3. Every index bound is inclusive.

| Label | Kind | Anchor | Range |
|---|---|---|---|
| A_r | D | `(-d-5+r,d+3-2r)` | `0<=r<=d+2` |
| B | D | `(-d-4,d+3)` | one |
| C | D | `(-d-4,d+4)` | one |
| E | D | `(-d-3,d+4)` | one |
| F | D | `(-d-2,d+4)` | one |
| G_r | D | `(-d+2r,d+3-r)` | `0<=r<=d-1` |
| J_r | H | `(-d-3+2r,d+5-r)` | `0<=r<=d+1` |
| K | H | `(d,3)` | one |
| L | V | `(d+1,0)` | one |
| M | V | `(d+2,0)` | one |
| N | V | `(d+3,1)` | one |
| P | V | `(d+4,-1)` | one |
| Q | V | `(d+5,-3)` | one |

### 4.1 Original outer containment and exact inner intersection

At offset `u=0,1,2`, direct substitution gives:

| Label | D0 | D1 | D2 |
|---|---|---|---|
| A_r | `2d+8-3r-2u` | `-d+3r+u` | `-d-8+u` |
| B | `2d+7-2u` | `-d-1+u` | `-d-6+u` |
| C | `2d+8-2u` | `-d-3+u` | `-d-5+u` |
| E | `2d+7-2u` | `-d-4+u` | `-d-3+u` |
| F | `2d+6-2u` | `-d-5+u` | `-d-1+u` |
| G_r | `2d+3-3r-2u` | `-d-5+u` | `2-d+3r+u` |
| J_r | `2d+8-3r-u` | `-d-6-u` | `-d-2+3r+2u` |
| K | `3-d-u` | `-d-5-u` | `2d+2+2u` |
| L | `-d-1+u` | `-d-2u` | `2d+1+u` |
| M | `-d-2+u` | `-d-1-2u` | `2d+3+u` |
| N | `-d-2+u` | `-d-4-2u` | `2d+6+u` |
| P | `-d-5+u` | `-d-1-2u` | `2d+6+u` |
| Q | `-d-8+u` | `2-d-2u` | `2d+6+u` |

Every entry lies in `[-d-8,2d+8]`. Here is a full interval check for the indexed rows, whose variables attain their extrema at the displayed endpoints:

- A: D0 lies in `[-d-2,2d+8]`, D1 in `[-d,2d+8]`, D2 in `[-d-8,-d-6]`.
- G: D0 lies in `[2-d,2d+3]`, D1 in `[-d-5,-d-3]`, D2 in `[2-d,2d+1]`.
- J: D0 lies in `[3-d,2d+8]`, D1 in `[-d-8,-d-6]`, D2 in `[-d-2,2d+5]`.

The ten fixed rows have only `u=0,1,2`; their extrema as printed lie between the same bounds for `d>=3`. This proves outer containment for every parameter in the theorem.

Compare the same table with (T3). A lies below I's D2 lower bound. B at u=0 lies below that bound, and at u=1,2 lies above I's D0 upper bound. C,E exceed I's D0 upper bound. F at u=0,1 exceeds that bound and at u=2 lies below I's D1 lower bound. G,J,K all lie below I's D1 lower bound. N lies below that D1 bound; P,Q exceed I's D2 upper bound. L has only u=0,1 inside I; M has only u=0 inside I. Those three cells are precisely S*. Therefore

    covered(C3) subset (W_3(d)\I) union S*.             (T5)

### 4.2 Disjointness of every orientation pair

For D-bones, the quantity `1-i-j` is constant. The A family occupies distinct levels `3,...,d+5`; B,C,E,F occupy `2,1,0,-1`; G occupies `-2,...,-d-1`. All D-bones are disjoint. The J horizontal rows are distinct and range from 4 through d+5; K occupies row 3. The five V-bones have distinct columns d+1 through d+5. Thus each orientation family is internally disjoint.

Every D-cell has `i<=d`: the A maximum is -1, the fixed-row maximum is at most -d, and the G maximum is d. Every V-cell has `i>=d+1`, proving D/V disjointness.

For D/H, let u denote the D offset and v the H offset. A_r meeting J_s would, from the second coordinate, require `s=2+2r+u`; the first coordinate would then require `v=-6-3r-u<0`. For B,C,E,F meeting J_s, substituting the equal-row equation makes the J first coordinate exceed the D first coordinate respectively by `5+u+v`, `3+u+v`, `2+u+v`, `1+u+v`. For G_r meeting J_s, equal rows require `s=2+r+u`, and the first-coordinate excess is `1+u+v`. Each case is impossible for nonnegative offsets.

For K in row 3, an A_r cell in that row has `2r+u=d`, hence first coordinate `-5-r<d`; a G_r cell in row 3 has `r+u=d`, hence first coordinate `r<=d-1`. The fixed D rows have second coordinate at least d+1, which is at least 4. None meets K's columns d,d+1,d+2. This exhausts D/H.

For H/V, J has row at least 4 whereas all five V-bones have row at most 3. K has row 3 and columns d,d+1,d+2. L and M stop at row 2; N,P,Q start at column at least d+3. None meets K. All orientation pairs are now checked.

### 4.3 Coverage, full tiling, and exact boundary equations

The number of bones is

    (d+3)+4+d+(d+2)+1+5=3d+15.

Their disjoint cells number `9d+45`. The original area formula gives

    |W_3|-|W_2|+3=(9d+42)+3=9d+45.

By (T5), equality of finite cardinalities proves

    covered(C3)=(W_3\I) disjoint-union S*.              (T6)

Remove S* from T2* and insert C3. This is the promised tiling T3 of W3. It retains `binom(d,2)-3` stones. The move preserves the previous `6d+12` bones; inserting C3 gives `9d+27` bones.

Let beta3 be the sum of the C3 bone generators and J3 the original translation. Equation (T6) is the exact integral cochain identity

    partial beta3 = 1_W3 - J3 1_W2 + partial[S*].        (T7)

Together with (T2), this also gives the direct positive replacement: remove the three tiles (T4), add the two moved horizontal bones, and add C3. The net change of the bone chain and the consumed stone is recorded, not hidden by a quotient.

The reflection `(i,j)->(i,1-i-j)` is its own inverse. It exchanges the region parameters, carries a right-stone cell set to a right-stone cell set, and permutes the three straight bone directions. Applying it cellwise to T3 yields the reflected tiling with identical counts. This completes the whole all-parameter construction.

## 5. The full translation-invariant bone cohomology

The finite-jet observation from turn 1 admits an exact integral calculation. Let

    P=Z[X^±1,Y^±1],
    H=1+X+X^2, V=1+Y+Y^2, D=X^2+XY+Y^2,
    Q=P/(H,V,D).

H and V are the cell polynomials of the bones at (0,0); D is the cell polynomial of the D-bone at (0,2). Multiplication by Laurent monomials is the original cell/tile translation. Thus the ideal is exactly the image of the global, finite-support integer bone-incidence map, and Q is its first cohomology.

Use a formal generator omega with `omega^2+omega+1=0`, and put

    C=Z[omega],
    E=C direct-sum F_3 sigma

with multiplication

    (a,c)(b,e)=(ab, abar*e+bbar*c),

where `abar` is the ring map `C->F_3` sending omega to 1. It is well-defined because `1+1+1=0` in F_3. This multiplication is associative and distributive by the ring and module laws; its unit is (1,0). Equivalently sigma^2=0, `(omega-1)sigma=0`, and 3sigma=0. The additive decomposition is literal, so sigma is nonzero of order three.

There is an algebra isomorphism

    Q -> E,
    X -> omega,
    Y -> omega^2+sigma.                                (T8)

Both images are units: their inverses are omega^2 and omega-sigma. H maps to zero. V maps to `(1+omega+omega^2)+3sigma=0`. D maps to the same zero. Thus the map is defined on the displayed quotient.

Here is its inverse, proved within Q. Write `s=1+X+Y`. The defining relations give

    XY=X+Y+2,
    (X-1)s=D-V=0,
    (Y-1)s=D-H=0.

Consequently `3s=(1+X+X^2)s=0` and `s^2=(1+X+Y)s=3s=0`. Also `Y=X^2+s`. Therefore

    E -> Q, omega -> [X], sigma -> [1+X+Y]

is well-defined. Both composites fix all the specified generators X,Y,omega,sigma. They are inverse algebra homomorphisms. In particular the underlying abelian group of the full quotient is `Z^2 direct-sum Z/3`, with no torsion discarded.

## 6. The original finite jet is exactly the reduction of this quotient

Let `A=F_3[epsilon,eta]/(epsilon^2,epsilon eta,eta^2)`. The quotient map E->A is

    omega -> 1+epsilon,
    sigma -> epsilon+eta.                             (T9)

Under (T8), Y maps to `(1+epsilon)^2+epsilon+eta=1+eta`; hence (T9) composes with the original cell map exactly as in turn 1. For an element `a+b omega+c sigma`, its image is

    (a+b) + (b+c)epsilon + c eta, reduced modulo 3.

Its kernel is precisely the subgroup `3C` (with zero sigma component), which is also 3E. Modulo 3 the inverse sends epsilon to omega-1 and eta to omega^2+sigma-1. Thus

    Q/3Q -> A

is an explicitly proved isomorphism, and (T8)-(T9) give the requested relationship between the integral cohomology and the finite jet.

A translated cell has E-class

    [X^i Y^j]=omega^(i+2j)+j sigma.                     (T10)

This follows for all integers from the unit formulas and sigma^2=0. The torsion coefficient is taken modulo three. Summing (T10) over the actual cyclically symmetric W_h gives zero in C: the cyclic cell permutation `(i,j)->(j,1-i-j)` changes `i+2j` by 2 modulo 3, so the three residue counts agree. The coordinate sums also agree and their sum is |W_h|. Therefore

    [1_W_h]=(binom(d,2)-h)sigma in Q.                   (T11)

This uses the exact area formula modulo three. Multiplication by every translation unit fixes sigma. The raw collar class is consequently `-sigma` in the full integral quotient, and adding S* cancels it there. Equation (T7) supplies the positive, support-contained lift, which is stronger information than the quotient equality alone.

## 7. Global, finite-support and positive lifts: actual comparison maps

For a finite cell set lambda, let C1(lambda) be its free integer cell module and B(lambda) the image of the bone generators entirely contained in lambda. Cell inclusion induces

    C1(lambda)/B(lambda) -> Q.

Its kernel is given by the explicit representative map

    (C1(lambda) intersect im(partial_global))/B(lambda)
          -> ker(C1(lambda)/B(lambda)->Q), [z]->[z].     (T12)

A class is killed precisely when its original representative is a global bone boundary. The prequotient kernel is B(lambda); choosing that same representative gives the inverse on every kernel class. This proves (T12), including the retained finite support.

A concrete nonzero kernel class can be written without a search. Let lambda be the union of the right stones at (0,0), (12,0), and (24,0), and let z be its 0/1 cell vector. No original bone is contained in lambda, so B(lambda)=0 and [z] is nonzero. Nevertheless z is a global bone boundary. In the original Laurent polynomials,

    3s=sH-(X+2)(D-V),
    (X^m-1)s=(1+X+...+X^(m-1))(D-V), m=12,24.

Adding these three identities produces the exact signed bone preimage of

    (1+X^12+X^24)s=z.

All terms are translates of the specified H,V,D bones. Their integer coefficients and finite global support are supplied by the checker. This realizes, rather than merely names, the comparison kernel. A second example, the three cells (0,0),(3,0),(6,0), has zero finite jet but full Q-class 3 in C, exhibiting the nonzero kernel 3C of (T9).

For the actual collar proof, no such out-of-region signed substitution is used. The nine-cell move is the explicit kernel vector (T2), acting with nonnegative resulting coefficients on its specified tiling subfibres; (T7) is a positive preimage contained in the actual enlarged region. These maps describe exactly how the obstruction calculation is returned to the original tiling problem.

Finite supports ordered by inclusion and joined by union, with their tile and cell modules, give the original coherent support diagram. The pinned Split-Zero reconstruction sends `(lambda,[z])` to its support-labelled class, supported zero to `(lambda,0)`, and absence to the bottom zero. The upstream D2-D5 inverse maps, D6 quotient and D7 kernel apply to the explicitly displayed diagrams. Translation is a support-index morphism with its actual inverse. No theta estimate or unproved positive lifting rule is imported.

## 8. What the next calculation now starts from

The third-collar failure recorded in turn 1 is resolved by (T1)-(T7). The construction gives h=3 for every d>=3, in addition to the existing h=1,2. It does not supply a recurrence for all remaining h.

There are also five fully specified h=4 tiling certificates for d=4,5,6,7,8 in `fourth-seeds.json`. Each translates T3 by (-2,1), removes the original stone at (-1,4-d), releases eight specifically recorded old bones and inserts the listed replacement bones. The checker verifies the entire tiling and the positive residual equation using integers. These five cases are bounded results. The recorded eight-bone release is a valid construction, not a proved minimum or an asserted uniform family.

The next research calculation is the support-contained transport of that next source stone through the displayed eight-bone patch, followed by a parameter-uniform table or a repeatable positive move sequence. The five seeds retain every original generator, so the next session can work on this specific map rather than restart a search. The full P7 interior still includes h>=4 where h<binom(d,2), and the known invariant-zero endpoints remain controls.

Two exploratory collar shapes were also tested: concentric bone-only differences `W_(h+d)(d+1)\W_h(d)` for d=2..5,h=0..4. A mixed-integer solver returned verified fillings for h=0,1 and infeasible statuses for h=2,3,4. Only the returned positive tilings were checked exactly; the solver's infeasibility statuses were not independently certified and are not theorems. These tests do not authorize an extension theorem. The successful argument of this note uses the explicit tables above instead.

## 9. Sources, tests and attribution

- Original problem: Propp, *Trimer Covers in the Triangular Grid: Twenty Mostly Open Problems*, Problem 7, https://www.samuelfhopkins.com/OPAC/files/proceedings/propp.pdf . The statement was already read in the pinned parent workbench.
- Author's status page: https://faculty.uml.edu/jpropp/benzels.html . It retains a June-2025 status horizon. A bounded search on 2026-09-15 found no established later full P7 resolution; it does not establish exhaustive novelty coverage.
- Original area/invariant conventions: Defant–Li–Propp–Young, https://arxiv.org/html/2209.05717v2 . The exact parameter/cell maps are in the parent proof.
- Bone-only endpoint control: Kim–Propp, *A pentagonal number theorem for tribone tilings*, https://arxiv.org/html/2206.04223v6 . No priority claim for (12,15) is made.
- Split-Zero input: `KokunoYumeto/zeta-function-research-reader@1c8ec52c85c173adc9f8403a8a26914955e2f5a9`, `workbenches/splitzero-tandem/tex/support_diagrams.tex`, D1–D8.

The construction tables were found with bounded mixed-integer exploration and then proved for all the stated parameters. The final constructor and checker use only the Python standard library. They verify original cells, shapes, multiplicities, the local kernel vector, both cochain equations, counts, reflected tilings, the full-quotient/jet square, and the five fourth-collar certificates. No solver return is used as the proof of the all-parameter result, and no external formal build or independent mathematical acceptance is claimed. Third-party manuscripts and source corpora are not redistributed.
