## ADDED Requirements

### Requirement: Litestar Application Framework
The dashboard SHALL use Litestar as the ASGI web framework instead of Starlette.

#### Scenario: Application initialization
- **GIVEN** the UI dependencies are installed
- **WHEN** the dashboard app is created via `create_app()`
- **THEN** a Litestar application instance is returned with configured routes and middleware

#### Scenario: Static file serving
- **GIVEN** a Litestar app is running
- **WHEN** a request is made to `/static/*`
- **THEN** static files are served from `src/duckalog/static/` directory

#### Scenario: Dependency injection
- **GIVEN** a route handler requires `DashboardContext`
- **WHEN** the handler is invoked
- **THEN** Litestar automatically injects the shared context instance

### Requirement: Datastar Integration
The dashboard SHALL use datastar-python SDK for real-time UI updates via server-sent events.

#### Scenario: Signal-based state management
- **GIVEN** a page with Datastar signals
- **WHEN** a user interacts with a form input
- **THEN** the corresponding signal is updated automatically via `data-bind` attribute

#### Scenario: Server-sent events for query results
- **GIVEN** a user submits a SQL query
- **WHEN** the query is executed on the backend
- **THEN** results are streamed via SSE using `ServerSentEventGenerator`
- **AND** the UI updates in real-time without page reload

#### Scenario: Real-time build status
- **GIVEN** a catalog build is triggered
- **WHEN** the build is in progress
- **THEN** build status updates are streamed via SSE
- **AND** the UI displays live progress without polling

### Requirement: Component-Based UI Architecture
The dashboard SHALL organize UI code into reusable components using starui.

#### Scenario: Layout components
- **GIVEN** a dashboard page needs common layout elements
- **WHEN** the page is rendered
- **THEN** layout components (header, navigation, footer) are used from `components/layout.py`

#### Scenario: Table components for views
- **GIVEN** a list of views needs to be displayed
- **WHEN** the views page is rendered
- **THEN** the table component from `components/tables.py` is used with starui styling

#### Scenario: Form components
- **GIVEN** a query input form is needed
- **WHEN** the query page is rendered
- **THEN** form components from `components/forms.py` are used with Datastar attributes

### Requirement: Modern Styling with Tailwind CSS
The dashboard SHALL use Tailwind CSS for utility-first styling and responsive design.

#### Scenario: Responsive layout
- **GIVEN** a user accesses the dashboard on a mobile device
- **WHEN** the page is rendered
- **THEN** the layout adapts using Tailwind responsive classes (sm:, md:, lg:)

#### Scenario: Dark/light theme support
- **GIVEN** a user wants to toggle between themes
- **WHEN** the theme toggle button is clicked
- **THEN** the UI switches between dark and light mode using Tailwind dark: classes

#### Scenario: Consistent spacing and typography
- **GIVEN** any dashboard page
- **WHEN** the page is rendered
- **THEN** consistent spacing (p-*, m-*, gap-*) and typography (text-*, font-*) are applied

### Requirement: Query Interface with Streaming Results
The dashboard SHALL provide an interactive query interface with real-time result streaming.

#### Scenario: Query submission
- **GIVEN** a user enters SQL in the query form
- **WHEN** the form is submitted
- **THEN** a POST request is sent to `/query/execute` with the SQL query

#### Scenario: Streaming query results
- **GIVEN** a query is being executed
- **WHEN** results are available
- **THEN** they are streamed via SSE as they're fetched from DuckDB
- **AND** the results table updates progressively

#### Scenario: Query error handling
- **GIVEN** a user submits invalid SQL
- **WHEN** the query fails
- **THEN** an error message is displayed via Datastar signal patch
- **AND** the error includes helpful details about what went wrong

#### Scenario: Loading indicators
- **GIVEN** a query is in progress
- **WHEN** results are being fetched
- **THEN** a loading indicator is displayed using `data-indicator` attribute
- **AND** the indicator disappears when results arrive

### Requirement: View Management Interface
The dashboard SHALL provide an interactive interface for browsing and searching views.

#### Scenario: View listing
- **GIVEN** a catalog with multiple views
- **WHEN** the views page is loaded
- **THEN** all views are displayed in a table with name, source, and semantic model status

#### Scenario: View search with Datastar
- **GIVEN** a user wants to find specific views
- **WHEN** text is entered in the search box
- **THEN** the view list filters in real-time using Datastar signals
- **AND** no page reload is required

#### Scenario: View detail page
- **GIVEN** a user clicks on a view name
- **WHEN** the detail page loads
- **THEN** the view's SQL definition and semantic model information are displayed

#### Scenario: Pagination for large catalogs
- **GIVEN** a catalog with more than 100 views
- **WHEN** the views page is loaded
- **THEN** results are paginated with navigation controls
- **AND** page size can be adjusted

### Requirement: CLI Command Integration
The dashboard CLI command SHALL be enabled and provide proper error handling.

#### Scenario: Starting the dashboard
- **GIVEN** the UI dependencies are installed
- **WHEN** `duckalog ui <config-path>` is executed
- **THEN** the dashboard starts on the specified host and port
- **AND** a startup message displays the URL

#### Scenario: Missing UI dependencies
- **GIVEN** the UI dependencies are NOT installed
- **WHEN** `duckalog ui` is executed
- **THEN** a clear error message is displayed
- **AND** installation instructions are provided: `pip install duckalog[ui]`

#### Scenario: CLI options
- **GIVEN** a user wants custom dashboard settings
- **WHEN** `duckalog ui --host 0.0.0.0 --port 8080 --row-limit 1000` is executed
- **THEN** the dashboard starts with the specified configuration

#### Scenario: Graceful shutdown
- **GIVEN** the dashboard is running
- **WHEN** the user presses Ctrl+C
- **THEN** the server shuts down gracefully
- **AND** any active SSE connections are closed properly

## MODIFIED Requirements

### Requirement: Dashboard Application Factory
The dashboard application factory SHALL create a Litestar app instead of a Starlette app, with proper configuration for static files, routes, and state management.

#### Scenario: App creation with context
- **GIVEN** a valid `DashboardContext` instance
- **WHEN** `create_app(context)` is called
- **THEN** a configured Litestar application is returned
- **AND** the context is available via dependency injection

#### Scenario: Route registration
- **GIVEN** a Litestar app is created
- **WHEN** the app is initialized
- **THEN** all dashboard routes are registered (/, /views, /views/{name}, /query)

#### Scenario: Static file configuration
- **GIVEN** a Litestar app is created
- **WHEN** the app is initialized
- **THEN** static file serving is configured for `/static` path

### Requirement: Dashboard State Management
The `DashboardContext` SHALL be compatible with Litestar's dependency injection system and manage catalog state efficiently.

#### Scenario: Context as dependency
- **GIVEN** a route handler requires catalog information
- **WHEN** the handler is invoked
- **THEN** the `DashboardContext` is automatically injected via Litestar

#### Scenario: DuckDB connection pooling
- **GIVEN** multiple concurrent queries are executed
- **WHEN** each query needs a database connection
- **THEN** connections are efficiently managed to avoid resource exhaustion

#### Scenario: Build status tracking
- **GIVEN** a catalog build is triggered
- **WHEN** the build status changes
- **THEN** the `DashboardContext.last_build` is updated
- **AND** SSE subscribers are notified of the change

### Requirement: HTML Generation
The dashboard SHALL generate HTML using type-safe Python functions instead of string templates, with proper Datastar attributes for reactivity.

#### Scenario: Type-safe HTML components
- **GIVEN** a component needs to render HTML
- **WHEN** the component function is called
- **THEN** HTML is generated using Python functions with type hints
- **AND** IDE provides autocomplete for element attributes

#### Scenario: Datastar attribute integration
- **GIVEN** an interactive UI element is rendered
- **WHEN** the HTML is generated
- **THEN** Datastar attributes (data-bind, data-on, data-signals) are properly included

#### Scenario: Component composition
- **GIVEN** a complex page layout
- **WHEN** the page is rendered
- **THEN** smaller components are composed together using Python function calls

## REMOVED Requirements

### Requirement: Starlette Framework Usage
**Reason**: Migrating to Litestar for better async support and dependency injection  
**Migration**: All Starlette-specific code will be replaced with Litestar equivalents

### Requirement: starhtml and starui Fallback Implementation
**Reason**: The 180-line fallback implementation in `views.py` is unmaintainable and produces poor UX  
**Migration**: Replace with proper dependencies and component architecture

### Requirement: Static HTML Generation
**Reason**: Moving to Datastar-based reactive UI for better user experience  
**Migration**: All static HTML pages will be enhanced with Datastar reactivity
