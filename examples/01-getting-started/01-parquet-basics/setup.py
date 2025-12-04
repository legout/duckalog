#!/usr/bin/env python3
"""Generate sample data for Parquet Basics example."""

import os
import sys

# Add parent directory to path to import shared generators
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from _shared.data_generators import generate_users
from _shared.utils import check_prerequisites, print_separator


def main():
    """Generate sample user data."""
    print("Parquet Basics - Setup")
    print_separator()

    # Check prerequisites
    check_prerequisites()
    print_separator()

    # Ensure data directory exists
    os.makedirs("data", exist_ok=True)

    # Generate users data
    print("Generating sample data...")
    generate_users(
        size="small", output_format="parquet", output_path="data/users.parquet"
    )

    print_separator()
    print("Setup complete!")
    print("\nNext steps:")
    print("  1. Run: duckalog build catalog.yaml")
    print('  2. Run: duckalog query "SELECT COUNT(*) FROM users"')


if __name__ == "__main__":
    main()
