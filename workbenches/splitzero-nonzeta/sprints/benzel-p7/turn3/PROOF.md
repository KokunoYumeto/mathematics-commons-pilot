# Fifth positive collar and the original three-polygon correspondence

Propp 7 focused attempt, turn 3. Recorded 15 September 2026.

## 0. Exact scope and input lineage

The new all-parameter result is a type-103 tiling of

    W_5(d)=V(d+15,2d+15), for every integer d>=4,

and its reflected region. There are binom(d,2)-5 right stones and 15d+75 bones. The proof uses 16 released source bones for all d>=4, including d=4. The earlier d=4 witness released 22; it is preserved, not called minimal or overwritten. In original parameters the new family is V(n,2n-15), n>=19, through d=n-15 and its inverse n=d+15.

The constructions of collars 1--4 in tables.json come from the earlier turn-1 and uploaded turn-2 sources. The previously supplied fourth-collar result is included with its complete indexed table and a fresh exact certificate replay. It is not counted as a new result of turn 3. The current GitHub head inspected was 038ed02bb524e60e9c2bd20c3a0aa02365f4001d. Its historical turn2 and TURN2.md are preserved. This continuation is additive; it does not silently replace either of those source generations.

The original P7 statement is Propp, https://arxiv.org/abs/2206.06472. The author page https://faculty.uml.edu/jpropp/benzels.html still labels P7 open, with an explicit June-2025 status horizon. The bounded search on this turn did not establish a later resolution. This is not an exhaustive novelty search. The original benzel coordinates and invariant convention are those used in https://arxiv.org/html/2209.05717v2. The support reconstruction input remains pinned to KokunoYumeto/zeta-function-research-reader@1c8ec52c85c173adc9f8403a8a26914955e2f5a9, workbenches/splitzero-tandem/tex/support_diagrams.tex, D1--D8.

The full P7 target remains unresolved by this work. No independent specialist review, Lean build, priority certification, or public resolution claim is asserted.

## 1. Original carriers and an explicit bijection

A cell is (x,y) in Z^2, with inverse barycentric map (x,y)->(x,y,1-x-y). Its three original differences are

    D0=y-x, D1=1-x-2y, D2=2x+y-1.

The original region V(a,b) is defined by 1-a<=D0,D1,D2<=b-1. Throughout,

    W_h(d)=V(d+3h,2d+3h), d>=3, h>=0.

The original tile types have offsets

    R: (0,0),(1,0),(0,1);
    D: (0,0),(1,-1),(2,-2);
    H: (0,0),(1,0),(2,0);
    V: (0,0),(0,1),(0,2).

No other trihex is included. Every anchor and tile phase is retained below.

Put e_0=(0,0), e_1=(1,0), e_2=(0,1). Define

    Phi_d(r,s,p)=(d-2-2r-s,r-s)+e_p,   p in {0,1,2}.

The inverse on an original cell is

    p = x+2y-(d-2) mod 3, chosen in {0,1,2};
    (alpha,beta)=e_p;
    r=(y-x+d-2-beta+alpha)/3;
    s=(1-x-2y+d-3+alpha+2beta)/3.

The choice of p makes both numerators divisible by 3: y-x is congruent to -(x+2y), and 1-x-2y is congruent to 1-(x+2y). Substitution of the inverse in Phi_d gives (x,y); substitution of Phi_d in the inverse gives r,s,p, since alpha+2beta=p. Thus these are inverse maps on the entire original cell lattice, not just on the chosen tilings.

Write R=r+h and S=s+h. Substitution in the six benzel inequalities gives the following exact three polygon domains:

| phase p | upper bound on R | upper bound on S | lower bound on R+S |
|---|---:|---:|---:|
| 0 | d+2h-1 | d+2h-2 | h-1 |
| 1 | d+2h-1 | d+2h-1 | h |
| 2 | d+2h-2 | d+2h-1 | h-1 |

All three also have R>=0, S>=0, and R+S<=d+3h-2. These are equalities of the transported integer domains. For example, D0=3r-d+2+beta-alpha and D1=3s-d+3-alpha-2beta give the R,S bounds with their displayed integer rounding; D2=2d-5-3(r+s)+2alpha+beta gives the sum bounds. Evaluating the three possible offsets gives exactly the table, so the inverse maps restrict to the region and these polygons in both directions.

### 1.1 Area and base tiling from the same bijection

Each polygon is the triangle R,S>=0, R+S<=d+3h-2 with three corner triangles removed. The removed sizes are two copies of binom(h,2) and one copy of binom(h+1,2), in the order specified by the table. The upper-R and upper-S cuts do not intersect: their least combined sum exceeds d+3h-2 for d>=3,h>=0. Neither can intersect the removed lower-sum triangle. For h=0 the three removed counts are zero and all cuts are empty. Therefore each phase has exactly

    binom(d+3h,2)-2 binom(h,2)-binom(h+1,2)
      = binom(d,2)+(3d-1)h+3h^2

cells. This proves directly, using the original cell bijection,

    |W_h(d)|=3 binom(d,2)+(9d-3)h+9h^2.       (1)

At h=0 all three polygons are exactly r,s>=0, r+s<=d-2. Grouping the three cells with the same (r,s) gives the original right stone R(d-2-2r-s,r-s). These stones form T0. Their disjointness and exhaustiveness follow from both inverse maps, proving the base tiling without a finite enumeration.

### 1.2 All original tile phases

For a tile of kind K anchored at Phi_d(r,s,p), transport every original cell by Phi_d^{-1}. Each entry (q,u,v) below denotes the original cell Phi_d(r+u,s+v,q).

| Kind | Anchor phase | Three transported cells (phase, delta-r, delta-s) |
|---|---:|---|
| R | 0 | `((0, 0, 0), (1, 0, 0), (2, 0, 0))` |
| R | 1 | `((1, 0, 0), (2, -1, 0), (0, 0, -1))` |
| R | 2 | `((2, 0, 0), (0, 0, -1), (1, 1, -1))` |
| D | 0 | `((0, 0, 0), (2, -1, 1), (1, -1, 1))` |
| D | 1 | `((1, 0, 0), (0, -1, 0), (2, -2, 1))` |
| D | 2 | `((2, 0, 0), (1, 0, 0), (0, -1, 0))` |
| H | 0 | `((0, 0, 0), (1, 0, 0), (2, -1, 0))` |
| H | 1 | `((1, 0, 0), (2, -1, 0), (0, -1, -1))` |
| H | 2 | `((2, 0, 0), (0, 0, -1), (1, 0, -1))` |
| V | 0 | `((0, 0, 0), (2, 0, 0), (1, 1, -1))` |
| V | 1 | `((1, 0, 0), (0, 0, -1), (2, 0, -1))` |
| V | 2 | `((2, 0, 0), (1, 1, -1), (0, 1, -2))` |

For an original offset (u,v), the output phase is q=p+u+2v mod 3. With (alpha,beta)=e_p and (gamma,delta)=e_q, the inverse change of indices is

    delta-r=(beta+v-delta-alpha-u+gamma)/3,
    delta-s=(-alpha-u+gamma-2(beta+v-delta))/3.

These integers give every entry of the table. Applying Phi_d back returns each original offset, proving the table and its inverse on generators. In particular all nine bone phases and all three right-stone phases are retained; no phase restriction is asserted for arbitrary tilings.

The induced bijections on placed-tile generators and cell generators extend to inverse homomorphisms on their free nonnegative monoids, and on their free integer modules. Summing the three displayed cell images proves the incidence square commutes. The fibre of the positive incidence map over the original region vector is therefore mapped bijectively to the fibre over these three exact polygons. The inverse is the original tile map, not just an equality of counts.

For finite supports lambda, send lambda to Phi_d^{-1}(lambda). This preserves empty support and union and has the inverse Phi_d. The preceding linear maps commute with inclusions on these supports. Consequently they give the corresponding maps on the support-indexed complexes and, via the pinned reconstruction, their Split-Zero totals. Supported zero at lambda is sent to supported zero at its displayed image support. The same maps induce the homology/quotient comparisons because they carry the actual incidence boundaries to the actual incidence boundaries. This is the exact support and coefficient transport used here.

The d-direction also has an exact commuting identity:

    Phi_(d+1)(r,s,p)=Phi_d(r,s,p)+(1,0).

It identifies the particular translated narrow-shell inclusion tested during exploration. The three polygon equations do not supply a positive tiling of that shell; the saved failures concern that specific frozen-source inclusion, not other maps.

## 2. Original source tilings for the fifth collar

Each stage j uses the translation and released original tiles specified in tables.json, then inserts its listed positive bone families. In that file a family [name,kind,X,Y,U] means the anchor

    (X0*d+X1*r+X2, Y0*d+Y1*r+Y2), 0<=r<=U0*d+U1.

Singleton families have U=(0,0). This convention is a literal evaluation map, with the named source generator and r retained. The tables below include the complete preceding construction. Each released tile is matched with an actual original generator and checked against every intervening removal by source_membership in certify.py. The algorithm solves the displayed affine anchor equalities exactly; it never chooses a representative by finite sampling.

For the fifth collar translate T4 by t5=(1,1). Its original difference increments are (0,-3,3), so the translated inner bounds are

    D0 in [-d-11,2d+11],
    D1 in [-d-14,2d+8],
    D2 in [-d-8,2d+14].                         (2)

The outer W5 bounds are [-d-14,2d+14], proving inclusion of the actual translated source. Release S5=R(3-d,d-1) and these 16 bones:

| Original kind | Anchor | Original preimage (before its later translations) |
|---|---|---|
| R | `(-d+3,d-1)` | base q(d-3,0) |
| D | `(-d-6,d+5)` | stage 3 A_0 |
| D | `(-d-5,d+3)` | stage 3 A_1 |
| D | `(-d-5,d+5)` | stage 3 B |
| D | `(-d-5,d+6)` | stage 3 C |
| D | `(-d-4,d+6)` | stage 3 E |
| D | `(-d-3,d+6)` | stage 3 F |
| D | `(-d-2,d)` | stage 2 A |
| D | `(-d-2,d+1)` | stage 2 B |
| D | `(-d-1,d+5)` | stage 3 G_0 |
| D | `(-d+1,d+4)` | stage 3 G_1 |
| H | `(-d-3,d+2)` | stage 2 E |
| H | `(-d-1,d+1)` | stage 2 G |
| H | `(-d,d)` | stage 2 H |
| H | `(-d,d+2)` | stage 1 F_0 |
| H | `(-d+2,d+1)` | stage 1 F_1 |
| V | `(-d+1,d-3)` | stage 2 K_0 |

The base indices (d-3,0) lie in the original triangle for all d>=4 and differ from all four previously consumed pairs. The stage-3 preimages have subsequent total translation (-1,2); the stage-2 preimages have total translation zero; the stage-1 preimages have total translation (1,1). Applying those shifts to their printed anchors gives the table above. All constant indices 0,1 are within the corresponding ranges. None equals an earlier removed tile for any integer d>=4. The exact affine inverse witnesses and the exclusion calculations are emitted in all-parameter-summary.json, including d=4; no exceptional source assumption is used.

## 3. The fifth replacement, for all d>=4

Insert the following bones. The column `inside offsets` uses the bone's original offset u=0,1,2 and the inner bounds (2). A blank entry means that all three cells are outside the translated source.

| Label | Kind | Anchor | r range | Inside offsets |
|---|---|---|---|---|
| D0 | D | `(-d+r-8,d-2r+3)` | `0..d+3` | `[]` |
| D1 | D | `(-d-8,d+4)` | singleton | `[]` |
| D2 | D | `(-d-4,d+2)` | singleton | `[0, 1, 2]` |
| D3 | D | `(-d-3,d+2)` | singleton | `[0, 1, 2]` |
| D4 | D | `(-d-3,d+3)` | singleton | `[0, 1, 2]` |
| D5 | D | `(-d-1,d-1)` | singleton | `[0, 1, 2]` |
| D6 | D | `(-d+1,d+1)` | singleton | `[0, 1, 2]` |
| D7 | D | `(-d+1,d+3)` | singleton | `[0, 1, 2]` |
| D8 | D | `(-d+2,d+1)` | singleton | `[0, 1, 2]` |
| D9 | D | `(-d+2,d+3)` | singleton | `[0, 1, 2]` |
| H0 | H | `(-d-9,d+5)` | singleton | `[]` |
| H1 | H | `(-d-8,d+6)` | singleton | `[]` |
| H2 | H | `(-d-7,d+4)` | singleton | `[2]` |
| H3 | H | `(-d-7,d+7)` | singleton | `[]` |
| H4 | H | `(-d-6,d+3)` | singleton | `[1, 2]` |
| H5 | H | `(-d-6,d+5)` | singleton | `[0, 1, 2]` |
| H6 | H | `(-d-6,d+8)` | singleton | `[]` |
| H7 | H | `(-d-5,d+6)` | singleton | `[0, 1, 2]` |
| H8 | H | `(-d-5,d+9)` | singleton | `[]` |
| H9 | H | `(-d-4,d+4)` | singleton | `[0, 1, 2]` |
| H10 | H | `(-d-3,d+5)` | singleton | `[0, 1, 2]` |
| H11 | H | `(-d-1,d+2)` | singleton | `[0, 1, 2]` |
| H12 | H | `(-d-1,d+4)` | singleton | `[0, 1, 2]` |
| V0 | V | `(-d+r-5,d-2r)` | `0..d+2` | `[]` |
| V1 | V | `(-d,d-1)` | singleton | `[0, 1, 2]` |
| V2 | V | `(-d+1,d-2)` | singleton | `[0, 1, 2]` |
| V3 | V | `(-2,-d-5)` | singleton | `[]` |
| V4 | V | `(-1,-d-6)` | singleton | `[]` |
| V5 | V | `(0,-d-6)` | singleton | `[]` |
| V6 | V | `(1,-d-7)` | singleton | `[]` |
| V7 | V | `(2,-d-7)` | singleton | `[]` |
| V8 | V | `(3,-d-8)` | singleton | `[]` |
| V9 | V | `(4,-d-8)` | singleton | `[]` |
| V10 | V | `(r+5,-d+r-9)` | `0..d+4` | `[]` |

### 3.1 Containment and exact intersection

Substitute every anchor plus its three original offsets into D0,D1,D2. Each bound is affine in d and r. For an expression Ad+Br+C on 0<=r<=ud+v, its minimum in r is attained at r=0 for B>=0 and at r=ud+v for B<0. This produces an affine expression ad+c. Its nonnegativity for d>=4 follows from a>=0 and 4a+c>=0. The exact verifier applies these comparisons to all 612 outer one-sided inequalities.

For every offset marked inside, the same calculation proves all six inequalities in (2). For every offset marked outside, the verifier supplies one fixed coordinate inequality violating (2) by at least one, valid on the complete parameter range. There is no unresolved cutoff or omitted residue class. The 51 inside cells are compared as a multiset of affine coordinate pairs in d with the cells of the 17 released tiles. They agree identically.

For example, D0_r lies wholly outside the inner D0 or D2 bounds as certified by those literal expressions, while H2 has only offset 2 inside and H4 has offsets 1,2 inside. The general verifier, not this illustrative sentence, prints the exact offset table above. The right stone and all 16 source bones are retained in the 51-cell identity.

### 3.2 Every collision is ruled out on the unbounded domain

Cells from a single indexed family have injective (r,u) coordinates: its anchor step and original bone direction have nonzero determinant. Singleton bones have three distinct cells.

For two different families and offsets u,v, introduce real variables (d,r,s). Include d>=4, both exact index ranges, and the two coordinate equalities. Encode the latter as pairs of opposite inequalities. There are exactly nine inequalities in each system and 5,049 such systems for the 34 fifth-collar families.

The file all-parameter-certificates.json, regenerated by certify.py, gives a nonnegative rational combination of each system whose left side is zero and whose right side is strictly negative. The acceptance function recomputes the nine constraints from the original table and checks every coefficient sum using exact fractions. Thus a simultaneous collision would give 0<0. This rules it out for all real solutions of those bounds, hence for the original integer indices. The finite d replay is not used for this conclusion.

The generator affine.py uses exact elimination to discover the combinations. The acceptance arithmetic does not rely on a solver status, a tolerance, or agreement among models. Every family pair and all nine pairs of offsets are enumerated directly, so there is no unlisted collision system. Earlier collars are checked by the identical argument on their own domains; the complete numbers are given in section 6.

### 3.3 The positive partition and tiling

The replacement contains (d+13) diagonal bones, 13 horizontal bones and (2d+17) vertical bones, totalling 3d+43. Its disjoint cells therefore number 9d+129. Formula (1) gives

    |W5|-|W4|=9d+78.

The source intersection contains exactly 51 cells. Containment, disjointness, exact source intersection and cardinality prove

    covered(C5)=(W5 \ ((1,1)+W4)) disjoint-union covered(S5+eta5),

where eta5 is the sum of the 16 original released bone generators. Hence

    T5=(((1,1)+T4) \ {S5 and the 16 released bones}) union C5

is an original type-103 tiling for every integer d>=4. Its incidence identity in the free integer cell module is

    partial beta5 = 1_W5 - J5 1_W4 + partial S5 + partial eta5.       (3)

Every coefficient of beta5 is +1. T4 has binom(d,2)-4 right stones and 12d+48 bones; deleting one stone and 16 bones, then adding 3d+43 bones, gives the announced counts. This proves the fifth-family result.

The involution (x,y)->(x,1-x-y) sends (D0,D1,D2) to (-D2,-D1,-D0), hence sends V(a,b) onto V(b,a). It preserves right stones, interchanges H and D bones and reverses the V direction; re-anchoring the reversed bone at its original opposite endpoint gives the printed positive orientation. Applying the involution twice is the identity. This proves the reflected family and its inverse tile transport.

## 4. The exact positive-fibre bijection and cohomology relation

Let A5 be the set of 17 released tiles in the translated source and B5 the 3d+43 replacement bones. Let U be the set of all original W4 tilings whose translates contain A5. Let V be the set of all original W5 tilings containing B5. Both sets have literal definitions on the original tiling carrier.

Define

    F(T)=(J5 T \ A5) union B5,
    F^{-1}(T')=J5^{-1}((T' \ B5) union A5).

The partition identity in section 3 proves both functions are defined. The remaining cells of a target tiling containing B5 are precisely J5(W4) minus the released cells, so every remaining tile lies entirely in J5(W4). Removing B5, reinserting A5 and translating back therefore gives an original source tiling. Both compositions remove and restore the same disjoint tile sets and equal the identity. T4 supplies a member of U. This proves an actual bijection of the specified positive tiling fibres, not an assertion that F covers all W5 tilings.

On tile vectors F is the affine map J5 c-A5+B5. Differences satisfy

    F(c)-F(c')=J5(c-c').

The linear cochain map is J5, with partial J5=J5 partial on each original generator. Equation (3) specifies the fixed affine correction. Thus the affine positive-fibre map and the linear cochain map are related by these exact formulas; neither is substituted for the other.

In the finite-support bone quotient of W5, the original representative map gives

    [1_W5]-J5[1_W4]=-[S5],

since beta5 and eta5 are bone boundaries. The earlier integral global quotient Q and its finite-jet observation receive this equality through the cell inclusions. The source stone has the retained order-three global class, and the correction is realized inside the specified support by the positive partition. The observation is used together with the original representatives and their support; no vanishing scalar observation is treated as a positive source section.

The same formula applies on the support-indexed complexes under the pinned Split-Zero reconstruction: inclusion of supports and translation act on the original generators, and quotient maps take a boundary to its support-labelled zero. The positive fibre map is the displayed affine correction inside those same cell modules.

## 5. What was additionally checked, and what remains next

Five sixth-collar positive certificates are saved for d=4,5,6,7,8. Each names the actual translated T5 source, its removed stone and old bones, and every new bone. The constructors for h<=5 contain no search. The h=6 data are bounded integer certificates, not an all-parameter sixth-collar formula. Solver optimality is not used or claimed. The d=4,h=6 certificate reaches the known zero-invariant endpoint for that fixed d.

Three bone-only annuli are also saved, for source (d,h)=(3,0),(3,1),(4,0), using the literal zero translation into W_(h+d)(d+1). The direct calculation

    binom(d+1,2)-(h+d)=binom(d,2)-h

preserves the stone-count invariant, and (1) gives annulus area 9(2d+1)(d+h). Every saved annulus is checked as a positive bone partition of exactly the original set difference. A uniform annulus formula has not been proved. Timed searches on larger cases are recorded as uncompleted searches, not infeasibility results.

The three-polygon and all-phase tile maps in section 1 provide a concrete next calculation in both parameters. The next work is to construct a parameter-uniform positive lift through the remaining h values, using the actual transported incidence map, and to return that lift by Phi_d. The exact sixth-collar and constant-charge annuli are starting configurations. This is a continuation task, not a stated conditional theorem or a completed full P7 argument.

## 6. Replay and all-parameter source closure

Run `python check.py --max-d 100 --output evidence/normal.json` and the corresponding `python -O check.py --max-d 100 --output evidence/optimized.json`. Both modes execute the exact all-parameter certificates, original source membership calculations, finite tilings and reflection checks, positive forward/inverse fibre maps, polygon inverse and tile-map tests, saved finite certificates and rejection tests.

The five stages have 189, 495, 702, 2484 and 5049 collision contradictions, respectively. The stage-3 construction holds for d>=3; stages 4 and 5 hold for d>=4. All source membership and range checks use these unbounded domains.

### Complete prior-stage tables

For each family below the anchor is (X0*d+X1*r+X2, Y0*d+Y1*r+Y2), 0<=r<=U0*d+U1. These are the unchanged mathematical anchors from the preceding constructions. The explicit base tiling in section 1 and these tables supply the entire mathematical source used by the fifth constructor.

#### Stage 1: d>=3, translation (-2, 1)

Released original generators:

    R(-2, -d+3)

| Family | Kind | X | Y | U |
|---|---|---|---|---|
| A | D | `[0, 0, -2]` | `[-1, 0, 3]` | `[0, 0]` |
| B | D | `[0, 0, -2]` | `[-1, 0, 4]` | `[0, 0]` |
| C | D | `[0, 0, -1]` | `[-1, 0, 1]` | `[0, 0]` |
| F | H | `[-1, 2, -1]` | `[1, -1, 1]` | `[1, -1]` |
| G | H | `[0, 1, 0]` | `[-1, 1, 3]` | `[1, -2]` |
| E | V | `[0, 0, 1]` | `[-1, 0, 0]` | `[0, 0]` |
| J | V | `[0, 1, 2]` | `[-1, 1, 0]` | `[1, -1]` |

#### Stage 2: d>=3, translation (1, 1)

Released original generators:

    R(-d+1, d)

| Family | Kind | X | Y | U |
|---|---|---|---|---|
| A | D | `[-1, 0, -2]` | `[1, 0, 0]` | `[0, 0]` |
| B | D | `[-1, 0, -2]` | `[1, 0, 1]` | `[0, 0]` |
| R | D | `[-1, 1, -1]` | `[1, -2, -2]` | `[1, -1]` |
| E | H | `[-1, 0, -3]` | `[1, 0, 2]` | `[0, 0]` |
| F | H | `[-1, 0, -2]` | `[1, 0, 3]` | `[0, 0]` |
| G | H | `[-1, 0, -1]` | `[1, 0, 1]` | `[0, 0]` |
| H | H | `[-1, 0, 0]` | `[1, 0, 0]` | `[0, 0]` |
| K | V | `[-1, 1, 1]` | `[1, -2, -3]` | `[1, -1]` |
| L | V | `[0, 0, 1]` | `[-1, 0, -2]` | `[0, 0]` |
| M | V | `[0, 0, 2]` | `[-1, 0, -3]` | `[0, 0]` |
| N | V | `[0, 1, 3]` | `[-1, 1, -2]` | `[1, 0]` |

#### Stage 3: d>=3, translation (1, -2)

Released original generators:

    R(d-2, 0)
    H(d-1, 1)
    H(d, 0)

| Family | Kind | X | Y | U |
|---|---|---|---|---|
| A | D | `[-1, 1, -5]` | `[1, -2, 3]` | `[1, 2]` |
| B | D | `[-1, 0, -4]` | `[1, 0, 3]` | `[0, 0]` |
| C | D | `[-1, 0, -4]` | `[1, 0, 4]` | `[0, 0]` |
| E | D | `[-1, 0, -3]` | `[1, 0, 4]` | `[0, 0]` |
| F | D | `[-1, 0, -2]` | `[1, 0, 4]` | `[0, 0]` |
| G | D | `[-1, 2, 0]` | `[1, -1, 3]` | `[1, -1]` |
| J | H | `[-1, 2, -3]` | `[1, -1, 5]` | `[1, 1]` |
| K | H | `[1, 0, 0]` | `[0, 0, 3]` | `[0, 0]` |
| L | H | `[1, 0, -2]` | `[0, 0, 0]` | `[0, 0]` |
| M | H | `[1, 0, -2]` | `[0, 0, 1]` | `[0, 0]` |
| P | V | `[1, 0, 1]` | `[0, 0, 0]` | `[0, 0]` |
| Q | V | `[1, 0, 2]` | `[0, 0, 0]` | `[0, 0]` |
| N | V | `[1, 1, 3]` | `[0, -2, 1]` | `[0, 2]` |

#### Stage 4: d>=4, translation (-2, 1)

Released original generators:

    R(-1, -d+4)
    D(-1, -d+1)
    H(0, -d+3)
    V(-1, -d-2)
    V(0, -d-3)
    V(1, -d-4)
    V(1, -d)
    V(2, -d-3)
    V(2, -d)

| Family | Kind | X | Y | U |
|---|---|---|---|---|
| A | D | `[0, 0, -4]` | `[-1, 0, -2]` | `[0, 0]` |
| B | D | `[0, 0, -2]` | `[-1, 0, -3]` | `[0, 0]` |
| C | D | `[0, 0, -1]` | `[-1, 0, -2]` | `[0, 0]` |
| D | D | `[0, 0, -1]` | `[-1, 0, 4]` | `[0, 0]` |
| E | D | `[0, 0, -1]` | `[-1, 0, 5]` | `[0, 0]` |
| F | D | `[0, 0, 0]` | `[-1, 0, -4]` | `[0, 0]` |
| G | D | `[0, 0, 1]` | `[-1, 0, -3]` | `[0, 0]` |
| H | D | `[0, 0, 1]` | `[-1, 0, -2]` | `[0, 0]` |
| I | D | `[0, 0, 2]` | `[-1, 0, -5]` | `[0, 0]` |
| J | H | `[-1, 2, -4]` | `[1, -1, 7]` | `[1, 2]` |
| K | H | `[0, 1, 3]` | `[-1, 1, -3]` | `[1, 1]` |
| L | H | `[1, 0, 2]` | `[0, 0, 3]` | `[0, 0]` |
| M | H | `[1, 0, 2]` | `[0, 0, 4]` | `[0, 0]` |
| N | H | `[1, 0, 3]` | `[0, 0, 1]` | `[0, 0]` |
| O | H | `[1, 0, 3]` | `[0, 0, 2]` | `[0, 0]` |
| P | H | `[1, 0, 4]` | `[0, 0, -1]` | `[0, 0]` |
| Q | H | `[1, 0, 4]` | `[0, 0, 0]` | `[0, 0]` |
| R | V | `[0, 0, -1]` | `[-1, 0, -1]` | `[0, 0]` |
| S | V | `[0, 0, 0]` | `[-1, 0, -2]` | `[0, 0]` |
| T | V | `[0, 0, 1]` | `[-1, 0, -1]` | `[0, 0]` |
| U | V | `[0, 0, 2]` | `[-1, 0, -2]` | `[0, 0]` |
| V | V | `[0, 0, 2]` | `[-1, 0, 1]` | `[0, 0]` |
| W | V | `[0, 0, 4]` | `[-1, 0, -6]` | `[0, 0]` |
| Z | V | `[0, 1, 5]` | `[-1, 1, -6]` | `[1, 2]` |
