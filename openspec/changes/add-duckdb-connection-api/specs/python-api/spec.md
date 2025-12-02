## ADDED Requirements
### Requirement: Connect to Existing DuckDB Catalog
The system SHALL provide a Python API function that creates a DuckDB connection to an existing DuckDB database created by Duckalog and returns the connection for query execution.

#### Scenario: User connects to previously built catalog
- **WHEN** a user calls `connect_to_catalog("catalog.yaml")` 
- **THEN** the function extracts the database path from the provided Duckalog configuration
- **AND** establishes a connection to that DuckDB database using duckdb.connect()
- **AND** returns the active DuckDB connection object
- **AND** the connection can be used directly for executing queries against the catalog views

#### Scenario: User connects to in-memory catalog
- **WHEN** a user calls `connect_to_catalog("config.yaml", in_memory=True)`
- **THEN** the function uses ":memory:" as the DuckDB database path
- **AND** establishes an in-memory DuckDB connection
- **AND** returns the in-memory connection for immediate use

#### Scenario: User connects with custom database path override
- **WHEN** a user calls `connect_to_catalog("catalog.yaml", database_path="custom.db")`
- **THEN** the function uses the specified database path instead of the one in the config
- **AND** establishes a connection to `custom.db`
- **AND** ignores the database path defined in the configuration

### Requirement: Connect to Catalog and Build in Single Operation
The system SHALL provide a Python API function that builds the DuckDB catalog from configuration AND returns a DuckDB connection to the resulting database in a single operation.

#### Scenario: User builds catalog and connects immediately
- **WHEN** a user calls `connect_and_build_catalog("catalog.yaml")`
- **THEN** the function first builds the DuckDB catalog from the provided configuration
- **AND** after successful catalog building, creates a DuckDB connection to the database
- **AND** returns the active connection object for immediate query execution
- **AND** the connection includes all views and attachments defined in the catalog

#### Scenario: Build and connect with custom output path
- **WHEN** a user calls `connect_and_build_catalog("catalog.yaml", database_path="analytics.db", output_path="s3://bucket/catalog.duckdb")`
- **THEN** the function builds the catalog and uploads it to the specified remote path
- **AND** establishes a connection to the local copy of the database (for metadata queries)
- **AND** returns the connection object for immediate use

#### Scenario: Dry run option for validation only
- **WHEN** a user calls `connect_and_build_catalog("catalog.yaml", dry_run=True)`
- **THEN** the function only validates the configuration without building
- **AND** does not create any database files or connections
- **AND** returns None or raises an error if validation fails

#### Scenario: Error handling during build phase
- **WHEN** a user calls `connect_and_build_catalog()` but the build fails
- **THEN** no connection is created
- **AND** the function raises an appropriate EngineError or ConfigError
- **AND** no database files are created or modified

### Requirement: Connection Lifecycle Management
Both connection functions SHALL provide clear guidance on connection lifecycle management and include automatic cleanup options.

#### Scenario: Context manager usage for automatic cleanup
- **WHEN** a user uses connect_to_catalog() as a context manager
- **THEN** the connection is automatically closed when exiting the with block
- **AND** resources are properly released without user intervention

#### Scenario: Manual connection management guidance
- **WHEN** a user uses direct connection return value
- **THEN** documentation explains proper connection closing patterns
- **AND** examples show both manual `conn.close()` and context manager usage

#### Scenario: Connection validation and metadata
- **WHEN** a connection is created to a DuckDB database
- **THEN** the function validates that the database exists and is a valid DuckDB file
- **AND** metadata about the connection (like database path) is returned or logged in verbose mode
- **AND** the connection state is ready for query execution

### Requirement: Integration with Existing APIs
The new functions SHALL integrate seamlessly with the current Duckalog API without breaking changes.

#### Scenario: Function reuses existing build_catalog logic
- **WHEN** connect_and_build_catalog() is called
- **THEN** it internally calls the existing build_catalog() function
- **AND** leverages all existing validation and engine logic
- **AND** uses the same error handling patterns as the current API

#### Scenario: Functions work with current configuration types
- **WHEN** users provide YAML or JSON configuration files
- **THEN** both functions accept the same input formats as build_catalog()
- **AND** environment variable interpolation works identically to existing behavior
- **AND** all DuckyDB pragmas, extensions, and secrets are properly applied

#### Scenario: Functions complement current Python API
- **WHEN** users are already using load_config() and other APIs
- **THEN** the new functions provide a natural progression in the workflow
- **AND** they can be used together with existing validation functions
- **AND** integrate seamlessly with the current API patterns