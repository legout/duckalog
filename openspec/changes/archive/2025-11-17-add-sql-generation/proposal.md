## Why

The project needs a clear, testable contract for how view definitions in the config are turned into `CREATE OR REPLACE VIEW` SQL, including quoting, option rendering, and support for all source types.

This behavior is currently only described in `docs/PRD_Spec.md` as conceptual Python functions, which makes it harder to evolve SQL generation, add new sources, or ensure consistent behavior between Python API and CLI.

## What Changes

- Introduce a `sql-generation` capability spec that defines:
  - Utility helpers for identifier quoting and option rendering.
  - `generate_view_sql(view: ViewConfig) -> str` for all supported source types and raw SQL views.
  - `generate_all_views_sql(config: Config) -> str` including optional header comments.
- Specify how `options` maps are rendered into function arguments for `*_scan` calls, including handling of strings, booleans, and numbers.
- Clarify that SQL generation is pure (no I/O) and deterministic for a given config.

## Impact

- Provides a stable contract for SQL emitted by both the CLI (`generate-sql`, `build --dry-run`) and any Python callers.
- Enables snapshot-style SQL tests that are resilient to future refactors of the SQL generation code.
- Makes it easier to add new sources or adjust scan function names in future changes via well-scoped spec updates.

