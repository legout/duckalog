## ADDED Requirements
### Requirement: DuckDB Settings Configuration
The system SHALL allow users to define DuckDB session settings in the catalog configuration file.

#### Scenario: Single setting as string
- **WHEN** a user provides `duckdb.settings: "threads = 32"` in YAML config
- **THEN** the system SHALL execute `SET threads = 32` after applying pragmas

#### Scenario: Multiple settings as list
- **WHEN** a user provides `duckdb.settings: ["threads = 32", "memory_limit = '1GB'"]` in config
- **THEN** the system SHALL execute each SET statement in order after applying pragmas

#### Scenario: Settings with environment variables
- **WHEN** a user provides `duckdb.settings: "threads = ${env:THREAD_COUNT}"` in config
- **THEN** the system SHALL interpolate the environment variable before executing the SET statement

#### Scenario: Settings validation
- **WHEN** a user provides invalid settings syntax
- **THEN** the system SHALL raise a validation error during config loading

#### Scenario: Empty settings
- **WHEN** a user does not provide settings or provides an empty value
- **THEN** the system SHALL continue without error and apply no additional settings

