# Turn 8 — an unbounded deletion family and its original Split-Zero comparison

16 September 2026. This is a written constructive research argument with exact
integer-Laurent-polynomial replay. Independent mathematical review, a new Lean
build, and novelty certification have not been performed. The complete original
Propp Problem 7 is not declared resolved. All original cell coordinates, tile
orientations, integer coefficients, support labels and positive filling fibres
are retained. The two remaining nonzero deletion residue classes are recorded as
unfinished research, not as premises of the result below.

## 1. The completed three-parameter family

Write t_n=n(n-1)/2. For every three integers

    k>=1,  m>=3k+2,  d>=m,
    q=3k,  Delta=t_m-3k,  h=t_d-t_m+3k,

this note constructs a type-103 tiling of the original benzel

    W_h(d)=V(d+3h,2d+3h).

It contains exactly Delta right stones and 3h(h+d) bones. Its reflected tiling
is constructed too. No search or optimization is called by the constructor.
Thus the deletion count is unbounded: q ranges over every positive multiple of
three in its full canonical domain q<=m-2. This is not just a list of fixed-q
examples. The preceding triangular-invariant construction supplies q=0.

The original parameter map has inverse d=b-a and h=(2a-b)/3 on the displayed
integer lane. The original axial cell is (x,y), with differences

    u=y-x,  v=1-x-2y,  w=2x+y-1.

V(a,b) consists of the cells with each difference in [1-a,b-1]. The four permitted
original tiles and their exact cell offsets are

    R: (0,0),(1,0),(0,1);
    H: (0,0),(1,0),(2,0);
    V: (0,0),(0,1),(0,2);
    D: (0,0),(1,-1),(2,-2).

Their incidence boundary sends a placed tile to its three original cell
generators. Rotation and reflection are

    rho(x,y)=(y,1-x-y),     F(x,y)=(x,1-x-y).

The inverses are rho^2 and F. They induce (u,v,w)->(v,w,u) and
(u,v,w)->(-w,-v,-u). On tiles rho cycles H,V,D and preserves R; F exchanges H,D
and preserves V,R. Consequently F carries the constructed tiling of V(a,b) to a
tiling of V(b,a), with its inverse unchanged.

### Retained parent construction

The complete preceding constructive proof is preserved in
`sources/turn6-PROOF.md`, §§1–3, not replaced by a tileability assumption. Its
code is retained as `packing.py` with original bytes (the filename alone changes).
For clarity, all input maps needed here are stated explicitly.

Let r(n) be the unique positive integer with t_r<n<=t_(r+1). In reflected
coordinates the parent packing consists of horizontal bands

    H(L_y+3j,y), 0<=j<b_y, 1<=y<=2h+d,
    (L_y,b_y)=(1-2y-r(y+Delta),y)                    for y<=h,
    (L_y,b_y)=(y-3h-d+1,min(h,2h+d-y))             for y>h.

Apply F, F rho and F rho^2 to the bands. The resulting matching is
Gamma_Delta(d,h). The parent proof verifies all six original containment
inequalities, pairwise sector disjointness and the exact complement:

    partial Gamma_Delta(d,h)+1_(Omega_Delta)=1_(W_h(d)).                 (1)

The rank map defining that complement is a bijection on the original cells:

    (r,s,p) -> rho^p(r-s,-s),  r>=1, 0<=s<r, p=0,1,2;
    rank=t_r+s+1.

The inverse takes the unique minimum among u,v,w, rotates it to u, and recovers
r=-u and s=-y. The cyclic differences are 2 modulo 3, so the minimum is unique.
Omega_Delta consists precisely of ranks at most Delta, and has 3Delta cells.
In particular Omega_(t_m)=W_0(m). The exact base tiling is

    T_0(m)={R(m-2-2r-s,r-s): r,s>=0, r+s<=m-2}.                       (2)

The phase/cell bijection and original region count in the retained proof give

    |W_h(d)|=3Delta+9h(h+d).                                         (3)

No assertion concerning all positive fillings is inferred from (1).

## 2. The actual source bones, with their receiving indices

Fix k,m in the result's domain. A source label has sector p=0,1,2, row y and
depth ell from the right end of a band. Set

    r_y=m-1 for y<=3k,    r_y=m for y>3k,
    a(p,y,ell)=F rho^p H(y-r_y-2-3ell,y).                             (4)

The following list specifies the entire source matching A_(m,k); include all
three sectors for every listed (y,ell):

* for 0<=ell<=k-2: ell+1<=y<=m+2k-4, and also the two rows
  y=m+2k-2+ell and y=m+2k-1+ell;
* for ell=k-1: k<=y<=m+3k-2;
* for k<=ell<=2k-2: ell+1<=y<=2k.

Empty ranges contribute no tiles. Every row is in 1..m+3k, and
0<=ell<min(y,3k). The two added rows are strictly above the first range. Thus
no source labels are repeated. Counting these ranges gives

    |A_(m,k)|=3km+6k^2-3.                                           (5)

These are actual generators of Gamma_Delta(d,h), even at d=m. Here is the exact
source-to-target comparison, including its inverse index map.

The equality t_(m-1)<y+Delta<=t_m holds for 1<=y<=3k, because 3k<=m-2;
t_m<y+Delta<=t_(m+1) holds for 3k<y<=m+3k. These prove the two branches of r_y.

For d=m, h=3k. Rows y<=3k are prefix bones with index j=y-1-ell. Rows y>3k
are finite tail bones with index j=3k-1-ell and tail start L=y-9k-m+1.
Then

    L+3j=y-m-2-3ell,

which is exactly the original anchor in (4). The inverse to the tail index
map is j_stable=j_tail+y-3k, recovering j_stable=y-1-ell. All indices lie in
the original ranges, not in enlarged fictitious bands.

For d>=m+1, h=t_d-t_m+3k>=m+3k. Every source row is a prefix row, with
j=y-1-ell. The original anchor is again (4), and the index inverse is the
identity. Hence A_(m,k) is a subset of the original parent matching at every
exterior d>=m. In particular its cells are disjoint from Omega_Delta by (1).

This comparison preserves the sector, original row, tile orientation and all
three cells. Its linear extension commutes with the original cell incidence
map. No finite tail is silently identified with a prefix.

## 3. Stones, long strips and explicit corner replacements

### The actual retained stones

Remove from T_0(m) the following original 3k stones:

    D_(m,k)={rho^p R(m-2-a,-a): 0<=a<k, p=0,1,2}.                    (6)

The base indices for the three rotations are obtained by permuting
(0,a,m-2-a). Since m-2>=3k, the corner ranges are disjoint; all tiles in (6)
are distinct members of (2). Let R_(m,k)=T_0(m) minus this set. Its cardinality
is t_m-3k=Delta.

The last 3k cell orbits of W_0(m) are

    M_(m,k)= union_(i=1)^(3k) Orb_rho(i,i+1-m).                       (7)

Indeed these are the rank-(t_m-3k+1)..t_m cells under the displayed inverse.
Consequently Omega_Delta=W_0(m) minus M_(m,k), as actual cell sets.

### The new bones

First insert the three rotated copies of the original horizontal strips

    H(y+m+3ell,y),
    0<=ell<k,   1-m+k-ell<=y<=-2k.                                  (8)

The row count m-3k+ell is at least 2+ell. These ranges therefore require no
extension of an index or limiting argument at the smallest m.

The corner table P_k below is written in coordinates (x,z). Its actual original
embedding is (x,z)->(x,z-m), followed by rho^p, p=0,1,2. The inverse first applies
rho^(-p), then sends (x,y)->(x,y+m). Every expression below is a placed original
tile, not a new prototile.

Horizontal corner families:

    H(2+3j,2),                  0<=j<k-1;
    H(y+3j,y),                  3<=y<=k, 0<=j<=k-y;
    H(3+2r+3j,1-r),            r,j>=0, r+j<=k-2.

Diagonal corner families:

    D(1-k+3j,4-k-3j),           0<=j<k;
    D(2-n+3j,2-n-3j),          1<=n<k, 0<=j<n;
    D(2-n+3j,3-n-3j),          1<=n<k, 0<=j<n.

Vertical corner families:

    V(1-2k+i,k-2i+3j),          0<=i,j<k;
    V(1-k,5-k+3j),              0<=j<k-1;
    V(2-k+i,4-k+i+3j),          i,j>=0, i+j<=k-2;
    V(x,2-3k-2x),               1-k<=x<=-1;
    V(2i,3-3k-i),               0<=i<k;
    V(2i+1,2-3k-i),             0<=i<k;
    V(2i+2,2-4i+3j),            1<=i<=k-2, 0<=j<i;
    V(2i+3,1-4i+3j),            1<=i<=k-2, 0<=j<i;
    V(2k,6-4k+3j),              0<=j<k-1.

At k=1 the table is the explicit four-tile set

    P_1={V(-1,1), V(0,0), V(1,-1), D(0,3)}.                         (9)

It is handled separately in the symbolic proof, so an expression with an outer
length k-2 is never interpreted as a negative number of terms.

Let B_(m,k) be (8) and the three actual embedded/rotated corner tables. For the
corner there are k(k-1) H bones, k^2 D bones and (5k^2+3k-2)/2 V bones. The
strip has km-(5k^2+k)/2 bones per sector. Thus

    |B_(m,k)|=3km+6k^2-3=|A_(m,k)|.                                (10)

Cardinality is not used by itself to claim coverage. The full coefficient
identity is proved next.

## 4. Exact identity with both parameters retained

For a finite original cell vector, the map [x,y]->X^x Y^y identifies its free
integer module with the Laurent polynomials of finite support. The inverse is
coefficient extraction on every original lattice cell. The four tile boundaries
are represented exactly by

    r=1+X+Y, h=1+X+X^2, v=1+Y+Y^2, d=1+XY^(-1)+X^2Y^(-2).

Work first in the integral domain

    Z[X^±1,Y^±1,Mx^±1,My^±1,Kx^±1,Ky^±1].                           (11)

The parameter specialization fixes X,Y and sends

    (Mx,My,Kx,Ky) -> (X^m,Y^m,X^k,Y^k).

Its kernel is the ideal generated by Mx-X^m, My-Y^m, Kx-X^k, Ky-Y^k. The
quotient isomorphism has inverse induced by the inclusion of X,Y; reducing the
four relations proves both inverse identities. No evaluation of X,Y at numbers
occurs in the proof.

A family with anchors

    x=x_m m+x_k k+x_i i+x_j j+x_0,
    y=y_m m+y_k k+y_i i+y_j j+y_0,
    0<=i<I, 0<=j<J_0+g i

has its exact cell polynomial obtained from the tile boundary, anchor monomial,
and the finite double sum. Put R=X^(x_i)Y^(y_i), S=X^(x_j)Y^(y_j). Its index factor
is

    [ Geo(R,I) - S^(J_0) Geo(R S^g,I) ]/(1-S),
    Geo(Z,N)=(1-Z^N)/(1-Z).                                         (12)

Equation (12) follows by summing 1+S+...+S^(J_0+gi-1) first, then summing in i.
All actual index lengths in the domain k>=2,m>=3k+2 are nonnegative. The powers
containing m or k remain the independent formal monomials in (11). Every
denominator contains X,Y only and is nonzero. Single-index families use Geo
directly. The separate k=1 calculation uses (9) and nonnegative index lengths.

### Shared exact family data

`families.json` is the single literal family table consumed by both the finite
constructor and the symbolic proof. An anchor row has coefficients
(m,k,i,j,constant), I has coefficients (m,k,constant), and J has coefficients
(m,k,constant,i). The exact affine expansions of the corner and strips in §3
are those rows. The six source blocks below exhibit the bijection with §2:

| Block | Depth ell | Original row y | Outer index | Inner index |
|---|---|---|---|---|
| A1 | i | i+1+j | 0<=i<k-1 | 0<=j<3k-i |
| A2 | i | 3k+1+j | 0<=i<k-1 | 0<=j<m-k-4 |
| A3 | i | m+2k-2+i+j | 0<=i<k-1 | 0<=j<2 |
| A4 | k-1 | k+i | 0<=i<2k+1 | one term |
| A5 | k-1 | 3k+1+i | 0<=i<m-2 | one term |
| A6 | k+i | k+i+1+j | 0<=i<k-1 | 0<=j<k-i |

In A1,A4,A6 one has y<=3k and the source x is y-m-1-3ell. In A2,A3,A5 one has
y>3k and x=y-m-2-3ell. Substitution gives the source anchors in `families.json`
term by term. Splitting the first row interval at 3k and applying the inverse
formulas i=ell or ell-k, j=y-(displayed initial row) recovers every source label
exactly once. This proves the table correspondence without extrapolating samples.

Rotation acts on cell polynomials by

    Rho(f)=Y f(Y^(-1),X Y^(-1)),

with the same linear exponent change on (Mx,My) and (Kx,Ky). Reflection is
Y f(XY^(-1),Y^(-1)). These are additive, invertible maps on the original cell
modules; the factor Y is applied once to a whole cell polynomial, not once per
factor. Denominators receive the linear exponent change without that affine
translation. This is precisely the original rho,F action, and explains the
module-versus-unital-algebra typing in the evaluator.

Let F_A,F_B be the original source and replacement cell polynomials, F_Del the
sum of the deleted stone boundaries, and F_M the missing cell indicator (7).
Applying (12) and the displayed affine actions to the finite family table gives

    F_B-F_A-F_Del+F_M=0.                                            (13)

Here is a finite, independently replayable exact certificate for (13). Multiply
by the product

    (1-Y^3)(1-XY^-2)(1-XY)(1-X^2Y^-4)(1-X^2Y^-1)
       (1-X^2Y^2)(1-X^3Y^-3)(1-X^3)(1-X^4Y^-2).                    (14)

The resulting numerator has every integer coefficient zero in all six
independent Laurent variables. `bivariate_certificate.py` expands the shared
families, forms (13), applies the stated affine maps, multiplies by (14), and
verifies coefficient cancellation exactly. The main calculation has 222 rational
terms and 28,128 expanded numerator terms before collection; no surviving
coefficient remains. At k=1, a separate 39-term identity has 510 expanded terms
and zero surviving coefficients. That calculation uses only m>=5.

When a denominator exponent is negative, the code applies the exact identity

    1/(1-X^-a Y^-b)=-X^a Y^b/(1-X^a Y^b).

Both sides are elements of the same explicitly localized ring. This retains its
monomial factor and sign. It is not a parameter substitution or discarded unit.

The localization of the integral domain (11) by the nonzero factors in (14) is
injective. Parameter specialization leaves those same nonzero X,Y factors, and
the target Laurent ring is also an integral domain. Thus the zero numerator
returns to the original finite cell identity, for every parameter in the domain:

    partial B_(m,k)+partial R_(m,k)
       =1_(Omega_Delta)+partial A_(m,k).                            (15)

One can inspect/replay (13) as finite integer arithmetic from the printed index
table; no optimization infeasibility status or finite range of m,k supplies its
proof. `verify.py` separately checks the family/index maps and original cells.

## 5. Positivity and the full original tiling

The source A_(m,k) is a matching inside the original Gamma by §2, and its cells
are disjoint from Omega by (1). Hence the right side of (15) is exactly the
all-ones vector of

    Lambda=Omega_Delta disjoint-union cells(A_(m,k)).

Every term on the left of (15) is an original placed tile with coefficient +1.
Equality of original coefficients forces every tile to stay inside Lambda,
forces every cell multiplicity to equal one, and excludes duplicate tiles and
overlaps. It therefore supplies the positive patch tiling, not just a signed
solution or cardinality equality.

Adjoin the frozen original bones Gamma minus A. The explicitly constructed full
tiling is

    (Gamma_Delta(d,h) minus A_(m,k)) union B_(m,k) union R_(m,k).       (16)

Equation (1) proves the frozen cells and patch cells are disjoint and exhaust
the original W_h(d). The counts follow from (5),(10) and |R|=Delta. Applying F
proves the reflected result. This completes the construction asserted in §1.

The construction is invariant under rho on the original placed tiles. Both
A and B are unions of three rotated sectors, and the deleted stones are full
rho-orbits. The parent Gamma and base T0 have the same property. Thus (16) gives
an actual rho-invariant positive tiling on this family.

## 6. Full integral comparison kernel and explicit cell duals

Use the actual free cell module C=Z[Lambda], old boundary image B_A=im(partial_A),
and new bone image B_B=im(partial_B). The original generator inclusion induces

    H_A=C/B_A -> H_(A+B)=C/(B_A+B_B).

The representative-preserving map gives the exact isomorphism

    B_B/(B_A intersect B_B) -> ker(H_A -> H_(A+B)).                   (17)

It sends the class of b to [b] in H_A. Its kernel is B_A intersect B_B. A kernel
representative decomposes as a+b, so b is an inverse preimage; changing that
decomposition changes b by precisely the intersection. This proves both inverse
maps, retaining the actual old boundaries. It is the original killed-class
comparison of Split-Zero D7, not a replacement by dimensions.

There is a complete integer basis construction for (17). Label old and new bones
as separate generators even when a placed shape occurs in both. Make the
bipartite graph with those vertices and each shared original cell as its edge.
Mark a vertex having a cell with no owner in the other matching. Call a component
closed when it contains no marked vertex.

An equality sum a_i partial A_i = sum b_j partial B_j implies a_i=b_j at every
shared cell and coefficient zero at a singly owned cell. Propagation gives zero
on each marked component and a single constant integer on each closed component.
Conversely each closed component gives the actual identity

    sum_(old vertices) partial A_i = sum_(new vertices) partial B_j.

These generators have disjoint vertex supports and are primitive. Hence they
are an integral basis of the intersection. Choose one new-bone pivot in every
closed component. If there are b new bones and c closed components, an explicit
basis of (17) consists of [partial B_j] for every nonpivot new bone, and

    K is isomorphic to Z^(b-c).                                    (18)

No claim that c vanishes for all parameters is needed or made. For a new-bone
coefficient vector, subtract its pivot coefficient on each closed component,
then keep the nonpivot coefficients. The inverse inserts zero at each pivot.
Their difference is exactly the printed intersection combination above.

The dual left inverse uses original cell cochains. Add a ground vertex for
singly owned cells, orient shared edges old->new, old-only edges old->ground,
and new-only edges ground->new. Root a spanning forest at ground in the open
part and at the selected new pivot in each closed component. For a nonpivot
new vertex, send one unit along the root-to-vertex forest path. Assign each
original cell edge +1 or -1 according to its orientation on that path and zero
otherwise. Vertex divergence is zero at every old vertex, +1 at the chosen new
vertex and -1 at a closed pivot (or ground). Thus its cell pairing annihilates
all old boundaries and is the Kronecker delta on the basis (18). This explicitly
constructs both integral coordinate maps and their duals; no numerical rank or
rational nullspace computation is used. `cohomology.MatchingKernel` implements
these original graph, path and cell maps, including intersection preimages.

The particular repaired class is

    z=1_(Omega_Delta)-partial R_(m,k)
      =partial(B_(m,k)-A_(m,k)).                                   (19)

The original cell p_m=(m-2,0) belongs to Omega (its rank is t_(m-2)+1<=Delta),
is covered by the deleted R(m-2,0), and is not covered by a retained stone. Every
old bone lies outside Omega. Coefficient evaluation at p_m therefore annihilates
B_A and sends z to 1. The map n->[nz] is a split injection of Z into H_A. Under
the actual comparison it becomes zero with the original boundary preimage (19).
This summand is retained together with the complete kernel (17), not used as a
substitute for the latter.

## 7. Actual Split-Zero supports, augmented cycles, and exterior maps

Let I index the actual old bones A_(m,k), and take

    L={bottom} disjoint-union P(I).

The bottom cell support is empty. The nonbottom empty-release label has cell
support Omega_Delta. For S subset I put

    Lambda_S=Omega_Delta union union_(i in S) cells(A_i).

The disjoint source partition makes S->Lambda_S a join-preserving injection,
with inverse reading the released old generators; bottom goes to the empty
cell set. Define original module complexes

    C_S^0=Z[all original contained bones], C_S^1=Z[Lambda_S], C_S^2=0,
    d^0=partial, d^1=0.

All transitions are original generator inclusions. Applying the pinned D1–D8
reconstruction gives Total^i=disjoint union_S C_S^i over G(Z)=Z disjoint-union{tau}.
For e=0_Z supported in G(Z), its operations are

    (S,x)+(T,y)=(S union T, jx+jy),
    r^bullet(S,x)=(S,rx),  e(S,x)=(S,0), tau(S,x)=(bottom,0).

The differential square is (S,x)->(S,0) in its actual target degree. Its label
projection retains S; the global absent zero has bottom label. At each support
the cycles and original boundaries give the internal quotient q(S,p)=(S,[p]).
It coequalizes the original incidence map and its supported-zero companion.
For a split-linear map f equalizing them, p-p' in the old boundary module gives

    f(S,p)=f(S,p')+f(S,p-p')=f(S,p')+f(S,0)=f(S,p').

The last equality is the image of fibre-zero absorption, so no cancellation in
an arbitrary target is assumed. This defines the unique descended split-linear
map; lifting original representatives verifies its scalar and addition laws.
The comparison (17) is natural for the same support transitions. Thus (19)
becomes its own supported zero, not tau. The nonempty support is retained.

Positive repairs have a genuinely linear augmented model. Let v_S=1_(Lambda_S)
and eta_ST=sum_(i in T minus S)[A_i]. The original partitions give

    v_T=jv_S+partial eta_ST,
    eta_SU=j eta_ST+eta_TU.

Use all original contained permitted tile generators, including R, and put

    Chat_S^0=Z direct-sum Z[contained permitted tiles],
    dhat_S(r,n)=partial n-r v_S,
    jhat_ST(r,n)=(r,jn+r eta_ST).                                   (20)

At bottom the entire module is zero. Direct expansion gives

    dhat_T jhat_ST=j dhat_S,    jhat_TU jhat_ST=jhat_SU.

Charge-one nonnegative integral cycles are exactly original positive patch
tilings: the cell sums are one. Inclusion into the signed integral cycle fibre
keeps the same charge, tiles and coefficients, with inverse on its image given
by those same coordinates. No vanishing class supplies positivity by itself;
(15) supplies the actual positive cycle at full release.

The exterior source-to-tail maps of §2 intertwine (20) on every original
generator. Adjoining frozen bones f_d=Gamma_Delta(d,h) minus A defines

    (r,n)->(r,n+r f_d).

Since partial f_d=1_(W_h)-v_I, this is the actual augmented cochain map to the
full benzel. At charge one it adjoins the original frozen tiling. Removing those
same frozen bones is inverse on the full tilings containing them. This does not
assert that every tiling of the full benzel contains the displayed frozen set.

## 8. Rotation, the integer norm, and the remaining two residues

The threefold symmetry of this construction is explicit. On original right-stone
anchors,

    rho R(x,y)=R(y,-x-y).

Equality with R(x,y) forces x=y=-x-y, hence x=y=0. Thus the central right stone
is the only fixed placed right stone; every other orbit has three distinct tiles.
For any rho-invariant original tiling, the right-stone count is therefore 0 or 1
modulo 3. This proves a specific obstruction for invariant Delta=2 modulo 3:
there is no rho-invariant positive tiling there. It does not prohibit asymmetric
positive tilings. The actual inclusion of fixed tilings into all tilings and the
original action rho give the comparison, rather than an assertion of unrelatedness.

On integer tile and cell modules retain the norm map N=1+rho+rho^2. It commutes
with partial term by term, and N^2=3N. No division by three is performed. On
support labels rho induces the actual join-preserving permutation of the old
bone orbits, and these cochain maps lift to G(Z) with e and tau retained.

For the still-unfinished q=3k+1 and q=3k+2 constructions, the following actual
bone-band homotopies were calculated. They are complete identities, not a general
positive completion theorem. In the original Laurent cell module, put
Z=XY for the first identity and Z=X^2/Y for the second:

    sum_(i=0)^(n-1) [partial H(x+i-1,y+i+1)-partial V(x+i,y+i)]
      = X^xY^y ((XY)^n-1)(1-X^-1Y),

    sum_(i=0)^(n-1) [partial D(x+2i,y-i+1)-partial H(x+2i,y-i)]
      = X^xY^y (1-(X^2/Y)^n)(Y-1).                                (21)

These follow by multiplying the literal three-cell polynomials and summing a
finite geometric progression. The endpoint cell vectors and every intermediate
placed bone are explicit, and changing the sign reverses the signed homotopy.
A two-strip version, relevant to the first remaining residue, is

    sum_(i=0)^(n-1) [partial D(x+i-2,y+i+2)+partial D(x+i-2,y+i+3)
                    -partial V(x+i,y+i)-partial V(x+i,y+i+3)]
     =X^xY^y (1-(XY)^n) C(X,Y),
    C=(XY^4+XY^3+XY^2+XY+Y^3+Y^2)/X^2.                           (22)

These identities transport endpoint obstructions between corners. Actual finite
supports and positive corner completions found in exploration are separately
recorded with their finite scope. A parameter-uniform positive endpoint formula
for the other two residues has not been completed in this contribution. Solver
statuses and zero jet values are not promoted to such a theorem.

## 9. Provenance, reproduction and acceptance boundary

The source input is the user's Split-Zero workbench, pinned at
`KokunoYumeto/zeta-function-research-reader@1c8ec52c85c173adc9f8403a8a26914955e2f5a9`,
`workbenches/splitzero-tandem/tex/support_diagrams.tex` D1–D8, and
`formal/splitzero/SplitZeroComplex.lean` (supported differential, cycle condition,
internal coequalizer). This note constructs its stated benzel diagrams, maps,
kernels and positive cycles; it does not claim to rebuild the original Lean
library or apply an unrelated analytic estimate. The preceding parent source
proof and code identities are preserved in `SOURCES.json`.

The original problem is Propp's Problem 7 in the trimer list. A bounded status
search did not establish a later complete resolution; it is not a complete
literature or novelty audit. The formerly known endpoint packing, base tiling,
and previously saved fixed-q controls retain their attribution and source history.

From this directory:

    python bivariate_certificate.py
    python verify.py --max-k 15 --output evidence/normal.json
    python -O verify.py --max-k 15 --output evidence/optimized.json

The symbolic proof checks both independent parameters before evaluation. The
finite replay separately checks positive cells, exterior source indices and their
inverses, independent region enumeration, integer matching-kernel coordinates,
cell-dual paths, supported scalar operations, augmented maps and deliberate bad
inputs. The stated execution receipts list exactly the completed parameter windows.
No independent specialist acceptance, priority determination, full P7 resolution,
or new Lean certificate is claimed. The remaining positive endpoint calculations
are research tasks, not premises advertised as finished results.
