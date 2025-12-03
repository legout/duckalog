## ADDED Requirements

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

