## MODIFIED Requirements

### Requirement: Configuration Schema Reference
The documentation SHALL provide a comprehensive YAML/JSON schema reference documenting all configuration options with types, defaults, required fields, and examples that reflect the current implementation.

#### Scenario: Complete configuration option lookup
- **GIVEN** a user writing a configuration file
- **WHEN** they need to understand available options
- **THEN** they find a schema reference with all configuration sections that exist in the current `Config` model:
  - `version`
  - `duckdb` (including `database`, `pragmas`, `install_extensions`, `load_extensions`, `settings`, `secrets`)
  - `views`
  - `attachments`
  - `iceberg_catalogs`
  - `semantic_models`
  - `imports`
  - `env_files`
- **AND** the reference does not document fields that are not present in the config models.

#### Scenario: Secret configuration matches implementation
- **GIVEN** a user wants to configure DuckDB secrets
- **WHEN** they consult the schema reference and examples
- **THEN** the documentation shows secrets configured under `duckdb.secrets`
- **AND** it does not instruct users to use unimplemented fields such as `secrets_ref`.

#### Scenario: Examples are schema-valid
- **GIVEN** examples in the schema reference and secrets guides
- **WHEN** a user copy/pastes them into a config file
- **THEN** the examples validate successfully against the current configuration schema
- **SO** users can rely on documentation without trial and error.
