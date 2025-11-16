# Multi-Source Analytics Example

This example demonstrates how to use Duckalog to build a comprehensive analytics catalog that combines data from multiple sources into a unified view. You'll learn how to configure attachments, Iceberg catalogs, and cloud storage to create powerful analytical queries.

## Business Scenario

Imagine you're building an analytics platform for a growing company. Your data lives in several places:
- **Raw events** stored as Parquet files in S3 (high-volume, cost-effective storage)
- **Reference data** in local DuckDB databases (fast, local access)
- **Legacy customer data** in SQLite (existing systems)
- **Product information** in PostgreSQL (operational systems)
- **Processed event data** in Iceberg tables (data warehouse)

This example shows how to unify all these sources into a single DuckDB catalog that enables rich analytics across your entire data landscape.

## Prerequisites

Before running this example, ensure you have:

1. **Python 3.9+** with Duckalog installed:
   ```bash
   pip install duckalog
   ```

2. **Required environment variables** (see Environment Variables section below)

3. **Sample data sources** (or use the provided examples with mock paths):
   - S3 bucket with Parquet files
   - Iceberg catalog access (e.g., AWS Glue, Tabular)
   - PostgreSQL database
   - Local DuckDB/SQLite databases (can be created for testing)

## Complete Configuration

Here's the full configuration with explanations for each section:

### Base Configuration

```yaml
# Configuration file version
version: 1

# DuckDB database settings
duckdb:
  # Output database file
  database: multi_source.duckdb
  
  # Extensions needed for cloud and data lake access
  install_extensions:
    - httpfs          # For HTTP/S3 file access
    - iceberg         # For Iceberg table support
  
  # Performance and behavior settings
  pragmas:
    - "SET memory_limit='2GB'"      # Limit memory usage
    - "SET threads=4"               # Parallel processing
    - "SET timezone='UTC'"          # Consistent time handling
    
    # Cloud storage configuration
    # These settings enable S3 access for Parquet files
    - "SET s3_region='us-west-2'"
    - "SET s3_access_key_id='${env:AWS_ACCESS_KEY_ID}'"
    - "SET s3_secret_access_key='${env:AWS_SECRET_ACCESS_KEY}'"
    - "SET s3_session_token='${env:AWS_SESSION_TOKEN}'"  # Optional for temp credentials
```

**Key Concepts Demonstrated:**
- Extension installation for extended functionality
- Memory and threading optimization for performance
- Environment variable injection for credentials
- Timezone consistency for global data

### Database Attachments

```yaml
# External database attachments
attachments:
  # Local DuckDB databases (read-only for safety)
  duckdb:
    - alias: reference         # How you'll reference this database in views
      path: ./reference_data.duckdb     # Local file path
      read_only: true         # Prevent accidental modifications
      
    - alias: historical
      path: ./historical_data.duckdb
      read_only: true

  # Legacy system in SQLite format
  sqlite:
    - alias: legacy           # Reference name for SQL queries
      path: ./legacy_system.db  # Local SQLite database file

  # Production and staging PostgreSQL databases
  postgres:
    - alias: prod_db         # Production database reference
      host: "${env:PROD_DB_HOST}"    # Environment variable for security
      port: 5432
      database: analytics_prod
      user: "${env:PROD_DB_USER}"
      password: "${env:PROD_DB_PASSWORD}"
      sslmode: require        # Secure connection

    - alias: staging_db      # Staging environment
      host: "${env:STAGING_DB_HOST}"
      port: 5432
      database: analytics_staging
      user: "${env:STAGING_DB_USER}"
      password: "${env:STAGING_DB_PASSWORD}"
      sslmode: require
```

**Key Concepts Demonstrated:**
- Multiple database attachment types (DuckDB, SQLite, PostgreSQL)
- Read-only attachments for safety
- Environment variable usage for credentials
- SSL configuration for secure connections
- Environment-specific configurations (prod vs staging)

### Iceberg Catalogs

```yaml
# Iceberg data lake catalogs
iceberg_catalogs:
  - name: production_iceberg    # Reference name used in views
    catalog_type: rest          # REST catalog (vs Hadoop, Spark, etc.)
    uri: "https://iceberg-catalog.production.company.com"  # Catalog endpoint
    warehouse: "s3://company-data-warehouse/production/"   # Storage location
    options:
      token: "${env:ICEBERG_PROD_TOKEN}"  # Authentication

  - name: staging_iceberg       # Staging environment catalog
    catalog_type: rest
    uri: "https://iceberg-catalog.staging.company.com"
    warehouse: "s3://company-data-warehouse/staging/"
    options:
      token: "${env:ICEBERG_STAGING_TOKEN}"
```

**Key Concepts Demonstrated:**
- REST catalog configuration (most common for cloud data lakes)
- Environment-specific catalog separation
- Token-based authentication
- Warehouse path configuration

### Views Definition

Views are the core of your analytics - they define how data is accessed and transformed:

```yaml
# Data access and transformation views
views:
  # Raw data from different sources
  - name: raw_events                    # View name for querying
    source: parquet                     # Data source type
    uri: "s3://company-data-lake/events/raw/*.parquet"  # File pattern
    description: "Raw events from data lake"

  - name: processed_events
    source: iceberg                     # Iceberg table access
    catalog: production_iceberg         # Reference to configured catalog
    table: analytics.processed_events   # Schema.table format
    description: "Processed events from production Iceberg catalog"

  - name: user_profiles
    source: duckdb                      # Attached DuckDB database
    database: reference                 # Alias from attachments section
    table: users                        # Table name in attached database
    description: "User reference data"

  - name: legacy_customers
    source: sqlite                      # SQLite attachment
    database: legacy                    # SQLite alias
    table: customers
    description: "Legacy customer data from SQLite"

  - name: product_data
    source: postgres                    # PostgreSQL attachment
    database: prod_db                   # Production database alias
    table: products
    description: "Product data from production Postgres"
```

**Key Concepts Demonstrated:**
- Multiple source types in unified catalog
- Schema.table naming for structured data
- Descriptive metadata for documentation

### Advanced Analytics Views

These views demonstrate complex analytics across multiple data sources:

```yaml
  # Enriched analytics views
  - name: enriched_events
    sql: |
      SELECT
        e.event_id,
        e.timestamp,
        e.event_type,
        e.user_id,
        e.session_id,
        e.properties,
        u.name as user_name,           # Join user reference data
        u.email,
        u.segment,
        p.name as product_name,        # Join product catalog
        p.category as product_category
      FROM raw_events e
      LEFT JOIN user_profiles u ON e.user_id = u.id
      LEFT JOIN product_data p ON e.properties->>'product_id' = p.id
    description: "Events enriched with user and product data"

  - name: event_metrics
    sql: |
      SELECT
        DATE(timestamp) as event_date,     # Daily aggregation
        event_type,
        COUNT(*) as event_count,
        COUNT(DISTINCT user_id) as unique_users,
        COUNT(DISTINCT session_id) as unique_sessions
      FROM enriched_events
      GROUP BY DATE(timestamp), event_type
      ORDER BY event_date DESC, event_count DESC
    description: "Daily event metrics for reporting"

  - name: user_activity_summary
    sql: |
      SELECT
        u.id as user_id,
        u.name,
        u.email,
        u.segment,
        COUNT(DISTINCT DATE(ee.timestamp)) as active_days,
        COUNT(DISTINCT ee.session_id) as total_sessions,
        COUNT(*) as total_events,
        MAX(ee.timestamp) as last_activity
      FROM user_profiles u
      LEFT JOIN enriched_events ee ON u.id = ee.user_id
      GROUP BY u.id, u.name, u.email, u.segment
      ORDER BY total_events DESC
    description: "User engagement summary"

  - name: product_performance
    sql: |
      SELECT
        p.id as product_id,
        p.name as product_name,
        p.category,
        COUNT(*) as event_count,
        COUNT(DISTINCT ee.user_id) as unique_users,
        MAX(ee.timestamp) as last_mentioned
      FROM product_data p
      JOIN enriched_events ee ON p.id = ee.properties->>'product_id'
      GROUP BY p.id, p.name, p.category
      ORDER BY event_count DESC
    description: "Product engagement analysis"
```

**Key Concepts Demonstrated:**
- SQL view composition (building on previous views)
- Cross-source joins (Parquet + DuckDB + PostgreSQL)
- JSON field access (`properties->>'product_id'`)
- Aggregation and window functions
- Complex business logic implementation

### Executive Reporting

```yaml
  - name: daily_kpi_report
    sql: |
      WITH daily_metrics AS (
        SELECT
          DATE(timestamp) as event_date,
          COUNT(*) as total_events,
          COUNT(DISTINCT user_id) as daily_active_users,
          COUNT(DISTINCT session_id) as daily_sessions
        FROM enriched_events
        GROUP BY DATE(timestamp)
      )
      SELECT
        event_date,
        total_events,
        daily_active_users,
        daily_sessions,
        ROUND(total_events * 1.0 / daily_sessions, 2) as events_per_session,
        LAG(daily_active_users) OVER (ORDER BY event_date) as prev_day_users,
        ROUND((daily_active_users - LAG(daily_active_users) OVER (ORDER BY event_date)) * 100.0 /
              LAG(daily_active_users) OVER (ORDER BY event_date), 2) as user_growth_pct
      FROM daily_metrics
      ORDER BY event_date DESC
    description: "Executive KPI dashboard data"
```

**Key Concepts Demonstrated:**
- Common Table Expressions (CTEs)
- Window functions for trend analysis
- Percentage growth calculations
- Executive-level metrics aggregation

## Step-by-Step Usage

### 1. Prepare Environment Variables

Create a `.env` file or export variables in your shell:

```bash
# AWS credentials for S3 access
export AWS_ACCESS_KEY_ID="your_aws_access_key"
export AWS_SECRET_ACCESS_KEY="your_aws_secret_key"
export AWS_SESSION_TOKEN="your_session_token"  # Optional

# PostgreSQL credentials
export PROD_DB_HOST="prod-db.company.com"
export PROD_DB_USER="analytics_user"
export PROD_DB_PASSWORD="secure_password"

export STAGING_DB_HOST="staging-db.company.com"
export STAGING_DB_USER="analytics_staging"
export STAGING_DB_PASSWORD="staging_password"

# Iceberg catalog tokens
export ICEBERG_PROD_TOKEN="your_production_catalog_token"
export ICEBERG_STAGING_TOKEN="your_staging_catalog_token"
```

### 2. Validate Configuration

Before building, validate your configuration:

```bash
duckalog validate docs/examples/multi-source-analytics-config.yaml
```

This checks:
- YAML syntax
- Environment variable resolution
- View definitions
- Attachment configurations

### 3. Generate SQL (Optional)

Preview the SQL that will be executed:

```bash
duckalog generate-sql docs/examples/multi-source-analytics-config.yaml --output preview.sql
cat preview.sql
```

### 4. Build the Catalog

Create your unified analytics catalog:

```bash
duckalog build docs/examples/multi-source-analytics-config.yaml
```

This will:
- Install required DuckDB extensions
- Create `multi_source.duckdb` database
- Set up all attachments
- Create all views and joins

### 5. Query Your Data

Connect to the unified catalog:

```bash
# Using DuckDB CLI
duckdb multi_source.duckdb

# Example queries in DuckDB:
SELECT * FROM daily_kpi_report ORDER BY event_date DESC LIMIT 10;

SELECT 
  event_type,
  COUNT(*) as events,
  COUNT(DISTINCT user_id) as users
FROM enriched_events 
WHERE DATE(timestamp) >= CURRENT_DATE - INTERVAL 7 DAYS
GROUP BY event_type
ORDER BY events DESC;
```

### 6. Use Programmatically

```python
from duckalog import load_config
import duckdb

# Load configuration
config = load_config("docs/examples/multi-source-analytics-config.yaml")

# Connect to the created catalog
con = duckdb.connect("multi_source.duckdb")

# Run analytics queries
df = con.execute("""
    SELECT * FROM user_activity_summary 
    WHERE active_days >= 7 
    ORDER BY total_events DESC
""").df()

print(df.head())
```

## Key Concepts Demonstrated

This example teaches several important Duckalog patterns:

1. **Multi-Source Unification**: How to bring together Parquet, DuckDB, SQLite, PostgreSQL, and Iceberg
2. **Environment-Based Configuration**: Using environment variables for different deployments
3. **Progressive Data Enrichment**: Building from raw data to enriched analytics
4. **Performance Optimization**: Memory limits, threading, and read-only attachments
5. **Security Best Practices**: No hardcoded credentials, read-only when possible
6. **SQL Composition**: Building complex analytics through view composition
7. **Business Logic**: Implementing real analytics patterns (KPI reporting, user engagement)

## Troubleshooting

### Common Issues

**Missing Environment Variables:**
```bash
# Check what variables are missing
duckalog validate docs/examples/multi-source-analytics-config.yaml
# Look for "Environment variable 'VAR_NAME' not found" errors
```

**S3 Connection Errors:**
```bash
# Verify AWS credentials
aws s3 ls s3://company-data-lake/events/raw/
# Check S3 region and credentials in config
```

**Database Connection Failures:**
```bash
# Test PostgreSQL connection manually
psql -h prod-db.company.com -U analytics_user -d analytics_prod
# Verify SSL settings and firewall rules
```

**Iceberg Catalog Issues:**
```bash
# Check catalog accessibility
curl -H "Authorization: Bearer $ICEBERG_PROD_TOKEN" \
     "https://iceberg-catalog.production.company.com/v1/config"
```

### Performance Tips

1. **Memory Limits**: Adjust `memory_limit` based on available RAM
2. **Threading**: Set `threads` to number of CPU cores
3. **Read-Only Attachments**: Use `read_only: true` when possible
4. **Query Optimization**: Use `generate-sql` to optimize complex views
5. **Index Consideration**: Ensure source tables have appropriate indexes

## Variations and Customizations

### Environment-Specific Configs

Create separate configs for different environments:

**`config-production.yaml`:**
```yaml
iceberg_catalogs:
  - name: main
    catalog_type: rest
    uri: "https://iceberg.company.com/prod"
    # Production settings
```

**`config-staging.yaml`:**
```yaml
iceberg_catalogs:
  - name: main
    catalog_type: rest
    uri: "https://iceberg.company.com/staging"
    # Staging settings
```

### Incremental Loading

For large datasets, consider incremental views:

```yaml
- name: recent_events
  sql: |
    SELECT * FROM enriched_events
    WHERE DATE(timestamp) >= CURRENT_DATE - INTERVAL 30 DAYS
```

### Custom Aggregations

Add domain-specific aggregations:

```yaml
- name: cohort_analysis
  sql: |
    SELECT 
      DATE_TRUNC('week', u.signup_date) as cohort_week,
      COUNT(DISTINCT u.id) as cohort_size,
      COUNT(DISTINCT ee.user_id) as retained_users
    FROM user_profiles u
    LEFT JOIN enriched_events ee ON u.id = ee.user_id
    GROUP BY DATE_TRUNC('week', u.signup_date)
```

This example demonstrates Duckalog's power to unify diverse data sources into a coherent analytics platform. Adapt the patterns shown here to your specific data landscape and business requirements.