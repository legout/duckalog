# Change: Add SQL File References Support

## Why

Currently, Duckalog requires SQL queries to be written directly inline within YAML or JSON configuration files. This creates several limitations:

1. **Poor maintainability**: Long SQL queries clutter configuration files and make them hard to read
2. **No syntax highlighting**: SQL in YAML doesn't benefit from SQL-specific syntax highlighting in editors
3. **Version control challenges**: SQL logic gets buried in configuration files, making diffs harder to review
4. **Code reusability**: Same SQL queries can't be easily shared across multiple configurations
5. **Testing difficulties**: SQL queries are harder to test in isolation when embedded in YAML
6. **Developer experience**: Database developers prefer working with `.sql` files with proper tooling support

The current inline approach works for simple queries but becomes unwieldy for complex analytical queries, stored procedures, or multi-statement operations.

## What Changes

- **Add SQL file reference capability**: Allow views to reference external `.sql` files instead of containing inline `sql` content
- **Support multiple reference formats**:
  - `sql_file: "path/to/query.sql"` - Direct file reference
  - `sql_template: "path/to/template.sql"` - Template with variable substitution
  - `sql_directory: "queries/"` - Directory of SQL files for batch operations
- **Maintain backward compatibility**: Existing inline `sql` field continues to work unchanged
- **Add file resolution logic**: Support relative paths (from config file location) and absolute paths
- **Implement variable substitution**: Allow parameters in SQL files to be replaced with values from the config
- **Add validation**: Ensure referenced SQL files exist and contain valid SQL

## Impact

**Benefits:**
- **Improved maintainability**: SQL queries stored in dedicated `.sql` files with proper tooling
- **Better developer experience**: SQL syntax highlighting, linting, and formatting in modern editors
- **Enhanced reusability**: Common SQL patterns can be shared across multiple configurations
- **Easier testing**: SQL files can be tested independently of configuration
- **Cleaner configurations**: YAML/JSON files focus on configuration rather than query logic
- **Better version control**: SQL changes have clearer diffs and commit history

**Considerations:**
- **File management**: Additional files to organize and deploy
- **Path resolution**: Need clear rules for relative vs absolute paths
- **Security**: Ensure SQL file references don't introduce injection vulnerabilities
- **Error handling**: Clear messages when SQL files are missing or invalid

## Technical Details

### Configuration Schema Updates

**New fields for SQL file references:**

```yaml
views:
  - name: view_name
    source: parquet  # or other source types
    uri: "s3://bucket/data/*.parquet"
    # NEW: SQL file reference options (mutually exclusive with sql field)
    sql_file: "queries/user_activity.sql"          # Direct SQL file
    sql_template: "templates/monthly_report.sql"   # Template with variables
    sql_variables:                                  # Variables for template substitution
      table_name: "users"
      date_column: "created_at"
      # OR use environment variables
      env:
        bucket_name: "S3_BUCKET"
        region: "AWS_REGION"
```

**Backward compatibility:**
```yaml
views:
  - name: legacy_view
    source: parquet
    uri: "s3://bucket/data/*.parquet"
    sql: |
      SELECT * FROM table
      WHERE condition = 'value'
    # This continues to work exactly as before
```

### SQL File Format

**Simple SQL file (`queries/user_activity.sql`):**
```sql
SELECT 
  user_id,
  DATE(created_at) as signup_date,
  region,
  COUNT(*) as total_events
FROM events
WHERE event_type = 'signup'
GROUP BY user_id, DATE(created_at), region
ORDER BY signup_date DESC
```

**Template SQL file (`templates/monthly_report.sql`):**
```sql
SELECT 
  DATE_TRUNC('month', {{ date_column }}) as month,
  COUNT(*) as total_records,
  AVG(metric_value) as avg_metric
FROM {{ table_name }}
WHERE {{ date_column }} >= CURRENT_DATE - INTERVAL 12 MONTH
GROUP BY DATE_TRUNC('month', {{ date_column }})
ORDER BY month DESC
```

### File Resolution Logic

1. **Relative paths**: Resolved relative to the configuration file location
2. **Absolute paths**: Used as-is (with security validation)
3. **Path normalization**: Clean up `..`, `.`, and redundant separators
4. **Existence validation**: SQL files must exist and be readable
5. **Size limits**: Prevent excessively large SQL files from causing issues

### Template Variable Substitution

**Supported substitution formats:**
- `{{ variable_name }}` - Direct variable replacement
- `${env:ENV_VAR}` - Environment variable substitution (existing feature)
- `${config:config_path}` - Configuration value substitution

**Example with mixed substitution:**
```yaml
views:
  - name: templated_view
    sql_template: "templates/complex_query.sql"
    sql_variables:
      start_date: "2023-01-01"
      end_date: "2023-12-31"
    env:
      S3_BUCKET: "my-data-bucket"
    config:
      database_name: "analytics"
```

### Implementation Architecture

**Core Components:**
1. **SQLFileLoader**: Loads and validates SQL files
2. **TemplateProcessor**: Handles variable substitution in templates
3. **PathResolver**: Resolves relative and absolute file paths
4. **ReferenceValidator**: Validates SQL file references and content

**Integration Points:**
1. **ConfigParser**: Modified to handle new SQL file reference fields
2. **ViewBuilder**: Updated to use SQL from files instead of inline
3. **ErrorHandler**: Enhanced to provide clear SQL file-related error messages

## Examples

### Example 1: Simple SQL File Reference

**Configuration (`catalog.yaml`):**
```yaml
version: 1

duckdb:
  database: analytics.duckdb

views:
  - name: user_summary
    source: parquet
    uri: "s3://data/users/*.parquet"
    sql_file: "sql/user_summary.sql"

  - name: daily_metrics
    source: duckdb
    database: reference
    table: events
    sql_file: "sql/daily_metrics.sql"
```

**SQL Files:**
```sql
-- sql/user_summary.sql
SELECT 
  user_id,
  COUNT(*) as total_events,
  MAX(timestamp) as last_activity
FROM user_data
GROUP BY user_id
ORDER BY total_events DESC
```

```sql
-- sql/daily_metrics.sql
SELECT 
  DATE(timestamp) as event_date,
  COUNT(*) as daily_events,
  COUNT(DISTINCT user_id) as unique_users
FROM events
GROUP BY DATE(timestamp)
ORDER BY event_date DESC
```

### Example 2: Template with Variables

**Configuration (`reports.yaml`):**
```yaml
version: 1

duckdb:
  database: reports.duckdb

views:
  - name: sales_report
    source: postgres
    database: sales_db
    sql_template: "templates/sales_analysis.sql"
    sql_variables:
      start_date: "2023-01-01"
      end_date: "2023-12-31"
      min_amount: 1000
    env:
      SALES_REGION: "EMEA"

  - name: inventory_report
    source: duckdb
    database: warehouse
    sql_template: "templates/inventory_analysis.sql"
    sql_variables:
      warehouse_id: "WH_001"
      low_stock_threshold: 10
```

**Template SQL (`templates/sales_analysis.sql`):**
```sql
SELECT 
  region,
  DATE_TRUNC('month', sale_date) as month,
  COUNT(*) as total_sales,
  SUM(amount) as total_revenue,
  AVG(amount) as avg_sale_amount
FROM sales
WHERE sale_date BETWEEN '{{ start_date }}' AND '{{ end_date }}'
  AND amount >= {{ min_amount }}
  AND region = '${env:SALES_REGION}'
GROUP BY region, DATE_TRUNC('month', sale_date)
ORDER BY region, month
```

### Example 3: Mixed Inline and File References

**Configuration (`hybrid.yaml`):**
```yaml
version: 1

duckdb:
  database: hybrid.duckdb

views:
  # Simple inline SQL (backward compatibility)
  - name: simple_view
    source: parquet
    uri: "s3://data/simple/*.parquet"
    sql: |
      SELECT id, name, created_at 
      FROM data 
      WHERE active = true

  # SQL from file
  - name: complex_analytics
    source: duckdb
    database: analytics
    sql_file: "sql/complex_analytics.sql"

  # Template with variables
  - name: templated_report
    source: postgres
    database: reporting
    sql_template: "templates/standard_report.sql"
    sql_variables:
      report_type: "monthly"
      threshold: 100
```

## Migration Guide

### From Inline SQL to SQL Files

**Before (inline):**
```yaml
- name: user_analysis
  source: duckdb
  database: analytics
  sql: |
    SELECT 
      u.user_id,
      u.name,
      COUNT(e.event_id) as event_count,
      MAX(e.timestamp) as last_event
    FROM users u
    LEFT JOIN events e ON u.user_id = e.user_id
    WHERE u.created_at >= CURRENT_DATE - INTERVAL 30 DAYS
    GROUP BY u.user_id, u.name
    ORDER BY event_count DESC
```

**After (SQL file reference):**
```yaml
- name: user_analysis
  source: duckdb
  database: analytics
  sql_file: "sql/user_analysis.sql"
```

**SQL file (`sql/user_analysis.sql`):**
```sql
SELECT 
  u.user_id,
  u.name,
  COUNT(e.event_id) as event_count,
  MAX(e.timestamp) as last_event
FROM users u
LEFT JOIN events e ON u.user_id = e.user_id
WHERE u.created_at >= CURRENT_DATE - INTERVAL 30 DAYS
GROUP BY u.user_id, u.name
ORDER BY event_count DESC
```

### Gradual Migration Strategy

1. **Identify complex queries**: Find views with long inline SQL (>$10 lines)
2. **Create SQL files**: Extract SQL to dedicated `.sql` files
3. **Update configuration**: Replace inline `sql` with `sql_file` references
4. **Test thoroughly**: Ensure queries produce identical results
5. **Update documentation**: Reflect new structure in examples and guides

## Validation Plan

### File System Validation
- **Existence checks**: Verify SQL files exist before processing
- **Readability validation**: Ensure files are readable and not corrupted
- **Path security**: Prevent directory traversal attacks
- **Size limits**: Enforce reasonable file size constraints

### SQL Content Validation
- **Syntax validation**: Parse SQL to ensure it's valid
- **Reference validation**: Check that all referenced tables/columns exist
- **Template validation**: Verify template variables are properly defined
- **Encoding validation**: Ensure files are in valid UTF-8 encoding

### Integration Testing
- **Backward compatibility**: Ensure existing inline SQL continues to work
- **Cross-platform**: Test path resolution on Windows, macOS, Linux
- **Template processing**: Test all variable substitution patterns
- **Error scenarios**: Verify appropriate error messages for missing/invalid files

### Performance Testing
- **File loading performance**: Ensure SQL file loading doesn't significantly impact build time
- **Memory usage**: Check that large SQL files don't cause memory issues
- **Concurrent access**: Test multiple configurations accessing the same SQL files

## Security Considerations

### File Access Control
- **Path restrictions**: Limit SQL file access to specific directories
- **Sandbox environment**: Prevent access to system files or sensitive directories
- **Permission validation**: Check file permissions before reading

### SQL Injection Prevention
- **Variable sanitization**: Ensure template variables are properly escaped
- **Query validation**: Parse and validate SQL before execution
- **Trusted sources**: Only load SQL files from trusted locations

### Template Security
- **Variable injection**: Prevent malicious variable names or values
- **Recursive templates**: Prevent infinite template expansion
- **Context isolation**: Ensure template variables don't access system context

## Backward Compatibility

This change is designed to be **100% backward compatible**:

1. **Existing configurations unchanged**: All current inline `sql` fields continue to work
2. **No breaking changes**: No existing functionality is removed or modified
3. **Gradual adoption**: Users can migrate at their own pace
4. **Mixed usage**: Configurations can use both inline SQL and file references simultaneously

**Deprecation plan**: 
- No deprecation of inline SQL is planned
- Both approaches will be supported indefinitely
- Migration is purely optional for improved maintainability

## Success Criteria

1. **✅ File Reference Support**: Users can reference external SQL files in configurations
2. **✅ Template Processing**: Variable substitution works correctly in templates
3. **✅ Backward Compatibility**: All existing inline SQL configurations continue to work
4. **✅ Path Resolution**: Relative and absolute paths work correctly across platforms
5. **✅ Error Handling**: Clear error messages for missing or invalid SQL files
6. **✅ Performance**: SQL file loading doesn't significantly impact build performance
7. **✅ Security**: File access restrictions prevent unauthorized access
8. **✅ Documentation**: Migration guide and examples enable easy adoption

## Implementation Timeline

**Phase 1 (Core Implementation)** - 2-3 days
- SQL file loader implementation
- Basic file reference support
- Path resolution logic
- Inline SQL backward compatibility

**Phase 2 (Templates & Variables)** - 2-3 days  
- Template processing engine
- Variable substitution (config, env, direct)
- Template validation and error handling

**Phase 3 (Testing & Polish)** - 2-3 days
- Comprehensive testing suite
- Error message improvements
- Performance optimization
- Documentation and examples

**Total Estimated Time**: 6-9 days for complete implementation

## Future Enhancements

**Potential follow-up improvements:**
- **SQL directory support**: Process all `.sql` files in a directory as views
- **Versioned SQL files**: Support for SQL file versioning or hot-reloading
- **SQL file templates**: Create reusable SQL query templates
- **IDE integration**: Plugin support for major IDEs
- **SQL formatting**: Automatic SQL formatting and linting
- **Query optimization**: Built-in query performance analysis