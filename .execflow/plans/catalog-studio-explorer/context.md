# Code Context — catalog-studio-explorer

## Files Retrieved

1. `src/duckalog/config/models.py` (lines 1–490) — defines `Config`, `ViewConfig`, `SemanticModelConfig`, `DuckDBConfig`, and all attachment types. The foundation plan already relies on `Config` as the validated input; this plan must use it to drive explorer pages.

2. `src/duckalog/dashboard/state.py` (lines 1–115) — defines `DashboardContext`, a dataclass with `config: Config`, `config_path: str`, `db_path`, `row_limit`, and read-only methods `get_views()`, `get_view(name)`, `get_catalog_stats()`, and `execute_query()`. This is the primary state boundary reused by explorer pages.

3. `src/duckalog/dashboard/routes/views.py` (lines 1–131) — defines `ViewsController` with `/views` (list) and `/views/{view_name}` (detail) routes. Current behavior: list renders a search card and a table of view name + schema + source type + description; detail renders info card + SQL card.

4. `src/duckalog/dashboard/app.py` (lines 1–95) — defines `create_app()` factory with signature `(config, config_path, *, db_path=None, row_limit=1000, static_dir=None) -> Litestar`. Registers `HomeController`, `ViewsController`, `QueryController`, `RunController`, `/health`, and static file router.

5. `tests/test_dashboard.py` (lines 1–1305) — extensive test suite for `DashboardContext`, dashboard routes, SSE endpoints, responsive design, CLI integration, and view search/filtering.

6. `.execflow/plans/starhtml-catalog-studio-foundation/execplan.md` — the foundation ExecPlan (already read in full above).

## Key Code

### Config and ViewConfig fields relevant to explorer pages

```python
# src/duckalog/config/models.py

class ViewConfig(BaseModel):
    name: str                              # primary key for detail pages
    db_schema: Optional[str] = None         # schema qualifier (shown as badge)
    sql: Optional[str] = None               # raw SQL; displayed in detail
    sql_file: Optional[SQLFileReference] = None
    sql_template: Optional[SQLFileReference] = None
    source: Optional[EnvSource] = None      # "parquet" | "delta" | "iceberg" | "duckdb" | "sqlite" | "postgres"
    uri: Optional[str] = None              # used when source is parquet/delta/iceberg
    database: Optional[str] = None          # attachment alias for db sources
    table: Optional[str] = None            # table name for db sources
    catalog: Optional[str] = None          # Iceberg catalog name
    options: dict[str, Any] = {}           # source-specific options
    description: Optional[str] = None       # shown in list and detail
    tags: list[str] = []                   # classification tags

class Config(BaseModel):
    version: int
    duckdb: DuckDBConfig                   # .duckdb.database (":memory:" default)
    views: list[ViewConfig]                 # primary explorer resource
    attachments: AttachmentsConfig          # duckdb/sqlite/postgres/duckalog attachments
    iceberg_catalogs: list[IcebergCatalogConfig]
    semantic_models: list[SemanticModelConfig]
    imports: Union[list, SelectiveImports]
    env_files: list[str]
    loader_settings: LoaderSettings
```

### DashboardContext read-only methods for explorer pages

```python
# src/duckalog/dashboard/state.py

@dataclass
class DashboardContext:
    config: Config
    config_path: str
    db_path: str | None = None
    row_limit: int = 1000

    def get_views(self) -> list[dict[str, Any]]:
        # Returns list of {"name", "schema", "description", "source_type"}
        # source_type = view.source or "sql"

    def get_view(self, name: str) -> dict[str, Any] | None:
        # Returns {"name", "schema", "description", "source", "sql"} or None

    def get_catalog_stats(self) -> dict[str, int]:
        # Returns {"total_views": int, "schemas": int}

    async def execute_query(
        self, sql: str, limit: int | None = None, batch_size: int = 50
    ) -> AsyncGenerator[tuple[list[str], list[tuple[Any, ...]]], None]:
        # Streams column headers + row batches; rejects non-read-only queries.
```

### Existing dashboard views routes pattern

```python
# src/duckalog/dashboard/routes/views.py

class ViewsController(Controller):
    path = "/views"

    @get()
    async def list_views(self, ctx: DashboardContext) -> Response[str]:
        views = ctx.get_views()
        # Renders table with name (linked), schema, source badge, truncated description
        # Has a search input with data-bind and data-signals for client-side filtering

    @get("/{view_name:str}")
    async def view_detail(self, view_name: str, ctx: DashboardContext) -> Response[str]:
        view = ctx.get_view(view_name)
        # Raises NotFoundException if view is None
        # Renders: page_header (name + description), info card (schema, source),
        # SQL card (pre/code with sql text)
```

### Studio foundation (planned but not yet implemented)

The foundation ExecPlan (`starhtml-catalog-studio-foundation`) creates:
- `src/duckalog/studio/__init__.py` — exports `create_app`, `StudioContext`
- `src/duckalog/studio/state.py` — `StudioContext` dataclass mirroring `DashboardContext` inputs
- `src/duckalog/studio/app.py` — `create_app(config, config_path, *, db_path=None, row_limit=500) -> ASGI app`
- `src/duckalog/studio/components.py` — StarHTML shell with nav entries "Overview", "Catalog", "Data", "SQL"
- `src/duckalog/cli.py` — new `studio` Typer command on port `8788`
- `tests/test_studio.py` — new test file

The studio package does **not yet exist** — foundation is in-progress but not complete.

## Architecture

```
duckalog studio <config.yaml>
  → cli.py: studio command
  → duckalog.studio.create_app()
      → StudioContext (mirrors DashboardContext, accepts Config)
          → config.views: list[ViewConfig]
          → config.duckdb.database: str
          → config.iceberg_catalogs, config.attachments, config.semantic_models
      → StarHTML app (ASGI)
          → /  (shell + overview)
          → /catalog/         (views list — explorer milestone 1)
          → /catalog/{name}   (view detail — explorer milestone 2)
          → /health
```

**Key boundary decisions from foundation plan:**
- `duckalog.studio` is isolated from `duckalog.dashboard`; StarHTML imports live only in studio package.
- `StudioContext` does not add config write methods in foundation; explorer pages are read-only.
- Reuse `DashboardContext` behavior internally (or delegate) to avoid duplicating query logic.

## Start Here

Read the foundation ExecPlan at `.execflow/plans/starhtml-catalog-studio-foundation/execplan.md` to understand what the `studio` package will look like after the foundation milestone completes, then open `src/duckalog/dashboard/routes/views.py` and `src/duckalog/dashboard/state.py` to understand the current explorer behavior the StarHTML pages must replace.

## Milestone Recommendations (Independently Verifiable)

### Milestone 1 — StudioContext with `get_views()` / `get_view()` / `get_catalog_stats()`

**What:** Add to `src/duckalog/studio/state.py` a `StudioContext` that exposes the same read-only surface as `DashboardContext` for the explorer pages. Add a `views_page()` component to `src/duckalog/studio/components.py` that renders a navigable view listing.

**Verifiable:** After implementation, `uv run python - <<'PY'` prints no import errors and a test creates a `StudioContext` from a temp config and calls `get_views()`.

### Milestone 2 — `/catalog/` route with view listing

**What:** Register a `/catalog/` route in `src/duckalog/studio/app.py`. The route renders a views list with name (link to detail), schema badge, source badge, description, and tags. Should handle empty views gracefully.

**Verifiable:** `curl -s http://127.0.0.1:8788/catalog/` returns HTTP 200 with visible view names from the loaded config.

### Milestone 3 — `/catalog/{name}` route with view detail

**What:** Register a `/catalog/{name}` route. Renders page header (name + description), info card (schema, source, tags), SQL card (sql or sql_file path or source description), and a back link to `/catalog/`. Raises 404 for unknown view names.

**Verifiable:** `curl -s http://127.0.0.1:8788/catalog/foo` returns HTTP 200 with the view name and SQL content. `curl -s http://127.0.0.1:8788/catalog/nonexistent` returns HTTP 404.

### Milestone 4 — Overview page with catalog stats and navigation

**What:** Enhance the root `/` page to show catalog stats (total views, schema count, database path) and links to `/catalog/`. This is the entry point that makes the shell useful before the explorer exists.

**Verifiable:** Root page shows "Total Views: N", schema count, database path, and a "Browse Catalog" link.

### Milestone 5 — StarHTML validation and existing tests still pass

**What:** Run `starhtml-check` on all new studio files. Run `uv run pytest tests/test_studio.py tests/test_dashboard.py -q`. Old dashboard must remain intact.

**Verifiable:** Zero ERROR from `starhtml-check`. All tests pass.

## Open Questions

- **StarHTML routing pattern:** The foundation ExecPlan assumes `app, rt = star_app()` and `@rt("/")` decorators. The actual installed API may differ — validate during foundation milestone before writing explorer routes.
- **Search/filter behavior:** The existing dashboard uses `data-signals` + `data-bind` for client-side view filtering. Decide whether the StarHTML explorer replicates this (with StarHTML's signal syntax) or simplifies it.
- **SQL file display in detail page:** `ViewConfig.sql_file` is a `SQLFileReference` with `path` and optional `variables`. Detail page should show the resolved path and variable context; clarify whether to resolve file content or show the path as-is.
- **Semantic model explorer:** The foundation plan mentions `semantic_models` as part of the full Studio scope. Decide whether to include semantic model overview/detail pages in this explorer plan or defer to a later plan.
- **Schema navigation:** Views can be grouped by `db_schema`. Consider adding a schema filter/tab to the views listing, consistent with how the existing dashboard treats schema as a display field.