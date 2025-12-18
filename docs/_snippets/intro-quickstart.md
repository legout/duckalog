# Duckalog

Duckalog is a Python library and CLI for building DuckDB catalogs from
declarative YAML/JSON configuration files. A single config file describes your
DuckDB database, attachments (other DuckDB files, SQLite, Postgres), Iceberg
catalogs, and views over Parquet/Delta/Iceberg or attached tables.

The goal is to make DuckDB catalogs reproducible, versionable, and easy to
apply in local workflows and automated pipelines.

## Quickstart

### 1. Create a minimal config

Create a file `catalog.yaml`:

```yaml
version: 1

duckdb:
  database: catalog.duckdb
  pragmas:
    - "SET memory_limit='1GB'"

views:
  - name: users
    source: parquet
    uri: "s3://my-bucket/data/users/*.parquet"
```

### 2. Build and query with new workflow

```bash
# NEW: Single command to build and query
duckalog run catalog.yaml --query "SELECT COUNT(*) FROM users"

# Interactive exploration
duckalog run catalog.yaml --interactive
# In shell: SELECT * FROM users LIMIT 5; SHOW TABLES; exit

# Quick data samples
duckalog run catalog.yaml --query "SELECT * FROM users LIMIT 5"
duckalog run catalog.yaml --query "SELECT name, email FROM users WHERE active = true"

# OLD: Two-step workflow (still works)
duckalog build catalog.yaml
duckalog query "SELECT COUNT(*) FROM users"
duckalog query "SELECT * FROM users LIMIT 5"
```

### 3. Python API Usage

The enhanced Python API provides organized SQL functionality:

```python
# Direct imports (backward compatible)
from duckalog import generate_view_sql, quote_ident, ViewConfig

# Enhanced organization with convenience groups
from duckalog import sql, utils

# Generate SQL with organized imports
view_config = ViewConfig(name="users", source="parquet", uri="s3://bucket/data/users/*.parquet")
view_sql = sql.generate_view_sql(view_config)

# Safe SQL construction
safe_table_name = utils.quote_ident("users table")
safe_path = utils.quote_literal("s3://bucket/data/users.parquet")

# Unified namespace access
from duckalog import SQL
catalog_sql = SQL.generate.generate_all_views_sql(config)
```

For comprehensive documentation, tutorials, and examples, visit the **[Duckalog Documentation](https://legout.github.io/duckalog/)**.

## Features

- **Config-driven catalogs** – Define DuckDB views in YAML/JSON instead of scattering `CREATE VIEW` statements across scripts.
- **NEW: Intelligent connection management** – Single `duckalog run` command with session state restoration and incremental builds.
- **Multiple sources** – Views over S3 Parquet, Delta Lake, Iceberg tables, and attached DuckDB/SQLite/Postgres databases.
- **Attachments & catalogs** – Configure attachments and Iceberg catalogs in same config and reuse them across views.
- **Semantic layer** – Define business-friendly dimensions and measures on top of existing views for BI and analytics.
- **Safe credentials** – Use environment variables (e.g. `${env:AWS_ACCESS_KEY_ID}`) instead of embedding secrets.
- **CLI + Python API** – Build catalogs from command line or from Python code with same semantics.
- **Web UI** – Interactive dashboard for catalog management, query execution, and data export (requires `duckalog[ui]`).

## Installation

```bash
pip install duckalog
```

For the web UI dashboard:

```bash
pip install duckalog[ui]
```