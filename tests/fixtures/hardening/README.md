# Validator hardening fixtures

These fragments are intentionally invalid inputs for the validator's supported
JSON-Schema subset. They are never pilot records and are outside the default
record-discovery directories.

- `malformed-items.json` proves that a schema keyword's value shape is checked.
- `aliased-remote-ref.json` proves that an arbitrary URL cannot resolve merely
  because its basename matches a trusted local schema.
- `nested-quantifier-pattern.json` proves that unsafe nested regex quantifiers
  fail schema preflight.
