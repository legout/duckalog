# SQL Files and Templates Example

This example demonstrates how to use external SQL files and parameterized SQL templates in Duckalog configurations.

## Overview

The example shows three different approaches to defining SQL in your catalog:

1. **Inline SQL**: Traditional SQL embedded directly in the YAML configuration
2. **SQL File Reference**: External SQL files loaded and inlined at configuration time
3. **SQL Template**: Parameterized SQL files with variable substitution

## Business Scenario

This example uses a simple e-commerce scenario with users and orders:

- **Users table**: Contains user information with status tracking
- **Orders table**: Contains order information with dates and amounts

## Configuration Structure

### Inline SQL View (Baseline)
```yaml
- name: top_customers
  description: "Top customers by revenue"
  sql: |
    SELECT 
      customer_id,
      SUM(amount) as total_revenue,
      COUNT(*) as order_count
    FROM orders
    GROUP BY customer_id
    ORDER BY total_revenue DESC
    LIMIT 100
```

### External SQL File
```yaml
- name: active_users
  description: "Users who are currently active"
  sql_file:
    path: "sql/active_users.sql"
```

### Parameterized SQL Template
```yaml
- name: recent_orders
  description: "Orders from the last 30 days"
  sql_template:
    path: "sql/recent_orders_template.sql"
    variables:
      days_back: 30
```

## SQL Files

### Plain SQL File (`sql/active_users.sql`)
```sql
-- Active users query
SELECT 
  user_id,
  username,
  email,
  created_at,
  last_login
FROM users
WHERE status = 'active'
  AND deleted_at IS NULL
ORDER BY last_login DESC;
```

### Template SQL File (`sql/recent_orders_template.sql`)
```sql
-- Recent orders template
SELECT 
  order_id,
  customer_id,
  order_date,
  total_amount,
  status
FROM orders
WHERE order_date >= CURRENT_DATE - INTERVAL '{{days_back}}' days
  AND status != 'cancelled'
ORDER BY order_date DESC;
```

## How It Works

1. **Configuration Loading**: When you load the catalog with `load_config()`, the system:
   - Reads the YAML configuration
   - Loads external SQL files referenced in `sql_file` and `sql_template`
   - Processes templates by substituting `{{variable}}` placeholders
   - Inlines all SQL content into the final configuration

2. **Template Variables**: The `sql_template` feature supports:
   - Variable substitution using `{{variable_name}}` syntax
   - Any data type (converted to strings automatically)
   - Validation that all required variables are provided

3. **Path Resolution**: SQL file paths are:
   - Resolved relative to the configuration file directory
   - Validated for security (no directory traversal)
   - Supported for both local files and remote URIs

## Running the Example

### 1. Load and Validate Configuration
```bash
# Test configuration loading
python3 -c "
import sys
sys.path.insert(0, '../..')
from pathlib import Path
from duckalog import load_config

config = load_config('catalog.yaml')
print(f'✓ Loaded {len(config.views)} views')
for view in config.views:
    print(f'  - {view.name}: {view.description}')
"
```

### 2. Build DuckDB Catalog
```bash
# Build the catalog (requires DuckDB)
duckalog build catalog.yaml --output=catalog.duckdb
```

### 3. Query the Results
```bash
# Connect and query
duckalog query catalog.duckdb "SELECT COUNT(*) as user_count FROM active_users"
duckalog query catalog.duckdb "SELECT COUNT(*) as order_count FROM recent_orders"
```

## Key Benefits

1. **Separation of Concerns**: Keep SQL logic separate from configuration metadata
2. **Editor Support**: Use your favorite SQL editor with syntax highlighting
3. **Reusability**: Share SQL files across multiple views and projects
4. **Maintainability**: Update SQL logic without touching YAML configuration
5. **Templates**: Create parameterized queries for different scenarios

## Advanced Usage

### Multiple Template Variables
```yaml
- name: filtered_report
  sql_template:
    path: "sql/custom_report.sql"
    variables:
      start_date: "2023-01-01"
      end_date: "2023-12-31"
      region: "US"
      min_amount: 100.00
```

### Remote SQL Files
```yaml
- name: shared_query
  sql_file:
    path: "s3://company-bucket/sql/shared_queries.sql"
```

## Error Handling

The system provides clear error messages for common issues:

- **Missing SQL files**: `SQLFileNotFoundError` with resolved path
- **Invalid templates**: `SQLTemplateError` listing missing variables
- **Security violations**: `SQLFileError` for path traversal attempts
- **Permission errors**: `SQLFilePermissionError` for unreadable files

## Next Steps

- Explore the [`02-intermediate/02-external-sql-files/`](../02-intermediate/02-external-sql-files/) example for more complex scenarios
- Check the [template processing documentation](../../docs/templates.md) for advanced features
- Review the [SQL file security guide](../../docs/sql-file-security.md) for production deployment