# Change: Stream query results incrementally via SSE

## Why
Query execution currently fetches all rows then patches the DOM once. This blocks the event loop and fails the spec requirement for streaming results as they are produced.

## What Changes
- Stream query rows incrementally using Datastar SSE patches.
- Offload DuckDB execution to a worker/executor to avoid blocking the loop.
- Add loading/progress signals and empty/error states.
- Update tests/docs for streamed queries.

## Impact
- Specs: `dashboard-ui`
- Code: `src/duckalog/dashboard/routes/query.py`, `state.py`
- Tests: query streaming SSE coverage
