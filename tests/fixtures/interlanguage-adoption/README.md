# Pinned interlanguage adoption fixture

This directory contains only the four-file machine-ingestion contract from exact upstream commit `5f41b18467c315aee5f465894dd85a277081c74e` of [`KokunoYumeto/modern-latex-manuscripts`](https://github.com/KokunoYumeto/modern-latex-manuscripts). It is committed so native CI validates the one production snapshot that the public adapter actually supports, rather than testing only generated lookalikes.

The exact byte lengths and SHA-256 identities are code-reviewed in `tools/interlanguage_adoption_pin.json`. The fixture contains metadata, a JSON Schema, a validation receipt, and a map-identity manifest. It contains no manuscript, scan, translation, or producer artifact.

The upstream repository dedicates its project-created metadata and manifests under CC0 1.0. Linked manuscripts, editions, scans, translations, and other third-party works retain their own rights; neither this fixture nor a passing test imports or relicenses them.
