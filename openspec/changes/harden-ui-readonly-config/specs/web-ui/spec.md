## MODIFIED Requirements

### Requirement: Manage catalog views
Users MUST be able to add, update, and delete view entries through the UI, with the configuration remaining valid on disk.

#### Scenario: View addition succeeds when valid
- **GIVEN** a JSON payload that satisfies `duckalog.config.ViewConfig`
- **WHEN** the user submits a create request via the UI
- **THEN** the server merges the new view into the current configuration, validates the full config, and writes it back to the original file format (YAML or JSON)
- **AND** the response includes enough metadata for the UI to update the visible list of views.

#### Scenario: View update enforces uniqueness and validation
- **GIVEN** a request that edits an existing view definition
- **WHEN** the edit would introduce a duplicate view name or violate the config schema
- **THEN** validation fails with a clear error message returned to the UI
- **AND** the on-disk config is not modified.

#### Scenario: View deletion removes entry safely
- **GIVEN** a request to delete an existing view
- **WHEN** the deletion is confirmed
- **THEN** the server removes the view from the configuration, validates the result, and writes the updated config back to disk
- **AND** the deleted view no longer appears in the dashboard list.

#### Scenario: Config writes preserve format and reload
- **WHEN** the UI adds, updates, or deletes a view
- **THEN** the server rewrites the config using the original file format (YAML keeps formatting/comments, JSON keeps indentation) via an atomic replace
- **AND** reloads the updated config into memory before responding so subsequent requests use the new state
- **AND** failures return an error without leaving partial temp files behind.

### Requirement: Schema inspection and catalog rebuild
The UI MUST support inspecting view schemas and triggering a catalog rebuild so the dashboard can reflect the current database state.

#### Scenario: Schema panel shows columns
- **GIVEN** the catalog has been built at least once for the configured database path
- **WHEN** the user requests the schema for a view from the dashboard
- **THEN** the server describes the view via DuckDB (for example, using `DESCRIBE` or `PRAGMA table_info`)
- **AND** returns the column names and types so the UI can display them.

#### Scenario: Rebuild button reapplies config
- **WHEN** the user clicks a rebuild action in the UI
- **THEN** the backend runs `duckalog.engine.build_catalog` (or equivalent) against the current config file
- **AND** the UI receives success or failure information suitable for user feedback (for example, a status message or banner).

#### Scenario: Blocking work does not stall the UI
- **WHEN** the server runs DuckDB-intensive work (schema describe, rebuild, query, or export)
- **THEN** the work is dispatched off the event loop (for example using background tasks/threadpool executors)
- **AND** the HTTP handler remains responsive to other requests while the work completes.

### Requirement: Querying and data export
Users MUST be able to preview data, run more complex queries, and export results as CSV, Parquet, or Excel files from the UI.

#### Scenario: Preview shows query rows
- **GIVEN** a simple query such as `SELECT * FROM my_view LIMIT 100`
- **WHEN** the user submits the query from the dashboard
- **THEN** the server executes it against the configured DuckDB catalog
- **AND** returns the top rows in a form the UI can render as a table.

#### Scenario: Export produces the requested format
- **GIVEN** the user selects a view or query and chooses an export format (CSV, Parquet, or Excel)
- **WHEN** the export action is invoked from the UI
- **THEN** the server streams a file download with the correct `Content-Type` and `Content-Disposition` headers for that format
- **AND** any temporary files used for export are cleaned up after the response is sent.

#### Scenario: Preview enforces read-only single-statement SQL
- **WHEN** the user submits a query from the dashboard
- **THEN** the server enforces a single read-only statement (no DDL/DML/multi-statement batches; trailing semicolons are rejected)
- **AND** any view- or table-derived identifiers are properly quoted/parameterized before execution
- **AND** the optional LIMIT is applied without corrupting the user SQL or allowing injection.

#### Scenario: Exports respect read-only constraints
- **WHEN** the user exports data from a view or query
- **THEN** the backend enforces the same read-only/multi-statement guards and identifier quoting as previews
- **AND** returns the expected file with correct headers for the chosen format.

### Requirement: Datastar-driven interactivity
The dashboard MUST use Datastar attributes and the Python SDK to keep the UI reactive without introducing a heavy client-side framework.

#### Scenario: UI uses Datastar for actions and updates
- **WHEN** the user performs an action such as adding a view, requesting a schema, rebuilding the catalog, running a query, or exporting data
- **THEN** the browser issues Datastar-driven requests to the backend (for example, via `data-on` attributes and Datastar actions)
- **AND** the backend uses the Datastar Python SDK to drive updates or patches back to the page
- **AND** no additional JavaScript framework beyond Datastar is required for the supported workflows.

#### Scenario: Datastar is the single dashboard path
- **WHEN** the dashboard is rendered
- **THEN** the Datastar-powered page is returned (no legacy fallback markup)
- **AND** the server uses the Datastar Python SDK/SSE helpers to push status updates (for example query completion or rebuild banners) without extra JS frameworks.

## ADDED Requirements

### Requirement: Local-first CORS defaults
The UI MUST default to a restrictive CORS posture suitable for localhost usage, with explicit opt-in for broader access.

#### Scenario: CORS limited to local origins
- **WHEN** the server starts without custom CORS configuration
- **THEN** only same-origin/localhost origins are allowed and credentials are disabled by default
- **AND** administrators can explicitly extend the allow-list via configuration when needed, with the default remaining restrictive.
