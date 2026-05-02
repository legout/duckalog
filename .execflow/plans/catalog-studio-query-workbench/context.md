# Code Context — catalog-studio-query-workbench

## Files Retrieved

1. `src/duckalog/dashboard/state.py` (lines 82–143) — `DashboardContext.execute_query()`, the core async generator for streaming SQL results in batches; also `get_views()`, `get_view()`, `get_catalog_stats()`. **This is the primary boundary to reuse.**

2. `src/duckalog/dashboard/routes/query.py` (lines 1–246) — `QueryController` with SSE/Datastar streaming via `datastar_py.ServerSentEventGenerator as SSE` + `@datastar_response` decorator; `RunController` for catalog build status. **Key SSE streaming pattern to translate to StarHTML.**

3. `tests/test_dashboard.py` (lines 1–1346) — four test classes relevant to query workbench:
   - `TestDashboardContext` (lines 44–104): tests `execute_query()` batch format, write rejection, row limits, progressive streaming, large result set batching, error propagation
   - `TestSSEDashboard` (lines 195–293): tests `/run/status` SSE, `/query/execute` endpoint, datastar bindings
   - `TestRealtimeQueryStreaming` (lines 295–500): tests query route config, page form elements, result display, row limits, concurrent queries, thread pool avoidance
   - `TestConcurrentQueries` (lines 1270–1346): tests concurrent async query execution without blocking

4. `src/duckalog/dashboard/components/layout.py` (lines 1–430) — `base_layout()`, `page_header()`, `card()`, `table_header_component()`, `table_rows_component()` — component patterns for query results UI.

5. `src/duckalog/dashboard/routes/views.py` (lines 1–131) — reference for route registration patterns (`/views`, `/views/{view_name}`) to model `/sql/` and `/sql/execute`.

6. `src/duckalog/config/models.py` (lines 1–490) — `ViewConfig` fields (name, schema, sql, source, tags, description) — used to understand what a query workbench might reference.

7. `pyproject.toml` (lines 1–100) — existing `ui` extra includes `datastar-py>=0.7.0`, `litestar>=2.0.0`, `htpy>=0.1.0`; no `starhtml` yet.

8. `.execflow/plans/starhtml-catalog-studio-foundation/execplan.md` + `catalog-studio-explorer/execplan.md` — foundation not yet implemented; `duckalog.studio` package does not yet exist.

## Key Code

### DashboardContext.execute_query — the streaming query engine

```python
# src/duckalog/dashboard/state.py (lines 82–143)

async def execute_query(
    self, sql: str, limit: int | None = None, batch_size: int = 50
) -> AsyncGenerator[tuple[list[str], list[tuple[Any, ...]]], None]:
    # Read-only enforcement (lines 100–103)
    sql_upper = sql.strip().upper()
    if not sql_upper.startswith(("SELECT", "WITH", "SHOW", "DESCRIBE", "EXPLAIN")):
        raise ValueError("Only read-only queries are allowed")

    # Thread pool execution (lines 108–143)
    # - Creates a NEW DuckDB connection per thread (connections not thread-safe)
    # - Queues: first (columns, []) then batches of ([], rows)
    # - effective_limit defaults to self.row_limit (1000)
    # - batch_size=50
    # - Yields AsyncGenerator[tuple[list[str], list[tuple[Any, ...]]], None]
```

**Batch protocol:**
- 1st yield: `(column_names_list, [])` — headers only, zero rows
- Subsequent yields: `([], batch_of_row_tuples)` — rows only, no columns
- On error: raises exception; stream ends with no sentinel value

### SSE/Datastar streaming in the existing dashboard

```python
# src/duckalog/dashboard/routes/query.py (lines 107–186)

@post("/execute")
@datastar_response
async def execute_query(self, request: Request, ctx: DashboardContext) -> AsyncGenerator:
    # Uses datastar_py ServerSentEventGenerator
    signals = await read_signals(request)
    sql = signals.get("sql", "").strip()

    yield SSE.patch_signals({"error": "", "loading": True})

    try:
        async for batch_columns, batch_rows in ctx.execute_query(sql):
            if first_batch:
                # Yield initial table structure with header
                yield SSE.patch_elements(header_html, selector="#query-results", mode="morph")
            else:
                # Append rows to tbody
                yield SSE.patch_elements(rows_html, selector="#results-tbody", mode="append")

        # Final: yield row count and signal update
        yield SSE.patch_signals({"loading": False, "row_count": count_text})
    except ValueError as e:
        yield SSE.patch_signals({"error": str(e), "loading": False})
```

**Key UI elements:**
- `div(id="query-results")` — container for result table
- `<thead id="results-thead">` — column headers
- `<tbody id="results-tbody">` — appended row batches
- `<p id="row-count">` — final row count display
- Datastar signals: `sql`, `loading`, `error`, `row_count`

### Test patterns in test_dashboard.py

```python
# Streaming batch validation (lines 438–452)
async for batch_columns, batch_rows in ctx.execute_query(large_query):
    batches.append(batch)
assert len(batches) >= 4  # headers + 3 batches of 50
assert total_rows == 150

# Row limit enforcement (lines 454–465)
# App created with row_limit=2; query returns 5 rows → only 2 returned

# Write query rejection (lines 81–87)
with pytest.raises(ValueError, match="read-only"):
    async for _ in ctx.execute_query("DROP TABLE foo"):

# Concurrent queries (lines 1305–1340)
async def execute_and_collect(query):
    async for columns, rows in ctx.execute_query(query):
        result.append((columns, rows))
tasks = [asyncio.create_task(execute_and_collect(f"SELECT {i}...")) for i in range(5)]
results = await asyncio.gather(*tasks)  # All 5 run concurrently
```

## Architecture

```
duckalog studio <config.yaml>
  → duckalog.cli:studio command (port 8788, row_limit=500)
      → duckalog.studio.create_app(config, config_path, db_path, row_limit)
          → StudioContext (mirrors DashboardContext)
              → async execute_query(sql) — async generator, batch protocol
          → StarHTML app
              → /                     (studio shell + overview)
              → /catalog/            (views list)
              → /catalog/{name}      (view detail)
              → /sql/                (NEW: query workbench page)       ← this plan
              → /sql/execute         (NEW: SSE streaming POST handler)  ← this plan
              → /health
```

**Critical boundary decisions from existing codebase:**
- `DashboardContext.execute_query()` is the single execution engine. `StudioContext` should delegate to it or reimplement the same protocol.
- SSE/Datastar streaming in the existing dashboard uses `datastar_py` library. StarHTML likely has its own signal/SSE integration — needs validation.
- Read-only enforcement happens in `execute_query()` by checking SQL prefix. The workbench should never bypass this.
- Row limit is per-context (`row_limit=1000` for dashboard, `row_limit=500` planned for studio). The workbench must respect it and display truncation indication.
- Concurrent query execution is tested and supported via async generators.

## Start Here

Open `src/duckalog/dashboard/state.py` lines 82–143 to understand the `execute_query()` batch protocol and thread-pool pattern, then `src/duckalog/dashboard/routes/query.py` lines 107–186 to understand the SSE/Datastar response pattern. These two files are the primary templates for what the StarHTML workbench must replicate.

## Pi-intercom handoff

The foundation plan (`starhtml-catalog-studio-foundation`) is a prerequisite — the `duckalog.studio` package does not yet exist. I am ready to delegate to the orchestrator or proceed with an ExecPlan draft once the foundation exists.

---

## Milestone Recommendations (Independently Verifiable)

### Milestone 1 — StudioContext.execute_query()

**What:** Add `async def execute_query()` to `StudioContext` in `src/duckalog/studio/state.py`, reusing or delegating to the exact same protocol as `DashboardContext.execute_query()`:
1. Read-only enforcement via SQL prefix check
2. Thread-pool DuckDB execution with per-thread connection
3. Queue-based async streaming with batch_size=50
4. First yield: `(columns, [])`, subsequent yields: `([], rows)`, error raises exception

**Verifiable:**
```bash
uv run python - <<'PY'
import asyncio, sys, sys.path.insert(0, 'src')
from pathlib import Path
from duckalog.config import load_config
from duckalog.studio import StudioContext

path = Path('/tmp/duckalog-m1-test.yaml')
path.write_text('version: 1\nduckdb:\n  database: ":memory:"\nviews:\n  - name: t\n    sql: "select 1"')
config = load_config(str(path))
ctx = StudioContext(config=config, config_path=str(path))
async def test():
    batches = []
    async for b in ctx.execute_query("SELECT 1 as x, 2 as y"):
        batches.append(b)
    assert len(batches) == 2, f"Expected 2 batches, got {len(batches)}"
    assert batches[0] == (['x','y'], []), f"Headers wrong: {batches[0]}"
    assert batches[1] == ([], [(1,2)]), f"Rows wrong: {batches[1]}"
    # write rejection
    try:
        async for _ in ctx.execute_query("DROP TABLE t"): pass
        assert False, "Should have raised"
    except ValueError as e:
        assert "read-only" in str(e)
asyncio.run(test())
print("M1 PASS")
PY
```

### Milestone 2 — `/sql/` GET route with query form UI

**What:** Add to `src/duckalog/studio/app.py` a GET route for `/sql/` that renders:
- A SQL textarea input (data-bound to a signal)
- An "Execute" button (triggers POST to `/sql/execute`)
- A `div(id="sql-results")` container (starts with placeholder text)
- Loading/error indicators via StarHTML signals

**Verifiable:**
```bash
curl -s http://127.0.0.1:8788/sql/ | rg "sql|query|execute|textarea|results"
```

### Milestone 3 — `/sql/execute` POST SSE streaming route

**What:** Add POST route `/sql/execute` to `src/duckalog/studio/app.py` that:
1. Reads the SQL signal from the request
2. Validates read-only (or let `execute_query` handle it)
3. Streams `StudioContext.execute_query()` batches
4. For the first batch: sends table header HTML to `#sql-results`
5. For subsequent batches: appends rows to `#sql-tbody`
6. On completion: sends row count signal
7. On error: sends error signal

**Verifiable:**
```bash
curl -s -X POST http://127.0.0.1:8788/sql/execute \
  -H "Content-Type: application/json" \
  -d '{"sql": "SELECT 1 as a, 2 as b"}' | rg "a|b|text/event-stream"
```

### Milestone 4 — Row limits and error handling

**What:** When a query returns more rows than `ctx.row_limit`, display truncation indicator. Invalid SQL returns error signal and message. Empty SQL returns error signal.

**Verifiable:**
```bash
# Large result set truncation
curl -s -X POST http://127.0.0.1:8788/sql/execute \
  -d '{"sql": "SELECT * FROM (VALUES (1),(2),(3)) AS t LIMIT 1000"}' | rg "limited|row|error"

# Invalid query
curl -s -X POST http://127.0.0.1:8788/sql/execute \
  -d '{"sql": "SELECT * FROM nonexistent"}' | rg "error|no such table"
```

### Milestone 5 — Tests covering query/SSE/concurrency/row limits/errors

**What:** Add test methods to `tests/test_studio.py` covering:
- `TestStudioQueryContext.execute_query_returns_correct_batches`
- `TestStudioQueryContext.execute_query_rejects_write`
- `TestStudioQueryContext.execute_query_row_limit_respected`
- `TestStudioQueryContext.execute_query_large_result_batched`
- `TestStudioQueryContext.execute_query_concurrent`
- `TestStudioSQLRoutes.sql_page_returns_200`
- `TestStudioSQLRoutes.sql_execute_returns_streaming_sse`
- `TestStudioSQLRoutes.sql_execute_invalid_query_returns_error`
- `TestStudioSQLRoutes.sql_execute_row_limit_indicator`
- `TestStudioSQLRoutes.sql_execute_empty_sql_returns_error`

**Verifiable:**
```bash
uv run pytest tests/test_studio.py::TestStudioQueryContext tests/test_studio.py::TestStudioSQLRoutes -v
```

### Milestone 6 — `starhtml-check` and existing dashboard tests pass

**What:** Run `starhtml-check` on `src/duckalog/studio/app.py` and `src/duckalog/studio/components.py`. Ensure `tests/test_dashboard.py` still passes.

**Verifiable:**
```bash
starhtml-check src/duckalog/studio/app.py src/duckalog/studio/components.py
uv run pytest tests/test_dashboard.py tests/test_studio.py -q
```

## Open Questions

1. **StarHTML SSE/signal API:** The foundation plan assumes `app, rt = star_app()` syntax. The actual StarHTML SSE integration pattern (how to stream patch events to the browser) must be validated once `duckalog.studio` is created. If StarHTML uses a different SSE protocol than `datastar_py`, the `/sql/execute` milestone needs adaptation.

2. **Concurrency in StudioContext:** `DashboardContext` is instantiated per-request (via Litestar DI). `StudioContext` in the foundation plan may be request-scoped or app-scoped. Thread-pool async query execution should work in either case, but the connection lifecycle matters.

3. **Datastar vs StarHTML signals:** The existing dashboard uses `datastar_py` with `data-signals`, `data-bind`, `data-on-click`. StarHTML has its own reactive signal model. The workbench UI may need a different binding syntax that must be validated.

4. **Route boundary:** Should `/sql/execute` be under `/sql/` (nested, like the dashboard's `/query/execute`) or at the top level `/sql-execute`? The dashboard uses nested controllers; StarHTML may prefer flat routes.

5. **Cancellation:** The existing dashboard does not implement SSE stream cancellation. Should the workbench plan add it? `asyncio.CancelledError` is caught in `RunController.run_status()` but not in `QueryController.execute_query()`.
