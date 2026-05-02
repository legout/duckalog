# Code Context: StarHTML Catalog Studio Foundation

## Files Retrieved

### Dashboard / UI Core
1. `src/duckalog/dashboard/app.py` (lines 1-98) — Litestar `create_app()` factory; entry point for `duckalog ui`. Accepts `Config`, `config_path`, `db_path`, `row_limit`, `static_dir`. Mounts `static_router` for `/static`. Exposes `/health`. Controllers: `HomeController`, `ViewsController`, `QueryController`, `RunController`. Debug via `DASHBOARD_DEBUG` env var.
2. `src/duckalog/dashboard/state.py` (lines 1-170) — `DashboardContext` dataclass. Holds `Config`, `config_path`, `db_path`, `row_limit`, `_connection`. Key methods: `get_views()`, `get_view()`, `execute_query()` (async generator, batched streaming), `get_catalog_stats()`. Query validation enforces read-only. Thread-isolated connection per stream via `asyncio.to_thread`.
3. `src/duckalog/dashboard/routes/home.py` (lines 1-80) — `HomeController` at `/`. Uses htpy elements, Datastar signals (`data-signals`), `data-on-click`. Renders stats, view list, run status card.
4. `src/duckalog/dashboard/routes/query.py` (lines 1-165) — `QueryController` at `/query` + `/query/execute`; `RunController` at `/run` + `/run/status`. Uses `datastar_response` decorator + `read_signals`. Global `_run_status` dict + `_run_lock` for async state. Inline `_run_catalog()` calls `engine.build_catalog()`.

### Layout / Components
5. `src/duckalog/dashboard/components/layout.py` (lines 1-360) — `base_layout()` returns full `<html>` document. Imports Tailwind CDN, Basecoat CDN, Datastar JS from CDN. Large inline `<script type="module">` with theme toggle, mobile menu, view search/filter logic. Component helpers: `nav_link()`, `page_header()`, `card()`, `table_component()`, `table_header_component()`, `table_rows_component()`.
6. `src/duckalog/static/README.md` — Documents CDN-delivery status. `datastar.js` (29KB, v1.0.0-RC.6) exists but is **not actively used**; actual loading from jsDelivr CDN URL hardcoded in `base_layout()`. Future bundling plan noted.

### Config / Models
7. `src/duckalog/config/models.py` (lines 1-450) — Pydantic models: `Config`, `ViewConfig`, `SemanticModelConfig`, `DuckDBConfig`, `SecretConfig`, `AttachmentsConfig`, various attachment types. Validation includes duplicate view names, schema resolution, semantic model base-view resolution.
8. `src/duckalog/config/__init__.py` (lines 1-130) — Public API surface: `load_config()`, path security functions, logging utils. Delegates to `config/api.py:load_config()`.

### CLI
9. `src/duckalog/cli.py` (lines 1-540) — Typer-based app. `run` command: config validation → `connect_to_catalog()` or `build_catalog()`. `ui` command: loads config → `dashboard.create_app()` → `uvicorn.run()`. CLI options include filesystem auth flags, `.env` loading. Shared `@app.callback()` creates filesystem objects.

### Engine / Connection
10. `src/duckalog/engine.py` (lines 1-600) — `build_catalog()` high-level entry point. `CatalogBuilder` orchestrates setup → state → export. `ConfigDependencyGraph` handles Duckalog attachment recursion. Private helpers: `_create_secrets`, `_apply_duckdb_settings`, `_setup_attachments`, `_setup_iceberg_catalogs`, `_create_views`.
11. `src/duckalog/connection.py` (lines 1-220) — `CatalogConnection` lazy-init manager. `get_connection()` restores session state via `_apply_catalog_state`. Incremental view creation via `_update_views()`. Context manager support.

### Tests
12. `tests/test_dashboard.py` (lines 1-1346) — 12 test classes: `TestDashboardContext`, `TestDashboardRoutes`, `TestStaticFiles`, `TestSSEDashboard`, `TestRealtimeQueryStreaming`, `TestResponsiveDesign`, `TestCLIIntegration`, `TestViewSearchIntegration`, `TestRuntimeHardening`, `TestConcurrentQueries`. Uses `litestar.testing.TestClient`. SSE streaming tests use `client.stream("GET", ...)`. 1346 lines, ~200 test methods.

### Existing StarHTML Plan
13. `.execflow/plans/rebuild-duckalog-ui-starhtml/brainstorm.md` — Approved approach: **Approach A: Parallel StarHTML "Catalog Studio"**. Build beside existing dashboard. Cover catalog viewer/editor, data viewer, SQL executor, run/status. Form/menu editing + expert YAML/JSON mode. Staged delivery. Open risks: StarHTML routing integration, CLI entry point design, StarUI maturity, YAML/JSON write safety, packaging/static assets, Python version constraints.

## Key Code

```python
# dashboard/app.py — factory signature (stable boundary)
def create_app(
    config: "Config",
    config_path: str,
    *,
    db_path: str | None = None,
    row_limit: int = 1000,
    static_dir: str | None = None,
) -> Litestar: ...

# cli.py — ui command entry point (stable boundary)
@app.command(name="ui", help="Launch the local dashboard for a catalog.")
def ui(
    config_path: str,
    host: str = "127.0.0.1",
    port: int = 8787,
    row_limit: int = 500,
    db_path: Optional[str] = None,
    verbose: bool = False,
) -> None: ...

# connection.py — catalog connection interface (stable boundary)
class CatalogConnection:
    def get_connection(self) -> duckdb.DuckDBPyConnection: ...
    config: Optional[Config]  # already loaded config

# config/models.py — main config model (stable boundary)
class Config(BaseModel):
    version: int
    duckdb: DuckDBConfig
    views: list[ViewConfig]
    attachments: AttachmentsConfig
    iceberg_catalogs: list[IcebergCatalogConfig]
    semantic_models: list[SemanticModelConfig]
```

## Architecture

```
cli.py (Typer)
  └── ui() → dashboard.app.create_app() → uvicorn.run()
                 │
                 ├── DashboardContext (config, db_path, row_limit, connection)
                 │
                 ├── HomeController  /           → home.py
                 ├── ViewsController /views/*   → views.py
                 ├── QueryController /query/*   → query.py (SSE streaming)
                 ├── RunController   /run/*     → query.py (SSE status)
                 ├── health_check    /health
                 └── static_router   /static/*
                          │
                          └── DashboardContext.execute_query()
                                    │
                                    └── engine.build_catalog() (run trigger)
```

**Config flow**: `cli.load_config()` → `config/api.py` → `config/loading/` → `config/resolution/` → validated `Config` Pydantic model.

**Connection flow**: `CatalogConnection.get_connection()` → `engine._apply_catalog_state()` → pragmas, secrets, attachments, iceberg catalogs, views.

## Dependencies / Extras

```toml
# pyproject.toml — current optional-dependencies layout
[project.optional-dependencies]
ui = [
    "litestar>=2.0.0",
    "htpy>=0.1.0",
    "datastar-py>=0.7.0",
    "uvicorn[standard]>=0.24.0",
    "python-multipart>=0.0.20",
    "msgspec>=0.18.0",
    "sniffio>=1.3.1",
]
```

StarHTML would need: `starhtml>=0.6.0` (or appropriate version), possibly `starui` for components. **StarHTML requires Python ≥3.12** — matches Duckalog's `requires-python = ">=3.12"`. StarHTML bundles Datastar JS as static assets in its wheel.

## Start Here

1. **Read the existing brainstorm** at `.execflow/plans/rebuild-duckalog-ui-starhtml/brainstorm.md` — it already captures the approved approach and all major unknowns.
2. **Read `pyproject.toml`** — verify StarHTML/Starlette dependency compatibility with Litestar; assess static asset bundling approach.
3. **Read `src/duckalog/dashboard/app.py`** — understand the current factory pattern that the new StarHTML app factory must coexist with.
4. **Read `tests/test_dashboard.py`** — understand the test structure that will need parallel StarHTML test coverage.

## Risks for the Plan

| Risk | Severity | Mitigation |
|------|----------|------------|
| StarHTML API instability (pre-1.0) | High | Pin to specific version; isolate StarHTML imports behind a feature flag; ensure existing dashboard remains buildable |
| Static asset bundling (Datastar.js) | Medium | StarHTML bundles its own Datastar — investigate whether it can be used standalone without uvicorn/static serving complications |
| Parallel maintenance of two UI stacks | High | Define clear phase boundaries; existing dashboard stays stable until StarHTML UI proves itself |
| CLI entry point design | Medium | `duckalog studio` as new command vs `--ui=studio` flag vs new sub-package; decide before scaffolding |
| Test coverage duplication | Medium | `test_dashboard.py` is Litestar-specific (uses `TestClient`); StarHTML tests need a different test client approach |
| Documentation split | Low | Docs will need to distinguish old vs new UI; plan early for a docs migration path |
| Config write safety (YAML/JSON editor) | High | Form/menu editing first; expert mode validation, preview, backup, rollback need clear spec before implementation |
| Datastar JS version mismatch | Medium | Current dashboard uses CDN v1.0.0-RC.6; StarHTML bundles its own — verify compatibility |
| StarUI component maturity | Medium | StarUI v0.4.1; shadcn/ui-style — assess coverage for Duckalog's needs (tables, forms, dialogs, data workbench) |

## Boundaries to Keep Stable

- **`duckalog.config.Config`** — Pydantic model interface for config loading; must not break for existing users
- **`duckalog.connection.CatalogConnection`** — connection management; any new UI uses this
- **`duckalog.engine.build_catalog()`** — the core build function; StarHTML UI triggers runs via this
- **`duckalog.cli.ui()`** — existing CLI command; new StarHTML studio may need a new command (`duckalog studio`)
- **Config loading flow** (`load_config()` → API → loading → resolution → validation) — do not restructure
- **`DashboardContext`** interface — `get_views()`, `get_view()`, `execute_query()`, `get_catalog_stats()` are stable behaviors new UI can reuse or reimplement