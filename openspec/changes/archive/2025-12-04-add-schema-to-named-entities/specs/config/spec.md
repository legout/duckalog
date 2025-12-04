## MODIFIED Requirements

### Requirement: View Definitions and Sources
Each view definition MUST have a unique identifier within the catalog and EITHER a `sql` field OR a `source` field with the required attributes for that source type.

#### Scenario: Raw SQL view (no schema)
- **GIVEN** a view with `name: vip_users` and a non-empty `sql` string
- **AND** the view does not specify `schema`, `source`, `uri`, `database`, `table`, or `catalog`
- **WHEN** the configuration is validated
- **THEN** the view is accepted as a raw SQL view
- **AND** its canonical identifier in DuckDB is the unqualified view name (for example, `vip_users`).

#### Scenario: Raw SQL view with schema
- **GIVEN** a view with `name: vip_users`, `schema: analytics`, and a non-empty `sql` string
- **WHEN** the configuration is validated
- **THEN** the view is accepted as a raw SQL view
- **AND** its canonical identifier in DuckDB is the schema-qualified name (for example, `analytics.vip_users`).

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

#### Scenario: View name and schema uniqueness
- **GIVEN** a catalog configuration with multiple view entries
- **WHEN** the configuration is validated
- **THEN** the combination of `schema` (if provided) and `name` MUST be unique within the catalog
- **AND** if two views share the same `name` and `schema` values, validation SHALL fail with a clear error indicating the duplicate.
