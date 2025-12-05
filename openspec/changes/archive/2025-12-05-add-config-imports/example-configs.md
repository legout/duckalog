# Config Imports Examples

## Example 1: Basic Split by Domain

### Directory Structure
```
project/
├── catalog.yaml
├── settings.yaml
├── views/
│   ├── users.yaml
│   ├── products.yaml
│   └── orders.yaml
└── secrets/
    └── s3-secrets.yaml
```

### `catalog.yaml` (Main file)
```yaml
imports:
  - ./settings.yaml
  - ./views/users.yaml
  - ./views/products.yaml
  - ./views/orders.yaml
  - ./secrets/s3-secrets.yaml

# Local overrides or additional configuration
duckdb:
  database: analytics.duckdb
  # settings.yaml will provide install_extensions and pragmas
  # secrets/s3-secrets.yaml will provide secrets
```

### `settings.yaml`
```yaml
duckdb:
  install_extensions:
    - httpfs
    - aws
    - iceberg
  pragmas:
    - "SET threads = 4"
    - "SET memory_limit = '4GB'"
  settings:
    - "SET s3_region = 'us-east-1'"
```

### `views/users.yaml`
```yaml
views:
  - name: users
    source: parquet
    uri: "s3://data-lake/users/*.parquet"
    description: "User data from S3"
  
  - name: active_users
    sql: |
      SELECT *
      FROM users
      WHERE status = 'active'
    description: "Active users only"
```

### `views/products.yaml`
```yaml
views:
  - name: products
    source: parquet
    uri: "s3://data-lake/products/*.parquet"
    description: "Product catalog"
  
  - name: product_categories
    sql: |
      SELECT DISTINCT category
      FROM products
      WHERE category IS NOT NULL
    description: "Unique product categories"
```

### `views/orders.yaml`
```yaml
views:
  - name: orders
    source: parquet
    uri: "s3://data-lake/orders/*.parquet"
    description: "Order transactions"
  
  - name: monthly_sales
    sql: |
      SELECT
        DATE_TRUNC('month', order_date) AS month,
        SUM(amount) AS total_sales,
        COUNT(*) AS order_count
      FROM orders
      GROUP BY 1
    description: "Monthly sales summary"
```

### `secrets/s3-secrets.yaml`
```yaml
duckdb:
  secrets:
    - type: s3
      provider: config
      key_id: "${env:AWS_ACCESS_KEY_ID}"
      secret: "${env:AWS_SECRET_ACCESS_KEY}"
      region: us-east-1
```

## Example 2: Environment-Specific Configuration

### Directory Structure
```
project/
├── catalog.yaml
├── base.yaml
├── dev.yaml
├── staging.yaml
└── prod.yaml
```

### `catalog.yaml`
```yaml
imports:
  - ./base.yaml
  - ./${env:ENVIRONMENT}.yaml

# Environment-specific file will be loaded based on ENVIRONMENT variable
# e.g., ENVIRONMENT=dev loads dev.yaml
# e.g., ENVIRONMENT=prod loads prod.yaml
```

### `base.yaml` (Common configuration)
```yaml
duckdb:
  install_extensions:
    - httpfs
    - aws

views:
  - name: users
    source: parquet
    uri: "${env:DATA_BUCKET}/users/*.parquet"
  
  - name: products
    source: parquet
    uri: "${env:DATA_BUCKET}/products/*.parquet"
```

### `dev.yaml` (Development environment)
```yaml
duckdb:
  database: dev_analytics.duckdb
  settings:
    - "SET threads = 2"
    - "SET memory_limit = '2GB'"

views:
  - name: test_data
    sql: |
      SELECT 'test' AS environment, 42 AS value
```

### `prod.yaml` (Production environment)
```yaml
duckdb:
  database: prod_analytics.duckdb
  settings:
    - "SET threads = 16"
    - "SET memory_limit = '16GB'"

attachments:
  postgres:
    - alias: production_db
      host: "${env:PG_HOST}"
      port: 5432
      database: analytics
      user: "${env:PG_USER}"
      password: "${env:PG_PASSWORD}"
```

## Example 3: Team-Based Organization

### Directory Structure
```
project/
├── catalog.yaml
├── infrastructure/
│   ├── settings.yaml
│   └── secrets.yaml
├── data-team/
│   ├── raw-views.yaml
│   └── transformed-views.yaml
├── analytics-team/
│   ├── semantic-models.yaml
│   └── business-views.yaml
└── data-science/
    └── ml-features.yaml
```

### `catalog.yaml`
```yaml
imports:
  - ./infrastructure/settings.yaml
  - ./infrastructure/secrets.yaml
  - ./data-team/raw-views.yaml
  - ./data-team/transformed-views.yaml
  - ./analytics-team/semantic-models.yaml
  - ./analytics-team/business-views.yaml
  - ./data-science/ml-features.yaml
```

### `infrastructure/settings.yaml`
```yaml
duckdb:
  database: team_analytics.duckdb
  install_extensions:
    - httpfs
    - aws
    - iceberg
    - spatial
  pragmas:
    - "SET threads = 8"
    - "SET memory_limit = '8GB'"
```

### `data-team/raw-views.yaml`
```yaml
views:
  - name: raw_users
    source: parquet
    uri: "s3://data-lake/raw/users/*.parquet"
  
  - name: raw_products
    source: parquet
    uri: "s3://data-lake/raw/products/*.parquet"
  
  - name: raw_orders
    source: parquet
    uri: "s3://data-lake/raw/orders/*.parquet"
```

### `data-team/transformed-views.yaml`
```yaml
views:
  - name: cleaned_users
    sql: |
      SELECT
        user_id,
        TRIM(email) AS email,
        LOWER(country) AS country,
        CAST(age AS INTEGER) AS age
      FROM raw_users
      WHERE email IS NOT NULL
  
  - name: product_sales
    sql: |
      SELECT
        p.product_id,
        p.name,
        p.category,
        COUNT(o.order_id) AS total_orders,
        SUM(o.amount) AS total_revenue
      FROM raw_products p
      LEFT JOIN raw_orders o ON p.product_id = o.product_id
      GROUP BY 1, 2, 3
```

### `analytics-team/semantic-models.yaml`
```yaml
semantic_models:
  - name: sales_analytics
    base_view: product_sales
    dimensions:
      - name: product_id
        expression: product_id
        type: string
      - name: category
        expression: category
        type: string
    measures:
      - name: total_orders
        expression: SUM(total_orders)
        type: number
      - name: total_revenue
        expression: SUM(total_revenue)
        type: number
```

## Example 4: Remote Imports

### `catalog.yaml`
```yaml
imports:
  - ./local-settings.yaml
  - s3://company-configs/shared/views.yaml
  - https://raw.githubusercontent.com/company/analytics-templates/main/semantic-models.yaml
  - ./team-overrides.yaml

duckdb:
  database: combined.duckdb
```

### `local-settings.yaml`
```yaml
duckdb:
  install_extensions:
    - httpfs
    - aws
  settings:
    - "SET s3_region = 'us-east-1'"
```

### `team-overrides.yaml`
```yaml
# Local overrides for shared configurations
views:
  - name: team_specific_view
    sql: SELECT 'team_data' AS source
```

## Example 5: Complex Merging Behavior

### `base.yaml`
```yaml
duckdb:
  database: base.duckdb
  install_extensions:
    - httpfs
  settings:
    - "SET threads = 4"

views:
  - name: view1
    sql: SELECT 1 AS id
```

### `override1.yaml`
```yaml
duckdb:
  database: override1.duckdb  # Overrides base.yaml's database
  install_extensions:
    - aws  # Added to base list (result: [httpfs, aws])

views:
  - name: view2
    sql: SELECT 2 AS id
```

### `override2.yaml`
```yaml
duckdb:
  settings:
    - "SET memory_limit = '4GB'"  # Added to base settings

views:
  - name: view3
    sql: SELECT 3 AS id
```

### `main.yaml`
```yaml
imports:
  - ./base.yaml
  - ./override1.yaml
  - ./override2.yaml

# Final merged configuration:
# duckdb:
#   database: override1.duckdb  # Last wins for scalars
#   install_extensions: [httpfs, aws]  # Lists concatenated
#   settings: ["SET threads = 4", "SET memory_limit = '4GB'"]  # Lists concatenated
# views: [view1, view2, view3]  # Lists concatenated
```

## Example 6: Error Cases

### Circular Import Error
```yaml
# a.yaml
imports:
  - ./b.yaml

duckdb:
  database: a.duckdb

# b.yaml
imports:
  - ./a.yaml  # ERROR: Circular import!

duckdb:
  database: b.duckdb
```

### Duplicate View Name Error
```yaml
# file1.yaml
views:
  - name: users
    sql: SELECT * FROM source1

# file2.yaml
views:
  - name: users  # ERROR: Duplicate view name!
    sql: SELECT * FROM source2

# main.yaml
imports:
  - ./file1.yaml
  - ./file2.yaml
```

### Missing Import File
```yaml
# main.yaml
imports:
  - ./missing.yaml  # ERROR: File not found!

duckdb:
  database: catalog.duckdb
```

## Best Practices

### 1. Start Simple
```yaml
# Start with single file, then split as needed
imports:
  - ./settings.yaml
  - ./views.yaml
```

### 2. Use Meaningful File Names
```
# Good
settings.yaml
user-views.yaml
product-views.yaml
semantic-models.yaml

# Avoid
file1.yaml
config2.yaml
stuff.yaml
```

### 3. Organize by Domain or Team
```
config/
├── infrastructure/     # DB settings, extensions, secrets
│   ├── settings.yaml
│   └── secrets.yaml
├── data-sources/      # Raw data views
│   ├── users.yaml
│   ├── products.yaml
│   └── orders.yaml
├── transformations/   # SQL transformations
│   ├── cleaning.yaml
│   └── aggregations.yaml
└── business/         # Semantic models
    ├── sales.yaml
    └── customers.yaml
```

### 4. Use Environment Variables for Paths
```yaml
imports:
  - ./${env:ENVIRONMENT}/settings.yaml
  - ./${env:TEAM}/views.yaml
```

### 5. Keep Import Lists Manageable
```yaml
# Good - organized by domain
imports:
  - ./infrastructure/*.yaml
  - ./data-sources/*.yaml
  - ./transformations/*.yaml

# Avoid - too many individual files
imports:
  - ./file1.yaml
  - ./file2.yaml
  - ./file3.yaml
  # ... 20 more files
```

### 6. Document Dependencies
```yaml
# catalog.yaml
# Imports are processed in order:
# 1. Infrastructure (settings, secrets)
# 2. Data sources (raw views)
# 3. Transformations (cleaned views)
# 4. Business logic (semantic models)

imports:
  # Infrastructure
  - ./infrastructure/settings.yaml
  - ./infrastructure/secrets.yaml
  
  # Data sources
  - ./data-sources/users.yaml
  - ./data-sources/products.yaml
  
  # Transformations
  - ./transformations/cleaning.yaml
  - ./transformations/aggregations.yaml
  
  # Business logic
  - ./business/semantic-models.yaml
```