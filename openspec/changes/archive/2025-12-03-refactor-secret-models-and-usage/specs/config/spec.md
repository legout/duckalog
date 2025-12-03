## ADDED Requirements

### Requirement: Canonical SecretConfig Model
Duckalog configuration MUST represent DuckDB secrets using a single canonical `SecretConfig` model that covers all supported secret types and maps directly to DuckDB `CREATE SECRET` parameters.

#### Scenario: Secrets configured via SecretConfig
- **GIVEN** a catalog configuration that defines one or more DuckDB secrets
- **WHEN** the configuration is loaded and validated
- **THEN** each secret is represented as a `SecretConfig` instance with a `type` discriminator (such as `\"s3\"`, `\"azure\"`, `\"gcs\"`, `\"http\"`, `\"postgres\"`, or `\"mysql\"`)
- **AND** only fields defined on `SecretConfig` are used to drive DuckDB `CREATE SECRET` statements, with no reliance on duplicated or backend‑specific config models.

#### Scenario: Secret options use supported primitive types
- **GIVEN** a `SecretConfig` with an `options` dictionary
- **WHEN** the configuration is validated and secret SQL is generated
- **THEN** option values of type `bool`, `int`, `float`, and `str` are accepted and rendered into SQL according to the SQL generation rules
- **AND** option values of any other type are rejected with a clear configuration or type error rather than being interpolated unsafely.

