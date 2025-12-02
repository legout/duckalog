## 1. Dashboard capability and ASGI app

- [x] 1.1 Define a `dashboard-ui` capability spec with requirements for launching a local dashboard, home page behavior, views browser, view detail, query runner, and build trigger/status.
- [x] 1.2 Implement a minimal ASGI app (in `src/duckalog/dashboard/`) that wires starhtml/starui layout and routes for the dashboard home, views browser, view detail, query runner, and build endpoint.
- [x] 1.3 Add a small set of unit/integration tests that exercise the ASGI app routes against an in-memory or temporary DuckDB catalog.

## 2. CLI / Python API integration

- [x] 2.1 Add a `duckalog ui` CLI command that accepts a catalog config path (and optional host/port) and launches the dashboard server.
- [x] 2.2 Provide a Python API entry point (e.g. `duckalog.dashboard.run_dashboard(config: Config, *, host: str, port: int)`) for programmatic usage.
- [x] 2.3 Ensure CLI and API share the same underlying launch logic and error handling (e.g. invalid config, port already in use).

## 3. UX, constraints, and documentation

- [x] 3.1 Implement reasonable defaults for local development: loopback-only host by default, explicit warning if bound to non-local interfaces, and a clearly documented default port.
- [x] 3.2 Ensure the dashboard works offline with all assets served from the duckalog package (no external CDNs or JS build steps).
- [x] 3.3 Add documentation pages under `docs/` describing how to launch and use the dashboard, its limitations (single-user, local-first), and how it relates to other duckalog interfaces.
