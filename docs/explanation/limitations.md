# Limitations and Known Issues

Understanding Duckalog's limitations helps you make informed decisions and avoid common pitfalls.

## Current Limitations

### 🚨 **Critical Limitations**

#### Single-Node Architecture
**Issue**: Duckalog runs on a single machine, not distributed
- **Maximum practical dataset**: ~1TB with sufficient RAM
- **No horizontal scaling**: Cannot distribute across multiple nodes
- **Single point of failure**: Machine failure affects entire catalog

**Workarounds**:
```yaml
# Partition data to stay within memory limits
views:
  - name: daily_events
    sql: |
      SELECT * FROM raw_events 
      WHERE event_date = '2024-01-01'  # Process one day at time
```

**Alternatives**: ClickHouse, BigQuery, Snowflake for distributed processing

#### No Write-Ahead Logging (WAL)
**Issue**: Database file corruption can occur if process crashes during writes
- **Risk**: Data loss if DuckDB process crashes mid-operation
- **Recovery**: May need to rebuild from scratch using configuration file

**Mitigation**:
```yaml
# Regular backups of configuration and data
# Use atomic operations where possible
```

**Alternatives**: PostgreSQL for transactional integrity

### ⚠️ **Significant Limitations**

#### Memory-Intensive Operations
**Issue**: Large joins and complex queries may exceed available memory
- **Symptoms**: Out-of-memory errors, very slow performance
- **Common triggers**: Self-joins, window functions on large datasets

**Detection**:
```sql
-- Monitor memory usage
PRAGMA memory_limit;
PRAGMA current_memory_usage;
```

**Solutions**:
```yaml
duckdb:
  settings:
    memory_limit: "8GB"  # Limit memory usage
    temp_directory: "./temp"  # Disk overflow
```

#### Concurrency Limitations
**Issue**: Limited support for concurrent writers/readers
- **Multiple writers**: Not supported (can corrupt database)
- **Read concurrency**: Limited by file locks and memory pressure
- **Dashboard users**: More than 10-20 concurrent users may degrade performance

**Best Practices**:
- Use read-only mode for analytics workloads
- Implement proper connection pooling
- Schedule write operations during low usage periods

#### External Database Dependencies
**Issue**: Performance and reliability depend on external databases
- **Network latency**: Major bottleneck for remote databases
- **Connection stability**: Failures affect catalog operations
- **Data transfer volume**: May be limited by network bandwidth

**Mitigation**:
```yaml
# Cache frequently accessed data locally
views:
  - name: cached_reference
    sql: |
      CREATE TABLE cached_reference AS
      SELECT * FROM postgres_reference LIMIT 1000000
```

### 🔧 **Functional Limitations**

#### Limited Real-time Capabilities
**Issue**: Not designed for streaming or real-time analytics
- **Near real-time**: Possible with frequent rebuilds (minutes)
- **Streaming**: Not supported
- **Low-latency queries**: Millisecond latency not guaranteed

**Alternatives**: Apache Flink, Apache Kafka + ClickHouse

#### No Automatic Scaling
**Issue**: Cannot automatically scale resources based on load
- **Manual scaling**: Requires infrastructure changes
- **Resource planning**: Must provision for peak load
- **Cost optimization**: Fixed resource allocation

#### Limited Data Type Support
**Issue**: Some advanced data types not fully supported
- **Geospatial**: Limited DuckDB geospatial support
- **JSON/JSONB**: Basic support, limited query capabilities
- **Arrays/Structures**: Supported but with performance considerations

## Known Issues

### 🐛 **Bug Reports and Workarounds**

#### Issue #1: Large External Parquet Files
**Problem**: Reading very large Parquet files (>10GB) may cause memory issues
**Status**: Open  
**Workaround**: Split into smaller files or use filters during ingestion
```yaml
views:
  - name: large_parquet
    sql: |
      SELECT * FROM read_parquet('huge_file.parquet') 
      WHERE date_column >= '2024-01-01'  # Reduce initial load
```

#### Issue #2: Iceberg Catalog Integration
**Problem**: Some Iceberg catalogs have compatibility issues with DuckDB
**Status**: In progress
**Workaround**: Use Parquet export from Iceberg tables first
```bash
# Export from Spark then ingest with Duckalog
spark.sql("COPY iceberg_db.table TO 'path/hadoop' FORMAT PARQUET")
```

#### Issue #3: DuckDB Version Compatibility
**Problem**: Duckalog may lag behind latest DuckDB releases
**Status**: Tracking in #452
**Workaround**: Use supported DuckDB versions, monitor compatibility matrix

### ⚠️ **Performance Issues**

#### Issue #10: Query Performance Degradation
**Problem**: Query performance may degrade after many catalog rebuilds
**Root Cause**: Database fragmentation from frequent table recreation
**Solution**:
```yaml
# Periodic database optimization
duckalog:
  settings:
    # Enable automatic vacuuming
    enable_progress_bar: false  # Reduces overhead
```

**Manual fix**:
```sql
VACUUM;  -- Reclaim space
PRAGMA optimize;  -- Optimize query plans
```

#### Issue #15: Memory Leaks in Long-running Processes
**Problem**: Memory usage slowly increases in long-running daemon processes
**Status**: Investigating in #478
**Workaround**: Regular process restarts or connection recycling
```python
# Periodically recycle connections
if time.time() - start_time > 3600:  # 1 hour
    conn.close()
    conn = connect_to_catalog("catalog.yaml")
```

### 🔧 **Integration Issues**

#### Issue #20: S3 Authentication Timing
**Problem**: S3 credentials may expire during long-running operations
**Severity**: Medium
**Solution**: Refresh credentials or use long-lived credentials
```yaml
# Use instance profiles or long-lived tokens
attachments:
  - name: s3_data
    uri: "s3://bucket/data/"
    # Prefer AWS profiles over temporary credentials
```

#### Issue #25: Windows Path Handling
**Problem**: Path resolution issues on Windows with backslashes
**Severity**: Low (Windows-specific)
**Solution**: Use forward slashes in configurations
```yaml
# Use forward slashes even on Windows
views:
  - name: local_data
    source: parquet
    uri: "C:/data/files/"  # Not "C:\data\files\"
```

## Mitigation Strategies

### 🛡️ **Preventive Measures**

#### Regular Health Checks
```python
def catalog_health_check(catalog_path):
    """Monitor catalog health and performance"""
    try:
        conn = connect_to_catalog(catalog_path)
        
        # Test basic functionality
        result = conn.execute("SELECT 1").fetchone()
        
        # Check memory usage
        memory = conn.execute("PRAGMA current_memory_usage").fetchone()
        
        # Test file accessibility
        conn.execute("SELECT COUNT(*) FROM information_schema.tables").fetchall()
        
        return True, f"Memory usage: {memory}"
    except Exception as e:
        return False, str(e)
```

#### Backup and Recovery
```bash
#!/bin/bash
# Backup script
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="backups/$DATE"

# Backup configuration
cp catalog.yaml "$BACKUP_DIR/catalog.yaml"

# Backup database (if exists and not corrupted)
duckdb catalog.duckdb ".backup $BACKUP_DIR/catalog.duckdb" 2>/dev/null

# Store backup metadata
echo "Backup created: $DATE" >> backup.log
```

#### Monitoring Dashboard
```yaml
# Add to your monitoring system
metrics:
  - catalog_build_duration_seconds
  - catalog_build_success_rate
  - query_response_time_p95
  - database_size_bytes
  - memory_usage_bytes
```

### 🔧 **Recovery Procedures**

#### Database Corruption Recovery
```bash
# 1. Identify corruption
duckdb broken.duckdb "PRAGMA database_list"

# 2. Attempt repair (may lose recent changes)
duckdb broken.duckdb "PRAGMA integrity_check"

# 3. Rebuild from configuration (most reliable)
duckalog build catalog.yaml --db-path new_catalog.duckdb

# 4. Migrate existing data if possible
duckdb new_catalog.duckdb "ATTACH 'broken.duckdb' AS old; INSERT INTO main.views SELECT * FROM old.views"
```

#### Performance Degradation Recovery
```sql
-- Complete database cleanup
VACUUM;                    -- Reclaim space
PRAGMA optimize;           -- Re-optimize indexes
PRAGMA progress_bar=false; -- Reduce overhead
ANALYZE;                   -- Update statistics
```

## Future Roadmap

### 🚧 **Planned Improvements**

#### Distributed Processing Support (Q2 2024)
- Multi-node DuckDB integration
- Automatic partitioning strategies
- Load balancing across nodes

#### Enhanced Concurrency (Q3 2024)
- Read/write separation
- Connection pooling improvements
- Better multi-user dashboard support

#### Streaming Integration (Q4 2024)
- incremental updates
- Change data capture (CDC)
- Real-time view refreshing

### 📋 **Under Consideration**

#### Advanced Authentication
- OAuth 2.0 support for external databases  
- Service account management
- Multi-tenant support

#### Cloud-native Features
- Automatic scaling based on load
- Managed storage integration
- Cost optimization recommendations

#### Enhanced Monitoring
- Built-in performance dashboards
- Automated alerting
- Predictive scaling recommendations

## Contributing to Issue Resolution

### 🐛 **Reporting Issues**

When reporting issues, include:

1. **Environment**: OS, Python version, Duckalog version, DuckDB version
2. **Configuration**: Sanitized catalog configuration
3. **Error details**: Full error messages and stack traces
4. **Reproduction steps**: Minimal steps to reproduce the issue
5. **Expected vs actual**: What you expected vs what happened

### 🔧 **Contributing Fixes**

1. **Fork repository**: Create a feature branch
2. **Add tests**: Include reproduction case in test suite
3. **Document changes**: Update relevant documentation
4. **Submit pull request**: With clear description of changes

## Conclusion

Duckalog is designed for specific use cases and scales excellently within its intended domain. The limitations listed above are largely intentional design trade-offs to maintain simplicity and performance for target workloads.

Key takeaways:

1. **Know your scale**: Duckalog excels at GB-TB analytical workloads
2. **Plan for growth**: Monitor performance and plan migration paths
3. **Implement safeguards**: Regular backups and health checks
4. **Choose the right tool**: Understand when to use alternatives

By understanding these limitations and planning accordingly, you can build robust, maintainable data pipelines using Duckalog while avoiding common pitfalls.

For the most current status on these issues, check the [GitHub Issues](https://github.com/legout/duckalog/issues) and [Roadmap](https://github.com/legout/duckalog/projects) pages.