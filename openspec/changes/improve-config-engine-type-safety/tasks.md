# Improve Config and Engine Type Safety – Tasks

## 1. Spec Updates

- [x] 1.1 Review `openspec/specs/config/spec.md` and the existing attachment and SQL file requirements.
- [x] 1.2 Review `openspec/specs/catalog-build/spec.md` to understand current expectations for engine attachment setup.
- [x] 1.3 Add `config` spec deltas to:
  - Clarify that optional SQL file references and nullable strings MUST be safely handled (checked before use and surfaced as configuration errors when missing).
- [x] 1.4 Add `catalog-build` spec deltas to:
  - Clarify that engine attachment logic MUST respect the declared attachment models and avoid assuming attributes that are not present for a given attachment type.

## 2. Config Module Changes

- [x] 2.1 Update `duckalog.config` so that:
  - Optional SQL file references are checked for `None` before accessing `.path`.
  - Optional strings are normalized or guarded before calling string methods like `.strip()`.
- [x] 2.2 Replace invalid type references such as `duckalog.config.SQLFileLoader` with valid type annotations (imported `SQLFileLoader` or string forward references).
- [ ] 2.3 Add or update unit tests to cover:
  - Missing SQL file references.
  - Optional string fields that may be `None` but are used in trimming/normalization logic.

## 3. Engine Module Changes

- [x] 3.1 Refine attachment-related types in `duckalog.engine`:
  - Use a union, protocol, or common base type that accurately reflects the attributes used in the engine.
  - Ensure assignments of `SQLiteAttachment` and `PostgresAttachment` are compatible with the declared types.
- [x] 3.2 Update attachment setup logic to branch correctly on attachment type where needed, so that attribute access is safe and clear.
- [ ] 3.3 Add or extend tests that exercise:
  - DuckDB, SQLite, and Postgres attachments through the engine path.
  - Error scenarios where attachment configuration is invalid or incomplete.

## 4. Validation

- [x] 4.1 Run `uv run mypy src/duckalog` and ensure the config/engine-related errors are resolved.
- [ ] 4.2 Run the `Tests` GitHub workflow to confirm that type changes do not break runtime behavior.
