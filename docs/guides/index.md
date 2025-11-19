# User Guide

Welcome to the Duckalog User Guide. This section covers how to use Duckalog effectively, from basic configuration to advanced patterns and troubleshooting.

## Getting Started

### Configuration Structure
At a high level, a Duckalog config looks like this:

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

### Environment Variables
Any string may contain `${env:VAR_NAME}` placeholders. Duckalog resolves these using the process environment before validation. If a variable is missing, a `ConfigError` is raised.

Example:
```yaml
duckdb:
  pragmas:
    - "SET s3_access_key_id='${env:AWS_ACCESS_KEY_ID}'"
    - "SET s3_secret_access_key='${env:AWS_SECRET_ACCESS_KEY}'"
```

## Core Concepts

### Attachments
Attachments let you expose tables from other databases inside DuckDB.

- **DuckDB attachments**: attach additional `.duckdb` files.
- **SQLite attachments**: attach local SQLite databases.
- **Postgres attachments**: connect to external Postgres instances.

Views that use attached databases set `source` to `duckdb`, `sqlite`, or `postgres` and provide `database` (attachment alias) and `table`.

### Iceberg Catalogs
Iceberg catalogs are configured under `iceberg_catalogs`. Iceberg views can either:

- Use a `uri` directly, or
- Refer to a `catalog` + `table` combination.

Duckalog validates that any `catalog` used by a view is defined in `iceberg_catalogs`.

## Configuration Patterns

### Parquet-only Configuration
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

### Attachments-only Configuration
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

### Iceberg-only Configuration
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

### Multi-source Configuration
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

## Troubleshooting

### Common Errors

#### 1. Invalid Configuration Syntax
Error message: `ConfigError: Invalid configuration file`

Solutions:
- Validate YAML syntax first with `yamllint` or an online YAML validator
- Ensure proper indentation (YAML is sensitive to spaces)
- Check for unescaped special characters in strings

#### 2. Missing Environment Variables
Error message: `ConfigError: Environment variable 'AWS_ACCESS_KEY_ID' not found`

Solutions:
- Check that all `env:VAR_NAME` variables are set
- Use `duckalog validate config.yaml` to check environment variables without building
- Consider using a `.env` file with `export` commands or a tool like `direnv`

#### 3. Connection Failures
Error message: `DuckDB Error: Invalid Input Error: Failed to open file`

Solutions:
- Check file paths in attachments section
- Ensure credentials for cloud storage are correct
- Verify network connectivity and firewall rules
- For local files, check file permissions

#### 4. SQL Errors in Views
Error message: `Parser Error: syntax error at or near "JOIN"`

Solutions:
- Validate SQL syntax with `duckalog generate-sql config.yaml` before building
- Check that all referenced views and tables exist
- Verify column names match across join conditions
- Use proper DuckDB SQL syntax (similar to PostgreSQL)

#### 5. Iceberg Catalog Issues
Error message: `Invalid Input Error: Can't load extension iceberg`

Solutions:
- Ensure DuckDB version supports Iceberg extensions
- Install required extensions: `duckdb.install_extension("iceberg")`
- Check catalog configuration and credentials
- Verify Iceberg catalog server is accessible

### Debugging Tips

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

## Next Steps

- Use ``duckalog generate-sql`` to inspect the SQL that will be executed.
- Use the API reference for details on each public function and model.
- Check out the examples in the documentation for more advanced use cases.