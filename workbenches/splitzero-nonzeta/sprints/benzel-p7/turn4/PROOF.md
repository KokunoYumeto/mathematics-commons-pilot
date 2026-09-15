# Turn 4: actual Split-Zero homology, Rees delay, and the positive repair fibre

15 September 2026. Parent: `d7cd069031536bea677ed31f7729ebdd4e9f97f6`, the fifth-collar contribution in PR 24 of `KokunoYumeto/mathematics-commons-pilot`.

This continuation proves an all-parameter support statement for the original fifth repair. It supplies a genuine support-indexed augmented complex, computes its distinguished integral homology transitions and their Rees defect, and gives exact dual certificates for its positive fibres. It does not claim a sixth-family construction, a full resolution of Propp 7, independent specialist acceptance, Lean verification, or priority.

## 0. Source mathematics actually used

The coefficient and reconstruction sources are the owner's `KokunoYumeto/zeta-function-research-reader`, pinned at `1c8ec52c85c173adc9f8403a8a26914955e2f5a9`:

- `workbenches/splitzero-tandem/tex/split_zero_carriers.tex`, scalar carrier and ring reflection.
- `workbenches/splitzero-tandem/tex/support_diagrams.tex`, D1-D8: reconstruction, changing support indices, coequalizer, comparison kernel, and the inclusion of the global-zero kernel into the supported-zero preimage.
- `formal/splitzero/DERIVED_MATHEMATICS.md`, sections 1-6, and `formal/splitzero/SplitZeroComplex.lean`, especially `differential_square`, `cycle_condition`, `homology_coequalizes`, and `homology_coequalizer`.
- `workbenches/split-support-rees-trace/RESEARCH_NOTE.md`, sections 2-5: the two filtrations on the actual comparison image, their Rees inclusion, residue pairing, amplification, and boundary character.

The current guide was also read at `ba360f08f3417464ca915233e3d3b54f5b76b30c`. Its same-source metric/residual-observation programme is not silently transferred to tilings. The core D1-D8 file has the identical blob `d3493f891291ee6e94dbf2c77649f7d85d240df2` at both revisions. The new 132-page analytic continuation was not independently audited or rebuilt here. Full source URLs and reading scope are in `SOURCES.json`.

The new constructions below are specializations and calculations on the original benzel complexes, not additional assertions made by those upstream sources. In particular, the positive-fibre certificate is proved below, rather than attributed to an upstream theorem.

## 1. Fixed original supports and the sixteen released generators

Throughout, d is an integer at least 4. Use the original cells `(x,y)` with

    y-x, 1-x-2y, 2x+y-1 in [1-a,b-1],
    W_h(d)=V(d+3h,2d+3h).

The bone anchors are H(x,y)={(x,y),(x+1,y),(x+2,y)}, V(x,y)={(x,y),(x,y+1),(x,y+2)}, D(x,y)={(x,y),(x+1,y-1),(x+2,y-2)}; S(x,y) is the right stone {(x,y),(x+1,y),(x,y+1)}.

The source is the parent's actual T4(d), translated by J(x,y)=(x+1,y+1). The parent proves it tiles J W4(d) inside W5(d). The source stone is S_d=S(3-d,d-1). Write

    K_d=W5(d) \ J W4(d),
    Lambda_empty=K_d disjoint-union cells(S_d).

For compact tables only, write a tile with offset anchor (u,v) for its original anchor (u-d,v+d). The map J_d(u,v)=(u-d,v+d) has inverse (x,y)->(x+d,y-d). It transports every displayed tile by translation; neither the region nor the coefficient of a cell is changed.

The parent's sixteen released old bones B1,...,B16 have these offset anchors, in their original order:

| i | kind | u | v |
|---:|---|---:|---:|
|1|D|-6|5|
|2|D|-5|3|
|3|D|-5|5|
|4|D|-5|6|
|5|D|-4|6|
|6|D|-3|6|
|7|D|-2|0|
|8|D|-2|1|
|9|D|-1|5|
|10|D|1|4|
|11|H|-3|2|
|12|H|-1|1|
|13|H|0|0|
|14|H|0|2|
|15|H|2|1|
|16|V|1|-3|

For A subset {1,...,16}, let

    Lambda_A = Lambda_empty disjoint-union (union of cells(Bi), i in A),
    v_A = sum of the original cell generators in Lambda_A.

These unions are disjoint because the stone and bones are actual distinct source tiles. Parent source membership is retained by exact blob checks in `support.py`. The original cell count is

    |Lambda_A|=9d+81+3|A|.

All placed bones contained in Lambda_A are permitted, not only the bones in a proposed replacement table. Let C_A^0 be the free integer module on those placed bones, C_A^1 the free integer module on Lambda_A, and C_A^2=0. The original differential is incidence: partial[b]=sum_{c in b}[c]. Write B_A=im partial and H_A=C_A^1/B_A.

For A subset B, let j_AB be inclusion of the original generators and eta_AB=sum_{i in B\A}[Bi]. Then

    v_B = j_AB v_A + partial eta_AB,
    eta_AC = j_BC eta_AB + eta_BC.

These are equalities of original cochains. In particular [v_A] transports to [v_B]. The affine map on positive fillings is n -> j_AB n + eta_AB, with the original incidence equality. On the target fillings containing the specified old bones eta_AB with coefficient one, restriction/removal gives its inverse. The inverse follows from the disjoint source-cell partition and nonnegativity, not from cancellation of cell counts alone.

## 2. The actual Split-Zero objects, including the affine-to-linear map

Take G(Z)=Z disjoint-union {tau}, with supported ring zero e. Its pair presentation is tau->(0,0), n->(n,1), onto {(0,0)} union (Z x {1}); componentwise arithmetic with Boolean support proves the operations and inverse. Thus e and tau have the same integer reflection but different support characters.

Use the join-semilattice

    L={bottom} disjoint-union P({1,...,16}).

Bottom represents empty CELL support. The empty RELEASE SET represents Lambda_empty, which is nonempty, and is a different label. The join of supported labels is union. The map bottom->empty cell set, A->Lambda_A preserves bottom and joins and is injective; its inverse on the image recovers exactly which disjoint old bone cells were added.

At bottom put C^i_bottom=0. Reconstruct each degree by the upstream D2 formula:

    M^i = disjoint union_{A in L} C_A^i,
    (A,x)+(B,y)=(A union B, j x+j y),
    e(A,x)=(A,0), tau(A,x)=(bottom,0).

The incidence maps commute with every j_AB and therefore give G(Z)-linear maps. The next differential has value (A,0) in degree 2. Hence

    d^1 d^0(A,n)=(A,0)=z_L(A,n).

Both sides have the original source and target degrees. At a nonbottom label this value is not (bottom,0), as is proved by the label projection. The cycle equalizer d(x)=e d(x) gives all original degree-one cell vectors here, as the outgoing amplitude is zero.

The projection q(A,p)=(A,[p]) is the coequalizer of (A,n)->(A,partial n) and (A,n)->(A,0). To check the universal property directly, let f equalize those two actual maps into any G(Z)-semimodule N. Two representatives p,p' at A differing by partial n have

    f(A,p)=f(A,p')+f(A,partial n)
          =f(A,p')+f(A,0)=f(A,p').

The last identity is the image of the original fibre-zero absorption. Thus g(A,[p])=f(A,p) is well-defined. Lifting representatives proves addition and scalar compatibility, and surjectivity of q proves uniqueness. No cancellation in N is used.

Here is a linear complex which also retains the AFFINE source correction and the positive fibre. At each supported label define

    C_hat_A^0 = Z direct-sum C_A^0,
    d_hat_A(r,n)=partial n-r v_A,
    C_hat_A^1=C_A^1, C_hat_A^2=0.

At bottom all three groups are zero. The actual transition is

    j_hat_AB^0(r,n)=(r,j_AB n+r eta_AB),
    j_hat_AB^1=j_AB.

The two cochain identities above prove

    d_hat_B j_hat_AB^0 = j_AB d_hat_A,
    j_hat_BC^0 j_hat_AB^0 = j_hat_AC^0.

Thus the upstream reconstruction applies to this actual diagram of complexes. Addition transports both summands by these arrows before adding; merely adding their tile coordinates at a union label would omit the charge-dependent corrections.

Its charge-one nonnegative integral cycles are EXACTLY the original patch tilings: d_hat_A(1,n)=0 says partial n=v_A; integer nonnegative counts and the all-ones target force each cell to be covered once. Conversely every patch tiling supplies such a cycle. The inclusion of these positive cycles into the integral cycle fibre is the identity on all charge and tile coordinates. The calculation below supplies a signed cycle outside that positive fibre, together with the exact dual certificate and the later positive cycle. This supplies the relationship rather than assuming either fibre determines the other.

`support.py` implements these reconstructed cochains, augmented arrows, support-preserving zero action, and the computed cyclic homology subdiagram. No Lean build is claimed.

## 3. A signed integral lift at the fifteenth support, for every d>=4

Let A_j={1,...,j}. Denote by beta the parent's proved positive fifth replacement on Lambda_A16. It consists of 3d+43 original bones. The following nine bones rho are literal fixed rows D2,D3,D4,D5,D6,D8,H11,V1,V2 of that table:

    D(-4,2), D(-3,2), D(-3,3), D(-1,-1), D(1,1),
    D(2,1), H(-1,2), V(0,-1), V(1,-2).

Anchors in this section use the explicit translation J_d of section 1. Their cells include all three cells of B16=V(1,-3). The union of their cells, minus B16, has 24 cells.

The following signed chain mu uses only bones within that 24-cell set:

    +H(-4,2) +V(-3,1) -D(-3,2)
    +D(-2,0) +D(-2,1) +H(-2,1)
    +H(-1,0) +H(-1,2) +D(1,1) +D(2,1).

Expansion of every three-cell generator gives

    partial mu = partial rho - partial B16.                 (1)

This is a single finite integer identity, retained in `signed_patch.json`; translation J_d proves it for every d. No coefficient field is changed. Therefore

    gamma15=beta-rho+mu,
    partial gamma15=v_A15.                                 (2)

All bones of beta-rho avoid B16's cells, by the parent's disjoint partition and the inclusion of those cells in rho. Every bone of mu is in Lambda_A15, verified on the unbounded original domain in section 4. The coefficient of D(-d-3,d+2) is -1, and all other coefficients are nonnegative. In particular gamma15 is an actual integral signed lift in this original support.

Let w=v_empty, included by the actual cell maps in every larger support. Then

    a15=gamma15 - sum_{i=1}^{15}[Bi],
    partial a15=w.                                         (3)

This fixed-vector preimage will determine the actual image filtration in section 6. The original all-ones target v_A15, its correction to w, and all negative coefficients remain available.

## 4. Sixteen exact duals exclude every proper positive support

For each i, `dual_certificates.json` supplies an integer cochain y_i on Lambda_{A16\{i}}. Its weights are at cells J_d(u,v). The complete coefficients are part of this proof, not a request for a future separation argument. They satisfy, for every integer d>=4,

    partial^* y_i(b)=sum_{c in b} y_i(c) >= 0
          for EVERY placed bone b contained in that support,
    y_i(v_{A16\{i}})<0.                                    (4)

Here partial^* is the transpose of the original incidence map into the integer dual. For example y_15 is -1 at the single cell J_d(4,-1) and zero elsewhere. All nine possible placed bones through that cell leave Lambda_{A16\{15}}.

The complete y_16 is given by the following offset/weight pairs:

    (-1,0):1, (-1,2):2, (0,-1):-1, (0,0):1, (0,2):-1,
    (1,0):-2, (1,1):3, (1,2):-1, (1,3):1,
    (2,0):1, (2,1):3, (2,2):2,
    (3,-1):-4, (3,0):7, (3,1):-3, (4,-1):-10.

Their sum is -1. On the signed chain mu, every positive term evaluates to zero; the negative term D(-3,2) evaluates to +1. Thus y_16(partial mu)=-1 by the same original incidence pairing.

For reference, the other exact negative evaluations, in order i=1,...,16, are

    -9,-1,-2,-2,-2,-2,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1.

### Complete verification over the unbounded parameter range

The checker never assumes that a sample of d determines the answer. Each cochain has finitely many negative sites. Every bone of negative total weight contains a negative site, so it occurs among the three orientations and three anchor offsets through such a site. The checker enumerates precisely those candidates.

For each candidate it must show that some cell is outside the actual support. At an affine cell J_d(u,v), membership in W5 and J W4 consists of the six original affine inequalities. Membership in a released original tile is a pair of affine equalities. Collect every nonconstant affine expression ad+b occurring in these tests. The integer interval endpoints floor(-b/a) and floor(-b/a)+1 separate every possible change of sign or equality. On each resulting interval, all membership truth values are constant. The last interval is unbounded. The verifier checks this sign stability exactly, then checks membership using the original inequalities, not a surrogate shape.

For the actual sixteen certificates, every test is already stable on the single interval [4,infinity). There are respectively

    51,35,41,32,27,29,33,23,21,15,18,12,12,13,9,28

negative-weight candidate bones, and each is excluded by those original membership tests. All nonzero weighted sites remain inside the claimed support. All remaining contained bones have nonnegative sum by the exhaustive negative-site argument. The same procedure proves containment of every cell of mu on [4,infinity). The fixed-table matches for rho are equality checks on the original affine generator formulas. Together these finite exact checks prove (1)-(4) on the stated infinite domain.

### Conclusion on the positive fibres

A nonnegative real chain n with partial n=v_{A16\{i}} would satisfy

    y_i(v)=<partial^*y_i,n> >= 0,

contradicting its displayed negative integer value. Thus that fibre is empty even over nonnegative reals.

For any proper A choose i outside A. A positive filling at A would extend to A16\{i} by adding the actual disjoint old bones with indices in (A16\{i})\A, using the affine map of section 1. This is impossible by (4). Consequently

    {A : the original nonnegative real filling fibre over v_A is nonempty}
        = {A16}.                                           (5)

At A16 the parent's beta is a positive integral filling. This excludes all 65,535 proper subsets simultaneously, for every d>=4. It proves inclusion-minimality WITHIN THE DISPLAYED sixteen-bone release dictionary for the fixed source tiling, source stone and translation. Alternative source tilings, stones, translations, or released bones outside that dictionary remain represented by other supports; no global minimum over those choices is asserted.

The map from positive integral cycles into all integral cycles in section 2 has empty charge-one source at A15 and contains the explicit charge-one signed target (1,gamma15). At A16 it contains (1,beta). Under the original augmented arrow, (1,gamma15) goes to (1,gamma15+B16). Its difference from (1,beta) is the explicit incidence-kernel vector rho-mu-B16. This gives all the maps between the two stages and the exact positive repair, not a categorical claim of unrelated objects.

## 5. The distinguished internal homology class and its comparison kernel

Put p_d=J_d(4,-1)=(4-d,d-1), an actual cell of the removed source stone. For every prefix A_j with j<=14, the evaluation l_j(p)=coefficient of p_d annihilates all its contained bone boundaries: its support is contained in the maximal omission of B15 treated by y_15. But l_j(w)=1. Therefore

    Z -> H_Aj, n -> [n w]

is injective with left inverse l_j. At A15, equation (3) kills [w] integrally; inclusion and the same preimage kill it at A16. The actual cyclic image subdiagram is thus

    Z --id--> ... --id--> Z --> 0 --> 0,
    labels             A0,...,A14  A15  A16.                 (6)

Each displayed 0 remains the zero AT ITS LABEL in the reconstruction. For example the transition sends (A14,[w]) to (A15,0), whereas tau sends it to (bottom,0). Those points have different labels. This is an operational use of the upstream support-indexed homology, not a numerical rank substituted for a transition map.

For the original chain inclusion C_A0 -> C_A15, let

    Krep={p in C_A0^1 : its original inclusion lies in B_A15}.

The map Krep/B_A0 -> ker(H_A0 -> H_A15), [p]->[p], is well-defined, injective, and surjective: source boundaries map to boundaries; the prequotient kernel is exactly B_A0; every killed class has a source representative in Krep. The element w belongs to Krep by (3). Evaluation at p_d gives the split injection Z[w] into this actual comparison kernel. No claim that it is the entire kernel is made.

One may also keep the constant charge-line diagram E_A=Z, at every supported label, and the map E_A -> H_A sending n to [nw]. On the prefix chain its supported-zero preimage is 0 through A14 and all of Z from A15 onward. Its global-zero kernel is only its bottom fibre: a supported source maps to a supported target label, even when its amplitude is zero. Their inclusion is exactly the upstream D8 map, here calculated on the charge-line comparison.

## 6. The actual Rees inclusion, integral lift, and residue dual

Use I_Z=Z w inside the original terminal cell module. Define

    V_Z={n in C_A16^0 : partial n belongs to Z w},
    c:V_Z -> I_Z, n -> partial n,
    F_j V_Z=V_Z intersect C_Aj^0    (0<=j<=16).

Outside this range extend by 0 at j<0 and by V_Z at j>=16. The target filtration is G_j I_Z=0 at j<0 and I_Z at j>=0. This is the source's comparison-image construction on the actual incidence map, with the original integer cutoff labels retained.

Evaluation at p_d proves c(F_j)=0 for j<15; a15 proves c(F_j)=I_Z for j>=15. Its quotient-to-image isomorphism sends [n] to partial n with inverse k w -> [k a15]; changing a preimage is exactly addition of an original incidence-kernel element.

Writing the decreasing indices as a=-j gives precisely the Rees convention of the source:

    L_Q=T^15 Z[T] w subset L_P=Z[T] w,
    D_Z=L_P/L_Q = Z[T]/(T^15) w.                            (7)

The isomorphism sends a polynomial of degree below 15 to its original class; the inverse takes the unique remainder modulo T^15. Its integral basis is w,Tw,...,T^14w. Rationalization acts coefficientwise and has no kernel on this explicitly free abelian group. Over the source's characteristic-zero field Q it yields a defect of length 15. This statement concerns (7), not the torsion of every benzel cohomology group.

The dual lattice quotient is T^(-15)Z[T]w^* / Z[T]w^*. Its residue pairing is

    ([f w],[g w^*]) -> coefficient of T^(-1) in fg.

Changing representatives changes fg by a polynomial, so the pairing is well-defined. In the bases T^i w and T^(-15+j)w^*, its matrix is 1_{i+j=14}; this matrix is its own inverse over Z. Thus all integral units, support maps and the residue coefficient are retained.

The graded defect and boundary character are

    Theta_D(z)=1+z+...+z^14,
    A_P(z)-A_Q(z)=1-z^15=(1-z)Theta_D(z),
    -[z d/dz (A_P-A_Q)]_(z=1)=15.                           (8)

On this same rank-one comparison, both its m-th tensor and symmetric power have inclusion T^(15m)Z[T] subset Z[T]. Their rationalized defects have length 15m, with the displayed monomial remainder bases. This is an evaluated amplification formula, not an unproved sublinear estimate or a claimed vanishing result.

The positive release threshold is 16 by (5), while the actual integral image delay measured by (7) is 15. Their relationship is supplied by the charge-one inclusion of section 2, the signed lift (2), its dual obstruction (4), and the positive lift beta. In particular an actual supported-zero homology class at A15 remains attached to a support with an empty positive filling fibre.

## 7. What was run and what changes next

`python verify.py` and `python -O verify.py` replay the exact affine certificates without a solver, the 24-cell signed identity, the source-row matches, all scalar/reconstructed-module laws on the stated finite test sets, the original augmented cochain squares, the noninjective homology transition, and the residue pairing. Separate tests enumerate every contained bone at d=4,...,100 and check the original positive and signed incidence equations. `recorded-checks.json` states the exact execution scope. Finite algebra tests are not represented as a Lean proof. The preceding all-parameter fifth construction is a pinned dependency, not a new discovery in this turn.

The new result removes every proper subset of the current repair dictionary from the positive search for every d, while showing explicitly that a signed integral lift was available earlier. Progress through other collars must therefore change the available support dictionary or source configuration rather than search its smaller subsets again. The augmented support complex and exact dual incidence maps provide the data structures for doing that calculation. No uniform variable-h positive lift has yet been supplied.
