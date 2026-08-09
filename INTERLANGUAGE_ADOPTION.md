# Interlanguage archive adoption adapter

This is an **infrastructure-only integration on top of protected Phase A**. It makes the existing `modern-latex-manuscripts` archive board inspectable as a source of bounded transcription, translation, source-recovery, repair, and review work while the elementary calibration remains submitted and under review. It does not turn archive metadata into a live Research Packet, mathematical evidence, or an accepted result.

The adapter is intentionally one-way. Its validation application makes no HTTP/API request:

- a human chooses one exact upstream commit;
- the caller places four allowlisted JSON files on local, non-on-demand storage in a new private directory that is not being changed concurrently;
- the adapter binds each opened local handle to the inspected path and reads only those four files;
- all four bytestrings must match a code-reviewed pin;
- no URL, command, workflow label, note, or mirror declaration from the board is fetched or executed; and
- the output is a ranked set of inert coordination pointers for human inspection.

## Approved snapshot

The current approved snapshot is upstream commit [`5f41b18467c315aee5f465894dd85a277081c74e`](https://github.com/KokunoYumeto/modern-latex-manuscripts/tree/5f41b18467c315aee5f465894dd85a277081c74e), tree `ac9630785b2f8d0534c9e35da95f957538158a47`. Floating `main` is only a discovery locator. It is not an immutable snapshot and must not silently replace this commit.

| Role | Exact path | Bytes | SHA-256 |
|---|---|---:|---|
| Board | `manifests/adopt.json` | 62,952 | `24b2deab6684b4714d7a555c6c78c4ecf57b3df96829fd13441d2773491af678` |
| Draft 2020-12 schema | `manifests/adopt.schema.json` | 11,922 | `fb0539f375937bf5fc68fc45363b501b2733559ac54953f08b6ce21f5e139b9d` |
| Validation receipt | `manifests/adopt.check.json` | 2,536 | `6c665fe849214af638975eb8bba52e88d7f339c2706bb842566d997d514d014d` |
| Map manifest | `manifests/github-custody/20260807_maps_r5.json` | 17,998 | `ec0f2b625455efa88ffc3c376c46fad8024114f1f87819d776accf6837f1864d` |

The commit identities inside those files have different jobs and are deliberately not equal:

- approved four-file snapshot and human decision point: `5f41b18467c315aee5f465894dd85a277081c74e`;
- validation/content source recorded by the receipt: `2695dbfe84726329267c71ba7a0af3486435f4c8`;
- evidence closure: `9f30531f669fc7c62e1d512d4b2460921464727e`;
- board evidence basis: `9c858b61c57f0c7e7281c275e0bb9c6c0f999d53`; and
- archive-map observation recorded upstream: `61b9d5cab6441b8fa02e34630d7145a916f0ea37`.

Their ancestry and the human decision to approve `5f41b184…` are provenance assertions reviewed outside this four-file adapter. Exact file hashes prove byte equality to the reviewed snapshot; they do not prove Git ancestry by themselves. The optional human board `docs/adopt.md` is not a fifth machine requirement; when displayed or audited, pin its same-commit identity: 22,929 bytes, SHA-256 `341b4878e11436130f6c3481eb27775e2926afdba6500ed71f5a1fa15672b230`.

Two public receipts are also pinned as **non-input provenance**, not additional machine requirements: source readback `manifests/published-github/20260809_handback_rb.json`, 4,641 bytes, SHA-256 `1230fb8c16f79ecee057f7fa0269c5f27c71b4cca8522bfe436cba82d7dc327f`; and r19 link audit `manifests/github-custody/20260809_links_r19.json`, 10,293 bytes, SHA-256 `fe990865c2b21bce9487a5090c28bd5e580e7d99e657f3941b154a11102beb53`. They record the upstream source readback and 37-document/1,160-link/786-target audit. The adapter neither fetches nor treats them as substitutes for the four required files.

## Try it

Python 3.10 or newer on Windows or Linux is sufficient; the tool has no third-party dependency. Its stable opened-handle binding currently fails closed on other operating systems. The archive repository is many gigabytes, so do not download its full ZIP merely to inspect this 95 KB interface. The following PowerShell block acquires only the four fixed files from the exact approved commit into a new local directory:

```powershell
$SnapshotRoot = Join-Path ([IO.Path]::GetTempPath()) ('adoption-snapshot-5f41b184-' + [Guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path (Join-Path $SnapshotRoot 'manifests/github-custody') | Out-Null
$PinnedBase = 'https://raw.githubusercontent.com/KokunoYumeto/modern-latex-manuscripts/5f41b18467c315aee5f465894dd85a277081c74e'
Invoke-WebRequest "$PinnedBase/manifests/adopt.json" -OutFile (Join-Path $SnapshotRoot 'manifests/adopt.json')
Invoke-WebRequest "$PinnedBase/manifests/adopt.schema.json" -OutFile (Join-Path $SnapshotRoot 'manifests/adopt.schema.json')
Invoke-WebRequest "$PinnedBase/manifests/adopt.check.json" -OutFile (Join-Path $SnapshotRoot 'manifests/adopt.check.json')
Invoke-WebRequest "$PinnedBase/manifests/github-custody/20260807_maps_r5.json" -OutFile (Join-Path $SnapshotRoot 'manifests/github-custody/20260807_maps_r5.json')
python tools/validate_adoption_snapshot.py $SnapshotRoot --limit 10
```

The acquisition step uses network access only for four hard-coded exact-commit raw URLs. The adapter application itself makes no HTTP/API request and rejects even a syntactically valid mixed or altered download. Keep this new directory local, private, and unchanged while validation runs; on Windows the tool also rejects UNC or remote drives, links, junctions, reparse points, and on-demand files. A portable program cannot prove every operating-system mount or ACL property, so the private, non-concurrent directory is also an operator requirement.

On Linux, the equivalent bounded acquisition is:

```bash
SnapshotRoot="$(mktemp -d -t adoption-snapshot-5f41b184-XXXXXXXX)"
mkdir -p "$SnapshotRoot/manifests/github-custody"
PinnedBase='https://raw.githubusercontent.com/KokunoYumeto/modern-latex-manuscripts/5f41b18467c315aee5f465894dd85a277081c74e'
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

Machine-readable `--json` output repeats the approved commit and tree, the four exact input identities, the explicitly optional human-board identity, the two non-input public receipts, and the separate claim, handback, and consumer-helper interfaces. It still emits only candidate coordination data and creates no Commons record.

## What a PASS establishes

A PASS establishes that:

- the four local files are bounded ordinary files at the four fixed paths, opened through stable local handles after link/reparse/containment checks;
- each byte length and SHA-256 matches the reviewed pin, including the validation receipt itself;
- JSON is strict UTF-8/LF without BOM, duplicate keys, non-finite numbers, unsafe nesting, or trailing ambiguity;
- the exact schema bytes declare Draft 2020-12 and the adapter's compiled board/item/mirror semantics agree with that reviewed schema; the adapter does not claim to be a general-purpose JSON Schema engine;
- the exact item, mirror, lane, enum, date, HTTPS, terminal-safety, portable-path, and conditional contracts hold;
- item and mirror IDs are unique and mirror references resolve;
- the 46 rows partition as three current, 38 ready, and five future, with zero integrated mirrors;
- all 19 required archive maps and both queue sources have an operational row reference;
- the 122 declared repository-path references and all predecessor/current/evidence canonical manifest streams recompute;
- the claim and handback forms are separately machine-bound, while the optional human-board identity and its 46-row completeness remain sealed upstream assertions;
- the receipt says `PASS`, reports no errors, binds the observed board/schema/map bytes, and preserves every required check flag; and
- candidate projection is deterministic and makes no application HTTP/API request or record creation.

## What a PASS does not establish

The four files alone cannot prove that every referenced upstream path still exists, that all 19 map files or 31 evidence files have the bytes described by the map manifest, that a human actually approved a commit, or that an adoption-row description is mathematically or historically correct. The receipt's `122/122 tracked` value and human-board completeness are sealed upstream assertions; this adapter recomputes the 122 references but has no upstream Git object database with which to re-run that tracked-path check.

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

The upstream `scripts/get-adopt.py` is a separate network acquisition helper, not this offline validator. It requires a human-approved full commit and Python plus `jsonschema`; it defaults to the upstream repository but exposes a general `--repository owner/name` override, while its four contract paths are fixed. It rejects floating refs, approval or identity mismatch, schema failure, and mixed revisions, but carries no independent trust pin for a repository chosen by the caller. It cannot establish trust, signatures, Git ancestry, source correctness, rights, or mathematical validity, and it does not fetch the optional Markdown human board. The Commons quickstart uses explicit exact-commit raw downloads so the acquisition and validation boundaries stay visible.

## Current integration state

The adapter is deliberately independent of calibration acceptance. It preserves every protected Phase A scientific byte, passes through the normal cross-platform protected-review path, and may be used to inspect coordination candidates while the calibration awaits a qualified independent human review. The public coordination record is [issue 10](https://github.com/KokunoYumeto/mathematics-commons-pilot/issues/10). A returned archive handback can inform a later steward-created Research Packet, but it is not itself an operational or mathematical claim.
