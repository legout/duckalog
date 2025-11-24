#!/usr/bin/env python3
"""
Generate test datasets for DuckDB performance testing.

Creates synthetic datasets of different sizes to test various performance
optimizations and query patterns.
"""

import os
import sys
import time
import argparse
from pathlib import Path
from datetime import datetime, timedelta

import numpy as np
import polars as pl
import pyarrow.dataset as ds


def create_events_dataset(num_rows):
    """Generate synthetic events data for performance testing."""
    print(f"📊 Generating {num_rows:,} events dataset...")

    np.random.seed(42)  # For reproducible results

    event_types = [
        "page_view", "click", "form_submit", "signup", "login", "logout",
        "purchase", "add_to_cart", "search", "download", "share", "comment"
    ]

    user_segments = ["free", "premium", "enterprise"]
    browsers = ["Chrome", "Firefox", "Safari", "Edge", "Mobile Safari"]
    referrers = ["direct", "google", "facebook", "twitter", "linkedin", "email", "organic"]
    page_categories = ["home", "product", "blog", "about", "contact", "pricing", "docs"]

    start_date = datetime.now() - timedelta(days=365)

    batch_size = 50_000
    total_batches = (num_rows + batch_size - 1) // batch_size

    batches: list[pl.DataFrame] = []

    for batch_num in range(total_batches):
        start_idx = batch_num * batch_size
        end_idx = min(start_idx + batch_size, num_rows)
        current_batch_size = end_idx - start_idx

        days_ago = np.random.exponential(scale=90, size=current_batch_size)
        days_ago = np.clip(days_ago, 0, 365)
        timestamps = [start_date + timedelta(days=int(day)) for day in days_ago]

        batch = pl.DataFrame(
            {
                "event_id": [f"evt_{start_idx + i:08d}" for i in range(current_batch_size)],
                "timestamp": timestamps,
                "event_type": np.random.choice(event_types, current_batch_size, p=[
                    0.35, 0.20, 0.10, 0.05, 0.08, 0.07, 0.03, 0.04, 0.03, 0.02, 0.02, 0.01
                ]),
                "user_id": [f"user_{np.random.randint(1, 50000):05d}" for _ in range(current_batch_size)],
                "session_id": [f"sess_{np.random.randint(1, 20000):05d}" for _ in range(current_batch_size)],
                "properties": [generate_event_properties() for _ in range(current_batch_size)],
            }
        )

        batches.append(batch)

        if batch_num % 10 == 0:
            print(f"  Generated {end_idx:,} / {num_rows:,} rows...")

    print("  Combining batches...")
    df = pl.concat(batches, how="vertical") if len(batches) > 1 else batches[0]

    return df


def generate_event_properties():
    """Generate realistic JSON properties for events."""
    properties = {
        "page_url": f"https://example.com/{np.random.choice(['page', 'product', 'blog'])}/{np.random.randint(1, 1000)}",
        "user_agent": np.random.choice([
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1"
        ]),
        "ip_address": f"{np.random.randint(1, 256)}.{np.random.randint(1, 256)}.{np.random.randint(1, 256)}.{np.random.randint(1, 256)}",
        "referrer": np.random.choice(["direct", "https://google.com", "https://facebook.com", "https://twitter.com", "https://linkedin.com"]),
        "page_title": f"Page Title {np.random.randint(1, 5000)}"
    }

    # Add event-specific properties
    event_specific = np.random.choice([
        {"duration": str(np.random.randint(10, 3000))},
        {"revenue": f"{np.random.uniform(0.99, 999.99):.2f}"},
        {"form_field": "email", "form_value": f"user{np.random.randint(1, 10000)}@example.com"},
        {"search_query": f"search term {np.random.randint(1, 1000)}"},
        {"button_text": np.random.choice(["Submit", "Buy Now", "Learn More", "Sign Up"])},
        {}
    ], p=[0.3, 0.2, 0.2, 0.15, 0.1, 0.05])

    properties.update(event_specific)
    return str(properties).replace("'", '"')  # Convert to JSON-like string


def write_partitioned_dataset(df: pl.DataFrame, base_dir: Path, partition_cols: list[str]) -> None:
    """Write a DataFrame as a partitioned Parquet dataset using pyarrow."""
    base_dir.mkdir(parents=True, exist_ok=True)
    partitioning = ds.partitioning(partition_cols, flavor="hive") if partition_cols else None
    ds.write_dataset(
        df.to_arrow(),
        base_dir,
        format="parquet",
        partitioning=partitioning,
        existing_data_behavior="delete_matching",
    )


def write_outputs(
    df: pl.DataFrame,
    single_path: Path,
    partition_dir: Path,
    partitioned: bool,
    partitioned_only: bool,
) -> None:
    if not partitioned_only:
        single_path.parent.mkdir(parents=True, exist_ok=True)
        df.write_parquet(single_path, compression="zstd")

    if partitioned:
        write_partitioned_dataset(df, partition_dir, ["year", "month"])


def create_directory_structure():
    """Create the necessary directory structure."""
    dirs = ["datasets", "temp", "results"]
    for dir_name in dirs:
        Path(dir_name).mkdir(exist_ok=True)
        print(f"📁 Created directory: {dir_name}")


def validate_system_resources():
    """Check if system has sufficient resources for dataset generation."""
    print("🔍 Checking system resources...")

    try:
        import psutil
        memory_gb = psutil.virtual_memory().total / (1024**3)
        cpu_cores = psutil.cpu_count()

        print(f"  Available RAM: {memory_gb:.1f} GB")
        print(f"  CPU cores: {cpu_cores}")

        if memory_gb < 2:
            print("⚠️  Warning: Low RAM detected. Consider generating smaller datasets.")
        if cpu_cores < 2:
            print("⚠️  Warning: Single-core system detected. Dataset generation may be slow.")

        return memory_gb, cpu_cores

    except ImportError:
        print("  psutil not available, skipping resource check")
        return 0, 0


def main():
    """Main function to generate datasets."""
    parser = argparse.ArgumentParser(description="Generate test datasets for DuckDB performance testing")
    parser.add_argument(
        "--size",
        choices=["small", "medium", "large", "all"],
        default="small",
        help="Dataset size to generate (small: 100K, medium: 1M, large: 10M rows)"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing datasets"
    )
    parser.add_argument(
        "--partitioned",
        action="store_true",
        help="Also write partitioned parquet output (year/month) alongside the single file",
    )
    parser.add_argument(
        "--partitioned-only",
        action="store_true",
        help="Write only partitioned parquet output (implies --partitioned)",
    )

    args = parser.parse_args()

    if args.partitioned_only:
        args.partitioned = True

    print("🚀 DuckDB Performance Test Dataset Generator")
    print("=" * 50)

    # Check system resources
    memory_gb, cpu_cores = validate_system_resources()
    print()

    # Create directory structure
    create_directory_structure()
    print()

    # Dataset sizes configuration
    dataset_configs = {
        "small": {"rows": 100_000, "filename": "events_small.parquet", "description": "Small dataset (100K rows)"},
        "medium": {"rows": 1_000_000, "filename": "events_medium.parquet", "description": "Medium dataset (1M rows)"},
        "large": {"rows": 10_000_000, "filename": "events_large.parquet", "description": "Large dataset (10M rows)"}
    }

    # Select datasets to generate
    if args.size == "all":
        datasets_to_generate = list(dataset_configs.values())
    else:
        datasets_to_generate = [dataset_configs[args.size]]

    # Generate datasets
    total_start_time = time.time()

    for config in datasets_to_generate:
        output_path = Path("datasets") / config["filename"]
        dataset_size_mb = config["rows"] * 0.001  # Rough estimate: 1KB per row

        # Check if dataset already exists
        if output_path.exists() and not args.force:
            print(f"⚠️  Dataset {config['filename']} already exists. Use --force to overwrite.")
            continue

        # Memory check for large datasets
        if config["rows"] >= 1_000_000 and memory_gb < 4:
            print(f"⚠️  Warning: Generating {config['description']} with low RAM. This may be slow.")

        print(f"📊 Generating {config['description']}...")
        print(f"   Estimated size: ~{dataset_size_mb:.0f} MB")

        start_time = time.time()
        df = create_events_dataset(config["rows"])
        df_with_partitions = df.with_columns(
            pl.col("timestamp").dt.year().alias("year"),
            pl.col("timestamp").dt.month().alias("month"),
        )

        single_output = Path("datasets") / config["filename"]
        partition_dir = Path("datasets") / f"{config['filename'].replace('.parquet', '')}_partitioned"

        write_outputs(
            df_with_partitions,
            single_output,
            partition_dir,
            partitioned=args.partitioned,
            partitioned_only=args.partitioned_only,
        )

        end_time = time.time()

        duration = end_time - start_time
        actual_rows = df.height
        rows_per_second = actual_rows / duration if duration else actual_rows

        print(f"   ✅ Completed in {duration:.1f}s ({rows_per_second:,.0f} rows/sec)")
        print(f"   ✅ Actual rows generated: {actual_rows:,}")
        if not args.partitioned_only and single_output.exists():
            print(f"   ✅ File size: {single_output.stat().st_size / (1024*1024):.1f} MB")
        if args.partitioned:
            print(f"   ✅ Partitioned output: {partition_dir}")
        print(
            f"   ✅ Date range: {df['timestamp'].min()} to {df['timestamp'].max()} | "
            f"Event types: {df['event_type'].n_unique()} | Users: {df['user_id'].n_unique()}"
        )
        print()

    total_duration = time.time() - total_start_time
    print(f"🎉 Dataset generation completed in {total_duration:.1f} seconds!")
    print()
    print("📋 Generated datasets:")
    for name, config in dataset_configs.items():
        output_path = Path("datasets") / config["filename"]
        if output_path.exists():
            size_mb = output_path.stat().st_size / (1024*1024)
            print(f"  ✅ {config['filename']}: {size_mb:.1f} MB")

    print()
    print("🚀 Next steps:")
    print("1. Build a performance catalog: duckalog build catalog-workstation.yaml")
    print("2. Run benchmarks: python benchmark.py --config catalog-workstation.yaml")
    print("3. Compare configurations: python benchmark.py --compare-results")


if __name__ == "__main__":
    main()
