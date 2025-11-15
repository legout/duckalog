## Duckalog

Duckalog is a Python library and CLI for building DuckDB catalogs from
declarative YAML/JSON configuration files. A single config file describes your
DuckDB database, attachments (other DuckDB files, SQLite, Postgres), Iceberg
catalogs, and views over Parquet/Delta/Iceberg or attached tables.

The goal is to make DuckDB catalogs reproducible, versionable, and easy to
apply in local workflows and automated pipelines.

---

## Features

- **Config-driven catalogs** – Define DuckDB views in YAML/JSON instead of
  scattering `CREATE VIEW` statements across scripts.
- **Multiple sources** – Views over S3 Parquet, Delta Lake, Iceberg tables, and
  attached DuckDB/SQLite/Postgres databases.
- **Attachments & catalogs** – Configure attachments and Iceberg catalogs in
  the same config and reuse them across views.
- **Safe credentials** – Use environment variables (e.g. `${env:AWS_ACCESS_KEY_ID}`)
  instead of embedding secrets.
- **CLI + Python API** – Build catalogs from the command line or from Python
  code with the same semantics.

For a full product and technical description, see `docs/PRD_Spec.md`.

---

## Installation

Requirements:

- Python 3.9 or newer

Install from PyPI (package name is `duckalog`):

```bash
pip install duckalog
```

This installs the Python package and the `duckalog` CLI entrypoint.

---

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

### 2. Build the catalog via CLI

```bash
duckalog build catalog.yaml
```

This will:

- Read `catalog.yaml`.
- Connect to `catalog.duckdb` (creating it if necessary).
- Apply pragmas.
- Create or replace the `users` view.

### 3. Generate SQL instead of touching the DB

```bash
duckalog generate-sql catalog.yaml --output create_views.sql
```

`create_views.sql` will contain `CREATE OR REPLACE VIEW` statements for all
views defined in the config.

### 4. Validate a config

```bash
duckalog validate catalog.yaml
```

This parses and validates the config (including env interpolation), without
connecting to DuckDB.

---

## Python API

The `duckalog` package exposes the same functionality as the CLI with
convenience functions:

```python
from duckalog import build_catalog, generate_sql, validate_config


# Build or update a catalog file in place
build_catalog("catalog.yaml")


# Generate SQL without executing it
sql = generate_sql("catalog.yaml")
print(sql)


# Validate config (raises ConfigError on failure)
validate_config("catalog.yaml")
```

You can also work directly with the Pydantic model:

```python
from duckalog import load_config

config = load_config("catalog.yaml")
for view in config.views:
    print(view.name, view.source)
```

---

## Configuration Overview

At a high level, configs follow this structure:

```yaml
version: 1

duckdb:
  database: catalog.duckdb
  install_extensions: []
  load_extensions: []
  pragmas: []

attachments:
  duckdb:
    - alias: refdata
      path: ./refdata.duckdb
      read_only: true

  sqlite:
    - alias: legacy
      path: ./legacy.db

  postgres:
    - alias: dw
      host: "${env:PG_HOST}"
      port: 5432
      database: dw
      user: "${env:PG_USER}"
      password: "${env:PG_PASSWORD}"

iceberg_catalogs:
  - name: main_ic
    catalog_type: rest
    uri: "https://iceberg-catalog.internal"
    warehouse: "s3://my-warehouse/"
    options:
      token: "${env:ICEBERG_TOKEN}"

views:
  # Parquet view
  - name: users
    source: parquet
    uri: "s3://my-bucket/data/users/*.parquet"

  # Delta view
  - name: events_delta
    source: delta
    uri: "s3://my-bucket/delta/events"

  # Iceberg catalog-based view
  - name: ic_orders
    source: iceberg
    catalog: main_ic
    table: analytics.orders

  # Attached DuckDB view
  - name: ref_countries
    source: duckdb
    database: refdata
    table: reference.countries

  # Raw SQL view
  - name: vip_users
    sql: |
      SELECT *
      FROM users
      WHERE is_vip = TRUE
```

### Environment variable interpolation

Any string value may contain `${env:VAR_NAME}` placeholders. During
`load_config`, these are resolved using `os.environ["VAR_NAME"]`. Missing
variables cause a `ConfigError`.

Examples:

```yaml
duckdb:
  pragmas:
    - "SET s3_access_key_id='${env:AWS_ACCESS_KEY_ID}'"
    - "SET s3_secret_access_key='${env:AWS_SECRET_ACCESS_KEY}'"
```

---

## Development & Spec References

- Product & technical spec: `docs/PRD_Spec.md`.
- OpenSpec project and changes: files under `openspec/`.

The implementation in `src/duckalog` is driven by OpenSpec changes such as:

- `add-config-schema` – configuration schema and validation.
- `add-sql-generation` – SQL generation rules.
- `add-catalog-build-cli` – engine and CLI behavior.
- `add-error-and-logging` – error types and logging semantics.
- `add-python-api` – convenience Python functions.
- `add-testing-strategy` – expectations for tests.
- `add-readme-docs` and `add-api-docstrings` – documentation foundations.
- `add-mkdocs-site` – MkDocs site configuration.

To work with the documentation site locally (after installing the `dev`
dependencies):

```bash
uv pip install -r pyproject.toml#dev  # or install mkdocs deps via your tool

mkdocs serve   # live-reload docs at http://127.0.0.1:8000
mkdocs build   # build static site into the "site/" directory
```
