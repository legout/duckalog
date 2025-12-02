## Why

duckalog today focuses on config-driven catalog builds and a CLI / Python API workflow. For many users, especially those exploring new configs or teaching the concepts, a small, local dashboard makes it easier to:

- Inspect what a catalog contains (views, attachments, semantic models) without writing ad-hoc scripts.
- Trigger builds and re-builds interactively while iterating on `catalog.yaml`.
- Run quick exploratory queries against a catalog and inspect results in a table.

There is existing and planned UI work in the project, but this change intentionally defines a fresh, minimal dashboard capability that:

- Is **local-first** and targeted at a single developer session, not a shared, multi-user web app.
- Is implemented entirely in Python using **starhtml** and **starui**, without a separate frontend build toolchain.
- Can later be complemented (not replaced) by a more conventional Starlette/FastAPI + htpy + Datastar interface if needed.

## What Changes

- Introduce a new `dashboard-ui` capability describing a lightweight, local web dashboard for duckalog catalogs:
  - Launchable from the CLI (e.g. `duckalog ui catalog.yaml`) and/or Python API.
  - Backed by an ASGI app that uses **starhtml** for view rendering and **starui** for layout/components.
  - Designed for a single catalog at a time (no multi-tenant, multi-user scope in this change).
- Define requirements for the initial dashboard features:
  - **Dashboard Home**: Shows high-level information about the selected catalog (config path, DuckDB file, counts of views/attachments/semantic models) and entry points to other pages.
  - **Views Browser**: Lists views with key metadata (name, source type, underlying location/attachment, semantic-layer presence) and allows drilling into a single view.
  - **View Detail**: Shows the resolved SQL (or core config fields) for a view and its semantic metadata (dimensions/measures) when available.
  - **Ad-hoc Query Runner**: Allows a user to run SQL against the catalog and see tabular results with limited pagination/row caps.
  - **Build Trigger & Status**: Provides a way to trigger a catalog build from the UI and observe basic status/progress and outcome.
- Establish non-goals and constraints for this initial capability:
  - Local, single-user usage only (no authentication, no multi-user session sharing).
  - No complex charting or visualization; focus on tables, text, and a small amount of status/progress UI.
  - No external CDNs or JS build steps; all assets are served from the duckalog package and implemented via starhtml/starui.
  - Clear extension points so a future change can introduce additional views (e.g. semantic-layer exploration, charts) or an alternate HTTP interface while reusing the same backend behavior.

## Impact

- Provides a discoverable, friendly way for users to explore catalogs and the semantic layer without dropping into a SQL shell.
- Encourages configuration-driven workflows by making build status, views, and query results visible in one place.
- Establishes a clear specification boundary for dashboard behavior that future UI implementations (e.g. a FastAPI/htpy + Datastar interface) can target while reusing the same underlying capabilities.
- Keeps the implementation aligned with project constraints: pure Python stack, minimal dependencies, offline-friendly, and no implicit multi-user guarantees.
