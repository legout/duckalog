## MODIFIED Requirements

### Requirement: Dashboard Home Overview
The dashboard home page SHALL present a modern, styled overview of the selected catalog with real-time build status updates and navigation to other dashboard sections using StarUI components and Tailwind CSS styling.

#### Scenario: Home shows catalog summary with styled components
- **GIVEN** the dashboard is launched for a valid catalog
- **WHEN** the user visits the home page
- **THEN** they see the catalog information displayed in a Card component with proper styling
- **AND** counts are shown using Badge components
- **AND** navigation uses styled Button components
- **AND** the page has responsive layout with Tailwind CSS classes
- **AND** the page links to the views browser, query runner, and build status sections.

#### Scenario: Home shows real-time build status
- **GIVEN** the catalog has been built at least once in the current process
- **WHEN** the user visits the home page
- **THEN** they see the build status displayed in an Alert component
- **AND** the status updates in real-time via Server-Sent Events without page refresh
- **AND** a link or button to view more detailed build status information is styled with Button component.

### Requirement: Views Browser
The dashboard SHALL provide a modern views browser with styled table, real-time search filtering, and pagination controls using StarUI Table component and Datastar reactivity.

#### Scenario: List views with styled table
- **GIVEN** a catalog with one or more views
- **WHEN** the user navigates to the views browser
- **THEN** they see a StarUI Table component with proper styling
- **AND** each row includes view name, source type, location, and semantic indicator Badge
- **AND** the table has pagination controls for large datasets
- **AND** each row indicates whether the view participates in the semantic layer using a Badge component.

#### Scenario: Filter views by name with real-time updates
- **GIVEN** a catalog with many views
- **WHEN** the user types a partial view name into the search input
- **THEN** the views table filters instantly using Datastar signals (client-side filtering)
- **AND** no page reload occurs
- **AND** clearing the search restores the full list
- **AND** search input uses StarUI Input component with proper styling.

#### Scenario: Navigate to view detail with styled interaction
- **GIVEN** the user is viewing the views browser
- **WHEN** they click on a specific view name
- **THEN** they are taken to a view detail page for that view
- **AND** the link is styled appropriately with hover states.

### Requirement: View Detail and Semantic Metadata
The dashboard SHALL provide a detail page for each view with syntax-highlighted SQL, tabbed interface for different sections, and styled semantic metadata display using StarUI Card components.

#### Scenario: Show core view definition with syntax highlighting
- **GIVEN** a view is defined in the catalog
- **WHEN** the user navigates to that view's detail page
- **THEN** they see the view information in a Card component
- **AND** SQL code is displayed with syntax highlighting
- **AND** configuration fields are formatted and styled appropriately
- **AND** the page uses tabs to separate Definition, Schema, and Semantic sections.

#### Scenario: Show semantic-layer information with styled components
- **GIVEN** the view participates in the semantic layer with defined dimensions and measures
- **WHEN** the user navigates to that view's detail page
- **THEN** they see semantic information in a separate Card component
- **AND** dimensions and measures are displayed in a formatted list or table
- **AND** the page makes clear when a view has no semantic-layer metadata using an Alert component.

### Requirement: Ad-hoc Query Runner
The dashboard SHALL provide a modern SQL query runner with syntax highlighting, real-time streaming results, query history, and export capabilities using Datastar SSE and StarUI components.

#### Scenario: Run query and display results with real-time streaming
- **GIVEN** the dashboard is connected to a valid catalog
- **WHEN** the user enters a SELECT query and submits it
- **THEN** the query streams results in real-time via Server-Sent Events
- **AND** results appear progressively as they are fetched (chunks of 100 rows)
- **AND** a loading indicator shows while query is executing
- **AND** the results are shown in a styled StarUI Table component
- **AND** query execution does not block the UI.

#### Scenario: Enforce result limits with visual indicators
- **GIVEN** a query would return more than the configured maximum number of rows
- **WHEN** the user runs the query from the dashboard
- **THEN** only up to the configured maximum rows are displayed
- **AND** a Badge component indicates that results have been truncated
- **AND** the truncation message specifies how many total rows were found.

#### Scenario: Show query errors with styled alerts
- **GIVEN** a query contains invalid SQL or fails at execution time
- **WHEN** the user runs the query from the dashboard
- **THEN** the error is displayed in an Alert component with "destructive" variant
- **AND** the error message is formatted for readability
- **AND** the previous successful results (if any) are cleared
- **AND** a retry button is available.

### Requirement: Build Trigger and Status
The dashboard SHALL allow users to trigger a catalog build with real-time status updates via Server-Sent Events using styled components and non-blocking background execution.

#### Scenario: Trigger build with styled UI feedback
- **GIVEN** the dashboard is connected to a valid catalog config
- **WHEN** the user clicks the "Build catalog" Button component
- **THEN** a catalog build starts in the background (non-blocking)
- **AND** the Button component is disabled during build
- **AND** a loading spinner appears using Datastar indicator
- **AND** the build uses the same semantics as the CLI build command.

#### Scenario: Show real-time build progress and completion
- **GIVEN** a build is in progress via the dashboard
- **WHEN** the build executes
- **THEN** status updates stream via Server-Sent Events to the client
- **AND** the UI updates in real-time without page refresh
- **AND** upon completion, an Alert component shows success or failure
- **AND** a summary includes number of views created/updated
- **AND** any failure includes a concise, formatted error message.

### Requirement: Implementation Stack and Constraints
The dashboard implementation SHALL use StarUI component library with Datastar for reactivity, require these dependencies explicitly, and remove the fallback compatibility layer for cleaner codebase.

#### Scenario: Implemented with StarUI and Datastar (no fallback)
- **GIVEN** the dashboard UI is built for this capability
- **WHEN** the implementation is inspected
- **THEN** the HTML views use StarUI components (Button, Card, Alert, Badge, Table, Input)
- **AND** Datastar is used for real-time reactivity and SSE streaming
- **AND** no fallback compatibility layer exists (removed from views.py)
- **AND** starhtml, starui, and datastar-python are required dependencies in `[ui]` extra
- **AND** no separate JavaScript build toolchain is required.

#### Scenario: Modern styling with Tailwind CSS
- **GIVEN** the dashboard pages are rendered
- **WHEN** viewed in a browser
- **THEN** Tailwind CSS v4 provides utility-first styling
- **AND** StarUI components include proper shadcn/ui-inspired design
- **AND** the interface is responsive (desktop-first, mobile-friendly)
- **AND** consistent spacing, typography, and color scheme throughout.

#### Scenario: Offline-friendly asset serving
- **GIVEN** a user starts the dashboard on a machine without internet access
- **WHEN** they load the dashboard in a browser
- **THEN** Datastar.js is served from local assets
- **AND** Tailwind CSS is loaded via CDN (requires internet) OR bundled locally
- **AND** the dashboard is fully functional without external CDNs for core functionality.

## ADDED Requirements

### Requirement: Query History
The dashboard SHALL maintain a browser-based query history using localStorage, allowing users to view and reuse recent queries without server-side storage.

#### Scenario: Save queries to history automatically
- **GIVEN** a user successfully executes a query
- **WHEN** the query completes
- **THEN** the query text and timestamp are saved to browser localStorage
- **AND** the history maintains the last 20 queries (FIFO)
- **AND** duplicate queries update the timestamp rather than creating new entries.

#### Scenario: View and load queries from history
- **GIVEN** the user has query history saved
- **WHEN** they open the query history panel
- **THEN** they see a list of recent queries with timestamps
- **AND** clicking a query loads it into the SQL editor
- **AND** the history is sorted by most recent first
- **AND** queries are displayed with truncated preview (first 50 characters).

#### Scenario: Clear query history
- **GIVEN** query history exists
- **WHEN** the user clicks "Clear History" button
- **THEN** all history is removed from localStorage
- **AND** a confirmation dialog prevents accidental deletion
- **AND** the history panel shows empty state message.

### Requirement: Data Export
The dashboard SHALL support exporting query results to CSV (client-side) and Parquet (server-side) formats with appropriate size limits and user feedback.

#### Scenario: Export results to CSV (client-side)
- **GIVEN** query results are displayed
- **WHEN** the user clicks "Export CSV" button
- **THEN** a CSV file is generated from the table data in the browser
- **AND** the browser downloads the file with a timestamp in the filename
- **AND** exports are limited to 10,000 rows with a warning if limit is exceeded
- **AND** all column types are properly formatted in CSV.

#### Scenario: Export results to Parquet (server-side)
- **GIVEN** query results are displayed
- **WHEN** the user clicks "Export Parquet" button
- **THEN** a request is sent to the server with the SQL query
- **AND** the server uses DuckDB COPY command to generate a Parquet file
- **AND** the Parquet file is downloaded via FileResponse
- **AND** exports are limited to 1,000,000 rows with error message if exceeded
- **AND** temporary files are cleaned up after download.

#### Scenario: Show export limits and warnings
- **GIVEN** query results exceed export limits
- **WHEN** the user attempts to export
- **THEN** a warning Alert component appears before export
- **AND** the warning specifies which rows will be included
- **AND** the user can confirm or cancel the export
- **AND** export button shows loading state during generation.

### Requirement: SQL Syntax Highlighting
The dashboard SHALL provide syntax highlighting for SQL code in the query editor and view detail pages using a JavaScript syntax highlighting library.

#### Scenario: Highlight SQL in query editor
- **GIVEN** the user is on the query page
- **WHEN** they type or paste SQL into the editor
- **THEN** SQL keywords are highlighted in a distinct color
- **AND** strings, numbers, and comments use different styling
- **AND** highlighting updates in real-time as user types
- **AND** the editor remains editable (not read-only).

#### Scenario: Display highlighted SQL in view details
- **GIVEN** a view has a SQL definition
- **WHEN** the user views the view detail page
- **THEN** the SQL is displayed with syntax highlighting
- **AND** line numbers are shown for multi-line queries
- **AND** the code is displayed in a monospace font
- **AND** a "Copy" button allows copying the raw SQL.

### Requirement: Visual Query Builder
The dashboard SHALL provide a simple visual query builder for constructing SELECT queries through a UI rather than writing SQL, supporting basic view selection, column filtering, and WHERE clauses.

#### Scenario: Build query by selecting view and columns
- **GIVEN** the user opens the visual query builder
- **WHEN** they select a view from the dropdown
- **THEN** the available columns are loaded and displayed as checkboxes
- **AND** selecting/deselecting columns updates the SQL preview
- **AND** the generated SQL shows: SELECT [selected columns] FROM [view]
- **AND** all columns are selected by default.

#### Scenario: Add simple WHERE filters
- **GIVEN** a view is selected in the query builder
- **WHEN** the user clicks "Add Filter"
- **THEN** a new filter row appears with column, operator, and value inputs
- **AND** the column dropdown shows all available columns
- **AND** operators include: =, !=, >, <, >=, <=, LIKE, IN
- **AND** the value input accepts text or numbers
- **AND** adding a filter updates the SQL preview with WHERE clause.

#### Scenario: Generate and run SQL from builder
- **GIVEN** the user has configured a query in the builder
- **WHEN** they click "Run Query"
- **THEN** the generated SQL is executed using the same flow as manual queries
- **AND** results stream to the table in real-time
- **AND** the query is added to history
- **AND** clicking "Copy SQL" copies the generated SQL to clipboard.

#### Scenario: Query builder limitations are clear
- **GIVEN** the user is using the visual query builder
- **WHEN** they attempt complex operations
- **THEN** JOINs, subqueries, and aggregations are not available in the UI
- **AND** a message indicates "For complex queries, use the SQL editor"
- **AND** the builder only supports AND logic for multiple filters (no OR)
- **AND** generated SQL can be copied to editor for manual enhancement.

### Requirement: Keyboard Shortcuts
The dashboard SHALL provide keyboard shortcuts for common operations to improve power user efficiency and accessibility.

#### Scenario: Run query with keyboard shortcut
- **GIVEN** the user has SQL in the query editor
- **WHEN** they press Ctrl+Enter (Cmd+Enter on Mac)
- **THEN** the query executes immediately
- **AND** focus remains in the editor
- **AND** the shortcut works regardless of cursor position.

#### Scenario: Focus search with keyboard shortcut
- **GIVEN** the user is on any dashboard page with a search input
- **WHEN** they press Ctrl+K (Cmd+K on Mac)
- **THEN** the search input receives focus
- **AND** any existing text is selected for easy replacement
- **AND** the shortcut is documented in the UI.

#### Scenario: Close modals with Escape
- **GIVEN** a modal or drawer is open (query history, export options, etc.)
- **WHEN** the user presses Escape
- **THEN** the modal/drawer closes
- **AND** focus returns to the previous element
- **AND** any unsaved changes are preserved or prompt for confirmation.

### Requirement: Responsive Table Pagination
The dashboard SHALL provide pagination controls for large result sets to prevent performance issues and improve user experience with configurable page size.

#### Scenario: Paginate large result sets
- **GIVEN** a query returns more than the page size (default 50 rows)
- **WHEN** results are displayed
- **THEN** only the first page of results is shown initially
- **AND** pagination controls appear below the table
- **AND** controls show: current page, total pages, and total rows
- **AND** "Previous" and "Next" buttons navigate between pages.

#### Scenario: Configure page size
- **GIVEN** results are paginated
- **WHEN** the user selects a different page size (25, 50, 100, 500)
- **THEN** the table re-renders with the new page size
- **AND** the current page resets to 1
- **AND** the selection persists in localStorage for future queries
- **AND** very large page sizes show a warning about performance.

#### Scenario: Pagination with streaming results
- **GIVEN** results are streaming via SSE
- **WHEN** the first page is filled (e.g., 50 rows)
- **THEN** pagination controls appear
- **AND** "Next" button is disabled until more pages are loaded
- **AND** a loading indicator shows on the "Next" button when loading
- **AND** users can navigate already-loaded pages while streaming continues.

### Requirement: Loading States and Progress Indicators
The dashboard SHALL provide clear visual feedback for all asynchronous operations using loading indicators, disabled states, and progress information.

#### Scenario: Show loading state during query execution
- **GIVEN** a query is submitted
- **WHEN** the query is executing
- **THEN** a loading spinner appears using Datastar indicator
- **AND** the "Run Query" button is disabled and shows loading state
- **AND** the results area shows a skeleton loader or progress message
- **AND** the loading state clears when results arrive or error occurs.

#### Scenario: Show loading state during build
- **GIVEN** a catalog build is triggered
- **WHEN** the build is in progress
- **THEN** the "Build Catalog" button shows a loading spinner
- **AND** the button is disabled during build
- **AND** a progress message indicates "Building catalog..."
- **AND** the home page build status indicator updates in real-time.

#### Scenario: Show loading state for data fetching
- **GIVEN** any page loads that requires fetching data (view list, view details)
- **WHEN** the data is being fetched
- **THEN** a skeleton loader displays in place of content
- **AND** the skeleton matches the expected layout (cards, tables, etc.)
- **AND** the skeleton disappears when real content loads
- **AND** errors show Alert component instead of skeleton.

### Requirement: Enhanced Error Presentation
The dashboard SHALL present errors in a user-friendly format with helpful context, suggestions for resolution, and styled Alert components rather than raw error text.

#### Scenario: Format SQL errors with context
- **GIVEN** a SQL query fails with a syntax error
- **WHEN** the error is displayed
- **THEN** an Alert component with "destructive" variant shows the error
- **AND** the error message is formatted with line breaks for readability
- **AND** if available, the error shows the problematic SQL line
- **AND** suggestions for common fixes are provided (e.g., "Check for missing quotes").

#### Scenario: Format connection errors clearly
- **GIVEN** the dashboard cannot connect to the DuckDB database
- **WHEN** the error occurs
- **THEN** an Alert explains the connection failed
- **AND** the database path is shown (if not sensitive)
- **AND** suggestions include: check file permissions, verify path, ensure database exists
- **AND** a retry button allows attempting reconnection.

#### Scenario: Show multiple errors grouped together
- **GIVEN** multiple errors occur (e.g., during build with multiple view failures)
- **WHEN** errors are displayed
- **THEN** errors are grouped in an expandable Alert component
- **AND** a summary shows "3 errors occurred - click to expand"
- **AND** expanding shows each error in a formatted list
- **AND** each error can be copied individually for debugging.
