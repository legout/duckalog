## Why

The CLI is currently implemented with Click and exposed via the `duckdb-catalog` command. As the project scope grows (subcommands, shared options, async-friendly UX), managing Click contexts and decorators becomes cumbersome. Typer (built on Click but offering type hints, shared option handling, and nested app composition) will reduce boilerplate and align with the Python API style. At the same time, the new branding "Duckalog" should be reflected in the CLI entry point so users and documentation stay consistent.

## What Changes

- Replace the Click-based CLI (`duckdb-catalog`) with a Typer application while preserving the existing command set (`build`, `generate-sql`, `validate`).
- Rename the installed console script from `duckdb-catalog` to `duckalog` across packaging, docs, and tests.
- Update the `catalog-build` capability spec to explicitly require Typer usage and the new command name, ensuring future changes follow the same structure.

## Impact

- Developers gain stricter type checking and clearer command definitions, making additional subcommands easier to add.
- Users interact with the CLI through the `duckalog` command, matching the library name and reducing confusion.
- Documentation, tests, and automation referencing the CLI must be updated to the new entry point, but the functional behavior remains the same.
