# User Guide

This guide explains how to structure Duckalog configuration files, common configuration patterns, secret management, and how to troubleshoot issues.

## Secret Management

Duckalog provides comprehensive secret management through the canonical `SecretConfig` model, ensuring secure credential handling without storing sensitive data in configuration files.

### Environment Variable Integration

All sensitive configuration uses environment variables for security:

```yaml
# Basic environment variable usage
duckdb:
  database: catalog.duckdb
  pragmas:
    - "SET s3_access_key_id='${env:AWS_ACCESS_KEY_ID}'"
    - "SET s3_secret_access_key='${env:AWS_SECRET_ACCESS_KEY}'"
    - "SET azure_connection_string='${env:AZURE_CONNECTION_STRING}'"

attachments:
  postgres:
    - host: "${env:PG_HOST}"
      user: "${env:PG_USER}"
      password: "${env:PG_PASSWORD}"
```

### Canonical Secret Configuration

Define secrets once and reference them across multiple views:

```yaml
secrets:
  - name: s3_prod
    type: s3
    key_id: "${env:AWS_ACCESS_KEY_ID}"
    secret: "${env:AWS_SECRET_ACCESS_KEY}"
    region: "us-east-1"
    endpoint: "https://s3.amazonaws.com"

  - name: azure_storage
    type: azure
    connection_string: "${env:AZURE_STORAGE_CONNECTION_STRING}"
    account_name: "${env:AZURE_STORAGE_ACCOUNT}"

  - name: gcs_service
    type: gcs
    service_account_key: "${env:GCS_SERVICE_ACCOUNT_JSON}"

  - name: http_api
    type: http
    bearer_token: "${env:API_BEARER_TOKEN}"
    header: "Authorization"

views:
  - name: production_data
    source: parquet
    uri: "s3://prod-bucket/data/*.parquet"
    secrets_ref: s3_prod

  - name: azure_logs
    source: parquet
    uri: "abfs://logcontainer@storageaccount.dfs.core.windows.net/logs/*.parquet"
    secrets_ref: azure_storage

  - name: reference_tables
    source: iceberg
    catalog: main_catalog
    table: analytics.reference_data
    secrets_ref: gcs_service
```

### Secret Types and DuckDB Integration

Each secret type maps to appropriate DuckDB `CREATE SECRET` statements:

**S3 Secrets:**
```sql
CREATE SECRET s3_prod (
    TYPE S3,
    KEY_ID 'AKIA...',
    SECRET 'secret...',
    REGION 'us-east-1',
    ENDPOINT 'https://s3.amazonaws.com'
);
```

**Azure Secrets:**
```sql
CREATE SECRET azure_storage (
    TYPE AZURE,
    CONNECTION_STRING 'DefaultEndpointsProtocol=...'
);
```

**PostgreSQL Secrets:**
```sql
CREATE SECRET postgres_creds (
    TYPE POSTGRES,
    CONNECTION_STRING 'postgresql://user:pass@host:5432/db'
);
```

### Security Best Practices

1. **Never commit secrets**: Use `.env` files or environment variables
2. **Rotate credentials**: Regularly update access keys and tokens
3. **Use principle of least privilege**: Grant minimal required permissions
4. **Audit access**: Monitor which secrets are used where

**Related:** [Architecture - Secret Management](architecture.md#secret-management-architecture)

## Remote Configuration

Duckalog supports loading configurations from remote sources using a unified filesystem interface:

### Loading Remote Configurations

```bash
# S3 configuration
duckalog build s3://my-bucket/catalog.yaml \
    --fs-key "${AWS_ACCESS_KEY_ID}" \
    --fs-secret "${AWS_SECRET_ACCESS_KEY}" \
    --aws-profile my-profile

# GCS configuration
duckalog build gs://my-bucket/catalog.yaml \
    --gcs-credentials-file /path/to/service-account.json

# Azure Blob Storage
duckalog build abfs://account@container/catalog.yaml \
    --azure-connection-string "${AZURE_CONNECTION_STRING}"

# GitHub repository
duckalog build github://user/repo/catalog.yaml \
    --fs-token "${GITHUB_TOKEN}"

# SFTP server
duckalog build sftp://server/path/catalog.yaml \
    --sftp-host server.com \
    --sftp-key-file ~/.ssh/id_rsa

# HTTP/HTTPS
duckalog build https://example.com/catalog.yaml \
    --fs-token "${API_TOKEN}"
```

### Shared Filesystem Architecture

All remote access options are centralized through the CLI's shared filesystem handler:

- **Protocol Detection**: Automatic protocol inference from options
- **Credential Management**: Secure handling of authentication details
- **Context Management**: Filesystem objects shared across commands
- **Error Handling**: Descriptive error messages for connection issues

## Configuration structure

At a high level, a config looks like this:

```yaml
version: 1

duckdb:
  database: catalog.duckdb
  pragmas:
    - "SET memory_limit='1GB'"

# Secure credential management
secrets:
  - name: s3_access
    type: s3
    key_id: "${env:AWS_ACCESS_KEY_ID}"
    secret: "${env:AWS_SECRET_ACCESS_KEY}"
    region: "us-east-1"
  
  - name: postgres_creds
    type: postgres
    connection_string: "${env:POSTGRES_CONNECTION_STRING}"

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
    secrets_ref: s3_access

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
      AND segment = 'premium'
```

## Path Resolution

Duckalog automatically resolves relative file paths to absolute paths relative to the configuration file location. This ensures consistent behavior across different working directories while maintaining security.

### How Path Resolution Works

- **Automatic Detection**: Duckalog detects whether paths are relative or absolute
- **Relative Path Resolution**: Resolves paths like `data/file.parquet` against the config file's directory  
- **Security Validation**: Blocks dangerous directory traversal while allowing reasonable parent directory access
- **Cross-Platform Support**: Works correctly on Windows, macOS, and Linux

### Configuration

Path resolution is enabled by default when loading configurations:

```python
from duckalog import load_config

# Path resolution enabled (default)
config = load_config("catalog.yaml")

# Explicitly enable/disable resolution
config = load_config("catalog.yaml", resolve_paths=True)
config = load_config("catalog.yaml", resolve_paths=False)
```

### Path Resolution Examples

#### Basic Relative Paths

**Project Structure:**
```
analytics/
├── catalog.yaml
├── data/
│   ├── events.parquet
│   └── users.parquet
└── databases/
    └── reference.duckdb
```

**Configuration:**
```yaml
version: 1

duckdb:
  database: catalog.duckdb

attachments:
  duckdb:
    - alias: refdata
      path: ./databases/reference.duckdb  # Resolved to absolute path
      read_only: true

views:
  - name: events
    source: parquet
    uri: data/events.parquet  # Resolved relative to catalog.yaml
    
  - name: users  
    source: parquet
    uri: ./data/users.parquet  # Explicit relative path
```

#### Parent Directory Access

**Project Structure:**
```
company/
├── shared/
│   └── reference_data/
│       └── customers.parquet
└── analytics/
    └── catalog.yaml
    └── data/
        └── events.parquet
```

**Configuration (`company/analytics/catalog.yaml`):**
```yaml
version: 1

views:
  - name: events
    source: parquet
    uri: ./data/events.parquet           # Resolved to /company/analytics/data/events.parquet
    
  - name: customers
    source: parquet
    uri: ../shared/reference_data/customers.parquet  # Resolved to /company/shared/reference_data/customers.parquet
```

#### Mixed Path Types

```yaml
version: 1

views:
  # Relative path - resolved automatically
  - name: local_data
    source: parquet
    uri: ./data/local.parquet
    
  # Absolute path - unchanged
  - name: absolute_data
    source: parquet
    uri: /absolute/path/data.parquet
    
  # Remote URI - unchanged
  - name: remote_data
    source: parquet
    uri: s3://my-bucket/data/remote.parquet
```

### Security Features

Path resolution includes comprehensive security validation:

#### Allowed Patterns
```yaml
# ✅ ALLOWED - Same directory
uri: data/file.parquet

# ✅ ALLOWED - Parent directory access (reasonable levels)
uri: ../shared/data.parquet
uri: ../../project/common.parquet

# ✅ ALLOWED - Subdirectories
uri: ./subdir/nested/file.parquet
```

#### Blocked Patterns
```yaml
# ❌ BLOCKED - Excessive parent directory traversal
uri: ../../../../etc/passwd

# ❌ BLOCKED - System directory access
uri: ../etc/config.parquet
uri: ../../usr/local/data.parquet
```

### Troubleshooting Path Resolution

#### Common Issues

**Path resolution failed:**
```
PathResolutionError: Path resolution failed: Path resolution violates security rules
```

**Solutions:**
- Reduce the number of parent directory traversals (`../`)
- Avoid system directories (`/etc/`, `/usr/`, etc.)
- Use relative paths within reasonable bounds

**File not found after resolution:**
```
DuckDB Error: Failed to open file
```

**Solutions:**
- Verify the resolved path points to an existing file
- Check file permissions
- Ensure the file is not a directory

#### Debugging

```python
from duckalog import generate_sql

# Generate SQL to see resolved paths
sql = generate_sql("catalog.yaml")
print(sql)  # Shows absolute paths after resolution
```

For complete details, see the [Path Resolution Guide](path-resolution.md).

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

## Common Configuration Patterns

### Parquet-only configuration

For simple cases where you only need to create views over Parquet files:

```yaml
version: 1

duckdb:
  database: catalog.duckdb
  pragmas:
    - "SET memory_limit='1GB'"
    - "SET s3_region='us-west-2'"

views:
  - name: sales_data
    source: parquet
    uri: "s3://data-bucket/sales/*.parquet"

  - name: customer_data
    source: parquet
    uri: "s3://data-bucket/customers/*.parquet"
    
  - name: sales_by_customer
    sql: |
      SELECT 
        c.customer_id,
        c.name,
        c.region,
        SUM(s.amount) as total_sales,
        COUNT(s.order_id) as order_count
      FROM customer_data c
      JOIN sales_data s ON c.customer_id = s.customer_id
      GROUP BY c.customer_id, c.name, c.region
```

### Attachments-only configuration

For joining data from existing databases:

```yaml
version: 1

duckdb:
  database: unified_catalog.duckdb

attachments:
  duckdb:
    - alias: analytics
      path: ./analytics_db.duckdb
      read_only: true
    - alias: warehouse
      path: ./warehouse_db.duckdb
      read_only: true

  sqlite:
    - alias: legacy
      path: ./legacy_system.db

views:
  - name: user_profiles
    source: duckdb
    database: analytics
    table: users
    
  - name: user_orders
    source: duckdb
    database: warehouse
    table: orders
    
  - name: legacy_customers
    source: sqlite
    database: legacy
    table: customers
    
  - name: complete_customer_view
    sql: |
      SELECT 
        p.user_id,
        p.name,
        p.email,
        o.total_orders,
        o.total_spent,
        l.rating as legacy_rating
      FROM user_profiles p
      JOIN user_orders o ON p.user_id = o.user_id
      LEFT JOIN legacy_customers l ON p.user_id = l.id
```

### Iceberg-only configuration

For working exclusively with Iceberg tables:

```yaml
version: 1

duckdb:
  database: iceberg_catalog.duckdb

iceberg_catalogs:
  - name: prod_catalog
    catalog_type: rest
    uri: "https://iceberg-catalog.company.com"
    warehouse: "s3://data-warehouse/production/"
    options:
      token: "${env:ICEBERG_PROD_TOKEN}"

  - name: staging_catalog
    catalog_type: rest
    uri: "https://iceberg-staging.company.com"
    warehouse: "s3://data-warehouse/staging/"
    options:
      token: "${env:ICEBERG_STAGING_TOKEN}"

views:
  - name: production_customers
    source: iceberg
    catalog: prod_catalog
    table: analytics.customers
    
  - name: staging_customers
    source: iceberg
    catalog: staging_catalog
    table: analytics.customers
    
  - name: customer_comparison
    sql: |
      SELECT 
        COALESCE(p.id, s.id) as customer_id,
        p.name as prod_name,
        s.name as staging_name,
        p.updated_at as prod_updated,
        s.updated_at as staging_updated
      FROM production_customers p
      FULL OUTER JOIN staging_customers s ON p.id = s.id
```

### Multi-source configuration

This example combines multiple data sources in a single catalog:

```yaml
version: 1

duckdb:
  database: unified_analytics.duckdb
  pragmas:
    - "SET memory_limit='4GB'"
    - "SET threads=4"
    - "SET s3_region='us-east-1'"

attachments:
  duckdb:
    - alias: reference
      path: ./reference_data.duckdb
      read_only: true
      
iceberg_catalogs:
  - name: data_lake
    catalog_type: rest
    uri: "https://iceberg.data-lake.internal"
    warehouse: "s3://enterprise-data-lake/"
    options:
      token: "${env:ICEBERG_TOKEN}"

views:
  # Reference data from attached database
  - name: user_segments
    source: duckdb
    database: reference
    table: user_segments
    
  # Raw events from S3
  - name: raw_events
    source: parquet
    uri: "s3://events-bucket/raw/*.parquet"
    
  # Processed events from Iceberg
  - name: processed_events
    source: iceberg
    catalog: data_lake
    table: analytics.processed_events
    
  # Unified analytics view
  - name: analytics_events
    sql: |
      SELECT 
        e.event_id,
        e.timestamp,
        e.user_id,
        e.event_type,
        e.properties,
        us.segment_name as user_segment,
        us.tier as user_tier
      FROM raw_events e
      LEFT JOIN user_segments us ON e.user_id = us.user_id
      WHERE e.timestamp >= CURRENT_DATE - INTERVAL 30 DAYS
```

## Error Handling

Duckalog provides a comprehensive exception hierarchy to help you handle errors gracefully in your applications.

### Exception Hierarchy

All Duckalog exceptions inherit from `DuckalogError`, making it easy to catch all library errors:

```python
from duckalog import DuckalogError, load_config, build_catalog

try:
    config = load_config("catalog.yaml")
    build_catalog(config)
except DuckalogError as e:
    # Handle any Duckalog-specific error
    print(f"Duckalog error: {e}")
```

### Specific Exception Types

For more targeted error handling, catch specific exception types:

```python
from duckalog import (
    ConfigError,        # Configuration issues
    EngineError,        # Database/build failures  
    PathResolutionError, # Path resolution problems
    RemoteConfigError,  # Remote config loading failures
    SQLFileError,       # SQL file processing issues
)

try:
    config = load_config("catalog.yaml")
except ConfigError as e:
    print(f"Configuration error: {e}")
except PathResolutionError as e:
    print(f"Path resolution failed: {e}")
    print(f"Original path: {e.original_path}")
    print(f"Resolved path: {e.resolved_path}")
except DuckalogError as e:
    print(f"Other Duckalog error: {e}")
```

### Best Practices

1. **Catch specific exceptions first**: Handle the most specific errors first, then catch more general ones
2. **Use exception chaining**: Duckalog preserves original exceptions to help with debugging
3. **Log with context**: Include relevant information when logging errors
4. **Validate early**: Use `validate_config()` to catch configuration errors before building

```python
import logging
from duckalog import ConfigError, EngineError, validate_config, build_catalog

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_catalog(config_path):
    try:
        # Validate configuration first
        validate_config(config_path)
        logger.info(f"Configuration {config_path} is valid")
        
        # Build catalog
        build_catalog(config_path)
        logger.info("Catalog built successfully")
        
    except ConfigError as e:
        logger.error(f"Configuration error in {config_path}: {e}")
        # Handle configuration issues (missing files, invalid syntax, etc.)
    except EngineError as e:
        logger.error(f"Engine error building catalog: {e}")
        # Handle database issues (connection failures, SQL errors, etc.)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise  # Re-raise unexpected errors
```

## Troubleshooting

### Common errors

#### 1. Invalid configuration syntax

Error message: `ConfigError: Invalid configuration file`

Solutions:
- Validate YAML syntax first with `yamllint` or an online YAML validator
- Ensure proper indentation (YAML is sensitive to spaces)
- Check for unescaped special characters in strings

#### 2. Missing environment variables

Error message: `ConfigError: Environment variable 'AWS_ACCESS_KEY_ID' not found`

Solutions:
- Check that all `env:VAR_NAME` variables are set
- Use `duckalog validate config.yaml` to check environment variables without building
- Consider using a `.env` file with `export` commands or a tool like `direnv`

#### 3. Connection failures

Error message: `DuckDB Error: Invalid Input Error: Failed to open file`

Solutions:
- Check file paths in attachments section
- Ensure credentials for cloud storage are correct
- Verify network connectivity and firewall rules
- For local files, check file permissions

#### 4. SQL errors in views

Error message: `Parser Error: syntax error at or near "JOIN"`

Solutions:
- Validate SQL syntax with `duckalog generate-sql config.yaml` before building
- Check that all referenced views and tables exist
- Verify column names match across join conditions
- Use proper DuckDB SQL syntax (similar to PostgreSQL)

#### 5. Iceberg catalog issues

Error message: `Invalid Input Error: Can't load extension iceberg`

Solutions:
- Ensure DuckDB version supports Iceberg extensions
- Install required extensions: `duckdb.install_extension("iceberg")`
- Check catalog configuration and credentials
- Verify Iceberg catalog server is accessible

### Debugging tips

1. **Validate before building**: Always run `duckalog validate config.yaml` first
2. **Generate SQL first**: Use `duckalog generate-sql config.yaml` to inspect generated SQL
3. **Start simple**: Begin with a single view and gradually add complexity
4. **Use environment check**: Create a simple script to verify required environment variables
5. **Check logs**: Run with verbose logging to see detailed error information

```bash
# Enable debug logging
duckalog build config.yaml --log-level DEBUG
```

## Best Practices

1. **Separate configurations**: Use different configs for different environments
2. **Version control**: Keep your configs in Git alongside your code
3. **Modular views**: Break complex SQL into multiple simpler views when possible
4. **Naming conventions**: Use consistent naming for views and attachments
5. **Security**: Never commit secrets to version control - use environment variables

## Next steps

- Use ``duckalog generate-sql`` to inspect the SQL that will be executed.
- Use the API reference for details on each public function and model.
- Check out the examples in the documentation for more advanced use cases.

