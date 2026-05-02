# Polish Catalog Studio data viewer and table exploration

This ExecPlan is a living document. The sections `Progress`, `Surprises & Discoveries`, `Decision Log`, and `Outcomes & Retrospective` must be kept up to date as work proceeds.

This document must be maintained in accordance with `.execflow/PLANS.md` from the repository root. It builds on the completed umbrella brainstorm at `.execflow/plans/rebuild-duckalog-ui-starhtml/brainstorm.md`, the read-only Explorer plan at `.execflow/plans/catalog-studio-explorer/execplan.md`, and the SQL Workbench plan at `.execflow/plans/catalog-studio-query-workbench/execplan.md`. If the Studio foundation, Explorer, and Query Workbench have not been implemented yet, implement them first.

## Purpose / Big Picture

After this change, Catalog Studio has a polished read-only data viewer for configured views. A user can open a view detail page, preview rows, paginate through data, inspect columns and types, see useful table statistics, copy a query into the SQL Workbench, and understand row-limit/truncation behavior. The existing dashboard remains unchanged.

This plan turns the Explorer from a metadata browser into a practical data exploration tool while staying read-only. It reuses the safe query execution policy established by the Query Workbench instead of introducing a separate mutable execution path.

## Progress

- [x] (2026-04-30) Created prerequisite ExecPlans for Explorer and Query Workbench.
- [x] (2026-04-30) Reviewed Explorer and Query Workbench scopes to identify the remaining data-viewer gap.
- [ ] Confirm the foundation, Explorer, and Query Workbench implementations exist and tests pass.
- [ ] Add state/query helpers for view previews, schema inspection, pagination, and basic statistics.
- [ ] Add StarHTML components for data preview tables, pagination controls, column metadata, empty/error states, and SQL Workbench handoff.
- [ ] Add routes/endpoints for view data preview and metadata fragments.
- [ ] Add tests for safe SQL generation, pagination, row limits, missing views, empty results, schema rendering, and old dashboard preservation.
- [ ] Run `starhtml-check`, Studio explorer/query tests, data viewer tests, and old dashboard tests.

## Surprises & Discoveries

- Observation: The Explorer plan is intentionally metadata-only.
  Evidence: It lists views and shows view definitions but defers data preview and active exploration.

- Observation: The Query Workbench already establishes read-only SQL execution, batching, row limits, and error handling.
  Evidence: The Query Workbench plan adds `StudioContext.execute_query()` and `/sql/execute` with read-only enforcement.

- Observation: Data preview must quote view identifiers correctly.
  Evidence: View names may include schemas. Preview queries must avoid string concatenation and use an existing quoting helper or a local safe identifier-quoting function.

## Decision Log

- Decision: Implement the data viewer after Query Workbench.
  Rationale: The viewer should reuse the same read-only query boundary and row-limit behavior rather than creating another execution engine.
  Date/Author: 2026-04-30 / planning session

- Decision: Keep the data viewer read-only.
  Rationale: Editing data is out of scope for Duckalog’s catalog configuration UI and would require different safety semantics.
  Date/Author: 2026-04-30 / planning session

- Decision: Use generated SELECT statements for previews and offer a handoff to SQL Workbench.
  Rationale: Users need quick preview by default, but the Workbench is the right place for custom SQL.
  Date/Author: 2026-04-30 / planning session

- Decision: Do not add charts or exports in this plan.
  Rationale: Pagination, schema inspection, and robust preview behavior are the core missing data-viewing capabilities. Charts and exports can be later UX layers.
  Date/Author: 2026-04-30 / planning session

## Outcomes & Retrospective

No implementation outcomes have been produced yet. At completion, update this section with exact routes, helper names, pagination model, query safety behavior, validation coverage, and test results.

## Context and Orientation

Catalog Studio already has an Explorer for configured views and a Query Workbench for ad-hoc read-only SQL. The old dashboard has basic query capabilities, but the new Studio needs a richer data viewer that starts from a known catalog view and helps the user inspect rows and columns without writing SQL by hand.

The data viewer should live in the new `src/duckalog/studio/` package. It should not modify config files. It should not change the old `src/duckalog/dashboard/` implementation. It should use the same DuckDB connection and read-only policy as `StudioContext.execute_query()` from the Query Workbench plan.

## Plan of Work

Begin by verifying prerequisites. The Studio package must expose Explorer pages and Query Workbench execution. If those are missing, implement the earlier plans first.

Add data-viewer helpers to `src/duckalog/studio/state.py` or a dedicated module such as `src/duckalog/studio/data_viewing.py`. Required helper operations are:

    quote_view_reference(view) -> str
    build_preview_query(view, *, limit: int, offset: int = 0, order_by: str | None = None) -> str
    get_view_columns(view_name) -> list[dict]
    preview_view_rows(view_name, *, limit: int, offset: int = 0) -> PreviewResult
    get_view_stats(view_name) -> dict

Use the validated `ViewConfig` from `StudioContext.get_view()` to construct safe queries. For schema-qualified views, quote schema and name separately. Reject unknown views before query construction. Do not accept arbitrary user-supplied identifiers without validation against known columns.

Implement pagination. The first version can use offset/limit pagination with next/previous buttons. Use the configured Studio row limit as an upper bound for page size. Default page size should be modest, for example 50 rows. A page-size selector may offer 25, 50, 100, and the configured limit. The UI should say when the preview is capped.

Implement column inspection. Use DuckDB metadata queries such as `DESCRIBE SELECT * FROM <view> LIMIT 0` or a safe equivalent to retrieve column names and types. Show column name, type, nullable if available, and a simple role badge if later semantic models are available. If metadata queries fail for a view, show a non-fatal error and keep the rest of the page usable.

Implement basic statistics. At minimum show preview row count, page size, offset/range, and whether more rows may exist. Optionally show total row count via `SELECT count(*)` behind a button or lazy endpoint because count can be expensive for large external sources. Do not run expensive count automatically unless tests and performance checks show it is safe.

Add StarHTML components. On a view detail page, add a “Data” tab or section with a preview table, pagination controls, column metadata panel, error area, and a “Open in SQL Workbench” link/button. The handoff should prefill or display the generated query if the Workbench supports prefilled SQL; otherwise copy/show the query text.

Add routes. Recommended endpoints are `GET /catalog/{view_name}/data` for a full data viewer page, `GET or POST /catalog/{view_name}/data/preview` for pagination updates, and `GET /catalog/{view_name}/columns` for a columns fragment if needed. If Explorer already has a tabbed route convention, follow it and update tests.

Keep all route operations read-only. They may execute generated SELECT/DESCRIBE/EXPLAIN-style queries only. Invalid view names return 404. Query/runtime errors render visible error states without crashing the app.

Add tests. Required tests include building preview SQL for schema and non-schema views, rejecting unknown views, safely quoting odd but valid view names, rendering a data viewer page, rendering a preview table, next/previous pagination, respecting row limits, showing empty-result state, showing query errors, rendering columns, and leaving old dashboard tests untouched.

## Concrete Steps

Verify prerequisites:

    uv run pytest tests/test_studio.py tests/test_studio_explorer.py tests/test_studio_query.py -q

Inspect Studio query/explorer helpers:

    rg -n "class StudioContext|execute_query|get_view|get_views|catalog|sql-results|row_limit" src/duckalog/studio tests/test_studio*.py

After helper implementation, smoke-test safe preview behavior:

    uv run python - <<'PY'
    import asyncio
    from pathlib import Path
    from duckalog.config import load_config
    from duckalog.studio import StudioContext
    from duckalog.studio.data_viewing import build_preview_query

    path = Path('/tmp/duckalog-data-viewer.yaml')
    path.write_text('''version: 1
    duckdb:
      database: ":memory:"
    views:
      - name: demo
        db_schema: analytics
        sql: "select 1 as id, 'a' as label union all select 2, 'b'"
    ''')
    ctx = StudioContext(config=load_config(str(path)), config_path=str(path), row_limit=50)
    view = ctx.get_view('demo')
    query = build_preview_query(view, limit=10, offset=0)
    assert 'analytics' in query and 'demo' in query
    async def main():
        batches = []
        async for batch in ctx.execute_query(query):
            batches.append(batch)
        assert batches[0][0]
    asyncio.run(main())
    print('data viewer helper ok')
    PY

Run StarHTML checks:

    starhtml-check src/duckalog/studio/app.py
    starhtml-check src/duckalog/studio/components.py
    starhtml-check src/duckalog/studio/data_viewer_components.py

Run focused tests:

    uv run pytest tests/test_studio_data_viewer.py -q

Run broader validation:

    uv run pytest tests/test_studio*.py tests/test_dashboard.py -q

Manual smoke test:

    cat >/tmp/duckalog-data-viewer.yaml <<'YAML'
    version: 1
    duckdb:
      database: ":memory:"
    views:
      - name: demo_view
        sql: "select * from range(125) as t(id)"
    YAML

    uv run duckalog studio /tmp/duckalog-data-viewer.yaml --port 8788 --row-limit 100

Then verify:

    curl -i http://127.0.0.1:8788/catalog/demo_view/data
    curl -s http://127.0.0.1:8788/catalog/demo_view/data | rg "Data Preview|id|Next|SQL Workbench"

## Validation and Acceptance

A user can open a data viewer for a configured view, see a preview table, inspect columns, page through results, and jump to the SQL Workbench with the generated query. The UI handles missing views, empty results, and query errors clearly. All operations are read-only and respect row limits.

Automated tests must prove helper behavior, route behavior, pagination, row-limit behavior, schema-qualified quoting, and old dashboard preservation. `starhtml-check` must pass on changed Studio UI files.

## Idempotence and Recovery

This plan does not write catalog files. It executes read-only generated queries and uses temporary test configs. Repeated tests should be deterministic. If a data source is external or slow, show errors or partial metadata gracefully instead of blocking the whole page.

If implementation must be backed out, remove data-viewer helpers/components/routes/tests and navigation links. Keep Explorer and Query Workbench intact.

## Artifacts and Notes

Prerequisite ExecPlans:

    .execflow/plans/catalog-studio-explorer/execplan.md
    .execflow/plans/catalog-studio-query-workbench/execplan.md

Relevant code references:

    src/duckalog/studio/state.py
    src/duckalog/dashboard/state.py
    src/duckalog/dashboard/routes/views.py
    src/duckalog/dashboard/routes/query.py
    src/duckalog/config/models.py:ViewConfig

Future work can add charts, export CSV/Parquet, saved preview filters, profiling, and semantic-model-aware exploration. Those are out of scope here.

## Revision Note

2026-04-30: Initial Catalog Studio Data Viewer Polish ExecPlan created.
