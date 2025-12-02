## ADDED Requirements

### Requirement: Safe SQL Generation for Views and Secrets
SQL generated from configuration for catalog builds MUST safely quote all configuration‑derived identifiers and string literals and MUST avoid interpolating unsupported secret option types.

#### Scenario: View SQL uses quoted identifiers
- **GIVEN** a config with views that reference attached databases or tables whose names contain spaces, reserved words, or other special characters
- **WHEN** SQL is generated for those views
- **THEN** database, schema, and table names are emitted as properly quoted identifiers
- **AND** attempts to inject additional SQL via these fields do not change the structure of the generated statement.

#### Scenario: Secret SQL uses safe literals and strict option types
- **GIVEN** a config with DuckDB secrets whose fields and options contain quotes or other special characters
- **WHEN** `CREATE SECRET` statements are generated for catalog builds or dry‑run SQL output
- **THEN** all string values are emitted as safely quoted literals
- **AND** numeric and boolean option values are rendered without quotes according to their type
- **AND** any secret option whose value type is not `bool`, `int`, `float`, or `str` causes validation or SQL generation to fail with a clear error instead of interpolating an unsafe representation.

