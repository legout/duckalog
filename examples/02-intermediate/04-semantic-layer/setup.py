#!/usr/bin/env python3
"""Generate sample data for Semantic Layer example."""

import os
import sys

# Add parent directory to path to import shared generators
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from _shared.data_generators import generate_sales, generate_users
from _shared.utils import check_prerequisites, print_separator


def main():
    """Generate sample data with customers and sales."""
    print("Semantic Layer - Setup")
    print_separator()

    # Check prerequisites
    check_prerequisites()
    print_separator()

    # Ensure data directory exists
    os.makedirs("data", exist_ok=True)

    # Generate customers (rename users to customers)
    print("Generating sample data...")
    generate_users(
        size="small", output_format="parquet", output_path="data/customers.parquet"
    )

    # Generate sales data
    generate_sales(
        size="small",
        output_format="parquet",
        output_path="data/sales.parquet",
        num_customers=100,
    )

    print_separator()
    print("Setup complete!")
    print("\nNext steps:")
    print("  1. Run: duckalog build catalog.yaml")
    print('  2. Run: duckalog query "SELECT * FROM revenue_summary"')


if __name__ == "__main__":
    main()
