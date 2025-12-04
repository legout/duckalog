#!/usr/bin/env python3
"""
Generate test data for the environment variables security example.

This script creates sample data to demonstrate the security features
without requiring real credentials or data sources.
"""

import os
import sys
import duckdb
import numpy as np
import polars as pl
from pathlib import Path
from datetime import datetime, timedelta


def create_reference_database():
    """Create a reference database with sample data."""
    print("🔧 Creating reference database...")

    ref_path = Path("reference_data.duckdb")
    con = duckdb.connect(str(ref_path))

    # Create reference tables
    con.execute("""
        CREATE TABLE reference_tables (
            id INTEGER,
            category VARCHAR(50),
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Insert sample reference data
    reference_data = [
        (1, "analytics", "Analytics and metrics data", datetime.now()),
        (2, "user_data", "User profile and activity data", datetime.now()),
        (3, "transactions", "Financial transaction records", datetime.now()),
        (4, "events", "System events and logs", datetime.now()),
        (5, "reports", "Generated reports and summaries", datetime.now())
    ]

    con.executemany(
        "INSERT INTO reference_tables VALUES (?, ?, ?, ?)",
        reference_data
    )

    print(f"✅ Reference database created: {ref_path}")
    con.close()


def generate_sample_parquet_data():
    """Generate sample Parquet data files to simulate S3 data."""
    print("📊 Generating sample Parquet data...")

    # Create data directory
    data_dir = Path("sample_data")
    data_dir.mkdir(exist_ok=True)

    # Generate events data
    np.random.seed(42)  # For reproducible data

    event_types = ["page_view", "click", "purchase", "login", "logout", "search", "data_access"]
    user_segments = ["free", "premium", "enterprise"]
    regions = ["us-east-1", "us-west-2", "eu-west-1", "ap-southeast-1"]

    events_data = []
    for i in range(10000):
        timestamp = datetime.now() - timedelta(days=np.random.randint(0, 90))
        events_data.append({
            "event_id": f"evt_{i:06d}",
            "timestamp": timestamp,
            "event_type": np.random.choice(event_types),
            "user_id": f"user_{np.random.randint(1, 1000):04d}",
            "properties": f'{{"session_id": "sess_{np.random.randint(1, 500):03d}", "ip": "192.168.{np.random.randint(1, 255)}.{np.random.randint(1, 255)}"}}',
            "category_id": np.random.randint(1, 6)
        })

    events_df = pl.DataFrame(events_data)
    events_file = data_dir / "events_sample.parquet"
    events_df.write_parquet(events_file, compression="zstd")
    print(f"✅ Events data created: {events_file} ({len(events_df):,} records)")

    # Generate user profiles data
    user_data = []
    for i in range(1000):
        user_data.append({
            "user_id": f"user_{i:04d}",
            "email": f"user{i}@example.com",
            "segment": np.random.choice(user_segments),
            "region": np.random.choice(regions),
            "created_at": datetime.now() - timedelta(days=np.random.randint(30, 365)),
            "updated_at": datetime.now() - timedelta(days=np.random.randint(0, 30))
        })

    users_df = pl.DataFrame(user_data)
    users_file = data_dir / "users_sample.parquet"
    users_df.write_parquet(users_file, compression="zstd")
    print(f"✅ User profiles created: {users_file} ({len(users_df):,} records)")

    return events_file, users_file


def setup_environment_file():
    """Set up a development environment file with sample values."""
    env_file = Path(".env")

    if env_file.exists():
        print(f"⚠️  Environment file {env_file} already exists. Skipping creation.")
        return

    print("📝 Creating development environment file...")

    sample_env = """# Development Environment Variables for Duckalog Security Example
# This file contains SAMPLE VALUES for demonstration only
# DO NOT use these values in production!

# Environment Settings
ENVIRONMENT=development
CATALOG_NAME=dev_security_catalog
MEMORY_LIMIT=2GB
THREAD_COUNT=4
TIMEZONE=UTC

# AWS Configuration (SAMPLE VALUES - replace with your own or use local files)
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
DATA_BUCKET_PREFIX=company-data

# Database Configuration (PostgreSQL - SAMPLE VALUES)
DB_HOST=localhost
DB_PORT=5432
DB_NAME=dev_analytics
DB_USER=dev_user
DB_PASSWORD=dev_password
DB_SSL_MODE=prefer

# Reference Database
REFERENCE_DB_PATH=./reference_data.duckdb

# Iceberg Configuration (SAMPLE VALUES)
ICEBERG_URI=https://dev-catalog.example.com
ICEBERG_TOKEN=dev-token-placeholder
WAREHOUSE_BUCKET=company-dev-warehouse

# Application Settings
LOG_LEVEL=INFO
ENABLE_AUDIT_LOG=true
"""

    with open(env_file, 'w') as f:
        f.write(sample_env)

    print(f"✅ Environment file created: {env_file}")
    print("📖 Edit this file with your actual values before running the example")


def validate_setup():
    """Validate that the setup is complete and ready for testing."""
    print("🔍 Validating setup...")

    required_files = [
        ".env.example",
        ".gitignore",
        "catalog-dev.yaml",
        "catalog-prod.yaml",
        "reference_data.duckdb"
    ]

    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)

    if missing_files:
        print(f"❌ Missing required files: {missing_files}")
        return False

    # Check environment variables file
    env_file = Path(".env")
    if not env_file.exists():
        print("⚠️  .env file not found. Run setup to create it.")
        print("💡 You can create it manually by copying .env.example")

    print("✅ Setup validation complete!")
    return True


def main():
    """Main setup function."""
    print("🚀 Setting up Environment Variables Security Example...")
    print("=" * 60)

    try:
        # Create reference database
        create_reference_database()

        # Generate sample data
        generate_sample_parquet_data()

        # Set up environment file
        setup_environment_file()

        # Validate setup
        validate_setup()

        print("\n🎉 Setup completed successfully!")
        print("\n📋 Next steps:")
        print("1. Review and edit the .env file with your actual values")
        print("2. Source environment variables: source .env")
        print("3. Validate configurations: python validate-configs.py")
        print("4. Build development catalog: duckalog build catalog-dev.yaml")
        print("5. Test production config with real values when ready")

    except Exception as e:
        print(f"❌ Setup failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
