#!/usr/bin/env python3
"""Generate sample data for Multi-Source Joins example."""

import os
import sys

import duckdb

# Add parent directory to path to import shared generators
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from _shared.data_generators import generate_events, generate_users
from _shared.utils import check_prerequisites, print_separator


def main():
    """Generate sample data from multiple sources."""
    print("Multi-Source Joins - Setup")
    print_separator()

    # Check prerequisites
    check_prerequisites()
    print_separator()

    # Ensure data directory exists
    os.makedirs("data", exist_ok=True)

    # Generate users as Parquet
    print("Generating Parquet data...")
        size="small", output_format="parquet", output_path="data/users.parquet"
    )

    # Generate events as Parquet
    generate_events(
        size="small",
        output_format="parquet",
        output_path="data/events.parquet",
        num_users=100,
    )

    # Generate reference data as DuckDB (profiles table)
    print("\nGenerating DuckDB reference data...")
    generate_users(
        size="small", output_format="duckdb", output_path="data/reference.duckdb"
    )

    # Add profiles table to reference DuckDB
    conn = duckdb.connect("data/reference.duckdb")
    conn.execute("""
        CREATE TABLE profiles AS
        SELECT
            id,
            name,
            country,
            'Bio for ' || name AS bio,
            'https://avatar.com/' || id::text AS avatar_url
        FROM users
    """)
    conn.close()

    print_separator()
    print("Setup complete!")
    print("\nNext steps:")
    print("  1. Run: duckalog build catalog.yaml")
    print('  2. Run: duckalog query "SELECT * FROM enriched_events LIMIT 5"')
    print("  2. Run: duckalog query \"SELECT * FROM enriched_events LIMIT 5\"")


if __name__ == "__main__":
    main()
