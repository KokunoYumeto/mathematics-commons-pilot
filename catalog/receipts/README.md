# Public audit projections

These files make the packet-admission audits inspectable without publishing machine-specific absolute paths. The original producer receipts remain unchanged outside this repository. `catalog/job-meta.json` and `catalog/jobs.json` bind both the original receipt identity and the public projection identity.

| Public file | Original bytes / SHA-256 | Public bytes / SHA-256 | Minimal transformation |
|---|---:|---:|---|
| `global.json` | 83,290 / `B22C68D85FE74B61680BD98877235038EC39B1AB92A467BAE74F74C1721FD9DA` | 81,598 / `F3FCA45C79995C3EE595DC65B22E319A0F4C629267B7AB2821C3875F60B5F3EF` | Replaced the exact private audit-root prefix in `source_audit_tsv` with `<AUDIT_ROOT>`; normalized the derived JSON projection from mixed/CRLF line endings to UTF-8 LF without BOM. |
| `gordan2.txt` | 1,805 / `872FA5281555852C8069C0ABB9E4B581DB968E837AAA2ED7F5DBD92BE5977A34` | identical | None; the source sidecar was already path-neutral. |
| `mikami.json` | 6,599 / `9C82EFB21623C85D6FCC55424EFEACC12023E68BE7B22826723A48959ED2D99F` | 6,143 / `313587214FF5FFA6EF76518E429451B2EEE0398E14C9A5F8795180A33E1BCF3A` | Replaced the exact private packet-root prefix in three fields with `<PACKET_ROOT>` and the exact private source-custody prefix in two fields with `<SOURCE_CUSTODY>`. |

No status, count, hash, mismatch, blocker, mathematical, or packet-content field was changed.
