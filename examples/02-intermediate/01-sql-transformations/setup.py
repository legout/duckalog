#!/usr/bin/env python3
"""Generate sample data for SQL Transformations example."""

import os
import sys

# Add parent directory to path to import shared generators
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from _shared.data_generators import generate_events, generate_users
from _shared.utils import check_prerequisites, print_separator


def main():
    """Generate sample data with users and events."""
    print("SQL Transformations - Setup")
    print_separator()

    # Check prerequisites
    check_prerequisites()
    print_separator()

    # Ensure data directory exists
    os.makedirs("data", exist_ok=True)

    # Generate users and events
    print("Generating sample data...")
    generate_users(
        size="small", output_format="parquet", output_path="data/users.parquet"
    )

    generate_events(
        size="small",
        output_format="parquet",
        output_path="data/events.parquet",
        num_users=100,
    )

    print_separator()
    print("Setup complete!")
    print("\nNext steps:")
    print("  1. Run: duckalog build catalog.yaml")
    print('  2. Run: duckalog query "SELECT * FROM daily_metrics LIMIT 5"')
    print(
        '  3. Run: duckalog query "SELECT * FROM user_summary WHERE total_events > 5"'
    )


if __name__ == "__main__":
    main()
