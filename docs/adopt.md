# Adopt work from the interlanguage archive

The practical job catalog contains ready-to-run source packets. A second, broader adoption board in [`modern-latex-manuscripts`](https://github.com/KokunoYumeto/modern-latex-manuscripts) describes active, partial, scattered, weak, source-only, and currently unworked author/work scopes that can be mirrored or checked.

The currently reviewed discovery snapshot is exact commit [`7a00b564ace8230c57309df2d66325e57d1c4043`](https://github.com/KokunoYumeto/modern-latex-manuscripts/tree/7a00b564ace8230c57309df2d66325e57d1c4043), tree `e3d53eb3216a2d6e99cce32a358ecd06377e3115`. It contains 78 bounded rows: 9 current, 64 ready for adoption, and 5 future. Ownership is non-exclusive; declared parallel mirrors are welcome.

## Exact machine interface

Fetch all four files from that same commit. Never mix revisions or treat floating `main` as an immutable snapshot.

| Role | Path | Bytes | SHA-256 |
|---|---|---:|---|
| Board | `manifests/adopt.json` | 151,030 | `2B81804831FDB030F1BBA81B07D2C9304D682E9F7D81DD6872A6DFDBA5452FDD` |
| Schema | `manifests/adopt.schema.json` | 32,255 | `42FD4B22961BF23F41E938368A394FBEDE64F22D08AE826FADD6BEBE0095DE6C` |
| Validation receipt | `manifests/adopt.check.json` | 16,330 | `BE5B38CF2C706FD554B90D0A592E79EBADC05DF22A2DC16ED5B04719D3946EAE` |
| Map manifest | `manifests/github-custody/maps-r8.json` | 8,051 | `15EAC635450D6DDCF8648453EEC19AAB5586C02A87539E6CEA28F277152445FF` |

The receipt reports `PASS`, `errors=[]`, 19/19 map identities replayed, and a 78-row human-board projection. A consumer still must human-approve the commit, verify all four bytes and hashes, validate the board against the same-commit schema, and inspect the referenced source/map evidence before starting work. The board is coordination metadata, not mathematical or translation certification.

### Exact-commit upstream helper

The approved snapshot already contains its generic consumer; Commons does not vendor a second schema compiler. At the same commit, `scripts/get-adopt.py` is 11,387 bytes / SHA-256 `BD45CC4D7845712A7609489CD48095E6931E87F2073115FD7E39AA6BBE8E62F2`, and its offline regression `scripts/test-adopt-offline.py` is 7,706 bytes / `F87A539BC1CAFA912CD78134EE173C4EAD428CBF761581E9AAB06D763D4BA537`.

After independently verifying the helper byte identity, a network consumer can require the same human-selected commit twice:

```console
python scripts/get-adopt.py --commit 7a00b564ace8230c57309df2d66325e57d1c4043 --approve 7a00b564ace8230c57309df2d66325e57d1c4043
```

For a fully materialized local clone, add `--git PATH_TO_REPOSITORY`; the helper reads exact Git objects, ignores working-tree bytes, and sets `GIT_NO_LAZY_FETCH=1`. That environment variable is a tested fail-closed request to Git, not an operating-system network sandbox, so enforce network isolation separately when categorical offline execution matters. The helper validates acquisition and the same-commit contract; it does not certify any row's mathematics, source, rights, or translation.

## Human views

- [Adoption board](https://github.com/KokunoYumeto/modern-latex-manuscripts/blob/7a00b564ace8230c57309df2d66325e57d1c4043/docs/adopt.md)
- [Author/work/language index](https://github.com/KokunoYumeto/modern-latex-manuscripts/blob/7a00b564ace8230c57309df2d66325e57d1c4043/docs/adopt-index.md)

Choose one bounded row, read its map and exact cursor, declare overlap, preserve all input/output identities, and return an inspectable result plus continuation cursor. If the row does not yet have a strict runnable packet, source recovery and packet construction are the first contribution—not an excuse to infer missing authority bytes.
