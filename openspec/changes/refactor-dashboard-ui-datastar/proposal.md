# Change: Refactor Dashboard UI for Datastar

## Why

The current Duckalog dashboard implementation has drifted significantly from the documented and tested behavior:

- Documentation and tests describe a Datastar + Starlette-based reactive dashboard with a locally served `datastar.js` bundle and a `duckalog ui` CLI entrypoint.
- The current code renders mostly static HTML using a thin starhtml/starui compatibility layer plus a large, unstyled fallback, with no Datastar integration and no use of `datastar-python`.
- The dashboard UI is visually minimal and not aligned with a modern component library; there is no consistent design system, and behavior like read-only SQL enforcement is not clearly implemented.
- The `duckalog ui` CLI command is commented out, so docs and examples that mention it do not work as described.

We want a clear, modern, Datastar-first dashboard that:

- Uses the agreed tech stack (Starlette, StarUI/BasecoatUI, Datastar + datastar-python, h2py/rustytags-style HTML generation).
- Matches the documented feature set (reactive dashboard, locally served Datastar bundle, read-only ad-hoc queries, catalog build controls).
- Is easy to extend and maintain.

## What Changes

- **Framework and app structure (Starlette-based)**
  - Keep Starlette as the ASGI framework for the dashboard.
  - Restructure the dashboard package into clearer modules:
    - `dashboard/app.py`: Starlette app factory, routes, middleware, and static mounts.
    - `dashboard/state.py`: Catalog context, DuckDB access, and build/query helpers.
    - `dashboard/html.py`: HTML/component helpers using a Python tag DSL (e.g. h2py/rustytags-style API).
    - `dashboard/datastar.py`: Datastar integration (signals, SSE endpoints, attribute helpers).
  - Mount static assets so that the Datastar JS bundle is served at `/static/datastar.js` as documented.

- **HTML templating and components**
  - Replace the current ad-hoc starhtml fallback and manual HTML string building with a proper Python-first HTML DSL:
    - Use a tag library compatible with Datastar and StarUI (e.g. h2py/rustytags-style tags) for building HTML from Python.
  - Use **StarUI** components as the primary building blocks (cards, buttons, tables, form inputs).
  - Apply **BasecoatUI** (or a similar Tailwind-style design system) classnames to ensure:
    - A consistent, modern look across pages (layout, typography, buttons, tables, forms).
    - Good defaults for spacing, contrast, and responsiveness without a separate frontend build pipeline.

- **Datastar + datastar-python integration**
  - Integrate the **Datastar JS** bundle already vendored in `src/duckalog/static/datastar.js` into all dashboard pages:
    - Reference `/static/datastar.js` in the base layout and ensure it loads for every dashboard view.
  - Use **datastar-python** on the server side to:
    - Define and patch Datastar “signals” representing dashboard state, such as:
      - Catalog summary (config path, database path, view count, attachment count, semantic model count, last build status).
      - View list and filter/search state.
      - Current query text, query status, and query results.
    - Provide a Datastar-compatible SSE endpoint for streaming updates to the browser.
    - Use the attribute generator helpers to attach `data-*` attributes for fetch/patch behaviors to HTML elements built via the tag DSL.

- **Dashboard UX and behavior**
  - **Home / Overview**
    - Show cards for key catalog metrics (views, attachments, semantic models).
    - Display last build status and elapsed time using Datastar-bound signals that update when a build completes.
    - Provide a “Build catalog” button wired to a Datastar fetch action that calls a build API endpoint and updates status signals.
  - **Views**
    - Display a searchable table of views (name, source, uri, database, table, semantic flag) using StarUI table components.
    - Implement name-based filtering via Datastar signals instead of full page reloads.
    - Allow clicking a row to show view details.
  - **View Detail**
    - Show either the view SQL (if defined) or a structured description of the source (source type, URI, database, table).
    - Show semantic-layer metadata (dimensions and measures) when available.
  - **Query**
    - Provide a large textarea for ad-hoc SQL and a “Run query” button.
    - On submit, call a Datastar-enabled query API endpoint that:
      - Executes a read-only query against the catalog.
      - Updates signals containing column names, rows (up to `row_limit`), and any error message.
    - Render results in a StarUI/BasecoatUI-styled table, with a clear “results truncated” indicator when applicable.

- **Safety and engine interaction**
  - Enforce **read-only SQL** in the dashboard query endpoint:
    - Only allow `SELECT` statements (and optionally other clearly safe statements) and reject any DDL/DML with a clear error.
  - Use `row_limit` consistently to cap result size, and surface truncation status in the UI.
  - Ensure `DashboardContext` provides clear, typed error outcomes for build and query operations so that UI code can display friendly messages.

- **CLI integration**
  - Introduce or re-enable a `duckalog ui` CLI command that:
    - Accepts a config path and options (host, port, row limit).
    - Constructs a `DashboardContext` and runs the Starlette app via an ASGI server (e.g. Uvicorn).
    - Prints the URL and appropriate warnings when binding to non-loopback hosts.

## Impact

- **Affected specs**
  - `dashboard-ui` spec: enhanced to describe the Datastar-based UI, read-only query semantics, and improved layout/UX.
  - `cli` spec: extended to include a (re)defined `ui` command for launching the dashboard.

- **Affected code**
  - `src/duckalog/dashboard/*`: refactored app structure, Datastar integration, and HTML rendering.
  - `src/duckalog/static/`: ensure Datastar bundle is served correctly.
  - `src/duckalog/cli.py`: `ui` subcommand for launching the dashboard.
  - `tests/test_ui.py` and related tests: updated to assert Datastar attributes, SSE, and improved behavior.

- **User experience**
  - A modern, visually consistent dashboard that matches published docs and tests.
  - Reactive behavior (build status updates, filters, query results) without client-side JavaScript frameworks.
  - Safer ad-hoc queries with clear error reporting and read-only enforcement.

- **Breaking changes**
  - No intentional breaking changes to existing APIs; changes are additive and align code with documented behavior.
  - If any existing, undocumented endpoints or UI assumptions must change, they will be called out explicitly in the implementation notes and specs.

## Risks and Trade-offs

- **Increased complexity**
  - Introducing Datastar signals and SSE adds conceptual complexity compared to the current static pages, but aligns with the documented architecture and enables a better UX.
- **Dependency surface**
  - Relying on StarUI/BasecoatUI and datastar-python adds UI-related dependencies; however, this is consistent with the project’s documented UI stack and avoids custom ad-hoc HTML frameworks.
- **Performance considerations**
  - Streaming and signal updates must be designed carefully to avoid unnecessary chatter for large catalogs, but the dashboard remains single-user and local-first by default, which constrains scope.

