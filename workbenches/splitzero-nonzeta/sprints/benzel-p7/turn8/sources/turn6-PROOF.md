# Turn 6 — stable residuals, positive transport, and infinite benzel families

15 September 2026. Written constructive research proofs, with exact replay and
finite certificates. Independent mathematical review and a Lean build have not
been performed. Priority of these constructions has not been established.
The full original Propp Problem 7 is not claimed resolved.

This continuation retains the original axial cells, the four original permitted
prototiles, integer incidence coefficients, every support, and the positive
filling fibre. An exact all-parameter argument is distinguished from its finite
replay by explicitly giving the argument; no experimental cutoff replaces a
quantifier. The finite core certificates in §7 produce infinite families through
the proved identity-on-generators transport, not by extrapolation.

## 1. Original objects and notation

A cell is (x,y) in Z². Its original differences are

    u=y-x,   v=1-x-2y,   w=2x+y-1.

They sum to zero. The benzel V(a,b) is the set where all three differences belong
to [1-a,b-1]. Throughout the principal lane,

    t_d=d(d-1)/2,  d>=3,  0<=h<=t_d,
    W_h(d)=V(d+3h,2d+3h),  Δ=t_d-h.

The inverse parameter map is d=b-a, h=(2a-b)/3. Its domain is retained: these
formulas concern this original integral lane, not every real pair (a,b).
The original right stone is

    R(x,y)={(x,y),(x+1,y),(x,y+1)}.

H(x,y), V(x,y), D(x,y) are the three bones with cell increments (1,0), (0,1),
(1,-1), respectively, each of length three. A placed tile generator maps under
∂ to the sum of its three original cell generators. A nonnegative integral
preimage of the all-ones region vector is a tiling: every cell sum is one, so
no tile multiplicity can exceed one and no overlap is possible. A tiling gives
the reverse preimage by its actual placed tiles.

Use the original bijections

    ρ(x,y)=(y,1-x-y),       F(x,y)=(x,1-x-y).

Their inverses are ρ² and F. On differences they give (v,w,u) and (-w,-v,-u).
Thus ρ preserves each original benzel and F exchanges V(a,b) with V(b,a).
On tile orientations ρ cycles H,V,D, and F interchanges H,D and fixes V.
Both preserve the original right-stone shape. All translations are literal
translations of the original integer cells.

For n>=1 let r(n) be the unique integer r>=1 satisfying

    t_r < n <= t_(r+1).

The interval for a fixed r has exactly r integers. The integer inverse is
implemented with isqrt and its defining inequalities are checked.

The original area identity is

    |W_h(d)|=3t_d+(9d-3)h+9h²=3Δ+9h(h+d).              (1)

For an explicit counting derivation, use

    Φ_d(r,s,p)=(d-2-2r-s,r-s)+e_p,
    e_0=(0,0), e_1=(1,0), e_2=(0,1).

For an original cell recover p as the representative 0,1,2 of
x+2y-(d-2) modulo 3. With e_p=(α,β), its inverse is

    r=(y-x+d-2-β+α)/3,
    s=(d-2-x-2y+α+2β)/3.

The phase choice proves integrality; substitution proves both inverse laws.
Set R=r+h,S=s+h and n=d+2h-1. All phases satisfy R,S>=0 and
R+S<=d+3h-2. The remaining bounds are

    phase 0: R<=n,   S<=n-1, R+S>=h-1;
    phase 1: R<=n,   S<=n,   R+S>=h;
    phase 2: R<=n-1, S<=n,   R+S>=h-1.

These follow by substituting Φ in the six original inequalities. In each
phase the big triangle loses three disjoint corner triangles. Its remaining
cardinality is C(d+3h,2)-2C(h,2)-C(h+1,2), equal to
 t_d+(3d-1)h+3h². Their sum proves (1). At h=0 all three domains coincide;
the three cells at each (r,s) are the original right stone. Hence

    T_0(d)={R(d-2-2r-s,r-s): r,s>=0,r+s<=d-2}          (2)

is a complete base tiling, with t_d stones.

## 2. A shifted positive packing on the entire two-parameter domain

Fix an integer shift 0<=s<=Δ. In the reflected benzel define a horizontal
sector E_s(d,h) by its bands. For 1<=y<=2h+d set

    L_y=1-2y-r(y+s), q_y=y                      (y<=h),
    L_y=y-3h-d+1,    q_y=min(h,2h+d-y)           (y>h).

The band consists of H(L_y+3j,y), 0<=j<q_y. Let Γ_s(d,h) be the images of
these actual placed bones under F, Fρ and Fρ². This specifies every tile,
not only a region whose tileability is asserted.

### 2.1 Containment

The reflected bounds are A=1-2d-3h and B=d+3h-1. For a prefix cell
x=1-2y-r+z, 0<=z<=3y-1, its differences are

    u=3y+r-1-z,  v=r-z,  w=1-3y-2r+2z.

Because y+s<=h+Δ=t_d, one has 1<=r<=d-1. Thus u ranges from r to
3y+r-1<=B; v ranges from r-3y+1>=A to r<=B; and w ranges from
1-3y-2r>=A to 3y-2r-1<=B. These are the original six bounds.

For a tail cell write y=h+ell, 1<=ell<=h+d, q=min(h,h+d-ell),
x=ell-2h-d+1+z, 0<=z<=3q-1. Then

    u=3h+d-1-z,
    v=d-3ell-z,
    w=3ell-3h-2d+1+2z.

The inequalities q<=h and ell+q<=h+d give A<=u,v,w<=B directly. In
particular u>=d. Empty bands have no cell to check.

### 2.2 Sector disjointness

Each sector cell has y>=1 and x<y: u>=r>=1 in a prefix and u>=d in a
tail. A cell in E_s intersect ρE_s would therefore satisfy 1<=x<y and
both (x,y) and (1-x-y,x) in E_s.

For prefix rows x,y, the lower endpoint constraints give

    y-x>=r(y+s),        y-x<=r(x+s).

Monotonicity forces equality r(x+s)=r(y+s)=r and y-x=r. But x+s and
y+s lie in the same r-element triangular block, whose maximum difference
is r-1. This is a contradiction.

For a tail row y and a prefix row x, those inequalities instead give
 y-x>=d and y-x<=r(x+s)<=d-1. For two tail rows, the lower endpoint
of row x gives 2x+y<=3h+d. The original row y gives y>=x+d; with
x>=h+1 this implies 2x+y>=3h+d+3. These cases exhaust 1<=x<y.
The other pairs of rotated sectors reduce to this pair by ρ. Reflection
preserves disjointness. Within one sector the bands have different y,
and within a band the original length-three intervals are disjoint.

### 2.3 Count and original incidence equation

One sector has

    sum_(y=1)^h y + sum_(ell=1)^(h+d) min(h,h+d-ell)
       = h(h+1)/2 + hd+h(h-1)/2 = h(h+d)

bones. Thus Γ_s has 3h(h+d) disjoint bones. By (1) its complement has
3Δ cells. The original integer incidence equation is

    ∂Γ_s + 1_(W_h\cells Γ_s)=1_(W_h).                 (3)

The known Kim–Propp zero-invariant construction is the endpoint of this
band scheme. That endpoint retains its source attribution. The argument
above proves the larger packing domain directly; it does not assume
positive completion of the complement.

## 3. The full residual has a parameter-independent inverse description

Take s=Δ. Define the locally finite infinite sector E_∞(Δ) by the bands

    H(1-2y-r(y+Δ)+3j,y), y>=1, 0<=j<y.

Let Σ_Δ=F(E_∞ union ρE_∞ union ρ²E_∞). Its finite prefix through row h
is literally the prefix of Γ_Δ(d,h); the tile generators have identical
coordinates, not merely equivalent counts.

### 3.1 Exact rank map on the original cell lattice

The three differences of an original cell are pairwise unequal: their
cyclic differences are all 2 modulo 3. Since they sum to zero, their
unique minimum is -k for an integer k>=1. Rotate to put that minimum
in coordinate u. The cell then has the unique form

    p_(k,m)=(k-m,-m),     0<=m<k.

Indeed v=1-k+3m and w=2k-3m-1 exceed -k exactly in that range. Thus

    (k,m,j) -> ρ^j p_(k,m),  j=0,1,2                 (4)

is a bijection. Its inverse uses the position of the unique minimum,
k=-min(u,v,w), and m=-y after that exact rotation. Put

    n(k,m)=t_k+m+1,
    Ω_Δ={ρ^j p_(k,m): n(k,m)<=Δ, j=0,1,2}.          (5)

Equation (4) proves |Ω_Δ|=3Δ. It also proves

    Ω_(t_k)=W_0(k),                                  (6)

including the empty k=1 case: the lower difference bounds retain exactly
the shells of minimum -1,...,-(k-1); the upper bounds follow from sum
zero. This supplies the original carrier bijection, not a picture-based
identification.

### 3.2 Which original cells the infinite bands cover

For the canonical p=p_(k,m), set B=k-m>=1 and a=1-2k+3m<=k-2. The
three possible pre-reflection coordinates are

    Fp=(B,B+a),   ρFp=(B+a,-m),   ρ²Fp=(-m,B).

The middle one has nonpositive second coordinate and is outside E_∞.
Membership of (-m,B) is exactly

    a<=r(B+Δ)<=k.                                    (7)

Membership of (B,B+a) is exactly a>=1 and

    r(B+a+Δ)<=a,

or equivalently B+Δ<=t_a. Its lower endpoint inequality is automatic
in that range. For a>=1, (7)'s lower inequality is B+Δ>t_a; its upper
inequality is B+Δ<=t_(k+1). For a<=0 the lower inequality is automatic
and the other possible point is absent. Since a<=k-2, these alternatives
are disjoint and exhaust exactly

    B+Δ<=t_(k+1),

which is Δ<=t_k+m=n(k,m)-1. Therefore an original cell has exactly
one Σ_Δ owner when its rank n exceeds Δ, and has no owner exactly
when it belongs to Ω_Δ. This proves both disjointness of the infinite
packing and its entire finite complement.

The code's stable_owner follows this inverse calculation and returns the
sector index, the original band row, the bone index, and the original
placed tile. All four are checked against its three cell generators.

### 3.3 The finite residual is exactly the same Ω_Δ

The prefix of Γ_Δ is a subset of Σ_Δ and avoids Ω_Δ. Also Ω_Δ is
contained in W_0(d), since Δ<=t_d. Reflection puts it in V(2d,d),
where every difference is <=d-1. A finite tail sector has u>=d;
its rotations and reflection therefore avoid Ω_Δ as well. Hence
Ω_Δ is disjoint from the entire finite packing and is inside W_h.
The complement has 3Δ cells by (3), exactly the cardinality of Ω_Δ.
Consequently

    ∂Γ_Δ(d,h)+1_(Ω_Δ)=1_(W_h(d))                    (8)

for all original integer d>=3 and 0<=h<=t_d. No positive completion
has been stipulated to obtain this identity.

## 4. Complete families at every triangular invariant

For d>=3 and 1<=k<=d put h=t_d-t_k. Equation (8) leaves precisely
Ω_(t_k)=W_0(k), and (2) tiles it by original right stones. Thus

    Γ_(t_k)(d,t_d-t_k) union T_0(k)                   (9)

is a complete positive type-103 tiling of V(d+3h,2d+3h). It has t_k
right stones and 3h(h+d) bones. The placement sets are disjoint by
§3, and both parts' original cell equations add to 1_W. Reflection
supplies the reflected pairs with an explicit inverse.

In particular k=2 proves the entire one-stone ray

    h=t_d-1,
    (a,b)=(d+3(t_d-1),2d+3(t_d-1)),  d>=3,          (10)

with its right stone exactly R(0,0). At k=1 this retains the known
zero-invariant bone tiling; at k=d it retains the original base tiling.
Neither endpoint is counted as a new discovery here.

## 5. The one-stone family is obtained by explicit positive chain homotopies

There is a direct relationship between (10) and the original unshifted
packing from turn 5. It explains the actual transport of the three
previously separated residual cells.

Set P_r=(t_(r+2),t_(r+1)) and Q_r=(1-r²,t_(r+1)). For
r=d-2,d-3,...,1, use the old horizontal band

    H(1-r²+3j,t_(r+1)), 0<=j<t_(r+1),

and replace it by

    H(2-r²+3j,t_(r+1)), 0<=j<t_(r+1).               (11)

The old union is the horizontal interval from Q_r to P_r-(1,0),
and the new union is from Q_r+(1,0) to P_r. Thus the signed tile
vector κ_r=new-old has the exact original boundary

    ∂κ_r=[P_r]-[Q_r].                               (12)

Also P_r=p_(r+2), Q_r=ρ²p_(r+1), where
 p_j=(t_j,t_j-j+1). Include all three rotations of (11).

These old bands are actual bones in Γ_0(d,t_d-1). In its defining
sector they are the rows y=t_(r+1), whose triangular block is r;
Fρ² maps the row to the displayed original horizontal interval.
Different r or sector uses disjoint old bones. Each simultaneous triple
of moves covers the three current holes and uncovers the three starts.
The process consequently changes the hole orbit of p_(r+2) to that
of p_(r+1). No original band awaiting use is changed by an earlier
move, because each new cell is a current hole and all such holes lie
outside those untouched original bones. At the end the hole set is

    orbit(p_2)={(1,0),(0,0),(0,1)}=R(0,0).

This is a proof of positivity at every step, not just a signed endpoint
equation. Each band move can also be performed bone by bone, from the
rightmost bone to the leftmost, shifting an original bone into the
adjacent hole and transferring the hole three cells to the left. Its
inverse shifts those same bones in reverse order.

The total number of moved original bones is

    3 sum_(r=1)^(d-2) t_(r+1)=3 C(d,3).             (13)

This is the cost of this specified construction, not a global minimum.
Since r(y+1) differs from r(y) precisely at these triangular rows,
the resulting bone set is exactly Γ_1(d,t_d-1), the k=2 construction
of §4, on the original placed generators.

### 5.1 Actual cochain maps and their homotopy

Let M=Z^3, concentrated in degree one, with basis e_j for j=0,1,2.
Let f_start(e_j)=[ρ^j p_d] and
 f_end(e_j)=[ρ^(j+2(d-2)) p_2]. For decreasing r choose the rotation
 j+2(d-2-r) of κ_r in the jth path. Let H(e_j) be its sum. Equations
(12) telescope to

    ∂H=f_start-f_end.                              (14)

Thus H is a displayed degree-minus-one cochain homotopy for the two
maps into the original bone/cell complex. Their equal induced classes
are represented by the original cells; summing (14) gives the positive
region-minus-stone equation after (11).

For a subset A of the three marked paths, let the target cell fibre be
the free module on all original cells used by those paths and their
endpoints. Let the degree-zero fibre be the free module on the original
old and new bones of those paths. Both sets are explicit finite unions.
All transitions for A⊂B are inclusions of these original generators;
H,f_start,f_end and ∂ commute with them. The source fibre is Z[A].
The empty-path label has the zero modules. Consequently (14) is an
identity on the entire join-indexed diagram, not only at its top fibre.

The pinned Split-Zero reconstruction makes the total carrier a disjoint
union of those fibres. Its supported scalar e sends (A,x) to (A,0),
and τ sends it to (empty,0). Addition uses the union of path labels
and the displayed inclusions. D1–D5 apply to these very modules and
maps. The internal quotient coequalizes the original incoming boundary
and its supported-zero companion. For the comparison of two supports,
D7 identifies killed original representatives modulo original boundaries
with the kernel of the induced homology map. Here (14) supplies the
particular representatives and boundaries, and (11) supplies their
positive realization. Neither is assumed from the other.

## 6. A second complete family: triangular invariant minus one

For m>=3 and d>=m put Δ=t_m-1 and h=t_d-t_m+1. The following original
core replacement is valid throughout this unbounded parameter domain.
At d=m use the previous complete first-collar tiling T_1(m) of W_1(m).
Its entire earlier proof is retained in sources/turn1-PROOF.md, §3.
For direct reproducibility the same actual constructor is printed here.
Translate T_0(m) by (-2,1), remove R(-2,3-m), and add

    D(-2,3-m), D(-2,4-m), D(-1,1-m), V(1,-m),
    H(-m-1+2r,m+1-r)      0<=r<m,
    H(r,3-m+r)           0<=r<m-1,
    V(r+2,r-m)           0<=r<m.

The retained source proof proves original containment, all pairwise
orientation intersections, the exact three-cell inner intersection, and
complete coverage for every m>=3. This dependency is a proved earlier
construction, not an unproved tileability premise.

For d>=m+1, one has h>=m+1. Let K=V(2m+3,m+3), the reflected core.
Any cell of K with y>=1 has y<=m+1: 3y=u-v+1<=3m+5. All outer
sector rows which can meet K are therefore prefix rows.

At y=1, r(y+Δ)=m-1 and the whole band has x=-m,...,2-m: one original
bone inside K. For 2<=y<=m+1, r(y+Δ)=m. The sector interval is

    1-2y-m <= x <= y-m.

Its intersection with K is exactly the last three cells

    y-m-2 <= x <= y-m.                              (15)

The lower endpoint follows from u<=m+2. At x=y-m-2,y-m-1,y-m,
substitution gives all six core bounds (their extrema occur at
2<=y<=m+1), so all three cells are present. They form one actual
bone of the sector, with index j=y-1 because
 1-2y-m+3(y-1)=y-m-2.

No bone crosses the core boundary: each of those rows has precisely
one last bone wholly inside, with all preceding bones outside. The
three sectors and F preserve K's original region. The finite tail
rows y>h>=m+1 miss it. Exactly 3(m+1) outer-source bones lie wholly
inside W_1(m). Their disjoint cells, together with Ω_Δ, exhaust it:

    |W_1(m)|=3(t_m-1)+9(m+1).

Hence the actual original bones of Γ_Δ(d,h) outside W_1(m) partition
its complement in W_h(d). Replacing the core by the explicit T_1(m)
produces the complete original tiling

    {b in Γ_Δ(d,h): cells(b) intersect W_1(m)=empty}
                       union T_1(m).               (16)

It contains Δ right stones and 3h(h+d) bones. This proves every
triangular-minus-one invariant ray (Δ=2,5,9,14,20,...) in full,
including all of their lowest admissible d.

## 7. Fixed original patch certificates give further infinite families

This section contains completed finite positive certificates and the
proved original-generator transport of those certificates. It does not
postulate a positive patch for arbitrary Δ.

For each actual recorded certificate choose its finite set A of Σ_Δ
bones. Every such bone has a unique stable owner label (sector,y,j).
Let Y=max y over A, and let D be the smallest integer d>=3 with
 t_d-Δ>=Y. At every d>=D, all those placed bones are literally in
the prefix of Γ_Δ(d,t_d-Δ). The support

    Λ=Ω_Δ union cells(A)

is therefore the same finite set of original integer cells for every
such d. The sets of *all* original placed R,H,V,D tiles contained in
Λ are identical. Consequently the two original incidence complexes at
any two parameters d,d'>=D are isomorphic by the identity on every
cell and every tile generator; the inverse is the same identity. This
preserves integer coefficients, nonnegative monoids, kernel, cokernel,
and each positive filling fibre exactly. The ambient inclusion maps
are the displayed original cell inclusions, and commute with incidence.

The release-subset versions use the join lattice P(A) with a separate
bottom for absence. Its empty release set still has support Ω_Δ. For
S⊂T⊂A, let η_ST be the sum of the newly released original bones.
The exact region vectors satisfy v_T=jv_S+∂η_ST. The augmented
complex and transitions are

    d_hat(r,n)=∂n-rv_S,
    j_hat_ST(r,n)=(r,jn+rη_ST).                     (17)

Expansion proves d_hat j_hat=j d_hat and composition follows from
η_SU=jη_ST+η_TU. These are genuine linear cochain maps. Charge-one
nonnegative integral cycles are the original positive patch tilings.
The pinned G(Z)-reconstruction retains (S,0) under supported zero and
sends τ to the external bottom. Internal homology uses the actual
incidence and supported-zero pair, with its original representative
kernel map. The identity-on-generators stabilization above preserves
this whole supported diagram, not merely the charge-one endpoint.

Each record in evidence/stable-patches.json prints Δ, Y, D, every
released original bone anchor and every replacement tile anchor.
verify.py independently expands these anchors, checks the stable owners,
checks distinct release bones, and checks

    ∂(replacement)=1_(Ω_Δ)+∂A.                     (18)

No optimizer is used by that acceptance step. Equations (8) and (18)
then give the explicit complete constructor

    (Γ_Δ(d,t_d-Δ) minus A) union replacement        (19)

for every integer d>=D in that record. All coefficients are +1,
the support intersection is exactly the released source cells, and the
positive inverse removes that same replacement and restores A on the
specified patch-containing fibres.

The remaining d<D are a finite, explicitly listed set for each record.
For every claimed completed invariant the file evidence/base-cases.json
contains each such original whole-region tiling. The verifier enumerates
**all** d=3,...,D-1 with t_d>=Δ and rejects a missing base case. It
checks every cell multiplicity and every original tile shape. The table
in COVERAGE.md is generated from these accepted certificates; only a row
with no missing d is marked COMPLETE_RAY. Larger-parameter certificates
for other records retain their exact threshold and missing lower cases.

Together with the completed triangular and triangular-minus-one families,
these literal records prove the completed invariant ranges stated in
COVERAGE.md. Their all-d quantifier follows from the exact transport
above and the exhaustive finite base-case list, not from an experimental
sequence matching initial values.

## 8. An exact obstruction to freezing the central stone at invariant two

The stable residual construction must allow the positive source fibre to
change; it cannot retain a central stone in every parameter case.
For W_1(3)=V(6,9), prescribe R(0,0) and remove its three cells. On the
39 remaining cells define y=2 at

    (-3,4),(-2,2),(-1,-1),(-1,0),(-1,3),(0,-3),
    (0,2),(1,-2),(2,-1),(2,1),(3,-1),(4,0),

and y=-1 at all remaining cells. Its region sum is 12*2-27=-3.
The exact verifier enumerates every contained original R,H,V,D tile
and checks its y-sum is nonnegative. Thus no nonnegative real tile
combination fills that punctured region: pairing ∂n=1 with y would
give -3=<∂*y,n>>=0. This concerns the image of the central-stone-
containing positive fibre under the explicit puncture map. It does not
exclude other right-stone placements. T_1(3), fully constructed in §6,
is a positive tiling with the required two stones and supplies the
opposite, whole-fibre witness. No solver nonexistence status is used.

## 9. Scope, source provenance and continuation

The earlier turn-5 work supplied a positive packing and finite dual-guided
repairs. This turn supplies an exactly ranked stable residual, the complete
one-stone transport, two unbounded families of invariant values, and finite
positive patches with proved all-parameter embedding maps. The parent
workbench sources are preserved. The original problem and the known
Kim–Propp endpoint retain their source attribution.

What remains outside these completed families is the positive completion
at general invariant Δ and, for a certificate with a high embedding
threshold, its explicitly listed lower parameter cases. The stable support
and full tile-incidence diagram now specify those objects exactly. No
unproved uniform positive section, external analytic estimate, or vanishing
of the entire comparison kernel is presented as a finished result.

The target is still the full original P7 existence statement. These
subfamily results are not a declaration of its resolution, and the role
of Split-Zero is identified by the actual supported complexes, original
cochain homotopy and positive fibres in §§5 and 7. The combinatorial
partition proofs and certificates supply the positive lifts; they have
not been inferred from a support label or an ordinary zero alone.
