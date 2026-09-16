# Third-collar repair and the integral, support-sensitive bone cohomology

**Propp 7 sprint, turn 2 — 15 September 2026.**

This continuation proves an explicit third-collar construction for every integer `d>=3`, and computes the entire translation-invariant integral bone quotient with inverse maps. It also constructs an infinite-order finite-support cohomology class killed by a specified support enlargement. Seven further fourth-collar tilings are supplied as individual exact witnesses.

The full original Propp 7 remains unresolved by this work. The mathematical arguments below are complete for their stated scopes; independent specialist review, a Lean build and a novelty determination have not been performed. The previously written first and second collars remain unchanged in [PROOF.md](PROOF.md). This note does not reclassify known endpoint or peripheral results as discoveries.

## 0. Integration with the concurrent turn-2 contribution

Commit `89acf6be7ad7e73892b7628f2419e16ef445b581` reached the branch during this calculation. Its [turn2/PROOF.md](turn2/PROOF.md) is retained unchanged. It proves the same third-family tiling and the same integral quotient, presented through an explicit nine-cell source-stone move. Those overlapping results are not counted as additional discoveries here.

The precise comparison is as follows. In the concurrent note let `C3_previous` be its section-4 bone chain, and put `x=d-2,y=0`. Our chain in section 3 is

    C3_here = C3_previous + [H(x,y)] + [H(x,y+1)].       (0a)

Its fixed diagonal F is our F_0; its G_r is our F_(r+1), for r=0,...,d-1. Every other diagonal, horizontal and vertical tile in its collar table has the same original anchor as the corresponding tile here. This proves (0a) on original generators.

The concurrent nine-cell identity is

    partial(S(x,y)+H(x+2,y)+H(x+1,y+1))
      =partial(H(x,y)+H(x,y+1)+S(x+3,y)).               (0b)

The two sides partition the same rows: columns x,...,x+4 at row y and columns x,...,x+3 at row y+1. Replacing either partition with the other gives inverse maps between the two specified tiling subfibres. Its move followed by its collar insertion therefore equals our direct three-tile replacement (8). This compares the full resulting tilings, not only their areas or cohomology classes.

For the quotient calculations, both notes send the original X to w and Y to w^2+sigma in the same square-zero extension. Their identification is the identity on those original generators and has the identical inverse a+bw+c*sigma -> a+bX+c(1+X+Y).

The additions here are the infinite-order class in the *actual collar-support* comparison kernel with a split Z inclusion, the positive-fibre comparison, the full 9-by-27 integral boundary certificate and inverse unimodular replay, and seven fourth-level witnesses through d=10. The concurrent snapshot has five fourth-level witnesses through d=8. Both finite witness sets remain preserved; no identity of their chosen fourth tilings is presumed. The first two collar sources remain unchanged.

## 1. Original carrier and the third family

Retain the cells and translated tiles of PROOF.md:

    D0(i,j)=j-i,  D1(i,j)=1-i-2j,  D2(i,j)=2i+j-1,
    V(a,b)={ (i,j) in Z^2 : 1-a<=D0,D1,D2<=b-1 }.

The original barycentric cell is `(i,j,1-i-j)`; projection onto the first two coordinates is the inverse map. A right stone `S(i,j)` consists of `(i,j),(i+1,j),(i,j+1)`. A bone `D(i,j)`, `H(i,j)` or `V(i,j)` consists of the three offsets `u=0,1,2` in direction `(1,-1)`, `(1,0)` or `(0,1)`, respectively. Here a one-letter tile symbol with its anchor is distinguished by its displayed argument from the region `V(a,b)`.

Use the same original region family

    W_h(d)=V(d+3h,2d+3h).

The parameter map has inverse `d=b-a`, `h=(2a-b)/3`. The source cell-count formula gives

    |W_h| = 3*d*(d-1)/2 + (9d-3)h + 9h^2.              (1)

The original right-minus-left stone invariant is

    Delta(W_h)=d*(d-1)/2-h.                             (2)

These identities are the substitutions into Defant–Li–Propp–Young [S2], equation (1) and its displayed Conway–Lagarias invariant. They retain the original cell count and stone units.

**Third-family result.** For every integer `d>=3`, the construction in this note tiles `W_3(d)` by

    d*(d-1)/2-3 right stones, and 9d+27 bones.           (3)

Equivalently, it constructs the original `(n,2n-9)` benzel for every integer `n>=12`, and its reflected partner. The equality of these parameterizations is `n=d+9` with inverse `d=n-9`.

## 2. The exact old tiles released

Let `T2(d)` be the second-collar tiling already defined and proved in PROOF.md, section 4. Translate it by

    t3=(1,-2).

Its inner region `I=t3+W_2(d)` has the bounds

    -d-8 <= D0 <= 2d+2,
    -d-2 <= D1 <= 2d+8,
    -d-5 <= D2 <= 2d+5.                                (4)

This follows from the difference increments `(-3,3,0)`. The outer region `O=W_3(d)` has all three difference bounds `[-d-8,2d+8]`, so `I` is contained in `O`.

Exactly these three old tiles will be released:

    S=S(d-2,0),
    U=H(d-1,1),
    V0=H(d,0).                                         (5)

All are actual members of the translated source tiling. Indeed, the three successive shifts `(-2,1),(1,1),(1,-2)` sum to zero. The right stone at the base anchor `q(0,0)=(d-2,0)` survives the first two collars: their consumed base indices are `(0,d-2)` and `(d-2,0)`, distinct from `(0,0)` for `d>=3`. In the first-collar table, `F_(d-1)` and `G_(d-2)` are horizontal bones. Translating that table by `(1,1)+(1,-2)=(2,-1)` gives respectively `H(d-1,1)` and `H(d,0)`. The second collar removes only a stone, so these bones survive. This identifies every released generator in the original source, not merely its incidence vector.

Define the two cell supports

    P0=(O\I) disjoint-union cells(S),
    P2=P0 disjoint-union cells(U) disjoint-union cells(V0).    (6)

The unions are disjoint because the old tiling is disjoint and the collar lies outside `I`.

## 3. Complete positive replacement table

The replacement `C3(d)` contains the following bones, each once with coefficient `+1`. As above, each bone uses offsets `u=0,1,2` in its specified direction.

| Label | Kind | Anchor | Index range |
|---|---|---|---|
| A_r | D | `(-d-5+r,d+3-2r)` | `0<=r<=d+2` |
| B | D | `(-d-4,d+3)` | one |
| C | D | `(-d-4,d+4)` | one |
| E | D | `(-d-3,d+4)` | one |
| F_r | D | `(-d-2+2r,d+4-r)` | `0<=r<=d` |
| G_r | H | `(-d-3+2r,d+5-r)` | `0<=r<=d+1` |
| H0 | H | `(d,3)` | one |
| H1 | H | `(d-2,0)` | one |
| H2 | H | `(d-2,1)` | one |
| J0 | V | `(d+1,0)` | one |
| J1 | V | `(d+2,0)` | one |
| J2 | V | `(d+3,1)` | one |
| J3 | V | `(d+4,-1)` | one |
| J4 | V | `(d+5,-3)` | one |

There are `(d+3)+3+(d+1)=2d+7` diagonal bones, `(d+2)+3=d+5` horizontal bones, and five vertical bones: altogether `3d+17`.

### 3.1 Outer containment

Direct substitution gives the difference coordinates of every cell:

| Label | D0 | D1 | D2 |
|---|---|---|---|
| A_r | `2d+8-3r-2u` | `-d+3r+u` | `-d-8+u` |
| B | `2d+7-2u` | `-d-1+u` | `-d-6+u` |
| C | `2d+8-2u` | `-d-3+u` | `-d-5+u` |
| E | `2d+7-2u` | `-d-4+u` | `-d-3+u` |
| F_r | `2d+6-3r-2u` | `-d-5+u` | `-d-1+3r+u` |
| G_r | `2d+8-3r-u` | `-d-6-u` | `-d-2+3r+2u` |
| H0 | `-d+3-u` | `-d-5-u` | `2d+2+2u` |
| H1 | `-d+2-u` | `-d+3-u` | `2d-5+2u` |
| H2 | `-d+3-u` | `-d+1-u` | `2d-4+2u` |
| J0 | `-d-1+u` | `-d-2u` | `2d+1+u` |
| J1 | `-d-2+u` | `-d-1-2u` | `2d+3+u` |
| J2 | `-d-2+u` | `-d-4-2u` | `2d+6+u` |
| J3 | `-d-5+u` | `-d-1-2u` | `2d+6+u` |
| J4 | `-d-8+u` | `-d+2-2u` | `2d+6+u` |

For completeness, the exact coordinate ranges are:

| Label | D0 range | D1 range | D2 range |
|---|---|---|---|
| A_r | `[-d-2,2d+8]` | `[-d,2d+8]` | `[-d-8,-d-6]` |
| B | `[2d+3,2d+7]` | `[-d-1,1-d]` | `[-d-6,-d-4]` |
| C | `[2d+4,2d+8]` | `[-d-3,-d-1]` | `[-d-5,-d-3]` |
| E | `[2d+3,2d+7]` | `[-d-4,-d-2]` | `[-d-3,-d-1]` |
| F_r | `[2-d,2d+6]` | `[-d-5,-d-3]` | `[-d-1,2d+1]` |
| G_r | `[3-d,2d+8]` | `[-d-8,-d-6]` | `[-d-2,2d+5]` |
| H0 | `[1-d,3-d]` | `[-d-7,-d-5]` | `[2d+2,2d+6]` |
| H1 | `[-d,2-d]` | `[1-d,3-d]` | `[2d-5,2d-1]` |
| H2 | `[1-d,3-d]` | `[-d-1,1-d]` | `[2d-4,2d]` |
| J0 | `[-d-1,1-d]` | `[-d-4,-d]` | `[2d+1,2d+3]` |
| J1 | `[-d-2,-d]` | `[-d-5,-d-1]` | `[2d+3,2d+5]` |
| J2 | `[-d-2,-d]` | `[-d-8,-d-4]` | `[2d+6,2d+8]` |
| J3 | `[-d-5,-d-3]` | `[-d-5,-d-1]` | `[2d+6,2d+8]` |
| J4 | `[-d-8,-d-6]` | `[-d-2,2-d]` | `[2d+6,2d+8]` |

Each coordinate expression is affine in the independently bounded indices `r,u`. Its minimum and maximum are obtained by choosing the indicated endpoints according to the signs of its coefficients. Substitution gives precisely the intervals in this table; for `d>=3` every interval is contained in `[-d-8,2d+8]`. Thus every displayed tile is contained in the original outer benzel.

### 3.2 Intersection with the inner source

Compare the coordinate table with (4). All cells of `A_r` are below the inner `D2` lower bound. All cells of `B,C,E` exceed the inner `D0` upper bound. All cells of `F_r,G_r,H0` are below the inner `D1` lower bound. All cells of `J2,J3,J4` exceed the inner `D2` upper bound.

Every cell of `H1,H2` is inside `I`. Exactly offsets `u=0,1` of `J0`, and offset `u=0` of `J1`, are inside `I`; their other offsets are below its `D1` lower bound. The nine inner cells are therefore

    (d-2,0),(d-1,0),(d,0),
    (d-2,1),(d-1,1),(d,1),
    (d+1,0),(d+1,1),(d+2,0).

They are exactly the disjoint union of the cells of `S,U,V0` in (5). This proves

    covered(C3) subset P2.                             (7)

### 3.3 Disjointness of every pair of families

The diagonal bones lie on pairwise distinct lines of constant `i+j`. The values for `A_r` are `-2-r`; those for `B,C,E` are `-1,0,1`; those for `F_r` are `2+r`. Thus all diagonal bones are disjoint. The horizontal bones have pairwise distinct rows: `G_r` uses rows `d+5,...,4`, and the other three use `3,0,1`. The five vertical bones have pairwise distinct columns `d+1,...,d+5`.

Here are the cross-orientation checks, retaining the actual cell coordinates.

For a diagonal `A_r` cell at offset `u` and a horizontal `G_s` cell at offset `v`, equality of the second coordinates forces `s=2+2r+u`. Equality of the first coordinates would then force `-6=3r+u+v`, impossible for the displayed nonnegative indices.

For diagonal `B,C,E` at offset `u`, a `G_s` cell in the same row respectively has `s=2+u`, `1+u`, `1+u`. Its leftmost column exceeds the diagonal cell's column by `5+u`, `3+u`, `2+u`, respectively. There is no intersection.

For diagonal `F_r` at offset `u` and `G_s` at offset `v`, equality of rows forces `s=1+r+u`. Equality of columns then forces `-1=u+v`, again impossible.

All cells of `A_r,B,C,E` have column at most `-1`, whereas `H0,H1,H2` have column at least `d-2>=1`. A cell of `F_r` in row 3 requires `r+u=d+1`; hence `u>=1` and its column is `d-u<=d-1`, to the left of `H0`. A cell of `F_r` in row 1 or 0 would require `r+u=d+3` or `d+4`, exceeding the maximum `d+2`. This excludes all diagonal/horizontal intersections.

Every diagonal cell has column at most `d`; every vertical cell has column at least `d+1`. Thus no diagonal bone meets a vertical bone.

The `G_r` rows are at least 4; the five vertical bones have rows at most 3. The horizontal bones `H1,H2` have columns at most `d`, to the left of all vertical bones. Finally `H0` occupies row 3 in columns `d,d+1,d+2`; the vertical bones in the last two columns end in row 2, and the other vertical columns exceed `d+2`. This checks all horizontal/vertical pairs.

The checks within and between the three orientations exhaust every pair of bones. Hence all `3d+17` bones have disjoint cells.

### 3.4 Coverage and resulting full tiling

The replacement covers exactly `9d+51` cells. Equation (1) gives

    |O|-|I| = 9d+42,
    |P2| = |O|-|I|+3+3+3 = 9d+51.

Together with (7) and disjointness this proves `covered(C3)=P2`. Therefore

    T3(d) = ((t3+T2(d)) \ {S,U,V0}) union C3(d)         (8)

is a tiling of `O`. Its stone count is `binom(d,2)-3`. Its bone count is

    (6d+12)-2+(3d+17)=9d+27.

This proves (3) on the full integer domain. The construction has no search step.

The reflection `r(i,j)=(i,1-i-j)` is its own inverse. In barycentric coordinates it swaps the second and third coordinates, negating and permuting the original three differences; consequently it carries `V(a,b)` to `V(b,a)`. On anchored tiles it carries

    S(i,j) -> S(i,-i-j),
    H(i,j) -> D(i,1-i-j),
    D(i,j) -> H(i,1-i-j),
    V(i,j) -> V(i,-1-i-j).

These formulas give the actual reflected tiling and both inverse identities, without changing the allowed prototiles.

## 4. A finite-support cohomology class of infinite order, and its killed image

For each finite cell support `P`, take the original free abelian groups

    C_B^0(P)=Z{placed bones contained in P},
    C^1(P)=Z{cells in P},
    partial_P[bone]=sum of its three cell generators.

Use the two-term complex concentrated in degrees 0 and 1. Its first cohomology is

    H_B^1(P)=C^1(P)/im(partial_P).

The inclusion `P0 subset P2` induces the inclusion on original cell generators and on original placed-bone generators. The boundary square commutes generator by generator. Its induced map is

    q:H_B^1(P0)->H_B^1(P2),  [z]->[z].                 (9)

Let `r0=1_(O\I)+partial S=1_P0`. Let `p=(d-2,0)`, the lower-left cell of the released stone. Its difference coordinates are

    (D0,D1,D2)(p)=(2-d,3-d,2d-5).

The distances to the six inner bounds in (4) are

    D0: 10, 3d;
    D1: 5, 3d+5;
    D2: 3d, 10.

Every bone through `p` consists of `p+v*a` with `v` in an interval of three consecutive integers containing zero and `a` one of `(1,-1),(1,0),(0,1)`. Thus `|v|<=2`; every difference coordinate changes by at most 4. All nine candidate placed bones through `p` consequently lie entirely inside `I`, for every `d>=3`.

Inside `I`, the support `P0` contains exactly the three cells of `S`. They are noncollinear, so no three-cell bone through `p` is contained in `P0`. Therefore the coefficient functional

    ell_p:C^1(P0)->Z,  z->the coefficient of [p] in z

kills every bone boundary in `P0`. It descends to `H_B^1(P0)`, and

    ell_p([r0])=1.                                    (10)

In particular `[r0]` has infinite order. The homomorphism

    eta:Z->H_B^1(P0),  n->n[r0]

is injective with explicit left inverse `ell_p`.

Let `beta3` be the sum of the `3d+17` placed-bone generators in the replacement table. The positive partition just proved gives the integral cochain identity

    partial beta3 = r0 + partial U + partial V0.       (11)

Both `U` and `V0` are actual bone generators in `P2`. Hence

    partial(beta3-[U]-[V0])=r0

inside the target complex. It follows that `q([r0])=0`. Equations (9)-(11) exhibit an infinite-order source class and its actual boundary preimage after enlargement. Moreover `eta` lands in `ker q`, and `ell_p` restricts to a left inverse there, so this kernel contains a displayed split copy of `Z`. No assertion that the entire kernel is generated by this class is made.

The familiar representative description is completely explicit here:

    Krep={z in C^1(P0): inclusion(z) is in im(partial_P2)},
    Krep/im(partial_P0) -> ker q,  [z]->[z].            (12)

Its kernel before quotienting is exactly `im(partial_P0)`, and each class killed by `q` has a representative in `Krep`; these give the inverse and the proof of (12).

### 4.1 Positive tiles and integral boundaries: the actual connecting maps

The free nonnegative incidence map is

    partial_N:N{placed bones in P}->N{cells in P}.

Coefficient inclusions `j_tile:N{tiles}->Z{tiles}` and `j_cell:N{cells}->Z{cells}` satisfy the exact square

    j_cell partial_N = partial_Z j_tile.

The source fibre for a tiling of `P` is `partial_N^(-1)(1_P)`. Its inclusion into the integral fibre has image exactly

    partial_Z^(-1)(1_P) intersect j_tile(N{tiles}).     (13)

Indeed both membership conditions say exactly that the original integer coefficients are nonnegative and their incidence is `1_P`. Every coefficient in that fibre is 0 or 1, because any coefficient at least 2 would give cell multiplicity at least 2. Thus (13) identifies the positive fibre with actual tilings.

For the present construction, the target-support integral preimage of `r0` is `beta3-[U]-[V0]`. Releasing those two *existing* source bones changes the cell target from `r0` to `r0+partial U+partial V0=1_P2`; its preimage is the positive vector `beta3`. Combining it with the unreleased old tiling proves the full positive result (8). Both the cohomology map and the coefficient-cone fibre map are retained.

### 4.2 Exact use of Split-Zero reconstruction

All finite cell supports, ordered by inclusion and joined by union, form the original support semilattice. The free groups, boundary maps and their quotient groups above form coherent diagrams on it. A translation carries each original cell and placed tile to its translate and has inverse the opposite translation. These operations commute with the incidence maps on generators.

The reconstruction and inverse are the maps D2-D5 of [S3]. Applying them gives the support-labelled class `(P,[z])`; the supported-zero scalar sends it to `(P,0)`, while absence sends it to the bottom zero. The map (9) sends the particular nonzero class `(P0,[r0])` to the supported zero `(P2,0)`; its source representative and the support change remain recorded. The internal quotient is the D6 coequalizer, and (12) is its D7 comparison-kernel map. Thus the nonzero source class, killed image, target boundary and positive tiling lift are supplied through the same explicit maps.

## 5. The full translation-invariant integral bone quotient

This section computes the original infinite-lattice quotient exactly and proves its precise relation to the earlier finite jet.

Identify the finite integer cell combinations on the whole lattice with

    Lambda=Z[X^±1,Y^±1],  [cell(i,j)]<->X^i Y^j.

The inverse takes a Laurent polynomial to its integer coefficient at each original cell. The free module on all translated bones is `Lambda^3`, indexed by the three original orientations. Its boundary is

    (f_H,f_V,f_D) -> f_H*(1+X+X^2)
                    +f_V*(1+Y+Y^2)
                    +f_D*(1+XY^(-1)+X^2Y^(-2)).       (14)

Every generator is an actual translated tile. Multiplication of the last generator by the unit `Y^2` gives `X^2+XY+Y^2`; therefore, with

    I_B=(1+X+X^2,1+Y+Y^2,X^2+XY+Y^2),
    B=Lambda/I_B,

the group underlying `B` is precisely the global first bone cohomology.

Write `x,y` for the original residue classes and `sigma=1+x+y` for the right stone. Set

    E=Z[w]/(w^2+w+1),
    rho:E->F_3,  rho(a+b*w)=a+b modulo 3.

The map `rho` is well-defined because `1+1+1=0` in `F_3`. Define the square-zero extension explicitly as the abelian group `E direct_sum F_3`, with product

    (u,c)*(v,e)=(uv,rho(u)*e+rho(v)*c).                (15)

Its identity is `(1,0)`. This defines the claimed ring, including its module action; no product-ring multiplication is substituted.

**Integral quotient result.** The following maps are inverse ring isomorphisms:

    B -> E semidirect_square_zero F_3,
    x -> (w,0),       y -> (w^2,1),

    E semidirect_square_zero F_3 -> B,
    (a+b*w,c) -> a+b*x+c*sigma.                        (16)

### 5.1 Proof of both maps

The first two bone relations give `x^2=-1-x`, `y^2=-1-y`. The diagonal relation then gives `xy=x+y+2`. Consequently

    x*sigma=x+x^2+xy=1+x+y=sigma,
    y*sigma=sigma.

Multiplying `1+x+x^2=0` by `sigma` gives `3*sigma=0`. Also

    sigma^2=(1+x+y)*sigma=3*sigma=0.                   (17)

These identities make the second map in (16) well-defined and multiplicative with exactly the action (15).

For the first map, write `s=(0,1)` in the extension. There `s^2=0`, `3s=0`, and `w*s=s`. The proposed images are `x=w`, `y=w^2+s`. They are units: `x^3=1`, and `y^3=w^6+3w^4s=1`. Thus they define a map on the Laurent ring. The three original relations have images

    1+w+w^2=0,
    1+(w^2+s)+(w+2s)=0,
    w^2+(1+s)+(w+2s)=0.

They therefore give a homomorphism from `B`.

The composite on `x` is `x`. On `y` the composite is `x^2+sigma=-1-x+1+x+y=y`. The opposite composite fixes `(w,0)` and sends `sigma` to `1+w+w^2+s=s`. Together with the integer unit, these elements generate the respective rings, proving both inverse identities.

It follows in particular that `sigma` has exact order 3, and

    B as an abelian group is Z^2 direct_sum Z/3.       (18)

The two free generators are `1,x`; the torsion generator is the original stone `sigma`. Their independence follows directly from the proved inverse map (16). These are full integer statements, not rank calculations over a field.

### 5.2 The earlier finite jet is the exact reduction of this quotient

Let

    A=F_3[e,f]/(e^2,ef,f^2).

The earlier cell map factors as

    Lambda -> B -> B/3B -> A,
    X -> x -> x mod 3 -> 1+e,
    Y -> y -> y mod 3 -> 1+f.                          (19)

The last arrow is an isomorphism, with inverse

    e -> x-1 mod 3,   f -> y-1 mod 3.

Indeed `(x-1)^2=-3x`, `(y-1)^2=-3y`, and `(x-1)(y-1)=3` in `B`, so the inverse respects all three defining relations. The two composites fix the displayed generators. This proves the precise relationship of the integral quotient and the previously used jet.

In particular `sigma` maps to `e+f`, and the original map on every cell remains

    X^i Y^j -> 1+i*e+j*f.

More precisely, (16) gives the integral expression

    [X^i Y^j]=w^(i+2j)+j*sigma,                       (20)

where the second coefficient is taken modulo 3. The formula follows by expanding the square-zero part of `y^j`; negative exponents are covered by the proved unit relations `x^3=y^3=1`. It also follows by checking the three residue classes of `j`. The code checks (20) against separately multiplied elements, retaining negative lattice coordinates.

Adding right-stone generators to (14) adds the ideal `(sigma)`. Its quotient is exactly `E`, through the projection `(u,c)->u` with section `u->(u,0)`. The kernel is the displayed `F_3*sigma`, not an unspecified lost part. This is the translation-invariant version of the bone/type-103 cohomology comparison.

### 5.3 Finite support to the global quotient, with its kernel retained

For every original finite support `P`, the map `[cell(i,j)]->[X^iY^j]` induces

    theta_P:H_B^1(P)->B.

It is well-defined because (14) sends every actual bone boundary to zero. These maps commute with support inclusions. Every global class has a representative on some finite support. Every equality in `B` is witnessed by a finite integer sum of actual placed-bone boundaries, so it holds after enlarging to the union of those finitely many tile supports. This proves the direct-limit identification with `B`, including both directions rather than assuming support-local injectivity.

There is a particularly concrete kernel in this continuation. Equations (10)-(11) prove

    [r0] != 0 in H_B^1(P0),
    q([r0])=0 in H_B^1(P2),
    theta_P0([r0])=theta_P2(q([r0]))=0 in B.

Thus the actual finite-support map to the global quotient kills an infinite-order class. Its inverse image in the enlarged support has the specified signed boundary, and (11) supplies the positive repair. The relation between all three objects is given by these maps and representatives.

For completeness, the full original-region observation can be computed without assuming a tiling of the unproved cases. Cyclic permutation `(i,j,k)->(j,k,i)` permutes `W_h` and changes the residue `i+2j` by 2 modulo 3. Thus the three residue counts are equal, and the `E`-component of its cell sum is zero. The coordinate sums are equal and their sum is `|W_h|`; therefore `sum j=|W_h|/3`. Equation (20) gives

    theta(1_W_h)=(|W_h|/3)*sigma
                 =(binom(d,2)-h)*sigma,               (21)

where (1) gives the last equality modulo 3. Translation fixes `sigma`, by (17). Hence the unmodified successive collar has class `-sigma`, and adding the actual released right stone cancels it. Equations (10)-(11) explicitly show what happens beyond that global observation on the finite support.

The functorial lift to the split coefficients sends absence to absence and a supported coefficient `r` to the supported coefficient `theta(r)`. On supported elements preservation of addition and multiplication follows from the displayed ring maps; the absence cases follow from the defining operations of `G`. No zero coefficient is reassigned to the absence element in this lift.

### 5.4 Independent integer matrix certificate

The relations `X^3-1=(X-1)(1+X+X^2)` and `Y^3-1=(Y-1)(1+Y+Y^2)` already belong to `I_B`. Factoring first by these two relations gives the nine original monomial classes `X^iY^j`, `0<=i,j<=2`, with all 27 translated bone columns retained. Quotienting that module by those columns gives exactly `B`: the factorization maps in both orders are induced by the identity of the Laurent generators, and the two periodic relations are already in the bone ideal.

The checker builds this explicit `9 by 27` integer incidence matrix. It supplies 98 elementary unimodular row/column operations taking it to diagonal

    1,1,1,1,1,1,3,0,0.

A separately implemented operation interpreter checks both the forward reduction and all inverse operations back to the original matrix. The retained diagonal 3 is the torsion in (18). This finite certificate accompanies, rather than replaces, the ring isomorphisms (16).

## 6. Fourth-collar witnesses and the exact next calculation

The new third-collar constructor leaves a right stone at original anchor `(1,3-d)` for every `d>=4`. Its base indices are `(0,d-3)`; these differ from the three consumed corners for that domain. After translation by `(-2,1)`, its anchor is `(-1,4-d)` in the fourth-collar source.

The file `evidence/turn2/fourth-witnesses.json` contains exact positive fourth-collar repairs for **each of the seven integers `d=4,5,6,7,8,9,10`**. Each lists the eight actual old bones released and every replacement-bone anchor. The checker reconstructs the source from (8), verifies every released generator is present, checks every new tile and cell multiplicity, and obtains a tiling of `(d+12,2d+12)` with `binom(d,2)-4` right stones. This statement is bounded to those listed integers.

With no old bones released, the source stone's anchor is an uncoverable cell of the corresponding exact patch in all seven cases; that obstruction is also replayed. The successful certificates therefore record which original generators were changed, rather than dropping the old source. The integer-programming search supplied candidate tables; only their exact integer replays are used as evidence. No claim of minimality of the eight-bone release is made.

The next calculation is to turn these fourth-collar certificates into a full-domain indexed construction, then make the boundary repair repeat through the remaining interior. The eight-bone tables for `d=5,...,10` exhibit affine dependence on `d`; `d=4` has a different recorded repair. That observed dependence is not used as an all-parameter theorem in this turn.

The full residual interior remains `d>=3,1<=h<=binom(d,2)-1` in the source-matched parameterization. We have now supplied complete constructions for `h=1,2,3`; `h=4` is presently recorded only at the seven new finite points. The invariant-zero endpoints retain their prior source status. No blanket fourth-collar or full-P7 conclusion is asserted.

## 7. Replay, provenance and audit boundary

From this directory:

```sh
python check_turn2.py --max-d 100 --output evidence/turn2/normal.json
python -O check_turn2.py --max-d 100 --output evidence/turn2/optimized.json
```

Both runs passed: 98 parameter values, 196 third-family tilings including reflections, 98 prior source tilings rechecked, 98 positive patch identities, 98 signed inclusion-kernel identities, 882 bone candidates at the infinite-order obstruction cells, and 428,848 third-target tile placements per run. The seven fourth-collar witnesses contain 1,057 full-tiling placements. The algebra checks retain all 27 periodic boundary columns, replay the 98 unimodular operations and their inverses, and test 1,681 Laurent monomials and 121 signed polynomials against the displayed maps.

The code uses exact integers and the Python standard library. Normal and optimized runs execute the same explicit error checks. Neither a solver status nor an agreement of AI outputs is treated as mathematical verification. The complete arguments for the all-parameter third collar and integral quotient are above; formal verification and independent specialist review remain absent from this snapshot.

### Sources

- **[S1]** James Propp, *Trimer Covers in the Triangular Grid: Twenty Mostly Open Problems*, Problem 7. Original locator: https://www.samuelfhopkins.com/OPAC/files/proceedings/propp.pdf . This turn retains the previously read target; it does not claim a new full-PDF audit.
- **[S2]** Colin Defant, Rupert Li, James Propp, Benjamin Young, *Tilings of Benzels via the Abacus Bijection*, arXiv:2209.05717v2, equation (1) and the Conway–Lagarias formula: https://arxiv.org/html/2209.05717v2 . The original formulas and region/tiling conventions were re-read in HTML this turn.
- **[S3]** Split-Zero support reconstruction, quotients and comparison kernels, `KokunoYumeto/zeta-function-research-reader@1c8ec52c85c173adc9f8403a8a26914955e2f5a9`, `workbenches/splitzero-tandem/tex/support_diagrams.tex`, D1-D8: https://github.com/KokunoYumeto/zeta-function-research-reader/blob/1c8ec52c85c173adc9f8403a8a26914955e2f5a9/workbenches/splitzero-tandem/tex/support_diagrams.tex . The particular specialization used here is explicitly constructed in section 4.
- **[S4]** Exact turn-1 input: `KokunoYumeto/mathematics-commons-pilot@90f23b04fbde1e25d07342e2b8a8c80d919402c5`, `workbenches/splitzero-nonzeta/sprints/benzel-p7/PROOF.md` and `check.py`.
- **[S5]** Propp's author status page, read 15 September 2026: https://faculty.uml.edu/jpropp/benzels.html . Its Problem 7 open label has the page's June-2025 status horizon. The bounded new search did not establish a later resolution; this is not a complete novelty audit.

The square-zero calculation and collar tables are supplied with proofs, not a claim of first priority. No third-party book, paper PDF, private transcript or formal-source corpus is redistributed in this continuation. The historical workbench records are preserved.
