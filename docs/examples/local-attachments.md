# Local Attachments Example

This example demonstrates how to attach and work with local DuckDB and SQLite databases in Duckalog. It's ideal for combining data from multiple local databases or integrating existing data stores into your analytics pipeline.

## When to Use This Example

Choose this example if:

- You have multiple local DuckDB databases to combine
- You need to integrate existing SQLite databases
- You want to join data across different local databases
- You're working with read-only reference data
- You need to build a unified view of local data sources
- You want to avoid duplicating data by referencing instead of copying

## Prerequisites

1. **Duckalog installed:**
   ```bash
   pip install duckalog
   ```

2. **Sample local databases** - Create test data for demonstration:
   ```python
   # Create sample DuckDB databases
   import duckdb
   
   # Reference data database
   con_ref = duckdb.connect("reference_data.duckdb")
   con_ref.execute("""
     CREATE TABLE users AS
     SELECT 
       user_id,
       name,
       email,
       signup_date,
       country,
       segment
     FROM range(1, 101) t(user_id)
     CROSS JOIN (VALUES 
       ('Alice', 'alice@example.com', '2023-01-15', 'US', 'enterprise'),
       ('Bob', 'bob@example.com', '2023-02-20', 'UK', 'smb'),
       ('Carol', 'carol@example.com', '2023-03-10', 'DE', 'enterprise'),
       ('David', 'david@example.com', '2023-04-05', 'US', 'startup'),
       ('Eve', 'eve@example.com', '2023-05-12', 'FR', 'smb')
     ) u(name, email, signup_date, country, segment)
     WHERE user_id <= 5
   """)
   
   # Analytics database with sales data
   con_analytics = duckdb.connect("analytics_data.duckdb")
   con_analytics.execute("""
     CREATE TABLE sales AS
     SELECT 
       sale_id,
       user_id,
       product_name,
       amount,
       sale_date,
       region
     FROM range(1, 501) t(sale_id)
     CROSS JOIN (VALUES 
       ('Laptop', 1200.00, '2023-01-01', 'North'),
       ('Mouse', 25.00, '2023-01-02', 'South'),
       ('Keyboard', 75.00, '2023-01-03', 'East'),
       ('Monitor', 300.00, '2023-01-04', 'West'),
       ('Desk', 450.00, '2023-01-05', 'North')
     ) p(product_name, amount, sale_date, region)
     CROSS JOIN (SELECT user_id FROM range(1, 6)) u(user_id)
     WHERE sale_id <= 100
   """)
   
   con_ref.close()
   con_analytics.close()
   
   # Create sample SQLite database
   import sqlite3
   
   con_sqlite = sqlite3.connect("legacy_system.db")
   con_sqlite.execute("""
     CREATE TABLE customer_preferences (
       user_id INTEGER PRIMARY KEY,
       preferred_categories TEXT,
       communication_style TEXT,
       last_contact_date DATE
     )
   """)
   
   preferences_data = [
     (1, 'electronics,books', 'email', '2023-06-15'),
     (2, 'home,garden', 'phone', '2023-06-10'),
     (3, 'technology,software', 'email', '2023-06-20'),
     (4, 'gaming,electronics', 'slack', '2023-06-18'),
     (5, 'office,productivity', 'email', '2023-06-12')
   ]
   
   con_sqlite.executemany(
     "INSERT INTO customer_preferences VALUES (?, ?, ?, ?)",
     preferences_data
   )
   
   con_sqlite.commit()
   con_sqlite.close()
   
   print("Created sample databases: reference_data.duckdb, analytics_data.duckdb, legacy_system.db")
   ```

## Basic Attachment Configuration

### Single Database Attachment

Create a file called `local-attachments.yaml`:

```yaml
version: 1

# DuckDB configuration
duckdb:
  database: unified_catalog.duckdb
  pragmas:
    # Performance settings for local work
    - "SET memory_limit='1GB'"
    - "SET threads=2"
    - "SET temp_directory='/tmp/duckdb_temp'"  # For large operations

# Attach local databases
attachments:
  duckdb:
    - alias: reference       # How you'll reference this database
      path: ./reference_data.duckdb   # Path to DuckDB file
      read_only: true        # Prevent modifications (recommended)
      
    - alias: analytics
      path: ./analytics_data.duckdb
      read_only: true

  sqlite:
    - alias: legacy         # SQLite database reference
      path: ./legacy_system.db

# Views that use attached databases
views:
  - name: user_reference
    source: duckdb          # Attached DuckDB database
    database: reference     # Alias from attachments section
    table: users            # Table name in attached database
    description: "User reference data from local DuckDB"

  - name: sales_data
    source: duckdb
    database: analytics
    table: sales
    description: "Sales data from analytics database"

  - name: customer_prefs
    source: sqlite          # SQLite attachment
    database: legacy        # SQLite alias
    table: customer_preferences
    description: "Customer preferences from legacy system"
```

**Key configuration elements:**
- `attachments` section defines external databases
- `alias` provides reference name used in views
- `read_only: true` prevents accidental data modification
- Views reference attached databases by alias
- Different source types: `duckdb`, `sqlite`, `postgres`

## Advanced Attachment Patterns

### Multiple Tables from Same Database

```yaml
views:
  # Access multiple tables from the same attachment
  - name: user_profiles
    source: duckdb
    database: reference
    table: users
    description: "User profiles"
    
  - name: user_stats
    source: duckdb
    database: reference
    table: user_statistics  # Different table, same database
    description: "User statistics"
    
  - name: sales_summary
    source: duckdb
    database: analytics
    table: sales
    description: "Raw sales transactions"
```

### Cross-Database Joins

```yaml
  # Join data across attached databases
  - name: user_sales_enriched
    sql: |
      SELECT 
        u.user_id,
        u.name,
        u.email,
        u.country,
        u.segment,
        p.preferred_categories,
        p.communication_style,
        COUNT(s.sale_id) as total_sales,
        SUM(s.amount) as total_revenue,
        AVG(s.amount) as avg_sale_amount
      FROM user_profiles u
      LEFT JOIN customer_prefs p ON u.user_id = p.user_id
      LEFT JOIN sales_data s ON u.user_id = s.user_id
      GROUP BY u.user_id, u.name, u.email, u.country, u.segment, 
               p.preferred_categories, p.communication_style
      ORDER BY total_revenue DESC NULLS LAST
    description: "Unified user view combining all data sources"

  - name: sales_by_region
    sql: |
      SELECT 
        u.country,
        u.segment,
        COUNT(DISTINCT u.user_id) as user_count,
        COUNT(s.sale_id) as total_sales,
        SUM(s.amount) as total_revenue,
        AVG(s.amount) as avg_sale_value
      FROM user_profiles u
      JOIN sales_data s ON u.user_id = s.user_id
      GROUP BY u.country, u.segment
      ORDER BY total_revenue DESC
    description: "Sales performance by region and segment"
```

## Read-Only vs Read-Write Attachments

### Read-Only Attachments (Recommended)

```yaml
attachments:
  duckdb:
    - alias: reference
      path: ./reference_data.duckdb
      read_only: true        # Safe - prevents modifications
```

**Benefits:**
- Prevents accidental data corruption
- Allows safe concurrent access
- Better for production use
- Clear data provenance

**Use when:**
- Reference data that shouldn't change
- Historical data
- Data shared across multiple processes
- Production environments

### Read-Write Attachments (Use Carefully)

```yaml
attachments:
  duckdb:
    - alias: staging
      path: ./staging_data.duckdb
      read_only: false       # Allows modifications
      
  sqlite:
    - alias: legacy
      path: ./legacy_system.db
      read_only: false
```

**Considerations:**
- Use only when you need to modify source data
- Be aware of potential concurrency issues
- Ensure proper backup strategies
- Consider performance implications

**Use when:**
- Staging area for data processing
- Temporary transformations
- Controlled ETL processes

## Step-by-Step Usage

### 1. Create Configuration File

Save the configuration above as `local-attachments.yaml`.

### 2. Validate Configuration

```bash
duckalog validate local-attachments.yaml
```

Expected output:
```
✅ Configuration is valid
✅ All database attachments found
✅ All views defined correctly
```

### 3. Generate SQL (Optional)

Preview the SQL that will be executed:

```bash
duckalog generate-sql local-attachments.yaml --output attachments.sql
cat attachments.sql
```

### 4. Build the Catalog

```bash
duckalog build local-attachments.yaml
```

This creates `unified_catalog.duckdb` with views over your attached databases.

### 5. Query Your Data

```bash
# Connect with DuckDB
duckdb unified_catalog.duckdb

# Example queries:
# Simple view access
SELECT * FROM user_reference LIMIT 10;

# Cross-database join
SELECT 
  u.name,
  u.country,
  COUNT(s.sale_id) as sales_count,
  SUM(s.amount) as total_revenue
FROM user_reference u
LEFT JOIN sales_data s ON u.user_id = s.user_id
GROUP BY u.user_id, u.name, u.country
ORDER BY total_revenue DESC;

# Complex analytics across sources
SELECT * FROM user_sales_enriched WHERE total_sales > 0;
```

### 6. Use Programmatically

```python
from duckalog import load_config, build_catalog
import duckdb

# Build catalog
build_catalog("local-attachments.yaml")

# Connect to unified catalog
con = duckdb.connect("unified_catalog.duckdb")

# Simple queries
users_df = con.execute("SELECT * FROM user_reference WHERE country = 'US'").df()
print("US Users:")
print(users_df)

# Cross-database analytics
analytics_df = con.execute("""
    SELECT 
      country,
      segment,
      COUNT(*) as user_count,
      SUM(total_revenue) as segment_revenue
    FROM user_sales_enriched
    GROUP BY country, segment
    ORDER BY segment_revenue DESC
""").df()
print("\nRevenue by Country/Segment:")
print(analytics_df)

# Find power users
power_users = con.execute("""
    SELECT name, email, total_sales, total_revenue
    FROM user_sales_enriched
    WHERE total_sales >= 5
    ORDER BY total_revenue DESC
""").df()
print("\nPower Users:")
print(power_users)
```

## Performance Optimization

### Memory Management

```yaml
duckdb:
  pragmas:
    - "SET memory_limit='2GB'"      # Adjust based on available RAM
    - "SET threads=4"               # Match CPU cores
    - "SET temp_directory='/tmp/duckdb_temp'"  # For large operations
    - "SET wal_autocheckpoint='1GB'" # For read-write attachments
```

### Large Dataset Considerations

```yaml
# For large databases, consider selective views
views:
  - name: recent_users
    sql: |
      SELECT * FROM user_reference
      WHERE signup_date >= CURRENT_DATE - INTERVAL 365 DAYS
    description: "Users from last year"
    
  - name: high_value_sales
    sql: |
      SELECT * FROM sales_data
      WHERE amount >= 100.0
    description: "Sales above $100"
```

## Key Concepts Demonstrated

This example teaches:

1. **Database Attachment**: How to connect external DuckDB/SQLite databases
2. **Read-Only Safety**: Best practices for safe data access
3. **Cross-Database Joins**: Joining data across multiple local databases
4. **Alias Management**: Organizing and referencing attached databases
5. **Performance Optimization**: Memory and threading for local work
6. **Data Unification**: Combining disparate data sources
7. **SQL Composition**: Building complex analytics across sources

## Troubleshooting

### Common Issues

**1. Database File Not Found:**
```bash
# Check file exists and path is correct
ls -la reference_data.duckdb
ls -la analytics_data.duckdb
ls -la legacy_system.db

# Verify current directory
pwd
```

**2. Permission Errors:**
```bash
# Check read permissions
ls -l *.duckdb *.db

# Fix permissions if needed
chmod 644 *.duckdb *.db

# For read-write access, ensure write permissions
chmod 666 *.duckdb *.db
```

**3. Schema/Table Not Found:**
```sql
-- Check available tables in attached database
SHOW TABLES FROM reference;
SHOW TABLES FROM analytics;
SHOW TABLES FROM legacy;
```

**4. Memory Issues:**
```yaml
# Reduce memory usage
duckdb:
  pragmas:
    - "SET memory_limit='512MB'"
    - "SET threads=2"
```

**5. Slow Cross-Database Queries:**
```yaml
# Optimize for local performance
duckdb:
  pragmas:
    - "SET threads=8"                    # Use more cores
    - "SET temp_directory='/fast/ssd/'"  # Use fast storage
```

### Debug Commands

```sql
-- List all attached databases
DATABASE_LIST;

-- Show schema for attached database
DESCRIBE reference.users;

-- Check query plan for optimization
EXPLAIN SELECT * FROM user_sales_enriched;

-- Monitor memory usage
PRAGMA memory_limit;
PRAGMA threads;
```

## Variations

### Backup and Restore Pattern

```yaml
# Create backup before building catalog
- name: backup_step
  sql: |
    -- Backup critical reference data
    CREATE TABLE backup_users AS SELECT * FROM user_reference;
```

### Incremental Data Loading

```yaml
# Load only new/changed data
views:
  - name: updated_sales
    sql: |
      SELECT * FROM sales_data
      WHERE sale_date >= (SELECT MAX(sale_date) FROM backup_sales)
```

### Data Quality Checks

```yaml
# Add data quality views
- name: data_quality_report
  sql: |
    SELECT 
      'user_reference' as table_name,
      COUNT(*) as record_count,
      COUNT(DISTINCT user_id) as unique_users,
      COUNT(*) - COUNT(email) as missing_emails
    FROM user_reference
    UNION ALL
    SELECT 
      'sales_data' as table_name,
      COUNT(*) as record_count,
      COUNT(DISTINCT user_id) as unique_users,
      COUNT(*) - COUNT(amount) as missing_amounts
    FROM sales_data
```

This example provides a solid foundation for working with local database attachments in Duckalog. The patterns shown here can be extended to handle more complex scenarios and larger datasets.

## Security Considerations

### File Permissions

```bash
# Set appropriate permissions for databases
chmod 640 reference_data.duckdb        # Read/write for owner, read for group
chmod 644 legacy_system.db             # Read-only for all

# For sensitive data, consider encryption
chmod 600 sensitive_data.duckdb        # Owner read/write only
```

### Data Access Control

```yaml
# Use views to control data access
views:
  - name: public_user_data
    sql: |
      SELECT user_id, name, country  -- Exclude sensitive fields
      FROM user_reference
```

This attachment pattern enables powerful data integration while maintaining security and performance. Adapt these patterns to your specific local data landscape and requirements.
