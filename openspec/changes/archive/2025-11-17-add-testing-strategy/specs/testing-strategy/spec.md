## ADDED Requirements

### Requirement: Config Testing Coverage
The test suite MUST include unit tests that exercise configuration parsing, validation, and environment interpolation for both YAML and JSON configs.

#### Scenario: YAML and JSON configs are tested
- **GIVEN** sample YAML and JSON config files that cover required and optional fields
- **WHEN** the test suite runs
- **THEN** tests assert that both formats are parsed into equivalent `Config` instances
- **AND** invalid configs (e.g. missing required fields, duplicate view names) cause validation failures as expected.

#### Scenario: Env interpolation behavior is tested
- **GIVEN** tests that set and unset environment variables around config loading
- **WHEN** configs with `${env:VAR}` placeholders are loaded
- **THEN** tests assert that placeholders are correctly resolved when variables are set
- **AND** that missing variables cause `ConfigError` to be raised.

### Requirement: SQL Generation Testing
The test suite MUST include snapshot-style tests for SQL generation covering all supported view source types and option combinations.

#### Scenario: SQL snapshots for all source types
- **GIVEN** representative `ViewConfig` instances for `parquet`, `delta`, `iceberg` (uri and catalog+table), attached databases, and raw SQL
- **WHEN** `generate_view_sql` and `generate_all_views_sql` are invoked in tests
- **THEN** the resulting SQL is compared against stored expectations
- **AND** changes to SQL output are detected as test failures unless intentionally updated.

### Requirement: Engine Integration Testing
The test suite MUST include integration tests that exercise the catalog build engine against temporary DuckDB files and simple attachment fixtures.

#### Scenario: Views created in temporary DuckDB
- **GIVEN** a temporary DuckDB file and a minimal config with one or more views
- **WHEN** the engine’s build function is invoked in a test
- **THEN** the test verifies that the expected views exist in the DuckDB catalog
- **AND** that re-running the build with the same config is idempotent.

#### Scenario: Attachments smoke tests
- **GIVEN** small local DuckDB and SQLite files created as fixtures
- **WHEN** engine tests attach these databases using the configured aliases
- **THEN** tests verify that views can be created over attached tables without errors.

### Requirement: Offline and Deterministic Tests
The default test suite MUST be deterministic and MUST NOT require external network connectivity or long-running external services.

#### Scenario: Tests run offline by default
- **GIVEN** a clean development or CI environment without network access to external databases or object stores
- **WHEN** the test suite is executed
- **THEN** all core tests pass using only local resources (temporary files, local DuckDB instances)
- **AND** any optional tests that require external services are clearly marked and disabled by default.

