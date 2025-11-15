# User Guide

This guide explains how to structure Duckalog configuration files and how to
use attachments and Iceberg catalogs.

## Configuration structure

At a high level, a config looks like this:

```yaml
version: 1

duckdb:
  database: catalog.duckdb
  pragmas:
    - "SET memory_limit='1GB'"

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
  - name: users
    source: parquet
    uri: "s3://my-bucket/data/users/*.parquet"

  - name: events_delta
    source: delta
    uri: "s3://my-bucket/delta/events"

  - name: ic_orders
    source: iceberg
    catalog: main_ic
    table: analytics.orders

  - name: ref_countries
    source: duckdb
    database: refdata
    table: reference.countries

  - name: vip_users
    sql: |
      SELECT *
      FROM users
      WHERE is_vip = TRUE
```

## Environment variables

Any string may contain `${env:VAR_NAME}` placeholders. Duckalog resolves these
using the process environment before validation. If a variable is missing, a
`ConfigError` is raised.

Example:

```yaml
duckdb:
  pragmas:
    - "SET s3_access_key_id='${env:AWS_ACCESS_KEY_ID}'"
    - "SET s3_secret_access_key='${env:AWS_SECRET_ACCESS_KEY}'"
```

## Attachments

Attachments let you expose tables from other databases inside DuckDB.

- **DuckDB attachments**: attach additional `.duckdb` files.
- **SQLite attachments**: attach local SQLite databases.
- **Postgres attachments**: connect to external Postgres instances.

Views that use attached databases set `source` to `duckdb`, `sqlite`, or
`postgres` and provide `database` (attachment alias) and `table`.

## Iceberg catalogs

Iceberg catalogs are configured under `iceberg_catalogs`. Iceberg views can
either:

- Use a `uri` directly, or
- Refer to a `catalog` + `table` combination.

Duckalog validates that any `catalog` used by a view is defined in
`iceberg_catalogs`.

## Next steps

- Use ``duckalog generate-sql`` to inspect the SQL that will be executed.
- Use the API reference for details on each public function and model.

