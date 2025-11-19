## ADDED Requirements

### Requirement: Launchable catalog dashboard
The system MUST provide a way to start a web UI that targets a specific Duckalog config file and underlying DuckDB catalog.

#### Scenario: UI starts for a given config
- **GIVEN** `duckalog` is installed and a valid config file path exists
- **WHEN** the user runs a CLI command such as `duckalog ui <config-path>` (exact name is not normative)
- **THEN** a Starlette-based app starts on localhost with an address printed to the console
- **AND** opening that address in a browser shows the catalog dashboard for that config.

### Requirement: View catalog metadata
Users MUST be able to see the configured catalog views and basic metadata from the dashboard.

#### Scenario: Views are listed on load
- **GIVEN** a valid Duckalog config with one or more views
- **WHEN** the user opens the dashboard
- **THEN** the page shows a list or table of all views including at least the view name, source type, and optional description
- **AND** selecting a view shows additional details (such as source URI or attached database/table) without requiring a full page reload.

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

### Requirement: Datastar-driven interactivity
The dashboard MUST use Datastar attributes and the Python SDK to keep the UI reactive without introducing a heavy client-side framework.

#### Scenario: UI uses Datastar for actions and updates
- **WHEN** the user performs an action such as adding a view, requesting a schema, rebuilding the catalog, running a query, or exporting data
- **THEN** the browser issues Datastar-driven requests to the backend (for example, via `data-on` attributes and Datastar actions)
- **AND** the backend uses the Datastar Python SDK to drive updates or patches back to the page
- **AND** no additional JavaScript framework beyond Datastar is required for the supported workflows.
