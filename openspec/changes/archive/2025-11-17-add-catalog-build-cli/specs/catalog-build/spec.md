## ADDED Requirements

### Requirement: Build Catalog from Config
The system MUST provide a function to build or update a DuckDB catalog from a validated configuration.

#### Scenario: Catalog built from YAML config
- **GIVEN** a valid YAML config describing a DuckDB database path, attachments, Iceberg catalogs, and views
- **WHEN** `build_catalog(config_path)` is called
- **THEN** the system opens the configured DuckDB database (or `:memory:` if unspecified)
- **AND** applies pragmas, installs and loads extensions, sets up attachments and Iceberg catalogs
- **AND** creates or replaces all configured views.

#### Scenario: Idempotent catalog builds
- **GIVEN** a valid config and an existing DuckDB catalog file
- **WHEN** `build_catalog(config_path)` is run multiple times with the same inputs
- **THEN** the resulting catalog contains the same set of views with the same definitions
- **AND** no duplicate or unexpected views are created.

### Requirement: Dry-run SQL generation
The system MUST support generating the full set of `CREATE OR REPLACE VIEW` statements from a config without connecting to DuckDB.

#### Scenario: SQL generated without touching DB
- **GIVEN** a valid config file
- **WHEN** `build_catalog(config_path, dry_run=True)` is called
- **THEN** the system generates SQL for all views based on the config
- **AND** does not attempt to open a DuckDB connection
- **AND** returns or prints the generated SQL.

### Requirement: CLI Build Command
The CLI MUST expose a `build` command that applies a config to a DuckDB catalog file, with options for overriding the DB path, dry-run, and verbose logging.

#### Scenario: CLI build applies config
- **GIVEN** a valid config file path
- **WHEN** `duckalog build catalog.yaml --db-path my_catalog.duckdb` is executed
- **THEN** the command opens or creates `my_catalog.duckdb`
- **AND** applies the configuration to create or replace views
- **AND** exits with status code `0` on success.

#### Scenario: CLI build fails on engine error
- **GIVEN** a config with an invalid view or attachment that causes SQL execution to fail
- **WHEN** `duckalog build catalog.yaml` is executed
- **THEN** the command prints a clear error message
- **AND** exits with a non-zero status code.

### Requirement: CLI Generate-SQL Command
The CLI MUST expose a `generate-sql` command that validates the config and writes SQL to stdout or a specified file without connecting to DuckDB.

#### Scenario: SQL written to file
- **GIVEN** a valid config file path
- **AND** an output file path `create_views.sql`
- **WHEN** `duckalog generate-sql catalog.yaml --output create_views.sql` is executed
- **THEN** the command validates the config
- **AND** writes `CREATE OR REPLACE VIEW` statements for all views to `create_views.sql`
- **AND** does not connect to DuckDB.

### Requirement: CLI Validate Command
The CLI MUST expose a `validate` command that parses and validates a config (including env interpolation) and reports success or failure via exit code.

#### Scenario: Valid config returns success
- **GIVEN** a valid config file
- **WHEN** `duckalog validate catalog.yaml` is executed
- **THEN** the command prints a success message
- **AND** exits with status code `0`.

#### Scenario: Invalid config returns failure
- **GIVEN** a config with missing required fields or unresolved `${env:VAR}` placeholders
- **WHEN** `duckalog validate catalog.yaml` is executed
- **THEN** the command prints a descriptive error message
- **AND** exits with a non-zero status code.
