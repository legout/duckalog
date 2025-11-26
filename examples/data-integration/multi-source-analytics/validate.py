#!/usr/bin/env python3
"""
Validation script for multi-source analytics example.

Ensures the example works correctly and produces expected results across all data sources.
"""

import sys
from pathlib import Path

import duckdb
import polars as pl


def validate_example():
    """Validate the multi-source analytics example functionality."""
    print("🔍 Validating multi-source analytics example...")

    try:
        # Get the script's directory for relative path resolution
        script_dir = Path(__file__).parent
        project_root = script_dir.parent.parent.parent  # Go up to project root

        # Check data files exist
        data_dir = script_dir / "data"
        required_files = ["reference_data.duckdb"]

        for file in required_files:
            if not (data_dir / file).exists():
                raise FileNotFoundError(f"Required data file missing: {file}")

        # Check Parquet files exist
        events_dir = data_dir / "events"
        if not events_dir.exists() or len(list(events_dir.glob("*.parquet"))) == 0:
            raise FileNotFoundError("No Parquet event files found in data/events/")

        parquet_files = list(events_dir.glob("*.parquet"))
        print(f"✅ Found {len(parquet_files)} Parquet files")

        # Validate configuration
        from duckalog import load_config

        config = load_config(script_dir / "catalog.yaml")
        print("✅ Configuration validation passed")

        # Connect to the created catalog (in project root)
        db_path = project_root / "multi_source_analytics.duckdb"
        if not db_path.exists():
            raise FileNotFoundError(f"Catalog database not found: {db_path}")

        con = duckdb.connect(db_path)
        print("✅ Connected to analytics catalog")

        # Manually attach reference database (workaround for Duckalog attachment issue)
        ref_db_path = script_dir / "data" / "reference_data.duckdb"
        con.execute(f"ATTACH '{ref_db_path}' AS reference (READ_ONLY)")
        print("✅ Manually attached reference database")

        # Validate expected views exist
        expected_views = [
            "raw_events",
            "user_profiles",
            "product_data",
            "enriched_events",
            "event_metrics",
            "user_activity_summary",
            "product_performance",
            "daily_kpi_report",
        ]

        existing_views = con.execute(
            "SELECT table_name FROM information_schema.tables WHERE table_schema = 'main'"
        ).fetchall()
        existing_view_names = [row[0] for row in existing_views]

        missing_views = set(expected_views) - set(existing_view_names)
        if missing_views:
            raise ValueError(f"Missing views: {missing_views}")

        print(f"✅ All {len(expected_views)} expected views found")

        # Validate data quality
        print("\n📊 Validating data quality...")

        # Check raw events
        event_count = con.execute("SELECT COUNT(*) FROM raw_events").fetchone()[0]
        if event_count < 100:
            raise ValueError(f"Too few events: {event_count}")

        print(f"✅ Raw events: {event_count:,}")

        # Check user data
        user_count = con.execute("SELECT COUNT(*) FROM user_profiles").fetchone()[0]
        if user_count < 100:
            raise ValueError(f"Too few users: {user_count}")

        print(f"✅ Users: {user_count:,}")

        # Check product data
        product_count = con.execute("SELECT COUNT(*) FROM product_data").fetchone()[0]
        if product_count < 10:
            raise ValueError(f"Too few products: {product_count}")

        print(f"✅ Products: {product_count:,}")

        # Validate enriched data
        enriched_count = con.execute("SELECT COUNT(*) FROM enriched_events").fetchone()[
            0
        ]
        print(f"✅ Enriched events: {enriched_count:,}")

        # Check joins are working (should have user/product info for some events)
        enriched_with_user = con.execute("""
            SELECT COUNT(*) FROM enriched_events
            WHERE user_name IS NOT NULL
        """).fetchone()[0]

        if enriched_with_user == 0:
            raise ValueError("No user joins found in enriched events")

        print(f"✅ Events with user data: {enriched_with_user:,}")

        # Validate analytics views
        print("\n📈 Validating analytics views...")

        # Check daily KPI report
        kpi_count = con.execute("SELECT COUNT(*) FROM daily_kpi_report").fetchone()[0]
        if kpi_count < 7:  # Should have at least a week of data
            raise ValueError(f"Insufficient KPI data: {kpi_count} days")

        print(f"✅ Daily KPI data: {kpi_count} days")

        # Test some key queries work
        print("\n🧪 Testing key analytics queries...")

        # Test event metrics
        event_types = con.execute("""
            SELECT event_type, COUNT(*) as count
            FROM event_metrics
            GROUP BY event_type
            ORDER BY count DESC
        """).fetchall()

        if len(event_types) < 3:
            raise ValueError("Insufficient event type diversity")

        print(f"✅ Event types found: {len(event_types)}")

        # Test user activity summary
        active_users = con.execute("""
            SELECT COUNT(*) FROM user_activity_summary
            WHERE total_events > 0
        """).fetchone()[0]

        if active_users == 0:
            raise ValueError("No active users found")

        print(f"✅ Active users: {active_users:,}")

        # Validate data consistency
        print("\n🔎 Validating data consistency...")

        # Check date ranges make sense
        date_range = con.execute("""
            SELECT
                MIN(timestamp) as min_date,
                MAX(timestamp) as max_date,
                COUNT(DISTINCT DATE(timestamp)) as unique_days
            FROM raw_events
        """).fetchone()

        print(
            f"✅ Date range: {date_range[0]} to {date_range[1]} ({date_range[2]} days)"
        )

        # Check for data integrity
        null_check = con.execute("""
            SELECT COUNT(*) FROM enriched_events
            WHERE user_id IS NULL OR timestamp IS NULL
        """).fetchone()[0]

        if null_check > 0:
            raise ValueError(f"Found {null_check} records with NULL critical fields")

        print("✅ Data integrity checks passed")

        # Performance validation
        print("\n⚡ Performance validation...")

        # Test query performance
        import time

        start_time = time.time()

        result = con.execute("""
            SELECT
                event_date,
                SUM(total_events) as daily_total,
                AVG(daily_active_users) as avg_users
            FROM daily_kpi_report
            WHERE event_date >= CURRENT_DATE - INTERVAL 30 DAYS
            GROUP BY event_date
            ORDER BY event_date DESC
        """).fetchall()

        query_time = time.time() - start_time

        if query_time > 5.0:  # Should be fast for this dataset
            print(f"⚠️  Query took {query_time:.2f}s (consider optimization)")
        else:
            print(f"✅ Query performance: {query_time:.2f}s")

        con.close()

        print("\n🎉 All validations passed!")
        print("✅ Multi-source analytics example is working correctly")
        print("\n🚀 Ready for exploration:")
        print("   duckdb multi_source_analytics.duckdb")
        print("   SELECT * FROM daily_kpi_report ORDER BY event_date DESC LIMIT 10;")

        return True

    except Exception as e:
        print(f"\n❌ Validation failed: {e}")
        return False


if __name__ == "__main__":
    success = validate_example()
    sys.exit(0 if success else 1)
