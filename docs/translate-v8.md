# Translation starter v8

Publication checkpoint: `translate-v8` is prepared on the maintenance branch. The tag, asset, and anonymous readback will be recorded here immediately after remote publication.

Release asset: `translation-starter-v8.zip`, 16,580 bytes, SHA-256 `EA600BCA211224902C80AC0B1D235383A8E9748A6D3A8156611AC291E41C4429`.

The checked-in asset manifest is [`catalog/assets/translate-v8.json`](../catalog/assets/translate-v8.json); it records 12 source files / 60,777 bytes and the per-member hashes.

The ZIP contains the current work/language catalog and the local/web translation workflow. It contains no textbook, source work, or completed translation. The catalog is non-exclusive: choose a work outside maintained project lanes, choose a target language and written standard, read its distribution class and note, then acquire the exact source and return cumulative checkpoints.

The distribution labels are descriptive:

- `open_license`: an open license is named; follow attribution, ShareAlike, component, and notice terms.
- `noncommercial_only`: the recorded source note limits distribution to non-commercial use; this package is not for commercial distribution.
- `mixed_components`: the source combines components with different or incomplete terms; preserve each named notice.
- `terms_unclassified`: the current catalog does not normalize the terms.
- `reference_only`: the row is a reference or component, not a standalone translation job.

Use `LOCAL.md` or `WEB.md` to start. The workflow returns `SOURCE_INTAKE`, `IN_PROGRESS`, or `COMPLETE` with a cumulative package, exact cursor, and manifest after every bounded unit. A missing source is recorded as the next acquisition step; it is not silently treated as a missing translation.

The older [`translate-v7`](https://github.com/KokunoYumeto/mathematics-commons-pilot/releases/tag/translate-v7) release remains immutable history. Use v8 for the current wording and catalog projection.
