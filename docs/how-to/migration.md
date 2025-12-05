# How to Migrate from Manual SQL

Migrate existing manual SQL workflows to Duckalog configuration-driven approach while preserving business logic and ensuring consistency.

## Problem

You have existing manual SQL workflows (CREATE VIEW statements, SQL files, database scripts) and want to migrate to Duckalog's declarative configuration approach.

## Prerequisites

- Existing SQL knowledge and workflows
- Understanding of your current data architecture
- Access to current SQL files and database schemas
- Basic Duckalog configuration knowledge

## Solution

### 1. Inventory Existing SQL Assets

Catalog your current SQL resources:

```bash
# Find all SQL files
find . -name "*.sql" -type f > sql_inventory.txt

# Analyze existing database
duckdb current_database.duckdb -c "
SELECT 
    table_name,
    sql as definition
FROM information_schema.views 
WHERE table_schema = 'main'
ORDER BY table_name;
" > existing_views.sql

# Check for stored procedures
duckdb current_database.duckdb -c "
SELECT 
    routine_name,
    routine_definition
FROM information_schema.routines 
WHERE routine_schema = 'main';
" > existing_routines.sql
```

### 2. Create Base Configuration

Start with a minimal Duckalog configuration:

```yaml
# migration/base.yaml
version: 1

duckdb:
  database: migrated_analytics.duckdb
  # Preserve existing database settings
  pragmas:
    - "SET memory_limit='4GB'"
    - "SET threads=4"

# Start with empty views - will add gradually
views: []
```

### 3. Migrate Simple Views First

Convert straightforward views to Duckalog format:

#### Original SQL
```sql
-- existing_views.sql
CREATE VIEW active_users AS
SELECT 
    user_id,
    username,
    email,
    created_at
FROM users 
WHERE status = 'active';
```

#### Duckalog Configuration
```yaml
# migration/views/users.yaml
version: 1
imports:
  - ../base.yaml

views:
  - name: active_users
    sql: |
      SELECT 
          user_id,
          username,
          email,
          created_at
      FROM users 
      WHERE status = 'active'
```

### 4. Migrate Complex Views

Handle views with joins, subqueries, and complex logic:

#### Original Complex SQL
```sql
-- existing_analytics.sql
CREATE VIEW user_analytics AS
SELECT 
    u.user_id,
    u.username,
    COUNT(o.order_id) as order_count,
    SUM(o.amount) as total_spent,
    u.created_at
FROM users u
LEFT JOIN orders o ON u.user_id = o.user_id
WHERE u.created_at >= '2023-01-01'
GROUP BY u.user_id, u.username, u.created_at;
```

#### Duckalog Configuration
```yaml
# migration/views/analytics.yaml
version: 1
imports:
  - ../base.yaml

views:
  - name: user_analytics
    sql: |
      SELECT 
          u.user_id,
          u.username,
          COUNT(o.order_id) as order_count,
          SUM(o.amount) as total_spent,
          u.created_at
      FROM users u
      LEFT JOIN orders o ON u.user_id = o.user_id
      WHERE u.created_at >= '2023-01-01'
      GROUP BY u.user_id, u.username, u.created_at
```

### 5. Migrate Views with External Data Sources

Convert views that reference external files and databases:

#### Original SQL with External Files
```sql
-- existing_external.sql
CREATE VIEW daily_events AS
SELECT * FROM read_parquet('/data/events/' || DATE_FORMAT(CURRENT_DATE, '%Y-%m-%d') || '.parquet');
```

#### Duckalog Configuration
```yaml
# migration/views/external.yaml
version: 1
imports:
  - ../base.yaml

views:
  - name: daily_events
    source: parquet
    uri: "data/events/daily-*.parquet"
    sql: |
      SELECT * FROM '{{daily_events}}' 
      WHERE event_date = CURRENT_DATE
```

### 6. Migrate Database Attachments

Convert multi-database queries to Duckalog attachments:

#### Original Multi-Database SQL
```sql
-- existing_multi_db.sql
CREATE VIEW user_orders AS
SELECT 
    u.user_id,
    u.username,
    o.order_id,
    o.amount,
    o.order_date
FROM main.users u
JOIN legacy.orders o ON u.user_id = o.user_id;
```

#### Duckalog Configuration
```yaml
# migration/attachments.yaml
version: 1
imports:
  - ../base.yaml

duckdb:
  database: migrated_analytics.duckdb

attachments:
  duckdb:
    - alias: legacy
      path: "./databases/legacy.duckdb"
      read_only: true

views:
  - name: user_orders
    sql: |
      SELECT 
          u.user_id,
          u.username,
          o.order_id,
          o.amount,
          o.order_date
      FROM main.users u
      JOIN legacy.orders o ON u.user_id = o.user_id
```

### 7. Organize Migrated Configuration

Structure your migrated configuration for maintainability:

```
migration/
├── base.yaml              # Common settings
├── attachments.yaml         # Database attachments
├── views/
│   ├── users.yaml          # User-related views
│   ├── analytics.yaml      # Analytics views
│   ├── external.yaml       # External data views
│   └── reports.yaml        # Reporting views
└── main.yaml              # Main configuration
```

```yaml
# migration/main.yaml
version: 1
imports:
  - ./base.yaml
  - ./attachments.yaml
  - ./views/users.yaml
  - ./views/analytics.yaml
  - ./views/external.yaml
  - ./views/reports.yaml

duckdb:
  database: migrated_analytics.duckdb
```

### 8. Incremental Migration Strategy

Migrate gradually to reduce risk:

#### Phase 1: Foundation (Week 1)
```yaml
# Phase 1: Basic structure
- Set up base configuration
- Migrate 2-3 simple views
- Test basic functionality
```

#### Phase 2: Core Views (Week 2-3)
```yaml
# Phase 2: Essential views
- Migrate user and order views
- Set up database attachments
- Test data consistency
```

#### Phase 3: Advanced Analytics (Week 4-5)
```yaml
# Phase 3: Complex analytics
- Migrate analytics and reporting views
- Optimize performance
- Full integration testing
```

#### Phase 4: External Data (Week 6)
```yaml
# Phase 4: External integration
- Migrate external data source views
- Set up automated data refresh
- Production deployment preparation
```

## Verification

### 1. Compare Results

Validate that migrated views produce same results:

```bash
# Build original database
duckdb original.duckdb < original_setup.sql

# Build migrated database
duckalog build migration/main.yaml

# Compare view definitions
duckdb original.duckdb -c "SHOW ALL views;" > original_views.txt
duckdb migrated_analytics.duckdb -c "SHOW ALL views;" > migrated_views.txt

# Compare row counts
diff original_views.txt migrated_views.txt

# Test sample queries
duckdb original.duckdb -c "SELECT COUNT(*) FROM user_analytics LIMIT 5;"
duckdb migrated_analytics.duckdb -c "SELECT COUNT(*) FROM user_analytics LIMIT 5;"
```

### 2. Data Consistency Checks

Ensure data integrity after migration:

```sql
-- Check row counts match
SELECT 
    'user_analytics' as view_name,
    COUNT(*) as row_count
FROM user_analytics
UNION ALL
SELECT 
    'legacy_user_analytics' as view_name,
    COUNT(*) as row_count
FROM legacy_user_analytics;
```

### 3. Performance Validation

Compare query performance:

```bash
# Time query execution
time duckdb original.duckdb -c "SELECT * FROM user_analytics WHERE user_id = 12345;"
time duckdb migrated_analytics.duckdb -c "SELECT * FROM user_analytics WHERE user_id = 12345;"

# Check query plans
EXPLAIN SELECT * FROM user_analytics WHERE user_id = 12345;
```

## Common Variations

### 1. Migrate from Stored Procedures

Convert stored procedures to views:

```sql
-- Original stored procedure
CREATE PROCEDURE get_user_orders(user_id_param INTEGER)
BEGIN
    SELECT * FROM orders WHERE user_id = user_id_param;
END;
```

```yaml
# Migrated as parameterized view
views:
  - name: user_orders
    sql: |
      SELECT * FROM orders 
      WHERE user_id = '{{user_id_param}}'
```

### 2. Migrate Dynamic SQL

Handle dynamic SQL generation:

```sql
-- Original dynamic SQL
DO $$
BEGIN
    EXECUTE 'CREATE VIEW temp_' || $1 || ' AS SELECT * FROM ' || $1;
END $$;
```

```yaml
# Migrated as multiple views
views:
  - name: temp_users
    sql: "SELECT * FROM users"
  - name: temp_orders
    sql: "SELECT * FROM orders"
  - name: temp_products
    sql: "SELECT * FROM products"
```

### 3. Migrate ETL Workflows

Convert ETL processes to Duckalog views:

```yaml
# Original ETL: Extract-Transform-Load
# Migrated: Direct views over transformed data
views:
  - name: cleaned_users
    source: parquet
    uri: "data/processed/cleaned_users.parquet"
  - name: user_metrics
    sql: |
      SELECT 
          user_segment,
          COUNT(*) as user_count,
          AVG(order_value) as avg_order_value
      FROM cleaned_users
      GROUP BY user_segment
```

## Troubleshooting

### SQL Syntax Differences

**Issue**: DuckDB SQL syntax differs from your database

**Solution**:
```sql
-- Check DuckDB syntax
duckdb -c "YOUR_SQL_HERE"

-- Common differences:
-- PostgreSQL: || → DuckDB: ||
-- MySQL: IFNULL → DuckDB: COALESCE
-- SQL Server: GETDATE → DuckDB: CURRENT_DATE
```

### Data Type Mismatches

**Issue**: Data types not compatible with DuckDB

**Solution**:
```sql
-- Cast to compatible types
SELECT 
    CAST(text_column AS INTEGER) as numeric_value,
    COALESCE(nullable_column, 'default') as safe_column
FROM source_table;
```

### Performance Issues

**Issue**: Migrated views are slower than original

**Solution**:
```yaml
# Optimize DuckDB settings
duckdb:
  database: migrated_analytics.duckdb
  pragmas:
    - "SET memory_limit='8GB'"
    - "SET threads=8"
    - "SET enable_optimizer=true"
```

### Missing Dependencies

**Issue**: Views depend on objects that don't exist

**Solution**:
```yaml
# Ensure proper order with imports
# main.yaml
imports:
  - ./base.yaml
  - ./attachments.yaml    # Attachments first
  - ./views/tables.yaml   # Table views second
  - ./views/analytics.yaml # Analytics views last (depend on tables)
```

## Best Practices

### 1. Migration Strategy
- **Start small** with simple, non-critical views
- **Test thoroughly** at each migration phase
- **Maintain parallel systems** during transition
- **Document differences** between old and new systems

### 2. Configuration Organization
- **Use imports** to modularize configuration
- **Group related views** in separate files
- **Maintain base configuration** with common settings
- **Follow naming conventions** for consistency

### 3. Validation Approach
- **Automate comparisons** between old and new systems
- **Use same test data** for both systems
- **Monitor performance** throughout migration
- **Get stakeholder sign-off** at each phase

### 4. Risk Mitigation
- **Backup original systems** before migration
- **Create rollback procedures** for each phase
- **Test with production data** in staging environment
- **Plan for cutback** if issues arise

## Next Steps

After successful migration:

- **Decommission** old SQL workflows
- **Train team** on Duckalog configuration
- **Establish new deployment** procedures
- **Monitor performance** and optimize further
- **Document lessons learned** for future migrations

You now have a systematic approach to migrate from manual SQL workflows to Duckalog's declarative configuration while preserving business logic and improving maintainability.