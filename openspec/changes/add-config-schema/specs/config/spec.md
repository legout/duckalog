## ADDED Requirements

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

