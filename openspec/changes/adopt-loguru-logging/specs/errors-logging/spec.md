## MODIFIED Requirements

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
