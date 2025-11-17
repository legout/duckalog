## Why

Users need a simple way to build, validate, and inspect DuckDB catalogs from configuration files, both from Python code and from the command line.

The PRD defines core use cases (`build`, `generate-sql`, `validate`) but there is no OpenSpec-backed description of how the engine and CLI should behave, including idempotency, error handling, and offline-friendly SQL generation.

## What Changes

- Introduce a `catalog-build` capability spec that defines:
  - The `build_catalog(config_path, db_path, dry_run, verbose)` Python API behavior.
  - How DuckDB connections are opened, extensions installed/loaded, and pragmas applied.
  - How attachments and Iceberg catalogs are set up before view creation.
  - How views are created or replaced based on validated config.
- Define CLI commands:
  - `duckalog build` for applying a config to a DuckDB file (with `--db-path`, `--dry-run`, `--verbose`).
  - `duckalog generate-sql` for writing `CREATE VIEW` SQL without touching the database.
  - `duckalog validate` for validating configs and environment interpolation without connecting to DuckDB by default.
- Specify idempotency, exit codes, and error reporting semantics for the core commands.

## Impact

- Provides a stable contract for how catalogs are built and validated, enabling predictable automation in CI/CD and data pipelines.
- Clarifies the responsibilities and boundaries between the Python API and CLI wrapper.
- Enables future changes (e.g., additional source types or new commands) to extend the `catalog-build` capability in a controlled way.
