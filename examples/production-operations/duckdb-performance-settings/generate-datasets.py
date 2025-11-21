#!/usr/bin/env python3
"""
Generate test datasets for DuckDB performance testing.

Creates synthetic datasets of different sizes to test various performance
optimizations and query patterns.
"""

import os
import sys
import time
import duckdb
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
import argparse


def create_events_dataset(num_rows, output_path):
    """Generate synthetic events data for performance testing."""
    print(f"📊 Generating {num_rows:,} events dataset...")

    # Seed for reproducible results
    np.random.seed(42)

    # Define data characteristics
    event_types = [
        "page_view", "click", "form_submit", "signup", "login", "logout",
        "purchase", "add_to_cart", "search", "download", "share", "comment"
    ]

    user_segments = ["free", "premium", "enterprise"]
    browsers = ["Chrome", "Firefox", "Safari", "Edge", "Mobile Safari"]
    referrers = ["direct", "google", "facebook", "twitter", "linkedin", "email", "organic"]
    page_categories = ["home", "product", "blog", "about", "contact", "pricing", "docs"]

    start_date = datetime.now() - timedelta(days=365)

    # Generate data in batches to manage memory
    batch_size = 50000
    total_batches = (num_rows + batch_size - 1) // batch_size

    all_data = []

    for batch_num in range(total_batches):
        start_idx = batch_num * batch_size
        end_idx = min(start_idx + batch_size, num_rows)
        current_batch_size = end_idx - start_idx

        # Generate timestamps (more recent events are more common)
        days_ago = np.random.exponential(scale=90, size=current_batch_size)
        days_ago = np.clip(days_ago, 0, 365)
        timestamps = [start_date + timedelta(days=int(day)) for day in days_ago]

        # Generate event data
        batch_data = {
            "event_id": [f"evt_{start_idx + i:08d}" for i in range(current_batch_size)],
            "timestamp": timestamps,
            "event_type": np.random.choice(event_types, current_batch_size, p=[
                0.35, 0.20, 0.10, 0.05, 0.08, 0.07, 0.03, 0.04, 0.03, 0.02, 0.02, 0.01
            ]),
            "user_id": [f"user_{np.random.randint(1, 50000):05d}" for _ in range(current_batch_size)],
            "session_id": [f"sess_{np.random.randint(1, 20000):05d}" for _ in range(current_batch_size)],
            "properties": [generate_event_properties() for _ in range(current_batch_size)]
        }

        df_batch = pd.DataFrame(batch_data)
        all_data.append(df_batch)

        if batch_num % 10 == 0:
            print(f"  Generated {end_idx:,} / {num_rows:,} rows...")

    # Combine all batches
    print("  Combining batches...")
    df = pd.concat(all_data, ignore_index=True)

    # Save to Parquet
    print(f"  Saving to {output_path}...")
    df.to_parquet(output_path, index=False, compression='snappy')

    # Validate the generated data
    print("  Validating dataset...")
    validation_df = pd.read_parquet(output_path)
    print(f"  ✅ Generated {len(validation_df):,} rows")
    print(f"  ✅ Date range: {validation_df['timestamp'].min()} to {validation_df['timestamp'].max()}")
    print(f"  ✅ Unique event types: {validation_df['event_type'].nunique()}")
    print(f"  ✅ Unique users: {validation_df['user_id'].nunique()}")

    return len(validation_df)


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

    args = parser.parse_args()

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
        actual_rows = create_events_dataset(config["rows"], output_path)
        end_time = time.time()

        duration = end_time - start_time
        rows_per_second = actual_rows / duration

        print(f"   ✅ Completed in {duration:.1f}s ({rows_per_second:,.0f} rows/sec)")
        print(f"   ✅ Actual rows generated: {actual_rows:,}")
        print(f"   ✅ File size: {output_path.stat().st_size / (1024*1024):.1f} MB")
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