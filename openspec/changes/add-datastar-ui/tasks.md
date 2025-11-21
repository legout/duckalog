## 1. Requirements & Spec
- [x] Finalize the `web-ui` change spec in `openspec/changes/add-datastar-ui/specs/web-ui/spec.md` so it directly reflects the supported workflows (view catalog, CRUD, schema, rebuild, query, export).
- [x] Keep implementation details (framework choices, routing structure) out of the spec except where Datastar usage is explicitly required for behaviour.

## 2. Backend & CLI
- [x] Add a dedicated UI module (for example, `duckalog.ui`) that builds a Starlette app for the catalog dashboard and exposes internal JSON/REST endpoints for CRUD, schema, rebuild, query, and export.
- [x] Ensure config changes go through existing validation, with atomic write semantics (no partial writes when validation fails).
- [x] Add a CLI entrypoint (for example, `duckalog ui <config-path>`) that starts the UI against a specific config/catalog, with sensible defaults for host/port and clear console output.

## 3. Frontend & Coverage
- [x] Create Datastar-enabled HTML/htpy templates for the dashboard that surface the catalog list, schema view, rebuild button, query runner, and export actions.
- [x] Update README/docs to introduce the web UI, its limitations (e.g. single-user/local focus, not a hardened multi-tenant admin), and how to launch it.
- [x] Add tests or smoke checks that exercise critical workflows end-to-end (at least: list views, successful/failed CRUD, schema inspection, rebuild, query preview, export) and run `openspec validate add-datastar-ui --strict` as part of the change.
