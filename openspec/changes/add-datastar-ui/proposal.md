# Datastar-Driven Catalog UI

## Why
- Users managing DuckDB catalogs increasingly want live visibility into their views, schemas, and queries without constantly switching to the CLI.
- The existing codebase already captures the catalog definition and build machinery in Python, so a Python-first UI can reuse the same models, validation, and DuckDB interactions instead of reimplementing them in another stack.
- A slim Starlette + Datastar + htpy experience keeps the UI server-rendered and reactive with minimal JavaScript, which fits the project’s “Python-first, minimal dependencies” goal better than a heavy SPA framework.

## What Changes
- Add a Datastar-backed Starlette dashboard (specified in `specs/web-ui`) that lets users:
  - view the catalog (list views and metadata),
  - add, edit, or delete catalog entries,
  - inspect table schemas,
  - rebuild the DuckDB catalog,
  - preview data and run more complex queries,
  - and export query results as CSV, Parquet, or Excel.
- Reuse existing config models and engine helpers to load/validate configs, persist changes, rebuild the catalog, and run queries against the configured DuckDB database.
- Provide a CLI entrypoint (for example, `duckalog ui <config-path>`) that starts the Starlette app so the UI is discoverable and easy to launch from an installed `duckalog`.
- Document the new UI capability, its supported workflows, and any configuration or security considerations so users know when and how to use it.

## Impact
- Introduces a new optional “web UI” surface to the project in addition to the existing CLI and Python API; the CLI remains the primary interface for automated workflows.
- Adds runtime web-UI dependencies (for example, Starlette, Datastar, htpy, a small ASGI server, and an Excel writer) which SHOULD be isolated behind an optional extra or dedicated module so core `duckalog` usage stays lightweight.
- Requires new HTML/template assets and Datastar attributes for live updates, plus a thin REST/JSON surface used by the UI for CRUD, schema, query, and export operations (not intended as a general-purpose public API in the first iteration).
- Expands test surface to cover config persistence safeguards (no partial writes on validation error), key UI endpoints, and the critical workflows (view list, CRUD, schema inspection, rebuild, query preview, export).
