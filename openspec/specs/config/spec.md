# config Specification

## Purpose
TBD - created by archiving change add-config-schema. Update Purpose after archive.
## Requirements
### Requirement: Catalog Config Format
Catalog configuration MUST be provided as a YAML or JSON document that includes a numeric `version` field and top-level sections for `duckdb`, `views`, and optional `attachments` and `iceberg_catalogs`.

#### Scenario: YAML config accepted
- **GIVEN** a valid `catalog.yaml` file with keys `version`, `duckdb`, and `views`
- **WHEN** the configuration is loaded
- **THEN** it is parsed successfully into the `Config` model
- **AND** the `version` field is present and numeric.

#### Scenario: JSON config accepted
- **GIVEN** a valid `catalog.json` file with equivalent structure to `catalog.yaml`
- **WHEN** the configuration is loaded
- **THEN** it is parsed successfully into the `Config` model
- **AND** the `version` field is present and numeric.

### Requirement: Environment Variable Interpolation
The system MUST support `${env:VAR_NAME}` placeholders in any string value and resolve them from the process environment, failing fast when required variables are missing.

#### Scenario: Placeholder is resolved from environment
- **GIVEN** `AWS_ACCESS_KEY_ID` is set in the environment
- **AND** a config pragma value is `\"SET s3_access_key_id='${env:AWS_ACCESS_KEY_ID}'\"`
- **WHEN** the configuration is loaded
- **THEN** the placeholder is replaced with the value of `AWS_ACCESS_KEY_ID`
- **AND** the resulting `Config` instance contains the interpolated value.

#### Scenario: Missing environment variable causes error
- **GIVEN** `AWS_SECRET_ACCESS_KEY` is NOT set in the environment
- **AND** a config pragma value is `\"SET s3_secret_access_key='${env:AWS_SECRET_ACCESS_KEY}'\"`
- **WHEN** the configuration is loaded
- **THEN** configuration loading fails
- **AND** a configuration error is raised indicating the missing environment variable.

### Requirement: View Definitions and Sources
Each view definition MUST have a unique `name` and EITHER a `sql` field OR a `source` field with the required attributes for that source type.

#### Scenario: Raw SQL view
- **GIVEN** a view with `name: vip_users` and a non-empty `sql` string
- **AND** the view does not specify `source`, `uri`, `database`, `table`, or `catalog`
- **WHEN** the configuration is validated
- **THEN** the view is accepted as a raw SQL view.

#### Scenario: Parquet view with required uri
- **GIVEN** a view with `source: parquet` and a non-empty `uri`
- **WHEN** the configuration is validated
- **THEN** the view is accepted
- **AND** the `uri` value is required and cannot be empty.

#### Scenario: Iceberg view with either uri or catalog+table
- **GIVEN** a view with `source: iceberg`
- **AND** either a non-empty `uri`
- **OR** both `catalog` and `table` set
- **WHEN** the configuration is validated
- **THEN** the view is accepted
- **AND** configurations that mix `uri` with `catalog` or `table`, or omit both, are rejected.

#### Scenario: Attached database view requires database and table
- **GIVEN** a view with `source` set to `duckdb`, `sqlite`, or `postgres`
- **AND** both `database` (attachment alias) and `table` are provided
- **WHEN** the configuration is validated
- **THEN** the view is accepted
- **AND** configurations missing either `database` or `table` for these sources are rejected.

### Requirement: Attachments and Iceberg Catalogs
Attachments and Iceberg catalogs MUST follow the shapes defined by their configuration models and MUST be validated before any catalog build.

#### Scenario: DuckDB and SQLite attachments validated
- **GIVEN** `attachments.duckdb[]` entries with `alias`, `path`, and optional `read_only`
- **AND** `attachments.sqlite[]` entries with `alias` and `path`
- **WHEN** the configuration is validated
- **THEN** entries missing required fields are rejected with clear validation errors.

#### Scenario: Postgres attachments validated
- **GIVEN** `attachments.postgres[]` entries with `alias`, `host`, `port`, `database`, `user`, and `password`
- **WHEN** the configuration is validated
- **THEN** entries missing any required field are rejected with clear validation errors.

#### Scenario: Iceberg catalog definitions validated
- **GIVEN** `iceberg_catalogs[]` entries each with a `name`, `catalog_type`, and optional `uri`, `warehouse`, and `options`
- **WHEN** the configuration is validated
- **THEN** entries missing `name` or `catalog_type` are rejected
- **AND** invalid field types (e.g. non-object `options`) are rejected.

### Requirement: DuckDB Secrets Configuration
The system SHALL allow users to define DuckDB secrets in the catalog configuration file for accessing external services and databases.

#### Scenario: S3 secret with CONFIG provider
- **WHEN** a user provides an S3 secret configuration in YAML
- **THEN** the system SHALL execute `CREATE SECRET` with the specified KEY_ID, SECRET, REGION, and other parameters

#### Scenario: Persistent secret with scope
- **WHEN** a user provides a persistent secret with a scope prefix
- **THEN** the system SHALL execute `CREATE PERSISTENT SECRET ... SCOPE 'prefix'` to create a scoped persistent secret

#### Scenario: Multiple secrets for same service type
- **WHEN** a user defines multiple S3 secrets with different scopes
- **THEN** the system SHALL create all secrets and allow DuckDB to automatically select the appropriate one based on path matching

#### Scenario: Secret with credential_chain provider
- **WHEN** a user provides a secret using the credential_chain provider
- **THEN** the system SHALL execute `CREATE SECRET ... USING credential_chain` to let DuckDB auto-fetch credentials

#### Scenario: Azure secret configuration
- **WHEN** a user provides an Azure secret with connection string or tenant ID
- **THEN** the system SHALL create the appropriate Azure secret type with the specified parameters

#### Scenario: Database secret for PostgreSQL
- **WHEN** a user provides a PostgreSQL secret with connection parameters
- **THEN** the system SHALL create a postgres secret type for use with PostgreSQL attachments

#### Scenario: Secret validation
- **WHEN** a user provides an invalid secret configuration (missing required fields for type)
- **THEN** the system SHALL raise a validation error during config loading

#### Scenario: Empty secrets configuration
- **WHEN** a user does not provide secrets or provides an empty list
- **THEN** the system SHALL continue without error and create no secrets

#### Scenario: Secrets with environment variables
- **WHEN** a user provides secret values using `${env:VAR_NAME}` syntax
- **THEN** the system SHALL interpolate environment variables before creating the secret

#### Scenario: HTTP secret for basic auth
- **WHEN** a user provides an HTTP secret with username and password
- **THEN** the system SHALL create an http secret type for HTTP basic authentication

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

### Requirement: Semantic Models Configuration
The system SHALL allow users to define optional semantic models that provide business-friendly metadata on top of existing views.

#### Scenario: Semantic model with dimensions and measures
- **WHEN** a user provides a `semantic_models` section with models containing `name`, `base_view`, `dimensions`, and `measures`
- **THEN** the system SHALL validate that each semantic model has a unique name
- **AND** the system SHALL validate that each `base_view` references an existing view in the `views` section
- **AND** the system SHALL validate that dimension and measure names are unique within each model

#### Scenario: Semantic model validation errors
- **WHEN** a user provides a semantic model with a duplicate name
- **THEN** the system SHALL raise a validation error indicating the duplicate semantic model name
- **WHEN** a user provides a semantic model with a `base_view` that doesn't exist
- **THEN** the system SHALL raise a validation error indicating the missing base view
- **WHEN** a user provides dimensions or measures with duplicate names within the same model
- **THEN** the system SHALL raise a validation error indicating the duplicate dimension/measure name

#### Scenario: Empty semantic models
- **WHEN** a user does not provide semantic models or provides an empty list
- **THEN** the system SHALL continue without error and no semantic models are available

#### Scenario: Semantic model metadata
- **WHEN** a user provides optional metadata like `label`, `description`, or `tags` on semantic models, dimensions, or measures
- **THEN** the system SHALL accept and preserve this metadata without validation beyond basic type checking

