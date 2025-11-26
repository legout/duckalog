# Path Resolution Examples

This document provides practical examples of how path resolution works in Duckalog configurations, showing both the problem that path resolution solves and the solutions it enables.

## Basic Path Resolution Examples

### Example 1: Simple Relative Paths

**Project Structure:**
```
my-analytics/
├── catalog.yaml
└── data/
    ├── users.parquet
    └── events.parquet
```

**Configuration (`catalog.yaml`):**
```yaml
version: 1

duckdb:
  database: analytics.duckdb

views:
  - name: users
    source: parquet
    uri: "data/users.parquet"  # Resolves to: /path/to/my-analytics/data/users.parquet
    description: "User data"

  - name: events
    source: parquet
    uri: "./data/events.parquet"  # Resolves to: /path/to/my-analytics/data/events.parquet
    description: "Event data"
```

**Result:**
- Can run `duckalog build` from any directory
- Paths consistently resolve to files relative to `catalog.yaml`
- Works on Windows, macOS, and Linux

### Example 2: Parent Directory Traversal

**Project Structure:**
```
projects/
├── shared-data/
│   ├── reference/
│   │   ├── lookup-tables.parquet
│   │   └── geographies.parquet
│   └── external/
│       └── third-party-data.parquet
│
├── customer-analytics/
│   ├── catalog.yaml
│   └── queries/
│       └── customer-metrics.sql
│
└── product-analytics/
    ├── catalog.yaml
    └── reports/
        └── product-performance.sql
```

**Customer Analytics Configuration (`customer-analytics/catalog.yaml`):**
```yaml
version: 1

duckdb:
  database: customer_analytics.duckdb

views:
  - name: shared_lookup
    source: parquet
    uri: "../shared-data/reference/lookup-tables.parquet"
    description: "Shared lookup tables"

  - name: geographies
    source: parquet
    uri: "../shared-data/reference/geographies.parquet"
    description: "Geographic reference data"

  - name: external_data
    source: parquet
    uri: "../shared-data/external/third-party-data.parquet"
    description: "External third-party data"
```

**Result:**
- Both projects can access shared data using relative paths
- Teams can work independently while sharing reference data
- No absolute paths hardcoded in configurations

### Example 3: Mixed Absolute and Relative Paths

**Configuration:**
```yaml
version: 1

duckdb:
  database: analytics.duckdb

# Attachments with mixed path types
attachments:
  duckdb:
    - alias: local_reference
      path: "reference/local.duckdb"  # Relative path
      read_only: true
    
    - alias: corporate_reference
      path: "/data/reference/corporate.duckdb"  # Absolute path (for shared resources)
      read_only: true

views:
  # Local data using relative paths
  - name: local_events
    source: parquet
    uri: "data/events.parquet"
    description: "Local event data"

  # Corporate data using absolute paths
  - name: corporate_users
    source: parquet
    uri: "/data/corporate/users/calendar-2024/*.parquet"
    description: "Corporate user data"

  # Remote data (not modified by path resolution)
  - name: cloud_data
    source: parquet
    uri: "s3://company-bucket/analytics/*.parquet"
    description: "Cloud data via S3"
```

## Cross-Platform Examples

### Example 4: Cross-Platform Development

**Configuration (works on all platforms):**
```yaml
version: 1

duckdb:
  database: cross-platform.duckdb

views:
  # Use forward slashes for cross-platform compatibility
  - name: users_mac_windows_linux
    source: parquet
    uri: "data/users.parquet"  # ✅ Works on macOS, Windows, Linux
    description: "Cross-platform user data"

  # Avoid platform-specific patterns
  - name: not_recommended
    source: parquet
    uri: "data\\users.parquet"  # ❌ Windows-specific
    description: "Windows-only path pattern"
```

**Result:**
- Same configuration works across development environments
- Teams with mixed OS setups can share configurations
- Forward slashes provide maximum compatibility

## Environment Variable Integration

### Example 5: Environment Variables with Path Resolution

**Configuration:**
```yaml
version: 1

duckdb:
  database: "${env:PROJECT_NAME:analytics}.duckdb"

attachments:
  duckdb:
    - alias: reference
      path: "${env:REFERENCE_PATH:./reference.duckdb}"
      read_only: true

views:
  - name: data
    source: parquet
    uri: "${env:DATA_DIR:data}/*.parquet"
    description: "Data from configurable directory"
```

**Usage Scenarios:**

```bash
# Development (default values work)
duckalog build catalog.yaml
# resolves: uri="data/*.parquet", path="./reference.duckdb"

# Production (override paths)
export DATA_DIR=/var/data/production
export REFERENCE_PATH=/var/reference/production
export PROJECT_NAME=prod_analytics

duckalog build catalog.yaml
# resolves: uri="/var/data/production/*.parquet", path="/var/reference/production/production.duckdb"
```

## Security Examples

### Example 6: Security Validation in Action

**Configuration with Security Issues:**
```yaml
version: 1

duckdb:
  database: security-test.duckdb

views:
  # ✅ Safe relative paths
  - name: safe_relative
    source: parquet
    uri: "data/users.parquet"
    description: "Safe relative path"

  - name: safe_parent_traversal
    source: parquet
    uri: "../shared/data.parquet"
    description: "Reasonable parent traversal"

  # ❌ Blocked for security
  - name: excessive_traversal
    source: parquet
    uri: "../../../../etc/passwd"
    description: "Blocked: excessive parent traversal"

  # ❌ Blocked for security
  - name: dangerous_system_path
    source: parquet
    uri: "/etc/passwd"
    description: "Blocked: dangerous system path"
```

**Validation Result:**
```bash
$ duckalog validate catalog.yaml
❌ Config error: Path resolution violates security rules: '../..//../../etc/passwd' resolves to '/etc/passwd' which is outside reasonable bounds

# Safe paths:
# ✅ "data/users.parquet" → /project/data/users.parquet
# ✅ "../shared/data.parquet" → /shared/data.parquet
# ❌ "../../../../etc/passwd" → BLOCKED
```

## Real-World Scenarios

### Example 7: Data Lake Integration

**Organization Structure:**
```
company/
├── data-lake/
│   ├── raw/
│   │   ├── events/
│   │   └── users/
│   ├── processed/
│   │   ├── daily/
│   │   └── weekly/
│   └── reference/
│       ├── geographies/
│       └── products/
│
├── analytics/
│   ├── marketing/
│   │   ├── catalog.yaml
│   │   └── metrics/
│   └── finance/
│       ├── catalog.yaml
│       └── reports/
│
└── dashboards/
    ├── kpi/
    └── segment/
```

**Marketing Analytics Configuration (`analytics/marketing/catalog.yaml`):**
```yaml
version: 1

duckdb:
  database: marketing_analytics.duckdb
  install_extensions:
    - parquet

views:
  # Raw event data
  - name: raw_events
    source: parquet
    uri: "../../data-lake/raw/events/*.parquet"
    description: "Raw marketing events"

  # Processed data
  - name: daily_metrics
    source: parquet
    uri: "../../data-lake/processed/daily/metrics/*.parquet"
    description: "Daily processed metrics"

  # Reference data
  - name: product_reference
    source: parquet
    uri: "../../data-lake/reference/products/*.parquet"
    description: "Product reference data"

  # Derived analytics views
  - name: campaign_performance
    sql: |
      SELECT
        campaign_id,
        event_date,
        COUNT(*) as impressions,
        COUNT(DISTINCT user_id) as unique_users,
        SUM(CASE WHEN event_type = 'conversion' THEN 1 ELSE 0 END) as conversions
      FROM raw_events
      WHERE event_date >= CURRENT_DATE - INTERVAL '90 days'
      GROUP BY campaign_id, event_date
    description: "Marketing campaign performance"
```

### Example 8: CI/CD Pipeline Integration

**GitHub Actions Workflow:**
```yaml
name: Validate and Build Catalogs

on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v3
      with:
        python-version: '3.9'
    
    - name: Install duckalog
      run: pip install duckalog
    
    - name: Validate configurations
      run: |
        # Validate from project directory
        duckalog validate analytics/marketing/catalog.yaml
        duckalog validate analytics/finance/catalog.yaml
        
        # Validate from different working directory (tests path resolution)
        cd /tmp
        duckalog validate ${{ github.workspace }}/analytics/marketing/catalog.yaml
        
    - name: Show resolved paths
      run: |
        # Show how paths are resolved (useful for debugging)
        duckalog show-paths analytics/marketing/catalog.yaml
    
    - name: Build catalogs
      run: |
        # Build to test actual path resolution
        duckalog build analytics/marketing/catalog.yaml --dry-run > marketing.sql
        duckalog build analytics/finance/catalog.yaml --dry-run > finance.sql
```

## Migration Examples

### Example 9: From Absolute to Relative

**Before (Absolute Paths):**
```yaml
# Project structure:
# /home/user/projects/analytics/
# ├── catalog.yaml
# └── data/
#     ├── users.parquet
#     └── events.parquet

version: 1

duckdb:
  database: analytics.duckdb

views:
  - name: users
    source: parquet
    uri: "/home/user/projects/analytics/data/users.parquet"  # Hardcoded absolute path
    description: "User data"

  - name: events
    source: parquet
    uri: "/home/user/projects/analytics/data/events.parquet"  # Hardcoded absolute path
    description: "Event data"
```

**After (Relative Paths - Recommended):**
```yaml
version: 1

duckdb:
  database: analytics.duckdb

views:
  - name: users
    source: parquet
    uri: "data/users.parquet"  # Relative to config file
    description: "User data"

  - name: events
    source: parquet
    uri: "data/events.parquet"  # Relative to config file
    description: "Event data"
```

### Example 10: Migration Benefits

**Old Workflow (Absolute Paths):**
```bash
# Only works from specific directory
cd /home/user/projects/analytics
duckalog build catalog.yaml

# Fails from other directories
cd /tmp
duckalog build /home/user/projects/analytics/catalog.yaml
# ❌ Error: /home/user/projects/analytics/data/users.parquet not accessible from /tmp
```

**New Workflow (Relative Paths):**
```bash
# Works from any directory
duckalog build /home/user/projects/analytics/catalog.yaml

cd /tmp
duckalog build /home/user/projects/analytics/catalog.yaml
# ✅ Success: Paths resolve correctly regardless of working directory

# CI/CD friendly
docker run --rm -v /home/user/projects:/data analytics-runner duckalog build /data/analytics/catalog.yaml
```

## Troubleshooting Examples

### Example 11: Debugging Path Issues

**Configuration with Issues:**
```yaml
version: 1

duckdb:
  database: debug-example.duckdb

views:
  - name: missing_file
    source: parquet
    uri: "data/missing.parquet"
    description: "File doesn't exist"

  - name: wrong_case
    source: parquet
    uri: "data/Users.parquet"  # Wrong case on macOS/Linux
    description: "Case sensitivity issue"
```

**Debug Commands:**
```bash
# Show resolved paths to debug issues
$ duckalog show-paths catalog.yaml
Configuration: catalog.yaml
Config directory: /Users/volker/coding/libs/duckalog/debug-example

View Paths:
--------------------------------------------------------------------------------
missing_file:
  Original: data/missing.parquet
  Resolved: /Users/volker/coding/libs/duckalog/debug-example/data/missing.parquet

wrong_case:
  Original: data/Users.parquet
  Resolved: /Users/volker/coding/libs/duckalog/debug-example/data/Users.parquet

# Check file accessibility
$ duckalog validate-paths catalog.yaml --check
✅ Configuration is valid.

Checking file accessibility...
--------------------------------------------------
❌ missing_file: File does not exist: /Users/volker/coding/libs/duckalog/debug-example/data/missing.parquet
❌ wrong_case: File does not exist: /Users/volker/coding/libs/duckalog/debug-example/data/Users.parquet

❌ Found 2 inaccessible files:
  - missing_file: File does not exist: /Users/volker/coding/libs/duckalog/debug-example/data/missing.parquet
  - wrong_case: File does not exist: /Users/volker/coding/libs/duckalog/debug-example/data/Users.parquet
```

These examples demonstrate the practical benefits of path resolution and provide patterns for different use cases and scenarios.