# Duckalog Documentation

Welcome to the Duckalog documentation. Duckalog is a Python library and CLI
for building DuckDB catalogs from declarative YAML/JSON configuration files.

Use these docs to:

- Understand the core concepts behind Duckalog configs.
- Get started with the CLI and Python API.
- Find API reference information generated from the source code.
- Learn about the [system architecture](architecture.md) and design patterns.

For a deeper product and technical description, see the [Architecture in `architecture.md`](architecture.md).

## Quick Start Guide: A Realistic Example

Let's walk through a typical analytics scenario where you need to combine data from multiple sources: Parquet files in S3, a reference database (DuckDB), and an Iceberg table. We'll create a unified catalog that joins these datasources.

### Step 1: Set up your configuration

First, create a comprehensive config file called `analytics_catalog.yaml`:

```yaml
version: 1

duckdb:
  database: analytics.duckdb
  pragmas:
    - "SET memory_limit='2GB'"
    - "SET s3_access_key_id='${env:AWS_ACCESS_KEY_ID}'"
    - "SET s3_secret_access_key='${env:AWS_SECRET_ACCESS_KEY}'"

# Attach our reference data database
attachments:
  duckdb:
    - alias: refdata
      path: ./reference_data.duckdb
      read_only: true

# Configure Iceberg catalog access
iceberg_catalogs:
  - name: analytics_warehouse
    catalog_type: rest
    uri: "https://iceberg-catalog.example.com"
    warehouse: "s3://our-warehouse/analytics/"
    options:
      token: "${env:ICEBERG_TOKEN}"

views:
  # Raw events from S3 Parquet files
  - name: raw_events
    source: parquet
    uri: "s3://our-bucket/events/*.parquet"
  
  # Product data from Iceberg
  - name: products
    source: iceberg
    catalog: analytics_warehouse
    table: analytics.products
  
  # Customer reference data from attached database
  - name: customers
    source: duckdb
    database: refdata
    table: customers
  
  # Enhanced events with joined data
  - name: enhanced_events
    sql: |
      SELECT 
        e.event_id,
        e.timestamp,
        e.user_id,
        e.event_type,
        c.name as customer_name,
        c.segment as customer_segment,
        p.category as product_category,
        p.price as product_price
      FROM raw_events e
      JOIN customers c ON e.customer_id = c.id
      LEFT JOIN products p ON e.product_id = p.id
  
  # Daily aggregation
  - name: daily_metrics
    sql: |
      SELECT 
        DATE(timestamp) as event_date,
        event_type,
        COUNT(*) as event_count,
        COUNT(DISTINCT user_id) as unique_users,
        AVG(product_price) as avg_product_value
      FROM enhanced_events
      GROUP BY DATE(timestamp), event_type
```

### Step 2: Set environment variables

Before running Duckalog, set the required environment variables:

```bash
export AWS_ACCESS_KEY_ID="your_aws_key"
export AWS_SECRET_ACCESS_KEY="your_aws_secret"
export ICEBERG_TOKEN="your_iceberg_token"
```

### Step 3: Validate and build your catalog

First, let's validate the configuration to catch any issues early:

```bash
duckalog validate analytics_catalog.yaml
```

If validation passes, build the catalog:

```bash
duckalog build analytics_catalog.yaml
```

This will create the `analytics.duckdb` file with all your views properly configured.

### Step 4: Use your catalog

Now you can query your unified data source:

```bash
# Connect directly with DuckDB CLI
duckdb analytics.duckdb -c "SELECT * FROM daily_metrics ORDER BY event_date DESC LIMIT 10"

# Or use duckalog to generate SQL for inspection
duckalog generate-sql analytics_catalog.yaml --output create_views.sql
```

### Step 5: Programmatically interact with your catalog

You can also use the Python API for more advanced workflows:

```python
from duckalog import build_catalog, generate_sql, load_config
import polars as pl
import duckdb

# Load configuration
config = load_config("analytics_catalog.yaml")

# Generate SQL without execution
sql = generate_sql("analytics_catalog.yaml")
print("SQL to be executed:")
print(sql)

# Build catalog programmatically
build_catalog("analytics_catalog.yaml")

# Query with DuckDB directly
con = duckdb.connect("analytics.duckdb")

# Get daily metrics as DataFrame
metrics_df = con.execute("SELECT * FROM daily_metrics WHERE event_date >= CURRENT_DATE - INTERVAL 7 DAYS").df()
print(f"Last 7 days of metrics: {metrics_df}")

# Get enhanced events for a specific user
user_events = con.execute("SELECT * FROM enhanced_events WHERE user_id = 'user123'").df()
print(f"User events: {user_events}")

con.close()
```

This example demonstrates how Duckalog can help you create a cohesive analytics layer that combines data from multiple sources, applies business logic, and provides a single point of access for your data consumers.

## Path Resolution Feature

Duckalog includes automatic path resolution that converts relative file paths to absolute paths relative to the configuration file location. This provides consistent behavior across different working directories while maintaining security validation.

### Key Benefits

- **Portability**: Configurations can be moved between environments without breaking file references
- **Security**: Built-in validation prevents directory traversal attacks while allowing reasonable parent directory access
- **Consistency**: Paths are resolved consistently regardless of the current working directory
- **Flexibility**: Works with relative paths, absolute paths, and remote URIs

### Quick Example

```yaml
version: 1

duckdb:
  database: catalog.duckdb

views:
  - name: events
    source: parquet
    uri: data/events.parquet        # Automatically resolved to absolute path
    
  - name: reference
    source: parquet  
    uri: ../shared/data/users.parquet  # Parent directory access allowed
```

The paths above are automatically resolved relative to the configuration file location when loaded.

**Learn more:** [Path Resolution Guide](path-resolution.md)

## Secret Management

Duckalog provides comprehensive secret management for secure credential handling:

### Environment Variable Integration
All sensitive configuration uses environment variables:

```yaml
duckdb:
  pragmas:
    - "SET s3_access_key_id='${env:AWS_ACCESS_KEY_ID}'"
    - "SET s3_secret_access_key='${env:AWS_SECRET_ACCESS_KEY}'"

attachments:
  postgres:
    - host: "${env:PG_HOST}"
      user: "${env:PG_USER}"
      password: "${env:PG_PASSWORD}"
```

### Canonical Secret Configuration
Define secrets once and reference them across views:

```yaml
secrets:
  - name: s3_credentials
    type: s3
    key_id: "${env:AWS_ACCESS_KEY_ID}"
    secret: "${env:AWS_SECRET_ACCESS_KEY}"
    region: "us-east-1"

views:
  - name: sales_data
    source: parquet
    uri: "s3://my-bucket/sales/*.parquet"
    secrets_ref: s3_credentials
```

## Remote Configuration

Load configurations from remote sources:

```bash
# S3 configuration
duckalog build s3://my-bucket/catalog.yaml --fs-key AKIA... --fs-secret...

# GitHub repository
duckalog build github://user/repo/catalog.yaml --fs-token ghp_...

# Azure Blob Storage
duckalog build abfs://account@container/catalog.yaml --azure-connection-string "..."
```

**Learn more:** [Architecture - Remote Configuration](architecture.md#remote-configuration-architecture)

## Quick Reference

### Documentation Structure

- **[System Architecture](architecture.md)** - Understanding Duckalog's design, components, and patterns
  - **[Config Package Structure](architecture.md#2-configuration-models-package-duckalogconfigmodels)** - Unified configuration interface
  - **[CatalogBuilder Orchestration](architecture.md#4-engine-module-enginepy-with-catalogbuilder-orchestration)** - Engine workflow management
  - **[Path Security Architecture](architecture.md#path-security-architecture)** - Security boundaries and validation
  - **[Secret Management](architecture.md#secret-management-architecture)** - Canonical secret models and DuckDB integration
  - **[Remote Configuration](architecture.md#remote-configuration-architecture)** - Remote access and filesystem integration
- **[Path Resolution Guide](path-resolution.md)** - Automatic path resolution and security features
- **[User Guide](guides/usage.md)** - Configuration patterns and troubleshooting

### Install

```bash
pip install duckalog
```

### Basic Commands

```bash
# Build a catalog from configuration
duckalog build catalog.yaml

# Generate SQL without executing it
duckalog generate-sql catalog.yaml --output create_views.sql

# Validate configuration syntax
duckalog validate catalog.yaml
```

### Python API

```python
from duckalog import build_catalog, generate_sql, validate_config

# Build or update a catalog
build_catalog("catalog.yaml")

# Generate SQL without execution
sql = generate_sql("catalog.yaml")

# Validate configuration
validate_config("catalog.yaml")
```

For a deeper product and technical description, see the PRD in
`docs/PRD_Spec.md`.
