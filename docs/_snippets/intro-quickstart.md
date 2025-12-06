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

### 2. Build the catalog

```bash
duckalog build catalog.yaml
```

### 3. Query your catalog

```bash
# Quick count of users
duckalog query "SELECT COUNT(*) FROM users"

# View sample data
duckalog query "SELECT * FROM users LIMIT 5"

# Use explicit catalog path
duckalog query "SELECT * FROM users LIMIT 5" --catalog catalog.duckdb
duckalog query "SELECT * FROM users LIMIT 5" -c analytics.duckdb

# Query with specific conditions
duckalog query "SELECT name, email FROM users WHERE active = true" --catalog analytics.duckdb
```

For comprehensive documentation, tutorials, and examples, visit the **[Duckalog Documentation](https://legout.github.io/duckalog/)**.

## Features

- **Config-driven catalogs** – Define DuckDB views in YAML/JSON instead of scattering `CREATE VIEW` statements across scripts.
- **Multiple sources** – Views over S3 Parquet, Delta Lake, Iceberg tables, and attached DuckDB/SQLite/Postgres databases.
- **Attachments & catalogs** – Configure attachments and Iceberg catalogs in same config and reuse them across views.
- **Semantic layer** – Define business-friendly dimensions and measures on top of existing views for BI and analytics.
- **Safe credentials** – Use environment variables (e.g. `${env:AWS_ACCESS_KEY_ID}`) instead of embedding secrets.
- **CLI + Python API** – Build catalogs from command line or from Python code with the same semantics.
- **Web UI** – Interactive dashboard for catalog management, query execution, and data export (requires `duckalog[ui]`).

## Installation

```bash
pip install duckalog
```

For the web UI dashboard:

```bash
pip install duckalog[ui]
```