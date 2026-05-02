# Add the Catalog Studio Query Workbench

This ExecPlan is a living document. The sections `Progress`, `Surprises & Discoveries`, `Decision Log`, and `Outcomes & Retrospective` must be kept up to date as work proceeds.

This document must be maintained in accordance with `.execflow/PLANS.md` from the repository root. It builds on the completed umbrella brainstorm at `.execflow/plans/rebuild-duckalog-ui-starhtml/brainstorm.md`, the prerequisite foundation plan at `.execflow/plans/starhtml-catalog-studio-foundation/execplan.md`, and the prerequisite explorer plan at `.execflow/plans/catalog-studio-explorer/execplan.md`. If those plans have not been implemented yet, implement them first. This Query Workbench plan assumes that `src/duckalog/studio/`, `duckalog.studio.create_app()`, `StudioContext`, the `duckalog studio` CLI command, and read-only `/catalog/` Studio pages already exist.

## Purpose / Big Picture

After this change, a user can open Duckalog Catalog Studio, navigate to a SQL workbench, type a read-only SQL query, execute it, and see query results stream into the browser in batches. The workbench rejects write queries such as `DROP TABLE`, shows clear validation and runtime errors, respects the Studio row limit, and displays when results are truncated. The existing Litestar dashboard and its `/query` route remain unchanged.

This plan completes the read-only “explore and analyze” half of Catalog Studio: the prior Explorer pages let users discover configured views, and this Workbench lets them query the catalog interactively. It deliberately does not edit catalog files, run catalog builds, or add a full data preview browser. Those responsibilities belong to later ExecPlans.

## Progress

- [x] (2026-04-30) Completed the umbrella brainstorm and selected a parallel StarHTML “Catalog Studio” direction.
- [x] (2026-04-30) Created the prerequisite foundation ExecPlan at `.execflow/plans/starhtml-catalog-studio-foundation/execplan.md`.
- [x] (2026-04-30) Created the prerequisite explorer ExecPlan at `.execflow/plans/catalog-studio-explorer/execplan.md`.
- [x] (2026-04-30) Read the foundation and explorer plans, existing dashboard query route, dashboard state/query execution code, and query-related scout context.
- [x] (2026-04-30) Ran a scout pass and saved query-workbench-specific context at `.execflow/plans/catalog-studio-query-workbench/context.md`.
- [ ] Confirm the foundation and explorer implementations exist and expose the expected Studio package, shell, and navigation.
- [ ] Add or confirm `StudioContext.execute_query()` with the same read-only, batched async generator protocol as the existing dashboard.
- [ ] Add StarHTML components for the SQL workbench page, result table shell, row rendering, loading state, and error display.
- [ ] Add `GET /sql/` route for the workbench page and `POST /sql/execute` route for StarHTML/Datastar streaming result updates.
- [ ] Add tests for direct query execution, write rejection, row limits, batching, concurrent queries, SQL page rendering, streaming success, empty SQL, invalid SQL, and truncation indication.
- [ ] Run `starhtml-check`, Studio tests, and existing dashboard tests, then update this plan with results.

## Surprises & Discoveries

- Observation: The existing dashboard’s query execution engine is already separated from the Litestar route.
  Evidence: `src/duckalog/dashboard/state.py:DashboardContext.execute_query()` is an async generator that enforces read-only SQL, runs DuckDB work in a thread pool with a per-thread connection, and yields headers first followed by row batches.

- Observation: The existing dashboard route provides a good streaming response shape but is tied to `datastar-py` and Litestar decorators.
  Evidence: `src/duckalog/dashboard/routes/query.py:QueryController.execute_query()` uses `@datastar_response`, `read_signals(request)`, and `ServerSentEventGenerator.patch_elements()` / `patch_signals()` to morph a result container, append table rows, update row count, and surface errors.

- Observation: The Studio package is a prerequisite and may not exist until earlier ExecPlans are executed.
  Evidence: The query scout context notes that `src/duckalog/studio/` is planned by `starhtml-catalog-studio-foundation` but not guaranteed to be present before implementation. This plan must be implemented after the foundation and explorer plans, not in parallel with their shared route and component files.

## Decision Log

- Decision: Create Query Workbench after Catalog Studio Explorer and before any catalog editing plans.
  Rationale: Querying is read-only but exercises the most important StarHTML/Datastar interactivity and streaming patterns. It is safer than config editing and gives users immediate value after browsing catalog views.
  Date/Author: 2026-04-30 / planning session

- Decision: Reuse the existing `execute_query()` behavior and batch protocol rather than inventing a new query engine for Studio.
  Rationale: The current dashboard already has tested read-only enforcement, row limiting, batched streaming, and concurrent execution behavior. Reusing this boundary reduces change amplification and keeps query policy in one place.
  Date/Author: 2026-04-30 / planning session

- Decision: Use `/sql/` and `/sql/execute` as the Studio routes.
  Rationale: “SQL” matches the Studio navigation label and avoids colliding with the old dashboard’s `/query` route. Keeping the execute endpoint nested under `/sql` mirrors the old dashboard’s `/query/execute` structure while using Studio product language.
  Date/Author: 2026-04-30 / planning session

- Decision: Do not add cancellation, saved queries, result export, charts, or data-preview shortcuts in this ExecPlan.
  Rationale: The goal is a minimal, correct, streaming read-only workbench. Extra workflow features would widen scope and obscure whether StarHTML SSE streaming works reliably.
  Date/Author: 2026-04-30 / planning session

## Outcomes & Retrospective

No implementation outcomes have been produced yet. At completion, update this section with the exact routes added, how StarHTML streaming was implemented, the tests and `starhtml-check` results, any concurrency or DuckDB connection surprises, and the recommended next ExecPlan. The expected next plan after this one is Catalog Studio Editing Safety, unless implementation discovers a need for a small Studio cleanup plan first.

## Context and Orientation

Duckalog builds DuckDB catalogs from YAML or JSON configuration files. A Catalog Studio user should be able to browse configured views and then run ad-hoc read-only SQL against the DuckDB database that Duckalog uses. “Read-only” means the SQL may inspect data, schemas, or query plans, but it must not mutate database state. The existing dashboard allows SQL that starts with `SELECT`, `WITH`, `SHOW`, `DESCRIBE`, or `EXPLAIN`, and rejects anything else with `ValueError("Only read-only queries are allowed")`.

The current query implementation is split across two files. `src/duckalog/dashboard/state.py:DashboardContext.execute_query()` is the execution engine. It is an async generator, which means callers can loop over results as they become available instead of waiting for the full query to finish. Its first yield is a tuple containing column names and no rows, like `(["x", "y"], [])`. Later yields contain no columns and a batch of row tuples, like `([], [(1, 2), (3, 4)])`. It stops after `row_limit` rows. It uses `asyncio.to_thread()` and creates a new DuckDB connection inside that worker thread because DuckDB connections are not thread-safe.

`src/duckalog/dashboard/routes/query.py:QueryController.execute_query()` is the old Litestar/Datastar streaming route. It reads the SQL from Datastar signals, calls `ctx.execute_query(sql)`, sends an initial table shell when it receives the header batch, appends rows to the table body for later batches, then updates a final row count. On validation or runtime errors it patches an error signal. The new Studio route should keep the same behavior but express it with the StarHTML and Datastar helpers available in the new `duckalog.studio` package.

The prerequisite foundation plan creates the `src/duckalog/studio/` package and app shell. The prerequisite explorer plan adds read-only catalog pages. This Query Workbench plan extends those Studio files. It should not create another app, another CLI command, or another query engine module unless implementation evidence shows that a small helper module is needed to keep `app.py` and `components.py` deep and readable.

## Plan of Work

Begin by verifying that the foundation and explorer implementations exist. `from duckalog.studio import create_app, StudioContext` must succeed, the `duckalog studio` CLI command must exist, and the Studio app should already serve `/`, `/health`, `/catalog/`, and `/catalog/{view_name}`. If these prerequisites are missing, stop and implement the earlier ExecPlans first.

Add or confirm `StudioContext.execute_query()` in `src/duckalog/studio/state.py`. The method must accept `sql: str`, optional `limit: int | None = None`, and `batch_size: int = 50`. It must expose the same observable protocol as `DashboardContext.execute_query()`: reject SQL not starting with `SELECT`, `WITH`, `SHOW`, `DESCRIBE`, or `EXPLAIN`; default the effective limit to `self.row_limit`; yield column headers first as `(columns, [])`; yield row batches as `([], rows)`; and raise exceptions so the route can turn them into visible errors. The simplest implementation may delegate to `DashboardContext.execute_query()` if `StudioContext` already wraps or owns a dashboard context. If it copies the logic, keep the policy identical and add tests that prove the two protocols match for simple cases.

Add query workbench components in `src/duckalog/studio/components.py` or a new Studio component module if the foundation already split components by feature. The page should include a heading such as “SQL Workbench”, a textarea bound to a StarHTML signal named `sql`, an execute button that posts to `/sql/execute`, a loading indicator, an error area, and a results container with id `sql-results`. The initial results area should say “Execute a read-only query to see results.” The UI copy must make the safety constraint clear: only read-only SQL is allowed. Use StarHTML signal names in snake_case, for example `sql`, `loading`, `error`, and `row_count`.

Add small rendering helpers for result tables. One helper should render the table shell from a column list with an element id such as `sql-results` and a tbody id such as `sql-results-tbody`. Another helper should render a batch of table rows. Escape or render cell values safely through StarHTML element creation rather than string-concatenating untrusted values where possible. If StarHTML’s SSE patch API requires HTML strings, centralize string generation in one helper and document the reason in `Surprises & Discoveries`.

Update the Studio app route registration in `src/duckalog/studio/app.py`. Add `GET /sql/` to render the workbench inside the existing Studio shell. Add `POST /sql/execute` to stream result updates. The `POST` route must read the SQL value from the StarHTML/Datastar request payload. If no SQL was provided or the trimmed SQL is empty, stream an error update and set `loading` false. For valid input, clear any previous error, set loading true, stream headers and rows from `ctx.execute_query(sql)`, then set loading false and update the row count. If `ctx.execute_query()` raises `ValueError`, stream the read-only error. If DuckDB raises a runtime error, stream a message beginning with `Query error:`. Always reset loading to false before the stream ends.

Before implementing the streaming route, inspect the actual StarHTML version installed by the foundation work and identify its SSE/signal helpers. The repository’s StarHTML skill describes an SSE pattern using `@sse`, `yield elements(...)`, and `yield signals(...)`. Prefer that idiom if available. If the installed StarHTML API differs, adapt locally inside `src/duckalog/studio/app.py` and record the exact API in `Surprises & Discoveries`. Do not reuse `datastar_py.litestar.datastar_response` in the new Studio route unless StarHTML cannot provide an equivalent and you record why; the purpose of this plan is to prove the StarHTML-native streaming path.

Update navigation so the existing “SQL” nav item links to `/sql/` and is visibly active when the workbench is open, following whatever active-nav pattern the foundation or explorer implementation established. Do not add data preview or edit links that perform real actions.

Add tests. Put them in `tests/test_studio.py` if that file remains manageable, or create `tests/test_studio_query.py` if the existing Studio tests have become large. Add direct context tests for `execute_query()` because they are fast and isolate query policy from StarHTML streaming. Add route tests for the workbench page and streaming endpoint. The streaming tests should check status code, content type when possible, and response text for table headers, row values, row count, and errors. Add a concurrency test that starts several `StudioContext.execute_query()` tasks with `asyncio.gather()` and proves they all return their own rows. Keep old dashboard tests unchanged.

Run `starhtml-check` on all Studio files that contain StarHTML components or reactive attributes. Then run the new Studio query tests, the broader Studio tests, and `tests/test_dashboard.py` to prove the old dashboard still works.

## Concrete Steps

Work from the repository root `/Users/volker/coding/libs/duckalog`.

First verify prerequisites:

    uv run python - <<'PY'
    from duckalog.studio import create_app, StudioContext
    print(create_app, StudioContext)
    PY

Then confirm the expected Studio routes are already registered by prior plans. The exact introspection command may differ depending on the StarHTML app object, so use repository tests and a smoke run if route introspection is not simple:

    uv run pytest tests/test_studio.py -q

If this fails because the foundation or explorer work is missing, stop and implement those plans first.

Inspect the StarHTML API available in the environment before writing the SSE route:

    uv run python - <<'PY'
    import inspect
    import starhtml
    print('starhtml module:', starhtml)
    for name in ('sse', 'signals', 'elements', 'get', 'post', 'star_app'):
        print(name, getattr(starhtml, name, None))
    PY

If this command shows that `sse`, `signals`, or `elements` live in submodules, inspect those submodules and record the discovery. The implementation should use the installed API, not remembered examples.

After adding `StudioContext.execute_query()`, validate the batch protocol with a small script:

    uv run python - <<'PY'
    import asyncio
    from pathlib import Path
    from duckalog.config import load_config
    from duckalog.studio import StudioContext

    path = Path('/tmp/duckalog-studio-query.yaml')
    path.write_text('''
    version: 1
    duckdb:
      database: ":memory:"
    views:
      - name: t
        sql: "select 1 as x"
    ''')
    ctx = StudioContext(config=load_config(str(path)), config_path=str(path), row_limit=2)

    async def main():
        batches = []
        async for batch in ctx.execute_query('SELECT * FROM (VALUES (1), (2), (3)) AS t(x)'):
            batches.append(batch)
        print(batches)
        assert batches[0][0] == ['x']
        assert sum(len(rows) for _, rows in batches) == 2
        try:
            async for _ in ctx.execute_query('DROP TABLE t'):
                pass
            raise AssertionError('write query should have failed')
        except ValueError as exc:
            assert 'read-only' in str(exc)
    asyncio.run(main())
    print('query context ok')
    PY

After adding routes and components, run StarHTML checks:

    starhtml-check src/duckalog/studio/app.py
    starhtml-check src/duckalog/studio/components.py

If implementation creates `src/duckalog/studio/query.py` or another component file, run the checker on that file too.

Run focused tests:

    uv run pytest tests/test_studio.py -q

or, if query tests are split out:

    uv run pytest tests/test_studio.py tests/test_studio_query.py -q

Then verify the old dashboard still passes:

    uv run pytest tests/test_dashboard.py -q

Finally, manually smoke-test the workbench. Create a sample config if needed:

    cat >/tmp/duckalog-studio-query.yaml <<'YAML'
    version: 1
    duckdb:
      database: ":memory:"
    views:
      - name: demo_view
        sql: "select 1 as id, 'studio' as label"
        description: "Demo view"
    YAML

Start the Studio app:

    uv run duckalog studio /tmp/duckalog-studio-query.yaml --port 8788 --row-limit 2

In another terminal, verify the page exists:

    curl -i http://127.0.0.1:8788/sql/
    curl -s http://127.0.0.1:8788/sql/ | rg "SQL Workbench|Execute|read-only|sql-results"

Then verify the streaming endpoint. The exact payload shape may depend on StarHTML’s request format. If StarHTML posts signals as JSON, a command like this should work:

    curl -i -X POST http://127.0.0.1:8788/sql/execute \
      -H 'Content-Type: application/json' \
      -d '{"sql":"SELECT 1 as a, 2 as b"}'

The expected response is an event stream or streaming response containing enough patched HTML or signals to identify columns `a` and `b`, values `1` and `2`, and no error. If StarHTML requires a different signal payload, update this plan with the working command.

Verify write rejection:

    curl -s -X POST http://127.0.0.1:8788/sql/execute \
      -H 'Content-Type: application/json' \
      -d '{"sql":"DROP TABLE demo_view"}' | rg "read-only|error"

Verify row-limit indication:

    curl -s -X POST http://127.0.0.1:8788/sql/execute \
      -H 'Content-Type: application/json' \
      -d '{"sql":"SELECT * FROM range(10)"}' | rg "limited|2 row"

## Validation and Acceptance

Acceptance is user-visible. After this plan is implemented, the running Studio app has a SQL navigation item that opens `/sql/`. The page contains a textarea, execute button, loading and error areas, and a results container. Submitting `SELECT 1 as a, 2 as b` streams a result table with columns `a` and `b` and row values `1` and `2`. Submitting `DROP TABLE something` does not execute and shows a read-only error. Submitting invalid SQL shows a query error. Queries that return more than the configured row limit show only the limited number of rows and an indication that the result was limited.

Automated validation must cover both the execution engine and route behavior. Direct context tests must prove header-first batch protocol, row limiting, write rejection, large-result batching, and concurrent query execution. Route tests must prove the `/sql/` page renders and `/sql/execute` produces streaming success and error responses. The old dashboard tests must continue to pass, especially the existing query and SSE tests in `tests/test_dashboard.py`.

StarHTML-specific validation requires `starhtml-check` on all changed Studio files with no ERROR findings. This matters because StarHTML has reactive attribute rules that ordinary Python tests may not catch, such as signal naming, positional argument order, and correct signal usage in reactive attributes.

## Idempotence and Recovery

This plan is additive on top of the foundation and explorer. It adds read-only query execution exposure, components, routes, and tests. It does not write catalog files and should not modify database state because write SQL is rejected before execution. Test files must use pytest temporary directories and in-memory DuckDB databases unless a file-backed database is specifically needed.

If StarHTML’s SSE API is different from expected, pause long enough to inspect the installed package and adapt the route locally. Record the final API and a working curl example in `Surprises & Discoveries`. Do not change old Litestar dashboard streaming code to make Studio streaming work.

If the streaming route is difficult to test at the HTTP level because the test client buffers server-sent events, keep direct `StudioContext.execute_query()` tests strong and add a route test that verifies the endpoint returns the correct status/content type and contains a representative first chunk. Record any test-client limitation in `Surprises & Discoveries`.

If concurrency tests fail because `StudioContext` accidentally shares a DuckDB connection across worker threads, fix `execute_query()` to create a per-thread connection as the existing dashboard does. Do not reuse a single `self.connection` object inside `asyncio.to_thread()`.

If this implementation must be backed out, remove only the Query Workbench additions: `StudioContext.execute_query()` if unused elsewhere, `/sql/` and `/sql/execute` route registration, SQL workbench components, navigation link activation changes, and query tests. Keep the foundation and explorer pages intact.

## Artifacts and Notes

The umbrella brainstorm is:

    .execflow/plans/rebuild-duckalog-ui-starhtml/brainstorm.md

The prerequisite foundation ExecPlan is:

    .execflow/plans/starhtml-catalog-studio-foundation/execplan.md

The prerequisite explorer ExecPlan is:

    .execflow/plans/catalog-studio-explorer/execplan.md

The query scout context is:

    .execflow/plans/catalog-studio-query-workbench/context.md

Relevant existing code references are:

    src/duckalog/dashboard/state.py:DashboardContext.execute_query
    src/duckalog/dashboard/routes/query.py:QueryController.query_form
    src/duckalog/dashboard/routes/query.py:QueryController.execute_query
    src/duckalog/dashboard/components/layout.py:table_header_component
    src/duckalog/dashboard/components/layout.py:table_rows_component
    tests/test_dashboard.py

The required query batch protocol is:

    first yield: (columns, [])
    later yields: ([], rows)

where `columns` is a list of column names and `rows` is a list of row tuples. The row count displayed to users should count only actual data rows, not the header batch.

## Interfaces and Dependencies

At the end of this plan, `StudioContext` must expose this method:

    async def execute_query(
        self,
        sql: str,
        limit: int | None = None,
        batch_size: int = 50,
    ) -> AsyncGenerator[tuple[list[str], list[tuple[Any, ...]]], None]: ...

It must preserve the existing read-only allowlist:

    SELECT
    WITH
    SHOW
    DESCRIBE
    EXPLAIN

The Studio app must expose these routes in addition to routes from prior plans:

    GET /sql/
    POST /sql/execute

The SQL workbench component must include stable element ids so tests and streaming patches have durable targets:

    sql-input
    sql-results
    sql-results-tbody
    sql-row-count

If the foundation or explorer plan established different id naming conventions, keep the spirit of stable semantic ids and update tests accordingly. Do not add new project dependencies for this plan. StarHTML and any existing Datastar integration should already be available from the foundation UI extra.

The next ExecPlan should be Catalog Studio Editing Safety. It should not start with form controls. It should first define the safe write model: how to load raw config text, validate edits against `Config`, preview diffs, create backups, save atomically, and recover on failure.

## Revision Note

2026-04-30: Initial Catalog Studio Query Workbench ExecPlan created. It is scoped to read-only SQL execution and StarHTML streaming so Catalog Studio can support analysis before the project takes on catalog editing safety and expert editor complexity.
