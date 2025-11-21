#!/usr/bin/env python3
"""
Performance benchmarking script for DuckDB configurations.

Tests different DuckDB performance settings and measures query execution
times, memory usage, and other performance metrics.
"""

import os
import sys
import time
import json
import statistics
from pathlib import Path
from datetime import datetime
import argparse
import duckdb
import pandas as pd


class PerformanceBenchmark:
    """Comprehensive performance benchmarking for DuckDB."""

    def __init__(self, config_path, dataset_size="medium"):
        self.config_path = config_path
        self.dataset_size = dataset_size
        self.results = {
            "config_name": Path(config_path).stem,
            "dataset_size": dataset_size,
            "timestamp": datetime.now().isoformat(),
            "benchmarks": []
        }

    def load_config(self):
        """Load and parse the Duckalog configuration."""
        try:
            from duckalog import load_config
            config = load_config(self.config_path)
            return config
        except Exception as e:
            print(f"❌ Failed to load config {self.config_path}: {e}")
            return None

    def setup_database(self, config):
        """Set up DuckDB database with the given configuration."""
        # Use in-memory database with configuration applied
        con = duckdb.connect(':memory:')

        # Apply pragmas from configuration
        if hasattr(config.duckdb, 'pragmas') and config.duckdb.pragmas:
            for pragma in config.duckdb.pragmas:
                try:
                    con.execute(pragma)
                except Exception as e:
                    print(f"⚠️  Warning: Failed to apply pragma '{pragma}': {e}")

        return con

    def get_memory_usage(self, connection):
        """Get current memory usage from DuckDB."""
        try:
            result = connection.execute("PRAGMA memory_limit").fetchone()
            if result:
                return result[0]
        except:
            pass
        return "unknown"

    def run_benchmark_query(self, connection, query_name, query_sql):
        """Run a single benchmark query and measure performance."""
        print(f"  📊 Running {query_name}...")

        # Clear caches between runs
        connection.execute("CLEAR CACHE")

        # Measure performance
        start_time = time.time()
        start_memory = self.get_memory_usage(connection)

        try:
            result = connection.execute(query_sql).fetchall()
            end_time = time.time()
            end_memory = self.get_memory_usage(connection)

            # Calculate metrics
            duration = end_time - start_time
            row_count = len(result)

            benchmark_result = {
                "query_name": query_name,
                "duration_seconds": duration,
                "rows_returned": row_count,
                "rows_per_second": row_count / duration if duration > 0 else 0,
                "memory_before": str(start_memory),
                "memory_after": str(end_memory),
                "success": True,
                "error": None
            }

            print(f"    ✅ {duration:.3f}s, {row_count:,} rows ({row_count/duration:,.0f} rows/sec)")
            return benchmark_result

        except Exception as e:
            print(f"    ❌ Failed: {e}")
            return {
                "query_name": query_name,
                "duration_seconds": 0,
                "rows_returned": 0,
                "rows_per_second": 0,
                "memory_before": str(start_memory),
                "memory_after": str(end_memory),
                "success": False,
                "error": str(e)
            }

    def run_full_benchmark(self, connection):
        """Run the complete benchmark suite."""
        print("🏃‍♂️ Running performance benchmark suite...")

        benchmark_queries = [
            ("simple_select", """
                SELECT COUNT(*) as total_events
                FROM events_medium
            """),

            ("simple_aggregation", """
                SELECT event_type, COUNT(*) as event_count
                FROM events_medium
                GROUP BY event_type
                ORDER BY event_count DESC
            """),

            ("complex_aggregation", """
                SELECT
                    event_type,
                    COUNT(*) as event_count,
                    COUNT(DISTINCT user_id) as unique_users,
                    AVG(CAST(properties->>'duration' AS INTEGER)) as avg_duration
                FROM events_medium
                WHERE timestamp >= CURRENT_DATE - INTERVAL '30 days'
                GROUP BY event_type
                HAVING COUNT(*) > 100
                ORDER BY event_count DESC
            """),

            ("join_operation", """
                WITH daily_stats AS (
                    SELECT
                        DATE(timestamp) as event_date,
                        event_type,
                        COUNT(*) as daily_count
                    FROM events_medium
                    GROUP BY DATE(timestamp), event_type
                ),
                user_stats AS (
                    SELECT
                        user_id,
                        COUNT(*) as total_events
                    FROM events_medium
                    GROUP BY user_id
                )
                SELECT
                    d.event_date,
                    d.event_type,
                    d.daily_count,
                    u.total_events
                FROM daily_stats d
                LEFT JOIN user_stats u ON d.daily_count > 100
                WHERE d.daily_count > 50
                ORDER BY d.event_date DESC, d.daily_count DESC
                LIMIT 1000
            """),

            ("window_function", """
                SELECT
                    user_id,
                    event_type,
                    timestamp,
                    ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY timestamp DESC) as event_rank,
                    LAG(timestamp, 1) OVER (PARTITION BY user_id ORDER BY timestamp) as prev_event
                FROM events_medium
                WHERE user_id IS NOT NULL
                AND timestamp >= CURRENT_DATE - INTERVAL '7 days'
                LIMIT 10000
            """),

            ("string_operations", """
                SELECT
                    event_type,
                    COUNT(*) as total_events,
                    COUNT(CASE WHEN properties->>'page_url' LIKE '%product%' THEN 1 END) as product_pages,
                    AVG(LENGTH(properties->>'page_title')) as avg_title_length
                FROM events_medium
                WHERE properties IS NOT NULL
                GROUP BY event_type
            """)
        ]

        # Adapt queries based on available views
        try:
            existing_views = connection.execute("""
                SELECT table_name FROM information_schema.tables
                WHERE table_schema = 'main' AND table_type = 'VIEW'
            """).fetchall()
            view_names = [row[0] for row in existing_views]

            # Use available views if they exist
            if 'test_aggregation' in view_names:
                benchmark_queries.append(("view_aggregation", "SELECT * FROM test_aggregation LIMIT 1000"))
            if 'test_join' in view_names:
                benchmark_queries.append(("view_join", "SELECT * FROM test_join LIMIT 1000"))
            if 'funnel_analysis' in view_names:
                benchmark_queries.append(("analytics_funnel", "SELECT * FROM funnel_analysis"))

        except Exception as e:
            print(f"  ⚠️  Could not check available views: {e}")

        # Run all benchmarks
        for query_name, query_sql in benchmark_queries:
            result = self.run_benchmark_query(connection, query_name, query_sql)
            self.results["benchmarks"].append(result)

        print("✅ Benchmark suite completed")

    def save_results(self, output_dir="results"):
        """Save benchmark results to a JSON file."""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"benchmark_{self.results['config_name']}_{timestamp}.json"
        filepath = output_path / filename

        with open(filepath, 'w') as f:
            json.dump(self.results, f, indent=2)

        print(f"💾 Results saved to: {filepath}")
        return filepath

    def print_summary(self):
        """Print a summary of benchmark results."""
        print("\n📊 Benchmark Summary")
        print("=" * 50)
        print(f"Configuration: {self.results['config_name']}")
        print(f"Dataset Size: {self.results['dataset_size']}")
        print(f"Timestamp: {self.results['timestamp']}")

        successful_benchmarks = [b for b in self.results["benchmarks"] if b["success"]]
        failed_benchmarks = [b for b in self.results["benchmarks"] if not b["success"]]

        print(f"\n✅ Successful benchmarks: {len(successful_benchmarks)}")
        print(f"❌ Failed benchmarks: {len(failed_benchmarks)}")

        if successful_benchmarks:
            durations = [b["duration_seconds"] for b in successful_benchmarks]
            throughputs = [b["rows_per_second"] for b in successful_benchmarks if b["rows_per_second"] > 0]

            print(f"\n⏱️  Performance Metrics:")
            print(f"   Average query time: {statistics.mean(durations):.3f}s")
            print(f"   Fastest query: {min(durations):.3f}s")
            print(f"   Slowest query: {max(durations):.3f}s")

            if throughputs:
                print(f"   Average throughput: {statistics.mean(throughputs):,.0f} rows/sec")
                print(f"   Peak throughput: {max(throughputs):,.0f} rows/sec")

        if failed_benchmarks:
            print(f"\n❌ Failed Queries:")
            for benchmark in failed_benchmarks:
                print(f"   {benchmark['query_name']}: {benchmark['error']}")

    def compare_with_baseline(self, baseline_path):
        """Compare current results with a baseline."""
        try:
            with open(baseline_path, 'r') as f:
                baseline = json.load(f)

            print(f"\n📈 Comparison with baseline: {Path(baseline_path).stem}")
            print("=" * 50)

            current_results = {b["query_name"]: b for b in self.results["benchmarks"] if b["success"]}
            baseline_results = {b["query_name"]: b for b in baseline["benchmarks"] if b["success"]}

            for query_name in current_results:
                if query_name in baseline_results:
                    current = current_results[query_name]
                    baseline = baseline_results[query_name]

                    duration_change = (current["duration_seconds"] - baseline["duration_seconds"]) / baseline["duration_seconds"] * 100
                    throughput_change = (current["rows_per_second"] - baseline["rows_per_second"]) / baseline["rows_per_second"] * 100 if baseline["rows_per_second"] > 0 else 0

                    print(f"{query_name}:")
                    print(f"  Duration: {current['duration_seconds']:.3f}s vs {baseline['duration_seconds']:.3f}s ({duration_change:+.1f}%)")
                    print(f"  Throughput: {current['rows_per_second']:,.0f} vs {baseline['rows_per_second']:,.0f} rows/sec ({throughput_change:+.1f}%)")

        except Exception as e:
            print(f"❌ Could not compare with baseline: {e}")


def main():
    """Main benchmark execution function."""
    parser = argparse.ArgumentParser(description="DuckDB Performance Benchmark")
    parser.add_argument("--config", required=True, help="Path to catalog configuration file")
    parser.add_argument("--dataset", default="medium", choices=["small", "medium", "large"], help="Dataset size to test")
    parser.add_argument("--name", help="Custom name for this benchmark run")
    parser.add_argument("--output", default="results", help="Output directory for results")
    parser.add_argument("--compare", help="Compare results with baseline file")
    parser.add_argument("--list-results", action="store_true", help="List all available result files")

    args = parser.parse_args()

    # List available results and exit if requested
    if args.list_results:
        results_dir = Path(args.output)
        if results_dir.exists():
            result_files = list(results_dir.glob("benchmark_*.json"))
            if result_files:
                print(f"📁 Available result files in {args.output}:")
                for file in sorted(result_files):
                    print(f"  {file.name}")
            else:
                print(f"📁 No result files found in {args.output}")
        else:
            print(f"📁 Results directory {args.output} does not exist")
        return

    print("🚀 DuckDB Performance Benchmark")
    print("=" * 50)
    print(f"Configuration: {args.config}")
    print(f"Dataset: {args.dataset}")

    # Initialize benchmark
    benchmark = PerformanceBenchmark(args.config, args.dataset)

    # Load configuration
    config = benchmark.load_config()
    if config is None:
        sys.exit(1)

    # Set up database
    print("\n🔧 Setting up database with performance settings...")
    connection = benchmark.setup_database(config)

    # Check dataset availability
    dataset_path = Path("datasets") / f"events_{args.dataset}.parquet"
    if not dataset_path.exists():
        print(f"❌ Dataset {dataset_path} not found. Run 'python generate-datasets.py --size {args.dataset}' first.")
        sys.exit(1)

    print(f"✅ Using dataset: {dataset_path}")

    # Load dataset into view
    try:
        view_name = f"events_{args.dataset}"
        connection.execute(f"CREATE OR REPLACE VIEW {view_name} AS SELECT * FROM '{dataset_path}'")
        print(f"✅ Created view {view_name}")
    except Exception as e:
        print(f"❌ Failed to create view: {e}")
        sys.exit(1)

    # Run benchmark
    print("\n" + "=" * 50)
    start_time = time.time()
    benchmark.run_full_benchmark(connection)
    total_time = time.time() - start_time

    # Print summary
    benchmark.print_summary()
    print(f"\n⏱️  Total benchmark time: {total_time:.2f}s")

    # Save results
    results_path = benchmark.save_results(args.output)

    # Compare with baseline if requested
    if args.compare:
        benchmark.compare_with_baseline(args.compare)

    # Close connection
    connection.close()

    print(f"\n🎉 Benchmark completed!")
    print(f"📊 Results saved to: {results_path}")
    print(f"📈 To compare runs: python benchmark.py --compare {results_path}")


if __name__ == "__main__":
    main()