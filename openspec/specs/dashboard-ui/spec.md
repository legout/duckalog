# dashboard-ui Specification

## Purpose
TBD - created by archiving change add-dashboard-starui. Update Purpose after archive.
## Requirements
### Requirement: Local Dashboard Launch
The system SHALL provide a way to launch a local web dashboard for a single Duckalog catalog from the Python API, and MAY optionally provide a CLI command for launching the same dashboard implementation.

#### Scenario: Launch dashboard from CLI with config path (optional)
- **GIVEN** a valid `catalog.yaml` configuration file on disk
- **AND** an installation where the `duckalog ui` CLI command is enabled
- **WHEN** the user runs `duckalog ui catalog.yaml`
- **THEN** a local HTTP server is started on a default host and port
- **AND** the CLI prints the URL where the dashboard is available.

### Requirement: Dashboard Home Overview
The dashboard home page SHALL present a concise overview of the selected catalog and navigation to other dashboard sections.

#### Scenario: Home shows catalog summary
- **GIVEN** the dashboard is launched for a valid catalog
- **WHEN** the user visits the home page
- **THEN** they see the catalog config path, DuckDB database location, and counts of views, attachments, and semantic models (if present)
- **AND** the page links to the views browser, query runner, and build status sections.

#### Scenario: Home shows recent build status
- **GIVEN** the catalog has been built at least once in the current process
- **WHEN** the user visits or refreshes the home page
- **THEN** they see the status of the last build (success/failure, timestamp)
- **AND** a link or button to view more detailed build status information.

### Requirement: Views Browser
The dashboard SHALL provide a views browser that lists catalog views and key metadata in a tabular layout.

#### Scenario: List views with metadata
- **GIVEN** a catalog with one or more views
- **WHEN** the user navigates to the views browser
- **THEN** they see a table with one row per view including at minimum the view name, source type, and underlying location or attachment reference
- **AND** each row indicates whether the view participates in the semantic layer (e.g. has dimensions or measures defined).

#### Scenario: Filter or search views by name
- **GIVEN** a catalog with many views
- **WHEN** the user types a partial view name into a search or filter input
- **THEN** the views table updates to show only matching views
- **AND** clearing the search restores the full list.

#### Scenario: Navigate to view detail
- **GIVEN** the user is viewing the views browser
- **WHEN** they select or click on a specific view
- **THEN** they are taken to a view detail page for that view.

### Requirement: View Detail and Semantic Metadata
The dashboard SHALL provide a detail page for each view that surfaces its definition and semantic metadata where available.

#### Scenario: Show core view definition
- **GIVEN** a view is defined in the catalog
- **WHEN** the user navigates to that view's detail page
- **THEN** they see the view name and either its resolved SQL or the key configuration fields that define it (e.g. source type and URI)
- **AND** any available engine-level metadata such as row count or sample schema when inexpensive to compute.

#### Scenario: Show semantic-layer information when present
- **GIVEN** the view participates in the semantic layer with defined dimensions and measures
- **WHEN** the user navigates to that view's detail page
- **THEN** they see a list of dimensions and measures with their labels and expressions
- **AND** the page makes clear when a view has no semantic-layer metadata.

### Requirement: Ad-hoc Query Runner
The dashboard SHALL provide a simple ad-hoc SQL query runner against the selected catalog.

#### Scenario: Run query and display results
- **GIVEN** the dashboard is connected to a valid catalog
- **WHEN** the user enters a SELECT query and submits it
- **THEN** the query is executed against the catalog's DuckDB database
- **AND** the results are shown in a tabular view with column headers and a reasonable default row limit.

#### Scenario: Enforce result limits and show truncation
- **GIVEN** a query would return more than the configured maximum number of rows
- **WHEN** the user runs the query from the dashboard
- **THEN** only up to the configured maximum rows are displayed
- **AND** the UI indicates that results have been truncated.

#### Scenario: Show query errors clearly
- **GIVEN** a query contains invalid SQL or fails at execution time
- **WHEN** the user runs the query from the dashboard
- **THEN** the error is displayed in the UI in a clear, non-technical-friendly format
- **AND** the previous successful results (if any) are not mistaken for the failed query's output.

### Requirement: Build Trigger and Status
The dashboard SHALL allow users to trigger a catalog build and observe basic status and results.

#### Scenario: Trigger build from dashboard
- **GIVEN** the dashboard is connected to a valid catalog config
- **WHEN** the user clicks a “Build catalog” action in the UI
- **THEN** a catalog build is started using the same semantics as the CLI build command
- **AND** the UI indicates that a build is in progress.

#### Scenario: Show build completion and summary
- **GIVEN** a build has completed via the dashboard
- **WHEN** the user views the build status section
- **THEN** they see whether the build succeeded or failed, when it completed, and a short summary (e.g. number of views created or updated)
- **AND** any failure surface includes a concise error message suitable for users to act on.

### Requirement: Dashboard Documentation Accuracy
The dashboard documentation MUST accurately reflect the current implementation using Datastar framework, include all security features, and document the complete feature set.

#### Scenario: Correct framework documentation
- **GIVEN** users reading dashboard documentation
- **WHEN** they learn about the technical implementation
- **THEN** the documentation correctly identifies Datastar as the reactive web framework
- **AND** does NOT mention deprecated frameworks like starhtml/starui
- **AND** includes information about bundled Datastar assets for offline operation
- **SO** users have accurate technical information

#### Scenario: Security features documented
- **GIVEN** users deploying the dashboard
- **WHEN** they consult the documentation for security information
- **THEN** they find documentation of all security features:
  - Admin token protection for mutating operations
  - Read-only SQL enforcement (SELECT only, blocks DDL/DML)
  - CORS protection (localhost restriction by default)
  - Background task processing for non-blocking operations
  - Atomic configuration updates
- **AND** they find examples of production deployment with security enabled
- **SO** they can deploy the dashboard securely

#### Scenario: Complete feature list
- **GIVEN** users learning dashboard capabilities
- **WHEN** they read the feature documentation
- **THEN** they find complete documentation of all features:
  - View management (create, edit, delete)
  - Query execution with real-time results
  - Data export (CSV, Excel, Parquet formats)
  - Schema inspection (tables and views)
  - Catalog rebuild functionality
  - Semantic layer explorer
  - Model details (dimensions and measures with expressions)
- **AND** each feature includes usage instructions and screenshots/examples
- **SO** they understand full dashboard capabilities

#### Scenario: Python API as primary entry point
- **GIVEN** users wanting to launch the dashboard
- **WHEN** they read the documentation
- **THEN** the Python API method (run_dashboard) is documented as the primary entry point
- **AND** includes working code examples
- **AND** CLI launch (duckalog ui) is clearly marked as optional or may not be available
- **SO** users can reliably launch the dashboard regardless of installation method

#### Scenario: Datastar runtime requirements
- **GIVEN** users installing dashboard dependencies
- **WHEN** they read the installation documentation
- **THEN** they find information about Datastar runtime requirements:
  - No legacy fallback (exclusive Datastar patterns)
  - Reactive data binding capabilities
  - Server-Sent Events for real-time updates
  - Modern web patterns with built-in security
  - Bundled assets for offline operation
- **AND** they understand why duckalog[ui] extra is required
- **SO** they can install and understand dashboard dependencies

### Requirement: Implementation Stack and Constraints
The initial dashboard implementation SHALL use a pure-Python stack with starhtml and starui, be local-first, and avoid external build tooling and CDNs.

#### Scenario: Implemented with starhtml and starui
- **GIVEN** the dashboard UI is built for this capability
- **WHEN** the implementation is inspected
- **THEN** the HTML views and layouts are implemented using starhtml and starui components
- **AND** no separate JavaScript build toolchain (e.g. webpack, Vite) is required to develop or run the dashboard.

#### Scenario: Local-first and loopback by default
- **GIVEN** a user launches the dashboard without overriding host or port
- **WHEN** the HTTP server starts
- **THEN** it binds to a loopback-only interface by default
- **AND** the documentation explains how to change host/port while warning about exposing the dashboard beyond local development.

#### Scenario: Offline-friendly asset serving
- **GIVEN** a user starts the dashboard on a machine without internet access
- **WHEN** they load the dashboard in a browser
- **THEN** all required assets (CSS, JavaScript, fonts) are served from the duckalog installation
- **AND** the dashboard is fully functional without external CDNs.

### Requirement: Dashboard Deployment Patterns
The documentation SHALL provide practical deployment patterns for the dashboard including local development, production deployment, and security configuration.

#### Scenario: Local development setup
- **GIVEN** a developer wanting to use the dashboard locally
- **WHEN** they follow the local development documentation
- **THEN** they find clear instructions for:
  - Installing UI dependencies (duckalog[ui])
  - Launching dashboard with default settings
  - Accessing dashboard at localhost
  - Understanding default security (no admin token in dev)
- **SO** they can quickly start using the dashboard for development

#### Scenario: Production deployment guidance
- **GIVEN** a user deploying dashboard in production
- **WHEN** they consult deployment documentation
- **THEN** they find production deployment guidance including:
  - Setting DUCKALOG_ADMIN_TOKEN for security
  - Configuring host and port binding
  - Understanding CORS implications
  - Background task behavior
  - Resource requirements
- **AND** they find example deployment configurations
- **SO** they can deploy securely and reliably

#### Scenario: Security configuration reference
- **GIVEN** a user configuring dashboard security
- **WHEN** they need security configuration details
- **THEN** they find reference documentation for:
  - Admin token environment variable
  - Read-only SQL enforcement (not configurable, always active)
  - CORS middleware configuration
  - Default security settings
  - Security best practices
- **SO** they can configure appropriate security for their deployment

