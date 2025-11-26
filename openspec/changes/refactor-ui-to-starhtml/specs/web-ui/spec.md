## MODIFIED Requirements

### Requirement: Launchable catalog dashboard
The system MUST provide a way to start a web UI that targets a specific Duckalog config file and underlying DuckDB catalog, with improved maintainability through StarHTML framework.

#### Scenario: UI starts with StarHTML rendering
- **GIVEN** `duckalog` is installed with StarHTML dependencies and a valid config file path exists
- **WHEN** the user runs a CLI command such as `duckalog ui <config-path>` with StarHTML enabled
- **THEN** a Starlette-based app starts on localhost with StarHTML-based dashboard rendering
- **AND** opening that address in a browser shows the catalog dashboard with type-safe reactive components

#### Scenario: UI maintains backward compatibility
- **GIVEN** existing users without StarHTML dependencies
- **WHEN** the user runs the UI command without StarHTML available
- **THEN** the system falls back to the existing HTML string implementation
- **AND** all existing functionality continues to work unchanged

### Requirement: View catalog metadata
Users MUST be able to see the configured catalog views and basic metadata from the dashboard, implemented with type-safe StarHTML components.

#### Scenario: Views list uses reactive StarHTML components
- **GIVEN** a valid Duckalog config with one or more views and StarHTML rendering enabled
- **WHEN** the user opens the dashboard
- **THEN** the page shows a reactive table of all views using StarHTML components including at least the view name, source type, and optional description
- **AND** selecting a view shows additional details through StarHTML signal-driven updates without page reload

### Requirement: Manage catalog views
Users MUST be able to add, update, and delete view entries through the UI using StarHTML forms with proper signal handling.

#### Scenario: View creation uses StarHTML form components
- **GIVEN** StarHTML rendering enabled and a user accessing the view creation interface
- **WHEN** the user submits a create request through StarHTML form with real-time validation
- **THEN** the server processes the request using existing backend logic
- **AND** StarHTML signals automatically update the view list without manual DOM manipulation

#### Scenario: View deletion uses reactive confirmation
- **GIVEN** a request to delete an existing view with StarHTML rendering
- **WHEN** the user confirms deletion through a StarHTML modal/dialog component
- **THEN** the signal-driven request updates the server state
- **AND** StarHTML automatically removes the view from the list with smooth transitions

### Requirement: Querying and data export
Users MUST be able to preview data, run more complex queries, and export results using StarHTML components with improved type safety and error handling.

#### Scenario: Query interface uses StarHTML editor
- **GIVEN** StarHTML rendering enabled and a user accessing the query interface
- **WHEN** the user enters and submits a query through the StarHTML SQL editor component
- **THEN** reactive signals handle query submission and results display
- **AND** results appear in a type-safe table component with proper error boundaries

#### Scenario: Export uses StarHTML download components
- **GIVEN** query results displayed in StarHTML interface
- **WHEN** the user selects an export format through StarHTML dropdown components
- **THEN** signal-driven request triggers file download
- **AND** visual feedback shows export progress and completion

### Requirement: Datastar-driven interactivity
The dashboard MUST use Datastar attributes integrated through StarHTML's type-safe signal system for enhanced reliability and maintainability.

#### Scenario: StarHTML provides type-safe Datastar integration
- **GIVEN** StarHTML rendering enabled for any UI interaction
- **WHEN** the user performs actions through StarHTML components
- **THEN** all Datastar attributes are generated through StarHTML's Python DSL with type safety
- **AND** no manual HTML string embedding of Datastar attributes is required
- **AND** signal type checking prevents runtime errors from malformed expressions

## ADDED Requirements

### Requirement: Configurable UI rendering framework
The system MUST support configuration to choose between StarHTML and legacy HTML string rendering modes.

#### Scenario: Framework selection via environment
- **GIVEN** both StarHTML and legacy dependencies are available
- **WHEN** the administrator sets `DUCKALOG_UI_FRAMEWORK=starhtml` environment variable
- **THEN** the dashboard renders using StarHTML components
- **AND** setting `DUCKALOG_UI_FRAMEWORK=legacy` uses the original implementation

#### Scenario: Automatic framework detection
- **GIVEN** duckalog UI command is executed without explicit framework preference
- **WHEN** StarHTML dependencies are available
- **THEN** the system automatically prefers StarHTML rendering
- **AND** falls back to legacy mode only if StarHTML is unavailable

### Requirement: Type-safe component development
StarHTML components MUST provide type safety and IDE support for dashboard development.

#### Scenario: Component type checking
- **GIVEN** development environment with StarHTML
- **WHEN** developing UI components
- **THEN** all signals and expressions benefit from Python type hints
- **AND** IDE autocomplete works for component properties and signal operations
- **AND** type errors are caught at development time rather than runtime