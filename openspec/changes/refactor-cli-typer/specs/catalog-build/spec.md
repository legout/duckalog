## MODIFIED Requirements

### Requirement: CLI Build Command
The CLI MUST expose a Typer-based application named `duckalog` that applies configs to DuckDB catalogs.

#### Scenario: Command name reflects product branding
- **GIVEN** the project is installed via pip
- **WHEN** a user runs `duckalog build catalog.yaml`
- **THEN** the Typer app executes the existing build workflow
- **AND** legacy `duckdb-catalog` references are deprecated in docs/tests.

#### Scenario: Typer enforces typed options
- **GIVEN** the CLI is implemented with Typer
- **WHEN** command handlers are defined
- **THEN** positional arguments and options are type-annotated (e.g., `Path`, `Optional[str]`)
- **AND** Typer generates help text consistent with those annotations.

### Requirement: CLI Generate-SQL Command
`duckalog generate-sql` MUST validate configs and emit SQL without connecting to DuckDB.

#### Scenario: Shared verbose option per command
- **GIVEN** each Typer subcommand accepts a `--verbose` flag
- **WHEN** `duckalog generate-sql --verbose` or `duckalog build --verbose` is executed
- **THEN** the verbose flag enables INFO-level logging for that command without requiring duplicate plumbing.

### Requirement: CLI Validate Command
`duckalog validate` MUST parse configs, interpolate env vars, and exit non-zero on errors.

#### Scenario: Tests reference new command name
- **GIVEN** automated tests or documentation examples
- **WHEN** they invoke the CLI
- **THEN** they use `duckalog ...` rather than `duckdb-catalog ...` to avoid divergence.
