# Interlanguage archive adoption adapter

This is an **infrastructure-only integration on top of protected Phase A**. It makes the existing `modern-latex-manuscripts` archive board inspectable as a source of bounded transcription, translation, source-recovery, repair, and review work while the elementary calibration remains submitted and awaits independent review. It does not turn archive metadata into a live Research Packet, mathematical evidence, or an accepted result.

The adapter is intentionally one-way. Its validation application makes no HTTP/API request:

- a human chooses one exact upstream commit;
- the caller places four allowlisted JSON files on local, non-on-demand storage in a new private directory that is not being changed concurrently;
- the adapter binds each opened local handle to the inspected path and reads only those four files;
- all four bytestrings must match a code-reviewed pin;
- no URL, command, workflow label, note, or mirror declaration from the board is fetched or executed; and
- the output is a ranked set of inert coordination pointers for human inspection.

## Approved snapshot

The current approved snapshot is upstream closure commit [`1ecde9651d5fa508c5a3c0056021bfa89c4ea888`](https://github.com/KokunoYumeto/modern-latex-manuscripts/tree/1ecde9651d5fa508c5a3c0056021bfa89c4ea888), tree `8962d9c5a74ed9758d9e551e0ac3da174aab16c0`. It supersedes the earlier `7f791dfb…` interface before that adapter was merged and closes the independently reported promisor-clone gap. Floating `main` is only a discovery locator. It is not an immutable snapshot and must not silently replace this commit.

| Role | Exact path | Bytes | SHA-256 |
|---|---|---:|---|
| Board | `manifests/adopt.json` | 81,818 | `37a58ce18133d99d7492753e795f146d6764611c88682c0ce813a3ea05035fb7` |
| Draft 2020-12 schema | `manifests/adopt.schema.json` | 17,236 | `9512088cc7a823c0470b0931e68a2bf1cf9095e94577288ba530c2c164ac3b9a` |
| Validation receipt | `manifests/adopt.check.json` | 5,005 | `4b45b540aa243d623737fcdeeedc4b8a60cbd1b4b8ff758627c263cb5ff35ee5` |
| Map manifest | `manifests/github-custody/20260807_maps_r5.json` | 17,998 | `ec0f2b625455efa88ffc3c376c46fad8024114f1f87819d776accf6837f1864d` |

The commit identities inside those files have different jobs and are deliberately not equal:

- approved four-file evidence closure and human decision point: `1ecde9651d5fa508c5a3c0056021bfa89c4ea888`;
- content/source state: `24fe25af7e593dee03280c46cf941ec6d83a4f84`, tree `cc8bbb2b79ae84125ab85e7713b86a53cf76cf03`;
- producer-recorded pre-commit validation context in `adopt.check.json`: `9a892452bba8f484ccef449c2d6d6dd49f05e41d`. That object is not publicly resolvable and is not in the public source-to-closure ancestry, so it is an opaque receipt datum rather than a trust anchor;
- board evidence basis: `9c858b61c57f0c7e7281c275e0bb9c6c0f999d53`; and
- archive-map observation recorded upstream: `61b9d5cab6441b8fa02e34630d7145a916f0ea37`.

Public Git ancestry independently places `7f791dfb…`, source `24fe25af…`, and closure `1ecde965…` in that exact order. The four contract blobs are byte-identical at source and closure. Exact file hashes prove equality to the reviewed snapshot but do not themselves prove ancestry or human approval. The optional human board `docs/adopt.md` is not a fifth machine requirement; when displayed or audited, pin its same-commit identity: 28,917 bytes, SHA-256 `006e210d24b79945543b46942a9230dd938705418a146eb80fe0ce7f6751e9c7`.

Two exact public receipts are pinned as **non-input provenance**, not additional machine requirements: claims/offline receipt `manifests/published-github/20260809_claims_offline_rb.json`, 7,154 bytes, SHA-256 `9085b14d5bfb872b0cbfd8c43929844ecbb124802bc1ebe50e81470f999b020a`; and source link audit `manifests/github-custody/20260809_links_r27.json`, 10,767 bytes, SHA-256 `96d6574817c13981d5c4f030d76039259103907bbdd2e264778126b0809f0f35`. The latter audits source commit `24fe25af…`—39 documents, 1,199 links, and 799 targets with no missing or prohibited target—not the later closure tree. The reported post-closure replay covers 1,203 links, but no separate pinned r28 receipt is claimed. Neither receipt certifies mathematical correctness, source correctness, or rights.

Three upstream programs are identified as **optional executable provenance**, never as machine inputs or trust anchors: `scripts/get-adopt.py`, 10,952 bytes / SHA-256 `0351d7c759ce8825e3dcdd7fb36b1ce29b58ff1e6676e7be07f660ab21edda15`; `scripts/test-adopt-offline.py`, 7,526 / `68f1cfee2af3d2fb74ca86b8bd9266ad026699809239d4a6a09cbd24122a0b74`; and `scripts/check-claims.py`, 13,596 / `100f8d72f2f6beedd979c69d99bfc519b8d19351e73ae01516b1e86bd32591b6`.

## Try it

Python 3.10 or newer on Windows or Linux is sufficient; the Commons tool has no third-party dependency. Its stable opened-handle binding currently fails closed on other operating systems. The archive repository is many gigabytes, so do not download its full ZIP merely to inspect this 122,057-byte interface. The following PowerShell block acquires only the four fixed files from the exact approved commit into a new local directory:

```powershell
$SnapshotRoot = Join-Path ([IO.Path]::GetTempPath()) ('adoption-snapshot-1ecde965-' + [Guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path (Join-Path $SnapshotRoot 'manifests/github-custody') | Out-Null
$PinnedBase = 'https://raw.githubusercontent.com/KokunoYumeto/modern-latex-manuscripts/1ecde9651d5fa508c5a3c0056021bfa89c4ea888'
Invoke-WebRequest "$PinnedBase/manifests/adopt.json" -OutFile (Join-Path $SnapshotRoot 'manifests/adopt.json')
Invoke-WebRequest "$PinnedBase/manifests/adopt.schema.json" -OutFile (Join-Path $SnapshotRoot 'manifests/adopt.schema.json')
Invoke-WebRequest "$PinnedBase/manifests/adopt.check.json" -OutFile (Join-Path $SnapshotRoot 'manifests/adopt.check.json')
Invoke-WebRequest "$PinnedBase/manifests/github-custody/20260807_maps_r5.json" -OutFile (Join-Path $SnapshotRoot 'manifests/github-custody/20260807_maps_r5.json')
python tools/validate_adoption_snapshot.py $SnapshotRoot --limit 10
```

The acquisition step uses network access only for four hard-coded exact-commit raw URLs. The adapter application itself makes no HTTP/API request and rejects even a syntactically valid mixed or altered download. Keep this new directory local, private, and unchanged while validation runs; on Windows the tool also rejects UNC or remote drives, links, junctions, reparse points, and on-demand files. A portable program cannot prove every operating-system mount or ACL property, so the private, non-concurrent directory is also an operator requirement.

On Linux, the equivalent bounded acquisition is:

```bash
SnapshotRoot="$(mktemp -d -t adoption-snapshot-1ecde965-XXXXXXXX)"
mkdir -p "$SnapshotRoot/manifests/github-custody"
PinnedBase='https://raw.githubusercontent.com/KokunoYumeto/modern-latex-manuscripts/1ecde9651d5fa508c5a3c0056021bfa89c4ea888'
curl --fail --location --proto '=https' --tlsv1.2 "$PinnedBase/manifests/adopt.json" --output "$SnapshotRoot/manifests/adopt.json"
curl --fail --location --proto '=https' --tlsv1.2 "$PinnedBase/manifests/adopt.schema.json" --output "$SnapshotRoot/manifests/adopt.schema.json"
curl --fail --location --proto '=https' --tlsv1.2 "$PinnedBase/manifests/adopt.check.json" --output "$SnapshotRoot/manifests/adopt.check.json"
curl --fail --location --proto '=https' --tlsv1.2 "$PinnedBase/manifests/github-custody/20260807_maps_r5.json" --output "$SnapshotRoot/manifests/github-custody/20260807_maps_r5.json"
python tools/validate_adoption_snapshot.py "$SnapshotRoot" --limit 10
```

If you already have those four files in their repository layout, point the adapter at that local root directly:

```powershell
python tools/validate_adoption_snapshot.py C:\path\to\snapshot --limit 10
```

The default view shows `ready_for_adoption` rows. Narrow it without changing the source snapshot:

```powershell
python tools/validate_adoption_snapshot.py C:\path\to\snapshot --query gauss
python tools/validate_adoption_snapshot.py C:\path\to\snapshot --all-lanes --language fr --priority high
python tools/validate_adoption_snapshot.py C:\path\to\snapshot --readiness review_ready --limit 20
python tools/validate_adoption_snapshot.py C:\path\to\snapshot --all-lanes --json
```

The production CLI has no `--pin` override and no download mode. Updating the approved snapshot requires a reviewed code-and-pin change, not a user-supplied checksum file.

Machine-readable `--json` output repeats the approved closure commit and tree, content-source role, qualified non-public validation-context datum, the four exact input identities, the explicitly optional human-board and three executable identities, both non-input receipts, board and issue transport modes, and the separate claim and handback interfaces. It still emits only candidate coordination data and creates no Commons record.

## What a PASS establishes

A PASS establishes that:

- the four local files are bounded ordinary files at the four fixed paths, opened through stable local handles after link/reparse/containment checks;
- each byte length and SHA-256 matches the reviewed pin, including the validation receipt itself;
- JSON is strict UTF-8/LF without BOM, duplicate keys, non-finite numbers, unsafe nesting, or trailing ambiguity;
- the exact schema bytes declare Draft 2020-12 and the adapter's compiled board/item/mirror semantics agree with that reviewed schema; the adapter does not claim to be a general-purpose JSON Schema engine;
- the exact item, mirror, lane, enum, date, HTTPS, terminal-safety, portable-path, and conditional contracts hold;
- the board, schema, and receipt agree on exactly two ordered upstream consumer modes, `raw_github` and `local_git_object_database`;
- the board, schema, and receipt bind the offline consumer regression path and the exact claim-auditor mode composition: board via `raw_github` or `local_git_object_database`, issues via `public_github_api` or `json_fixture`;
- item and mirror IDs are unique and mirror references resolve;
- the 46 rows partition as three current, 38 ready, and five future, with zero integrated mirrors;
- exactly the three current rows have named owners; the other 43 rows are explicitly unclaimed, and claims are non-exclusive;
- all 19 required archive maps and both queue sources have an operational row reference;
- the board and receipt co-bind exact declarations for the two queue files totaling 93,584 bytes;
- all 14 reusable workflow definitions have the exact eight-field contract, every item workflow token resolves, and no workflow is unused;
- the 133 declared repository-path references and all predecessor/current/evidence canonical manifest streams recompute;
- the claim and handback forms are separately machine-bound, while the optional human-board identity and its 46-row completeness remain sealed upstream assertions;
- the receipt says `PASS`, reports no errors, binds the observed board/schema/map bytes, and preserves every required check flag; and
- candidate projection is deterministic and makes no application HTTP/API request or record creation.

## What a PASS does not establish

The four files alone cannot prove that every referenced upstream path still exists, that the two queue-source files currently have their declared bytes, that all 19 map files or 31 evidence files have the bytes described by the map manifest, that a human actually approved a commit, or that an adoption-row description is mathematically or historically correct. The receipt's `133/133 tracked`, human-board/index completeness, queue-byte replay, label, and upstream-link results are sealed assertions. This Commons adapter validates their mutually bound declarations and recomputes the 133 references, but this four-file invocation has neither the extra source bytes nor an upstream Git object database with which to repeat those external checks.

The board is coordination metadata. Priority is queue ordering, ownership is non-exclusive scope coordination, and an empty `mirrors` array means no inspectable mirror has been integrated into that board—not that no outside work exists.

## From a board row to a contribution

1. Validate the exact snapshot and choose a bounded row.
2. Read its pinned archive map, source basis, next cursor, prerequisites, and rights notes.
3. Use the row's claim form to declare a proposed scope. Parallel work is allowed; declare overlap instead of pretending it does not exist.
4. Work in a fork or mirror with exact source identities, bounded page/work ownership, a logbook, and separate production and checking passes.
5. Use the separate handback form to return an inspectable result, partial checkpoint, pause, or withdrawal with exact outputs, checks, continuation cursor, and reusable method findings; a claim is not a handback.
6. If the work is also proposed to the Mathematics Commons, a steward must separately create the appropriate source/problem and Research Packet history under the Commons rights, privacy, resource, and independent-review gates.

No adapter command promotes a row into `packets/`, imports third-party manuscript bytes, grants redistribution rights, or accepts mathematics. Linked manuscripts and editions retain their own rights. Commons-originated metadata and workflow contributions remain CC0 modulo those pre-existing rights. Native CI carries the exact four-file production fixture under the upstream CC0 metadata dedication; it contains no manuscript bytes.

## Upstream helper boundary

The upstream `scripts/get-adopt.py` is a separate acquisition and validation helper, not the Commons validator. It requires the same explicit 40-hex commit twice, Python, and `jsonschema`; raw-GitHub mode also requires network access. It defaults to the upstream repository but exposes a general `--repository owner/name` override, while its four contract paths are fixed. Repetition is not cryptographic attestation, and the helper carries no independent trust pin for a repository chosen by the caller.

The reviewed helper also exposes a local Git-object mode. Execute only the exact 10,952-byte helper identified above from commit `1ecde965…`, after verifying its SHA-256; never execute a helper silently taken from floating `main`.

```console
cmd /d /s /c "python scripts/get-adopt.py --commit 1ecde9651d5fa508c5a3c0056021bfa89c4ea888 --approve 1ecde9651d5fa508c5a3c0056021bfa89c4ea888 --git C:\path\to\fully-materialized-repository > board.json"
```

Use a checkout or bare-repository root, not a linked-worktree `.git` indirection file. The `cmd.exe` wrapper preserves the helper's binary stdout on Windows; native-output redirection in Windows PowerShell 5.1 and older PowerShell 7 releases can transcode it, so do not use an unqualified `> board.json` there. The helper reads the four fixed `commit:path` blobs and ignores dirty or untracked working-tree bytes. Every local Git subprocess sets `GIT_NO_LAZY_FETCH=1`. The exact pinned regression independently passed against an unreachable promisor remote: a missing blob failed, made no remote attempt, and the fully materialized four-blob case reproduced all 122,057 bytes. This is a tested fail-closed Git contract, not an operating-system network sandbox; strict offline operation still requires a Git build that honors the variable, local materialization of all four blobs, and an operator-controlled network boundary where categorical isolation matters.

Board acquisition and issue-state auditing are separate transport choices. A fully offline upstream claim audit requires both local board transport (`--git`) and a local issue fixture (`--issues-file`); combining `--git` with the public GitHub issue API is not offline. The Commons validator itself neither invokes these scripts nor reads issue state.

The helper rejects floating refs, approval or identity mismatch, schema failure, and mixed revisions. It does not fetch the human docs, queue-source bytes, issue/claim state, producer artifacts, signatures, or complete repository history, and it does not recrawl every map target. It cannot establish human approval, trust, source correctness, rights, or mathematical validity. Its output is not a Commons Research Packet. The Commons quickstart keeps acquisition and local four-file validation visibly separate.

## Current integration state

The adapter is deliberately independent of calibration acceptance. It preserves every protected Phase A scientific byte, passes through the normal cross-platform protected-review path, and may be used to inspect coordination candidates while the calibration awaits a qualified independent human review. The public coordination record is [issue 10](https://github.com/KokunoYumeto/mathematics-commons-pilot/issues/10). A returned archive handback can inform a later steward-created Research Packet, but it is not itself an operational or mathematical claim.
