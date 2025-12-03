# errors-logging Specification

## Purpose
Define consistent exception handling patterns and logging behavior for Duckalog, ensuring all errors are properly categorized, logged, and propagated with appropriate context.

## Exception Hierarchy

### Requirement: Standardized Exception Types
The system MUST use a consistent exception hierarchy based on `DuckalogError` as the base class for all library exceptions.

#### Exception Hierarchy:
- `DuckalogError`: Base exception for all Duckalog-specific errors
- `ConfigError(DuckalogError)`: Configuration-related errors
- `EngineError(DuckalogError)`: Catalog build/engine errors
- `RemoteConfigError(ConfigError)`: Remote configuration loading errors
- `SQLFileError(DuckalogError)`: SQL file loading/parsing errors

#### Scenario: Exception inheritance and usage
- **GIVEN** a failure occurs in the Duckalog library
- **WHEN** the error is raised
- **THEN** it MUST inherit from `DuckalogError` and include:
  - A clear, descriptive error message
  - Original exception context when wrapping lower-level errors
  - Proper exception chaining using `raise ... from exc`

### Requirement: Error Context and Logging
All exceptions MUST be logged with appropriate context and MUST preserve the original exception chain.

#### Scenario: Exception wrapping with context
- **GIVEN** a lower-level exception occurs (e.g., file not found, network error)
- **WHEN** it is caught and re-raised as a domain-specific exception
- **THEN** the system MUST:
  - Log the error with context using the logging utilities
  - Raise the appropriate `DuckalogError` subclass
  - Preserve the original traceback using `from exc`
  - Provide a clear message about what operation failed
## Requirements
### Requirement: Error Types and Responsibilities
The system MUST distinguish configuration-time failures from runtime/engine failures using dedicated exception types.

#### Scenario: ConfigError for invalid configuration
- **GIVEN** a config file that is missing required fields, has parse errors, or contains unresolved `${env:VAR}` placeholders
- **WHEN** the configuration is loaded or validated
- **THEN** a `ConfigError` (inheriting from `DuckalogError`) is raised with a message that indicates the nature of the configuration problem.

#### Scenario: EngineError for DuckDB or attachment failures
- **GIVEN** a valid configuration
- **AND** a failure occurs while opening DuckDB, attaching a database, configuring an Iceberg catalog, or executing a view SQL statement
- **WHEN** the catalog build is attempted
- **THEN** an `EngineError` (inheriting from `DuckalogError`) is raised that wraps the underlying exception and includes context about which operation failed.

#### Scenario: SQLFileError for SQL processing failures
- **GIVEN** a SQL file that cannot be loaded, parsed, or processed
- **WHEN** attempting to load or execute the SQL file
- **THEN** a `SQLFileError` (inheriting from `DuckalogError`) is raised with a message indicating the specific SQL file and nature of the failure.

#### Scenario: RemoteConfigError for remote configuration failures
- **GIVEN** a remote configuration source that is unreachable or returns invalid data
- **WHEN** attempting to load remote configuration
- **THEN** a `RemoteConfigError` (inheriting from `ConfigError`) is raised with context about the remote source and failure reason.

### Requirement: Error Handling Patterns
All code MUST use consistent error handling patterns that avoid bare `except Exception` blocks and ensure proper exception chaining.

#### Scenario: Wrapping lower-level exceptions
- **GIVEN** a lower-level exception occurs during a Duckalog operation
- **WHEN** the exception is caught
- **THEN** the code MUST:
  - Use targeted exception types where possible, OR
  - Catch `Exception as exc:` and log context using logging utilities
  - Raise an appropriate `DuckalogError` subclass with `from exc`
  - Avoid silent `pass` blocks except in explicitly documented fallback cases

### Requirement: CLI Error Handling and Exit Codes
CLI commands MUST surface errors with clear messages and appropriate exit codes.

#### Scenario: Validate command fails on invalid config
- **GIVEN** an invalid config file
- **WHEN** `duckalog validate` is executed
- **THEN** the command prints a message indicating the config is invalid
- **AND** exits with a non-zero status code.

#### Scenario: Build command fails on engine error
- **GIVEN** a configuration that passes validation
- **AND** a failure occurs during catalog build (e.g. invalid SQL, attachment failure)
- **WHEN** `duckalog build` is executed
- **THEN** the command prints a clear error message derived from the `EngineError`
- **AND** exits with a non-zero status code.

### Requirement: Logging Levels and Secret Handling
Logging MUST use a centralized Duckalog logging abstraction backed by `loguru`, and MUST avoid exposing secrets at INFO level.

#### Scenario: High-level INFO logs via loguru-backed abstraction
- **GIVEN** logging is configured at INFO level via the Duckalog logging utilities
- **WHEN** a catalog build or validation runs
- **THEN** logs include high-level events such as "loading config", "connecting to DuckDB", "setting up attachments", and "creating view X"
- **AND** do not include full connection strings or secret values.

#### Scenario: DEBUG logs with redaction using loguru
- **GIVEN** logging is configured at DEBUG level via the Duckalog logging utilities
- **WHEN** a catalog build or validation runs
- **THEN** logs MAY include detailed information such as generated SQL or attachment parameters
- **BUT** any values derived from environment variables intended as secrets (e.g. passwords, access keys, tokens) MUST be redacted or omitted before being passed to the underlying `loguru` logger.

### Requirement: Centralized Logging Abstraction
All Duckalog internal modules MUST emit logs via a centralized logging abstraction, rather than importing the stdlib `logging` module directly for application logging.

#### Scenario: Core modules use logging utilities
- **GIVEN** a core module such as the engine, config validators, or CLI implementation
- **WHEN** it needs to emit log messages about progress, configuration, or errors
- **THEN** it uses the Duckalog logging utilities (e.g. `get_logger`, `log_info`, `log_debug`, `log_error`)
- **AND** does not configure or invoke the stdlib `logging` module directly for those messages.

### Requirement: Print Usage for User-Facing Output
Library code SHOULD log progress and debug information through the logging abstraction, and MUST avoid using `print()` for internal diagnostics.

#### Scenario: Library progress output
- **GIVEN** a library function that previously used `print()` to emit progress or debug information (e.g. number of views or records)
- **WHEN** the function is executed
- **THEN** it emits those messages via the centralized logging abstraction at an appropriate level (INFO or DEBUG)
- **AND** reserves `print()` only for explicitly specified user-facing CLI output where required by other specs.

### Requirement: Unified Exception Hierarchy and Chaining
Duckalog MUST expose a unified exception hierarchy for configuration, engine, and remote‑config errors, and MUST preserve underlying tracebacks via exception chaining.

#### Scenario: Exceptions derive from DuckalogError
- **GIVEN** operations that can fail due to configuration issues, engine failures, remote loading problems, or SQL file errors
- **WHEN** such a failure occurs
- **THEN** the system raises a domain‑specific exception such as `ConfigError`, `EngineError`, `RemoteConfigError`, or `SQLFileError`
- **AND** each of these exception types is a subclass of a common `DuckalogError` base class.

#### Scenario: Underlying errors are chained and logged
- **GIVEN** a lower‑level library error (for example, a DuckDB exception or filesystem error) during Duckalog operations
- **WHEN** the error is surfaced to callers
- **THEN** Duckalog logs the failure with relevant context
- **AND** raises an appropriate `DuckalogError` subclass using `raise ... from exc` so that callers can inspect the original cause.

