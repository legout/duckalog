# Change: Harden UI config loading and safety guards

## Why
Running `duckalog ui` with a DuckDB database file (e.g., `product_analytics.duckdb`) currently crashes with a UTF-8 decode error because the UI treats any path as a text config. We need user-friendly validation and safer parsing to prevent binary file reads and improve schema lookup safety.

## What Changes
- Validate UI input path and fail fast on likely binary/db files with a clear message pointing to YAML/JSON configs.
- Add UnicodeDecodeError handling during config load with actionable guidance.
- Quote view names when describing schemas to avoid failures/injection from unquoted identifiers.
- Remove duplicate datastar import and trim minor UI boilerplate.

## Impact
- Affected capability: ui
- Code: `src/duckalog/ui.py` (config load, schema describe, imports)
- User UX: clearer errors when passing the wrong file, more robust schema endpoints.
