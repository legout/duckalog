# Proposal: Implement Secrets Creation in DuckDB Catalog

## Why
While Duckalog supports configuring DuckDB secrets through YAML/JSON configuration files (including validation, type hints, and environment variable interpolation), the secrets are **not actually being created in the DuckDB catalog**. The `_create_secrets()` function in `src/duckalog/engine.py` logs the configuration but does not execute `CREATE [PERSISTENT] SECRET` statements. This means users cannot verify secrets with `SELECT * FROM duckdb_secrets()` and persistent secrets don't survive database restarts, despite the configuration being fully supported and validated.

The configuration schema, tests, and specs all indicate that secrets should be functional, but the implementation has a TODO comment indicating it was deferred: "Implement actual CREATE SECRET when syntax is stable".

## What Changes
- **SQL Generation**: Add `generate_secret_sql()` function in `src/duckalog/sql_generation.py` to generate CREATE SECRET statements
- **Engine Execution**: Modify `_create_secrets()` in `src/duckalog/engine.py` to execute CREATE SECRET statements instead of just logging
- **Dry-Run Support**: Ensure CREATE SECRET statements appear in dry-run output
- **Testing**: Add integration tests to verify secrets are created in DuckDB and queryable
- **Validation**: Add unit tests for SQL generation function

## Impact
- **Affected specs**: catalog-build (modified to execute secrets), secrets-creation (new SQL generation capability)
- **User-facing**: Secrets will actually work with DuckDB - persistent secrets survive restarts, multiple scoped secrets enable automatic path-based selection
- **API**: New `generate_secret_sql()` function, `_create_secrets()` now executes instead of just logging
- **Breaking Changes**: None - this implements already-documented behavior that users expect to work
