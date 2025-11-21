# Benchmark Results

This directory contains performance benchmark results for different DuckDB configurations.

## File Naming Convention

Results are saved with the following naming pattern:
```
benchmark_{config-name}_{timestamp}.json
```

Example: `benchmark_workstation_20241121_143022.json`

## Result Structure

Each result file contains:
- `config_name`: Name of the tested configuration
- `dataset_size`: Dataset size used for testing (small/medium/large)
- `timestamp`: When the benchmark was run
- `benchmarks`: Array of individual benchmark results

## Benchmark Metrics

Each benchmark includes:
- `query_name`: Name of the benchmark query
- `duration_seconds`: Query execution time
- `rows_returned`: Number of rows returned
- `rows_per_second`: Query throughput
- `memory_before/memory_after`: Memory usage before/after query
- `success`: Whether the query completed successfully
- `error`: Error message (if failed)

## Comparing Results

To compare results between configurations:

```bash
# Compare current run with baseline
python benchmark.py --compare results/baseline_workstation.json

# List all available result files
python benchmark.py --list-results
```

## Performance Analysis

Use the results to:

1. **Identify Bottlenecks**: Find which queries are slowest
2. **Compare Configurations**: See how different settings affect performance
3. **Track Regressions**: Monitor performance changes over time
4. **Optimize Settings**: Choose optimal configuration for your workload

## Sample Performance Insights

Based on benchmark results, typical performance patterns:

- **Limited**: 2-4x slower than workstation configurations
- **Workstation**: Good balance of performance and resource usage
- **Server**: 2-3x faster than workstation for large datasets
- **Analytics**: Optimized for complex analytical queries

Results will vary based on hardware specifications and data characteristics.