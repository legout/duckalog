# Getting Started with Duckalog

Learn Duckalog from scratch with no prior experience. This comprehensive tutorial takes you from basic concepts to building a complete analytics catalog.

## Learning Objectives

After completing this tutorial, you will be able to:

- **Understand Duckalog fundamentals** - Configuration, views, and data sources
- **Create basic catalogs** - Single Parquet file configurations
- **Add SQL transformations** - Business logic and data filtering
- **Implement multi-source joins** - Combine data from multiple sources
- **Use config imports** - Organize configuration for maintainability
- **Build and query catalogs** - End-to-end workflow

## Prerequisites

- **Python 3.12+** installed and accessible
- **Duckalog package** installed:
  ```bash
  pip install duckalog
  ```
- **Basic command line** familiarity
- **Text editor** for configuration files
- **No prior Duckalog experience** required

## Step 1: Single Parquet File Catalog

Create your first Duckalog configuration with a single Parquet data source.

### 1.1 Create Sample Data

First, let's create some sample data to work with:

```bash
# Create project directory
mkdir duckalog-tutorial
cd duckalog-tutorial

# Create data directory
mkdir data

# Create sample Parquet data
python3 -c "
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

# Sample users data
users_data = pd.DataFrame({
    'user_id': [1, 2, 3, 4, 5],
    'username': ['alice', 'bob', 'charlie', 'diana', 'eve'],
    'email': ['alice@example.com', 'bob@example.com', 'charlie@example.com', 'diana@example.com', 'eve@example.com'],
    'created_at': ['2023-01-01', '2023-01-15', '2023-02-01', '2023-02-15', '2023-03-01'],
    'status': ['active', 'active', 'active', 'inactive', 'active']
})

# Sample orders data
orders_data = pd.DataFrame({
    'order_id': [101, 102, 103, 104, 105, 106],
    'user_id': [1, 2, 1, 3, 2, 4],
    'amount': [29.99, 49.99, 19.99, 89.99, 39.99, 59.99],
    'order_date': ['2023-01-02', '2023-01-16', '2023-01-03', '2023-02-02', '2023-02-16', '2023-03-02'],
    'status': ['completed', 'completed', 'completed', 'completed', 'completed', 'completed']
})

# Save as Parquet files
pq.write_table(users_data, 'data/users.parquet')
pq.write_table(orders_data, 'data/orders.parquet')

print('Sample data created successfully!')
"
```

### 1.2 Create Basic Configuration

Create your first Duckalog configuration file:

```yaml
# step1_basic.yaml
version: 1

duckdb:
  database: tutorial.duckdb
  # Basic performance settings
  pragmas:
    - "SET memory_limit='1GB'"
    - "SET threads=2"

views:
  - name: users
    source: parquet
    uri: "data/users.parquet"
    description: "User data from sample dataset"
```

### 1.3 Build and Test

Build your first catalog and verify it works:

```bash
# Build the catalog
duckalog build step1_basic.yaml

# Test the catalog
duckdb tutorial.duckdb -c "
-- Check if view was created
SHOW TABLES;

-- Query the users view
SELECT * FROM users LIMIT 5;

-- Check view definition
DESCRIBE users;
"
```

**Expected Output:**
- Database file: `tutorial.duckdb`
- View: `users` with 5 records
- Successful query execution

### 1.4 Understanding What Happened

Let's break down what Duckalog did:

1. **Read Configuration**: Parsed `step1_basic.yaml`
2. **Created Database**: Connected to/created `tutorial.duckdb`
3. **Applied Pragmas**: Set memory limit and threads
4. **Created View**: Executed `CREATE VIEW users AS SELECT * FROM 'data/users.parquet'`
5. **Validated**: Ensured view was created successfully

## Step 2: Adding SQL Transformations

Add business logic and data transformations using SQL views.

### 2.1 Create Transformed Views

Extend your configuration with SQL transformations:

```yaml
# step2_transformations.yaml
version: 1

duckdb:
  database: tutorial.duckdb
  pragmas:
    - "SET memory_limit='1GB'"
    - "SET threads=2"

views:
  - name: users
    source: parquet
    uri: "data/users.parquet"
    description: "Raw user data"

  - name: active_users
    sql: |
      SELECT 
          user_id,
          username,
          email,
          created_at
      FROM users 
      WHERE status = 'active'
    description: "Active users only"

  - name: user_registrations_by_month
    sql: |
      SELECT 
          DATE_TRUNC('month', created_at) as registration_month,
          COUNT(*) as new_users
      FROM users 
      GROUP BY DATE_TRUNC('month', created_at)
      ORDER BY registration_month
    description: "Monthly user registration counts"
```

### 2.2 Build and Test Transformations

```bash
# Build with transformations
duckalog build step2_transformations.yaml

# Test the new views
duckdb tutorial.duckdb -c "
-- Test active_users view
SELECT * FROM active_users;

-- Test monthly registrations
SELECT * FROM user_registrations_by_month;

-- Verify transformation logic
SELECT 
    COUNT(*) as total_users,
    SUM(CASE WHEN status = 'active' THEN 1 ELSE 0 END) as active_users
FROM users;
"
```

### 2.3 Understanding SQL Views

Key concepts you learned:

- **SQL Views**: Virtual tables based on SELECT queries
- **Data Filtering**: Using WHERE clauses to subset data
- **Aggregations**: Using GROUP BY for summary statistics
- **Date Functions**: DATE_TRUNC for time-based analysis
- **View Dependencies**: Views can reference other views

## Step 3: Multi-Source Joins

Combine data from multiple sources using joins and attachments.

### 3.1 Create Additional Data Source

Add an orders data source to join with users:

```yaml
# step3_joins.yaml
version: 1

duckdb:
  database: tutorial.duckdb
  pragmas:
    - "SET memory_limit='1GB'"
    - "SET threads=2"

views:
  - name: users
    source: parquet
    uri: "data/users.parquet"

  - name: orders
    source: parquet
    uri: "data/orders.parquet"

  - name: user_orders
    sql: |
      SELECT 
          u.user_id,
          u.username,
          u.email,
          o.order_id,
          o.amount,
          o.order_date,
          o.status
      FROM users u
      LEFT JOIN orders o ON u.user_id = o.user_id
    description: "Users with their order information"

  - name: user_summary
    sql: |
      SELECT 
          u.user_id,
          u.username,
          u.email,
          COUNT(o.order_id) as order_count,
          COALESCE(SUM(o.amount), 0) as total_spent,
          MAX(o.order_date) as last_order_date
      FROM users u
      LEFT JOIN orders o ON u.user_id = o.user_id
      GROUP BY u.user_id, u.username, u.email
    description: "User order summary statistics"
```

### 3.2 Build and Test Joins

```bash
# Build with joins
duckalog build step3_joins.yaml

# Test the joined views
duckdb tutorial.duckdb -c "
-- Test user_orders join
SELECT * FROM user_orders LIMIT 5;

-- Test user summary
SELECT * FROM user_summary LIMIT 5;

-- Verify join logic
SELECT 
    COUNT(*) as total_users,
    COUNT(CASE WHEN o.order_id IS NOT NULL THEN 1 END) as users_with_orders
FROM users u
LEFT JOIN orders o ON u.user_id = o.user_id;
"
```

### 3.3 Understanding Join Concepts

Key concepts you learned:

- **LEFT JOINs**: Include all records from left table, matching from right
- **Aggregations with JOINs**: Group after joining for accurate summaries
- **NULL handling**: Using COALESCE for missing values
- **Performance**: Views can reference other views efficiently

## Step 4: Using Config Imports for Modularity

Organize your configuration using imports for better maintainability.

### 4.1 Create Modular Configuration

Split your configuration into logical modules:

```yaml
# config/base.yaml
version: 1

duckdb:
  database: tutorial.duckdb
  pragmas:
    - "SET memory_limit='1GB'"
    - "SET threads=2"
```

```yaml
# config/views/users.yaml
version: 1

views:
  - name: users
    source: parquet
    uri: "../data/users.parquet"
    description: "Raw user data"
```

```yaml
# config/views/orders.yaml
version: 1

views:
  - name: orders
    source: parquet
    uri: "../data/orders.parquet"
    description: "Order data"
```

```yaml
# config/transforms/analytics.yaml
version: 1

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

  - name: user_orders
    sql: |
      SELECT 
          u.user_id,
          u.username,
          u.email,
          o.order_id,
          o.amount,
          o.order_date,
          o.status
      FROM users u
      LEFT JOIN orders o ON u.user_id = o.user_id

  - name: user_summary
    sql: |
      SELECT 
          u.user_id,
          u.username,
          u.email,
          COUNT(o.order_id) as order_count,
          COALESCE(SUM(o.amount), 0) as total_spent,
          MAX(o.order_date) as last_order_date
      FROM users u
      LEFT JOIN orders o ON u.user_id = o.user_id
      GROUP BY u.user_id, u.username, u.email
```

### 4.2 Create Main Configuration

Create a main configuration that imports the modules:

```yaml
# step4_modular.yaml
version: 1
imports:
  - ./base.yaml
  - ./views/users.yaml
  - ./views/orders.yaml
  - ./transforms/analytics.yaml
```

### 4.3 Build and Test Modular Configuration

```bash
# Build with imports
duckalog build step4_modular.yaml

# Test that all views are available
duckdb tutorial.duckdb -c "
-- List all views
SHOW TABLES;

-- Test each imported view
SELECT * FROM users LIMIT 3;
SELECT * FROM orders LIMIT 3;
SELECT * FROM active_users LIMIT 3;
SELECT * FROM user_orders LIMIT 3;
SELECT * FROM user_summary LIMIT 3;
"
```

### 4.4 Understanding Import Benefits

Advantages of using imports:

- **Organization**: Group related configurations together
- **Reusability**: Share base settings across projects
- **Team Collaboration**: Different teams can own different modules
- **Maintainability**: Easier to update specific functionality
- **Testing**: Test individual modules in isolation

## Check Your Understanding

Test your knowledge with these exercises:

### Exercise 1: Basic Configuration
Create a configuration that:
- Uses a Parquet file named `products.parquet`
- Creates a view called `active_products`
- Filters for products with `status = 'active'`

<details>
<summary>Click to see solution</summary>

```yaml
# exercise1_solution.yaml
version: 1

duckdb:
  database: tutorial.duckdb

views:
  - name: active_products
    source: parquet
    uri: "data/products.parquet"
    sql: |
      SELECT * FROM products 
      WHERE status = 'active'
```
</details>

### Exercise 2: SQL Transformation
Create a view that:
- Uses the `active_products` view
- Calculates total inventory value
- Groups by product category

<details>
<summary>Click to see solution</summary>

```yaml
# exercise2_solution.yaml
version: 1

duckdb:
  database: tutorial.duckdb

views:
  - name: active_products
    source: parquet
    uri: "data/products.parquet"
    sql: |
      SELECT * FROM products 
      WHERE status = 'active'

  - name: inventory_by_category
    sql: |
      SELECT 
          category,
          COUNT(*) as product_count,
          SUM(price * quantity) as total_value
      FROM active_products
      GROUP BY category
```
</details>

### Exercise 3: Multi-Source Configuration
Create a configuration with imports that:
- Has separate base, views, and analytics modules
- Joins customer data with order data
- Creates a customer lifetime value view

<details>
<summary>Click to see solution</summary>

```yaml
# base.yaml
version: 1
duckdb:
  database: tutorial.duckdb
  pragmas:
    - "SET memory_limit='1GB'"
    - "SET threads=2"
```

```yaml
# views/customers.yaml
version: 1
views:
  - name: customers
    source: parquet
    uri: "../data/customers.parquet"
```

```yaml
# views/orders.yaml
version: 1
views:
  - name: orders
    source: parquet
    uri: "../data/orders.parquet"
```

```yaml
# analytics.yaml
version: 1
views:
  - name: customer_lifetime_value
    sql: |
      SELECT 
          c.customer_id,
          c.name,
          COUNT(o.order_id) as total_orders,
          SUM(o.amount) as lifetime_value
      FROM customers c
      LEFT JOIN orders o ON c.customer_id = o.customer_id
      GROUP BY c.customer_id, c.name
```

```yaml
# main.yaml
version: 1
imports:
  - ./base.yaml
  - ./views/customers.yaml
  - ./views/orders.yaml
  - ./analytics.yaml
```
</details>

## Troubleshooting

### Common Issues and Solutions

#### Build Fails
**Issue**: `ConfigError: Field required`

**Solution**: Ensure you have all required fields:
```yaml
version: 1  # Required
duckdb:         # Required
  database: tutorial.duckdb
views: []         # Required (can be empty)
```

#### Data File Not Found
**Issue**: `PathResolutionError: Failed to resolve import path`

**Solution**: Check file paths are correct:
```bash
# Verify data files exist
ls -la data/

# Use absolute paths if needed
views:
  - name: users
    source: parquet
    uri: "/full/path/to/data/users.parquet"
```

#### SQL Syntax Errors
**Issue**: `EngineError: Failed to create view`

**Solution**: Test SQL in DuckDB first:
```bash
# Test SQL manually
duckdb tutorial.duckdb -c "YOUR SQL HERE"
```

## Next Steps

After completing this tutorial:

1. **Explore Advanced Features**:
   - Database attachments for multi-database scenarios
   - Semantic models for business-friendly metadata
   - Environment variables for secure configuration

2. **Work Through Examples**:
   - [Multi-Source Analytics Example](../examples/multi-source-analytics.md)
   - [Environment Variables Example](../examples/environment-vars.md)
   - [Config Imports Example](../examples/config-imports.md)

3. **Learn Best Practices**:
   - [Performance Tuning Guide](../how-to/performance-tuning.md)
   - [Environment Management Guide](../how-to/environment-management.md)
   - [Troubleshooting Guide](../guides/troubleshooting.md)

4. **Try the Dashboard**:
   - [Dashboard Tutorial](dashboard-basics.md)
   - Interactive data exploration
   - Real-time query execution

## Congratulations!

You have successfully:
- ✅ Created your first Duckalog configuration
- ✅ Implemented SQL transformations
- ✅ Built multi-source data joins
- ✅ Organized configuration with imports
- ✅ Understood core Duckalog concepts

You're now ready to tackle more advanced Duckalog scenarios and build sophisticated data catalogs for your analytics needs!

## Need Help?

If you encountered issues:
- Review the [Troubleshooting Guide](../guides/troubleshooting.md)
- Check the [API Reference](../reference/api.md)
- Explore [Examples](../examples/index.md) for similar patterns
- Ask questions in GitHub discussions

Ready to continue your Duckalog journey? Try the [Dashboard Tutorial](dashboard-basics.md) next!