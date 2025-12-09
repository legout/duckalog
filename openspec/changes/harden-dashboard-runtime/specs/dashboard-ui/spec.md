## ADDED Requirements

### Requirement: Dashboard Runtime Defaults
The dashboard SHALL use production-safe runtime defaults for the Litestar application.

#### Scenario: Production-safe defaults
- **WHEN** the dashboard app is created without explicit debug overrides
- **THEN** debug mode is disabled by default
- **AND** a simple health check endpoint or hook is available for runtime monitoring.

### Requirement: Dashboard Runtime Resource Management
The dashboard SHALL manage database connections and blocking work safely for concurrent read workloads.

#### Scenario: Connection lifecycle
- **WHEN** the dashboard starts and stops
- **THEN** database connections are initialized on startup
- **AND** all connections are closed or released during shutdown.

#### Scenario: Concurrent read queries
- **WHEN** multiple read-only queries are executed concurrently
- **THEN** blocking DuckDB work is offloaded from the event loop (for example via a threadpool or connection pool)
- **AND** resource limits prevent connection or worker exhaustion.
