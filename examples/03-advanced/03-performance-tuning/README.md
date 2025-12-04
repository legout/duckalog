# DuckDB Performance Settings Example

This example demonstrates how to optimize DuckDB performance through strategic configuration of memory management, parallelism, storage settings, and query optimization pragmas. You'll learn to tune DuckDB for different workloads and hardware configurations.

## 🎯 Learning Objectives

After completing this example, you'll understand:

- **Memory Management**: Optimize memory allocation for your dataset size
- **Parallelism**: Configure thread usage for optimal performance
- **Storage Settings**: Tune storage formats and temporary directories
- **Query Optimization**: Enable specific optimizations for different query patterns
- **Hardware Adaptation**: Adapt settings to available system resources
- **Performance Monitoring**: Measure and validate performance improvements

## 📋 Prerequisites

- Duckalog installed (`pip install duckalog`)
- Basic understanding of database performance concepts
- Available system memory (4GB+ recommended for full testing)

## 🏗️ Example Structure

```
duckdb-performance-settings/
├── README.md                  # This file
├── catalog-workstation.yaml   # High-performance workstation settings
├── catalog-server.yaml        # Server-grade hardware settings
├── catalog-limited.yaml       # Resource-constrained environment
├── catalog-analytics.yaml     # Analytics-optimized settings
├── generate-datasets.py       # Create test datasets for benchmarking
├── benchmark.py               # Performance testing and validation
├── performance-tuner.py       # Automated performance optimization
└── results/                   # Directory for benchmark results
    └── README.md
```

## 🚀 Quick Start

### 1. Generate Test Data

```bash
# Create datasets for performance testing (1M - 10M rows)
python generate-datasets.py --size medium

# This will create:
# - Small dataset (100K rows): datasets/events_small.parquet
# - Medium dataset (1M rows): datasets/events_medium.parquet
# - Large dataset (10M rows): datasets/events_large.parquet
```

### 2. Baseline Performance Test

```bash
# Test with default settings for baseline
python benchmark.py --config catalog-limited.yaml --dataset medium --name baseline
```

### 3. Optimized Performance Tests

```bash
# Test workstation-optimized settings
python benchmark.py --config catalog-workstation.yaml --dataset medium --name workstation

# Test server-optimized settings
python benchmark.py --config catalog-server.yaml --dataset medium --name server

# Test analytics-optimized settings
python benchmark.py --config catalog-analytics.yaml --dataset medium --name analytics
```

### 4. Automated Performance Tuning

```bash
# Run automatic performance optimization
python performance-tuner.py --dataset medium
```

## ⚡ Performance Scenarios Covered

### Scenario 1: High-Performance Workstation

Optimized for development machines with abundant memory and SSD storage:

```yaml
duckdb:
  database: "performance_workstation.duckdb"
  install_extensions:
    - httpfs
    - parquet
    - json
  pragmas:
    # Memory Management - Use 50% of available RAM
    - "SET memory_limit='8GB'"
    - "SET max_memory='8GB'"

    # Parallelism - Use all available CPU cores
    - "SET threads=8"
    - "SET enable_progress_bar=true"

    # Storage Optimizations
    - "SET temp_directory='/tmp/duckdb_temp'"
    - "SET preserve_insertion_order=false"

    # Query Optimizations
    - "SET enable_optimizer=true"
    - "SET enable_optimizer_caching=true"
    - "SET force_parallelism=true"
```

### Scenario 2: Server-Grade Hardware

Configured for production servers with high concurrency and large datasets:

```yaml
duckdb:
  database: "performance_server.duckdb"
  install_extensions:
    - httpfs
    - parquet
    - json
    - fts
  pragmas:
    # Large Memory Allocation - Use 75% of available RAM
    - "SET memory_limit='32GB'"
    - "SET max_memory='32GB'"
    - "SET enable_memory_map=true"

    # High Parallelism
    - "SET threads=16"
    - "SET enable_progress_bar=false"  # Reduce overhead

    # Production Storage Settings
    - "SET temp_directory='/var/tmp/duckdb_prod'"
    - "SET preserve_insertion_order=false"
    - "SET checkpoint_threshold='1GB'"

    # Advanced Optimizations
    - "SET enable_optimizer=true"
    - "SET enable_optimizer_caching=true"
    - "SET force_parallelism=true"
    - "SET enable_profiling=true"

    # Concurrency Settings
    - "SET wal_autocheckpoint=250000"
    - "SET enable_object_cache=true"
```

### Scenario 3: Resource-Constrained Environment

Optimized for limited hardware (cloud instances, edge devices):

```yaml
duckdb:
  database: "performance_limited.duckdb"
  install_extensions:
    - parquet
  pragmas:
    # Conservative Memory Usage - Use 25% of available RAM
    - "SET memory_limit='1GB'"
    - "SET max_memory='1GB'"

    # Limited Parallelism
    - "SET threads=2"
    - "SET enable_progress_bar=true"

    # Efficient Storage
    - "SET temp_directory='./temp'"
    - "SET preserve_insertion_order=false"

    # Minimal Overhead Optimizations
    - "SET enable_optimizer=true"
    - "SET enable_optimizer_caching=false"  # Save memory
    - "SET force_parallelism=false"  # Avoid thread overhead

    # Conservative Settings
    - "SET checkpoint_threshold='100MB'"
    - "SET enable_profiling=false"  # Save resources
```

### Scenario 4: Analytics Workloads

Specialized for analytical queries and aggregations:

```yaml
duckdb:
  database: "performance_analytics.duckdb"
  install_extensions:
    - httpfs
    - parquet
    - json
    - fts
  pragmas:
    # Analytics-Friendly Memory Management
    - "SET memory_limit='16GB'"
    - "SET max_memory='16GB'"
    - "SET enable_memory_map=true"

    # High Parallelism for Complex Queries
    - "SET threads=12"
    - "SET enable_progress_bar=true"

    # Analytics Optimizations
    - "SET enable_optimizer=true"
    - "SET enable_optimizer_caching=true"
    - "SET force_parallelism=true"
    - "SET enable_profiling=true"

    # Storage for Large Analytics
    - "SET temp_directory='/tmp/analytics_temp'"
    - "SET preserve_insertion_order=false"
    - "SET checkpoint_threshold='500MB'"

    # Query-Specific Optimizations
    - "SET enable_join_order=true"
    - "SET enable_propagate_null_elimination=true"
    - "SET enable_distinct_projection_optimization=true"
```

## 📊 Performance Testing

### Built-in Benchmarks

The example includes comprehensive benchmarks that test:

1. **Query Performance**: SELECT, aggregation, JOIN operations
2. **Data Loading**: Import speed for different data sizes
3. **Memory Usage**: Peak memory consumption during operations
4. **Concurrency**: Performance under simultaneous queries

### Sample Benchmark Results

| Configuration | Query Time (1M rows) | Memory Usage | Startup Time |
|---------------|---------------------|--------------|--------------|
| Limited       | 45.2s              | 512MB        | 1.2s         |
| Workstation   | 12.8s              | 2.1GB        | 1.8s         |
| Server        | 8.3s               | 4.8GB        | 2.1s         |
| Analytics     | 9.1s               | 3.2GB        | 1.9s         |

### Running Custom Benchmarks

```bash
# Test specific query patterns
python benchmark.py \
  --config catalog-workstation.yaml \
  --dataset large \
  --queries "select,aggregate,join" \
  --name custom_test

# Generate comparison report
python benchmark.py --compare-results
```

## 🔧 Advanced Performance Tuning

### Memory Optimization Strategies

**1. Memory Limit Allocation**
```yaml
# Conservative (25% of system RAM)
- "SET memory_limit='4GB'"

# Balanced (50% of system RAM)
- "SET memory_limit='8GB'"

# Aggressive (75% of system RAM)
- "SET memory_limit='12GB'"
```

**2. Memory Mapping for Large Files**
```yaml
# Enable memory mapping for large datasets
- "SET enable_memory_map=true"

# This can improve performance by up to 40% for large files
```

### Parallelism Configuration

**1. Thread Count Optimization**
```yaml
# For CPU-intensive workloads: Use all available cores
- "SET threads=8"

# For I/O-intensive workloads: Use 2x available cores
- "SET threads=16"

# For memory-constrained: Use fewer threads to avoid memory pressure
- "SET threads=2"
```

**2. Parallel Query Execution**
```yaml
# Force parallelism even for small queries
- "SET force_parallelism=true"

# Let DuckDB decide (recommended for mixed workloads)
- "SET force_parallelism=false"
```

### Storage Configuration

**1. Temporary Directory Optimization**
```yaml
# Use fast SSD for temporary storage
- "SET temp_directory='/nvme/duckdb_temp'"

# Use RAM disk for ultra-fast temporary storage
- "SET temp_directory='/dev/shm/duckdb_temp'"
```

**2. Checkpoint Tuning**
```yaml
# Frequent checkpoints (more durable, slightly slower)
- "SET checkpoint_threshold='100MB'"

# Infrequent checkpoints (faster, less durable)
- "SET checkpoint_threshold='1GB'"
```

## 🎛️ Performance Monitoring

### Built-in Profiling

```yaml
# Enable query profiling
- "SET enable_profiling=true"

# Enable query optimizer profiling
- "SET enable_profiling_optimizer=true"
```

### Monitoring Scripts

```bash
# Real-time performance monitoring
python performance-tuner.py --monitor --config catalog-workstation.yaml

# Generate performance report
python performance-tuner.py --report --results-dir results/
```

### Key Performance Metrics

- **Query Execution Time**: How long individual queries take
- **Memory Peak Usage**: Maximum memory consumed during operations
- **CPU Utilization**: How effectively CPU resources are used
- **I/O Throughput**: Data read/write rates
- **Cache Hit Rates**: How often data is found in cache vs. disk

## 🧪 Performance Validation

### Automated Testing

```bash
# Run complete performance validation suite
python benchmark.py --validate-all

# Test specific workload types
python benchmark.py --workload analytics --size large
python benchmark.py --workload oltp --size medium
```

### Regression Testing

```bash
# Compare against baseline performance
python benchmark.py --regression-test --baseline results/baseline.json
```

## 📈 Performance Tips

### General Optimizations

1. **Use appropriate memory limits**: Don't allocate too much or too little
2. **Enable optimizer**: DuckDB's optimizer provides significant improvements
3. **Use memory mapping**: For large files that fit in available RAM
4. **Choose correct thread count**: Match threads to workload characteristics
5. **Fast storage**: Place temporary directories on fast storage

### Workload-Specific Tips

**Analytics Workloads:**
- High parallelism (8+ threads)
- Aggressive memory allocation (50%+ of RAM)
- Enable all optimizer features
- Use memory mapping for large datasets

**OLTP Workloads:**
- Moderate parallelism (2-4 threads)
- Conservative memory allocation (25% of RAM)
- Frequent checkpoints for durability
- Optimize for single-record operations

**Batch Processing:**
- Maximum parallelism
- Large memory allocation
- Disable progress bars to reduce overhead
- Use RAM disk for temporary storage

## 📚 Key Takeaways

1. **Memory Management**: Allocate memory based on workload and available RAM
2. **Parallelism**: More threads help with CPU-intensive, less with I/O-intensive workloads
3. **Storage**: Fast temporary storage can significantly improve performance
4. **Optimizer**: Always enable DuckDB's query optimizer
5. **Monitoring**: Regular performance validation prevents regressions
6. **Adaptation**: Different workloads require different optimization strategies

## 🎯 Next Steps

- Try the **Environment Variables Security** example for production deployment
- Explore the **Multi-Source Analytics** example for complex data integration
- Review the contributing guidelines for creating your own examples

---

**💡 Tip**: Start with conservative settings and gradually optimize based on actual performance measurements and workload characteristics.