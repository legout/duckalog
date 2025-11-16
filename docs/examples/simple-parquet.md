# Simple Parquet Example

This example shows how to create DuckDB views over Parquet files stored in cloud storage. It's perfect for getting started with Duckalog when your data is already in Parquet format.

## When to Use This Example

Choose this example if:
- Your data is in Parquet files (local or S3)
- You want to query Parquet data with SQL
- You're working with partitioned data
- You need simple, fast analytics without complex joins
- You want to combine multiple Parquet datasets

## Prerequisites

1. **Duckalog installed:**
   ```bash
   pip install duckalog
   ```

2. **Sample Parquet files** - You can use your own or create test data:
   ```python
   # Create sample Parquet files for testing
   import pandas as pd
   import duckdb
   
   # Create sample data
   users_df = pd.DataFrame({
       'user_id': range(1, 101),
       'name': [f'User {i}' for i in range(1, 101)],
       'signup_date': pd.date_range('2023-01-01', periods=100),
       'region': ['US', 'EU', 'APAC'] * 33 + ['US']
   })
   
   events_df = pd.DataFrame({
       'event_id': range(1, 1001),
       'user_id': [i % 100 + 1 for i in range(1000)],
       'event_type': ['page_view', 'click', 'purchase'] * 333 + ['page_view'],
       'timestamp': pd.date_range('2023-01-01', periods=1000, freq='H'),
       'value': [i * 0.5 for i in range(1000)]
   })
   
   # Save as Parquet
   users_df.to_parquet('./users.parquet')
   events_df.to_parquet('./events.parquet')
   
   # Or upload to S3 (if you have AWS credentials configured)
   import boto3
   s3 = boto3.client('s3')
   users_df.to_parquet('s3://your-bucket/data/users.parquet')
   events_df.to_parquet('s3://your-bucket/data/events.parquet')
   ```

## Basic Configuration Pattern

### Single View Example

Create a file called `simple-parquet.yaml`:

```yaml
version: 1

# DuckDB configuration
duckdb:
  database: simple_catalog.duckdb
  install_extensions:
    - httpfs  # Required for cloud storage access
  
  pragmas:
    # Performance settings
    - "SET memory_limit='1GB'"
    - "SET threads=2"
    
    # S3 configuration (if using cloud storage)
    - "SET s3_region='us-east-1'"
    - "SET s3_access_key_id='${env:AWS_ACCESS_KEY_ID}'"
    - "SET s3_secret_access_key='${env:AWS_SECRET_ACCESS_KEY}'"

# View definitions
views:
  # Simple single-table view
  - name: users
    source: parquet
    uri: "s3://your-bucket/data/users.parquet"  # Or local: "./users.parquet"
    description: "User reference data from Parquet"
```

**Key configuration elements:**
- `source: parquet` - Specifies Parquet file source
- `uri` - Path to Parquet file (supports wildcards for partitioned data)
- Extension installation for cloud access
- S3 credentials via environment variables

### Multi-View Example with Joins

For more complex analytics, define multiple views:

```yaml
version: 1

duckdb:
  database: analytics_catalog.duckdb
  install_extensions:
    - httpfs
  
  pragmas:
    - "SET memory_limit='2GB'"
    - "SET s3_region='us-east-1'"
    - "SET s3_access_key_id='${env:AWS_ACCESS_KEY_ID}'"
    - "SET s3_secret_access_key='${env:AWS_SECRET_ACCESS_KEY}'"

views:
  # Raw data views
  - name: raw_users
    source: parquet
    uri: "s3://your-bucket/data/users/*.parquet"  # Supports partitioned data
    description: "User data from partitioned Parquet files"
    
  - name: raw_events
    source: parquet
    uri: "s3://your-bucket/data/events/*.parquet"
    description: "Event data from partitioned Parquet files"
  
  # Derived views with analytics
  - name: daily_active_users
    sql: |
      SELECT 
        DATE(timestamp) as event_date,
        COUNT(DISTINCT user_id) as active_users,
        COUNT(*) as total_events
      FROM raw_events
      GROUP BY DATE(timestamp)
      ORDER BY event_date DESC
    description: "Daily active user metrics"
    
  - name: user_summary
    sql: |
      SELECT 
        u.user_id,
        u.name,
        u.region,
        u.signup_date,
        COUNT(DISTINCT DATE(e.timestamp)) as active_days,
        COUNT(e.event_id) as total_events,
        MAX(e.timestamp) as last_activity
      FROM raw_users u
      LEFT JOIN raw_events e ON u.user_id = e.user_id
      GROUP BY u.user_id, u.name, u.region, u.signup_date
      ORDER BY total_events DESC NULLS LAST
    description: "User engagement summary"
    
  - name: popular_content
    sql: |
      SELECT 
        event_type,
        COUNT(*) as event_count,
        COUNT(DISTINCT user_id) as unique_users,
        AVG(value) as avg_value
      FROM raw_events
      WHERE event_type IN ('page_view', 'click', 'purchase')
      GROUP BY event_type
      ORDER BY event_count DESC
    description: "Most popular content types"
```

## S3 Configuration Deep Dive

### Environment Variables

Set your AWS credentials as environment variables:

```bash
# Option 1: Direct environment variables
export AWS_ACCESS_KEY_ID="AKIA..."
export AWS_SECRET_ACCESS_KEY="your-secret-key"
export AWS_SESSION_TOKEN="optional-session-token"  # For temporary credentials

# Option 2: Using AWS CLI
aws configure set aws_access_key_id AKIA...
aws configure set aws_secret_access_key your-secret-key

# Option 3: Using IAM roles (for EC2/ECS)
# IAM role attached to instance/container
```

### S3 URI Patterns

Duckalog supports various S3 URI patterns:

```yaml
# Single file
uri: "s3://bucket/path/file.parquet"

# All files in directory
uri: "s3://bucket/path/*.parquet"

# Partitioned data with pattern
uri: "s3://bucket/year=2023/month=01/*.parquet"

# Specific date range
uri: "s3://bucket/data/2023-01-*.parquet"

# Multiple patterns (use SQL view composition)
uri: "s3://bucket/events/2023-*-*.parquet"
```

### Performance Considerations

```yaml
duckdb:
  pragmas:
    # Optimize for Parquet reading
    - "SET threads=4"                    # Match your CPU cores
    - "SET memory_limit='2GB'           # Set based on data size
    - "SET s3_region='us-east-1'        # Use same region as data
    - "SET enable_http_metadata_cache=true"  # Cache HTTP metadata
```

## Step-by-Step Usage

### 1. Create Your Configuration

Save the configuration above as `simple-parquet.yaml`.

### 2. Set Environment Variables

```bash
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
```

### 3. Validate Configuration

```bash
duckalog validate simple-parquet.yaml
```

Expected output:
```
✅ Configuration is valid
✅ All views defined correctly
✅ Environment variables resolved
```

### 4. Generate SQL (Optional)

Preview the SQL that will be executed:

```bash
duckalog generate-sql simple-parquet.yaml --output generated.sql

# View the generated SQL
cat generated.sql
```

### 5. Build the Catalog

```bash
duckalog build simple-parquet.yaml
```

This creates `simple_catalog.duckdb` with your Parquet views.

### 6. Query Your Data

```bash
# Connect with DuckDB
duckdb simple_catalog.duckdb

# Example queries:
SELECT * FROM users LIMIT 10;

SELECT 
  region,
  COUNT(*) as user_count
FROM users 
GROUP BY region
ORDER BY user_count DESC;

SELECT * FROM daily_active_users WHERE event_date >= CURRENT_DATE - INTERVAL 7 DAYS;
```

### 7. Use Programmatically

```python
from duckalog import load_config
import duckdb
import pandas as pd

# Load and build catalog
build_catalog("simple-parquet.yaml")

# Connect and query
con = duckdb.connect("simple_catalog.duckdb")

# Get DataFrame for analysis
users_df = con.execute("SELECT * FROM users WHERE region = 'US'").df()
print(users_df.head())

# Complex analytics
metrics_df = con.execute("""
    SELECT 
      DATE(timestamp) as date,
      COUNT(DISTINCT user_id) as daily_users,
      COUNT(*) as total_events,
      AVG(value) as avg_event_value
    FROM raw_events
    WHERE DATE(timestamp) >= CURRENT_DATE - INTERVAL 30 DAYS
    GROUP BY DATE(timestamp)
    ORDER BY date
""").df()

print(metrics_df)
```

## Key Concepts Demonstrated

This example teaches:

1. **Parquet as Data Source**: How to directly query Parquet files
2. **Cloud Storage Access**: S3 configuration and credentials
3. **Performance Optimization**: Memory and threading settings
4. **View Composition**: Building analytics from raw data
5. **SQL in Views**: Complex analytics with standard SQL
6. **Environment Variables**: Secure credential management
7. **Partitioned Data**: Handling large datasets with wildcards

## Troubleshooting

### Common Issues

**1. S3 Access Denied:**
```bash
# Test S3 access
aws s3 ls s3://your-bucket/data/

# Check permissions - user needs:
# - s3:GetObject for file access
# - s3:ListBucket for directory listing
```

**2. Parquet File Not Found:**
```bash
# Verify file exists
aws s3 ls s3://your-bucket/data/users.parquet

# Check wildcard patterns
aws s3 ls s3://your-bucket/data/*.parquet
```

**3. Memory Errors:**
```yaml
# Reduce memory usage
duckdb:
  pragmas:
    - "SET memory_limit='512MB'"
```

**4. Slow Queries:**
```yaml
# Increase parallelism
duckdb:
  pragmas:
    - "SET threads=8"  # Match CPU cores
```

### Performance Tips

1. **Use Partitioned Data**: Organize Parquet files by date/region
2. **Optimize File Sizes**: 100MB-1GB per file works well
3. **Co-locate Data**: Store in same S3 region as queries
4. **Use Compression**: Parquet's built-in compression is efficient
5. **Filter Early**: Push down filters to Parquet reading when possible

## Variations

### Local Files Only

For local files without cloud access:

```yaml
version: 1

duckdb:
  database: local_catalog.duckdb
  # No extensions needed for local files
  pragmas:
    - "SET memory_limit='1GB'"

views:
  - name: local_data
    source: parquet
    uri: "./data/*.parquet"  # Local path with wildcard
```

### Date-Partitioned Data

For time-series data:

```yaml
views:
  - name: events_2023
    source: parquet
    uri: "s3://bucket/events/year=2023/*.parquet"
    
  - name: recent_events
    sql: |
      SELECT * FROM events_2023
      WHERE DATE(timestamp) >= CURRENT_DATE - INTERVAL 30 DAYS
```

This example provides a solid foundation for working with Parquet data in Duckalog. Adapt the patterns to your specific data structure and requirements.