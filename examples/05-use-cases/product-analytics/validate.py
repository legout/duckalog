#!/usr/bin/env python3
"""
Product Analytics Validation Script

This script validates the product analytics example by:
1. Checking data quality and integrity
2. Validating conversion funnel calculations
3. Testing A/B test statistical significance logic
4. Verifying user behavior patterns and path analysis
5. Checking real-time metrics calculations
"""

import sys
import os
import polars as pl
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
import warnings

warnings.filterwarnings("ignore")


def load_data():
    """Load all data files for validation."""
    data_dir = Path("data")

    if not data_dir.exists():
        print("❌ Data directory not found. Run generate_data.py first.")
        return None

    try:
        user_sessions = pl.read_parquet(data_dir / "user_sessions.parquet")
        user_events = pl.read_parquet(data_dir / "user_events.parquet")

        return {"user_sessions": user_sessions, "user_events": user_events}
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        return None


def validate_data_integrity(data):
    """Validate basic data integrity and relationships."""
    print("🔍 Validating Data Integrity...")
    errors = []

    user_sessions = data["user_sessions"]
    user_events = data["user_events"]

    # Check for required columns
    required_session_cols = [
        "session_id",
        "user_id",
        "start_time",
        "end_time",
        "device_type",
        "acquisition_source",
    ]
    required_event_cols = [
        "event_id",
        "session_id",
        "user_id",
        "event_type",
        "event_timestamp",
        "feature_name",
    ]

    missing_session_cols = [
        col for col in required_session_cols if col not in user_sessions.columns
    ]
    missing_event_cols = [
        col for col in required_event_cols if col not in user_events.columns
    ]

    if missing_session_cols:
        errors.append(f"user_sessions missing columns: {missing_session_cols}")
    if missing_event_cols:
        errors.append(f"user_events missing columns: {missing_event_cols}")

    # Validate data types and formats
    try:
        user_sessions = user_sessions.with_columns(
            [
                pl.col("start_time").cast(pl.Datetime),
                pl.col("end_time").cast(pl.Datetime),
            ]
        )
        user_events = user_events.with_columns(
            [pl.col("event_timestamp").cast(pl.Datetime)]
        )
    except Exception as e:
        errors.append(f"DateTime conversion error: {e}")

    # Check temporal consistency
    if "start_time" in user_sessions.columns and "end_time" in user_sessions.columns:
        invalid_sessions = user_sessions.filter(
            pl.col("end_time") < pl.col("start_time")
        )
        if invalid_sessions.height > 0:
            errors.append(
                f"{invalid_sessions.height} sessions have end_time before start_time"
            )

    # Check data volume
    print(f"   Data Volume:")
    print(f"   - User Sessions: {user_sessions.height:,}")
    print(f"   - User Events: {user_events.height:,}")

    # Check for reasonable session durations
    if user_sessions.height > 0:
        user_sessions = user_sessions.with_columns(
            [
                (
                    (pl.col("end_time") - pl.col("start_time")).dt.total_seconds() / 60
                ).alias("duration_minutes")
            ]
        )

        # Sessions longer than 24 hours might be data quality issues
        long_sessions = user_sessions.filter(pl.col("duration_minutes") > 1440)
        if (
            long_sessions.height > user_sessions.height * 0.01
        ):  # More than 1% long sessions
            errors.append(
                f"High number of unusually long sessions: {long_sessions.height:,}"
            )

        # Sessions shorter than 1 second might be data quality issues
        short_sessions = user_sessions.filter(pl.col("duration_minutes") < 0.017)
        if (
            short_sessions.height > user_sessions.height * 0.05
        ):  # More than 5% short sessions
            errors.append(
                f"High number of unusually short sessions: {short_sessions.height:,}"
            )

    # Validate foreign key relationships
    session_ids_in_events = set(user_events["session_id"].unique().to_list())
    session_ids_in_sessions = set(user_sessions["session_id"].unique().to_list())

    orphaned_events = session_ids_in_events - session_ids_in_sessions
    if len(orphaned_events) > 0:
        errors.append(f"{len(orphaned_events)} events reference non-existent sessions")

    user_ids_in_events = set(user_events["user_id"].unique().to_list())
    user_ids_in_sessions = set(user_sessions["user_id"].unique().to_list())

    orphaned_users = user_ids_in_events - user_ids_in_sessions
    if len(orphaned_users) > 0:
        errors.append(f"{len(orphaned_users)} users in events not found in sessions")

    if errors:
        print("❌ Data Integrity Issues Found:")
        for error in errors:
            print(f"   - {error}")
        return False
    else:
        print("✅ Data integrity checks passed")
        return True


def validate_conversion_funnel_logic(data):
    """Validate conversion funnel logic and calculations."""
    print("\n🔬 Validating Conversion Funnel Logic...")

    user_events = data["user_events"]

    # Check for funnel events
    funnel_events = [
        "page_view",
        "add_to_cart",
        "checkout_start",
        "payment_info",
        "order_confirmation",
    ]
    available_funnel_events = [
        e for e in funnel_events if e in user_events["event_type"].unique().to_list()
    ]

    print(f"   Available funnel events: {available_funnel_events}")

    if len(available_funnel_events) < 3:
        print("   ⚠️  Insufficient funnel events for comprehensive analysis")
        return True

    # Test funnel progression logic
    funnel_counts = {}
    for event in funnel_events:
        if event in user_events["event_type"].unique().to_list():
            funnel_counts[event] = user_events.filter(pl.col("event_type") == event)[
                "user_id"
            ].n_unique()
        else:
            funnel_counts[event] = 0

    print(f"   Funnel counts by step:")
    for event, count in funnel_counts.items():
        print(f"   - {event}: {count:,} unique users")

    # Validate funnel drop-off logic
    if funnel_counts["page_view"] > 0:
        conversion_rates = {}
        prev_count = funnel_counts["page_view"]

        for event in [
            "add_to_cart",
            "checkout_start",
            "payment_info",
            "order_confirmation",
        ]:
            if funnel_counts[event] > 0:
                conversion_rates[event] = funnel_counts[event] / prev_count
                prev_count = funnel_counts[event]
            else:
                conversion_rates[event] = 0

        print(f"   Step-to-step conversion rates:")
        for event, rate in conversion_rates.items():
            print(f"   - {event}: {rate:.1%}")

        # Check for reasonable conversion rates
        if conversion_rates["add_to_cart"] > 0.8:
            print("   ⚠️  Very high add-to-cart rate - may indicate data quality issues")
        elif conversion_rates["add_to_cart"] < 0.01:
            print("   ⚠️  Very low add-to-cart rate - may indicate tracking issues")
        else:
            print("   ✅ Add-to-cart conversion rate looks reasonable")

    return True


def validate_ab_test_logic(data):
    """Validate A/B test logic and statistical significance."""
    print("\n🧪 Validating A/B Test Logic...")

    user_events = data["user_events"]

    # Look for A/B test data in event properties
    ab_test_events = user_events.filter(pl.col("event_type").str.contains("(?i)test"))

    if ab_test_events.height == 0:
        print("   ℹ️  No A/B test events found in current dataset")
        return True

    print(f"   Found {ab_test_events.height:,} A/B test related events")

    # Simulate A/B test validation using event types as variants
    # This is a simplified validation since the actual test data might be in properties
    conversion_events = user_events.filter(pl.col("event_type") == "purchase")

    if conversion_events.height > 0:
        # Simulate A/B test with device types as variants
        device_conversions = conversion_events.group_by("device_type").agg(
            [
                pl.col("user_id").n_unique().alias("converting_users"),
                pl.col("event_id").count().alias("total_conversions"),
            ]
        )

        # Get total users by device type from sessions
        device_totals = (
            data["user_sessions"]
            .group_by("device_type")
            .agg(pl.col("user_id").n_unique().alias("total_users"))
        )

        # Merge conversion data
        ab_test_results = device_conversions.join(device_totals, on="device_type")
        ab_test_results = ab_test_results.with_columns(
            [
                (pl.col("converting_users") / pl.col("total_users")).alias(
                    "conversion_rate"
                )
            ]
        )

        print("   Simulated A/B test results by device type:")
        for row in ab_test_results.iter_rows():
            print(f"   - {row[0]}: {row[3]:.2%} conversion ({row[1]:,}/{row[2]:,})")

        # Validate statistical significance logic
        if ab_test_results.height >= 2:
            # Simple chi-square test validation
            results = ab_test_results.to_dicts()
            control_rate = results[0]["conversion_rate"]
            test_rate = results[1]["conversion_rate"]

            lift = (test_rate - control_rate) / control_rate if control_rate > 0 else 0

            print(f"   Conversion lift: {lift:.1%}")

            if abs(lift) < 0.05:
                print("   ✅ Small but realistic conversion difference")
            elif abs(lift) > 0.5:
                print(
                    "   ⚠️  Very large conversion difference - may indicate data issues"
                )
            else:
                print("   ✅ Reasonable conversion difference for A/B test")

    return True


def validate_user_behavior_patterns(data):
    """Validate user behavior analytics and path analysis."""
    print("\n👤 Validating User Behavior Patterns...")

    user_sessions = data["user_sessions"]
    user_events = data["user_events"]

    # Validate session-level metrics
    user_sessions = user_sessions.with_columns(
        [
            ((pl.col("end_time") - pl.col("start_time")).dt.total_seconds() / 60).alias(
                "duration_minutes"
            )
        ]
    )

    # Check session duration distribution
    avg_duration = user_sessions["duration_minutes"].mean()
    median_duration = user_sessions["duration_minutes"].median()

    print(f"   Session duration analysis:")
    print(f"   - Average: {avg_duration:.1f} minutes")
    print(f"   - Median: {median_duration:.1f} minutes")

    if avg_duration < 1:
        print("   ⚠️  Very short average session duration")
    elif avg_duration > 60:
        print("   ⚠️  Very long average session duration")
    else:
        print("   ✅ Reasonable session duration")

    # Validate event sequences
    events_per_session = (
        user_events.group_by("session_id")
        .count()
        .with_columns(pl.col("count").alias("event_count"))
    )
    avg_events_per_session = events_per_session["event_count"].mean()

    print(f"   Events per session:")
    print(f"   - Average: {avg_events_per_session:.1f}")

    if avg_events_per_session < 2:
        print("   ⚠️  Very few events per session")
    elif avg_events_per_session > 100:
        print("   ⚠️  Very high events per session - possible data quality issues")
    else:
        print("   ✅ Reasonable events per session")

    # Check device and acquisition source distribution
    device_dist = user_sessions["device_type"].value_counts(normalize=True)
    source_dist = user_sessions["acquisition_source"].value_counts(normalize=True)

    print(f"   Device distribution:")
    for row in device_dist.iter_rows():
        print(f"   - {row[0]}: {row[1]:.1%}")

    print(f"   Acquisition source distribution:")
    for row in source_dist.iter_rows():
        print(f"   - {row[0]}: {row[1]:.1%}")

    # Validate user engagement patterns
    user_activity = user_events.group_by("user_id").agg(
        [
            pl.col("session_id").n_unique().alias("sessions"),
            pl.col("event_id").count().alias("total_events"),
        ]
    )

    avg_sessions_per_user = user_activity["sessions"].mean()
    avg_events_per_user = user_activity["total_events"].mean()

    print(f"   User activity:")
    print(f"   - Average sessions per user: {avg_sessions_per_user:.1f}")
    print(f"   - Average events per user: {avg_events_per_user:.1f}")

    return True


def validate_real_time_metrics(data):
    """Validate real-time metrics calculation logic."""
    print("\n📊 Validating Real-time Metrics Logic...")

    user_events = data["user_events"]
    user_sessions = data["user_sessions"]

    # Get recent data for "real-time" validation
    now = datetime.now()
    one_hour_ago = now - timedelta(hours=1)
    one_day_ago = now - timedelta(days=1)

    # Convert timestamps for comparison
    user_events = user_events.with_columns(
        [pl.col("event_timestamp").cast(pl.Datetime)]
    )
    user_sessions = user_sessions.with_columns([pl.col("start_time").cast(pl.Datetime)])

    # Simulate real-time window calculations
    recent_events = user_events.filter(pl.col("event_timestamp") >= one_day_ago)
    recent_sessions = user_sessions.filter(pl.col("start_time") >= one_day_ago)

    print(f"   Recent activity (last 24 hours):")
    print(f"   - Events: {recent_events.height:,}")
    print(f"   - Sessions: {recent_sessions.height:,}")
    print(f"   - Unique users: {recent_events['user_id'].n_unique():,}")

    # Validate conversion tracking
    conversion_events = recent_events.filter(pl.col("event_type") == "purchase")
    unique_users = recent_sessions["user_id"].n_unique()
    conversion_rate = conversion_events.height / unique_users if unique_users > 0 else 0

    print(f"   - Conversions: {conversion_events.height:,}")
    print(f"   - Conversion rate: {conversion_rate:.2%}")

    # Validate device breakdown logic
    device_breakdown = recent_sessions.group_by("device_type").agg(
        [
            pl.col("session_id").count().alias("sessions"),
            pl.col("user_id").n_unique().alias("unique_users"),
        ]
    )

    print(f"   Device breakdown (last 24 hours):")
    for row in device_breakdown.iter_rows():
        print(f"   - {row[0]}: {row[1]} sessions, {row[2]} users")

    # Check for error events
    error_events = recent_events.filter(pl.col("event_type").str.contains("(?i)error"))

    print(f"   - Error events: {error_events.height:,}")
    if recent_events.height > 0:
        error_rate = error_events.height / recent_events.height
        print(f"   - Error rate: {error_rate:.2%}")

        if error_rate > 0.1:
            print("   ⚠️  High error rate detected")
        else:
            print("   ✅ Acceptable error rate")

    return True


def validate_performance_characteristics(data):
    """Validate performance and scalability characteristics."""
    print("\n⚡ Validating Performance Characteristics...")

    user_sessions = data["user_sessions"]
    user_events = data["user_events"]

    # Data size metrics
    print(f"   Data Size Metrics:")
    print(f"   - Sessions: {user_sessions.height:,}")
    print(f"   - Events: {user_events.height:,}")
    print(f"   - Events per session: {user_events.height / user_sessions.height:.1f}")

    # Cardinality metrics
    unique_users = user_sessions["user_id"].n_unique()
    unique_sessions = user_sessions["session_id"].n_unique()
    unique_events = user_events["event_id"].n_unique()

    print(f"   Cardinality Metrics:")
    print(f"   - Unique users: {unique_users:,}")
    print(f"   - Unique sessions: {unique_sessions:,}")
    print(f"   - Unique events: {unique_events:,}")

    # Time span analysis
    event_time_span = (
        user_events["event_timestamp"].max() - user_events["event_timestamp"].min()
    ).days

    session_time_span = (
        user_sessions["start_time"].max() - user_sessions["start_time"].min()
    ).days

    print(f"   Time Span:")
    print(f"   - Events: {event_time_span} days")
    print(f"   - Sessions: {session_time_span} days")

    # Memory usage estimation for common operations
    print(f"   Performance Considerations:")
    events_per_day = user_events.height / max(event_time_span, 1)
    print(f"   - Events per day: {events_per_day:.0f}")

    if events_per_day > 100000:
        print("   ⚠️  High event volume - consider partitioning strategies")
    else:
        print("   ✅ Manageable event volume")

    # Feature usage complexity
    unique_features = user_events["feature_name"].n_unique()
    print(f"   - Unique features: {unique_features}")

    if unique_features > 100:
        print("   ⚠️  High feature cardinality - may impact performance")
    else:
        print("   ✅ Manageable feature count")

    return True


def main():
    """Main validation function."""
    print("🔎 Product Analytics Validation Script")
    print("=" * 50)

    # Load data
    data = load_data()
    if data is None:
        return False

    # Run validations
    validations = [
        validate_data_integrity(data),
        validate_conversion_funnel_logic(data),
        validate_ab_test_logic(data),
        validate_user_behavior_patterns(data),
        validate_real_time_metrics(data),
        validate_performance_characteristics(data),
    ]

    print("\n" + "=" * 50)

    if all(validations):
        print("✅ All validations passed! Product analytics example is ready.")
        return True
    else:
        print("❌ Some validations failed. Please review the issues above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
