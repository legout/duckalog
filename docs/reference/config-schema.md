# Configuration Schema Reference

Complete reference for Duckalog configuration schema, including all options, types, defaults, and examples.

## Overview

Duckalog configurations use YAML or JSON format with a hierarchical structure. All configurations must specify a version and include required sections for DuckDB database and views.

## Root Configuration

### Config

The top-level configuration object.

#### Fields

| Field | Type | Required | Default | Description |
|--------|------|-----------|---------|-------------|
| `version` | integer | ✅ | - | Configuration schema version (must be positive integer) |
| `duckdb` | DuckDBConfig | ✅ | - | DuckDB database configuration |
| `views` | array[ViewConfig] | ✅ | - | List of view definitions |
| `attachments` | AttachmentsConfig | ❌ | `{}` | Database attachment configurations |
| `iceberg_catalogs` | array[IcebergCatalogConfig] | ❌ | `[]` | Iceberg catalog configurations |
| `semantic_models` | array[SemanticModelConfig] | ❌ | `[]` | Semantic model definitions |
| `imports` | ImportConfig | ❌ | `[]` | Configuration imports |

#### Example

```yaml
version: 1
duckdb:
  database: analytics.duckdb
  pragmas:
    - "SET memory_limit='2GB'"
views:
  - name: users
    source: parquet
    uri: "data/users.parquet"
```

## DuckDB Configuration

### DuckDBConfig

Configuration for DuckDB database connection and behavior.

#### Fields

| Field | Type | Required | Default | Description |
|--------|------|-----------|---------|-------------|
| `database` | string | ✅ | - | Path to DuckDB database file |
| `install_extensions` | array[string] | ❌ | `[]` | Extensions to install before creating views |
| `load_extensions` | array[string] | ❌ | `[]` | Extensions to load after connecting |
| `pragmas` | array[string] | ❌ | `[]` | DuckDB pragmas to set |
| `settings` | SettingsConfig | ❌ | - | Session-level settings (legacy) |

#### Examples

```yaml
# Basic configuration
duckdb:
  database: catalog.duckdb

# With extensions
duckdb:
  database: catalog.duckdb
  install_extensions:
    - httpfs
    - json
    - parquet

# With pragmas
duckdb:
  database: catalog.duckdb
  pragmas:
    - "SET memory_limit='4GB'"
    - "SET threads=4"
    - "SET enable_progress_bar=false"

# With settings (legacy format)
duckdb:
  database: catalog.duckdb
  settings:
    memory_limit: "4GB"
    threads: 4
    enable_progress_bar: false
```

## Views Configuration

### ViewConfig

Definition of a database view in Duckalog.

#### Fields

| Field | Type | Required | Default | Description |
|--------|------|-----------|---------|-------------|
| `name` | string | ✅ | - | View name (must be unique within schema) |
| `db_schema` | string | ❌ | `main` | Database schema for view |
| `description` | string | ❌ | - | Human-readable description of view |
| `source` | string | ✅ | - | Data source type (see Source Types) |
| `uri` | string | ✅ | - | Source URI or file path |
| `sql` | string | ❌ | - | SQL statement for view |
| `sql_file` | SQLFileConfig | ❌ | - | External SQL file configuration |
| `materialized` | boolean | ❌ | `false` | Whether to materialize view as table |
| `tags` | array[string] | ❌ | `[]` | Tags for categorization |

#### Source Types

| Type | Description | URI Examples |
|------|-------------|-------------|
| `parquet` | Apache Parquet files | `data/file.parquet`, `s3://bucket/data/*.parquet` |
| `delta` | Delta Lake tables | `s3://bucket/delta-table/`, `data/delta-table/` |
| `iceberg` | Apache Iceberg tables | `s3://bucket/iceberg-table/`, `gs://bucket/table/` |
| `duckdb` | DuckDB database files | `./reference.duckdb`, `s3://bucket/catalog.duckdb` |
| `sqlite` | SQLite database files | `./legacy.db`, `/absolute/path/data.db` |
| `postgres` | PostgreSQL databases | See PostgreSQL configuration below |

#### Examples

```yaml
# Parquet source
views:
  - name: users
    source: parquet
    uri: "data/users.parquet"
    description: "User data from Parquet files"

# Delta Lake source
views:
  - name: orders
    source: delta
    uri: "s3://analytics-bucket/orders/"
    description: "Order data from Delta Lake"

# SQL view
views:
  - name: active_users
    sql: |
      SELECT * FROM users 
      WHERE status = 'active'
    description: "Active users only"

# External SQL file
views:
  - name: complex_analytics
    sql_file:
      path: "./analytics/complex_query.sql"
      variables:
        start_date: "2023-01-01"
        min_amount: 100
    description: "Complex analytics from external SQL"

# Materialized view
views:
  - name: user_metrics
    source: duckdb
    database: analytics
    table: user_metrics
    materialized: true
    sql: |
      SELECT * FROM user_metrics
    description: "Materialized user metrics table"
```

## SQL File Configuration

### SQLFileConfig

Configuration for loading SQL from external files with optional template processing.

#### Fields

| Field | Type | Required | Default | Description |
|--------|------|-----------|---------|-------------|
| `path` | string | ✅ | - | Path to SQL file (relative or absolute) |
| `variables` | object | ❌ | `{}` | Template variables for substitution |
| `as_template` | boolean | ❌ | `false` | Whether to process file as template |

#### Template Processing

When `as_template: true`, the SQL file can contain template variables using `{variable}` syntax:

```sql
-- analytics_query.sql
SELECT 
    event_type,
    COUNT(*) as event_count,
    AVG(event_value) as avg_value
FROM events 
WHERE event_date >= '{start_date}'
  AND event_type = '{event_type}'
GROUP BY event_type
```

```yaml
# With template variables
views:
  - name: event_analytics
    sql_file:
      path: "./analytics/analytics_query.sql"
      variables:
        start_date: "2023-01-01"
        event_type: "purchase"
      as_template: true
```

## Attachments Configuration

### AttachmentsConfig

Container for different types of database attachments.

#### Fields

| Field | Type | Required | Default | Description |
|--------|------|-----------|---------|-------------|
| `duckdb` | array[DuckDBAttachment] | ❌ | `[]` | DuckDB database attachments |
| `sqlite` | array[SQLiteAttachment] | ❌ | `[]` | SQLite database attachments |
| `postgres` | array[PostgresAttachment] | ❌ | `[]` | PostgreSQL database attachments |

### DuckDBAttachment

Attach another DuckDB database file.

#### Fields

| Field | Type | Required | Default | Description |
|--------|------|-----------|---------|-------------|
| `alias` | string | ✅ | - | Alias for attached database |
| `path` | string | ✅ | - | Path to DuckDB database file |
| `read_only` | boolean | ❌ | `true` | Whether attachment is read-only |

#### Example

```yaml
attachments:
  duckdb:
    - alias: reference_data
      path: "./reference.duckdb"
      read_only: true
    - alias: analytics_archive
      path: "/archive/analytics_2023.duckdb"
      read_only: true
```

### SQLiteAttachment

Attach a SQLite database file.

#### Fields

| Field | Type | Required | Default | Description |
|--------|------|-----------|---------|-------------|
| `alias` | string | ✅ | - | Alias for attached database |
| `path` | string | ✅ | - | Path to SQLite database file |
| `read_only` | boolean | ❌ | `true` | Whether attachment is read-only |

#### Example

```yaml
attachments:
  sqlite:
    - alias: legacy_system
      path: "./legacy_data.db"
      read_only: true
```

### PostgresAttachment

Attach a PostgreSQL database.

#### Fields

| Field | Type | Required | Default | Description |
|--------|------|-----------|---------|-------------|
| `alias` | string | ✅ | - | Alias for attached database |
| `host` | string | ✅ | - | PostgreSQL server hostname |
| `port` | integer | ❌ | `5432` | PostgreSQL server port |
| `database` | string | ✅ | - | PostgreSQL database name |
| `user` | string | ✅ | - | PostgreSQL username |
| `password` | string | ✅ | - | PostgreSQL password |
| `sslmode` | string | ❌ | `prefer` | SSL connection mode |
| `schema` | string | ❌ | `public` | Database schema |

#### Example

```yaml
attachments:
  postgres:
    - alias: data_warehouse
      host: "warehouse.company.com"
      port: 5432
      database: "analytics"
      user: "readonly_user"
      password: "${env:PG_PASSWORD}"
      sslmode: "require"
      schema: "public"
```

## Iceberg Catalogs Configuration

### IcebergCatalogConfig

Configuration for Apache Iceberg catalog integration.

#### Fields

| Field | Type | Required | Default | Description |
|--------|------|-----------|---------|-------------|
| `name` | string | ✅ | - | Catalog name (must be unique) |
| `catalog_type` | string | ✅ | - | Catalog type (rest, jdbc, glue) |
| `uri` | string | ✅ | - | Catalog URI |
| `warehouse` | string | ❌ | - | Warehouse location |
| `options` | object | ❌ | `{}` | Additional catalog options |

#### Catalog Types

| Type | Description | Example URI |
|------|-------------|-------------|
| `rest` | REST catalog | `https://iceberg-catalog.company.com/` |
| `jdbc` | JDBC catalog | `jdbc:postgresql://host:5432/db` |
| `glue` | AWS Glue catalog | `glue://account-id:region` |

#### Example

```yaml
iceberg_catalogs:
  - name: production_iceberg
    catalog_type: rest
    uri: "https://iceberg-catalog.company.com/"
    warehouse: "s3://production-data-lake/"
    options:
      token: "${env:ICEBERG_TOKEN}"
```

## Semantic Models Configuration

### SemanticModelConfig

Business-friendly metadata layer for analytics and BI tools.

#### Fields

| Field | Type | Required | Default | Description |
|--------|------|-----------|---------|-------------|
| `name` | string | ✅ | - | Model name (must be unique) |
| `base_view` | string | ✅ | - | Base view name for model |
| `label` | string | ❌ | - | Display label for model |
| `description` | string | ❌ | - | Model description |
| `tags` | array[string] | ❌ | `[]` | Categorization tags |
| `dimensions` | array[SemanticDimensionConfig] | ❌ | `[]` | Dimension definitions |
| `measures` | array[SemanticMeasureConfig] | ❌ | `[]` | Measure definitions |
| `joins` | array[SemanticJoinConfig] | ❌ | `[]` | Join configurations (v2+) |
| `defaults` | SemanticDefaultsConfig | ❌ | - | Default configuration (v2+) |

### SemanticDimensionConfig

Dimension definition for semantic models.

#### Fields

| Field | Type | Required | Default | Description |
|--------|------|-----------|---------|-------------|
| `name` | string | ✅ | - | Dimension name |
| `expression` | string | ✅ | - | SQL expression for dimension |
| `label` | string | ❌ | - | Display label |
| `description` | string | ❌ | - | Dimension description |
| `type` | string | ❌ | - | Data type (string, number, date, etc.) |
| `time_grains` | array[string] | ❌ | `[]` | Time grains for date dimensions |

#### Example

```yaml
semantic_models:
  - name: sales_analytics
    base_view: sales_data
    dimensions:
      - name: order_date
        expression: "created_at::date"
        label: "Order Date"
        type: "date"
        time_grains: ["year", "quarter", "month", "day"]
      - name: customer_region
        expression: "UPPER(region)"
        label: "Customer Region"
        type: "string"
```

### SemanticMeasureConfig

Measure definition for semantic models.

#### Fields

| Field | Type | Required | Default | Description |
|--------|------|-----------|---------|-------------|
| `name` | string | ✅ | - | Measure name |
| `expression` | string | ✅ | - | SQL expression for measure |
| `label` | string | ❌ | - | Display label |
| `description` | string | ❌ | - | Measure description |
| `type` | string | ❌ | - | Data type (number, currency, etc.) |
| `aggregation` | string | ❌ | - | Aggregation type (sum, avg, count, etc.) |

#### Example

```yaml
semantic_models:
  - name: sales_analytics
    base_view: sales_data
    measures:
      - name: total_revenue
        expression: "SUM(amount)"
        label: "Total Revenue"
        type: "currency"
        aggregation: "sum"
      - name: average_order_value
        expression: "AVG(amount)"
        label: "Average Order Value"
        type: "number"
        aggregation: "avg"
```

### SemanticJoinConfig

Join configuration for semantic models (v2+).

#### Fields

| Field | Type | Required | Default | Description |
|--------|------|-----------|---------|-------------|
| `to_view` | string | ✅ | - | Target view to join |
| `type` | string | ❌ | `left` | Join type (left, right, inner, full) |
| `on_condition` | string | ✅ | - | Join condition SQL expression |

#### Example

```yaml
semantic_models:
  - name: customer_analytics
    base_view: customers
    joins:
      - to_view: orders
        type: left
        on_condition: "customers.id = orders.customer_id"
      - to_view: products
        type: left
        on_condition: "orders.product_id = products.id"
```

### SemanticDefaultsConfig

Default configuration for semantic models (v2+).

#### Fields

| Field | Type | Required | Default | Description |
|--------|------|-----------|---------|-------------|
| `time_dimension` | string | ❌ | - | Default time dimension name |
| `primary_measure` | string | ❌ | - | Default primary measure name |
| `default_filters` | array[SemanticFilterConfig] | ❌ | `[]` | Default filters |

#### Example

```yaml
semantic_models:
  - name: sales_analytics
    base_view: sales_data
    defaults:
      time_dimension: order_date
      primary_measure: total_revenue
      default_filters:
        - dimension: order_date
          operator: ">="
          value: "2023-01-01"
```

## Import Configuration

### ImportConfig

Configuration for importing other configuration files.

#### Types

```yaml
# Simple list of paths
imports:
  - ./base.yaml
  - ./views.yaml
  - ./analytics.yaml

# Selective imports (advanced)
imports:
  duckdb:
    - path: ./database.yaml
      override: true
  views:
    - path: ./core_views.yaml
      override: true
    - path: ./analytics_views.yaml
      override: false
```

### ImportEntry

Individual import entry with optional override control.

#### Fields

| Field | Type | Required | Default | Description |
|--------|------|-----------|---------|-------------|
| `path` | string | ✅ | - | Path to configuration file |
| `override` | boolean | ❌ | `true` | Whether this import can override existing values |

### SelectiveImports

Section-specific imports for targeted configuration merging.

#### Fields

| Field | Type | Required | Default | Description |
|--------|------|-----------|---------|-------------|
| `duckdb` | array[ImportEntry] | ❌ | `[]` | DuckDB configuration imports |
| `views` | array[ImportEntry] | ❌ | `[]` | View definition imports |
| `attachments` | array[ImportEntry] | ❌ | `[]` | Attachment configuration imports |
| `iceberg_catalogs` | array[ImportEntry] | ❌ | `[]` | Iceberg catalog imports |
| `semantic_models` | array[ImportEntry] | ❌ | `[]` | Semantic model imports |

## Environment Variable Interpolation

### Syntax

Use `${env:VARIABLE_NAME}` syntax for environment variable substitution.

#### Examples

```yaml
# Basic substitution
duckdb:
  database: "${env:DB_PATH}"

# With default values
views:
  - name: users
    uri: "${env:DATA_PATH}/users.parquet"
    sql: |
      SELECT * FROM users 
      WHERE created_at >= '${env:START_DATE}'
```

### Supported Variables

Any environment variable can be used. Common patterns:

```bash
# Database credentials
export DB_HOST=localhost
export DB_USER=analytics_user
export DB_PASSWORD=${env:DB_PASSWORD}

# Cloud storage
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
export AWS_DEFAULT_REGION=us-west-2

# File paths
export DATA_DIR=/data/analytics
export CONFIG_DIR=/etc/duckalog
```

## Validation Rules

### Required Fields

All configurations must include:
- ✅ `version`: Positive integer
- ✅ `duckdb`: Database configuration
- ✅ `views`: Array of views (can be empty)

### Uniqueness Constraints

- View names must be unique within each schema
- Attachment aliases must be unique
- Iceberg catalog names must be unique
- Semantic model names must be unique

### Type Validation

- All string fields support environment variable interpolation
- File paths are resolved relative to configuration file
- Remote URIs are validated for supported schemes
- SQL expressions are validated for basic syntax

## Common Patterns

### Multi-Environment Configuration

```yaml
# Base configuration
version: 1
duckdb:
  database: "${env:ENVIRONMENT}_analytics.duckdb"

# Environment-specific imports
imports:
  - "./base-${env:ENVIRONMENT}.yaml"
```

### Team Collaboration Structure

```yaml
# Shared base configuration
version: 1
imports:
  - ./infrastructure/database.yaml    # Team: Infrastructure
  - ./data/views/users.yaml           # Team: Data
  - ./analytics/models.yaml           # Team: Analytics
  - ./business/reports.yaml           # Team: Business
```

### Production Deployment

```yaml
version: 1
duckdb:
  database: /data/prod/analytics.duckdb
  pragmas:
    - "SET memory_limit='8GB'"
    - "SET threads=8"
    - "SET enable_progress_bar=false"

# Secure credential management
attachments:
  postgres:
    - alias: warehouse
      host: "${env:PG_HOST}"
      user: "${env:PG_USER}"
      password: "${env:PG_PASSWORD}"
```

This comprehensive schema reference covers all Duckalog configuration options for building sophisticated data catalogs.