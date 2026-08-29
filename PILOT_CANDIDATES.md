# First-pilot candidate docket

**Status:** researched shortlist for steward and reviewer selection; not yet the live pilot queue

**Assessment date:** 7 August 2026

**Targeted status refresh:** 30 August 2026 for Erdős problem 617 only. The other records retain their 7 August assessments.

**Target:** nine candidate records—seven established-problem candidates and two provisionally shortlisted community-originated status-reconciliation candidates

This docket turns the abstract six-to-ten-record target into a concrete starting set. A listing here is not a claim that a problem is open, solved, novel, suitable, or accepted. Before Day 1, a record steward must create an exact `problem_record`, open every material source, date and qualify the status assessment, resolve the intended statement, record rights, reserve reviewers, and issue only bounded packets. Erdős Problems pages are useful mutable indexes; they are not treated as adjudicating authority.

Selection and recruitment status is tracked on the [first-pilot launch board](PILOT_LAUNCH.md).

The proposed mix tests several outcomes that matter even when no new theorem appears: statement repair, literature reconciliation, rediscovery and attribution, formal replay, exact computation, certificate checking, special cases, exposition, and rejection of overclaim.

## Recommended first wave

### 1. Erdős problem 728 — solved-result and formal-replay calibration

The tracker's reconstructed intended question asks, for sufficiently small \(\varepsilon>0\) and every \(C>0\), for infinitely many \(a,b,n\) with \(a,b\geq\varepsilon n\), \(a!b!\mid n!(a+b-n)!\), and \(a+b>n+C\log n\). Sothanaphan proves the stronger logarithmic-window result: for every \(0<C_1<C_2\) and \(0<\varepsilon<1/2\), infinitely many triples satisfy

\[
\varepsilon n\leq a,b\leq(1-\varepsilon)n,\qquad
a!b!\mid n!(a+b-n)!,
\]

and

\[
C_1\log n<a+b-n<C_2\log n.
\]

- Leads: [tracker record, accessed 7 August 2026](https://www.erdosproblems.com/forum/thread/728), [Sothanaphan, arXiv:2601.07421](https://arxiv.org/abs/2601.07421), [Lean development pinned at commit `68da20b`](https://github.com/plby/lean-proofs/blob/68da20b96673899166e94638f5a7fffeb7231d35/src/v4.24.0/ErdosProblems/Erdos728b.lean).
- Qualified status: solved in the reconstructed intended sense; retain the historical ambiguity and require an informal-to-formal correspondence review.
- First packets: statement-lineage audit; pinned Lean build and axiom report; informal-to-formal correspondence review; small exact witnesses and exposition.
- Review needs: analytic number theory, (p)-adic valuation arguments, and Lean/mathlib.
- Rights boundary: the paper reports CC BY 4.0. The inspected Lean source did not establish a repository-wide license; link and verify it, but do not import or rededicate it without a documented basis.
- Overclaim guardrail: kernel acceptance does not by itself prove correspondence with Erdős's intended question, and replay is not a new-discovery claim.

### 2. Erdős problem 635 — uncertain-status literature reconciliation

For fixed \(t\geq1\), the problem asks for the largest \(A\subseteq\{1,\ldots,N\}\) such that whenever \(a,b\in A\) and \(b-a\geq t\), the difference \(b-a\) does not divide \(b\). One highlighted subquestion asks for an upper bound of \((1/2+o_t(1))N\) as \(N\to\infty\) with \(t\) fixed.

- Leads: [tracker record, accessed 7 August 2026](https://www.erdosproblems.com/635), [Elliott, *Probabilistic Number Theory I* (1979), Lemma 4.7](https://doi.org/10.1007/978-1-4612-9989-9), and [Ruzsa, “Erdős and the Integers”](https://doi.org/10.1006/jnth.1999.2395) as historical context.
- Qualified status: the tracker currently marks the overall extremal problem open and reports an affirmative answer to the asymptotic subquestion, first from a ChatGPT-5.2 argument and separately through an implication from Elliott's Lemma 4.7. That implication has not yet been independently reconstructed for this docket; treat the subquestion as reported-resolved/status-unverified until its source packet passes review.
- First packets: locate and reconstruct the Elliott implication; check fixed-\(t\) versus uniform quantifiers; enumerate exact small \((N,t)\) optima with certificates; formalize the \(t=1\) result or elementary constructions.
- Review needs: analytic/extremal number theory, asymptotics, exact enumeration, and optionally Lean.
- Rights boundary: use bibliographic metadata, links, and new summaries for copyrighted books and papers.
- Overclaim guardrail: never mark the overall problem solved merely because one asymptotic yes/no subquestion is verified.

### 3. Erdős problem 124 — canonical-statement repair and special cases

For a finite set \(A\) of integers greater than one, the intended conjecture concerns completeness of the sequence of sufficiently positive powers of elements of \(A\), with conditions involving \(\sum_{a\in A}1/(a-1)\) and \(\gcd(A)\). Nearby finite/infinite-set and exponent-zero variants have materially different answers.

- Sources: Burr, Erdős, Graham and Li, [“Complete sequences of sets of integer powers”](https://matwbn.icm.edu.pl/ksiazki/aa/aa77/aa7722.pdf), *Acta Arithmetica* 77 (1996), 133–138; [tracker record, accessed 7 August 2026](https://www.erdosproblems.com/124); [pinned Formal Conjectures declaration](https://github.com/google-deepmind/formal-conjectures/blob/7ce32c596f6cff050fa928a842a9dbe333b36b85/FormalConjectures/ErdosProblems/124.lean).
- Qualified status: the Burr–Erdős–Graham–Li finite-base conjecture for \(s\geq1\) and \(\gcd(A)=1\) remains open in general. The \(s=0\) question is reported solved, and \(A=\{3,4,7\}\) is a proved special case. For infinite base sets, Melfi constructed complete examples with arbitrarily small reciprocal sum, so the finite-set necessity does not extend unchanged.
- First packets: separate every variant in a canonical statement note; independently verify the paper's claim that 581 is the largest missing integer for \(\Sigma(\operatorname{Pow}(\{3,4,7\};1))\), separating finite enumeration below the cutoff from the analytic argument proving completeness above it; search additional finite sets with exact certificates; audit formal-statement correspondence; formalize one known special case or necessary condition.
- Review needs: additive number theory, complete sequences, exact computation, and Lean.
- Rights boundary: preserve the paper's terms; no open license was established for the primary paper in this audit. The cited Formal Conjectures repository is Apache-2.0, but this file contains six `sorry` occurrences and is a statement declaration, not a formal proof. Do not relabel either third-party component CC0.
- Overclaim guardrail: always state finite versus infinite (A) and the exponent convention; resolution of a simplified variant does not settle the intended conjecture.

## Second wave after the first workflow review

### 4. Erdős problem 333 — solved-negative verification and provenance

Current public evidence supports a negative answer. Erdős–Newman (1977), Theorem 2, together with a condensation argument, yields a density-zero set \(A\) for which every additive basis \(B\) satisfying \(A\subseteq B+B\) has

\[
|B\cap[1,N]|\not=o(N^{1/2}).
\]

The finite theorem predates the later Erdős–Graham question, and a public Lean development now proves an explicit dyadic-condensation version. Treat this pilot record as independent reconstruction, statement correspondence, and provenance reconciliation—not discovery.

- Sources: Erdős and Newman, [“Bases for Sets of Integers”](https://doi.org/10.1016/0022-314X(77)90003-8), *Journal of Number Theory* 9 (1977), 420–425; [tracker record, accessed 7 August 2026](https://www.erdosproblems.com/333); [pinned explanatory note](https://github.com/plby/lean-proofs/blob/68da20b96673899166e94638f5a7fffeb7231d35/ErdosProblems/Erdos333.md); [pinned Lean proof](https://github.com/plby/lean-proofs/blob/68da20b96673899166e94638f5a7fffeb7231d35/src/v4.30.0/ErdosProblems/Erdos333.lean).
- Qualified status: solved-negative in the current tracker and supported by the cited reconstruction; the pilot must still independently check the source implication, formal-statement correspondence, and provenance.
- First packets: reconstruct the exact Theorem 2-to-infinite-counterexample implication; audit \(\mathbb N\), zero, interval, density, and little-\(o\) conventions; replay the pinned Lean theorem and axiom report; publish the 1977 theorem → 1980 question → later rediscovery/formalization timeline.
- Review needs: additive combinatorics, probabilistic methods, asymptotics, and optionally Lean.
- Rights boundary: link and cite the copyrighted paper. The pinned Lean file contains no `sorry` and reports only `propext`, `Classical.choice`, and `Quot.sound`, but its repository has no declared license; link and replay rather than importing it. Publish only a new reconstruction and Commons-originated metadata under the Commons rule.
- Overclaim guardrail: use “rediscovery,” “reconciliation,” or “formalization,” not “first proof.”

### 5. Erdős problem 617 — fixed-case verification and claim review

For \(r\geq3\), the conjecture asks whether every \(r\)-edge-colouring of \(K_{r^2+1}\) contains \(r+1\) vertices whose induced complete graph omits at least one colour. The source proves \(r=3,4\). Public July 2026 preprints claim the fixed cases \(r=5,6,7,8,9\), but they do not address every \(r\), and the general problem remains open.

- Sources: Erdős and Gyárfás, [“Split and balanced colorings of complete graphs”](https://doi.org/10.1016/S0012-365X(98)00323-9), *Discrete Mathematics* 200 (1999), 79–86; [tracker record, accessed 30 August 2026](https://www.erdosproblems.com/617); [pinned Formal Conjectures declaration](https://github.com/google-deepmind/formal-conjectures/blob/7ce32c596f6cff050fa928a842a9dbe333b36b85/FormalConjectures/ErdosProblems/617.lean); Sneiderman's [fixed-\(r=5,6,7,8\) release](https://github.com/Robby955/erdos-617-fixed-cases/releases/tag/fixed-r5-r8-2026-07-20), including the non-computational \(r=6\) preprint; Kara's independent [fixed-\(r=5\) formal-verification release](https://github.com/RamazanKara/erdos-617-r5-formal-verification/releases/tag/e058-r5) and [frozen Zenodo record](https://doi.org/10.5281/zenodo.21535386).
- Qualified status: open for general \(r\geq3\); Erdős–Gyárfás prove \(r=3,4\). The fixed \(r=5\) theorem now has an independent formal and certificate verification whose exported Lean theorem reports exactly `propext`, `Classical.choice`, and `Quot.sound`; the verifier nevertheless records that independent expert review is incomplete. Treat \(r=5\) as a machine-verified fixed-case resolution, not a resolution of the all-\(r\) conjecture. The public \(r=6,7,8,9\) manuscripts remain preprint claims without completed external mathematical review and stay `CLAIMED_UNVERIFIED` for this docket.
- First packets: source-to-formal statement audit; reconstruct or formalize the published \(r=3\) or \(r=4\) argument; independently replay the frozen \(r=5\) verification and audit its correspondence to the historical statement; digest and adversarially check the non-computational \(r=6\) proof claim, formalizing its load-bearing lemmas or full fixed-case conclusion where feasible. Defer the computer-assisted \(r=7,8,9\) packages until certificate-review capacity is explicitly reserved.
- Review needs: Ramsey/extremal graph theory, finite geometry, formal-statement correspondence, reproducible certificate checking, and Lean graph theory.
- Rights boundary: link and cite the original paper. Preserve Apache-2.0 for the Formal Conjectures declaration and Kara's verification repository, and CC BY 4.0 for the archived Kara preprint; these are distinct rights layers. No repository-wide license was established for the inspected Sneiderman fixed-case repository, so link and review it without importing or rededicating its files.
- Overclaim guardrail: one or several fixed values do not prove the universal conjecture. A counterexample needs an explicit colouring and independent exact checker; a positive fixed-case result needs a checked proof or certificate and statement-correspondence review. Do not call \(r=6\) verified merely because its release is intact or because other models agree with it.

## Visible anchors, kept deliberately bounded

### 6. Erdős problem 242 — Erdős–Straus

For each integer \(n>2\), the tracker formulation asks for distinct positive integers \(x<y<z\) satisfying \(4/n=1/x+1/y+1/z\). Record this denominator and ordering convention explicitly before comparing computational or theoretical claims across sources.

- Sources: [tracker record, accessed 7 August 2026](https://www.erdosproblems.com/242), [Salez, arXiv:1406.6307](https://arxiv.org/abs/1406.6307), [Elsholtz–Tao, arXiv:1107.1010](https://arxiv.org/abs/1107.1010) as theoretical context, [Mihnea–Dumitru, arXiv:2509.00128](https://arxiv.org/abs/2509.00128), and the [verification code pinned at commit `e36eef1`](https://github.com/esc-paper/erdos-straus/tree/e36eef1815d339701b9f168fe7fa504ccfa401e8).
- Qualified status: open. Salez verified the conjecture through \(10^{17}\). Mihnea–Dumitru (2025) report verification through \(10^{18}\); this remains a preprint computation requiring artifact-level replay, not a proof.
- First packets: reproduce a bounded interval with an independently written checker; audit compiler, overflow, completeness, hashes, and source availability behind published bounds; formalize one congruence family; build a curated literature/status map.
- Review needs: Diophantine and analytic number theory, exact systems programming, and Lean.
- Rights boundary: the cited papers use arXiv's non-exclusive distribution license; the pinned code repository is CC0-1.0. Preserve those distinct layers and do not treat arXiv availability as a software license.
- Overclaim guardrail: finite search is not proof. Preserve denominator distinctness, prime reductions, and exact congruence coverage.

### 7. Erdős problem 993 — independence polynomials of trees

The conjecture asks whether the sequence counting independent sets of each size in every tree is unimodal. Li (2026) proves unimodality for the two infinite non-log-concave families \(T_{3,m,n}\) and \(T^*_{3,m,n}\). Zenodo v3 reports an exhaustive computation over all 8,691,747,673 unlabeled trees with at most 29 vertices.

- Sources: Alavi, Malde, Schwenk and Erdős, [“The vertex independence sequence of a graph is not constrained”](https://combinatorica.hu/~p_erdos/1987-33.pdf) (1987); [canonical tracker record, accessed 7 August 2026](https://www.erdosproblems.com/993) and [tracker discussion](https://www.erdosproblems.com/forum/thread/993); [Li, arXiv:2603.03025](https://arxiv.org/abs/2603.03025); [finite-verification Zenodo v3](https://doi.org/10.5281/zenodo.19100781); [repository release `paper-v2-2026-03-18-doi`](https://github.com/BrettRey/erdos-problem-993/releases/tag/paper-v2-2026-03-18-doi), tag commit `487096954fef98f7ff93a352d241f3f8d62ef0e5`.
- Qualified status: the universal tree/forest conjecture remains open. The finite result is a replayable empirical claim, not a proof.
- First packets: independently reproduce a smaller feasible range; verify known non-log-concave examples remain unimodal; audit enumeration completeness, graph isomorphism handling, integer arithmetic, manifests, and checksums; formalize the deletion recurrence and selected families.
- Review needs: enumerative graph theory, graph isomorphism, exact polynomial arithmetic, reproducible HPC, and Lean.
- Rights boundary: the cited Zenodo artifact reports CC BY 4.0 and the living repository reports MIT, but the repository has advanced beyond the DOI snapshot; treat the older article separately and bind any replay to the pinned release.
- Overclaim guardrail: exhaustive finite evidence is not a universal proof, and failure of log-concavity is not failure of unimodality.

## Community-nominated candidates — two slots provisionally filled

These records arose in the public community discussion that prompted the pilot. Both are now status-reconciliation tasks rather than open-conjecture attacks. Their inclusion remains provisional until a steward freezes a Commons-originated canonical statement, checks the source and rights layers, and reserves an independent reviewer.

### 8. Random monomial unitaries — elementary reconstruction and literature reconciliation

Let \(U_n=D_nP_{\sigma_n}\), where \(D_n\) is diagonal with unit-modulus entries and \(\sigma_n\) is a uniform permutation. Each cycle \(C\) of length \(\ell\) contributes the roots of

\[
z^\ell-\prod_{j\in C}(D_n)_{jj},
\]

a rotated regular \(\ell\)-gon. Hence, for half-open arcs \(A\),

\[
\left|\mu_n(A)-\frac{|A|}{2\pi}\right|
\leq \frac{K(\sigma_n)}n,
\]

where \(K(\sigma_n)\) is the number of cycles. Since \(\mathbb E[2^{K(\sigma_n)}]=n+1\), Markov's inequality and Borel–Cantelli give \(K(\sigma_n)/n\to0\) almost surely under any coupling of the uniform marginals. Thus \(\mu_n\) converges weakly almost surely to uniform measure. Random diagonal phases are not needed for this bound.

- Sources: [u/dForga's original 17 August 2025 post](https://www.reddit.com/r/LLMmathematics/comments/1mt30bn/spectral_equidistribution_of_random_monomial/); [Najnudel–Nikeghbali, arXiv:1005.0402](https://arxiv.org/abs/1005.0402); [published article](https://doi.org/10.5802/aif.2777); [exact Zenodo version 17058911](https://doi.org/10.5281/zenodo.17058911), under concept DOI `10.5281/zenodo.17058910`.
- Qualified status: resolved/known, not an open conjecture. The model and convergence literature predate the Reddit post; the pilot contribution is an elementary reconstruction, exact discrepancy statement, literature reconciliation, and attribution record. Make no novelty claim for the model or convergence theorem.
- First packets: freeze the statement and coupling quantifiers; independently prove the weighted-cycle characteristic polynomial and arc-discrepancy lemma; locate the closest result in the 2013 paper; reconcile the 2025 Reddit post, September 2025 deposit, and August 2026 resolution comment; optionally formalize the deterministic finite lemma.
- Review needs: random permutations, spectral measures, discrepancy, probability, and optionally Lean.
- Rights boundary: Reddit content is not automatically CC0; link and summarize it unless the author documents a CC0 permission. The cited Zenodo version reports CC BY 4.0. A newly written independent reconstruction may be CC0 under the Commons rule while preserving proposer and literature attribution.
- Overclaim guardrail: the exact elementary discrepancy inequality still needs a precise prior-art locator before any priority statement.

### 9. Flat holomorphic embeddings into \(\mathbb C\times\mathbb H\) — correction and resolved flat case

Classify holomorphic isometric embeddings

\[
F=(f,g):(\mathbb C,|dz|^2)\longrightarrow
\left(\mathbb C\times\mathbb H,
|dw_1|^2+\frac{|dw_2|^2}{(\operatorname{Im}w_2)^2}\right).
\]

The Cayley transform of \(g:\mathbb C\to\mathbb H\) is bounded entire, so Liouville's theorem gives \(g\equiv c\). The metric equation then gives \(|f'|\equiv1\); the open mapping theorem forces \(f'\) to be constant. Therefore every embedding is

\[
F(z)=(az+b,c),\qquad |a|=1, b\in\mathbb C, c\in\mathbb H.
\]

- Source: [u/dForga's original 12 August 2025 post](https://www.reddit.com/r/LLMmathematics/comments/1mo5vcs/embeddings_of_riemann_surfaces_into_%E2%84%82_%E2%84%8D/).
- Qualified status: proposed resolved status for the flat-\(\mathbb C\) case, supported by this elementary argument but pending independent packet-level verification and a prior-art check. The post's much broader “general \(\rho\)” question is neither solved nor precise enough to inherit this status.
- First packets: freeze the flat statement, target-metric normalization, and embedding-versus-immersion convention; independently check the Liouville/open-mapping proof; search for a standard literature locator; publish a correction note separating the flat theorem from the broader question; explicitly reject the false 2025 general-classification claim.
- Review needs: complex analysis, Riemannian geometry, and source/status review.
- Rights boundary: link and summarize the Reddit source unless the author documents permission; publish an independently drafted CC0 statement and proof with provenance intact. Do not use Zenodo `10.5281/zenodo.17058899` or its exact version `10.5281/zenodo.17058900` as positive mathematical evidence merely because the deposit reports CC BY 4.0.
- Overclaim guardrail: the broader rigidity claim is false. On \(\mathbb H\), \(F(z)=(z,z)\) embeds holomorphically in \(\mathbb C\times\mathbb H\) with induced metric \((1+(\operatorname{Im}z)^{-2})|dz|^2\), both components nonconstant, and variable curvature.

Every later community nomination must still supply an immutable statement and attribution basis, a dated qualified status assessment, primary-source locators, explicit rights, a bounded useful deliverable, objective checks and resource caps, an independent-review lane, proportionate tool disclosure, and clear stop conditions.

## Proposed launch order

Begin with 728, 635, and 124. Together they test formal replay and statement correspondence, status reconciliation under uncertainty, and canonical-statement repair with bounded computation. Add the two small community resolved-calibration records after their statement and rights packets pass. Admit 333 and the refreshed 617 fixed-case review only after the first process review; scope 617 first to the frozen \(r=5\) replay and independent \(r=6\) proof review. Keep 242 and 993 as reserve anchors unless reviewers and computational capacity are explicitly reserved.

That produces a seven-record active pilot with two documented reserves; it does not pretend that all nine can consume reviewer capacity simultaneously.

No candidate moves into `problems/` until its exact record validates, a steward accepts responsibility, and at least one independent reviewer is reserved. The eventual public queue is the validated record set, not this prose shortlist.
