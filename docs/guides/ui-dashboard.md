# Duckalog Dashboard

The dashboard is a lightweight, reactive web UI for exploring and managing Duckalog catalogs. It is built entirely in Python using **Datastar** and **Starlette**—no frontend build tools or external CDNs are required.

## Installation Requirements

The dashboard requires the `duckalog[ui]` installation:

```bash
pip install duckalog[ui]
```

This includes:
- **Datastar Python SDK** (`datastar-python>=0.1.0`): Reactive web framework
- **Starlette** (`starlette>=0.27.0`): ASGI web framework  
- **Uvicorn** (`uvicorn[standard]>=0.20.0`): ASGI server
- **CORS middleware**: Security-focused web access control

## Launch from Python (recommended)

```python
from duckalog.dashboard import run_dashboard

run_dashboard("catalog.yaml", host="127.0.0.1", port=8787, row_limit=500)
```

Pass a `Config` object instead of a path if you already loaded one.

## Launch from the CLI

```bash
duckalog ui catalog.yaml --host 127.0.0.1 --port 8787 --row-limit 500
```

- Binds to loopback by default; only expose other hosts if you understand the risk.
- `--row-limit` caps ad-hoc query results (defaults to 500 rows).
- The CLI prints the dashboard URL after startup.

## Production Deployment

For production use, enable security features:

```bash
# Set admin token for mutating operations
export DUCKALOG_ADMIN_TOKEN="your-secure-random-token"
duckalog ui catalog.yaml --host 0.0.0.0 --port 8000
```

### Runtime Configuration

The dashboard includes several runtime hardening features:

**Debug Mode**
- Debug mode is **disabled by default** for production safety
- To enable debug mode during development:
  ```bash
  export DASHBOARD_DEBUG=true
  duckalog ui catalog.yaml
  ```

**Health Monitoring**
- Built-in `/health` endpoint for monitoring application status
- Returns JSON with status and timestamp
- Checks database connectivity
- Returns 200 for healthy, 500 for unhealthy

**Connection Management**
- Database connections are properly managed via startup/shutdown lifecycle hooks
- Connections are opened on application startup and closed on shutdown
- No resource leaks from unclosed connections

## Core Features

### View Management
- **Home**: See config path, DuckDB database, counts (views/attachments/semantic models), and last build status. Trigger a build.
- **Views**: Browse views with source type and location/attachment info; search by name.
- **View detail**: Inspect the view definition (SQL or source fields) and any semantic-layer dimensions/measures.
- **Catalog Rebuild**: Rebuild catalog with updated configuration.

### Query Execution
- **Query**: Run ad-hoc SQL against the catalog with row-limit enforcement and clear error display.
- **Streaming Results**: Query results stream progressively as rows are fetched, keeping the UI responsive even for large result sets. Rows appear in batches (~50 rows per batch) rather than waiting for the entire query to complete.
- **Row Limit Enforcement**: Results are automatically limited to the configured row limit (default: 500 rows). If results are truncated, a notice displays the limit.
- **Error Handling**: Errors display clearly without exposing internal stack traces.
- **Data Export**: Export query results as CSV, Excel, or Parquet.
- **Schema Inspection**: View table and view schemas.

### Semantic Layer
- **Semantic Layer Explorer**: Browse semantic models with business-friendly labels.
- **Model Details**: View dimensions and measures with expressions and descriptions.

## Security Features

### Built-in Security
- **Read-Only SQL Enforcement**: Only allows SELECT queries, blocks DDL/DML
- **CORS Protection**: Restricted to localhost origins by default
- **Background Task Processing**: Non-blocking database operations
- **Configuration Security**: Atomic, format-preserving config updates

### Production Security
- **Authentication**: Admin token protection for mutating operations (production mode)
- **Secure Defaults**: Localhost-only binding by default
- **No External Dependencies**: All assets served locally, no CDN security risks

## Technical Implementation

### Reactive Architecture
- **Datastar Framework**: Real-time UI updates using Server-Sent Events
- **Background Processing**: All database operations run in background threads via `asyncio.to_thread()`
- **Non-blocking Event Loop**: Database queries never block the async event loop
- **Format Preservation**: Maintains YAML/JSON formatting when updating configs
- **Error Handling**: Comprehensive security-focused error messages

### Concurrency and Performance
- **Threadpool Execution**: DuckDB operations execute in a threadpool to prevent event loop blocking
- **Concurrent Queries**: Multiple queries can execute concurrently without interference
- **Graceful Shutdown**: Application properly closes all database connections on shutdown
- **Resource Management**: Connection lifecycle is fully managed via Litestar lifespan hooks

### Configuration Management
- **Atomic Operations**: Config updates use atomic file operations
- **In-Memory Updates**: Configuration changes take effect immediately
- **Format Detection**: Automatic YAML/JSON format detection and preservation

## Scope and Limitations

### Current Scope
- Single-user, local-first design
- No external assets or CDNs; everything served from duckalog installation
- Focused on tables and text—charts/advanced visuals are out of scope
- Local configuration files only (remote configs not yet supported)

### Security Considerations
- Admin token required for production deployments
- CLI credentials visible in process list (use environment variables for production)
- Designed for trusted environments; not a multi-tenant SaaS platform
