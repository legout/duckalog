# Change: Update config + secrets docs to match implementation

## Why
Several docs pages currently describe a configuration shape that does not match the implemented Pydantic models in `src/duckalog/config/models.py`:
- Secrets are documented as top-level `secrets:` and view-level `secrets_ref`, but the implementation uses `duckdb.secrets` and does not define `secrets_ref` on `ViewConfig`.
- The configuration schema reference includes fields that are not implemented (e.g. `materialized` on views).
This causes users to write configs that fail validation.

## What Changes
- Update documentation pages and examples to match the implemented config schema:
  - Secrets are defined under `duckdb.secrets`
  - No `secrets_ref` field is documented or used
  - `duckdb.settings` is documented in the form the implementation accepts (string or list of `SET ...` statements)
  - Remove documentation of non-existent fields (e.g. `views[].materialized`)
- Ensure all YAML examples shown in affected docs are schema-valid for the current `Config` model.

## Out of Scope
- Dashboard/UI documentation content and behavior descriptions (will be rewritten separately).

## Impact
- Affected documentation (non-exhaustive, scoped to schema/secrets correctness):
  - `docs/reference/config-schema.md`
  - `docs/examples/duckdb-secrets.md`
  - `docs/guides/usage.md` (secret-related sections only)
  - `docs/SECURITY.md` (secret-related examples)
  - `docs/explanation/architecture.md` (update schema references in diagrams/text)
- No code changes.
