# Best Practices: Path Management in Duckalog

This guide provides comprehensive best practices for managing paths in Duckalog configurations to ensure security, portability, maintainability, and cross-platform compatibility.

## Executive Summary

- **Use relative paths** for local data files
- **Organize data logically** relative to your configuration
- **Validate path accessibility** regularly
- **Implement security boundaries** with reasonable limits
- **Consider cross-platform compatibility** in all paths
- **Use environment variables** for external dependencies

## Path Strategy

### ✅ Recommended: Relative-First Approach

```yaml
# Recommended structure
version: 1

duckdb:
  database: analytics.duckdb

views:
  - name: users
    source: parquet
    uri: "data/users.parquet"  # ✅ Relative - portable and predictable
    
  - name: events
    source: parquet
    uri: "../shared/events/*.parquet"  # ✅ Reasonable parent traversal
    
  - name: cloud_backup
    source: parquet
    uri: "s3://company-bucket/data/*.parquet"  # ✅ Remote URI unchanged
```

**Benefits:**
- ✅ Works from any working directory
- ✅ Portable across development environments
- ✅ Easy to version control and share
- ✅ Clear project structure

### ❌ Avoid: Absolute Path Dependencies

```yaml
# Anti-pattern
version: 1

duckdb:
  database: "/opt/analytics/analytics.duckdb"  # ❌ Hardcoded absolute path

views:
  - name: users
    source: parquet
    uri: "/home/user/project/data/users.parquet"  # ❌ User-specific path
    
  - name: events
    source: parquet
    uri: "C:\\Projects\\Analytics\\Data\\events.parquet"  # ❌ Windows-specific
```

**Problems:**
- ❌ Fails when run from different working directories
- ❌ Not portable across environments
- ❌ Breaks in CI/CD pipelines
- ❌ Team coordination required

## Project Organization Structure

### Recommended Directory Layout

```
project-root/
├── README.md
├── catalog.yaml              # Main configuration file
├── requirements.txt
├── .gitignore
│
├── data/                     # Local data files
│   ├── raw/                  # Raw data sources
│   │   ├── users.parquet
│   │   ├── events/
│   │   └── transactions.parquet
│   ├── processed/            # Processed/transformed data
│   │   ├── daily/
│   │   └── weekly/
│   └── reference/            # Reference/lookup data
│       ├── geographies.parquet
│       └── product-catalog.parquet
│
├── reference/                # Reference databases
│   ├── lookup-dbs/
│   └── external-references/
│
├── sql/                      # SQL files for complex views
│   ├── views/
│   └── procedures/
│
├── notebooks/                # Jupyter notebooks (optional)
├── scripts/                  # Utility scripts
└── tests/                    # Test files
```

### Configuration Mapping

```yaml
version: 1

duckdb:
  database: "analytics.duckdb"

attachments:
  # Local reference databases
  duckdb:
    - alias: lookups
      path: "reference/lookup-dbs/main-reference.duckdb"
      read_only: true

views:
  # Raw data sources
  - name: raw_users
    source: parquet
    uri: "data/raw/users.parquet"

  - name: raw_events
    source: parquet
    uri: "data/raw/events/*.parquet"

  # Processed data
  - name: daily_metrics
    source: parquet
    uri: "data/processed/daily/*.parquet"

  # Reference data
  - name: geographies
    source: parquet
    uri: "data/reference/geographies.parquet"

  # Complex views using reference data
  - name: enriched_users
    sql: |
      SELECT u.*, g.country_name, g.region
      FROM raw_users u
      LEFT JOIN lookups.geographic_reference g ON u.geo_id = g.id
```

## Cross-Platform Compatibility

### Use Forward Slash Separators

```yaml
# ✅ Cross-platform compatible
views:
  - name: data_files
    source: parquet
    uri: "data/subdirectory/files.parquet"

# ❌ Windows-only (not recommended)
views:
  - name: windows_files
    source: parquet
    uri: "data\\subdirectory\\files.parquet"
```

### Avoid Platform-Specific Patterns

```yaml
# ✅ Platform-agnostic
attachments:
  duckdb:
    - alias: reference
      path: "reference/data.duckdb"

# ❌ Platform-specific
attachments:
  duckdb:
    - alias: reference
      path: "C:\\Data\\reference\\data.duckdb"  # Windows only
      path: "/var/data/reference/data.duckdb"   # Unix only
```

### Environment-Specific Paths

```yaml
# ✅ Flexible with environment variables
version: 1

duckdb:
  database: "${env:DB_PATH:analytics.duckdb}"

attachments:
  duckdb:
    - alias: reference
      path: "${env:REF_PATH:./reference.duckdb}"
      read_only: true

views:
  - name: data
    source: parquet
    uri: "${env:DATA_DIR:data}/*.parquet"
```

## Security Best Practices

### Security-First Path Design

```yaml
# ✅ Secure path patterns
views:
  - name: safe_local_data
    source: parquet
    uri: "data/safe-data.parquet"  # Within project bounds

  - name: safe_shared_data
    source: parquet
    uri: "../shared/safe-data.parquet"  # Reasonable parent traversal

  - name: remote_secure
    source: parquet
    uri: "s3://secure-company-data/analytics/*.parquet"  # Authenticated remote
```

### Dangerous Patterns to Avoid

```yaml
# ❌ Dangerous anti-patterns
views:
  - name: dangerous_traversal
    source: parquet
    uri: "../../../../etc/passwd"  # ❌ Excessive traversal - BLOCKED

  - name: system_paths
    source: parquet
    uri: "/etc/shadow"  # ❌ System file access - BLOCKED

  - name: wildcard_danger
    source: parquet
    uri: "../../../**/*"  # ❌ Too broad - RISKY
```

### Security Validation

```bash
# Regular security checks
duckalog validate catalog.yaml                    # Basic validation
duckalog validate-paths catalog.yaml --verbose   # Full path security check
```

## Team Collaboration Guidelines

### Standardize Path Conventions

```yaml
# Team-wide standard conventions
version: 1

duckdb:
  database: "{team}-{project}.duckdb"  # Template naming

views:
  # Naming convention: {data_type}_{source}_{timeframe}
  - name: raw_events_prod_2024
    source: parquet
    uri: "data/raw/events/production/2024/*.parquet"

  - name: processed_metrics_daily
    source: parquet
    uri: "data/processed/metrics/daily/*.parquet"
```

### Documentation Standards

```yaml
# Include path documentation for team clarity
version: 1

views:
  - name: customer_data
    source: parquet
    uri: "data/customers/current/*"
    description: |
      Current customer data from CRM system.
      Updated daily via ETL pipeline.
      Location: data/customers/current/
      Owner: data-engineering-team
      SLA: Updated by 06:00 UTC daily

  - name: external_reference
    source: parquet
    uri: "../shared/reference/geographies.parquet"
    description: |
      Shared geographic reference data maintained by data governance team.
      Location: ../shared/reference/
      Contact: data-governance@company.com
      Update frequency: Weekly
```

## Performance Optimization

### Organize for Query Performance

```yaml
# Optimized data layout for performance
version: 1

views:
  # Partitioned data for efficient querying
  - name: partitioned_events
    source: parquet
    uri: "data/events/by-date/year=*/month=*/day=*/*.parquet"
    description: "Events partitioned by date for time-based queries"

  # Pre-aggregated data for common queries
  - name: daily_summary
    source: parquet
    uri: "data/summaries/daily/*.parquet"
    description: "Pre-computed daily summaries for faster dashboard access"

  # Reference data optimized with DuckDB features
  - name: indexed_lookups
    source: parquet
    uri: "data/reference/indexed-tables/*.parquet"
    description: "Reference tables with DuckDB-friendly indexing"
```

### Path-Based Performance Considerations

```yaml
# ✅ Efficient path patterns
views:
  - name: efficient_globbing
    source: parquet
    uri: "data/events/2024-*.parquet"  # ✅ Specific, manageable glob

  - name: targeted_partitions
    source: parquet
    uri: "data/partitions/date=2024-01-*/*.parquet"  # ✅ Hive-style partitions

# ❌ Inefficient or problematic patterns
views:
  - name: too_broad
    source: parquet
    uri: "data/**/*"  # ❌ Too broad, performance issues

  - name: deep_wildcard
    source: parquet
    uri: "**/events/**/*.parquet"  # ❌ Excessive recursion
```

## CI/CD Integration

### Configuration for Pipelines

```yaml
# Pipeline-friendly configuration
version: 1

duckdb:
  database: "${env:CATALOG_NAME:ci-test-catalog}.duckdb"

views:
  - name: test_data
    source: parquet
    uri: "data/test/sample-data.parquet"
    description: "Small dataset for pipeline testing"

  - name: production_data
    source: parquet
    uri: "${env:PROD_DATA_PATH:data/production}/*.parquet"
    description: "Production data (environment-specific)"
```

### Pipeline Validation Steps

```yaml
# .github/workflows/validate-catalog.yml
name: Validate Catalog Configuration

on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Setup Python
      uses: actions/setup-python@v3
      with:
        python-version: '3.9'
    
    - name: Install Duckalog
      run: pip install duckalog
    
    - name: Validate Configuration
      run: duckalog validate catalog.yaml
    
    - name: Check Path Accessibility
      run: duckalog validate-paths catalog.yaml
    
    - name: Test from Different Directories
      run: |
        # Test path resolution from different working directories
        cd /tmp
        duckalog validate ${{ github.workspace }}/catalog.yaml
        duckalog show-paths ${{ github.workspace }}/catalog.yaml
```

## Monitoring and Maintenance

### Regular Validation Script

```bash
#!/bin/bash
# validate-all-paths.sh - Regular path validation

echo "🔍 Validating all catalog configurations..."

# Find all catalog files
find . -name "catalog*.yaml" -o -name "catalog*.yml" | while read catalog; do
    echo ""
    echo "📋 Validating: $catalog"
    
    if duckalog validate "$catalog"; then
        echo "✅ Configuration valid"
        
        # Check path accessibility
        if duckalog validate-paths "$catalog"; then
            echo "✅ All paths accessible"
        else
            echo "❌ Path issues detected"
        fi
    else
        echo "❌ Configuration invalid"
    fi
done

echo ""
echo "🏁 Validation complete"
```

### Documentation Maintenance

```yaml
# Include version and last updated information
version: 1

# Metadata for tracking and maintenance
metadata:
  config_version: "1.2"
  last_updated: "2024-01-15"
  updated_by: "data-engineering-team"
  environment: "production"

views:
  - name: critical_data
    source: parquet
    uri: "data/critical/current-data.parquet"
    metadata:
      importance: "critical"
      sla: "99.9% uptime"
      owner: "data-platform-team"
      last_verified: "2024-01-15"
```

## Migration Strategies

### Incremental Migration Path

```yaml
# Phase 1: Keep both old and new paths
version: 1

views:
  - name: data_v1_legacy  # Legacy absolute path
    source: parquet
    uri: "/opt/data/legacy/users.parquet"
    description: "Legacy path for backward compatibility"

  - name: data_v2_new     # New relative path
    source: parquet
    uri: "data/users.parquet"
    description: "New relative path for future use"

# Phase 2: Migration verification
views:
  - name: data_comparison  # Verify both sources match
    sql: |
      SELECT
        COUNT(*) as legacy_count,
        (SELECT COUNT(*) FROM data_v2_new) as new_count
      FROM data_v1_legacy
    description: "Verify migration between legacy and new data sources"

# Phase 3: Transition to relative paths only
views:
  - name: users_final     # Final relative path only
    source: parquet
    uri: "data/users.parquet"
    description: "Final configuration using relative paths only"
```

## Troubleshooting Common Issues

### Path Not Found Debugging

```bash
# Step 1: Show resolved paths
duckalog show-paths catalog.yaml --check

# Step 2: Check file existence manually
ls -la resolved/path/to/file.parquet

# Step 3: Verify working directory context
pwd
cat catalog.yaml | grep uri
```

### Cross-Platform Issues

```yaml
# Problem: Windows path separators
uri: "data\\subdir\\file.parquet"  # ❌ May fail on macOS/Linux

# Solution: Use forward slashes
uri: "data/subdir/file.parquet"    # ✅ Works everywhere
```

### Environment Variable Issues

```bash
# Debug environment variables
echo $DATA_DIR
echo $DB_PATH

# Test with defaults
duckalog validate catalog.yaml  # Uses defaults if variables not set
```

## Tooling and Automation

### Path Validation Automation

```python
# scripts/validate_paths.py
import sys
from pathlib import Path
from duckalog.config import load_config
from duckalog.path_resolution import validate_file_accessibility

def validate_catalog_paths(catalog_path):
    """Validate all file paths in a catalog configuration."""
    try:
        config = load_config(str(catalog_path))
        issues = []
        
        for view in config.views:
            if view.uri and view.source in ('parquet', 'delta'):
                is_accessible, error = validate_file_accessibility(view.uri)
                if not is_accessible:
                    issues.append((view.name, view.uri, error))
        
        return issues
    except Exception as e:
        return [("config_error", str(catalog_path), str(e))]

if __name__ == "__main__":
    catalog_path = Path(sys.argv[1])
    issues = validate_catalog_paths(catalog_path)
    
    if issues:
        print("❌ Path validation failed:")
        for name, path, error in issues:
            print(f"  {name}: {error}")
        sys.exit(1)
    else:
        print("✅ All paths valid")
```

### Configuration Health Check

```bash
# scripts/health-check.sh
#!/bin/bash

echo "🏥 Catalog Health Check"
echo "======================="

# List all catalogs
catalogs=$(find . -name "catalog*.yaml" -o -name "catalog*.yml")

for catalog in $catalogs; do
    echo ""
    echo "📋 Checking: $catalog"
    
    # Basic validation
    if duckalog validate "$catalog" 2>/dev/null; then
        echo "  ✅ Valid configuration"
    else
        echo "  ❌ Invalid configuration"
        continue
    fi
    
    # Path validation
    if duckalog validate-paths "$catalog" 2>/dev/null; then
        echo "  ✅ All paths accessible"
    else
        echo "  ❌ Path accessibility issues"
    fi
    
    # Show resolved paths (for inspection)
    echo "  📁 Path resolution:"
    duckalog show-paths "$catalog" | grep "Resolved:" | head -3 | while read line; do
        echo "      $line"
    done
done
```

These best practices ensure your Duckalog configurations are secure, maintainable, portable, and performant across all environments and use cases.