# Two positive collar lifts for Propp's Problem 7

**Sprint turn 1 — 15 September 2026.** Written proof and executable finite replay. This does not resolve the full Problem 7. The all-parameter construction below is derived in this continuation; its priority relative to every earlier special-family construction has not been established. In particular, the first collar overlaps the P6 family and carries no claim of first discovery. No independent specialist review or Lean build is claimed.

## 1. Target, source coordinates, and exact scope

Propp's Problem 7 asks for tilings by right stones and all three bone orientations throughout the original admissible domain with nonnegative Conway–Lagarias invariant. Use its integer cells `(i,j,k)` with `i+j+k=1` and all three differences in `[1-a,b-1]`. The axial map and inverse are

    (i,j,k) -> (i,j),        (i,j) -> (i,j,1-i-j).

Write

    D0=j-i, D1=1-i-2j, D2=2i+j-1,
    V(a,b)={(i,j):1-a<=D0,D1,D2<=b-1}.

The original right stone at axial anchor `(i,j)` has cells

    S(i,j)={(i,j),(i+1,j),(i,j+1)}.

Let `D(i,j)`, `H(i,j)`, `V(i,j)` denote respectively the three bones with cells

    D: (i+u,j-u), H: (i+u,j), V: (i,j+u), u=0,1,2.

Thus every tile below is an actual translated original prototile. In tile tables `V` denotes a vertical bone; `V(a,b)` with parameters denotes the region.

Put

    W_h(d)=V(d+3h,2d+3h),  d>=3, h>=0.

The source cell-count formula (DLPY, equation (1)) gives

    |W_h(d)|=3 binom(d,2)+(9d-3)h+9h^2.                 (1)

The source invariant in stone-count units is

    Delta(W_h)=binom(d,2)-h.                             (2)

These are literal substitutions `a=d+3h,b=2d+3h`, with inverse `d=b-a,h=(2a-b)/3` on the residue-zero family. No region is changed by this parameter map.

**Constructed result.** For every integer `d>=3`, the regions `W_1(d)` and `W_2(d)` have explicitly specified type-103 tilings. Their numbers of right stones and bones are, respectively,

    W_1: binom(d,2)-1 right stones, 3d+3 bones;
    W_2: binom(d,2)-2 right stones, 6d+12 bones.          (3)

In original parameters the second family is `(a,b)=(n,2n-6)`, `n>=9`, and its reflected family. This is an infinite subfamily of the original target, not a renamed replacement for Problem 7.

## 2. Base tiling and its two reserved stones

For integers `r,s>=0`, `r+s<=d-2`, place the right stone with anchor

    q(r,s)=(d-2-2r-s,r-s).

The associated sum-zero barycentric anchor has third coordinate `2-d+r+2s`. Its difference coordinates are

    2-d+3r, 2-d+3s, 2-d+3(d-2-r-s).

Each lies in `[2-d,2d-4]`. A right stone varies each difference by `-1,0,1`, so each placed cell belongs to `W_0(d)`.

For any cell there are exactly three possible right-stone anchors containing it. Their first differences occupy the three distinct residues modulo three. Every displayed anchor has first difference `2-d` modulo three, so two displayed stones cannot share a cell. There are `binom(d,2)` anchors. Their disjoint cells have cardinality `3 binom(d,2)=|W_0|` by (1), proving coverage.

Call this tiling `T_0`. It contains the two distinct stones

    Q0=S(0,2-d)       (r=0,s=d-2),
    Q1=S(2-d,d-2)     (r=d-2,s=0).                       (4)

They are distinct for `d>=3`.

## 3. First collar: an explicit positive solution of the residual equation

Translate `W_0` and `T_0` by

    t1=(-2,1).

The difference-coordinate increments are `(3,0,-3)`. Consequently the translated inner region `I1=t1+W_0` has bounds

    D0 in [4-d,2d+2],
    D1 in [1-d,2d-1],
    D2 in [-d-2,2d-4],                                 (5)

and is contained in `W_1`, whose three bounds are `[-d-2,2d+2]`. The translated `Q0` is

    S1=S(-2,3-d).

Here is the complete bone family `C1`:

| Label | Kind | Anchor | Index range |
|---|---|---|---|
| A | D | `(-2,3-d)` | one tile |
| B | D | `(-2,4-d)` | one tile |
| C | D | `(-1,1-d)` | one tile |
| F_r | H | `(-d-1+2r,d+1-r)` | `0<=r<=d-1` |
| G_r | H | `(r,3-d+r)` | `0<=r<=d-2` |
| E | V | `(1,-d)` | one tile |
| J_r | V | `(r+2,r-d)` | `0<=r<=d-1` |

### Containment and the exact intersection with the inner source

Substitution gives the following difference coordinates for the cell with offset `u` in each row:

| Label | D0 | D1 | D2 |
|---|---|---|---|
| A | `5-d-2u` | `2d-3+u` | `-d-2+u` |
| B | `6-d-2u` | `2d-5+u` | `-d-1+u` |
| C | `2-d-2u` | `2d+u` | `-d-2+u` |
| F_r | `2d+2-3r-u` | `-d-u` | `-d-2+3r+2u` |
| G_r | `3-d-u` | `2d-5-3r-u` | `2-d+3r+2u` |
| E | `-d-1+u` | `2d-2u` | `1-d+u` |
| J_r | `-d-2+u` | `2d-1-3r-2u` | `3r+3-d+u` |

Every entry is in `[-d-2,2d+2]`: it is affine in `r,u`, so the minimum and maximum occur at the displayed index endpoints and `u=0,2`; substitution with `d>=3` gives the bounds. This proves outer containment for every integer parameter.

Against (5), all cells of C, G, E and J violate the lower D0 bound; all cells of F violate the lower D1 bound. Row A has only its `u=0` cell inside I1. Row B has only its `u=0,1` cells inside I1. Those three cells are exactly S1. Thus

    covered(C1) subset (W_1\I1) union S1.               (6)

### Disjointness

The three D-bones have distinct `k=1-i-j` coordinates (`d,d-1,d+1`). H-bones F have distinct rows `j>=2`; H-bones G have distinct rows `j<=1`, so all H-bones are mutually disjoint. V-bones occupy distinct columns `i=1` and `i=2,...,d+1`.

D versus F: every D cell has `j<=1`, whereas F has `j>=2`. D versus G: G has `i>=0` and `j>=3-d`. The possible D cells at `i>=0` have `j<3-d`. D versus V: rows A and B have `i<=0`; row C has only one cell with `i=1`, at `j=-d-1`, below E. The other V columns begin at `i=2`.

E versus H: E has `j<=2-d`, below G and F. A cell of J in column `i` has `j<=i-d`. A G-cell in that column satisfies `r>=i-2`, hence `j=3-d+r>=i+1-d`. An F-cell has `j>=2` and `i<=d+3-2j`; combining this with `j<=i-d` would give `j<=1`, a contradiction. This checks every pair of orientation families.

There are `3+d+(d-1)+1+d=3d+3` bones. Their disjoint cells number `9d+9`. Equation (1) gives

    |W_1|-|W_0|+|S1|=9d+6+3=9d+9.

Together with (6) this proves the exact partition

    covered(C1)=(W_1\I1) disjoint-union S1.              (7)

Remove S1 from the translated source tiling and insert C1. The result

    T1=(t1+T0)\{S1} union C1                            (8)

is a genuine type-103 tiling of W_1. The other reserved source stone Q1 survives and now has anchor `(-d,d-1)`.

## 4. Second collar: another exact positive lift

Translate T1 and W_1 by

    t2=(1,1).

The difference-coordinate increments are `(0,-3,3)`. The translated inner region `I2=t2+W_1` is contained in W_2 and has bounds

    D0 in [-d-2,2d+2],
    D1 in [-d-5,2d-1],
    D2 in [1-d,2d+5].                                  (9)

The surviving reserved stone becomes

    S2=S(1-d,d).

Use this complete bone family C2:

| Label | Kind | Anchor | Index range |
|---|---|---|---|
| A | D | `(-d-2,d)` | one tile |
| B | D | `(-d-2,d+1)` | one tile |
| C_r | D | `(-d-1+r,d-2-2r)` | `0<=r<=d-1` |
| F | H | `(-d-3,d+2)` | one tile |
| G | H | `(-d-2,d+3)` | one tile |
| H | H | `(-d-1,d+1)` | one tile |
| J | H | `(-d,d)` | one tile |
| K_r | V | `(1-d+r,d-3-2r)` | `0<=r<=d-1` |
| L | V | `(1,-d-2)` | one tile |
| M | V | `(2,-d-3)` | one tile |
| N_r | V | `(3+r,-d-2+r)` | `0<=r<=d` |

### Containment and inner intersection

| Label | D0 | D1 | D2 |
|---|---|---|---|
| A | `2d+2-2u` | `3-d+u` | `-d-5+u` |
| B | `2d+3-2u` | `1-d+u` | `-d-4+u` |
| C_r | `2d-1-3r-2u` | `6-d+3r+u` | `-d-5+u` |
| F | `2d+5-u` | `-d-u` | `-d-5+2u` |
| G | `2d+5-u` | `-d-3-u` | `-d-2+2u` |
| H | `2d+2-u` | `-d-u` | `-d-2+2u` |
| J | `2d-u` | `1-d-u` | `-d-1+2u` |
| K_r | `2d-4-3r+u` | `6-d+3r-2u` | `-d-2+u` |
| L | `-d-3+u` | `2d+4-2u` | `-d-1+u` |
| M | `-d-5+u` | `2d+5-2u` | `-d+u` |
| N_r | `-d-5+u` | `2d+2-3r-2u` | `3-d+3r+u` |

The endpoint substitution used above proves that every entry belongs to W_2's bounds `[-d-5,2d+5]`.

Against (9), A, B, C and K are below the D2 lower bound; F and G exceed the D0 upper bound; L exceeds the D1 upper bound; M and N are below the D0 lower bound. H has only its `u=2` cell in I2. J has only its `u=1,2` cells in I2. The three exceptional cells are exactly S2. Thus

    covered(C2) subset (W_2\I2) union S2.               (10)

### Disjointness

The D-bones have distinct `k` levels `3,2,4,...,d+3`. The four H-bones have distinct rows `d+2,d+3,d+1,d`. The V-bones have distinct columns `1-d,...,0,1,2,3,...,d+3`.

D versus H: H's rows `d+2,d+3` exceed all D rows. In row `d+1`, D contributes only the point with column `-d-2`, to the left of H's columns. In row `d`, D contributes only columns `-d-2,-d-1`, to the left of J's columns starting at `-d`. The indexed D-family has rows at most `d-2`.

H versus V: K has row at most `d-1`, below all H rows. L, M and N have columns at least 1; all H cells have column at most `2-d<=-1`.

D versus V: A and B have columns at most `-d`, to the left of K's first column `1-d`. C has columns at most 0, to the left of L, M and N. For a possible C_r/K_s collision at offsets u,v, equality of first coordinates gives `s=r+u-2`; equality of second coordinates then gives `u-v=3`. This is impossible for `0<=u,v<=2`. These arguments exhaust all pairs.

There are `2+d+4+d+2+(d+1)=3d+9` bones, covering `9d+27` disjoint cells. Equation (1) gives

    |W_2|-|W_1|+|S2|=9d+24+3=9d+27.

Together with (10), this proves

    covered(C2)=(W_2\I2) disjoint-union S2.             (11)

Therefore

    T2=(t2+T1)\{S2} union C2                            (12)

tiles W_2 by precisely the original right stones and bones. No tiling search or unproved induction step is used in (8) or (12). Equations (3) follow by counting the two consumed stones and the two added bone families.

The reflection `(i,j,k)->(i,k,j)`, or axially `(i,j)->(i,1-i-j)`, is its own inverse, sends V(a,b) to V(b,a), preserves both stone orientations and permutes bone directions. Applying it to every placed tile gives the reflected family with the same certificate.

## 5. A finite-jet obstruction and its explicit cancellation

The following calculation identifies the exact class canceled by the collar lift. It keeps the original lattice translations and gives a nonzero cohomology observation for an unmodified collar.

Let

    A=F_3[e,f]/(e^2,ef,f^2),
    phi: Z[X^+-1,Y^+-1] -> A,
    X -> 1+e, Y -> 1+f.

The displayed images are units, with inverses `1-e,1-f`, so this is a defined ring homomorphism. For every integer i,j,

    phi(X^i Y^j)=1+i e+j f.                             (13)

Map a cell generator `(i,j)` to (13) and extend linearly. A bone with direction `(p,q)` maps to the sum over u=0,1,2:

    3 + (3i+3p)e + (3j+3q)f = 0.

A right stone maps to `e+f`; a left stone maps to `2e-f=-(e+f)`. The class `e+f` is nonzero, since `1,e,f` is a basis of A. Multiplication by any translation unit `1+i e+j f` fixes `e+f`.

For any W_h, cyclic permutation of the barycentric coordinates permutes the finite cell set. Thus the three coordinate sums are equal, and each is `|W_h|/3`. Its cell observation is consequently

    phi(1_W_h)=(|W_h|/3)(e+f)
              =(binom(d,2)-h)(e+f),                   (14)

where (1) gives the second equality modulo three. Translating W_h leaves this observation unchanged because its cell count is divisible by three.

For the raw residual `r_h=1_W_(h+1)-J 1_W_h` of a containing translation J, (14) gives

    phi(r_h)=-(e+f) != 0.                              (15)

Every integral sum of bone boundaries has phi-value zero. Equation (15) therefore detects an actual obstruction to filling that collar with bones while leaving the entire source tiling untouched. Adding the boundary of one actual right stone cancels this observation. For h=0 and h=1, the tables prove the stronger integral identities

    partial beta_1 = 1_W1 - J1 1_W0 + partial S1,
    partial beta_2 = 1_W2 - J2 1_W1 + partial S2.         (16)

Here beta_i is the sum of the original placed bone generators, each with coefficient +1. The positive coefficients and the exact partition checks establish the actual tiling lifts. Equation (15) by itself supplies no such positive preimage.

## 6. The exact Split-Zero cohomology interface

For a finite cell support lambda let C_B^0(lambda) be the free Z-module on placed bones contained in lambda; let C_103^0(lambda) additionally include the placed right stones; let C^1(lambda) be the free Z-module on its cells. Define the actual two-term differentials by

    partial[tile]=sum_(cell in tile)[cell].

Finite supports, ordered by inclusion and joined by union, form a semilattice with bottom the empty set. Inclusions of actual tile and cell generators give coherent maps of these complexes. Translation sends every original cell and tile to its translate and commutes with partial on generators; its inverse is translation by the negative vector.

The inclusion from the bone complex to the type-103 complex is identity in degree one. On first cohomology its kernel has the explicit description

    im(partial_103)/im(partial_B)
        -> ker(C^1/im(partial_B) -> C^1/im(partial_103)),
    [z] -> [z].                                       (17)

The forward map is defined because im(partial_B) is a submodule of im(partial_103). Its prequotient kernel is exactly im(partial_B); every killed class has a representative in im(partial_103). These facts give the inverse and prove (17).

The cell observation phi kills bone boundaries, hence descends to the bone cohomology. Equations (15)-(16) retain the collar class and its opposite stone class there before displaying their bone-boundary lift. This is the particular comparison-kernel computation used here.

Apply the pinned upstream reconstruction to the full support diagrams: a reconstructed class is `(lambda,[z])`, a transition preserves its actual representative, the supported-zero scalar sends it to `(lambda,0)`, and the absent scalar sends it to the bottom zero. The natural reconstruction maps and inverse are the upstream D2-D5 maps. The quotient uses the D6 coequalizer, and (17) is D7 specialized to these displayed complexes. The observation target may be the constant A-diagram on the same support labels; its bottom fibre is allowed by the source construction.

No infinite theta-source estimate or arithmetic weight bound is imported. The argument uses these explicit support, quotient, jet and positive-boundary maps. Both the small jet observation and the positive lift are recorded, so an agent cannot treat disappearance of the jet obstruction as an automatically supplied tiling.

## 7. Scope of the next step

The full unresolved construction range after the previously source-matched families is `d>=3,1<=h<=binom(d,2)-1`. This note constructs h=1,2. The remaining interior values begin at h=3 where present; the invariant-zero endpoint retains its published Kim–Propp construction.

The exact fixed-source test at d=3,h=2 attempts to retain every old bone, remove only the remaining right stone and fill the next collar with bones. For every one of the 13 containing integer translations there is a cell of that patch belonging to no permitted bone contained in the patch. The code records such cells directly. Thus this particular frozen-source recurrence stops, including at the already tileable invariant-zero endpoint. It neither refutes P7 nor rules out a lift after moving old bones.

The next research task is to construct a support-changing boundary repair with old bone generators retained in the comparison, then obtain a repeatable positive lift through the full h-range. No universal repair or remaining induction is assumed in this note.

## Sources and verification

- James Propp, *Trimer Covers in the Triangular Grid: Twenty Mostly Open Problems*, Sections 1 and 6, Problem 7: https://www.samuelfhopkins.com/OPAC/files/proceedings/propp.pdf
- Author status page rechecked 2026-09-15; still labels P7 open, with a stated June-2025 status horizon: https://faculty.uml.edu/jpropp/benzels.html
- Defant, Li, Propp, Young, *Tilings of Benzels via the Abacus Bijection*, arXiv:2209.05717v2, equation (1), invariant formula and Theorem 1.1: https://arxiv.org/html/2209.05717v2
- The preceding workbench continuation, especially the residual parameter maps: https://github.com/KokunoYumeto/mathematics-commons-pilot/blob/ea0cf71f7af213f6e25dd0669e2e67cc024bd0dc/workbenches/splitzero-nonzeta/review/notes/proofs.md
- Split-Zero support reconstruction and cohomology, upstream commit `1c8ec52c85c173adc9f8403a8a26914955e2f5a9`, `workbenches/splitzero-tandem/tex/support_diagrams.tex`, D1-D8: https://github.com/KokunoYumeto/zeta-function-research-reader/blob/1c8ec52c85c173adc9f8403a8a26914955e2f5a9/workbenches/splitzero-tandem/tex/support_diagrams.tex

`python check.py` and `python -O check.py` replay explicit tilings, independent cell-set definitions, shapes, incidence identities, invariant counts and the fixed-source obstruction. They are bounded implementation tests accompanying the written all-parameter proof, not a replacement for it. Third-party proof manuscripts or formalizations are not bundled.
