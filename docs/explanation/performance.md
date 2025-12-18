# Performance Characteristics

Understanding Duckalog's performance profile helps you design efficient data pipelines and set realistic expectations.

## Duckalog Performance Overview

Duckalog is built on DuckDB, which provides exceptional performance for analytical workloads through columnar storage, vectorized execution, and advanced query optimization. The performance characteristics are primarily inherited from DuckDB with additional overhead for configuration processing.

## Key Performance Factors

### 1. **Data Size and Memory Requirements**

#### Ideal Range: 1MB - 100GB
```yaml
# Excellent performance for this scale
views:
  - name: daily_events
    source: parquet
    uri: "s3://analytics/events-100GB-total"
```

**Performance Characteristics:**
- **< 1GB**: Loads entirely into cache, queries complete in milliseconds
- **1-10GB**: Frequent cache misses but still fast (seconds)
- **10-100GB**: Requires careful query optimization, manages memory well
- **100GB-1TB**: Possible but requires additional optimization

#### Memory Management
```yaml
duckdb:
  database: analytics.duckdb
  settings:
    # Important for large datasets
    memory_limit: "8GB"
    temp_directory: "./duckdb_temp"
```

**Guidelines:**
- **Dataset size**: Allocate 2-4x dataset size in RAM for optimal performance
- **Available RAM**: Set memory_limit to 75% of available RAM
- **Temp storage**: Ensure sufficient disk space for spill-over operations

### 2. **Query Complexity Patterns**

#### Simple Filters and Aggregations (Fastest)
```sql
-- Optimal: Simple operations on columnar data
SELECT user_id, COUNT(*) FROM events WHERE event_date = '2024-01-01' GROUP BY user_id
```
**Performance**: Milliseconds to seconds regardless of dataset size

#### Complex Joins (Good)
```sql
-- Good: DuckDB's join optimizer performs well
SELECT u.name, e.event_type, COUNT(*) 
FROM users u 
JOIN events e ON u.id = e.user_id 
GROUP BY u.name, e.event_type
```
**Performance**: Seconds for GB-scale, minutes for TB-scale

#### Window Functions and Subqueries (Varies)
```sql
-- Moderate: More complex execution plans
SELECT *, 
       ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY timestamp DESC) as rn,
       LAG(timestamp) OVER (PARTITION BY user_id ORDER BY timestamp) as prev_timestamp
FROM events
```
**Performance**: Can be memory-intensive, test on sample data

### 3. **Data Source Performance**

#### Parquet Files (Optimal)
```yaml
views:
  - name: parquet_source
    source: parquet
    uri: "s3://bucket/data/"
    # Benefits: Columnar pruning, predicate pushdown, compression
```

**Characteristics:**
- **Predicate pushdown**: DuckDB reads only needed columns and row groups
- **Compression**: Efficient storage and faster I/O
- **Partitioning**: Works well with hive-style partitioning

#### CSV Files (Slower)
```yaml
views:
  - name: csv_source
    sql: "SELECT * FROM read_csv_auto('data.csv')"
    # Limitation: Full scans required, less compression
```

**Performance Impact:**
- 2-5x slower than equivalent Parquet
- More memory pressure during ingestion
- Limited predicate optimization

#### External Databases (Network Dependent)
```yaml
attachments:
  - name: postgres
    type: postgres
    connection_string: "${env:POSTGRES_URL}"
```

**Factors:**
- **Network latency**: Primary bottleneck
- **Data transfer volume**: Use WHERE clauses to limit data
- **Database performance**: Source database affects overall performance

### 4. **Multi-Source Join Performance**

#### Efficient Join Patterns
```yaml
# Good: Partitioned by join key
views:
  - name: user_metrics
    sql: |
      SELECT u.id, u.name, COUNT(e.id) as event_count
      FROM users u  -- 10M rows, partitioned by id
      JOIN events e ON u.id = e.user_id  -- 100M rows, partitioned by user_id
      GROUP BY u.id, u.name
```

#### Performance Considerations
- **Data locality**: Joins work best on data from the same storage system
- **Join order**: DuckDB optimizes, but smaller tables first helps
- **Partitioning**: Align partitioning strategies across datasets

### 5. **Configuration Loading Performance**

Duckalog 0.4.0+ features a refactored configuration architecture with request-scoped caching, which significantly improves performance for complex configurations with many imports.

**Performance Characteristics:**
- **Initial Load**: Parsing, interpolating, and merging a complex configuration tree takes tens of milliseconds.
- **Cached Load**: Repeatedly loading the same configuration (e.g., in a long-running service) using a shared cache is ~1000x faster, typically completing in tens of microseconds.
- **Deep Import Trees**: Caching prevents redundant processing of files imported multiple times within the same configuration tree.

**Best Practices:**
- In long-running applications (like web servers), reuse the `RequestContext` or use the provided `request_cache_scope` to benefit from cross-request caching.
- Keep configuration trees manageable; while caching handles deep imports efficiently, extremely large trees still incur initial parsing overhead.

## Benchmark Scenarios

### Scene 1: E-commerce Analytics (10GB Parquet)
```yaml
 Dataset: 50M event records, compressed to 10GB Parquet
 Query: Daily sales metrics by product category
 Hardware: 4 CPU, 16GB RAM
 Result: ~2 seconds query time
```

### Scene 2: User Behavior Analysis (50GB Multi-source)
```yaml
 Dataset: 200M events + 10M users + 5M products
 Query: 30-day user cohort analysis
 Hardware: 8 CPU, 32GB RAM  
 Result: ~30 seconds query time
```

### Scene 3: Real-time Dashboard (1GB Rolling Window)
```yaml
 Dataset: 1GB of recent data, refreshed hourly
 Query: Dashboard metrics, 20+ concurrent users
 Hardware: 4 CPU, 16GB RAM
 Result: <500ms per query with caching
```

## Performance Optimization Strategies

### 1. **Storage Optimization**

#### Use Columnar Formats
```bash
# Convert CSV to Parquet for 5-10x performance improvement
duckalog extract-csv --source data.csv --target data.parquet
```

#### Optimize Parquet Files
```yaml
# In your data pipeline
views:
  - name: optimized_data
    sql: |
      CREATE TABLE optimized_data AS
      SELECT * FROM raw_data
      WHERE event_date >= '2024-01-01'
```

**Best Practices:**
- **File size**: 128MB-1GB Parquet files per partition
- **Compression**: SNAPPY (default) or ZSTD for better compression
- **Partitioning**: Date-based or categorical partitioning

### 2. **Query Optimization**

#### Materialize Intermediate Results
```yaml
views:
  # Step 1: Filter and prepare data
  - name: filtered_events
    sql: |
      SELECT user_id, event_type, timestamp 
      FROM raw_events 
      WHERE timestamp >= '2024-01-01'
  
  # Step 2: Join with prepared data
  - name: user_metrics
    sql: |
      SELECT u.name, COUNT(*) as event_count
      FROM users u
      JOIN filtered_events e ON u.id = e.user_id
      GROUP BY u.name
```

#### Use Appropriate Data Types
```sql
-- Good: Specific data types
CREATE TABLE events (
    user_id BIGINT,
    timestamp TIMESTAMP,
    amount DECIMAL(10,2),
    event_type VARCHAR(50)
);

-- Avoid: Generic data types
CREATE TABLE events (
    user_id TEXT,    -- Should be BIGINT
    timestamp TEXT,  -- Should be TIMESTAMP
    amount TEXT     -- Should be DECIMAL
);
```

### 3. **Configuration Optimization**

#### Memory Settings
```yaml
duckdb:
  database: analytics.duckdb
  settings:
    # Allocate sufficient memory
    memory_limit: "12GB"
    
    # Enable parallelism
    threads: 4
    
    # Optimize for your workload
    force_parallelism: true
    
    # Temporary storage for large operations
    temp_directory: "./duckdb_temp"
```

#### Connection Pooling
```yaml
# For concurrent access
duckdb:
  database: analytics.duckdb
  settings:
    # Enable multiple readers
    access_mode: "READ_ONLY"
```

## Monitoring Performance

### Built-in Monitoring
```sql
-- Check query performance
EXPLAIN ANALYZE SELECT * FROM large_table WHERE date_column = '2024-01-01';

-- Profile memory usage
PRAGMA memory_limit;
PRAGMA threads;
```

### Application-Level Monitoring
```python
import duckdb
import time

conn = duckalog.connect_to_catalog("catalog.yaml")
start_time = time.time()
result = conn.execute("SELECT COUNT(*) FROM large_table").fetchone()
query_time = time.time() - start_time
print(f"Query completed in {query_time:.2f} seconds")
```

## Scalability Limits

### Current Limitations

#### Single-Node Processing
- **Max practical dataset**: ~1TB with sufficient RAM
- **Concurrent users**: Limited by I/O and memory
- **Query complexity**: Complex joins may hit memory limits

#### Memory Constraints
```yaml
# Monitor memory usage
duckdb:
  settings:
    memory_limit: "8GB"  # Limit to available RAM
```

**Symptoms of memory pressure:**
- Queries become very slow
- Temporary file usage increases
- Out-of-memory errors for complex queries

### When to Scale Up vs Out

#### Scale Up (Single Machine)
**Signs you need more resources:**
- Queries consistently > 30 seconds
- Memory usage > 80% of available RAM
- I/O becomes bottleneck

**Solutions:**
- More RAM (16GB → 32GB → 64GB)
- Faster storage (NVMe SSDs)
- More CPU cores

#### Scale Out (Distributed)
**Signs you need distributed processing:**
- Datasets > 1TB and growing
- High concurrent query load
- Need for real-time processing

**Alternatives:**
- ClickHouse for real-time analytics
- BigQuery/Snowflake for cloud-native warehousing
- Spark for massive distributed processing

## Performance Testing

### Benchmark Your Workload
```python
import duckdb
import time
from duckalog import connect_to_catalog

def benchmark_query(conn, query, iterations=5):
    times = []
    for i in range(iterations):
        start = time.time()
        result = conn.execute(query).fetchall()
        times.append(time.time() - start)
    
    avg_time = sum(times) / len(times)
    min_time = min(times)
    max_time = max(times)
    
    print(f"Query: {query[:50]}...")
    print(f"Average: {avg_time:.2f}s, Min: {min_time:.2f}s, Max: {max_time:.2f}s")
    return avg_time

# Test your critical queries
conn = connect_to_catalog("catalog.yaml")
benchmark_query(conn, "SELECT COUNT(*) FROM large_table")
benchmark_query(conn, """
    SELECT user_id, COUNT(*) 
    FROM events 
    WHERE event_date >= '2024-01-01' 
    GROUP BY user_id
""")
```

### Performance Regression Testing
```yaml
# Add to CI/CD pipeline
name: performance-test
on: [push]
jobs:
  benchmark:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Duckalog
        run: pip install duckalog
      - name: Run benchmarks
        run: python benchmarks/performance_test.py
      - name: Check regression
        run: python benchmarks/check_regression.py
```

## Common Performance Pitfalls

### 1. **Cartesian Products**
```sql
-- BAD: Creates 1B x 1B = 1 trillion row result set
SELECT * FROM large_table1 CROSS JOIN large_table2

-- GOOD: Use specific join conditions
SELECT * FROM large_table1 JOIN large_table2 ON id1 = id2
```

### 2. **Reading Entire Datasets Unnecessarily**
```sql
-- BAD: Reads entire table, then filters in application
SELECT * FROM events

-- GOOD: Push-down filters to storage layer
SELECT * FROM events WHERE event_date >= '2024-01-01'
```

### 3. **Inefficient Data Types**
```sql
-- BAD: String operations are slow
WHERE CAST(timestamp AS TEXT) LIKE '2024-01%'

-- GOOD: Use proper date operations
WHERE timestamp >= '2024-01-01' AND timestamp < '2024-02-01'
```

## Performance Monitoring Checklist

### Regular Performance Reviews
- [ ] Check query execution times for critical business queries
- [ ] Monitor memory usage during peak hours
- [ ] Review storage costs and compression ratios
- [ ] Test performance on dataset growth projections

### Alerting Setup
- [ ] Query latency > 30 seconds
- [ ] Memory usage > 80%
- [ ] Disk space > 90% full
- [ ] Query failures due to memory limits

### Capacity Planning
- [ ] Dataset growth trends
- [ ] User growth projections
- [ ] Required performance SLAs
- [ ] Infrastructure upgrade timeline

## Conclusion

Duckalog provides excellent performance for analytical workloads through its DuckDB foundation, especially when configured and used appropriately. The key factors affecting performance are:

1. **Data size relative to available memory**
2. **Query complexity and join patterns**
3. **Data source characteristics and formats**  
4. **Hardware configuration and optimization**

By understanding these characteristics and applying the optimization strategies outlined above, you can achieve query performance ranging from milliseconds to minutes depending on your specific use case and scale requirements.

Remember that performance is a continuum - Duckalog excels at GB-TB scale analytics but may not be the right solution for petabyte-scale distributed processing or real-time transactional workloads.