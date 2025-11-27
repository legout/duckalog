# Design Document: starhtml/starui Dashboard UI for Duckalog

## Context

This change introduces a new `dashboard-ui` capability for duckalog: a lightweight, local-only web dashboard that helps users inspect catalogs, run ad-hoc queries, and trigger builds.

Key constraints from the project and proposal:
- The dashboard is single-user and local-first; it is not a multi-tenant web app.
- Implementation must be pure Python, without a separate frontend build toolchain.
- The UI stack is **starhtml** and **starui** for HTML rendering and layout/components.
- A future, more conventional HTTP interface (e.g. Starlette/FastAPI + htpy + Datastar) may be added later but should be able to reuse the same core behavior.

The goal of this design is to define how the dashboard ASGI app is structured, how it integrates with the existing duckalog config/build/query capabilities, and how it satisfies the local-first and stack constraints.

## Goals / Non-Goals

### Goals
- Provide a small, composable ASGI application that:
  - Renders HTML using starhtml and starui components.
  - Exposes routes for the dashboard home, views browser, view detail, query runner, and build trigger/status.
- Integrate cleanly with the duckalog CLI (`duckalog ui ...`) and a Python API for programmatic launch.
- Keep state management simple and explicit: one catalog per dashboard instance, clear lifecycle for DuckDB connections.
- Make it easy to extend the dashboard with additional pages or an alternate interface in future changes.

### Non-Goals
- Implement authentication, authorization, or multi-user session management.
- Provide advanced visualization or BI-style charts (beyond simple tabular views).
- Define or implement a second web UI stack (FastAPI/htpy/Datastar); that will be a separate change.
- Introduce complex background job infrastructure; builds and queries run in-process for this change.

## High-Level Design

### ASGI App Structure

The dashboard will be implemented as a small ASGI app, hosted in a dedicated module, for example:

- `src/duckalog/dashboard/app.py` – ASGI app factory and route wiring.
- `src/duckalog/dashboard/views.py` – starhtml/starui view functions/components.
- `src/duckalog/dashboard/state.py` – lightweight state objects (catalog config, paths, connection factory).

An app factory will accept a resolved `Config` (and possibly a pre-initialized engine wrapper), and return an ASGI application that:
- Mounts HTTP routes (e.g. `/`, `/views`, `/views/{name}`, `/query`, `/build`).
- Uses starhtml/starui to render HTML for GET routes.
- Accepts POST submissions for actions (query execution, build trigger).

### State and DuckDB Connections

To stay simple and testable:
- The dashboard app instance is parameterized by a single catalog config (or equivalent).
- A small abstraction (e.g. `DashboardContext`) exposes:
  - Parsed catalog configuration.
  - A way to open or reuse DuckDB connections appropriately for queries and builds.
  - Accessors for catalog metadata (views, attachments, semantic-layer models).
- Each HTTP request handler uses this context to:
  - Fetch metadata for display.
  - Run queries with clear resource lifecycles (opening/closing connections or using a shared pool with proper locking, as decided during implementation).

The change does not prescribe an exact connection strategy, but the implementation should:
- Avoid long-lived transactions tied to HTTP sessions.
- Prefer short-lived query connections or a small shared connection guarded by appropriate concurrency handling.

### starhtml/starui Usage

Views will be composed as Python functions that return starhtml/starui component trees:
- A common layout component (header, navigation, footer) is shared across pages.
- Individual pages (home, views browser, view detail, query runner, build status) are implemented as separate functions.
- Forms and tables are defined using starui components where available; where not available, simple starhtml primitives are used.

This approach ensures:
- No handcrafted HTML strings or templates.
- A clear mapping from requirements to view functions.
- Easy reuse of layout components and styles.

### CLI and Python API Integration

The CLI `duckalog ui` command will:
- Load and validate the catalog config using existing config loading utilities.
- Construct a `DashboardContext` and ASGI app via the app factory.
- Start a local ASGI server (e.g. uvicorn) bound to loopback by default, with configurable host/port options.
- Print the dashboard URL to stdout and run until interrupted.

The Python API will expose a `run_dashboard`-style function that:
- Accepts a `Config` (or config path) and host/port.
- Creates and runs the same ASGI app as the CLI, returning a handle or running in the foreground depending on the design of the public API.

Both paths share the same app factory to avoid divergence in behavior.

### Local-First and Offline Behavior

To honor local-first and offline-friendly constraints:
- The dashboard serves all required assets (CSS/JS) from within the duckalog package.
- Any starui/starhtml-related static assets are bundled or referenced locally; no external CDNs are used.
- The default host is a loopback interface, and documentation explicitly warns about changing host/port to bind externally.

If Datastar or other reactive tooling is introduced later, it will be done in a separate change, ensuring that:
- This dashboard remains functional without network connectivity.
- No runtime dependency on external CDNs is added.

## Risks / Trade-offs

- **Risk: Starhtml/starui familiarity** – Contributors might be less familiar with starhtml/starui than with template-based stacks.
  - *Mitigation:* Keep view functions small and well-named; document layout and component usage in the codebase and docs.
- **Risk: Connection lifecycle complexity** – Managing DuckDB connections inside an ASGI app may be subtle.
  - *Mitigation:* Centralize connection management in `DashboardContext` and add tests for concurrent query and build operations.
- **Risk: Future alternate interface** – A later FastAPI/htpy + Datastar interface could drift from this dashboard’s behavior.
  - *Mitigation:* Treat the `dashboard-ui` spec as behaviorally authoritative; future interfaces should be specified to reuse the same underlying capabilities.

## Open Questions

- Should query execution and build operations share a single DuckDB connection or use separate connections?
- How much build and query history (if any) should be preserved in memory for display?
- Should we support multiple catalogs in one process (e.g. multiple tabs/windows) or enforce one catalog per dashboard instance?

These questions can be answered during implementation, as long as the resulting behavior remains consistent with the `dashboard-ui` specification and local-first constraints.

