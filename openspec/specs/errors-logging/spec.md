# errors-logging Specification

## Purpose
TBD - created by archiving change add-error-and-logging. Update Purpose after archive.
## Requirements
### Requirement: Error Types and Responsibilities
The system MUST distinguish configuration-time failures from runtime/engine failures using dedicated exception types.

#### Scenario: ConfigError for invalid configuration
- **GIVEN** a config file that is missing required fields, has parse errors, or contains unresolved `${env:VAR}` placeholders
- **WHEN** the configuration is loaded or validated
- **THEN** a `ConfigError` is raised with a message that indicates the nature of the configuration problem.

#### Scenario: EngineError for DuckDB or attachment failures
- **GIVEN** a valid configuration
- **AND** a failure occurs while opening DuckDB, attaching a database, configuring an Iceberg catalog, or executing a view SQL statement
- **WHEN** the catalog build is attempted
- **THEN** an `EngineError` is raised that wraps the underlying exception and includes context about which operation failed.

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
Logging MUST use the standard Python logging module and MUST avoid exposing secrets at INFO level.

#### Scenario: High-level INFO logs
- **GIVEN** logging is configured at INFO level
- **WHEN** a catalog build or validation runs
- **THEN** logs include high-level events such as “loading config”, “connecting to DuckDB”, “setting up attachments”, and “creating view X”
- **AND** do not include full connection strings or secret values.

#### Scenario: DEBUG logs with redaction
- **GIVEN** logging is configured at DEBUG level
- **WHEN** a catalog build or validation runs
- **THEN** logs MAY include detailed information such as generated SQL or attachment parameters
- **BUT** any values derived from environment variables intended as secrets (e.g. passwords, access keys, tokens) MUST be redacted or omitted.

