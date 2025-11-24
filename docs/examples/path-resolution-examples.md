# Path Resolution Examples

This section provides practical examples of using Duckalog's path resolution feature in various scenarios.

## Example 1: Basic Project Structure

### Project Layout

```
data-analytics/
├── config/
│   └── catalog.yaml
├── data/
│   ├── raw/
│   │   ├── events.parquet
│   │   └── users.parquet
│   ├── processed/
│   │   ├── daily_metrics.parquet
│   │   └── user_segments.parquet
│   └── external/
│       └── reference_data.parquet
└── databases/
    └── reference.duckdb
```

### Configuration (`config/catalog.yaml`)

```yaml
version: 1

duckdb:
  database: catalog.duckdb
  pragmas:
    - "SET memory_limit='2GB'"

attachments:
  duckdb:
    - alias: refdb
      path: ../databases/reference.duckdb
      read_only: true

views:
  # Raw data files
  - name: raw_events
    source: parquet
    uri: ../data/raw/events.parquet
    description: "Raw event data from production"
    
  - name: raw_users
    source: parquet
    uri: ../data/raw/users.parquet
    description: "Raw user data"
    
  # Processed data files
  - name: daily_metrics
    source: parquet
    uri: ../data/processed/daily_metrics.parquet
    description: "Daily aggregated metrics"
    
  - name: user_segments
    source: parquet
    uri: ../data/processed/user_segments.parquet
    description: "User segmentation data"
    
  # External reference data
  - name: external_reference
    source: parquet
    uri: ../data/external/reference_data.parquet
    description: "External reference data"
    
  # Data from attached database
  - name: reference_customers
    source: duckdb
    database: refdb
    table: customers
    description: "Customer reference data"
    
  # Combined analytics view
  - name: analytics_dashboard
    sql: |
      SELECT 
        u.user_id,
        u.name,
        u.email,
        us.segment_name,
        dm.event_date,
        dm.total_events,
        dm.unique_users
      FROM raw_users u
      LEFT JOIN user_segments us ON u.user_id = us.user_id
      LEFT JOIN daily_metrics dm ON u.segment_id = dm.segment_id
      WHERE dm.event_date >= CURRENT_DATE - INTERVAL 30 DAYS
```

### Loading with Path Resolution

```python
from duckalog import load_config, generate_sql

# Load configuration with automatic path resolution
config = load_config("config/catalog.yaml")

print(f"Loaded config with {len(config.views)} views")

# Verify paths were resolved
for view in config.views:
    if hasattr(view, 'uri') and view.uri:
        print(f"View: {view.name}")
        print(f"  URI: {view.uri}")
        print(f"  Is absolute: {view.uri.startswith('/')}")
```

## Example 2: Multi-Environment Configuration

### Development vs Production

**Development Structure:**
```
dev-project/
├── config/
│   ├── catalog.yaml
│   └── catalog-dev.yaml
├── data/
│   ├── sample/
│   │   └── events.parquet
│   └── testing/
│       └── users.parquet
└── databases/
    └── dev_reference.duckdb
```

**Production Structure:**
```
prod-project/
├── config/
│   ├── catalog.yaml
│   └── catalog-prod.yaml
├── data/
│   ├── live/
│   │   └── events.parquet
│   └── archive/
│       └── users.parquet
└── databases/
    └── prod_reference.duckdb
```

### Development Configuration (`dev-project/config/catalog.yaml`)

```yaml
version: 1

duckdb:
  database: dev_catalog.duckdb
  pragmas:
    - "SET memory_limit='1GB'"

attachments:
  duckdb:
    - alias: refdb
      path: ../databases/dev_reference.duckdb
      read_only: true

views:
  - name: dev_events
    source: parquet
    uri: ../data/sample/events.parquet
    description: "Development sample events"
    
  - name: dev_users
    source: parquet
    uri: ../data/testing/users.parquet
    description: "Development test users"
```

### Production Configuration (`prod-project/config/catalog.yaml`)

```yaml
version: 1

duckdb:
  database: prod_catalog.duckdb
  pragmas:
    - "SET memory_limit='8GB'"
    - "SET threads=8"

attachments:
  duckdb:
    - alias: refdb
      path: ../databases/prod_reference.duckdb
      read_only: true

views:
  - name: prod_events
    source: parquet
    uri: ../data/live/events.parquet
    description: "Production live events"
    
  - name: prod_users
    source: parquet
    uri: ../data/archive/users.parquet
    description: "Production archived users"
```

### Environment-Aware Loading

```python
import os
from duckalog import load_config

def load_environment_config(base_path: str, env: str = "dev"):
    """Load configuration for specific environment"""
    config_path = os.path.join(base_path, f"{env}-project/config/catalog.yaml")
    return load_config(config_path)

# Load development configuration
dev_config = load_environment_config("/path/to/projects", "dev")
print(f"Development config: {dev_config.views[0].uri}")

# Load production configuration  
prod_config = load_environment_config("/path/to/projects", "prod")
print(f"Production config: {prod_config.views[0].uri}")
```

## Example 3: Shared Enterprise Resources

### Enterprise Structure

```
company/
├── shared/
│   ├── reference_data/
│   │   ├── geography.parquet
│   │   ├── currency_rates.parquet
│   │   └── company_calendar.parquet
│   ├── databases/
│   │   ├── enterprise_master.duckdb
│   │   └── analytics_cache.duckdb
│   └── schemas/
│       └── standard_views.sql
├── analytics/
│   ├── config/
│   │   └── catalog.yaml
│   ├── data/
│   │   ├── department_a/
│   │   │   └── metrics.parquet
│   │   └── department_b/
│   │       └── reports.parquet
│   └── sql/
│       └── custom_views.sql
└── finance/
    ├── config/
    │   └── catalog.yaml
    ├── data/
    │   ├── transactions/
    │   │   └── daily.parquet
    │   └── budgets/
    │       └── quarterly.parquet
    └── sql/
        └── financial_views.sql
```

### Analytics Configuration (`company/analytics/config/catalog.yaml`)

```yaml
version: 1

duckdb:
  database: analytics_catalog.duckdb
  pragmas:
    - "SET memory_limit='4GB'"
    - "SET threads=4"

# Attach shared enterprise databases
attachments:
  duckdb:
    - alias: enterprise_master
      path: ../../shared/databases/enterprise_master.duckdb
      read_only: true
    - alias: analytics_cache
      path: ../../shared/databases/analytics_cache.duckdb
      read_only: true

views:
  # Shared enterprise reference data
  - name: geography
    source: parquet
    uri: ../../shared/reference_data/geography.parquet
    description: "Geographic reference data"
    
  - name: currency_rates
    source: parquet
    uri: ../../shared/reference_data/currency_rates.parquet
    description: "Currency exchange rates"
    
  - name: company_calendar
    source: parquet
    uri: ../../shared/reference_data/company_calendar.parquet
    description: "Company calendar with holidays"
    
  # Local department data
  - name: dept_a_metrics
    source: parquet
    uri: ../data/department_a/metrics.parquet
    description: "Department A metrics"
    
  - name: dept_b_reports
    source: parquet
    uri: ../data/department_b/reports.parquet
    description: "Department B reports"
    
  # Views using enterprise database
  - name: enterprise_customers
    source: duckdb
    database: enterprise_master
    table: customers
    description: "Enterprise customer master"
    
  # Combined analytics views
  - name: regional_performance
    sql: |
      SELECT 
        g.region_name,
        g.country_code,
        dm.metric_type,
        dm.metric_value,
        dm.reporting_date
      FROM geography g
      JOIN dept_a_metrics dm ON g.region_id = dm.region_id
      WHERE dm.reporting_date >= CURRENT_DATE - INTERVAL 90 DAYS
    
  - name: budget_vs_actual
    sql: |
      SELECT 
        cc.fiscal_year,
        cc.fiscal_quarter,
        b.budget_amount,
        SUM(dm.metric_value) as actual_amount,
        (SUM(dm.metric_value) - b.budget_amount) as variance
      FROM company_calendar cc
      JOIN dept_b_reports dm ON cc.date_key = dm.reporting_date
      LEFT JOIN (
        SELECT * FROM enterprise_master.finance_budgets
      ) b ON cc.fiscal_quarter = b.quarter AND cc.fiscal_year = b.year
      GROUP BY cc.fiscal_year, cc.fiscal_quarter, b.budget_amount
```

### Finance Configuration (`company/finance/config/catalog.yaml`)

```yaml
version: 1

duckdb:
  database: finance_catalog.duckdb
  pragmas:
    - "SET memory_limit='6GB'"
    - "SET threads=6"

# Attach shared enterprise databases (same as analytics)
attachments:
  duckdb:
    - alias: enterprise_master
      path: ../../shared/databases/enterprise_master.duckdb
      read_only: true

views:
  # Shared enterprise reference data
  - name: currency_rates
    source: parquet
    uri: ../../shared/reference_data/currency_rates.parquet
    description: "Currency exchange rates"
    
  # Finance-specific data
  - name: daily_transactions
    source: parquet
    uri: ../data/transactions/daily.parquet
    description: "Daily transaction data"
    
  - name: quarterly_budgets
    source: parquet
    uri: ../data/budgets/quarterly.parquet
    description: "Quarterly budget data"
    
  # Financial analytics
  - name: transaction_analysis
    sql: |
      SELECT 
        dt.transaction_date,
        dt.customer_id,
        dt.amount,
        dt.currency,
        cr.usd_rate,
        (dt.amount * cr.usd_rate) as amount_usd,
        em.customer_segment
      FROM daily_transactions dt
      JOIN currency_rates cr ON dt.currency = cr.currency_code 
        AND dt.transaction_date = cr.effective_date
      LEFT JOIN enterprise_master.customers em ON dt.customer_id = em.customer_id
      WHERE dt.transaction_date >= CURRENT_DATE - INTERVAL 30 DAYS
```

## Example 4: Cloud and Local Hybrid Setup

### Hybrid Project Structure

```
hybrid-analytics/
├── config/
│   └── catalog.yaml
├── local-data/
│   ├── sensitive/
│   │   └── pii_data.parquet
│   └── cache/
│       └── local_cache.duckdb
├── databases/
│   └── reference.duckdb
└── sql/
    └── views/
```

### Hybrid Configuration (`config/catalog.yaml`)

```yaml
version: 1

duckdb:
  database: hybrid_catalog.duckdb
  pragmas:
    - "SET memory_limit='4GB'"
    - "SET s3_region='us-west-2'"
    - "SET s3_access_key_id='${env:AWS_ACCESS_KEY_ID}'"
    - "SET s3_secret_access_key='${env:AWS_SECRET_ACCESS_KEY}'"

attachments:
  duckdb:
    - alias: refdb
      path: ../databases/reference.duckdb
      read_only: true
    - alias: cache
      path: ../local-data/cache/local_cache.duckdb
      read_only: false  # Allow writing to cache

views:
  # Cloud data (remote URIs - not resolved)
  - name: cloud_events
    source: parquet
    uri: s3://data-lake/raw/events/*.parquet
    description: "Cloud-based raw events"
    
  - name: cloud_users  
    source: parquet
    uri: s3://data-lake/processed/users.parquet
    description: "Cloud-based processed users"
    
  # Local sensitive data (resolved relative paths)
  - name: sensitive_pii
    source: parquet
    uri: ../local-data/sensitive/pii_data.parquet
    description: "Local PII data (not stored in cloud)"
    
  # Local reference data
  - name: local_reference
    source: duckdb
    database: refdb
    table: reference_data
    description: "Local reference database"
    
  # Cache data (read-write attachment)
  - name: cached_results
    source: duckdb
    database: cache
    table: precomputed_metrics
    description: "Locally cached computation results"
    
  # Hybrid views combining cloud and local data
  - name: enhanced_events
    sql: |
      SELECT 
        ce.event_id,
        ce.timestamp,
        ce.event_type,
        ce.properties,
        sp.customer_name,
        sp.email,
        sp.segment,
        lr.internal_category
      FROM cloud_events ce
      LEFT JOIN sensitive_pii sp ON ce.user_id = sp.user_id
      LEFT JOIN local_reference lr ON ce.event_type = lr.event_category
      WHERE ce.timestamp >= CURRENT_DATE - INTERVAL 7 DAYS
    
  # View that updates local cache
  - name: update_cache
    sql: |
      -- Update local cache with latest aggregations
      INSERT OR REPLACE INTO cache.precomputed_metrics
      SELECT 
        DATE(timestamp) as event_date,
        event_type,
        COUNT(*) as event_count,
        COUNT(DISTINCT user_id) as unique_users,
        CURRENT_TIMESTAMP as cache_updated
      FROM cloud_events 
      WHERE timestamp >= CURRENT_DATE - INTERVAL 1 DAY
      GROUP BY DATE(timestamp), event_type
```

## Example 5: Security Demonstration

### Security Test Configuration

```yaml
version: 1

duckdb:
  database: security_test.duckdb

views:
  # ✅ ALLOWED - Safe relative paths
  - name: safe_local_data
    source: parquet
    uri: ./data/local.parquet
    description: "Safe local data"
    
  - name: safe_parent_data
    source: parquet
    uri: ../shared/data.parquet
    description: "Safe parent directory data"
    
  - name: safe_grandparent_data
    source: parquet
    uri: ../../project/common.parquet
    description: "Safe grandparent directory data"
    
  # ✅ ALLOWED - Remote URIs (bypass local file security)
  - name: remote_s3_data
    source: parquet
    uri: s3://secure-bucket/data.parquet
    description: "Remote S3 data"
    
  - name: remote_http_data
    source: parquet
    uri: https://api.example.com/data.parquet
    description: "Remote HTTP data"
    
  # ❌ BLOCKED - Security violations (these would cause errors)
  # Uncommenting these would cause ConfigError during loading
  
  # - name: system_files
  #   source: parquet
  #   uri: ../../../etc/passwd
  #   description: "Blocked - system file access"
    
  # - name: system_config
  #   source: parquet
  #   uri: ../usr/local/config.parquet
  #   description: "Blocked - system directory access"
    
  # - name: excessive_traversal
  #   source: parquet
  #   uri: ../../../../../../../root/.ssh/id_rsa
  #   description: "Blocked - excessive directory traversal"
```

### Security Validation Code

```python
from duckalog import load_config, ConfigError
from duckalog.path_resolution import validate_path_security, is_relative_path
from pathlib import Path

def test_security_examples():
    """Demonstrate security validation"""
    
    config_dir = Path("/project/config")
    
    # Test safe paths
    safe_paths = [
        "./data/local.parquet",
        "../shared/data.parquet", 
        "../../project/common.parquet"
    ]
    
    print("Testing safe paths:")
    for path in safe_paths:
        is_rel = is_relative_path(path)
        is_safe = validate_path_security(path, config_dir)
        print(f"  {path}: relative={is_rel}, safe={is_safe}")
    
    # Test dangerous paths
    dangerous_paths = [
        "../../../etc/passwd",
        "../usr/local/config.parquet",
        "../../../../root/.ssh/id_rsa"
    ]
    
    print("\nTesting dangerous paths:")
    for path in dangerous_paths:
        is_rel = is_relative_path(path)
        is_safe = validate_path_security(path, config_dir)
        print(f"  {path}: relative={is_rel}, safe={is_safe}")

# Run security tests
test_security_examples()

# Test configuration loading with security validation
try:
    config = load_config("security_test_catalog.yaml")
    print("Configuration loaded successfully")
except ConfigError as e:
    print(f"Configuration error: {e}")
```

## Example 6: Programmatic Path Resolution

### Direct Path Resolution Usage

```python
from duckalog.path_resolution import (
    resolve_relative_path,
    validate_path_security,
    detect_path_type,
    normalize_path_for_sql
)
from pathlib import Path

def demonstrate_path_resolution():
    """Demonstrate path resolution functionality"""
    
    config_dir = Path("/project/analytics/config")
    
    # Test different path types
    test_paths = [
        "data/events.parquet",
        "../shared/reference.parquet",
        "/absolute/path/data.parquet",
        "s3://bucket/data.parquet",
        "../../../etc/passwd",  # This should fail security validation
    ]
    
    print("Path Resolution Examples:")
    print("=" * 50)
    
    for path in test_paths:
        print(f"\nOriginal path: {path}")
        
        # Detect path type
        path_type = detect_path_type(path)
        print(f"  Path type: {path_type}")
        
        # Check if relative
        is_rel = is_relative_path(path)
        print(f"  Is relative: {is_rel}")
        
        # Validate security
        try:
            is_safe = validate_path_security(path, config_dir)
            print(f"  Security validation: {'PASS' if is_safe else 'BLOCKED'}")
        except Exception as e:
            print(f"  Security validation: ERROR - {e}")
        
        # Resolve if relative and safe
        if is_rel:
            try:
                resolved = resolve_relative_path(path, config_dir)
                print(f"  Resolved path: {resolved}")
                
                # Normalize for SQL
                sql_path = normalize_path_for_sql(resolved)
                print(f"  SQL format: {sql_path}")
                
            except Exception as e:
                print(f"  Resolution failed: {e}")
        else:
            print(f"  Path unchanged: {path}")

# Run demonstration
demonstrate_path_resolution()

# Example: Building dynamic configuration
def build_dynamic_config(config_file_path: str, data_patterns: dict):
    """Build configuration with dynamic path resolution"""
    
    config_dir = Path(config_file_path).parent
    resolved_views = []
    
    for view_name, path_pattern in data_patterns.items():
        try:
            # Resolve the path pattern
            resolved_path = resolve_relative_path(path_pattern, config_dir)
            
            # Create view with resolved path
            view = {
                "name": view_name,
                "source": "parquet",
                "uri": resolved_path,
                "description": f"Auto-resolved view for {view_name}"
            }
            resolved_views.append(view)
            
        except Exception as e:
            print(f"Failed to resolve {view_name}: {e}")
    
    return {
        "version": 1,
        "duckdb": {"database": "dynamic_catalog.duckdb"},
        "views": resolved_views
    }

# Usage example
data_sources = {
    "raw_events": "../data/events/raw/*.parquet",
    "processed_users": "../data/users/processed.parquet", 
    "reference_data": "./reference/common.parquet"
}

dynamic_config = build_dynamic_config("/project/config/catalog.yaml", data_sources)
print("\nDynamic configuration:")
print(dynamic_config)
```

## Example 7: Migration from Absolute to Relative Paths

### Before: Absolute Paths

```yaml
# old-catalog.yaml
version: 1

duckdb:
  database: /Users/john/projects/analytics/catalog.duckdb

views:
  - name: events
    source: parquet
    uri: /Users/john/projects/analytics/data/events.parquet
    
  - name: users
    source: parquet
    uri: /Users/john/projects/analytics/data/users.parquet

attachments:
  duckdb:
    - alias: refdb
      path: /Users/john/shared/reference.duckdb
      read_only: true
```

### After: Relative Paths

```yaml
# new-catalog.yaml
version: 1

duckdb:
  database: catalog.duckdb

views:
  - name: events
    source: parquet
    uri: ./data/events.parquet
    
  - name: users
    source: parquet
    uri: ./data/users.parquet

attachments:
  duckdb:
    - alias: refdb
      path: ../shared/reference.duckdb
      read_only: true
```

### Migration Script

```python
import yaml
import re
from pathlib import Path
from duckalog.path_resolution import is_relative_path

def migrate_to_relative_paths(config_path: str, base_path: str = None):
    """Migrate absolute paths to relative paths in a configuration file"""
    
    config_path = Path(config_path)
    if base_path is None:
        base_path = config_path.parent
        
    # Load existing configuration
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    # Helper function to convert absolute to relative path
    def to_relative_path(abs_path: str) -> str:
        if not abs_path or not is_relative_path(abs_path):
            try:
                path_obj = Path(abs_path)
                if path_obj.is_absolute():
                    rel_path = path_obj.relative_to(base_path)
                    return str(rel_path)
            except (ValueError, OSError):
                pass
        return abs_path
    
    # Convert database path
    if 'duckdb' in config and 'database' in config['duckdb']:
        config['duckdb']['database'] = to_relative_path(
            config['duckdb']['database']
        )
    
    # Convert view URIs
    if 'views' in config:
        for view in config['views']:
            if 'uri' in view:
                view['uri'] = to_relative_path(view['uri'])
    
    # Convert attachment paths
    if 'attachments' in config:
        for attach_type in ['duckdb', 'sqlite']:
            if attach_type in config['attachments']:
                for attachment in config['attachments'][attach_type]:
                    if 'path' in attachment:
                        attachment['path'] = to_relative_path(attachment['path'])
    
    # Save migrated configuration
    backup_path = config_path.with_suffix('.yaml.backup')
    config_path.rename(backup_path)
    
    with open(config_path, 'w') as f:
        yaml.dump(config, f, default_flow_style=False)
    
    print(f"Configuration migrated to relative paths")
    print(f"Original saved to: {backup_path}")
    print(f"New config: {config_path}")

# Usage
migrate_to_relative_paths("old-catalog.yaml")
```

These examples demonstrate the flexibility and security of Duckalog's path resolution feature across various real-world scenarios. The key benefits are:

1. **Portability**: Configurations can be moved between environments
2. **Security**: Automatic protection against dangerous file access
3. **Maintainability**: Clear relative path structure
4. **Flexibility**: Works with local files, shared resources, and remote URIs
5. **Cross-Platform**: Consistent behavior across operating systems