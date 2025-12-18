--8<-- "_snippets/intro-quickstart.md"

# Duckalog Documentation

Welcome to the Duckalog documentation! This comprehensive guide will help you master Duckalog's features and patterns.

## Getting Started

The documentation is organized for different learning styles and needs:

- **[Tutorials](tutorials/index.md)** - Step-by-step hands-on learning for beginners
- **[How-to Guides](how-to/index.md)** - Practical solutions for specific problems
- **[Reference](reference/index.md)** - Technical API documentation and configuration schema
- **[Understanding](explanation/philosophy.md)** - Background context and architectural concepts
- **[Examples](examples/index.md)** - Real-world configuration examples and patterns

## Expanded Quickstart Guide

Let's build on the basic quickstart above with a more realistic analytics scenario that combines multiple data sources.

### Step 1: Initialize with the starter template

Instead of creating a config from scratch, use Duckalog's built-in template generator:

```bash
duckalog init --output analytics_catalog.yaml
```

This creates a well-structured configuration with examples and educational comments.

### Step 2: Set up your analytics configuration

Here's a more comprehensive example that shows Duckalog's multi-source capabilities:

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

Before running Duckalog, set required environment variables:

```bash
export AWS_ACCESS_KEY_ID="your_aws_key"
export AWS_SECRET_ACCESS_KEY="your_aws_secret"
export ICEBERG_TOKEN="your_iceberg_token"
```

### Step 3: Validate and run your catalog (New Workflow)

With the new workflow, you can validate and use your catalog in a single command:

```bash
# Validate first (optional but recommended)
duckalog validate analytics_catalog.yaml

# NEW: Single command to build and query
duckalog run analytics_catalog.yaml --query "SELECT * FROM daily_metrics ORDER BY event_date DESC LIMIT 10"

# OR: Start interactive session
duckalog run analytics_catalog.yaml --interactive
# In the interactive shell, you can run:
# SELECT * FROM daily_metrics ORDER BY event_date DESC LIMIT 10;
# SHOW TABLES;
# DESCRIBE enhanced_events;

# OLD: Two-step workflow (still works)
duckalog build analytics_catalog.yaml
duckdb analytics.duckdb -c "SELECT * FROM daily_metrics ORDER BY event_date DESC LIMIT 10"
```

# Or use duckalog to generate SQL for inspection
duckalog generate-sql analytics_catalog.yaml --output create_views.sql
```

### Step 6: Programmatically interact with your catalog

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

### Step 7: Explore more features

Now that you have a working catalog, explore these advanced capabilities:

- **[Semantic Layer](tutorials/getting-started.md#semantic-models)**: Add business-friendly dimensions and measures
- **[Web UI Dashboard](tutorials/dashboard-basics.md)**: Interactive catalog management and querying
- **[Path Resolution](path-resolution.md)**: Automatic path handling with security validation
- **[Remote Configuration](reference/cli.md#remote-configuration-support)**: Load configs from S3, GCS, Azure, and more

## Key Features Overview

### ✅ Multi-Source Data Integration
- **S3 Parquet/Delta/Iceberg**: Direct querying of cloud data lakes
- **Database Attachments**: Connect DuckDB, SQLite, PostgreSQL databases
- **Semantic Layer**: Business-friendly dimensions and measures
- **Path Resolution**: Automatic path handling with security validation

### ✅ Developer Experience  
- **Config-Driven**: Declarative YAML/JSON configurations
- **Idempotent**: Same config always produces the same catalog
- **CLI + Python API**: Use from command line or in code
- **Remote Configs**: Load configurations from S3, GCS, Azure, GitHub

### ✅ Production Ready
- **Security**: Environment variable credentials, no secrets in configs
- **Performance**: Optimized for large-scale analytics workloads
- **Monitoring**: Comprehensive logging and error handling
- **Web UI**: Interactive dashboard for catalog management

### ✅ Enterprise Features
- **Semantic Models**: Business-friendly metadata layer
- **Secret Management**: Canonical credential configuration
- **Audit Trail**: Config-driven change tracking
- **Multi-Cloud**: Support for AWS, GCP, Azure storage systems

## Popular Examples

- 📊 **[Multi-Source Analytics](examples/multi-source-analytics.md)**: Combine Parquet, DuckDB, and PostgreSQL data
- 🔒 **[Environment Variables Security](examples/environment-vars.md)**: Secure credential management patterns  
- ⚡ **[DuckDB Performance Settings](examples/duckdb-settings.md)**: Optimize memory, threads, and storage
- 🏷️ **[Semantic Layer v2](examples/config-imports.md)**: Business-friendly semantic models with dimensions and measures

## Quick Reference

```bash
# Installation
pip install duckalog           # Core package
pip install duckalog[ui]       # With web dashboard
pip install duckalog[remote]   # With remote configuration support

# Core CLI commands
duckalog init                  # Create starter configuration
duckalog build catalog.yaml    # Build DuckDB catalog
duckalog validate catalog.yaml # Check configuration syntax
duckalog ui catalog.yaml       # Launch web dashboard

# Remote configuration examples
duckalog build s3://bucket/config.yaml          # S3 configuration
duckalog build github://user/repo/config.yaml   # GitHub repository
duckalog build gs://bucket/config.yaml          # Google Cloud Storage
```

```python
# Python API basics
from duckalog import build_catalog, generate_sql, validate_config

# Start with a template
from duckalog.config_init import create_config_template
config = create_config_template(format="yaml", output_path="my_config.yaml")

# Build and validate
build_catalog("my_config.yaml")
validate_config("my_config.yaml")
sql = generate_sql("my_config.yaml")
```

## Next Steps

- **🆕 New to Duckalog?** Start with the [Getting Started Tutorial](tutorials/getting-started.md)
- **🎯 Have a specific problem?** Browse the [How-to Guides](how-to/index.md)  
- **📚 Need technical details?** Check the [Reference documentation](reference/index.md)
- **🏗️ Want to understand the design?** Read the [Architecture overview](explanation/architecture.md)
- **💡 Need ideas?** Explore the [Examples](examples/index.md) collection
