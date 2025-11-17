## Why

`docs/PRD_Spec.md` requires the engine to "error if a view references a non-existent catalog" for Iceberg views, but the current implementation only validates the shapes of `iceberg_catalogs` and `ViewConfig` and relies on DuckDB to fail later if an invalid catalog name is used.

This makes it harder to get fast, clear feedback during config validation and increases the risk of misconfigured Iceberg catalog names only surfacing at runtime.

## What Changes

- Introduce a change to the `config` / `catalog-build` specs that explicitly requires:
  - Every `ViewConfig` with `source: iceberg` and a `catalog` field to reference a catalog defined in `iceberg_catalogs`.
  - Config validation to fail early with a `ConfigError` (or engine setup with `EngineError`) if any view references a missing catalog.
- Update the engine implementation to perform this cross-reference check before executing any `iceberg_scan` calls.
- Tighten tests to cover:
  - Successful configs where all `catalog` references exist.
  - Failing configs where one or more Iceberg views reference undefined catalogs.

## Impact

- Moves a subtle runtime failure into a deterministic validation error.
- Aligns the implementation with the PRD requirement around Iceberg catalog reference integrity.
- Provides a clearer contract for future changes that add new catalog types or view source variations.

