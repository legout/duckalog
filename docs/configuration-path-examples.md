# Configuration Examples: Path Resolution

This document provides practical configuration examples demonstrating how to use path resolution effectively in various scenarios.

## Simple Project Structure

### Basic Relative Paths

```yaml
# catalog.yaml - in project root
version: 1

duckdb:
  database: analytics.duckdb
  install_extensions:
    - parquet

views:
  - name: users
    source: parquet
    uri: "data/users.parquet"
    description: "User profiles from parquet files"

  - name: events
    source: parquet
    uri: "data/events/*.parquet"
    description: "Event data with wildcard support"
```

**Project Structure:**
```
my-project/
├── catalog.yaml
└── data/
    ├── users.parquet
    └── events/
        ├── events_2024.parquet
        └── events_2023.parquet
```

### Configuration with Directories

```yaml
version: 1

duckdb:
  database: multi_source.duckdb
  install_extensions:
    - parquet
    - httpfs

views:
  # Different data sources with different relative paths
  - name: raw_data
    source: parquet
    uri: "raw/consumer-events/*.parquet"
    description: "Raw consumer event data"

  - name: processed_data
    source: parquet
    uri: "processed/daily-aggregates.parquet"
    description: "Processed daily aggregates"

  - name: reference_data
    source: parquet
    uri: "reference/lookup-tables/*.parquet"
    description: "Reference lookup tables"

  # Remote data (not affected by path resolution)
  - name: cloud_backup
    source: parquet
    uri: "s3://backup-bucket/analytics/*.parquet"
    description: "Cloud backup data"
```

**Project Structure:**
```
data-platform/
├── catalog.yaml
├── raw/
│   └── consumer-events/
├── processed/
│   └── daily-aggregates.parquet
└── reference/
    └── lookup-tables/
```

## Multi-Project Collaboration

### Shared Resources Structure

```yaml
# team-a/analytics.yaml
version: 1

duckdb:
  database: team_a_analytics.duckdb

views:
  - name: our_events
    source: parquet
    uri: "data/events/*.parquet"
    description: "Team A event data"

  - name: shared_reference
    source: parquet
    uri: "../shared-data/reference/geo-boundaries.parquet"
    description: "Shared geographic reference data"

  - name: company_lookups
    source: parquet
    uri: "../shared-data/lookups/product-categories.parquet"
    description: "Company-wide product categories"
```

**Multi-Project Structure:**
```
company-analytics/
├── shared-data/
│   ├── reference/
│   │   └── geo-boundaries.parquet
│   └── lookups/
│       └── product-categories.parquet
├── team-a/
│   ├── analytics.yaml
│   └── data/
└── team-b/
    ├── analytics.yaml
    └── data/
```

### Team-B Configuration

```yaml
# team-b/analytics.yaml
version: 1

duckdb:
  database: team_b_analytics.duckdb

views:
  - name: our_metrics
    source: parquet
    uri: "data/metrics/*.parquet"
    description: "Team B metrics data"

  - name: same_geo_reference
    source: parquet
    uri: "../shared-data/reference/geo-boundaries.parquet"
    description: "Same reference data used by Team A"

  - name: shared_products
    source: parquet
    uri: "../shared-data/lookups/product-categories.parquet"
    description: "Shared product categories"
```

## Advanced Path Patterns

### Environment Variable Integration

```yaml
version: 1

duckdb:
  database: "${env:CATALOG_NAME:analytics}.duckdb"

views:
  - name: configurable_data
    source: parquet
    uri: "${env:DATA_DIR:data}/*.parquet"
    description: "Configurable data directory"

  - name: reference_tables
    source: parquet
    uri: "${env:REF_DIR:reference}/{table}.parquet"
    description: "Reference tables with variable substitution"

attachments:
  duckdb:
    - alias: historical_db
      path: "${env:HIST_DB_PATH:./historical.duckdb}"
      read_only: true
```

### Mixed Path Types

```yaml
version: 1

duckdb:
  database: mixed_paths.duckdb

# Local attachments with relative paths
attachments:
  duckdb:
    - alias: local_reference
      path: "reference/data.duckdb"
      read_only: true

  # External database with absolute path
  duckdb:
    - alias: corporate_reference
      path: "/shared/data/corporate-reference.duckdb"
      read_only: true

views:
  # Local data using relative paths
  - name: local_parquet
    source: parquet
    uri: "data/local-parquet/*.parquet"
    description: "Local parquet data"

  # Analysis views using local data
  - name: local_analysis
    sql: |
      SELECT *
      FROM local_parquet lp
      JOIN local_reference.reference_data rd ON lp.id = rd.id
    description: "Local data analysis"

  # Analysis using corporate reference
  - name: corporate_analysis
    sql: |
      SELECT *
      FROM local_parquet lp
      JOIN corporate_reference.company_dimensions cd ON lp.company_id = cd.id
    description: "Analysis with corporate reference data"
```

## Cross-Platform Considerations

### Windows-Compatible Configuration

```yaml
version: 1

duckdb:
  database: cross-platform.duckdb

views:
  # Use forward slashes for cross-platform compatibility
  - name: universal_data
    source: parquet
    uri: "data/universal/*.parquet"
    description: "Works on Windows, macOS, Linux"

  - name: parent_directory
    source: parquet
    uri: "../shared/parent-data.parquet"
    description: "Parent directory traversal works on all platforms"

  - name: complex_relative
    source: parquet
    uri: "data/subdir/more-levels/deep-data.parquet"
    description: "Complex relative path structure"

attachments:
  duckdb:
    - alias: local_db
      path: "databases/reference.duckdb"
      read_only: true
```

## Performance Optimization

### Optimized Path Configuration

```yaml
version: 1

duckdb:
  database: performance-optimized.duckdb
  pragmas:
    - "SET memory_limit='8GB'"
  install_extensions:
    - parquet

views:
  # Partitioned data with relative paths
  - name: partitioned_events
    source: parquet
    uri: "data/partitioned/events/year=*/month=*/*.parquet"
    description: "Partitioned event data for efficient querying"

  - name: aggregated_daily
    source: parquet
    uri: "data/aggregated/daily/*.parquet"
    description: "Pre-aggregated daily data for faster queries"

  - name: reference_indexes
    source: parquet
    uri: "data/reference/with-indexes/*.parquet"
    description: "Reference data with DuckDB indexes"

  # Views for different query patterns
  - name: quick_lookups
    sql: |
      SELECT u.*, r.category_name
      FROM reference_indexes.users u
      JOIN reference_indexes.reference r ON u.category_id = r.category_id
    description: "Optimized for quick lookups"

  - name: time_series_analysis
    sql: |
      SELECT 
        DATE(event_timestamp) as event_date,
        COUNT(*) as event_count,
        COUNT(DISTINCT user_id) as unique_users
      FROM partitioned_events
      WHERE event_timestamp >= CURRENT_DATE - INTERVAL '90 days'
      GROUP BY DATE(event_timestamp)
      ORDER BY event_date DESC
    description: "Time series analysis on partitioned data"
```

## Security-Focused Configuration

### Secure Path Management

```yaml
version: 1

duckdb:
  database: secure-analytics.duckdb

views:
  # Safe relative paths within project bounds
  - name: secure_user_data
    source: parquet
    uri: "data/anonymized-users.parquet"
    description: "Anonymized user data (safe within project)"

  - name: secure_events
    source: parquet
    uri: "data/processed-events.parquet"
    description: "Processed events (sanitized data)"

  # Reference data from same project
  - name: secure_reference
    source: parquet
    uri: "reference/dimension-tables.parquet"
    description: "Reference data within project security scope"

  # Remote secure access (no local path issues)
  - name: secure_remote
    source: parquet
    uri: "s3://secure-company-analytics/data/processed/*.parquet"
    description: "Secure remote data via S3"
```

## Development vs Production

### Development Configuration

```yaml
# config-dev.yaml
version: 1

duckdb:
  database: "dev_analytics.duckdb"

views:
  - name: dev_users
    source: parquet
    uri: "data/users-sample.parquet"
    description: "Sample user data for development"

  - name: dev_events
    source: parquet
    uri: "../dev-datasets/events-2024-sample.parquet"
    description: "Sample events from dev datasets"

  - name: mock_reference
    source: parquet
    uri: "reference/mock-lookup-tables.parquet"
    description: "Mock reference data for testing"
```

### Production Configuration

```yaml
# config-prod.yaml
version: 1

duckdb:
  database: "${env:PROD_DB_PATH:/var/data/analytics-prod.duckdb}"

views:
  - name: prod_users
    source: parquet
    uri: "data/users.parquet"  # Same relative structure
    description: "Production user data"

  - name: prod_events
    source: parquet
    uri: "../production-datasets/events/full-events.parquet"  # Different relative target
    description: "Full production events dataset"

  - name: prod_reference
    source: parquet
    uri: "reference/production-lookup-tables.parquet"  # Different reference data
    description: "Production reference tables"
```

## Error Handling Examples

### Configuration with Built-in Redundancy

```yaml
version: 1

duckdb:
  database: resilient-analytics.duckdb

views:
  - name: primary_data
    source: parquet
    uri: "data/primary-dataset.parquet"
    description: "Primary data source"

  - name: backup_data
    source: parquet
    uri: "../backup/primary-dataset.parquet"
    description: "Backup data source (same schema)"

  - name: fallback_metric
    sql: |
      SELECT 
        COALESCE(p.user_count, b.user_count) as user_count,
        COALESCE(p.event_count, b.event_count) as event_count,
        CASE
          WHEN p.user_count IS NOT NULL THEN 'primary'
          WHEN b.user_count IS NOT NULL THEN 'backup'
          ELSE 'no_data'
        END as data_source
      FROM (
        SELECT COUNT(DISTINCT user_id) as user_count, COUNT(*) as event_count
        FROM primary_data
      ) p
      FULL OUTER JOIN (
        SELECT COUNT(DISTINCT user_id) as user_count, COUNT(*) as event_count
        FROM backup_data
      ) b ON 1=1
    description: "Resilient metrics with fallback to backup"
```

## Migration Examples

### Legacy Absolute Path Migration

**Legacy Configuration:**
```yaml
# Before migration
version: 1

duckdb:
  database: "/opt/analytics/analytics.duckdb"

views:
  - name: users
    source: parquet
    uri: "/opt/analytics/data/users.parquet"

  - name: events
    source: parquet
    uri: "/opt/analytics/data/events/*.parquet"
```

**Migrated Configuration:**
```yaml
# After migration to relative paths
version: 1

duckdb:
  database: "analytics.duckdb"  # Relative to config location

views:
  - name: users
    source: parquet
    uri: "data/users.parquet"  # Relative to config directory

  - name: events
    source: parquet
    uri: "data/events/*.parquet"  # Relative pattern
```

## Validation and Testing Examples

### Configuration with Test and Production Sections

```yaml
version: 1

duckdb:
  database: "testable-analytics.duckdb"

# Development/testing views
views:
  - name: test_users_sample
    source: parquet
    uri: "data/test/users-small.parquet"
    description: "Small sample for testing"

  - name: test_events_sample
    source: parquet
    uri: "data/test/events-sample.parquet"
    description: "Sample events for testing"

  # Production views (same structure, different data)
  - name: prod_users
    source: parquet
    uri: "data/production/users.parquet"
    description: "Production user data"

  - name: prod_events
    source: parquet
    uri: "data/production/events/*.parquet"
    description: "Production events"

  # Validation view to test data integrity
  - name: validate_data_quality
    sql: |
      SELECT 
        'test_users_sample' as data_source,
        COUNT(*) as total_count,
        COUNT(DISTINCT user_id) as unique_users,
        MIN(CASE WHEN user_id IS NULL THEN 1 END) as null_user_ids
      FROM test_users_sample
      
      UNION ALL
      
      SELECT 
        'prod_users' as data_source,
        COUNT(*) as total_count,
        COUNT(DISTINCT user_id) as unique_users,
        MIN(CASE WHEN user_id IS NULL THEN 1 END) as null_user_ids
      FROM prod_users
    description: "Data quality validation across environments"
```

These configuration examples demonstrate how to use path resolution effectively in various scenarios, from simple projects to complex multi-team environments.