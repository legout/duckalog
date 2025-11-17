## MODIFIED Requirements

### Requirement: Iceberg Catalog Reference Validation
The engine MUST ensure that any Iceberg view using a `catalog` name references a defined Iceberg catalog before executing queries.

#### Scenario: View references existing Iceberg catalog
- **GIVEN** a config with `iceberg_catalogs` containing a catalog named `main_ic`
- **AND** a view with `source: iceberg` and `catalog: main_ic`
- **WHEN** the configuration is validated or a catalog build is attempted
- **THEN** the catalog name passes validation and normal processing continues.

#### Scenario: View references missing Iceberg catalog
- **GIVEN** a config where `iceberg_catalogs` does not include a catalog named `missing_ic`
- **AND** a view with `source: iceberg` and `catalog: missing_ic`
- **WHEN** the configuration is validated or a catalog build is attempted
- **THEN** the operation fails fast with a clear error indicating the missing Iceberg catalog name
- **AND** no DuckDB queries are executed for that config.

