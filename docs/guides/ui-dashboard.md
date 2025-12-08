# Duckalog Dashboard

The dashboard is a lightweight, reactive web UI for exploring and managing Duckalog catalogs. It is built entirely in Python using **Starlette** and **Datastar** infrastructure—no frontend build tools or external CDNs are required.

## Installation Requirements

The dashboard requires the `duckalog[ui]` installation:

```bash
pip install duckalog[ui]
```

This includes:
- **Starlette** (`starlette>=0.27.0`): ASGI web framework
- **Uvicorn** (`uvicorn[standard]>=0.24.0`): ASGI server
- **Datastar JavaScript Bundle**: Vendored reactive framework (served locally)
- **Security middleware**: CORS protection and security headers

## Launch from Python (recommended)

```python
from duckalog.ui import UIServer

# Create and run the UI server
server = UIServer(
    config_path="catalog.yaml",
    host="127.0.0.1",
    port=8787,
    row_limit=1000
)
server.run()
```

Or use the existing convenience function:

```python
from duckalog.dashboard import run_dashboard

run_dashboard("catalog.yaml", host="127.0.0.1", port=8787, row_limit=500)
```

## Launch from the CLI

```bash
duckalog ui catalog.yaml --host 127.0.0.1 --port 8787 --row-limit 1000
```

- Binds to loopback by default; only expose other hosts if you understand the risk.
- `--row-limit` caps ad-hoc query results (defaults to 1000 rows).
- The CLI prints the dashboard URL and security warnings after startup.

## Production Deployment

For production use, enable security features:

```bash
# Set admin token for mutating operations
export DUCKALOG_ADMIN_TOKEN="your-secure-random-token"
duckalog ui catalog.yaml --host 0.0.0.0 --port 8000
```

## Core Features

### View Management
- **Home**: See config path, DuckDB database, counts (views/attachments/semantic models), and last build status. Trigger a build.
- **Views**: Browse views with source type and location/attachment info; search by name.
- **View detail**: Inspect the view definition (SQL or source fields) and any semantic-layer dimensions/measures.
- **Catalog Rebuild**: Rebuild catalog with updated configuration.

### Query Execution
- **Query**: Run ad-hoc SQL against the catalog with row-limit enforcement and clear error display.
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
- **Datastar Framework**: Vendored JavaScript bundle served locally for reactive UI updates
- **Server-Sent Events**: Real-time updates via `/sse/events` endpoint
- **Signal Management**: Server-side signals for catalog summary, views, query state, and build status
- **Background Processing**: Async task management for non-blocking operations
- **Error Handling**: Comprehensive security-focused error messages

### Security Implementation
- **SQL Security**: Comprehensive read-only SQL enforcement blocking DDL/DML operations
- **CORS Protection**: Localhost-only access with configurable host binding
- **Security Headers**: Complete CSP, XSS, and clickjacking protection
- **Input Validation**: Comprehensive SQL sanitization and validation

### API Architecture
- **RESTful Endpoints**: `/api/summary`, `/api/views`, `/api/query` for data access
- **JSON Responses**: Structured data for reactive UI updates
- **Error Standardization**: Consistent error format across all endpoints
- **Rate Limiting**: Built-in row limiting for query protection

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
