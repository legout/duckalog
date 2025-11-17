## MODIFIED Requirements

### Requirement: DuckDB Attachment Read-only Default
DuckDB attachments MUST default to read-only mode unless explicitly configured otherwise.

#### Scenario: DuckDB attachment without read_only field
- **GIVEN** an `attachments.duckdb[]` entry with `alias` and `path` but no `read_only` field
- **WHEN** the configuration is loaded
- **THEN** the corresponding `DuckDBAttachment` instance has `read_only=True`
- **AND** the engine attaches the DuckDB file in read-only mode.

#### Scenario: DuckDB attachment explicitly read-write
- **GIVEN** an `attachments.duckdb[]` entry with `alias`, `path`, and `read_only: false`
- **WHEN** the configuration is loaded
- **AND** a catalog build is executed
- **THEN** the attachment is opened without the `READ_ONLY` clause, allowing write operations.

