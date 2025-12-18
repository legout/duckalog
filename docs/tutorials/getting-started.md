# Getting Started with Duckalog

Learn Duckalog from scratch with no prior experience. This comprehensive tutorial takes you from basic concepts to building a complete analytics catalog.

## Learning Objectives

After completing this tutorial, you will be able to:

- **Understand Duckalog fundamentals** - Configuration, views, and data sources
- **Use new connection management** - `duckalog run` command with intelligent session management
- **Create basic catalogs** - Single Parquet file configurations
- **Add SQL transformations** - Business logic and data filtering
- **Implement multi-source joins** - Combine data from multiple sources
- **Use config imports** - Organize configuration for maintainability
- **Build and query catalogs** - End-to-end workflow with new primary workflow

## New: Understanding the `duckalog run` Workflow

This tutorial uses the new `duckalog run` command, which replaces the old `build` + `query` workflow with intelligent connection management.

### Why the New Workflow?

```bash
# OLD WORKFLOW (deprecated but still works):
duckalog build config.yaml     # Build catalog
duckalog query "SELECT..."      # Query separately

# NEW WORKFLOW (recommended):
duckalog run config.yaml --query "SELECT..."    # Single command
duckalog run config.yaml --interactive          # Interactive shell
```

### Key Benefits

- **Single Command**: Build and query in one step
- **Session State**: Pragmas, settings, and attachments are automatically restored
- **Incremental Updates**: Only missing views are created for faster builds
- **Connection Reuse**: Intelligent connection pooling and management
- **Lazy Loading**: Database connections established only when needed

All examples in this tutorial use the new workflow, with notes about the old workflow for reference.

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

### 1.3 Build and Test with New Workflow

Build your first catalog and verify it works using the new `run` command:

```bash
# NEW: Build and connect in one command
duckalog run step1_basic.yaml --interactive

# In the interactive shell, run these commands:
SHOW TABLES;
SELECT * FROM users LIMIT 5;
DESCRIBE users;
exit

# OR: Direct query mode
duckalog run step1_basic.yaml --query "SELECT * FROM users LIMIT 5"

# OLD: Two-step workflow (still works but deprecated)
duckalog build step1_basic.yaml
duckdb tutorial.duckdb -c "
SHOW TABLES;
SELECT * FROM users LIMIT 5;
DESCRIBE users;
"
```

**Expected Output:**
- Database file: `tutorial.duckdb`
- View: `users` with 5 records
- Successful query execution

### 1.4 Understanding What Happened

Let's break down what the new `run` command did:

1. **Read Configuration**: Parsed `step1_basic.yaml`
2. **Smart Connection**: Connected to/created `tutorial.duckdb` with intelligent connection management
3. **Applied Pragmas**: Set memory limit and threads (automatically stored for session restoration)
4. **Created View**: Executed `CREATE VIEW users AS SELECT * FROM 'data/users.parquet'` (incremental update)
5. **Session Management**: Stored session state (pragmas, settings) for future connections
6. **Validated**: Ensured view was created successfully and connection is ready

**Key Benefits of New Workflow:**
- **Single Command**: No need to run separate build and query commands
- **Session State**: Pragmas and settings are automatically restored on reconnection
- **Incremental Updates**: Only missing views are created for faster subsequent runs
- **Connection Reuse**: Database connections are managed efficiently

## Step 2: Environment Variables and .env Files

Learn how to use environment variables and `.env` files for secure, portable configuration.

### 2.1 Why Use Environment Variables?

Environment variables help you:
- **Keep secrets secure** - No hardcoded passwords in configuration files
- **Support multiple environments** - Different values for dev, staging, prod
- **Improve portability** - Same config works everywhere with different variables
- **Follow security best practices** - Separate configuration from code

### 2.2 Creating Your First .env File

Create a `.env` file in your project directory:

```bash
# Create .env file
cat > .env << EOF
# Database configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=tutorial
DB_USER=postgres
DB_PASSWORD=your_password

# Application settings
MEMORY_LIMIT=1GB
THREAD_COUNT=2
ENVIRONMENT=development

# File paths
DATA_PATH=./data
CATALOG_NAME=tutorial
EOF

echo "✅ Created .env file with environment variables"
```

### 2.3 Using .env Variables in Configuration

Create a new configuration that uses the .env variables:

```yaml
# step2_env_vars.yaml
version: 1

duckdb:
  database: "${env:CATALOG_NAME:tutorial}.duckdb"
  pragmas:
    - "SET memory_limit='${env:MEMORY_LIMIT:512MB}'"
    - "SET threads='${env:THREAD_COUNT:2}'"
    - "SET environment='${env:ENVIRONMENT:development}'"

views:
  - name: users
    source: parquet
    uri: "${env:DATA_PATH:./data}/users.parquet"
    description: "User data from ${env:DATA_PATH:./data}/users.parquet"
```

**Note the syntax:**
- `${env:VARIABLE_NAME}` - Use environment variable
- `${env:VARIABLE_NAME:default_value}` - Use variable with default value

### 2.4 Building with Environment Variables

```bash
# NEW: Build and connect with .env variables (automatically loaded)
duckalog run step2_env_vars.yaml --verbose --query "SELECT * FROM users LIMIT 3"

# Check the verbose output for .env loading:
# Loading .env files {'config_path': 'step2_env_vars.yaml', 'file_count': 1}
# Loaded .env file {'file_path': '/path/to/.env', 'var_count': 8}
# Completed .env file loading {'total_files': 1}

# Interactive mode with environment variables
duckalog run step2_env_vars.yaml --interactive
# In shell: SHOW TABLES; SELECT * FROM users LIMIT 3; exit

# OLD: Two-step workflow (still works)
duckalog build step2_env_vars.yaml --verbose
duckdb tutorial.duckdb -c "
SHOW TABLES;
SELECT * FROM users LIMIT 3;
"
```

### 2.5 Testing Variable Resolution

Create a simple test to verify your environment variables:

```yaml
# test_env.yaml
version: 1

test_section:
  db_host: "${env:DB_HOST:not_set}"
  memory_limit: "${env:MEMORY_LIMIT:not_set}"
  data_path: "${env:DATA_PATH:not_set}"
  missing_var: "${env:DOES_NOT_EXIST:default_value}"
```

```bash
# Test environment variable resolution
duckalog validate test_env.yaml

# Set a missing variable and test again
export DOES_NOT_EXIST="now_it_works"
duckalog validate test_env.yaml
```

### 2.6 Environment-Specific Configuration

Create different .env files for different environments:

```bash
# .env.development (for local development)
cat > .env.development << EOF
ENVIRONMENT=development
MEMORY_LIMIT=512MB
THREAD_COUNT=2
DATA_PATH=./data
EOF

# .env.production (for production deployment)
cat > .env.production << EOF
ENVIRONMENT=production
MEMORY_LIMIT=4GB
THREAD_COUNT=8
DATA_PATH=/data/production
EOF

# Use specific environment
source .env.development
duckalog run step2_env_vars.yaml  # Uses development values

source .env.production
duckalog run step2_env_vars.yaml  # Uses production values

# Test specific environments with queries
duckalog run step2_env_vars.yaml --query "SELECT current_setting('memory_limit')"
```

### 2.7 Understanding .env File Discovery

Duckalog automatically discovers `.env` files in this order:

1. **Configuration file directory** (highest priority)
2. **Parent directories** (up to 10 levels)
3. **Current working directory**

```bash
# Test .env discovery
mkdir -p subdir/configs
cp .env subdir/configs/

# Both configurations will find and use the .env file:
duckalog run step2_env_vars.yaml                    # Uses ./.env
duckalog run subdir/configs/step2_env_vars.yaml     # Uses subdir/configs/.env
```

### 2.8 Security Best Practices

```bash
# 1. Never commit .env files to version control
echo ".env*" >> .gitignore

# 2. Use secure file permissions
chmod 600 .env

# 3. Use different .env files for different environments
ls -la .env*

# 4. Validate your .env files don't contain secrets
grep -iE "(password|secret|key)" .env || echo "✅ No obvious secrets found"
```

### 2.9 Understanding Environment Variable Concepts

Key concepts you learned:

- **Automatic .env Loading**: Duckalog discovers and loads .env files automatically
- **Variable Interpolation**: `${env:VAR_NAME}` syntax for environment variables
- **Default Values**: `${env:VAR:default}` provides fallback values
- **Hierarchical Discovery**: Searches parent directories for .env files
- **Security**: Keep .env files out of version control
- **Environment Isolation**: Different .env files for different environments

## Step 3: Adding SQL Transformations

Add business logic and data transformations using SQL views.

### 3.1 Create Transformed Views

Extend your configuration with SQL transformations:

```yaml
# step3_transformations.yaml
version: 1

duckdb:
  database: "${env:CATALOG_NAME:tutorial}.duckdb"
  pragmas:
    - "SET memory_limit='${env:MEMORY_LIMIT:1GB}'"
    - "SET threads='${env:THREAD_COUNT:2}'"

views:
  - name: users
    source: parquet
    uri: "${env:DATA_PATH:./data}/users.parquet"
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

### 3.2 Build and Test Transformations

```bash
# NEW: Build and test with transformations
duckalog run step3_transformations.yaml --query "
-- Test active_users view
SELECT * FROM active_users;
"

# Interactive mode to explore all transformations
duckalog run step3_transformations.yaml --interactive
# In shell:
# SELECT * FROM active_users;
# SELECT * FROM user_registrations_by_month;
# SELECT COUNT(*) as total_users, SUM(CASE WHEN status = 'active' THEN 1 ELSE 0 END) as active_users FROM users;

# OLD: Two-step workflow (still works)
duckalog build step3_transformations.yaml
duckdb tutorial.duckdb -c "
SELECT * FROM active_users;
SELECT * FROM user_registrations_by_month;
"
```

### 3.3 Understanding SQL Views

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
# NEW: Build and test with imports
duckalog run step4_modular.yaml --query "
-- List all views
SHOW TABLES;
"

# Interactive mode to explore modular views
duckalog run step4_modular.yaml --interactive
# In shell:
# SHOW TABLES;
# SELECT * FROM users LIMIT 3;
# SELECT * FROM orders LIMIT 3;
# SELECT * FROM active_users LIMIT 3;
# SELECT * FROM user_orders LIMIT 3;
# SELECT * FROM user_summary LIMIT 5;

# Quick test of imported views
duckalog run step4_modular.yaml --query "SELECT COUNT(*) FROM users"
duckalog run step4_modular.yaml --query "SELECT COUNT(*) FROM orders"

# OLD: Two-step workflow (still works)
duckalog build step4_modular.yaml
duckdb tutorial.duckdb -c "SHOW TABLES; SELECT * FROM users LIMIT 3;"
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

**Solution**: Test SQL in interactive mode first:
```bash
# Test SQL interactively with new workflow
duckalog run step3_transformations.yaml --interactive
# Then test your SQL in the shell

# OLD: Test SQL manually (still works)
duckdb tutorial.duckdb -c "YOUR SQL HERE"
```

#### Connection Issues with New Workflow
**Issue**: Connection failures or session not restored

**Solution**: Use verbose logging to diagnose:
```bash
# Check connection details with verbose output
duckalog run config.yaml --verbose --query "SELECT 1"

# Force rebuild if views are missing
duckalog run config.yaml --force-rebuild
```

## Next Steps

After completing this tutorial:

1. **Explore New Connection Management**:
   - Session state restoration and persistent secrets
   - Incremental view updates for faster builds
   - Connection pooling and intelligent management
   - [`duckalog run`](../reference/cli.md#run---new-primary-command) command features

2. **Explore Advanced Features**:
   - Database attachments for multi-database scenarios
   - Semantic models for business-friendly metadata
   - Environment variables for secure configuration

3. **Work Through Examples**:
   - [Multi-Source Analytics Example](../examples/multi-source-analytics.md)
   - [Environment Variables Example](../examples/environment-vars.md)
   - [Config Imports Example](../examples/config-imports.md)

4. **Learn Best Practices**:
   - [Performance Tuning Guide](../how-to/performance-tuning.md)
   - [Environment Management Guide](../how-to/environment-management.md)
   - [Troubleshooting Guide](../guides/troubleshooting.md)
   - [Secrets Persistence Guide](../how-to/secrets-persistence.md)

5. **Try the Dashboard**:
   - [Dashboard Tutorial](dashboard-basics.md)
   - Interactive data exploration
   - Real-time query execution

6. **Migration Tips**:
   - Use `duckalog run` instead of `build` + `query` workflow
   - Leverage context managers for Python API (`with connect_to_catalog(...)`)
   - Consider using persistent secrets for long-running applications

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