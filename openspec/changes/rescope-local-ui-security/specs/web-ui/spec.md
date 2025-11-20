## MODIFIED Requirements

### Requirement: Querying and data export
Users MUST be able to preview data, run more complex queries, and export results as CSV, Parquet, or Excel files from the UI.

#### Scenario: Ad-hoc queries remain available with read-only enforcement
- **WHEN** the user calls `/api/query`
- **THEN** the server enforces single-statement, read-only SQL (no DDL/DML/multi-statement batches)
- **AND** the endpoint remains available for interactive local use.

#### Scenario: Exports may use view or read-only query
- **WHEN** requesting `/api/export`
- **THEN** the server accepts either a view name or a read-only query
- **AND** applies the same read-only/single-statement enforcement before exporting.

### Requirement: Authentication and authorization
The UI server MUST support authentication controls to prevent unauthorized access to catalog management operations.

#### Scenario: Optional admin token on mutating endpoints
- **GIVEN** an admin token is configured (for example via environment)
- **WHEN** a mutating request (`POST`/`PUT`/`DELETE`) arrives without a valid `Authorization: Bearer <token>` header
- **THEN** the server rejects it with 401
- **AND** when no token is configured, the server allows local use without authentication.

### Requirement: Lightweight architecture
The UI MUST remain lightweight for localhost use, favoring minimal layers.

#### Scenario: No mandatory service-layer split
- **WHEN** reviewing the UI code
- **THEN** a single Starlette app with shared helpers is acceptable
- **AND** service classes are optional, not mandatory for compliance.
