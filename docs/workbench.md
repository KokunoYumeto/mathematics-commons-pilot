# Open Problem Workbench

**State:** concept stub / future workstream. No conjecture packet is runnable from this repository yet.

Have spare compute and want to point an agent at real mathematics? Pick a bounded problem packet. Reproduce what is known, try something honest, and return the evidence. Most runs will not solve a conjecture. Some may correct a stale status, verify a computation, improve a bound, sharpen a formulation, or preserve a useful failed path. The Commons should let the next run start where the previous one stopped.

## Purpose

The Workbench would be an open cumulative catalog of known conjectures and open problems without prestige filtering. Small neglected problems, maintained field lists, Propp-style collections, the Riemann Hypothesis, and Millennium problems may all be represented. Famous problems receive no privileged truth status; deliberately huge entries must declare that their literature packet is sampled or partitioned rather than pretending to be complete.

The first practical collection should be the maintained Erdős open-problems list because it is numerous, numbered, bounded, actively maintained, and rich in problems for which literature/status reconciliation is independently valuable.

## Exploratory source-list atlas

A supplied 2026-08-21 research snapshot makes the future workstream concrete enough to browse without pretending that it is already a corpus. All counts below are **claims tied to that dated snapshot**, not live totals or Commons-admitted problem records.

| Source family | Reported scope in the supplied snapshot | Possible role | Next gate |
|---|---:|---|---|
| [Erdős Problems](https://www.erdosproblems.com/) | 1,217 records; 608 classified `open` in the bundled YAML | First numbered status-reconciliation pilot | Pin the exact repository commit; replay the statement, references, variants, and current status for each selected number. |
| [Formal Conjectures](https://google-deepmind.github.io/formal-conjectures/) | 2,967 statements reported by the snapshot | Compare informal statements with Lean encodings | Freeze an exact commit and perform semantic review. A formal statement, and especially one containing `sorry`, is not a proof. |
| [AIM problem lists](https://aimath.org/problemlists/) | 165 linked documents; 3,359 secondary rows | Institutional list-of-lists and source discovery | Recover exact record boundaries and primary wording; reconcile status and item-level access before admission. |
| [AMR problem lists](https://amathr.org/problems/) | 113 pointers; 3,342 secondary rows | Broad discovery index | Treat as pointers only until each target source and problem boundary replay. |
| [Open Problem Garden](https://www.openproblemgarden.org/) | 422 secondary rows | Community-maintained mixed-field leads | Audit the exact page revision, statement, status, attribution, and reuse state. |
| [Ben Green's 100 Open Problems](https://people.maths.ox.ac.uk/greenbj/papers/open-problems.pdf) | 85 imported rows of a numbered 100 | Bounded additive-combinatorics and number-theory lane | Resolve the 15 missing numbers and freeze the living document version before status review. |
| [Kourovka Notebook](https://kourovkanotebookorg.wordpress.com/) | 150 imported issue-21 rows | Specialist group-theory lane | Bind edition, section, problem number, later comments, and current specialist status. |
| [K3 problem list](https://www.ams.org/bookpages/surv-295) | 366 problem locators | Low-dimensional-topology locator lane | Keep the source link-only at this stage; verify wording, subquestion boundaries, and status from an authorized source copy. |
| [The Open Problems Project](https://topp.openproblem.net/) | More than 75 numbered geometry problems reported | Small specialist pilot | Freeze the site revision and reconcile older status claims. |
| Propp collections ([matchings](https://library.slmath.org/books/Book38/files/propp.pdf), [benzels](https://faculty.uml.edu/jpropp/benzels.html), [trimers](https://www.samuelfhopkins.com/OPAC/files/proceedings/propp.pdf)) | 32 matchings problems, 20 trimer problems, plus newer bounded lists reported | Several compact combinatorics pilots | Separate each list and revision; construct a later-work/status graph before selecting a target. |
| Dynamics collections ([Stony Brook](https://www.math.stonybrook.edu/open-problems-dynamical-systems), [OPDS/ET](https://www.imath.kiev.ua/~skolyada/opds_et.html), [Boyle](https://www.math.umd.edu/~mboyle/open/)) | Multiple mixed-age specialist lists | Status-reconciliation and source-recovery lane | Partition by list and date; older pages carry high stale-status risk. |
| [Arnold's Problems](https://link.springer.com/book/10.1007/b138219) | 861 historical problems reported | Large historical comparison corpus | Partition before use and expect extensive solved/changed-status reconciliation. |
| [Open Quantum Problems](https://www.iqoqi-vienna.at/detail/news/open-quantum-problems) | Active specialist pages reported | Modern specialist intake | Recover and freeze each problem page, then compare its intended semantics with any formal encoding. |
| [Clay Millennium problems](https://www.claymath.org/millennium-problems/), Hilbert, and Smale | Small famous lists with enormous literatures | Deliberately oversized or “meme” entries | Declare a sampled or partitioned evidence corpus; never claim complete literature coverage. |

These are discovery leads, not admitted Commons problems. No row is runnable until its primary source, exact revision, statement, current status, access state, and bounded literature receipt are independently frozen. Bibliographic and recovery infrastructure—arXiv, zbMATH Open, Crossref, OpenAlex, Unpaywall, the Internet Archive, OEIS, and House of Graphs—belongs in the evidence workflow, not in the problem-list count. Public forum posts remain leads until theorem lookup, counterexample search, and provenance review; a tag is not a conjecture registry.

The spot check itself demonstrates why those gates matter. On 2026-08-21 the live Formal Conjectures front page displayed totals different from the supplied snapshot, and the live UnsolvedMath dataset card described a different row total from the bundled revision-specific workbook. The official Erdős Problems FAQ also says its status coverage is a work in progress and recommends an independent literature search. The Workbench must preserve such drift instead of silently choosing whichever number looks newest.

The attachment's 858-row conservative queue is useful triage, not admission: Open Problem Garden 385, K3 189, Kourovka 118, Green 76, AMR 64, and Erdős 26. Of those rows, 832 have no reconciled `current_status`, 638 carry warning flags, and all retain an unresolved underlying-source provenance or reuse state. Its 2,076-row source-document manifest is almost entirely a link backlog and does not yet bind per-document acquisition dates, bytes, hashes, and licenses. A spot audit of the 17-row literature delta also found date, title, and author-metadata discrepancies. These are repair queues for a later reviewed generation, not evidence that a packet is ready to run.

## One problem entry

A catalog row would bind:

- canonical statement, variants, attribution, date, field, stable IDs, and current status;
- the maintained source-list entry, exact revision/date, and original numbering;
- provenance and a history of status changes without silently rewriting the source list;
- directly cited papers, preprints, notes, computational data, code, and archived pages that may lawfully be shared;
- links and exact identities for relevant restricted material that cannot be redistributed;
- a bounded supplementary search for closely relevant open literature and archived sources;
- a citation/claim graph classifying direct attacks, partial results, equivalent formulations, sharper or weaker variants, computations, surveys, claimed solutions, refutations, and unrelated mentions;
- exact URLs, acquisition dates, licenses/access states, bytes, hashes, and an unresolved-source ledger;
- a compact status-first research workflow; and
- cumulative checkpoint and evidence-bundle rules.

A one-line conjecture is not a runnable packet. The evidence boundary, omissions, search limits, and unresolved contradictions must be visible.

## Erdős-first collection

1. Freeze the maintained list revision and preserve its numbering, wording, status, references, and provenance.
2. For each entry, collect every cited open/shareable reference and archived page.
3. Perform one declared, bounded supplementary literature search.
4. Build the claim graph and reproduce known calculations where feasible.
5. Reconcile status. If a problem appears solved or materially advanced beyond the maintained list, record a candidate status delta with exact evidence.
6. Return that delta to review without silently changing the canonical-list layer or flooding maintainers with raw model output.

Status reconciliation is a first-class mathematical contribution. A stale “open” label, missed partial result, or ambiguous variant should be corrected only through exact sources and independent checking.

## Cumulative contribution loop

1. Download and verify one bounded problem packet.
2. Audit its literature and current status before attempting progress.
3. Reproduce known computations or examples where possible.
4. Try one declared mathematical or computational attack within explicit limits.
5. Return one structured result class: no progress, reproduced result, failed path, counterexample search, sharper bound, new lemma, suspected proof, suspected refutation, or status correction.
6. Package all new code, data, evidence, checks, errors, and logs with exact provenance and a continuation cursor.
7. Require independent verification before promoting any mathematical claim.

Parallel attempts are welcome when declared. Negative results and failed approaches remain searchable so pooled compute is not spent repeating invisible work.

## Epistemic contract

- AI output is never called a proof or resolution merely because it is fluent.
- Source facts, machine inferences, experiments, conjectures, proof sketches, and independently checked proofs remain separately typed.
- Every material claim cites an exact source; unresolved contradictions remain exposed.
- A proposed solution stays `CLAIMED_UNVERIFIED` until appropriate specialist review or independent formal/manual verification.
- Model agreement is not independent verification.
- Contributors return a concise evidence-backed delta, not raw model output addressed to a list maintainer or mathematician.
- Licenses and access rules remain component-specific; restricted material is linked and identified, not redistributed.
- The project promises no solution. Literature organization, corrected status, reproduced computations, sharper formulations, reusable data, and well-recorded failure are useful outcomes.

## Packet scale

The same envelope should support a tiny problem and an oversized problem, but not with the same completeness claim.

- A bounded Erdős entry may aim for exhaustive coverage of its maintained references plus one explicit supplementary search.
- A field-scale or famous problem must be split by time, formulation, method, or cited subcorpus. Its catalog row must say `sampled` or `partitioned`, list omitted strata, and reject any “complete literature” claim.
- A meme-scale Riemann Hypothesis entry is permitted, but it receives the same evidence, status, and independent-review rules as every other row.

## Reference snapshot

The supplied file `Mathematical_Commons_Open_Problem_Workbench_v0.2_2026-08-21.zip` is a **candidate research import**, not a published or runnable Commons packet. It is 13,308,489 bytes with SHA-256 `A087B8A9765476F7DC26B00280299153D3BE46A536C698035445AF723451BD2A`. An independent read-only replay found 160 safe archive entries and matched all 159 payload entries against its self-excluding `MANIFEST.sha256` (zero missing, extra, or hash-mismatched entries).

The attachment self-reports 8,785 nonblank secondary statement candidates, 1,246 preliminary candidates, 858 mechanically conservative candidates, 824 statement-integrity review rows, and 4,831 provenance/status/rights review rows. Those are useful queue-shaping facts, not a unique-problem count, canonical statement audit, current-status audit, or specialist mathematical review. Its validators establish internal package consistency; they do not make the imported claims true. No attachment file, script, literature claim, forum lead, or worked example has been promoted into the live Commons by this concept update.

## Gates before implementation

This concept becomes a live workstream only after a separate reviewed change supplies:

1. a stable problem/variant/status schema;
2. a source-rights and acquisition manifest;
3. a claim-graph vocabulary;
4. bounded literature-search receipts;
5. deterministic packet and cumulative-handback builders;
6. explicit contribution/result-state schemas;
7. independent mathematical and computational review routes; and
8. one small Erdős pilot whose source and status replay passes.

Until those gates exist, this document is a roadmap contract—not an invitation to infer, scrape, package, or announce a conjecture result.
