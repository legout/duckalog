# Design: Refactor Dashboard UI for Datastar

This document outlines the technical design for the Datastar‑based Duckalog dashboard described in `proposal.md`.

## 1. Architecture Overview

The dashboard remains a Starlette ASGI application but is restructured into clear layers:

- **State / Domain (`state.py`)**
  - `DashboardContext` owns:
    - Loaded `Config`
    - Optional `config_path`
    - `db_path` (DuckDB file)
    - `row_limit`
    - Last build status (`BuildStatus`)
  - Methods:
    - `view_list()`, `get_view(name)`, `semantic_for_view(name)`
    - `run_query(sql: str) -> QueryResult`
    - `trigger_build() -> BuildStatus`

- **HTML & Components (`html.py`)**
  - Provides Python-first HTML construction using a tag DSL (h2py/rustytags-style).
  - Wraps **StarUI** components and **BasecoatUI** class patterns to produce:
    - Layout skeleton (shell)
    - Cards, tables, forms, buttons

- **Datastar Integration (`datastar.py`)**
  - Integrates **datastar-python** with Starlette:
    - Defines Datastar signals for:
      - `summary` (config path, database, counts, last build)
      - `views` (list + filter)
      - `query` (sql text, status, columns, rows, truncated, error)
    - Exposes an SSE endpoint that streams Datastar events.
    - Provides helpers for generating Datastar `data-*` attributes.

- **App / Routing (`app.py`)**
  - Creates the Starlette app:
    - Mounts static assets (including `/static/datastar.js`).
    - Registers HTML routes and API routes.
    - Registers Datastar SSE endpoint.
  - Stores `DashboardContext` on `app.state.dashboard_ctx`.

- **CLI Integration (`cli.py`)**
  - Adds a `duckalog ui` command that constructs a `DashboardContext` and runs the app via Uvicorn.

## 2. Technology Choices

- **Web framework**: Starlette
  - Already used; minimal, ASGI-native, works well with SSE and Starlette TestClient.

- **HTML DSL**: h2py/rustytags-style tag API
  - Goal: replace ad‑hoc string concatenation and the starhtml fallback with a tested tag builder that:
    - Works well with Datastar (easy to attach `data-*` attributes).
    - Composes with StarUI components (e.g., `ui.card`, `ui.table`).

- **Components**: StarUI + BasecoatUI
  - StarUI:
    - Provides semantic component wrappers (cards, buttons, tables).
  - BasecoatUI:
    - Source of Tailwind-style utility classes for modern layout and responsive design.
    - Used via class strings in the tag DSL (no JS tooling required).

- **Reactivity**: Datastar JS + datastar-python SDK
  - Datastar JS is already vendored at `src/duckalog/static/datastar.js`.
  - datastar-python:
    - Generates Datastar attributes (`data-*`) from Python.
    - Provides SSE response helpers and `ServerSentEventGenerator`.

## 3. Routes and Endpoints

### 3.1 HTML Routes

All HTML routes share a common base layout:

- `GET /`
  - Renders overview/home page.
  - Includes:
    - Summary cards bound to `summary` signal.
    - “Build catalog” button with Datastar attributes to call `/api/build`.
    - Last build status derived from `summary.last_build`.
    - `<script src="/static/datastar.js" defer></script>`.

- `GET /views`
  - Renders views explorer.
  - Content:
    - Search input (bound to `views.filter` signal).
    - StarUI table bound to `views.items` signal.
  - Filtering is done via Datastar fetch to `/api/views`.

- `GET /views/{name}`
  - Renders view detail.
  - Uses `DashboardContext.get_view(name)` and `semantic_for_view(name)`.
  - Shows either SQL or a structured description of the source, plus semantic layer info.

- `GET /query`
  - Renders query panel.
  - Content:
    - SQL textarea bound to `query.sql`.
    - Run button with Datastar attributes to call `/api/query`.
    - Result table bound to `query.columns`, `query.rows`, `query.truncated`, `query.error`.

### 3.2 API Routes (JSON / Datastar)

These endpoints drive Datastar signals and are not intended for general public API use:

- `POST /api/build`
  - Body: none (or minimal metadata).
  - Behavior:
    - Calls `DashboardContext.trigger_build()`.
    - Computes updated summary (via `summarize_config` + build info).
    - Emits Datastar patch to `summary` signal with updated build status and timestamp.

- `GET /api/views`
  - Query param: `q` (optional).
  - Behavior:
    - Calls `DashboardContext.view_list()`.
    - Applies name filter if `q` provided.
    - Emits Datastar patch for `views.items` and `views.filter`.

- `POST /api/query`
  - Body: `{ "sql": "<user-sql>" }` or form-encoded equivalent.
  - Behavior:
    - Validates SQL as read-only (see §4.2).
    - If invalid, emits Datastar patch for:
      - `query.status = "error"`
      - `query.error = reason`
      - `query.rows = []`, `query.columns = []`.
    - If valid:
      - Calls `DashboardContext.run_query(sql)`.
      - Emits patches for `query.sql`, `query.columns`, `query.rows`, `query.truncated`, `query.error`, `query.status`.

### 3.3 Datastar SSE Endpoint

- `GET /events` (path name can be finalized during implementation)
  - Uses datastar-python’s Starlette integration to:
    - Accept a long-lived SSE connection.
    - Send Datastar events whenever signals are patched by API routes.
  - The HTML base layout configures Datastar JS to connect to this endpoint.

## 4. Backend Behavior Details

### 4.1 DashboardContext Responsibilities

`DashboardContext` is the single source of truth for catalog state:

- On initialization:
  - Stores `config`, `config_path`, `row_limit`.
  - Derives `db_path` from `config.duckdb.database`.

- For queries:
  - `run_query(sql)`:
    - Uses `duckdb.connect(db_path)` in a context manager.
    - Executes the provided SQL.
    - Fetches rows and column names.
    - Truncates results to `row_limit` and sets `truncated` flag.
    - Returns a `QueryResult` with `columns`, `rows`, `truncated`, `error`.

- For builds:
  - `trigger_build()`:
    - Starts a `BuildStatus` with `started_at`.
    - Calls `build_catalog(config_path)` (must have a non-None path).
    - On success:
      - Sets `success = True`, `summary = "Catalog build completed"`.
    - On `EngineError`:
      - Logs via existing logging utilities.
      - Sets `success = False`, `message = str(exc)`.
    - Always sets `completed_at` at the end.

### 4.2 Read-Only SQL Enforcement

The query API must ensure only safe, read‑only queries run:

- Minimal strategy:
  - Trim leading whitespace and comments.
  - Check the first non-comment token:
    - Allow only `SELECT` (case-insensitive) and possibly `WITH` (if followed by a `SELECT`).
  - Reject anything starting with `INSERT`, `UPDATE`, `DELETE`, `CREATE`, `ALTER`, `DROP`, `TRUNCATE`, or other DDL/DML.
  - On rejection:
    - Do not call DuckDB.
    - Return a clear error message and non-success status for UI display.

- Extension:
  - If future requirements demand more nuanced checks, extract this logic into a dedicated helper and add unit tests.

## 5. HTML and Component Design

### 5.1 Base Layout

The base layout built in `html.py` should:

- Include:
  - `<head>` with title and a CSS link (BasecoatUI/Tailwind-like classes).
  - `<script src="/static/datastar.js" defer></script>`.
  - Any Datastar bootstrap configuration needed (e.g. event endpoint path).
- Provide a consistent shell:
  - Top bar with project name, build status pill, and “Build catalog” button.
  - Side navigation (Home, Views, Query, Semantic Layer / future).
  - Main content area where per-page content is injected.

### 5.2 Pages

- **Overview**
  - Responsive card grid:
    - Catalog path
    - DuckDB path
    - View count
    - Attachment count
    - Semantic model count
    - Last build status

- **Views**
  - Search bar at top:
    - Datastar attributes bound to `views.filter` and `/api/views`.
  - StarUI table:
    - Uses BasecoatUI classes for striped rows, hover states, etc.

- **View Detail**
  - Card for view definition.
  - Card(s) for semantic models (dimensions, measures).

- **Query**
  - Large textarea card for SQL.
  - Primary button for “Run”.
  - Results card with table and status line (rows count, truncated state, error if any).

## 6. CLI Design (`duckalog ui`)

Add a Starlette-backed CLI command:

- Signature (high-level):
  - `duckalog ui [CONFIG_PATH] --host HOST --port PORT --row-limit ROW_LIMIT`
- Behavior:
  - Validates `CONFIG_PATH` exists (or fails with clear error).
  - Creates a `DashboardContext.from_path(config_path, row_limit=row_limit)`.
  - Calls `create_app(context)` from `dashboard.app`.
  - Runs via Uvicorn.
  - Prints:
    - `Starting dashboard at http://{host}:{port}`
    - Warning when `host` is not a loopback address.

## 7. Migration and Compatibility

- Preserve `DashboardContext` shape so existing tests can be adapted rather than rewritten.
- Keep Starlette and Uvicorn versions compatible with current `duckalog[ui]` extras.
- Ensure that:
  - `/static/datastar.js` remains the path for the Datastar bundle.
  - Tests only need updates for the new Datastar HTML and API behavior, not total rewrites.

This design is intended to be incremental: the existing dashboard can be refactored screen-by-screen into this structure while keeping Starlette, DuckDB, and core config logic stable. 

