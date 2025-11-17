## ADDED Requirements

### Requirement: generate_sql Convenience Function
The library MUST provide a `generate_sql(config_path: str) -> str` function that returns the full SQL script for all views defined in a config without connecting to DuckDB.

#### Scenario: SQL generated from config path
- **GIVEN** a valid YAML or JSON config file path
- **WHEN** `generate_sql(config_path)` is called
- **THEN** the function loads and validates the config
- **AND** returns the same SQL as `generate_all_views_sql` would produce for the corresponding `Config` instance
- **AND** does not open a DuckDB connection or modify any database files.

### Requirement: validate_config Convenience Function
The library MUST provide a `validate_config(config_path: str) -> None` function that validates a config and raises errors on failure without connecting to DuckDB.

#### Scenario: Valid config passes validation
- **GIVEN** a valid config file path
- **WHEN** `validate_config(config_path)` is called
- **THEN** the function completes without raising an exception
- **AND** does not create or modify any DuckDB catalog files.

#### Scenario: Invalid config raises ConfigError
- **GIVEN** a config file path pointing to an invalid or incomplete config
- **WHEN** `validate_config(config_path)` is called
- **THEN** the function raises a `ConfigError` describing the problem
- **AND** the exception can be caught by callers to handle validation failures.

### Requirement: No Side Effects for Convenience Functions
`generate_sql` and `validate_config` MUST be pure with respect to DuckDB catalogs and external systems.

#### Scenario: No DuckDB connections from convenience functions
- **GIVEN** a valid config file
- **WHEN** `generate_sql` or `validate_config` are called
- **THEN** no DuckDB connections are opened
- **AND** no `ATTACH` statements or `CREATE VIEW` statements are executed against any database.

