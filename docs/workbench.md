# Open Problem Workbench

**State:** independently replayed candidate package; exact source ZIP recovery is required before publication. No canonical runnable problem packet has yet passed the full admission contract.

The supplied Workbench v0.2 package supports statement verification, source recovery, status reconciliation, literature curation, reproducible computation, failed-approach records, and bounded mathematical attempts. It does not contain a verified solution collection. Its exact ZIP is currently unavailable, so this repository does not claim a downloadable release.

## Dedicated candidate workbench

The external [Erdős–Straus Workbench at commit `240c4e1db1ca8e07d21a7a8a5f9a0a043cb3aa95`](https://github.com/KokunoYumeto/erdos-straus-workbench/tree/240c4e1db1ca8e07d21a7a8a5f9a0a043cb3aa95) is registered here as a dedicated candidate workbench for independent review. This registration does not admit or accept its problem record or packet, make either runnable in the central catalog, or change the canonical counts or status on this page. The candidate's own current-status assessment is `not_assessed`; its first bounded packet is `ready` only for independent review and remains `CLAIMED_UNVERIFIED`.

The pinned candidate evidence is its [problem record](https://github.com/KokunoYumeto/erdos-straus-workbench/blob/240c4e1db1ca8e07d21a7a8a5f9a0a043cb3aa95/problems/MC-ES-PROBLEM-001-v1.0.0.json), [ready packet](https://github.com/KokunoYumeto/erdos-straus-workbench/blob/240c4e1db1ca8e07d21a7a8a5f9a0a043cb3aa95/packets/MC-ES-PACKET-R107-001-v1.1.0-ready.json), [draft-to-ready transition](https://github.com/KokunoYumeto/erdos-straus-workbench/blob/240c4e1db1ca8e07d21a7a8a5f9a0a043cb3aa95/transitions/MC-ES-TRANSITION-R107-001-v1.0.0.json), [producer replay receipt](https://github.com/KokunoYumeto/erdos-straus-workbench/blob/240c4e1db1ca8e07d21a7a8a5f9a0a043cb3aa95/work/MC-ES-PACKET-R107-001/R107_DEFICIT_PROGRESSION_REPLAY.json), and [CI run for the exact commit](https://github.com/KokunoYumeto/erdos-straus-workbench/actions/runs/32908242614). The replay receipt's `PASS` is producer evidence, not independent acceptance or a claim about the full conjecture.

## Purpose

The intended catalog includes known conjectures and open problems without prestige filtering. Small neglected problems, maintained field lists, Propp-style collections, the Riemann Hypothesis, and Millennium problems may all be represented. Deliberately large entries must declare that their literature package is sampled or partitioned rather than claiming completeness.

The first planned runnable collection is based on the maintained Erdős open-problems list because it is numerous, numbered, bounded, actively maintained, and rich in problems for which literature and status reconciliation are independently valuable. No Erdős packet has yet passed admission.

## Included source-list index

The supplied 2026-08-21 package contains a dated source-list index. All counts below are tied to that independently replayed package; they are not live totals or admitted canonical problem records.

| Source family | Reported scope in v0.2 | Candidate use | Required verification |
|---|---:|---|---|
| [Erdős Problems](https://www.erdosproblems.com/) | 1,217 records; 608 classified `open` in the bundled YAML | First numbered status-reconciliation collection | Pin the exact repository commit; replay the statement, references, variants, and current status for each selected number. |
| [Formal Conjectures](https://google-deepmind.github.io/formal-conjectures/) | 2,967 statements reported by the snapshot | Compare informal statements with Lean encodings | Freeze an exact commit and perform semantic review. A formal statement, and especially one containing `sorry`, is not a proof. |
| [AIM problem lists](https://aimath.org/problemlists/) | 165 linked documents; 3,359 secondary rows | Institutional list-of-lists and source discovery | Recover exact record boundaries and primary wording; reconcile status and item-level access before admission. |
| [AMR problem lists](https://amathr.org/problems/) | 113 pointers; 3,342 secondary rows | Broad discovery index | Treat as pointers only until each target source and problem boundary replay. |
| [Open Problem Garden](https://www.openproblemgarden.org/) | 422 secondary rows | Community-maintained mixed-field leads | Audit the exact page revision, statement, status, attribution, and reuse state. |
| [Ben Green's 100 Open Problems](https://people.maths.ox.ac.uk/greenbj/papers/open-problems.pdf) | 85 imported rows of a numbered 100 | Bounded additive-combinatorics and number-theory collection | Resolve the 15 missing numbers and freeze the living document version before status review. |
| [Kourovka Notebook](https://kourovkanotebookorg.wordpress.com/) | 150 imported issue-21 rows | Specialist group-theory collection | Bind edition, section, problem number, later comments, and current specialist status. |
| [K3 problem list](https://www.ams.org/bookpages/surv-295) | 366 problem locators | Low-dimensional-topology locator collection | Keep the source link-only at this stage; verify wording, subquestion boundaries, and status from an authorized source copy. |
| [The Open Problems Project](https://topp.openproblem.net/) | More than 75 numbered geometry problems reported | Small specialist collection | Freeze the site revision and reconcile older status claims. |
| Propp collections ([matchings](https://library.slmath.org/books/Book38/files/propp.pdf), [benzels](https://faculty.uml.edu/jpropp/benzels.html), [trimers](https://www.samuelfhopkins.com/OPAC/files/proceedings/propp.pdf)) | 32 matchings problems, 20 trimer problems, plus newer bounded lists reported | Several compact combinatorics collections | Separate each list and revision; construct a later-work/status graph before selecting a target. |
| Dynamics collections ([Stony Brook](https://www.math.stonybrook.edu/open-problems-dynamical-systems), [OPDS/ET](https://www.imath.kiev.ua/~skolyada/opds_et.html), [Boyle](https://www.math.umd.edu/~mboyle/open/)) | Multiple mixed-age specialist lists | Status reconciliation and source recovery | Partition by list and date; older pages carry high stale-status risk. |
| [Arnold's Problems](https://link.springer.com/book/10.1007/b138219) | 861 historical problems reported | Large historical comparison corpus | Partition before use and expect extensive solved/changed-status reconciliation. |
| [Open Quantum Problems](https://www.iqoqi-vienna.at/detail/news/open-quantum-problems) | Active specialist pages reported | Modern specialist intake | Recover and freeze each problem page, then compare its intended semantics with any formal encoding. |
| [Clay Millennium problems](https://www.claymath.org/millennium-problems/), Hilbert, and Smale | Small famous lists with enormous literatures | Deliberately oversized entries | Declare a sampled or partitioned evidence corpus; never claim complete literature coverage. |

These are discovery leads, not admitted Commons problems. No row is runnable until its primary source, exact revision, statement, current status, access state, and bounded literature receipt are independently frozen. Bibliographic and recovery infrastructure—arXiv, zbMATH Open, Crossref, OpenAlex, Unpaywall, the Internet Archive, OEIS, and House of Graphs—belongs in the evidence workflow, not in the problem-list count. Public forum posts remain leads until theorem lookup, counterexample search, and provenance review; a tag is not a conjecture registry.

The spot check itself demonstrates why those requirements matter. On 2026-08-21 the live Formal Conjectures front page displayed totals different from the supplied snapshot, and the live UnsolvedMath dataset card described a different row total from the bundled revision-specific workbook. The official Erdős Problems FAQ also says its status coverage is a work in progress and recommends an independent literature search. The Workbench must preserve such drift instead of silently choosing whichever number looks newest.

The previously replayed package's 858-row conservative queue is useful triage, not admission: Open Problem Garden 385, K3 189, Kourovka 118, Green 76, AMR 64, and Erdős 26. Of those rows, 832 have no reconciled `current_status`, 638 carry warning flags, and all retain an unresolved underlying-source provenance or reuse state. Its 2,076-row source-document manifest is almost entirely a link backlog and does not yet bind per-document acquisition dates, bytes, hashes, and licenses. A spot audit of the 17-row literature delta also found date, title, and author-metadata discrepancies. These are repair queues for a later reviewed generation, not evidence that a packet is ready to run.

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
6. Return that delta for peer review without changing the preserved source-list record or sending unreviewed model output directly to maintainers.

Status reconciliation is an accepted mathematical contribution. A stale “open” label, missed partial result, or ambiguous variant should be corrected only through exact sources and independent checking.

## Loop for a future runnable problem packet

The following loop applies only after a specific problem packet passes the admission requirements above.

1. Download and verify one bounded problem packet.
2. Audit its literature and current status before attempting progress.
3. Reproduce known computations or examples where possible.
4. Try one declared mathematical or computational attack within explicit limits.
5. Return one structured result class: no progress, reproduced result, failed path, counterexample search, sharper bound, new lemma, suspected proof, suspected refutation, or status correction.
6. Package all new code, data, evidence, checks, errors, and logs with exact provenance and a continuation cursor.
7. Require independent verification before promoting any mathematical claim.

Parallel attempts are allowed when declared. Record negative results and failed approaches so later contributors can avoid repeating them.

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

The packet format should support a tiny problem and an oversized problem, but not with the same completeness claim.

- A bounded Erdős entry may aim for exhaustive coverage of its maintained references plus one explicit supplementary search.
- A field-scale or famous problem must be split by time, formulation, method, or cited subcorpus. Its catalog row must say `sampled` or `partitioned`, list omitted strata, and reject any “complete literature” claim.
- An oversized Riemann Hypothesis entry is permitted, but it receives the same evidence, status, and independent-review rules as every other row.

## Expected package identity

The expected file is `Mathematical_Commons_Open_Problem_Workbench_v0.2_2026-08-21.zip`, 13,308,489 bytes, with SHA-256 `A087B8A9765476F7DC26B00280299153D3BE46A536C698035445AF723451BD2A`. Independent replay found 160 safe archive entries and matched all 159 payload entries against its self-excluding `MANIFEST.sha256`, with zero missing, extra, or hash-mismatched entries. Its internal validation report says PASS with 59 checks and zero failures.

Those facts describe the previously inspected source package, not a current public release. Publication remains incomplete until those exact bytes are restored, replayed again, uploaded, and anonymously read back.

The package reports 8,785 nonblank secondary statement candidates, 1,246 preliminary candidates, 858 mechanically conservative candidates, 824 statement-integrity review rows, 4,831 provenance/status/rights review rows, 2,076 source-document rows, 8,785 literature-query rows, 17 checked literature-delta rows, and 14 community leads. Its Erdős data contains 1,217 metadata records, including 608 classified as open in the snapshot, 556 with imported statement text, 52 statement gaps, and 76 status conflicts.

These counts support curation and review. They are not a unique-problem count, canonical-statement audit, current-status audit, complete literature review, or specialist mathematical review. Package validation establishes internal consistency only. The Erdős 68 example contains exact-rational computation and an intentionally incomplete Lean statement; it claims no proof.

## Requirements for a runnable problem packet

A problem becomes runnable only after a reviewed generation supplies:

1. a stable problem/variant/status schema;
2. a source-rights and acquisition manifest;
3. a claim-graph vocabulary;
4. bounded literature-search receipts;
5. deterministic packet and cumulative-handback builders;
6. explicit contribution/result-state schemas;
7. independent mathematical and computational review routes; and
8. one small Erdős test collection whose source and status replay passes.

Until those requirements pass for a specific problem, its row remains discovery or review material. Do not announce a conjecture result from an imported statement, literature lead, model output, or package-level PASS.
