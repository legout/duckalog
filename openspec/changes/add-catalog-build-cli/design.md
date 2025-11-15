## Overview

This design connects the new CLI + Python entry points to the reusable building blocks defined in other changes (`config`, `sql-generation`, `errors-logging`). The goal is to keep SQL generation and DuckDB execution flows well-factored so the CLI remains a thin wrapper while still supporting dry-run and verbose diagnostic modes.

```
config file -> load_config() -> Config
                             -> generate_all_views_sql() (dry-run)
                             -> build_catalog() -> DuckDB engine
```

## Key Components

1. **Config loader**: reuse `duckalog.load_config` for validation + env interpolation. This keeps CLI and Python API behavior in sync and ensures any CLI call fails early on schema issues.
2. **SQL generation**: reuse `generate_all_views_sql` for `generate-sql` CLI command and `build_catalog(..., dry_run=True)` to avoid duplicating logic.
3. **Engine module** (new): encapsulate DuckDB connection management, pragma execution, attachments, Iceberg catalog setup, and view creation. Exposed via `build_catalog()` in the Python API.
4. **CLI module**: wraps Click commands:
   - `build <config>` -> calls `build_catalog` (optionally overriding `db_path`, `dry_run`, `verbose`).
   - `generate-sql <config>` -> writes/prints output of `generate_all_views_sql(load_config(...))`.
   - `validate <config>` -> simply runs `load_config` (optionally `--no-duckdb` flag later).
5. **Error handling**: engine functions raise `ConfigError` (validation) or `EngineError` (DuckDB issues). CLI maps exceptions to exit codes per `errors-logging` spec. Verbose flag surfaces stack traces/debug logging.

## Execution Flow: `build_catalog`

1. `load_config(path)` → validated `Config`.
2. Resolve DuckDB path override: CLI `--db-path` or config `duckdb.database` default.
3. `with duckdb.connect(db_path)` context:
   - Apply `duckdb.install_extensions`, `load_extensions`, `pragmas` sequentially, surfacing failures as `EngineError`.
   - Call `setup_attachments(conn, config.attachments)` (DuckDB attaches, SQLite attaches, Postgres connectors) and `setup_iceberg_catalogs(conn, config.iceberg_catalogs)`.
4. Iterate `config.views` in order:
   - If `dry_run`, skip database work.
   - Else issue `CREATE OR REPLACE VIEW ...` using either raw SQL or `generate_view_sql(view)`.
5. On success return normally; CLI prints success message only in verbose mode.

## Execution Flow: `generate-sql`

1. `config = load_config(path)`.
2. `sql = generate_all_views_sql(config)`.
3. CLI writes to stdout or `--output` file (UTF-8 text). Pure function—no DuckDB.

## Execution Flow: `validate`

1. `load_config(path)`; failure raises `ConfigError`.
2. Optional `--with-duckdb` future flag might attempt DB connection, but MVP is config-only.

## Logging Strategy

- Use Python `logging` with module-level logger. CLI `--verbose` sets level to INFO; default is WARNING. Secrets (env interpolation outputs) never logged per `errors-logging` spec.
- Engine emits structured INFO messages for major steps (connecting, attachments, views) only when verbose.

## Error Mapping

- `ConfigError` → CLI exit code 2, message: `Config error: ...`.
- `EngineError` → exit code 3, message: `Engine error: ...`.
- Unexpected exceptions → exit code 1, optional stack trace if `--verbose`.

## Testing Strategy Alignment

- Unit tests for CLI command modules using Click test runner (simulate `build`, `generate-sql`, `validate`).
- Engine tests run against temporary DuckDB files (tmp_path) and minimal attachments (SQLite file). Use `dry_run` to test SQL path without DB.
- Snapshot tests for `generate-sql` command should reuse `generate_all_views_sql` to ensure CLI output matches python function.

## Future Extensions

- Additional CLI flags (e.g., `--catalog-only`, `--schema`) can hook into the same engine layer.
- Additional source types require only updates to `config` + `sql-generation`; this design keeps CLI untouched when possible.
