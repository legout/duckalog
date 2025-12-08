# Duckalog Dashboard

The dashboard is a lightweight, reactive web UI for exploring and managing Duckalog catalogs. It is built entirely in Python using **Litestar** and **Datastar.js**—no frontend build tools or external CDNs are required.

## Architecture Overview

The dashboard uses a modern, secure architecture:

- **Litestar Framework**: Modern Python web framework with async support
- **Datastar.js Client-side**: Reactive UI framework for real-time updates
- **Server-Sent Events**: Real-time communication without websockets
- **Tailwind CSS**: Modern, responsive styling framework
- **Local-first**: All assets served locally, no external dependencies

## Installation Requirements

The dashboard requires the `duckalog[ui]` installation:

```bash
pip install duckalog[ui]
```

This includes:
- **Litestar** (`litestar>=2.0.0`): Modern ASGI web framework
- **Uvicorn** (`uvicorn[standard]>=0.24.0`): ASGI server
- **Python Multipart** (`python-multipart>=0.0.20`): Form data support

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

### Modern Architecture
- **Litestar Framework**: Modern async web framework with built-in dependency injection
- **Datastar.js Integration**: Client-side reactive framework for real-time updates
- **Server-Sent Events**: Efficient real-time communication without websockets
- **Component-Based Design**: Modular, reusable UI components
- **Tailwind CSS**: Utility-first styling with dark/light theme support

### Real-time Features
- **Query Streaming**: Live query results as they execute
- **Build Status Updates**: Real-time catalog build progress
- **Reactive UI**: Interface updates automatically without page refresh
- **Signal-Based State**: Clean state management using Datastar signals

### Security Implementation
- **Read-Only SQL Enforcement**: Blocks DDL/DML operations automatically
- **Row Limit Protection**: Prevents resource exhaustion from large queries
- **DuckDB Read-Only Mode**: Additional database-level protection
- **Input Validation**: Comprehensive SQL injection prevention

### Performance Optimization
- **Efficient Connections**: Connection management for concurrent requests
- **Static File Caching**: Optimized asset serving with browser caching
- **Progressive Enhancement**: Graceful degradation for low-bandwidth scenarios
- **Minimal Dependencies**: Lightweight footprint with no external CDNs

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
