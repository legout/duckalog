# dashboard-ui Specification

## Purpose
Provide a local-first, Litestar- and Datastar-powered dashboard for inspecting and operating a single Duckalog catalog. The UI favors basecoatui components first, uses custom htpy components with Tailwind utilities when basecoatui lacks the needed element, and never uses starui.

## Requirements

### Requirement: Litestar + Datastar Application Stack
The dashboard SHALL run on Litestar with Datastar for reactive updates and htpy for type-safe HTML composition.

#### Scenario: Application initialization
- **GIVEN** the UI extras are installed
- **WHEN** `create_app(context)` is called
- **THEN** a Litestar application is returned with registered routes, middleware, and dependency injection wired for `DashboardContext`.

#### Scenario: Static file serving
- **GIVEN** the app is running
- **WHEN** a request is made to `/static/*`
- **THEN** assets (prebuilt CSS/JS/fonts) are served from the packaged `duckalog/static/` directory without requiring internet access.

#### Scenario: Dependency injection
- **GIVEN** a route declares `DashboardContext`
- **WHEN** the handler executes
- **THEN** Litestar injects the shared context instance for use in the handler.

### Requirement: Legacy Dashboard Clean Slate
The new dashboard SHALL not reuse or restore code, templates, or assets from the removed legacy dashboard implementation.

#### Scenario: No legacy file resurrection
- **WHEN** implementing the new dashboard
- **THEN** no deleted legacy dashboard modules, templates, or static assets are restored from version control or prior releases; all components/routes/state are newly implemented on the Litestar/Datastar stack.

### Requirement: Component and Styling Priority (Basecoatui First)
The dashboard SHALL prefer basecoatui components for UI and styling; it SHALL use custom htpy components with Tailwind utility classes when basecoatui lacks the needed element; starui MUST NOT be used.

#### Scenario: Basecoatui by default
- **WHEN** implementing a UI element that exists in basecoatui
- **THEN** the basecoatui variant is used (including its CSS/JS) and delivered via CDN as a temporary measure.

#### Scenario: Custom htpy components when basecoatui lacks
- **WHEN** basecoatui lacks the needed pattern or accessibility baseline
- **THEN** a small htpy-based component is created and styled with Tailwind utility classes
- **AND** its styles and behavior are bundled in `static/`.

#### Scenario: Tailwind fallback only
- **WHEN** no basecoatui component fits the need
- **THEN** Tailwind utility classes are used to compose the UI with htpy
- **AND** the compiled Tailwind CSS is shipped in `static/tailwind.css` with no CDN requirement for production.

### Requirement: Type-Safe HTML Generation
The dashboard SHALL generate HTML via htpy (or equivalent typed helpers) with Datastar attributes for reactivity.

#### Scenario: Component rendering
- **WHEN** a page is rendered
- **THEN** HTML is produced by Python functions with type hints
- **AND** Datastar attributes (`data-bind`, `data-on`, `data-signal`) are present where interactivity is required.

#### Scenario: Composition
- **WHEN** building complex layouts
- **THEN** smaller typed components are composed without raw string templates.

### Requirement: Security Posture and Defaults
The dashboard SHALL default to a secure, local-only posture with explicit opt-in for wider exposure.

#### Scenario: Loopback binding and CORS
- **WHEN** the server starts without overrides
- **THEN** it binds to `127.0.0.1` and enforces CORS to the same origin.

#### Scenario: Warning on public bind
- **WHEN** the user starts the dashboard on `0.0.0.0` or a non-loopback host without an admin token
- **THEN** the CLI emits a warning describing the risk and how to set `DUCKALOG_ADMIN_TOKEN`.

#### Scenario: Admin token for mutating actions
- **WHEN** a build or other mutating endpoint is called
- **THEN** the request is rejected unless the configured admin token is supplied.

#### Scenario: Read-only SQL enforcement
- **WHEN** a query is submitted
- **THEN** only `SELECT` statements are allowed; DDL/DML statements are rejected with a clear error.

#### Scenario: Sensitive data redaction
- **WHEN** requests or errors are logged
- **THEN** connection strings, secrets, and tokens are redacted from logs.

### Requirement: Temporary CDN Asset Delivery
UI assets MAY be delivered via CDN as a temporary measure to expedite shipping. This is an interim solution pending proper bundling.

#### Scenario: CDN asset loading
- **WHEN** the dashboard is loaded with internet access
- **THEN** Tailwind CSS, Basecoat CSS, and Datastar JS are loaded from CDNs (jsDelivr, cdn.tailwindcss.com) for rapid development and deployment.

#### Scenario: Offline limitations
- **WHEN** the dashboard is opened without internet access
- **THEN** the UI will not function fully as CDN assets are unavailable; this is an accepted limitation during the interim CDN period.

#### Scenario: Future bundling
- **WHEN** the interim period ends
- **THEN** all assets will be bundled locally for offline support as originally specified; this CDN approach is temporary and will be replaced with proper offline asset bundling.

### Requirement: Dashboard Home Overview
The home page SHALL summarize the catalog and recent activity.

#### Scenario: Catalog summary
- **WHEN** the home page loads
- **THEN** it shows config path, DuckDB file location, counts of views/attachments/semantic models, and navigation to views, query, and build sections.

#### Scenario: Live build status
- **WHEN** a build is in progress or has completed
- **THEN** current status (progress or last result with timestamp) is displayed and updated live via Datastar.

### Requirement: Views Browser
The dashboard SHALL list views with metadata and support fast filtering.

#### Scenario: List views
- **WHEN** the views page is opened
- **THEN** a table (basecoatui preferred) shows name, source type, location/attachment, and semantic-layer flag for each view.

#### Scenario: Search/filter
- **WHEN** text is entered in the search box
- **THEN** results filter in real time using Datastar signals without page reload.

#### Scenario: Pagination
- **WHEN** more than 100 views exist
- **THEN** pagination controls appear with adjustable page size.

#### Scenario: View detail navigation
- **WHEN** a view row is selected
- **THEN** the user is taken to a detail page showing its SQL/config and semantic metadata (if any).

### Requirement: Query Runner with Streaming and Limits
The dashboard SHALL provide a read-only query runner with streaming results and guardrails.

#### Scenario: Query submission and streaming
- **WHEN** a SELECT query is submitted
- **THEN** results stream via SSE as they are produced and render progressively in the table.

#### Scenario: Row limit and truncation
- **WHEN** a query returns more than the configured row limit (default 500; configurable via CLI and UI)
- **THEN** only the allowed rows are delivered
- **AND** the UI indicates results were truncated.

#### Scenario: Timeout and cancellation
- **WHEN** a query exceeds the max execution time or the client disconnects
- **THEN** execution is cancelled and the user sees a timeout/cancel notice.

#### Scenario: Error handling
- **WHEN** a query fails validation or execution
- **THEN** the error message is surfaced clearly without exposing internal stack traces.

### Requirement: Build Trigger and Status Streaming
The dashboard SHALL trigger builds and stream their status safely.

#### Scenario: Debounced build trigger
- **WHEN** a user clicks “Build catalog” repeatedly
- **THEN** only one build starts until the current build finishes or fails.

#### Scenario: Status stream
- **WHEN** a build runs
- **THEN** progress and final status stream over SSE, including counts of created/updated views and a short failure summary when applicable.

#### Scenario: Concurrency guard
- **WHEN** a second build request arrives during an active build
- **THEN** it is rejected with an informative message.

### Requirement: SSE Resilience and Limits
The dashboard SHALL manage SSE resources and degrade gracefully.

#### Scenario: Connection cap
- **WHEN** the number of SSE clients exceeds the configured limit
- **THEN** new connections are refused with a clear message.

#### Scenario: Heartbeat and reconnect
- **WHEN** an SSE connection idles
- **THEN** heartbeat events keep it alive; clients back off and retry with exponential delay on failure.

#### Scenario: Polling fallback
- **WHEN** SSE repeatedly fails (e.g., after N retries)
- **THEN** the UI falls back to periodic polling for status/results.

### Requirement: CLI Command Integration
The CLI SHALL start the dashboard with configurable options and robust messaging.

#### Scenario: Start with options
- **WHEN** the user runs `duckalog ui --host 0.0.0.0 --port 8080 --row-limit 1000 catalog.yaml`
- **THEN** the server starts with those settings and prints the access URL.

#### Scenario: Missing dependencies
- **WHEN** UI extras are not installed
- **THEN** the command exits with an actionable message: `pip install duckalog[ui]`.

#### Scenario: Insecure bind warning
- **WHEN** host is non-loopback and no admin token is set
- **THEN** the CLI prints a security warning before starting.

#### Scenario: Graceful shutdown
- **WHEN** the user presses Ctrl+C
- **THEN** the server stops cleanly and active SSE streams are closed.

### Requirement: Documentation Accuracy
Documentation SHALL match the implemented stack and capabilities and omit unimplemented features.

#### Scenario: Stack correctness
- **WHEN** users read the docs
- **THEN** they see Litestar + Datastar + htpy with basecoatui-first, Tailwind-fallback styling order, and no references to starui or starhtml.

#### Scenario: Security coverage
- **WHEN** deployment guidance is read
- **THEN** it documents admin token usage, read-only SQL enforcement, CORS/binding defaults, and log redaction.

#### Scenario: Feature scope clarity
- **WHEN** capabilities are listed
- **THEN** they include view browsing/detail, search, query runner with streaming, and build status; they do NOT promise view create/edit/delete or data export unless implemented.

#### Scenario: Migration guidance
- **WHEN** users move from the legacy dashboard
- **THEN** docs provide migration steps, changed commands, and screenshot examples of the new UI.
