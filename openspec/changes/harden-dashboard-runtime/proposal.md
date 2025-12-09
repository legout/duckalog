# Change: Harden dashboard runtime (connections, shutdown, debug)

## Why
The dashboard currently runs blocking DuckDB calls on the event loop, leaves connections open, and keeps Litestar debug mode on. These issues risk stalls and leaks under load.

## What Changes
- Add connection management/pooling suitable for concurrent queries.
- Offload blocking DB work to a threadpool where needed.
- Register startup/shutdown hooks to open/close resources cleanly.
- Disable debug in production/default app factory.
- Add basic health checks.

## Impact
- Specs: `dashboard-ui`
- Code: `dashboard/app.py`, `state.py`, possibly `routes/query.py`
- Tests: cover shutdown/health
