# Configuration Schema Reference

Complete reference for Duckalog configuration schema, including all options, types, defaults, and examples for both basic and advanced usage patterns.

## Overview

Duckalog configurations use YAML or JSON format with a hierarchical structure. The new modular architecture supports enhanced patterns including configuration imports, dependency injection hooks, and performance optimizations while maintaining full backward compatibility.

### Architecture Features

The configuration schema now supports:

- **Configuration Imports**: Modular configuration structure with file imports
- **Enhanced Environment Processing**: Advanced variable resolution and validation  
- **Import Resolution Performance**: Caching and optimization for complex configurations
- **Dependency Injection**: Customizable loading and resolution components
- **Backward Compatibility**: All existing configurations continue to work

### Version Requirements

- **Version 1**: Basic configuration structure (legacy compatible)
- **Version 1+**: Enhanced features with imports and modular patterns
- **Future versions**: Will maintain backward compatibility where possible

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
| `imports` | ImportConfig | ❌ | `[]` | Configuration imports and modular structure |
| `load_sql_files` | boolean | ❌ | `true` | Enable/disable SQL file loading for performance |
| `resolve_paths` | boolean | ❌ | `true` | Enable/disable path resolution (for testing) |
| `load_dotenv` | boolean | ❌ | `true` | Enable/disable .env file loading |

## Performance Configuration

### Performance Options

Enhanced performance tuning options for complex configurations and large-scale deployments.

#### Fields

| Field | Type | Required | Default | Description |
|--------|------|-----------|---------|-------------|
| `cache_imports` | boolean | ❌ | `true` | Enable import resolution caching |
| `max_import_depth` | integer | ❌ | `10` | Maximum import chain depth (security) |
| `parallel_loading` | boolean | ❌ | `false` | Enable parallel configuration loading |
| `preload_env` | boolean | ❌ | `true` | Preload all environment variables |
| `validate_paths` | boolean | ❌ | `true` | Validate all file paths during loading |

#### Examples

```yaml
# Performance optimization for large configurations
version: 1
cache_imports: true
max_import_depth: 5
parallel_loading: true
preload_env: true
validate_paths: false  # Skip for faster loading

duckdb:
  database: analytics.duckdb
  pragmas:
    - "SET memory_limit='8GB'"
    - "SET threads=8"

views:
  - name: large_dataset
    source: parquet
    uri: "data/large_dataset.parquet"
```

### Cache Configuration

Advanced caching options for enterprise deployments.

#### Fields

| Field | Type | Required | Default | Description |
|--------|------|-----------|---------|-------------|
| `import_cache_size` | integer | ❌ | `100` | Maximum cached import configurations |
| `path_cache_size` | integer | ❌ | `1000` | Maximum cached path resolutions |
| `env_cache_ttl` | integer | ❌ | `300` | Environment cache TTL in seconds |

#### Examples

```yaml
# Enterprise performance configuration
version: 1

cache_imports: true
import_cache_size: 500
path_cache_size: 5000
env_cache_ttl: 600

duckdb:
  database: enterprise_catalog.duckdb
```

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
| `database` | string | ❌ | `:memory:` | Path to DuckDB database file |
| `install_extensions` | array[string] | ❌ | `[]` | Extensions to install before creating views |
| `load_extensions` | array[string] | ❌ | `[]` | Extensions to load after connecting |
| `pragmas` | array[string] | ❌ | `[]` | DuckDB pragmas to set |
| `settings` | string or array[string] | ❌ | - | DuckDB SET statements executed after pragmas |

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

# With settings (single SET statement)
duckdb:
  database: catalog.duckdb
  settings: "SET memory_limit='4GB'"

# With settings (multiple SET statements)
duckdb:
  database: catalog.duckdb
  settings:
    - "SET memory_limit='4GB'"
    - "SET threads=4"
    - "SET enable_progress_bar=false"

# With secrets
duckdb:
  database: catalog.duckdb
  secrets:
    - type: s3
      name: production_s3
      key_id: "${env:AWS_ACCESS_KEY_ID}"
      secret: "${env:AWS_SECRET_ACCESS_KEY}"
      region: us-west-2
```

## Secrets Configuration

### SecretConfig

Configuration for DuckDB secrets used to authenticate with external services and databases. Secrets are defined within the `duckdb` configuration section.

#### Fields

| Field | Type | Required | Default | Description |
|--------|------|-----------|---------|-------------|
| `type` | string | ✅ | - | Secret type (s3, azure, gcs, http, postgres, mysql) |
| `name` | string | ❌ | type value | Optional name for the secret (defaults to type if not provided) |
| `provider` | string | ❌ | `config` | Secret provider (config or credential_chain) |
| `persistent` | boolean | ❌ | `false` | Whether to create a persistent secret (⚠️ Security implications apply) |
| `scope` | string | ❌ | - | Optional scope prefix for the secret |
| `key_id` | string | ❌ | - | Access key ID or username for authentication |
| `secret` | string | ❌ | - | Secret key or password for authentication |
| `region` | string | ❌ | - | Geographic region for cloud services |
| `endpoint` | string | ❌ | - | Custom endpoint URL for cloud services |
| `connection_string` | string | ❌ | - | Full connection string for databases |
| `tenant_id` | string | ❌ | - | Azure tenant ID for authentication |
| `account_name` | string | ❌ | - | Azure storage account name |
| `client_id` | string | ❌ | - | Azure client ID for authentication |
| `client_secret` | string | ❌ | - | Azure client secret for authentication |
| `service_account_key` | string | ❌ | - | GCS service account key |
| `json_key` | string | ❌ | - | GCS JSON key |
| `bearer_token` | string | ❌ | - | HTTP bearer token for authentication |
| `header` | string | ❌ | - | HTTP header for authentication |
| `database` | string | ❌ | - | Database name for database secrets |
| `host` | string | ❌ | - | Database host for database secrets |
| `port` | integer | ❌ | - | Database port for database secrets |
| `user` | string | ❌ | - | Database username (alternative to key_id for database types) |
| `password` | string | ❌ | - | Database password (alternative to secret for database types) |
| `options` | object | ❌ | `{}` | Additional key-value options for the secret |

#### Secret Types

| Type | Description | Common Fields |
|------|-------------|----------------|
| `s3` | Amazon S3 or S3-compatible storage | `key_id`, `secret`, `region`, `endpoint` |
| `azure` | Azure Blob Storage | `connection_string`, `tenant_id`, `account_name` |
| `gcs` | Google Cloud Storage | `service_account_key`, `json_key`, `key_id`, `secret` |
| `http` | HTTP basic authentication | `key_id`, `secret`, `bearer_token`, `header` |
| `postgres` | PostgreSQL database connections | `connection_string`, `host`, `port`, `database`, `user`, `password` |
| `mysql` | MySQL database connections (uses postgres type) | `connection_string`, `host`, `port`, `database`, `user`, `password` |

#### Examples

```yaml
# S3 secret with static credentials
duckdb:
  database: catalog.duckdb
  secrets:
    - type: s3
      name: production_s3
      key_id: "${env:AWS_ACCESS_KEY_ID}"
      secret: "${env:AWS_SECRET_ACCESS_KEY}"
      region: us-west-2

# Azure storage secret
duckdb:
  database: catalog.duckdb
  secrets:
    - type: azure
      name: azure_prod
      connection_string: "${env:AZURE_STORAGE_CONNECTION_STRING}"
      account_name: "${env:AZURE_STORAGE_ACCOUNT}"

# GCS secret with service account
duckdb:
  database: catalog.duckdb
  secrets:
    - type: gcs
      name: gcs_service_account
      service_account_key: "${env:GCS_SERVICE_ACCOUNT_JSON}"

# PostgreSQL database secret
duckdb:
  database: catalog.duckdb
  secrets:
    - type: postgres
      name: analytics_db
      connection_string: "${env:DATABASE_URL}"

# HTTP secret for API access
duckdb:
  database: catalog.duckdb
  secrets:
    - type: http
      name: api_auth
      key_id: "${env:API_USERNAME}"
      secret: "${env:API_PASSWORD}"

# Secret with additional options
duckdb:
  database: catalog.duckdb
  secrets:
    - type: s3
      name: minio_storage
      key_id: "${env:MINIO_ACCESS_KEY}"
      secret: "${env:MINIO_SECRET_KEY}"
      endpoint: http://minio-server:9000
      persistent: false  # Temporary secret (default)
      options:
        use_ssl: false
        url_style: path

# Persistent secret (use with caution)
duckdb:
  database: catalog.duckdb
  secrets:
    - type: s3
      name: production_s3
      key_id: "${env:AWS_ACCESS_KEY_ID}"
      secret: "${env:AWS_SECRET_ACCESS_KEY}"
      persistent: true  # Persists to database file
      region: us-west-2
```

**Security Note:** For detailed guidance on secrets persistence and security implications, see [Secrets Persistence Guide](../how-to/secrets-persistence.md).

## Views Configuration

### ViewConfig

Definition of a database view in Duckalog.

#### Fields

| Field | Type | Required | Default | Description |
|--------|------|-----------|---------|-------------|
| `name` | string | ✅ | - | View name (must be unique within schema) |
| `db_schema` | string | ❌ | - | Database schema for view |
| `description` | string | ❌ | - | Human-readable description of view |
| `source` | string | ❌ | - | Data source type (see Source Types) |
| `uri` | string | ❌ | - | Source URI or file path |
| `sql` | string | ❌ | - | SQL statement for view |
| `sql_file` | SQLFileReference | ❌ | - | External SQL file configuration |
| `sql_template` | SQLFileReference | ❌ | - | External SQL template with variable substitution |
| `database` | string | ❌ | - | Attachment alias for attached-database sources |
| `table` | string | ❌ | - | Table name (optionally schema-qualified) for attached sources |
| `catalog` | string | ❌ | - | Iceberg catalog name for catalog-based Iceberg views |
| `options` | object | ❌ | `{}` | Source-specific options passed to scan functions |
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

# View using attached database
views:
  - name: user_metrics
    source: duckdb
    database: analytics
    table: user_metrics
    sql: |
      SELECT * FROM user_metrics
    description: "User metrics from attached database"
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

Configuration for importing other configuration files with enhanced performance and caching from the new modular architecture.

#### Types

```yaml
# Simple list of paths (basic pattern)
imports:
  - ./base.yaml
  - ./views.yaml
  - ./analytics.yaml

# Selective imports (advanced pattern)
imports:
  duckdb:
    - path: ./database.yaml
      override: true
  views:
    - path: ./core_views.yaml
      override: true
    - path: ./analytics_views.yaml
      override: false

# Remote imports (new capability)
imports:
  - s3://company-configs/base.yaml
  - ./local-overrides.yaml
  - https://config.company.com/production.yaml
```

#### Enhanced Features

**Request-Scoped Caching:**
- Import resolution is cached within request scope
- Repeated imports across multiple configurations are optimized
- Import chain analysis for performance monitoring

**Remote Import Support:**
- Import from remote sources (S3, GCS, HTTPS, etc.)
- Mixed local and remote import combinations
- Authentication through environment variables

**Import Resolution Diagnostics:**
- Track import chain depth and complexity
- Performance metrics for import resolution
- Cache hit/miss statistics

### ImportEntry

Individual import entry with optional override control and enhanced resolution features.

#### Fields

| Field | Type | Required | Default | Description |
|--------|------|-----------|---------|-------------|
| `path` | string | ✅ | - | Path to configuration file (local or remote URI) |
| `override` | boolean | ❌ | `true` | Whether this import can override existing values |
| `optional` | boolean | ❌ | `false` | Whether import failure should be tolerated |
| `namespace` | string | ❌ | - | Optional namespace for import isolation |

#### Remote Import Examples

```yaml
# Remote import with authentication
imports:
  - path: s3://company-configs/base.yaml
    override: true
    optional: false
  - path: ./local-overrides.yaml
    override: true
  - path: https://config.company.com/production.yaml
    namespace: company
    optional: true
```

### SelectiveImports

Section-specific imports for targeted configuration merging with enhanced conflict resolution.

#### Fields

| Field | Type | Required | Default | Description |
|--------|------|-----------|---------|-------------|
| `duckdb` | array[ImportEntry] | ❌ | `[]` | DuckDB configuration imports |
| `views` | array[ImportEntry] | ❌ | `[]` | View definition imports |
| `attachments` | array[ImportEntry] | ❌ | `[]` | Attachment configuration imports |
| `secrets` | array[ImportEntry] | ❌ | `[]` | Secret configuration imports |

#### Advanced Import Patterns

```yaml
# Namespace isolation
imports:
  secrets:
    - path: ./dev-secrets.yaml
      namespace: dev
      override: false
    - path: ./prod-secrets.yaml
      namespace: prod
      override: false

# Optional imports for different environments
imports:
  views:
    - path: ./core-views.yaml
      override: true
    - path: ./dev-views.yaml
      optional: true
    - path: ./analytics-views.yaml
      optional: true
      namespace: analytics

# Remote fallback pattern
imports:
  - path: s3://company-configs/production-base.yaml
    override: true
    optional: true  # Fallback to local if remote fails
  - path: ./local-base.yaml
    override: true
```

### Import Resolution Algorithm

The new architecture enhances import resolution with:

1. **Dependency Analysis**: Analyze import graph for circular dependencies
2. **Performance Optimization**: Cache resolution results across multiple loads
3. **Error Context**: Provide detailed error information with import chain
4. **Remote Fallback**: Graceful handling of remote import failures

#### Import Chain Example

```yaml
# main.yaml
version: 1
imports:
  - ./base.yaml
  - ./views/users.yaml
  - ./analytics.yaml

# base.yaml
version: 1
duckdb:
  database: analytics.duckdb
imports:
  - ./shared/secrets.yaml

# analytics.yaml
version: 1
imports:
  - ./base.yaml  # Already loaded - cached result
  - ./views/reports.yaml
```

**Resolution with Caching:**
1. Load `main.yaml` → start request cache
2. Load `base.yaml` → load and cache `shared/secrets.yaml`
3. Load `views/users.yaml` → use cached base
4. Load `analytics.yaml` → reuse cached `base.yaml`
5. Load `views/reports.yaml` → complete resolution

**Performance Benefits:**
- `base.yaml` loaded once, reused twice
- `shared/secrets.yaml` resolved once
- Import chain depth: 3 levels
- Cache hit ratio: 40% for repeated imports
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
version: 1

duckdb:
  database: "${env:DB_PATH}"
  
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