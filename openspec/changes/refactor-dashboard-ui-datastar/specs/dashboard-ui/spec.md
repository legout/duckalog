## ADDED Requirements

### Requirement: Dashboard Datastar Integration

The dashboard MUST integrate Datastar and datastar-python to provide reactive, server-driven updates for core dashboard state.

#### Scenario: Dashboard loads Datastar bundle
- **GIVEN** the dashboard is launched via `duckalog ui` or `run_dashboard(...)`
- **WHEN** a user opens the main dashboard URL in a browser
- **THEN** the HTML response SHALL include a `<script>` tag that loads the local Datastar JavaScript bundle (e.g. `src="/static/datastar.js"`)
- **AND** no external CDN is required for Datastar.

#### Scenario: Dashboard exposes Datastar SSE endpoint
- **GIVEN** the dashboard server is running
- **WHEN** the browser connects to the configured Datastar SSE endpoint used by the dashboard
- **THEN** the server SHALL stream Datastar-compatible events
- **AND** these events SHALL be able to update one or more client-side signals defined for the dashboard UI.

#### Scenario: Dashboard uses Datastar attributes for interactivity
- **GIVEN** a rendered dashboard page (home, views, or query)
- **WHEN** the HTML is inspected
- **THEN** interactive controls (buttons, links, forms) involved in fetching or mutating state SHALL use Datastar `data-*` attributes
- **AND** these attributes SHALL be generated using datastar-python helpers to ensure correct syntax.

---

### Requirement: Dashboard Catalog Overview

The dashboard MUST display a catalog overview page that summarizes key metadata and build status, using Datastar signals to keep the UI in sync with backend state.

#### Scenario: Overview displays catalog summary
- **GIVEN** a valid Duckalog configuration with a DuckDB database, views, attachments, and semantic models
- **WHEN** a user opens the dashboard home page
- **THEN** the page SHALL display at least:
  - The resolved config path (if available)
  - The DuckDB database path
  - The number of views
  - The number of attachments
  - The number of semantic models
- **AND** these values SHALL be derived from the current configuration loaded into the dashboard.

#### Scenario: Overview shows last build status
- **GIVEN** the catalog has been built at least once from the dashboard or CLI
- **WHEN** a user opens or refreshes the dashboard home page
- **THEN** the page SHALL display the last build status (success/failure) and completion timestamp
- **AND** this status SHALL be updated reactively when a new build is triggered from the dashboard.

---

### Requirement: Dashboard Views Explorer

The dashboard MUST provide a views explorer that allows browsing, searching, and inspecting views defined in the catalog configuration.

#### Scenario: Views table lists core metadata
- **GIVEN** a configuration with one or more views
- **WHEN** a user navigates to the views section
- **THEN** the dashboard SHALL display a table with at least the following columns for each view:
  - View name
  - Source type (e.g. `parquet`, `delta`, `sql`)
  - URI or underlying location (when applicable)
  - Database and table (when applicable)
  - Whether the view has associated semantic-layer metadata.

#### Scenario: Views can be searched by name
- **GIVEN** a configuration with multiple views
- **WHEN** a user enters a search string into a views search control
- **THEN** the dashboard SHALL filter the visible rows to those whose names match or contain the search string
- **AND** this filtering SHALL be applied without a full page reload (e.g. via Datastar-driven updates).

#### Scenario: View detail shows definition and semantics
- **GIVEN** a specific view exists in the configuration
- **WHEN** a user navigates to that view’s detail panel or page
- **THEN** the dashboard SHALL display either:
  - The view’s SQL definition, if present
  - OR a structured description of its backing source (source type, URI, database, table)
- **AND** if one or more semantic models reference this view as a base view, the dashboard SHALL list their names, dimensions, and measures.

---

### Requirement: Dashboard Read-Only Query Panel

The dashboard MUST provide an ad-hoc query panel that allows users to run read-only SQL queries against the catalog, with enforced row limits and safe error handling.

#### Scenario: Query panel enforces read-only SQL
- **GIVEN** the dashboard is configured with a DuckDB database path
- **WHEN** a user submits a query from the dashboard query panel
- **AND** the query contains non-select statements (e.g. `INSERT`, `UPDATE`, `DELETE`, `CREATE`, `DROP`)
- **THEN** the dashboard SHALL reject the query
- **AND** display a clear error message indicating that only read-only queries are allowed
- **AND** SHALL NOT execute any mutating SQL against the catalog.

#### Scenario: Query panel runs SELECT queries and displays results
- **GIVEN** a valid catalog with at least one view or table available
- **WHEN** a user submits a valid `SELECT` query from the query panel
- **THEN** the dashboard SHALL execute the query against the configured DuckDB database
- **AND** render the results as a table with column headers and rows
- **AND** display any execution error in a user-friendly message if the query fails.

#### Scenario: Query panel enforces row limit
- **GIVEN** the dashboard is configured with a `row_limit` value
- **WHEN** a user executes a `SELECT` query that would return more than `row_limit` rows
- **THEN** the dashboard SHALL return only the first `row_limit` rows for display
- **AND** SHALL display an indicator that the results have been truncated.

---

### Requirement: Dashboard Build Controls

The dashboard MUST allow triggering catalog builds and reflect build progress and outcome in the UI.

#### Scenario: User can trigger a catalog build
- **GIVEN** the dashboard is associated with a configuration file path
- **WHEN** a user clicks a “Build catalog” control in the dashboard
- **THEN** the dashboard SHALL invoke the catalog build process using that configuration
- **AND** SHALL update the build status and completion time displayed on the overview.

#### Scenario: Failed builds show clear error status
- **GIVEN** the catalog build process fails due to a configuration or engine error
- **WHEN** the user triggers a build from the dashboard
- **THEN** the dashboard SHALL display a clear error message and failed status
- **AND** SHALL NOT leave the build status in an ambiguous or “in progress” state.

