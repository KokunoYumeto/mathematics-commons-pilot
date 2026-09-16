# Source-bound mathematical continuation

14 September 2026. These are written derivations and reproduced results, with exact finite certificates. No new full resolution of P7, P15–P19, Green 92 or AIM's coefficient-characterization question is asserted. Published results used below retain their attribution. Independent specialist review and upstream Lean reconstruction have not been performed.

## 1. Original benzel carriers and coefficient convention

The cell carrier is the integer triples v=(i,j,k) of sum one with all three differences j-i, k-j, i-k in [1-a,b-1], on the original domain a,b>=2, a<=2b, b<=2a. Write e1,e2,e3 for the standard basis. Right stones are u+{e1,e2,e3}, with sum(u)=0; left stones are u-{e1,e2,e3}, with sum(u)=2. Bones are {v-d,v,v+d} for d=e1-e2, e1-e3, e2-e3. These are Propp's five translated prototiles, not the excluded bent trihex.

The map to axial coordinates is (i,j,k)->(i,j), with inverse (i,j)->(i,j,1-i-j). It transforms the region differences into j-i, 1-i-2j, 2i+j-1. For a left stone with base u, translate axial coordinates by -(u_i-1,u_j); its offsets are {(0,0),(1,0),(1,-1)}. A right stone has offsets {(0,0),(1,0),(0,1)} after translating by -(u_i,u_j). Bones give straight triples in directions (1,-1),(1,0),(0,1). This supplies both inverse carrier maps and the explicit tile transport, including the literal carrier used in the P4 formalization.

Let R(T), L(T), B(T) count the right stones, left stones and bones of an actual tiling. Use the stone-count invariant Delta=R(T)-L(T). Propp's area-unit invariant C and this value satisfy C=3 Delta: each stone consists of three cells. With s=(a+b) mod 3, the published formula is

    6 Delta = 3(a-b)^2-a-b                         (s=0)
            = -a^2+4ab-b^2-a-b+2                  (s=1)
            = 3(a-b)^2+a+b-2                      (s=2).

The distinction of units is fixed by that multiplication map, not silently discarded. Source: Defant–Li–Propp–Young, arXiv:2209.05717v2, introduction and Theorem 1.1; Propp's problem paper, Section 1.

## 2. An explicit construction reproducing the resolved P14 family

For every original admissible (a,b) with a+b=1 mod 3, there is exactly one stones-and-bones tiling. This is the published DLPY Theorem 1.1. The following direct residue construction supplies another fully specified route to the same known endpoint.

Put A=1-a, B=b-1, and r=2-a mod 3. For each cell v, consider the three possible anchors u=v-e_j of right stones containing v. Their first differences u_j-u_i occupy the three different residue classes modulo 3. Choose the unique anchor whose first difference is r.

All differences of a sum-zero anchor are congruent: (u_k-u_j)-(u_j-u_i)=-3u_j. The three differences of the chosen anchor lie in [A-1,B+1], since the differences of v lie in [A,B]. The endpoints A+1=2-a and B-1=b-2 are both congruent to r. None of A-1,A,B,B+1 has that residue. Consequently every anchor difference belongs to [A+1,B-1]. Across its right stone, each of the three differences takes the three values delta(u)-1,delta(u),delta(u)+1. The entire chosen stone therefore lies in the original benzel.

Every cell in this stone selects the same anchor: that anchor has residue r and the selection is unique. Thus the stones partition the cell carrier. More explicitly, for the selected anchor set U, the map

    U x {1,2,3} -> V,  (u,j) -> u+e_j

is bijective, with inverse obtained by the cell's unique selected anchor and its offset index. This proves exhaustiveness and disjointness, not only containment.

For uniqueness of a right-stone tiling of any finite region, choose a cell of maximal first coordinate. In any right stone containing it, this cell must be the e1-offset; the e2- or e3-offset would put another cell one unit farther in the first coordinate. Its tile is therefore forced. Removing that tile and repeating proves uniqueness by induction on the number of cells.

Finally the published invariant and cell-area formulas give |V|=3 Delta in this residue family. In any stones-and-bones tiling,

    |V|/3 = R+L+B = Delta = R-L,

so 2L+B=0. Nonnegative integer tile counts force L=B=0. The partition constructed above is consequently the unique tiling using all five original prototiles. No extra symmetry or selected tiling family was imposed.

The checker verifies the partition directly for all 150 ordered admissible pairs with 2<=a,b<=30 and a+b=1 mod 3. This computation accompanies the all-parameter proof; it is not its replacement. The old author's-page open label is retained in provenance but no longer controls the workbench's P14 routing.

## 3. Exact residual scope for P7

Retain the original request for a type-103 tiling whenever Delta>=0. The involution (i,j,k)->(i,k,j) negates and permutes the three difference coordinates, so it transports the (a,b) carrier to (b,a). It preserves the right/left stone sets and permutes bone directions. It is its own inverse. We can therefore work on a<=b with this specific reflection available to return every construction.

The s=1 family is covered by Section 2. For s=2, generalized compression Theorem 1.1 gives a positive product counting the original right-stone/two-bone tilings, with

    n=b+1-a, k=(2a-b-1)/3,
    (a,b)=(n+3k,2n+3k-1).

Both coordinate transformations are inverse; k>=0 on this residue family. Each tiling counted there is also a type-103 tiling under the literal inclusion of the permitted tile sets. No change to its placed cells occurs. This disposes of that P7 subfamily using a published result, without asserting a bijection with the larger tiling set.

For s=0 define d=b-a and h=(2a-b)/3. The inverse is

    a=d+3h, b=2d+3h, Delta=binom(d,2)-h.

Substitution proves all three identities. Nonnegative invariant gives 0<=h<=binom(d,2). At h=0 the original boundary benzel is the same cell set as (a,2a-2), already covered by the unique-right-stone family. To check that cell equality directly, the largest difference of a cell bounded below by 1-a is at most 2a-2 because the three differences sum to zero. Equality 2a-2 forces the other two to be 1-a, whose reconstruction has a coordinate with denominator three; thus that value is unattainable for a sum-one integer cell. The actual upper bound is 2a-3, exactly the (a,2a-2) bound. At h=binom(d,2), the parameters are d(3d-1)/2,d(3d+1)/2, the bone-only family of Kim–Propp (arXiv:2206.04223).

The remaining new-construction scope after these published subfamilies is therefore

    d>=3, 1<=h<=binom(d,2)-1,
    (a,b)=(d+3h,2d+3h).

The h=1 part is also the P6 claim family: n=d+3 gives (a,b)=(n,2n-3). It remains claim-audit material here rather than being removed on a claimed Lean status alone. The checker supplies witnesses for all 38 unordered admissible nonnegative-invariant pairs with 2<=a<=b<=12. That finite window includes boundary and interior cases and is not a proof for the displayed infinite residual family.

## 4. Original weighted counts factor through finite jets

This calculation applies to the original all-five-tiles counts in P15–P18. Let T be the entire finite tiling set of a specified benzel. Put c=|Delta| and j(T)=min(R(T),L(T)), and retain the integer polynomial

    P(u)=sum_T u^j(T),  F(z)=sum_T z^(R(T)+L(T)).

The integer identity R+L=|R-L|+2 min(R,L), with R-L=Delta fixed, gives the exact equality

    F(z)=z^c P(z^2).                                      (1)

The original indexed map is Z[T]->Z[u], [T]->u^j(T). Its kernel consists of the integer combinations with zero coefficient sum on every j-fibre. The map P->z^c P(z^2) is an injective Z-linear map with inverse on its image obtained by reading the coefficients of z^(c+2j). Thus (1) retains the complete weighted polynomial, not just its parity or its value at a selected weight.

Writing a_j=#{T:j(T)=j} and M_m=sum_j a_j binom(j,m), the binomial theorem proves the finite exact expansion

    F(3)=3^c sum_(m>=0) 8^m M_m.                         (2)

For precision r>=1, let N=ceil(r/3) and define the actual ring maps

    J_r: Z[u] -> (Z/2^r)[epsilon]/(epsilon^N), u->1+epsilon,
    E_r: (Z/2^r)[epsilon]/(epsilon^N) -> Z/2^r, epsilon->8.

E_r is well-defined because 8^N=0 modulo 2^r. Its composite with J_r is evaluation at u=9 followed by reduction modulo 2^r. Therefore

    F(3) mod 2^r = 3^c E_r(J_r(P))
                 = 3^c sum_(0<=m<N) 8^m M_m mod 2^r.    (3)

The truncation uses the actual nilpotent epsilon and records its full surviving coefficients. In particular F(3)=3^c F(1) mod 8. Equivalently, multiplying by the actual inverse of the odd unit 3^c in Z/8 gives 3^(-c)F(3)=F(1) mod 8. This is a proved first-three-bits comparison of the weighted and unweighted observations.

For the peripheral families, direct substitution gives

    Delta(n,2n-3)=(n-5)(n-2)/2,
    Delta(n,2n-4)=(n^2-7n+14)/2.

The absolute value in c is retained, including n=4 in P16/P18. The new assignments request the original minority-stone factorial moments M_m at the needed finite precision. Controlling those moments uniformly as n varies remains mathematical work; (3) does not assert the requested 2-adic continuity.

Every ring map above lifts through G by G(f)(tau)=tau and G(f)(x-supported)=f(x)-supported. Composition follows on these two exhaustive cases. It sends supported zero to supported zero, including after an evaluation vanishes. For a fixed maximum precision, order the precision labels by reverse integer order and use the quotient maps as transitions. This is a finite join-semilattice with bottom at maximum precision and join=min. Its bottom fibre is allowed to be nonzero, exactly as in the upstream support-diagram construction. No unconstructed identification with the theta source is used.

There are 408 checked instances of (3): all 17 unordered admissible benzel pairs with 2<=a<=b<=7 and precisions 1 through 24. The independent exact-cover enumeration also reproduces their full polynomials, including the coefficient-by-coefficient invariant parity constraint.

## 5. P19: integral contraction certificates on the finite benzel window

Propp's full P19 concerns arbitrary simply-connected tileable regions. Here the certified family is explicitly limited to the 17 benzels above, with 6,492 tilings and 28,314 move edges in total. In particular the (7,7) case has 5,766 tilings and 26,127 permitted edges.

For a fixed region, let C_0 be the free Z-module on all its actual tilings and C_-1 the free Z-module on the allowed moves of Figure 5. Send an oriented move [T->U] to [U]-[T], and let epsilon:C_0->Z send every tiling to 1. Then epsilon partial=0. We use exactly the two permitted two-tile changes: opposite stones versus parallel bones; and a stone with a bone versus a stone of the same orientation with a differently oriented bone, with the identical six covered cells retained.

The emitted certificate lists every tiling, a root T0, and a parent for every other tiling. The checker validates coverage and disjointness, checks each parent edge against the actual two-move types, and verifies that every parent chain reaches T0. Let h([T]) be the signed sum along that chain from T0 to T, and let s(1)=[T0]. Telescoping gives, on every original generator,

    partial h = id_(C_0)-s epsilon,  epsilon s=id_Z.

For z in ker(epsilon) this becomes z=partial h(z); conversely every move boundary has augmentation zero. This proves ker(epsilon)=im(partial) over Z, so the reduced H_0 vanishes for every certified region. It retains explicit integer boundary representatives, not merely a floating-point rank.

The checker constructs tiles in two ways: translated triples in the barycentric carrier, and exhaustive classification of all three-cell subsets against axial offsets. It also compares a memoized fewest-options counting recurrence with a separate fixed-first-cell enumeration. These are independently implemented finite checks, not independent specialist review.

To attach the result to Split-Zero, let L be the power set of the permitted edge set, ordered by inclusion and joined by union. At each label A, retain the same C_0, the edge submodule Z[A], and H_A=C_0/im(partial_A). For A subset B, identity on C_0 and edge inclusion commute with partial. The resulting map H_A->H_B sends a class to the class of the same representative, and

    ker(H_A->H_B) = im(partial_B)/im(partial_A)

by that representative map, whose kernel and surjectivity are immediate from the two submodules. It is the upstream K_rep/B_C comparison with all original boundaries retained. Reconstructing the diagram sends a killed class to the zero at label B, not to absence. This is the concrete method application. Extending these contractions to every simply-connected region remains outside the finite certificate.

## 6. Green 92: an exact original-deck map and a reproduced collision family

Let A=Z<X0,X1> be the noncommutative polynomial algebra and I=(X0,X1). For a binary word w=w1...wn define

    S_w=(1+X_w1)...(1+X_wn).

Choosing either 1 or the letter in each factor proves that the coefficient of X_v1...X_vj is the number binom(w,v) of index-selected occurrences of v as a subsequence. Concatenation satisfies S_(uv)=S_u S_v. Linear extension from the free abelian group on original words gives the coefficient observation map; modulo I^(k+1) it records all decks through length k.

For fixed n>=k and |v|=j<=k, count pairs consisting of a selected occurrence of v and a k-index set containing it. Counting first the occurrence and first the k-index set gives respectively the right and left sides of

    sum_(|u|=k) binom(w,u) binom(u,v)
       = binom(n-j,k-j) binom(w,v).                     (4)

Thus the exact k-deck determines every smaller deck by division by the displayed positive integer. That division is only used on the realizable image, where (4) proves integrality. This explicitly relates Green's original k-deck question to the truncated algebra; no arbitrary linear kernel vector is called a collision of two source words.

For a concrete all-parameter family, define U0=0,V0=1 and

    U_(k+1)=U_k V_k,  V_(k+1)=V_k U_k.

These are the classical complementary Thue–Morse blocks; the k-binomial literature already studies their equal decks (Lejeune–Leroy–Rigo, arXiv:1812.07330). The following derivation is a reproduction, without a novelty claim.

Put D_k=S_Uk-S_Vk. Since D0=X0-X1 and

    D_(k+1)=D_k(S_Vk-1)-(S_Vk-1)D_k,

induction gives D_k in I^(k+1). The two distinct words of length 2^k therefore have the same subsequence counts through length k. To check the first surviving layer, for k>=1 let c_k be the coefficient of X0^k X1 in D_k. We have c1=1. The linear part of S_Vk-1 is 2^(k-1)(X0+X1). The coefficient of the all-zero monomial in D_k vanishes because U_k and V_k have equal zero counts. Consequently the displayed commutator gives

    c_(k+1)=-2^(k-1)c_k,
    c_k=(-1)^(k-1) 2^((k-1)(k-2)/2), which is nonzero.

This proves that the difference dies under truncation through degree k but survives in degree k+1, with its actual coefficient and source words retained. The code replays k=1,...,7 and performs 32,738 complete word/deck comparisons with a second checker that enumerates index subsets directly.

The exhaustive windows n<=12, k<=4 give first collision lengths 2,4,7,12 respectively. Witnesses are

    k=1: 01 / 10
    k=2: 0110 / 1001
    k=3: 0110001 / 1000110
    k=4: 011000100110 / 100010110001.

The scan includes all smaller eligible lengths, so the finite minimality statement is certified by the declared enumeration. It is not a new general bound for Green 92; the finite-jet difference and realizable two-word certificates are reusable attack inputs.

## 7. AIM coefficient maps: a complete small sign-chamber construction

Consider all real matrices [[a,b],[c,d]] with a,b>0 and c,d<0. For each such matrix use S=diag(1,1/b). Direct multiplication gives

    S^(-1) A S = [[a,1],[z,d]], z=bc<0.

The full coordinate map is (a,b,c,d)->(a,d,z,b); its inverse is (a,d,z,b)->(a,b,z/b,d), with a,b>0 and d,z<0. Thus b has been retained as an invertible coordinate, rather than an unjustified entry replacement.

The characteristic-coefficient map in the displayed chart is

    Phi(a,d,z)=(-a-d,ad-z).

For every desired pair (u,v) in R^2 take a=1+|u|+|v|, d=-u-a, z=ad-v. Then a>0 and a+u>=1+|v|, so d<0 and a(a+u)>|v|. Hence z=-a(a+u)-v<0. Direct substitution yields Phi(a,d,z)=(u,v). This is a complete section proving spectral arbitrariness of this particular 2x2 full sign pattern. It is a control instance, not a characterization of all patterns in AIM Section 2 Q1.

The Jacobian minor in (d,z) is [[-1,0],[a,-1]] with determinant 1. At (a,d,z)=(1,-1,-1), the actual matrix squares to zero. These observations specify finite-jet inputs at the original nilpotent point. The checker verifies 441 integer target pairs and three rational b-values for each.

## 8. Source-resolution controls and review boundary

AIM chip-firing Q14 is addressed by Perkinson–Yang–Yu, arXiv:1309.2201v2, Theorem 3, with inverse Algorithms 1–2 and the degree/kappa-inversion identity. Our exact reproduction verifies both inverse laws against independently enumerated parking functions and spanning trees: K2 through K6 and all 38 connected labelled four-vertex graphs, 43 graph cases and 1,569 graph/parking-function instances. Root 0 and descending neighbor order are fixed, as in the source. This is a replay of published mathematics.

AIM matrix-spectrum Section 3 Q6 is the Grone–Merris assertion proved by Hua Bai, arXiv:0911.2172v4. The status update uses that matching primary theorem. The quick checks construct the original incidence matrix B, retain L=BB^T, verify exact characteristic polynomials for 29 complete/complete-bipartite graph cases, and test the resulting integer majorizations. They do not audit Bai's full proof.

Shitov's arXiv:1612.01783v2 supplies a counterexample to the complex zero-pattern 2n analogue: order 708, 1,415 nonzeros. The workbench records this precise related result, not a disposition of the real sign-pattern or arbitrary-positive-characteristic questions. We reproduced the paper's two explicit 8x8 matrices, with characteristic polynomials t^8 and (t-1)^8, using exact trace recurrences and an independent rational-elimination determinant check at nine values of t. Agreement at nine points certifies equality of the degree-eight polynomials. This checks those two matrices, not the whole 708-dimensional generic-selection proof. The source's 8x8 block itself is not claimed spectrally arbitrary: its coefficient identity is phi4=-x4 phi7, as direct determinant expansion verifies.

P4 and P6 have pinned public formal sources, not merely an index mention. The P4 carrier, invariant numerator and publication endpoint were inspected. Its integer invariant numerator is exactly 6 Delta, and its target tile carrier matches Section 1. Nine finite P4 witnesses and seven P6 formula values were independently recalculated, the latter for n=5 through 11. The exact P4 commit is f8f91033216ba16fa851adbb9d6a9cf005509619; P6 is 5d1983de4592261dd0b915987ebcc9c0c8ae11b8. No Lean executable is installed in this runtime. Neither the full source dependency closure nor the trust-zero build was replayed. Both entries retain CLAIMED_UNVERIFIED and request that specific remaining review.

## Sources and reproduction

Primary problem sources and theorem locators are in ../catalog/status-delta.json. Upstream Split-Zero support diagrams are pinned at zeta-function-research-reader@1c8ec52c85c173adc9f8403a8a26914955e2f5a9, workbenches/splitzero-tandem/tex/support_diagrams.tex, especially D1–D8.

Run from this continuation's root:

    python tools/check_progress.py
    python -O tools/check_progress.py

The full certificate and receipt files are generated under evidence/. No network, paid computation, downstream agent launch or public-resolution announcement occurs. A finite receipt cannot promote a literature claim or our written argument to independently reviewed status.
