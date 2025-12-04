#!/usr/bin/env python3
"""Generate sample data for SQLite Attachment example."""

import os
import sys

# Add parent directory to path to import shared generators
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from _shared.data_generators import generate_sales, generate_users
from _shared.utils import check_prerequisites, print_separator


def main():
    """Generate sample data in a SQLite database."""
    print("SQLite Attachment - Setup")
    print_separator()

    # Check prerequisites
    check_prerequisites()
    print_separator()

    # Ensure data directory exists
    os.makedirs("data", exist_ok=True)

    # Generate users data (as customers)
    print("Generating sample data...")
    generate_users(size="small", output_format="sqlite", output_path="data/legacy.db")

    # Generate sales data (as orders)
    generate_sales(size="small", output_format="sqlite", output_path="data/legacy.db")

    print_separator()
    print("Setup complete!")
    print("\nNext steps:")
    print("  1. Run: duckalog build catalog.yaml")
    print('  2. Run: duckalog query "SELECT COUNT(*) FROM legacy.users"')
    print('  3. Run: duckalog query "SELECT * FROM legacy.sales LIMIT 5"')


if __name__ == "__main__":
    main()
