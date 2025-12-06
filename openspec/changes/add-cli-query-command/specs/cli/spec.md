## ADDED Requirements
### Requirement: CLI Query Command
The CLI SHALL expose a `query` command that executes SQL against an existing DuckDB catalog file and prints results to stdout.

#### Scenario: Query against default catalog in current directory
- **GIVEN** a DuckDB catalog file named `catalog.duckdb` exists in the current working directory and contains a view `users`
- **WHEN** `duckalog query "SELECT COUNT(*) FROM users"` is executed
- **THEN** the command opens `catalog.duckdb`
- **AND** executes the query against that catalog
- **AND** prints the result in a human-readable tabular format to standard output
- **AND** exits with status code `0`.

#### Scenario: Query with explicit catalog path
- **GIVEN** an existing DuckDB catalog file at `artifacts/analytics.duckdb` that contains a view `daily_metrics`
- **WHEN** `duckalog query artifacts/analytics.duckdb "SELECT * FROM daily_metrics LIMIT 5"` is executed
- **THEN** the command opens `artifacts/analytics.duckdb`
- **AND** executes the provided SQL against that catalog
- **AND** prints the result rows in a human-readable tabular format to standard output
- **AND** exits with status code `0`.

#### Scenario: Missing catalog file returns clear error
- **GIVEN** no DuckDB catalog file exists at the requested path
- **WHEN** `duckalog query missing.duckdb "SELECT 1"` is executed
- **THEN** the command prints a clear error message indicating that the catalog file could not be found or opened
- **AND** no query is executed
- **AND** the command exits with a non-zero status code.

#### Scenario: Invalid SQL returns clear error
- **GIVEN** a DuckDB catalog file `catalog.duckdb` exists but does not contain a view named `nonexistent_view`
- **WHEN** `duckalog query catalog.duckdb "SELECT * FROM nonexistent_view"` is executed
- **THEN** the command prints a clear error message derived from the underlying DuckDB error
- **AND** no partial or misleading results are printed
- **AND** the command exits with a non-zero status code.

