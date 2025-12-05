# How to Tune Performance

Optimize Duckalog performance for your specific workload and data characteristics through systematic tuning approaches.

## Problem

Your Duckalog catalog builds or queries are running slowly, consuming excessive memory, or not scaling with your data volume.

## Prerequisites

- Basic Duckalog and DuckDB knowledge
- Understanding of your data characteristics
- Access to performance metrics and monitoring
- Familiarity with SQL optimization concepts

## Solution

### 1. Memory Optimization

Configure DuckDB memory settings for your workload:

#### Basic Memory Configuration
```yaml
# config/performance.yaml
version: 1

duckdb:
  database: analytics.duckdb
  pragmas:
    # Set memory limit (adjust based on available RAM)
    - "SET memory_limit='4GB'"
    
    # Enable memory-mapped I/O for large files
    - "SET force_parallelism=true"
```

#### Advanced Memory Settings
```yaml
# For memory-intensive workloads
duckdb:
  database: analytics.duckdb
  pragmas:
    # Use all available memory
    - "SET memory_limit='8GB'"
    
    # Enable memory mapping for large datasets
    - "SET enable_memory_map=true"
    
    # Configure memory management
    - "SET memory_allocator=arena'"
    
    # Set checkpoint threshold
    - "SET checkpoint_threshold='2GB'"
```

#### Memory Usage Monitoring
```bash
# Monitor memory usage during build
time -v duckalog build config/performance.yaml

# Check DuckDB memory usage
duckdb analytics.duckdb -c "
SELECT 
    current_memory_usage,
    peak_memory_usage,
    allocator_memory_limit
FROM pragma_memory_info();
"
```

### 2. Threading Optimization

Configure parallelism for your CPU and workload:

#### CPU-Based Threading
```yaml
# For 4-core CPU
duckdb:
  database: analytics.duckdb
  pragmas:
    # Use all available cores
    - "SET threads=4"
    
    # Enable parallel processing
    - "SET enable_progress_bar=true"
    
    # Configure parallel join behavior
    - "SET parallel_join=true"
```

#### Workload-Specific Threading
```yaml
# For I/O-heavy workloads (many small files)
duckdb:
  database: analytics.duckdb
  pragmas:
    # More threads for parallel I/O
    - "SET threads=8"
    
    # Optimize for many small queries
    - "SET enable_optimizer=true"
    
    # Configure join order
    - "SET join_order_type=automatic'"
```

#### Thread Testing and Validation
```bash
# Test optimal thread count
for threads in 1 2 4 6 8; do
  echo "Testing with $threads threads..."
  time duckalog build config/performance.yaml --threads $threads
done

# Monitor CPU usage
htop  # Watch CPU utilization during builds
```

### 3. Query Optimization

Optimize SQL queries and view definitions:

#### Efficient View Design
```yaml
# Good: Filtered views with proper indexing
views:
  - name: recent_orders
    source: parquet
    uri: "data/orders.parquet"
    sql: |
      -- Filter early to reduce data processed
      SELECT 
          order_id,
          customer_id,
          order_date,
          amount
      FROM orders 
      WHERE order_date >= '2023-01-01'
        AND status = 'completed'
      
  - name: customer_summary
    source: duckdb
    database: analytics
    table: recent_orders  # Use filtered view
    sql: |
      -- Aggregate pre-filtered data
      SELECT 
          customer_id,
          COUNT(*) as order_count,
          SUM(amount) as total_spent
      FROM recent_orders
      GROUP BY customer_id
```

#### Column Pruning and Projection
```yaml
# Good: Select only needed columns
views:
  - name: order_metrics
    sql: |
      -- Select specific columns, not SELECT *
      SELECT 
          order_id,
          customer_id,
          amount,
          order_date
      FROM orders
      WHERE order_date >= '2023-01-01'

# Bad: Select all columns
views:
  - name: order_all_columns
    sql: |
      -- Inefficient: selects all columns
      SELECT * FROM orders
      WHERE order_date >= '2023-01-01'
```

#### Join Optimization
```yaml
# Good: Optimized joins with proper ordering
views:
  - name: customer_orders_full
    sql: |
      -- Join on indexed columns with proper ordering
      SELECT 
          c.customer_id,
          c.customer_name,
          o.order_id,
          o.order_date,
          o.amount
      FROM customers c
      INNER JOIN orders o ON c.customer_id = o.customer_id
      WHERE o.order_date >= '2023-01-01'
      ORDER BY c.customer_id, o.order_date  # Helps with join ordering
```

### 4. File Format Optimization

Choose optimal file formats for your data:

#### Parquet Optimization
```yaml
# For analytical workloads
views:
  - name: analytics_data
    source: parquet
    uri: "data/analytics/*.parquet"
    # Parquet configuration for performance
    sql: |
      SELECT * FROM analytics_data 
      WHERE event_date >= '2023-01-01'
```

#### File Organization
```yaml
# Organize files for optimal access patterns
views:
  - name: daily_events
    source: parquet
    # Date-partitioned files for partition pruning
    uri: "data/events/year=2023/month=*/day=*/events.parquet"
    sql: |
      SELECT * FROM daily_events 
      WHERE event_date BETWEEN '2023-01-01' AND '2023-12-31'
```

### 5. DuckDB Extensions and Settings

Leverage DuckDB extensions for performance:

#### Enable Extensions
```yaml
# For JSON and semi-structured data
duckdb:
  database: analytics.duckdb
  install_extensions:
    - httpfs      # For S3/cloud storage
    - json        # For JSON processing
    - parquet     # For Parquet optimization
  
  load_extensions:
    - httpfs
    - json
    - parquet
```

#### Extension-Specific Optimizations
```yaml
# For full-text search
duckdb:
  database: analytics.duckdb
  install_extensions:
    - fts        # Full-text search
  
  pragmas:
    - "SET enable_fts=true"
    
views:
  - name: searchable_documents
    sql: |
      -- Use FTS for text search
      SELECT 
          doc_id,
          title,
          content
      FROM documents 
      WHERE content MATCH 'search terms'
      ORDER BY rank
```

### 6. Caching Strategies

Implement effective caching for repeated queries:

#### Materialized Views
```yaml
# Create materialized views for expensive computations
views:
  - name: customer_metrics_raw
    source: parquet
    uri: "data/orders.parquet"
    sql: |
      -- Expensive aggregation
      SELECT 
          customer_id,
          COUNT(*) as order_count,
          SUM(amount) as total_spent,
          AVG(amount) as avg_order_value
      FROM orders
      GROUP BY customer_id

  - name: customer_metrics
    sql: |
      -- Refresh materialized view
      CREATE OR REPLACE TABLE customer_metrics AS
      SELECT * FROM customer_metrics_raw;
      
      -- Query materialized view
      SELECT * FROM customer_metrics
      WHERE customer_id = '{{customer_id}}'
```

#### Result Caching
```yaml
# Cache query results
duckdb:
  database: analytics.duckdb
  pragmas:
    - "SET enable_progress_bar=true"
    - "SET preserve_insertion_order=true"
    
views:
  - name: cached_results
    sql: |
      -- Use CREATE OR REPLACE for caching
      CREATE OR REPLACE TABLE temp_results AS
      SELECT * FROM expensive_computation
      WHERE date_parameter = '{{date_param}}'
```

### 7. Build Performance Monitoring

Monitor and analyze build performance:

#### Build Timing
```bash
# Time the build process
time duckalog build config/performance.yaml

# Detailed timing with verbose output
duckalog build config/performance.yaml --verbose --timing
```

#### Resource Monitoring
```bash
# Monitor memory usage
/usr/bin/time -v duckalog build config/performance.yaml

# Monitor CPU usage
duckalog build config/performance.yaml &
BUILD_PID=$!
# Monitor in another terminal
top -p $BUILD_PID

# Check disk I/O
iotop -p $BUILD_PID
```

#### Performance Analysis
```sql
-- Analyze query performance
EXPLAIN ANALYZE SELECT * FROM expensive_view WHERE date_column = '2023-01-01';

-- Check for missing indexes
PRAGMA table_info('your_table_name');

-- Monitor memory usage
SELECT * FROM pragma_memory_info();
```

## Verification

### 1. Performance Benchmarks

Establish baseline performance metrics:

```bash
# Benchmark current configuration
echo "Benchmarking current configuration..."
time duckalog build config/performance.yaml

# Test query performance
duckdb analytics.duckdb -c "
EXPLAIN ANALYZE SELECT * FROM your_view WHERE date_column = '2023-01-01';
"

# Record baseline metrics
echo "Build time: $BUILD_TIME seconds" > performance_baseline.txt
echo "Memory usage: $MEMORY_USAGE MB" >> performance_baseline.txt
```

### 2. Optimization Validation

Test each optimization individually:

```bash
# Test memory optimization
echo "Testing memory optimization..."
time duckalog build config/memory_optimized.yaml

# Test threading optimization  
echo "Testing threading optimization..."
time duckalog build config/thread_optimized.yaml

# Test query optimization
echo "Testing query optimization..."
time duckalog build config/query_optimized.yaml
```

### 3. Comparative Analysis

Compare performance across configurations:

```bash
# Run comparative benchmarks
for config in baseline memory_optimized thread_optimized query_optimized; do
  echo "Testing $config..."
  time duckalog build configs/${config}.yaml
  echo "---"
done

# Generate performance report
echo "Performance Comparison Results:" > performance_report.txt
echo "Configuration, Build Time, Memory Usage" >> performance_report.txt
# Add actual results from timing above
```

## Common Variations

### 1. Large Dataset Optimization

For datasets larger than available memory:

```yaml
# Out-of-core processing
duckdb:
  database: analytics.duckdb
  pragmas:
    # Use disk-based processing
    - "SET memory_limit='1GB'"           # Low memory for metadata
    - "SET force_parallelism=false"       # Reduce memory pressure
    - "SET enable_object_cache=true"       # Cache metadata
    - "SET object_cache_limit='256MB'"     # Limit cache size
```

### 2. High-Concurrency Optimization

For many concurrent users:

```yaml
# Concurrent access optimization
duckdb:
  database: analytics.duckdb
  pragmas:
    # Enable read-only mode for readers
    - "SET wal_autocheckpoint=1000000"     # Less frequent checkpoints
    - "SET enable_progress_bar=true"        # Progress indication
    - "SET preserve_insertion_order=false"   # Better concurrency
```

### 3. Cloud Storage Optimization

For S3/cloud data sources:

```yaml
# Cloud storage optimization
duckdb:
  database: analytics.duckdb
  install_extensions:
    - httpfs
  
  pragmas:
    # S3-specific settings
    - "SET s3_region='us-west-2'"
    - "SET s3_access_key_id='${env:AWS_ACCESS_KEY_ID}'"
    - "SET s3_secret_access_key='${env:AWS_SECRET_ACCESS_KEY}'"
    
    # Connection pooling for cloud
    - "SET s3_uploader_max_parts=8'"
    - "SET enable_http_stats=true"
```

## Troubleshooting

### Memory Issues

**Symptoms**: Out of memory errors, slow performance

**Solutions**:
```yaml
# Reduce memory usage
duckdb:
  pragmas:
    - "SET memory_limit='2GB'"        # Reduce from 4GB
    - "SET enable_memory_map=false"     # Disable memory mapping
    - "SET force_parallelism=false"    # Reduce parallelism
```

### Threading Issues

**Symptoms**: CPU not fully utilized, poor parallelism

**Solutions**:
```yaml
# Optimize threading
duckdb:
  pragmas:
    - "SET threads=2"                 # Reduce from 8 to 2
    - "SET enable_progress_bar=true"   # Monitor progress
    - "SET enable_optimizer=true"       # Better query planning
```

### I/O Bottlenecks

**Symptoms**: Slow builds with low CPU/memory usage

**Solutions**:
```yaml
# Optimize I/O patterns
duckdb:
  pragmas:
    - "SET enable_progress_bar=true"   # Monitor I/O
    - "SET checkpoint_threshold='1GB'"   # More frequent checkpoints
    - "SET wal_autocheckpoint=100000"   # Balance durability/performance
```

## Best Practices

### 1. Performance Monitoring
- **Establish baselines** before optimization
- **Monitor continuously** in production
- **Profile queries** to identify bottlenecks
- **Document performance** characteristics of your data

### 2. Incremental Optimization
- **Change one variable** at a time for proper measurement
- **Test each optimization** with realistic workloads
- **Roll back changes** that don't improve performance
- **Document successful optimizations** for future reference

### 3. Data-Aware Tuning
- **Understand your data characteristics** (size, distribution, access patterns)
- **Optimize for common queries** rather than edge cases
- **Use appropriate file formats** for your data type
- **Consider data growth** when configuring resources

### 4. Environment-Specific Tuning
- **Different settings** for development vs production
- **Scale resources** based on actual workload
- **Monitor resource usage** in each environment
- **Plan for scaling** as data volume grows

## Next Steps

After optimizing performance:

- **Set up monitoring** for ongoing performance tracking
- **Create performance tests** for regression detection
- **Document optimization decisions** and their impact
- **Plan for scaling** as data and users grow
- **Explore advanced features** like partitioning and indexing

You now have a comprehensive approach to optimize Duckalog performance for any workload and data characteristics.