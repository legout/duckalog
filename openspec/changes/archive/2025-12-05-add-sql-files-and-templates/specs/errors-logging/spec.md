## ADDED Requirements

### Requirement: SQL File and Template Error Reporting
Errors encountered while loading or processing SQL files and templates MUST be surfaced via `SQLFileError` with clear context for diagnostics.

#### Scenario: SQL file IO or path error reporting
- **GIVEN** a view that references a SQL file via `sql_file`
- **AND** the referenced file cannot be read due to a missing file, permission issue, or disallowed path
- **WHEN** the configuration loader attempts to load the SQL file
- **THEN** the system SHALL raise a `SQLFileError` (inheriting from `DuckalogError`) that includes the view name, the SQL path, and a short description of the failure
- **AND** that error SHALL be wrapped as a `ConfigError` or `RemoteConfigError` when appropriate, preserving the original exception via `raise ... from exc`.

#### Scenario: SQL template variable error reporting
- **GIVEN** a view that references a SQL template via `sql_template` with a `variables` mapping
- **AND** the template contains one or more `{{variable}}` placeholders that do not have corresponding entries in `variables`
- **WHEN** the configuration loader attempts to render the template
- **THEN** the system SHALL raise a `SQLFileError` that identifies the missing variable name, the view name, and the SQL path
- **AND** the error message SHALL instruct the user to add the missing variable or remove the placeholder.
