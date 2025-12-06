# Change: Add CLI Query Command

## Why
Users following the getting-started and examples guides are instructed to run commands such as:

- `duckalog query "SELECT COUNT(*) FROM users"`
- `duckalog query catalog.duckdb "SELECT * FROM active_users LIMIT 5"`

However, the CLI does not currently provide a `query` command. This gap is confusing for new users (the documented "next steps" fail) and makes it harder to quickly inspect a built catalog without writing a separate Python script or opening DuckDB manually.

Providing a first-class `duckalog query` command will:

- Align the CLI with existing documentation and examples.
- Make it easy to run ad‑hoc, read‑only SQL queries against an existing DuckDB catalog.
- Improve the interactive "getting started" experience by closing the loop from config → build → query.

## What Changes
- **New CLI command**: Add `duckalog query` to execute SQL against an existing DuckDB catalog file and print results to stdout.
  - Support an optional positional catalog path: `duckalog query [CATALOG_PATH] "SELECT ..."`:
    - If `CATALOG_PATH` is provided, open that DuckDB file.
    - If `CATALOG_PATH` is omitted, look for a sensible default in the current directory (e.g., `catalog.duckdb`) and fail with a clear error if no catalog can be found.
  - Treat the SQL argument as a single string parameter required for the command.
- **Output behavior**:
  - Execute the SQL in a DuckDB connection and render results in a human‑readable tabular format on stdout.
  - Return exit code `0` when the query runs successfully and a non‑zero code on errors.
- **Error handling**:
  - Clear errors when the catalog file cannot be opened or does not exist.
  - Clear errors when SQL execution fails (e.g., referencing a missing view).
- **Specs**:
  - Extend the `cli` spec with a new requirement describing the query command, its arguments, success behavior, and failure modes.

## Impact
- **Affected specs**:
  - `specs/cli/spec.md` (new `CLI Query Command` requirement).
- **Affected code**:
  - `src/duckalog/cli.py`: Add a new `query` command wired into the existing Typer app.
- **User experience**:
  - Examples and getting-started flows that currently reference `duckalog query` become accurate.
  - Users can quickly inspect catalogs and example views without opening a separate DuckDB shell.
- **Breaking changes**:
  - None. The `query` command is new and does not change existing commands or options.

## Risks and Trade-offs
- **Result formatting**:
  - A simple tabular text output is sufficient for an initial version; richer formatting (paging, JSON output) can be considered in follow-up changes if needed.
- **Catalog discovery heuristics**:
  - Defaulting to a local `catalog.duckdb` file in the current directory is intuitive for examples but may not match all production setups.
  - The spec will emphasize that providing an explicit catalog path is the recommended and deterministic usage, while implicit discovery is a convenience for quickstarts and tutorials.

