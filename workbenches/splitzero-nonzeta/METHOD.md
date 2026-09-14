# Split-Zero method: sources and actual transfer maps

Upstream: https://github.com/KokunoYumeto/zeta-function-research-reader/tree/1c8ec52c85c173adc9f8403a8a26914955e2f5a9

Read `workbenches/splitzero-tandem/tex/split_zero_carriers.tex`, `workbenches/splitzero-tandem/tex/support_diagrams.tex`, `formal/splitzero/DERIVED_MATHEMATICS.md` and `workbenches/split-support-rees-trace/RESEARCH_NOTE.md`. These are the source proofs, not replaced by this routing note. The programme and workbench guides were also read. The complete upstream analytic or Lean development was not independently re-verified in this session.

## Supported scalars and indexed sources

For the source carrier G(R)=R disjoint union {tau}, the supported ring zero is e=0_R, while tau is the additive identity and multiplicatively absorbing. The explicit semiring isomorphism is tau -> (0,0), r -> (r,1), onto {(0,0)} union (R x {1}) inside R x Boolean. Two supported pairs add to (r+s,1) and multiply to (rs,1); this proves the operation identities and the displayed inverse recovers each element.

The amplitude projection p sends tau and e to 0. The support projection chi sends tau to 0 and every supported element, including e, to 1. For a lifted determinant, p returns the ordinary signed sum and chi returns the Boolean sum of permitted permutation terms. The all-ones 2-by-2 determinant is e, from the two cancelling present terms. An entirely absent row produces tau. Therefore the actual term-indexed source is also retained: a free module on permutations, tilings or other original objects maps each basis element to its original signed/character-weighted contribution. The kernel of that evaluation, not term presence alone, controls cancellation.

## Support diagrams

Use a join-semilattice L with bottom, R-modules V_l and coherent linear maps rho_lk for l<=k. The source reconstructs their disjoint union with addition (l,x)+(k,y)=(l join k, rho_l,l-join-k(x)+rho_k,l-join-k(y)). A morphism (alpha,f_l) preserves bottom and joins and satisfies f_k rho_lk = rho'_alpha(l),alpha(k) f_l.

The inverse on a G(R)-semimodule M uses L=eM, V_l={m:em=l}, and rho_lk(m)=m+k. The comparison (l,m)->m has inverse m->(em,m). Absorption m+em=m proves the additive compatibility; the source proves the full natural comparisons. The bottom fibre is allowed to be nonzero.

For tilings of a fixed region, allowed move sets are indexed by inclusion and joined by union. Adding moves gives an inclusion on edge generators and identity on tiling generators, an actual coherent diagram. Changing the region requires a separately constructed extension map; no such map is assumed for arbitrary pairs of regions.

## Comparison cohomology

For a fixed cochain map f:C->D, write Z_C=ker d_C, B_C=im d_C(previous) and Krep={z in Z_C:f(z) belongs to B_D}. The map Krep/B_C -> ker H(f) sends [z] to its original source class. It is well-defined because f carries boundaries into boundaries; the prequotient kernel is exactly B_C; every kernel class has a cycle representative in Krep. These statements prove the isomorphism, retaining the actual source boundaries. Intertwining actions descend through the same representative map.

For F=T(alpha,f), the inverse image of all supported target zeros is T(L,ker f_l). Its global-zero kernel restricts to labels with alpha(l)=bottom. Their relationship is the inclusion of that label subset. A boundary at a nonbottom label remains its own supported zero.

For a move graph use d([t->t'])=[t']-[t] and epsilon([t])=1. Then reduced H0=ker epsilon/im d. Componentwise augmentation identifies H0 with one copy of R per component: choose a representative vertex in each component for the inverse and use paths as explicit boundary differences. Thus a finite graph with c components has reduced rank c-1. A uniform region theorem still needs a proof across all original regions.

## Rees defects, jets and actual metrics

For the source's filtered comparison c with actual image I, keep both Q^a I=c(F^a V) and P^a I=I intersect G^a W. The inclusion of Rees lattices L_Q into L_P gives D_c=L_P/L_Q. For the concrete inclusion T^2 k[T] into k[T], the quotient has basis 1,T, Hilbert polynomial 1+z, and numerator (1-z)(1+z)=1-z^2. Its negative derivative at z=1 is its length 2. The residue pairing is the invertible anti-diagonal matrix on the corresponding monomial bases.

For an ideal I in a polynomial algebra A, [f] -> df mod I defines I/I^2 -> Omega_A tensor_A A/I because d(uv)=u dv+v du vanishes modulo I for u,v in I. Its kernel remains part of the calculation. Matrix coefficient jobs retain all permitted original entries before using this map; setting entries to one requires a displayed coordinate change and inverse on the stated domain.

The Gram must come from the original source norm and observation map. For q:Q^2->Q, q(x,y)=x+y with Euclidean norm, the orthogonal section of 1 is (1/2,1/2), of norm squared 1/2. Every other preimage is (1/2+t,1/2-t), of norm squared 1/2+2t^2. This proves the actual source-derived minimum. Quantum jobs likewise retain frame coordinates and the exact Gram map; a symmetry restriction includes its actual inclusion into that source.

## Concrete calibration obligations

The triangle, edge-deleted path and edge-contracted two-parallel-edge graph have reduced Laplacians [[2,-1],[-1,2]], [[1,-1],[-1,2]], and [[2]], with cokernel orders 3,1,2. No injective homomorphism Z/2->Z/3 exists, since 2x=0 in Z/3 forces x=0. Hence these groups do not give the naive short exact sequence. AIM Q10 is an algebra-level question, so that group obstruction is not a disposal of its intended formulation. For the rational augmentation Q[C3]->Q, the kernel is Q[z]/(z^2+z+1), a field, whereas Q[C2] has the nontrivial idempotent (1+u)/2. This explicitly blocks an injective algebra arrow from Q[C2] onto that kernel. Coefficients and actual arrows remain essential.

For a binary word x and bit survival p, the mean trace polynomial is M_x(w)=p P_x(1-p+pw). Bit i survives with probability p, and its output index has generating function (1-p+pw)^i from the earlier bits; summing proves the identity. The coefficient map is triangular with diagonal p^(i+1), hence determinant p^(n(n+1)/2). Finite injectivity gives no uniform statistical sample bound without quantitative control of this same map.

For length-two subsequence decks, 0110 and 1001 both give multiplicities (1,2,2,1) in coordinates 00,01,10,11. Thus their basis-vector difference lies in the deck-map kernel and comes from two actual source words. General linear kernel elements retain their coefficients rather than being called two-word collisions automatically.

## Ranking rule

A: an explicit finite complex, relation matrix, quotient tower or polynomial map supplies an immediate bounded task. B: the source/target route is concrete but substantial construction or quantitative control remains. C: an explicit major bridge such as integral comparison, analytic compactness, geometric realization or passage to an infinite endpoint remains. This assesses the displayed routes; it does not assert that no other mathematical relationship exists. The exact first task and outstanding endpoint are both retained in seeds.psv.
