# Pinned interlanguage adoption fixture

This directory contains only the four-file machine-ingestion contract from exact upstream closure commit `1ecde9651d5fa508c5a3c0056021bfa89c4ea888` of [`KokunoYumeto/modern-latex-manuscripts`](https://github.com/KokunoYumeto/modern-latex-manuscripts). It supersedes the earlier `7f791dfb…` fixture before publication and is committed so native CI validates the one production snapshot that the public adapter actually supports, rather than testing only generated lookalikes.

The exact byte lengths and SHA-256 identities are code-reviewed in `tools/interlanguage_adoption_pin.json`. The 122,057-byte fixture contains coordination metadata, a JSON Schema, a validation receipt, and a map-identity manifest. Its queue-source hashes, workflow registry, human-index declarations, ownership semantics, consumer/offline-regression bindings, and board/issue audit modes are metadata inside that contract; the fixture does not include the queue documents themselves, any manuscript, scan, translation, or producer artifact.

The upstream repository dedicates its project-created metadata and manifests under CC0 1.0. Linked manuscripts, editions, scans, translations, and other third-party works retain their own rights; neither this fixture nor a passing test imports or relicenses them.
