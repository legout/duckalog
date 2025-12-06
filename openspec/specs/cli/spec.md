# cli Specification

## Purpose
TBD - created by archiving change add-config-init. Update Purpose after archive.

## Shared CLI Filesystem Options Architecture

### Requirement: Shared CLI Filesystem Options Handler
The CLI SHALL implement a centralized filesystem options handler that applies consistently across all commands that require remote filesystem access.

#### Rationale
Previously, filesystem-related CLI options (protocol, credentials, endpoints, etc.) were declared separately in each command (`build`, `generate-sql`, `validate`), leading to:
- Repeated option declarations with the same defaults and help text
- Duplicated logic for constructing filesystem objects from those options  
- Potential for behavior divergence between commands over time

#### Implementation
- A Typer application-level callback declares all filesystem options once
- The callback creates a filesystem object from provided options
- The filesystem object is stored in `ctx.obj["filesystem"]` for command access
- Individual commands retrieve the filesystem from context instead of handling options directly

#### Scope
- **Commands affected**: `build`, `generate-sql`, `validate` 
- **Options centralized**: `--fs-protocol`, `--fs-key`, `--fs-secret`, `--fs-token`, `--fs-anon`, `--fs-timeout`, `--aws-profile`, `--gcs-credentials-file`, `--azure-connection-string`, `--sftp-host`, `--sftp-port`, `--sftp-key-file`
- **Behavior preservation**: All existing CLI flags and semantics remain unchanged

#### User Impact
- No breaking changes to CLI surface
- Filesystem options now appear at application level in help output
- Commands have cleaner signatures without filesystem parameter clutter
- Consistent filesystem behavior across all commands
## Requirements
### Requirement: CLI Init Command
The CLI SHALL expose an `init` command that creates a new Duckalog configuration file.

#### Scenario: CLI creates YAML config file
- **WHEN** `duckalog init` is executed
- **THEN** a file named `catalog.yaml` is created in the current directory
- **AND** the file contains a valid, basic Duckalog configuration
- **AND** the command prints success message with file location

#### Scenario: CLI creates JSON config file
- **WHEN** `duckalog init --format json` is executed
- **THEN** a file named `catalog.json` is created in the current directory
- **AND** the file contains the same configuration structure as YAML but in JSON format
- **AND** the command prints success message with file location

#### Scenario: CLI creates custom filename
- **WHEN** `duckalog init --output my_config.yaml` is executed
- **THEN** a file named `my_config.yaml` is created with the configuration
- **AND** the command prints success message with the specified filename

#### Scenario: CLI handles file overwrite confirmation
- **WHEN** `duckalog init` is executed in a directory that already contains the target file
- **THEN** the command prompts for confirmation before overwriting
- **AND** with `--force` flag, the command overwrites without prompting
- **AND** with `--skip-existing` flag, the command skips creating the file

#### Scenario: CLI validates generated config
- **WHEN** `duckalog init` creates a configuration file
- **THEN** the generated file is immediately validated
- **AND** if validation fails, a `ConfigError` (inheriting from `DuckalogError`) is displayed and no file is created
- **AND** if validation succeeds, a success message is shown

### Requirement: CLI Init Command Options
The CLI init command SHALL support options for format, output path, and behavior customization.

#### Scenario: Format option support
- **WHEN** `duckalog init --format yaml` is executed
- **THEN** a YAML file is created (default behavior)
- **WHEN** `duckalog init --format json` is executed  
- **THEN** a JSON file is created
- **AND** invalid format values are rejected with a `ConfigError` (inheriting from `DuckalogError`)

#### Scenario: Output path options
- **WHEN** `duckalog init --output path/to/config.yaml` is executed
- **THEN** the configuration is created at the specified path
- **AND** parent directories are created if they don't exist
- **AND** relative paths are resolved relative to the current working directory

#### Scenario: Interactive mode support
- **WHEN** `duckalog init --interactive` is executed
- **THEN** the command prompts for basic customization options
- **AND** users can specify database name, view names, and other basic settings
- **AND** the generated config reflects the user's input choices

### Requirement: CLI Import Inspection
The Duckalog CLI MUST provide commands or options to inspect configuration imports without building a catalog.

#### Scenario: Show import graph
- **GIVEN** a catalog configuration that uses `imports` to pull in other files
- **WHEN** a user runs a CLI command such as `duckalog show-imports config.yaml`
- **THEN** the CLI SHALL display a tree or graph of imports starting from `config.yaml`
- **AND** the output SHALL include each imported file or URI at least once.

#### Scenario: Show merged configuration
- **GIVEN** a catalog configuration that uses imports
- **WHEN** a user runs a CLI command or option to preview the merged configuration
- **THEN** the CLI SHALL resolve all imports and output the resulting merged configuration or a clear summary of it
- **AND** the output SHALL reflect the same configuration that would be used by catalog build commands.

### Requirement: CLI Query Command
The CLI SHALL expose a `query` command for executing SQL queries against DuckDB catalogs.

#### Scenario: CLI query with explicit catalog path
- **WHEN** `duckalog query "SELECT COUNT(*) FROM users" --catalog catalog.duckdb` is executed
- **THEN** the command opens the specified catalog file in read-only mode
- **AND** executes the provided SQL query against the catalog
- **AND** displays results in a tabular format on stdout
- **AND** returns exit code 0 on successful execution

#### Scenario: CLI query with catalog discovery
- **WHEN** `duckalog query "SELECT COUNT(*) FROM users"` is executed without catalog flag
- **THEN** the command looks for `catalog.duckdb` in the current directory
- **AND** if found, executes the query against that catalog
- **AND** if not found, exits with error code 2 and clear error message

#### Scenario: CLI query with missing catalog
- **WHEN** `duckalog query "SELECT 1" --catalog missing.duckdb` is executed
- **THEN** the command exits with error code 2
- **AND** prints a clear error message indicating the catalog file was not found

#### Scenario: CLI query with invalid SQL
- **WHEN** `duckalog query "SELECT * FROM nonexistent_table" --catalog catalog.duckdb` is executed
- **THEN** the command exits with error code 3
- **AND** prints a clear SQL error message from DuckDB

#### Scenario: CLI query with no results
- **WHEN** `duckalog query catalog.duckdb "SELECT * FROM users WHERE id = 999"` returns no rows
- **THEN** the command prints "Query executed successfully. No rows returned."
- **AND** returns exit code 0

#### Implementation Requirements
- **Read-only access**: Catalog connections SHALL be opened in read-only mode
- **Tabular output**: Results SHALL be displayed in a clean, readable table format with borders and aligned columns
- **Error handling**: Clear error messages SHALL be provided for missing catalogs and SQL execution failures
- **Exit codes**: 
  - 0 for successful execution
  - 2 for catalog file access errors (not found, permission denied)
  - 3 for SQL execution errors
  - 1 for unexpected errors

