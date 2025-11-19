## MODIFIED Requirements

### Requirement: Attachments and Iceberg Catalogs

#### Scenario: Engine attachment setup respects model shapes
- **WHEN** the engine sets up DuckDB, SQLite, or Postgres attachments based on the loaded configuration
- **THEN** it SHALL treat each attachment according to its declared model (e.g., `DuckDBAttachment`, `SQLiteAttachment`, `PostgresAttachment`)
- **AND** SHALL avoid assuming attributes are present that are not part of the corresponding model
- **AND** SHALL branch on attachment type where the set of required attributes differs (for example, `host`, `port`, `database`, `user`, `password`, `options`).

