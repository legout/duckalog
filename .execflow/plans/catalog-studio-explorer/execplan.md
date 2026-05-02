# Add the Catalog Studio Explorer pages

This ExecPlan is a living document. The sections `Progress`, `Surprises & Discoveries`, `Decision Log`, and `Outcomes & Retrospective` must be kept up to date as work proceeds.

This document must be maintained in accordance with `.execflow/PLANS.md` from the repository root. It builds on the completed umbrella brainstorm at `.execflow/plans/rebuild-duckalog-ui-starhtml/brainstorm.md` and on the prerequisite foundation plan at `.execflow/plans/starhtml-catalog-studio-foundation/execplan.md`. If the foundation plan has not been implemented yet, implement it first; this Explorer plan assumes that `src/duckalog/studio/`, `duckalog.studio.create_app()`, `StudioContext`, `tests/test_studio.py`, and the `duckalog studio` CLI command already exist.

## Purpose / Big Picture

After this change, a user can open the new StarHTML-based Duckalog Catalog Studio and browse the catalog’s configured views through first-class Studio pages. The root overview becomes useful, the navigation entry named “Catalog” links to a real catalog explorer, `/catalog/` lists configured views with schema, source, tags, and descriptions, and `/catalog/{view_name}` shows a detail page for one view with its metadata and SQL or source definition. Unknown view names return a proper 404 response. The old Litestar dashboard remains unchanged.

This is the first product slice after the StarHTML foundation. It deliberately stays read-only. It establishes the page and state patterns later plans will reuse for data browsing, SQL execution, and catalog editing without taking on write-path safety or streaming query complexity yet.

## Progress

- [x] (2026-04-30) Completed the umbrella brainstorm and selected a parallel StarHTML “Catalog Studio” direction.
- [x] (2026-04-30) Created the prerequisite foundation ExecPlan at `.execflow/plans/starhtml-catalog-studio-foundation/execplan.md`.
- [x] (2026-04-30) Read the brainstorm, foundation ExecPlan, repository architecture notes, config model definitions, existing dashboard view routes, and scout context for explorer planning.
- [x] (2026-04-30) Ran a scout pass and saved explorer-specific context at `.execflow/plans/catalog-studio-explorer/context.md`.
- [ ] Confirm the foundation implementation exists and exposes `duckalog.studio.create_app` and `StudioContext`.
- [ ] Extend `StudioContext` with read-only explorer methods for catalog stats, view listing, and single-view details.
- [ ] Add StarHTML components for overview summary, catalog listing, empty catalog state, metadata badges, and view detail.
- [ ] Add `/catalog/` and `/catalog/{view_name}` routes to the Studio app.
- [ ] Update the root overview so it links to the catalog explorer and shows useful catalog summary information.
- [ ] Add tests for state methods, overview links, catalog listing, detail rendering, missing-view 404 behavior, empty catalog rendering, and old dashboard preservation.
- [ ] Run `starhtml-check` and focused pytest commands, then update this plan with results.

## Surprises & Discoveries

- Observation: The current Litestar dashboard already defines the user-facing explorer baseline.
  Evidence: `src/duckalog/dashboard/routes/views.py` has `/views` and `/views/{view_name}` routes. The list page shows view name, schema, source type, and description. The detail page shows name, description, schema, source, and SQL when present.

- Observation: `ViewConfig` contains more metadata than the old dashboard currently displays.
  Evidence: `src/duckalog/config/models.py:ViewConfig` defines `name`, `db_schema`, `sql`, `sql_file`, `sql_template`, `source`, `uri`, `database`, `table`, `catalog`, `options`, `description`, and `tags`. Catalog Studio can show tags and source definition details in addition to the old dashboard fields without requiring config writes.

- Observation: The prerequisite foundation plan is intentionally not implemented by this plan.
  Evidence: The scout context notes that `src/duckalog/studio/` may not exist until `starhtml-catalog-studio-foundation` is executed. This plan must be ticketized or implemented after that foundation work, not in parallel with changes to the same app factory and shell files.

## Decision Log

- Decision: Make Catalog Studio Explorer the next ExecPlan after the foundation.
  Rationale: It delivers visible product value, proves the new StarHTML shell with real catalog data, and avoids the higher risks of SQL streaming and config editing.
  Date/Author: 2026-04-30 / planning session

- Decision: Keep this Explorer plan read-only.
  Rationale: Catalog editing requires validation, preview diff, backup, and rollback semantics. Mixing it into explorer pages would blur the boundary and make this first product slice harder to validate.
  Date/Author: 2026-04-30 / planning session

- Decision: Use `/catalog/` and `/catalog/{view_name}` routes in the new Studio, not `/views`.
  Rationale: “Catalog” matches the new Catalog Studio product language and leaves the existing dashboard’s `/views` route untouched. Future Studio pages can group views, semantic models, attachments, and settings under the broader catalog concept.
  Date/Author: 2026-04-30 / planning session

- Decision: Display richer metadata than the old dashboard where it is already available from `ViewConfig`.
  Rationale: Tags, source URI/table/database, SQL file references, and template references help users understand their catalog without creating editing behavior. This improves user value while staying read-only.
  Date/Author: 2026-04-30 / planning session

## Outcomes & Retrospective

No implementation outcomes have been produced yet. At completion, update this section with what pages exist, which tests passed, how StarHTML routing behaved, any fields that were deferred, and which ExecPlan should follow. The expected next plan after this one is the Query Workbench, unless implementation discovers that the Studio shell or explorer needs another cleanup/foundation pass first.

## Context and Orientation

Duckalog builds DuckDB catalogs from YAML or JSON configuration files. A validated configuration is represented by the Pydantic model `Config` in `src/duckalog/config/models.py`. A Pydantic model is a Python class that validates and normalizes input data. A catalog “view” is represented by `ViewConfig`; it can be defined by inline SQL, by a SQL file, by a SQL template file, or by a data source such as Parquet, Delta, Iceberg, DuckDB, SQLite, or Postgres.

The existing web dashboard lives in `src/duckalog/dashboard/`. It uses Litestar, htpy, and Datastar. This Explorer plan targets the new StarHTML Studio package created by the foundation plan in `src/duckalog/studio/`. StarHTML is a Python-first reactive HTML framework. A StarHTML app is still an ASGI app, which means uvicorn can serve it just like the old dashboard app. StarHTML imports should remain inside `src/duckalog/studio/` so the core library and old dashboard do not become coupled to StarHTML.

The prerequisite foundation plan creates these files and interfaces:

    src/duckalog/studio/__init__.py
    src/duckalog/studio/app.py
    src/duckalog/studio/state.py
    src/duckalog/studio/components.py
    tests/test_studio.py

It also adds a `duckalog studio` CLI command. This Explorer plan extends those files; it should not create another app package or another CLI command.

The existing `DashboardContext` in `src/duckalog/dashboard/state.py` is the best reference for read-only behavior. It accepts `config`, `config_path`, optional `db_path`, and `row_limit`. It exposes `get_views()`, `get_view(name)`, and `get_catalog_stats()`. The new `StudioContext` should provide similar methods for the Explorer. It may delegate to `DashboardContext` if that was chosen during foundation implementation, or it may own its own small read-only projection helpers. The important design goal is that routes and components do not each know how to interpret `ViewConfig`; that knowledge should sit behind `StudioContext` or small helper functions.

The old dashboard list route is `src/duckalog/dashboard/routes/views.py:ViewsController.list_views()`. It renders a table with view name, schema, source type, and description. The old detail route is `ViewsController.view_detail()`. It renders the view name, description, schema, source, and inline SQL. The new Studio Explorer should meet this baseline and add tags and non-inline source descriptions where available.

## Plan of Work

Begin by verifying that the foundation plan has been implemented. From the repository root, `uv run python -c "from duckalog.studio import create_app, StudioContext; print(create_app, StudioContext)"` must succeed before this plan starts. If it fails because `duckalog.studio` does not exist, stop and implement `.execflow/plans/starhtml-catalog-studio-foundation/execplan.md` first.

Extend `src/duckalog/studio/state.py` so `StudioContext` exposes read-only explorer methods. At minimum, add or confirm `get_catalog_stats()`, `get_views()`, and `get_view(name: str)`. `get_views()` should return a list of dictionaries or small dataclass objects suitable for rendering. Each item should include `name`, `schema`, `description`, `source_type`, and `tags`. Use `view.db_schema or "main"` for schema. Use `view.source or "sql"` for source type. Include `tags` as a list of strings. `get_view()` should return richer detail for one view: `name`, `schema`, `description`, `source_type`, `tags`, `sql`, `sql_file`, `sql_template`, `uri`, `database`, `table`, `catalog`, and `options`, or return `None` for an unknown view. Do not expose write methods.

Add helper logic in `StudioContext` or `src/duckalog/studio/components.py` to turn a view definition into a human-readable definition summary. For inline SQL, the summary is the SQL text. For `sql_file`, show the file path and any variables; do not read or resolve the external file in this plan. For `sql_template`, show the template path, variables, and that it is a template. For source-backed views, show the source type and the meaningful fields: URI for Parquet/Delta/Iceberg URI views, catalog and table for Iceberg catalog-backed views, and database plus table for DuckDB/SQLite/Postgres attached-source views. For `options`, render a small key/value list if it is non-empty.

Extend `src/duckalog/studio/components.py` with components for the explorer. Prefer deep components that hide rendering policy rather than many shallow wrappers. Good components are `catalog_overview(ctx)`, `catalog_list_page(ctx)`, `view_detail_page(ctx, view)`, `view_badge(text, kind)`, `empty_catalog_state()`, and `metadata_grid(view)`. The components should make it obvious when a feature is coming later: show “Edit” or “Data Preview” as disabled or “coming soon” only if the foundation shell already established that visual language. Do not add active edit buttons that imply write behavior.

Update `src/duckalog/studio/app.py` to register `/catalog/` and `/catalog/{view_name}` routes. The list route should render the Studio shell with the catalog list page inside it. The detail route should use `ctx.get_view(view_name)`. If no view exists, return a 404 response using the idiom appropriate for the StarHTML/Starlette stack chosen in the foundation implementation. If StarHTML route parameter syntax differs from `/catalog/{view_name}`, adapt locally and record the exact route pattern in `Surprises & Discoveries`.

Update the root `/` overview route so it is no longer only a placeholder shell. It should show total views, schema count, database path or “in-memory”, and a prominent link to `/catalog/` labeled “Browse Catalog” or equivalent. This root page remains an overview; it should not duplicate the full catalog table.

Add tests to `tests/test_studio.py` or a companion `tests/test_studio_explorer.py`. Keep all Studio tests near each other. Use a temporary config that includes at least four view styles: one inline SQL view with tags and description, one view in a non-main schema, one source-backed Parquet or DuckDB/SQLite/Postgres view, and one SQL file or SQL template reference if validation permits creating it without needing a real file. If validation requires a real SQL file, create it under `tmp_path`. Tests should cover `StudioContext.get_views()`, `StudioContext.get_view()`, the root overview route, `/catalog/`, `/catalog/{known_view}`, `/catalog/{missing_view}`, and an empty catalog state if the `Config` model permits a config with zero views. If `Config` validation does not permit zero views, skip the empty state test and record the reason.

Preserve the old dashboard. Do not change `src/duckalog/dashboard/routes/views.py`, `src/duckalog/dashboard/components/layout.py`, or `tests/test_dashboard.py` except for an extremely small shared test helper extraction that does not alter behavior. Run the existing dashboard tests after the Studio tests.

Run `starhtml-check` on every Studio Python file that contains StarHTML elements, especially `src/duckalog/studio/app.py` and `src/duckalog/studio/components.py`. If implementation adds a separate route or component file, check that file too.

## Concrete Steps

Work from the repository root `/Users/volker/coding/libs/duckalog`.

First verify the prerequisite foundation:

    uv run python - <<'PY'
    from duckalog.studio import create_app, StudioContext
    print(create_app, StudioContext)
    PY

This must print function and class references without raising `ImportError`. If it fails, stop and implement `.execflow/plans/starhtml-catalog-studio-foundation/execplan.md` before continuing.

Inspect the foundation files before editing so the Explorer work follows local patterns:

    rg -n "def create_app|class StudioContext|@rt|Catalog Studio|Overview|Catalog" src/duckalog/studio tests/test_studio.py

Then add or extend state methods in `src/duckalog/studio/state.py`. A quick import-level check after this step should work:

    uv run python - <<'PY'
    from pathlib import Path
    from duckalog.config import load_config
    from duckalog.studio import StudioContext

    path = Path('/tmp/duckalog-studio-explorer.yaml')
    path.write_text('''
    version: 1
    duckdb:
      database: ":memory:"
    views:
      - name: orders
        db_schema: marts
        sql: "select 1 as order_id"
        description: "Orders mart"
        tags: [finance, demo]
    ''')
    config = load_config(str(path))
    ctx = StudioContext(config=config, config_path=str(path))
    print(ctx.get_catalog_stats())
    print(ctx.get_views())
    print(ctx.get_view('orders'))
    PY

The expected output includes one total view, schema `marts`, source type `sql`, and a detail object for `orders`.

After adding routes and components, run StarHTML checks:

    starhtml-check src/duckalog/studio/app.py
    starhtml-check src/duckalog/studio/components.py

If more Studio files contain StarHTML elements, run the checker on them too. The expected outcome is no ERROR findings.

Run focused tests:

    uv run pytest tests/test_studio.py -q

or, if Explorer tests are split into a new file:

    uv run pytest tests/test_studio.py tests/test_studio_explorer.py -q

Then verify the old dashboard remains intact:

    uv run pytest tests/test_dashboard.py -q

Finally, manually smoke-test the browser-facing behavior. Create a sample config if needed:

    cat >/tmp/duckalog-studio-explorer.yaml <<'YAML'
    version: 1
    duckdb:
      database: ":memory:"
    views:
      - name: orders
        db_schema: marts
        sql: "select 1 as order_id, 'demo' as status"
        description: "Orders mart"
        tags: [finance, demo]
      - name: raw_events
        source: parquet
        uri: "data/events/*.parquet"
        description: "Raw event files"
        tags: [raw]
    YAML

Start the Studio app:

    uv run duckalog studio /tmp/duckalog-studio-explorer.yaml --port 8788

In another terminal, verify:

    curl -i http://127.0.0.1:8788/catalog/
    curl -s http://127.0.0.1:8788/catalog/ | rg "orders|raw_events|marts|parquet|finance"
    curl -i http://127.0.0.1:8788/catalog/orders
    curl -s http://127.0.0.1:8788/catalog/orders | rg "Orders mart|select 1 as order_id|finance"
    curl -i http://127.0.0.1:8788/catalog/does_not_exist

The expected results are HTTP 200 for `/catalog/` and `/catalog/orders`, visible catalog metadata in the HTML, and HTTP 404 for the missing view.

## Validation and Acceptance

Acceptance is behavior a user can see. After this plan is implemented, `duckalog studio path/to/catalog.yaml` starts the new Studio app, the root page links to a real catalog explorer, `/catalog/` lists the catalog’s views, and `/catalog/{view_name}` shows one view’s metadata and definition. A missing view returns 404. The pages are read-only and do not imply that editing is available yet.

Automated validation must prove both Studio behavior and old dashboard preservation. The Studio test suite must include assertions that a loaded config drives the rendered HTML. It should check for the app title, “Browse Catalog” link, view names, schema labels, source labels, tags, descriptions, SQL text or source-definition text, and missing-view 404 behavior. The old dashboard validation must show that `tests/test_dashboard.py` still passes or, if local optional dependency conditions prevent running the full file, record the exact reduced command and why it is sufficient.

StarHTML-specific validation requires `starhtml-check` on all changed Studio StarHTML files with no ERROR findings. Ordinary Python tests are not enough because StarHTML has framework-specific rules around signal names, reactive attributes, positional argument order, and flash prevention.

## Idempotence and Recovery

This plan is additive on top of the foundation. It adds read-only state projection methods, components, routes, and tests. It should not change persisted catalog files or connect to external data sources. It should be safe to run tests repeatedly because tests use `tmp_path` and temporary config files.

If route registration fails because the StarHTML API differs from the foundation assumption, localize the fix to `src/duckalog/studio/app.py` and update this plan’s `Surprises & Discoveries`. Do not change `src/duckalog/cli.py` unless the foundation command itself was incomplete.

If the detail page cannot display a SQL file reference without reading the file, display the path and variables rather than reading content. Reading, resolving, or editing external SQL files is not part of this Explorer plan. If a test config with `sql_file` requires a real file, create a tiny file in `tmp_path`; do not depend on repository fixtures.

If an empty catalog cannot be represented because `Config` validation requires at least one view, remove the empty-state route test but keep an empty-state component if it is simple and harmless. Record the validation constraint in `Surprises & Discoveries`.

If this implementation must be backed out, remove only the Explorer additions: route registrations for `/catalog/` and `/catalog/{view_name}`, explorer components, explorer-specific state methods if they are not used by the foundation shell, and explorer tests. Keep the foundation Studio app and CLI command intact.

## Artifacts and Notes

The umbrella brainstorm is:

    .execflow/plans/rebuild-duckalog-ui-starhtml/brainstorm.md

The prerequisite foundation ExecPlan is:

    .execflow/plans/starhtml-catalog-studio-foundation/execplan.md

The explorer scout context is:

    .execflow/plans/catalog-studio-explorer/context.md

Relevant existing code references are:

    src/duckalog/config/models.py:ViewConfig
    src/duckalog/config/models.py:Config
    src/duckalog/dashboard/state.py:DashboardContext
    src/duckalog/dashboard/routes/views.py:ViewsController
    tests/test_dashboard.py

A useful sample `ViewConfig` shape for rendering is:

    name: str
    db_schema: str | None
    sql: str | None
    sql_file: SQLFileReference | None
    sql_template: SQLFileReference | None
    source: "parquet" | "delta" | "iceberg" | "duckdb" | "sqlite" | "postgres" | None
    uri: str | None
    database: str | None
    table: str | None
    catalog: str | None
    options: dict[str, Any]
    description: str | None
    tags: list[str]

Do not add data preview queries in this plan. The “Data” navigation entry may remain a placeholder until a later data viewer or query workbench plan.

## Interfaces and Dependencies

At the end of this plan, `StudioContext` must expose these read-only methods:

    def get_catalog_stats(self) -> dict[str, int]: ...
    def get_views(self) -> list[dict[str, Any]]: ...
    def get_view(self, name: str) -> dict[str, Any] | None: ...

The exact return type can be a dataclass instead of a dictionary if the foundation implementation already established dataclass projections, but the fields must cover the acceptance criteria: name, schema, source type, description, tags, and enough definition fields for the detail page.

The Studio app must expose these routes:

    GET /
    GET /health
    GET /catalog/
    GET /catalog/{view_name}

If StarHTML route syntax normalizes trailing slashes differently, tests and docs should follow the actual app behavior, but `/catalog/` should be reachable by a browser. Unknown view names must result in HTTP 404 rather than a blank detail page or a 500 error.

This plan should not add new project dependencies beyond those already introduced by the foundation plan. If a UI component library such as StarUI is needed for tables or badges, pause and revise the plan; do not add it opportunistically. Plain StarHTML components are sufficient for this read-only explorer slice.

The next ExecPlan should be Query Workbench unless implementation shows the explorer needs a follow-up cleanup. Query Workbench should own SQL editor UI, read-only query execution, streaming results, loading/error states, and cancellation or row-limit behavior.

## Revision Note

2026-04-30: Initial Catalog Studio Explorer ExecPlan created. It is scoped as the first read-only product slice after the StarHTML foundation and deliberately avoids catalog editing, data preview queries, and SQL execution so those risks can be handled in later plans.
