#!/usr/bin/env python3
"""
Product Analytics Data Generation Script

This script generates realistic product analytics data for demonstrating
conversion funnel analysis, A/B testing, user behavior analytics,
path analysis, and real-time metrics.
"""

import argparse
import json
import os
import random
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np

import polars as pl
import pyarrow as pa
import pyarrow.dataset as ds


def write_partitioned_dataset(
    df: pl.DataFrame, base_dir: Path, partition_cols: list[str] | None = None
) -> None:
    """Write a DataFrame as a partitioned Parquet dataset using pyarrow."""
    base_dir.mkdir(parents=True, exist_ok=True)

    # Convert to Arrow table
    table = df.to_arrow()

    if partition_cols:
        # Create schema for partitioning from the table schema
        partition_schema = pa.schema(
            [table.schema.field(col) for col in partition_cols]
        )
        partitioning = ds.partitioning(partition_schema, flavor="hive")
    else:
        partitioning = None

    ds.write_dataset(
        table,
        base_dir,
        format="parquet",
        partitioning=partitioning,
        existing_data_behavior="delete_matching",
    )


def write_outputs(
    df: pl.DataFrame,
    name: str,
    date_col: str | None,
    data_dir: Path,
    partitioned: bool,
    partitioned_only: bool,
) -> None:
    file_path = data_dir / f"{name}.parquet"
    partition_dir = data_dir / f"{name}_partitioned"

    if not partitioned_only:
        df.write_parquet(file_path, compression="zstd")

    if partitioned and date_col:
        df_with_parts = df.with_columns(
            pl.col(date_col).dt.year().alias("year"),
            pl.col(date_col).dt.month().alias("month"),
        )
        write_partitioned_dataset(df_with_parts, partition_dir, ["year", "month"])
    elif partitioned:
        write_partitioned_dataset(df, partition_dir, [])


def generate_events_batch(sessions_data: np.ndarray, batch_size: int = 1000):
    """Generate events in batches for better memory management and performance."""
    # Pre-compute feature data for performance
    feature_names = np.array(
        [
            "product_search",
            "product_view",
            "add_to_cart",
            "cart_view",
            "wishlist_add",
            "product_compare",
            "filter_apply",
            "sort_apply",
            "review_read",
            "review_write",
            "recommendation_click",
            "category_browse",
        ]
    )
    feature_probs = np.array(
        [0.8, 0.9, 0.3, 0.4, 0.15, 0.2, 0.5, 0.3, 0.4, 0.05, 0.25, 0.6]
    )
    feature_probs = feature_probs / feature_probs.sum()

    feature_data = {
        "product_search": {
            "category": "search",
            "conversion_impact": 0.3,
            "event_type": "search",
        },
        "product_view": {
            "category": "catalog",
            "conversion_impact": 0.5,
            "event_type": "view",
        },
        "add_to_cart": {
            "category": "conversion",
            "conversion_impact": 0.8,
            "event_type": "add",
        },
        "cart_view": {
            "category": "conversion",
            "conversion_impact": 0.6,
            "event_type": "click",
        },
        "wishlist_add": {
            "category": "engagement",
            "conversion_impact": 0.2,
            "event_type": "click",
        },
        "product_compare": {
            "category": "catalog",
            "conversion_impact": 0.4,
            "event_type": "click",
        },
        "filter_apply": {
            "category": "search",
            "conversion_impact": 0.2,
            "event_type": "filter",
        },
        "sort_apply": {
            "category": "search",
            "conversion_impact": 0.1,
            "event_type": "filter",
        },
        "review_read": {
            "category": "catalog",
            "conversion_impact": 0.3,
            "event_type": "view",
        },
        "review_write": {
            "category": "engagement",
            "conversion_impact": 0.1,
            "event_type": "click",
        },
        "recommendation_click": {
            "category": "catalog",
            "conversion_impact": 0.4,
            "event_type": "click",
        },
        "category_browse": {
            "category": "catalog",
            "conversion_impact": 0.2,
            "event_type": "click",
        },
    }

    # Pre-compute choice arrays
    pages = np.array(["home", "product", "category", "search", "cart"])
    categories = np.array(["electronics", "clothing", "books", "home", "sports"])
    search_queries = np.array(["laptop", "shoes", "novel", "furniture", "fitness"])
    filter_types = np.array(["price_range", "brand", "rating", "category"])

    event_ids = []
    session_ids_list = []
    user_ids_list = []
    event_types = []
    feature_names_list = []
    event_timestamps = []
    properties_list = []

    event_counter = 0

    for i in range(min(len(sessions_data), batch_size)):
        session_id = str(sessions_data[i, 0])
        user_id = str(sessions_data[i, 1])
        start_time = sessions_data[i, 2]
        end_time = sessions_data[i, 3]
        device_type = str(sessions_data[i, 4])
        browser = str(sessions_data[i, 5])

        # Calculate number of events efficiently
        session_duration = (end_time - start_time).total_seconds() / 60
        device_multiplier = (
            0.5 if device_type == "mobile" else 0.7 if device_type == "tablet" else 1.0
        )
        expected_events = int(session_duration * device_multiplier)
        num_events = max(
            1, min(expected_events, max(1, np.random.poisson(max(1, expected_events))))
        )

        # Batch generate random choices for this session
        session_features = np.random.choice(
            feature_names, size=num_events, p=feature_probs
        )
        session_pages = np.random.choice(pages, size=num_events)

        # Generate timestamps efficiently
        if num_events > 1:
            time_positions = np.sort(np.random.uniform(0, 1, size=num_events))
            session_duration_sec = session_duration * 60
            event_times = [
                start_time + timedelta(seconds=pos * session_duration_sec)
                for pos in time_positions
            ]
        else:
            event_times = [end_time]

        user_conversion_probability = 0.05

        for event_num in range(num_events):
            feature_name = session_features[event_num]
            feature_info = feature_data[feature_name]
            event_type = feature_info["event_type"]
            event_time = event_times[event_num]

            # Generate properties efficiently
            properties = {
                "page": session_pages[event_num],
                "device": device_type,
                "browser": browser,
                "category": feature_info["category"],
                "conversion_impact": feature_info["conversion_impact"],
            }

            # Add conditional properties with vectorized operations where possible
            if feature_name in ["product_view", "add_to_cart", "review_write"]:
                properties["product_id"] = f"product_{np.random.randint(1, 1001):04d}"
                properties["product_category"] = np.random.choice(categories)

            if feature_name in ["product_search", "category_browse"]:
                properties["search_query"] = np.random.choice(search_queries)
                properties["results_count"] = np.random.randint(5, 100)

            if feature_name == "filter_apply":
                properties["filter_type"] = np.random.choice(filter_types)
                properties["filter_value"] = "some_value"

            if feature_name == "add_to_cart":
                user_conversion_probability += 0.15

            # Check for purchase
            is_purchase = False
            if (
                event_num == num_events - 1
                and np.random.random() < user_conversion_probability
            ):
                event_type = "purchase"
                properties["order_value"] = float(np.random.uniform(25, 1000))
                properties["items_count"] = int(np.random.randint(1, 10))
                feature_name = "checkout"
                is_purchase = True

            # Update conversion probability
            if not is_purchase:
                user_conversion_probability += properties["conversion_impact"] * 0.01

            # Append data efficiently
            event_ids.append(f"event_{event_counter:08d}")
            session_ids_list.append(session_id)
            user_ids_list.append(user_id)
            event_types.append(event_type)
            feature_names_list.append(feature_name)
            event_timestamps.append(event_time)
            properties_list.append(json.dumps(properties))
            event_counter += 1

    return pl.DataFrame(
        {
            "event_id": event_ids,
            "session_id": session_ids_list,
            "user_id": user_ids_list,
            "event_type": event_types,
            "feature_name": feature_names_list,
            "event_timestamp": event_timestamps,
            "properties": properties_list,
        }
    )


def generate_user_sessions(
    start_date="2024-01-01", end_date="2024-12-31", num_users=50000
):
    """Generate user session data with realistic engagement patterns."""

    np.random.seed(789)

    start_dt = datetime.strptime(start_date, "%Y-%m-%d")
    end_dt = datetime.strptime(end_date, "%Y-%m-%d")

    sessions = []

    # Device and acquisition distributions
    devices = ["desktop", "mobile", "tablet"]
    device_probs = [0.55, 0.35, 0.10]

    acquisition_sources = [
        "organic_search",
        "paid_search",
        "social_media",
        "direct",
        "email",
        "referral",
    ]
    source_probs = [0.30, 0.25, 0.15, 0.15, 0.10, 0.05]

    # Generate sessions per day (following weekly patterns)
    current_date = start_dt
    session_counter = 0

    while current_date <= end_dt:
        # Base sessions with weekly pattern (higher on weekdays)
        base_sessions = 800
        if current_date.weekday() >= 5:  # Weekend
            daily_sessions = int(base_sessions * 0.7)
        else:
            daily_sessions = int(base_sessions * 1.2)

        # Add some randomness
        daily_sessions = int(daily_sessions * np.random.uniform(0.8, 1.2))

        for i in range(daily_sessions):
            session_id = f"session_{session_counter:08d}"
            user_id = f"user_{np.random.randint(1, num_users + 1):06d}"

            # Device and source selection
            device_type = np.random.choice(devices, p=device_probs)
            acquisition_source = np.random.choice(acquisition_sources, p=source_probs)

            # Session start time (more sessions during business hours)
            if device_type == "desktop":
                # Business hours peak for desktop
                hour = np.random.choice(
                    list(range(9, 18)),
                    p=[0.10, 0.12, 0.15, 0.18, 0.20, 0.15, 0.06, 0.03, 0.01],
                )
            else:
                # More varied hours for mobile
                hour = np.random.choice(list(range(24)))

            minute = np.random.randint(0, 60)
            second = np.random.randint(0, 60)

            start_time = current_date.replace(hour=hour, minute=minute, second=second)

            # Session duration based on device and user behavior
            if device_type == "mobile":
                duration_minutes = np.random.exponential(5)  # Shorter mobile sessions
            elif device_type == "tablet":
                duration_minutes = np.random.exponential(8)
            else:
                duration_minutes = np.random.exponential(12)  # Longer desktop sessions

            duration_minutes = max(1, min(duration_minutes, 120))  # 1 min to 2 hours
            end_time = start_time + timedelta(minutes=duration_minutes)

            # Geographic region (simplified)
            regions = ["North America", "Europe", "Asia Pacific", "Latin America"]
            region_weights = [0.45, 0.25, 0.20, 0.10]
            geographic_location = np.random.choice(regions, p=region_weights)

            sessions.append(
                {
                    "session_id": session_id,
                    "user_id": user_id,
                    "start_time": start_time,
                    "end_time": end_time,
                    "device_type": device_type,
                    "acquisition_source": acquisition_source,
                    "geographic_location": geographic_location,
                }
            )

            session_counter += 1

        current_date += timedelta(days=1)

    return pl.DataFrame(sessions)


def generate_user_events(sessions_df: pl.DataFrame):
    """Generate detailed user interaction events - optimized version."""

    np.random.seed(456)
    print("Generating user events...")

    # Pre-compute feature data for performance
    feature_names = np.array(
        [
            "product_search",
            "product_view",
            "add_to_cart",
            "cart_view",
            "wishlist_add",
            "product_compare",
            "filter_apply",
            "sort_apply",
            "review_read",
            "review_write",
            "recommendation_click",
            "category_browse",
        ]
    )
    feature_probs = np.array(
        [0.8, 0.9, 0.3, 0.4, 0.15, 0.2, 0.5, 0.3, 0.4, 0.05, 0.25, 0.6]
    )
    feature_probs = feature_probs / feature_probs.sum()  # Normalize

    features = {
        "product_search": {
            "category": "search",
            "prob": 0.8,
            "conversion_impact": 0.3,
            "event_type": "search",
        },
        "product_view": {
            "category": "catalog",
            "prob": 0.9,
            "conversion_impact": 0.5,
            "event_type": "view",
        },
        "add_to_cart": {
            "category": "conversion",
            "prob": 0.3,
            "conversion_impact": 0.8,
            "event_type": "add",
        },
        "cart_view": {
            "category": "conversion",
            "prob": 0.4,
            "conversion_impact": 0.6,
            "event_type": "click",
        },
        "wishlist_add": {
            "category": "engagement",
            "prob": 0.15,
            "conversion_impact": 0.2,
            "event_type": "click",
        },
        "product_compare": {
            "category": "catalog",
            "prob": 0.2,
            "conversion_impact": 0.4,
            "event_type": "click",
        },
        "filter_apply": {
            "category": "search",
            "prob": 0.5,
            "conversion_impact": 0.2,
            "event_type": "filter",
        },
        "sort_apply": {
            "category": "search",
            "prob": 0.3,
            "conversion_impact": 0.1,
            "event_type": "filter",
        },
        "review_read": {
            "category": "catalog",
            "prob": 0.4,
            "conversion_impact": 0.3,
            "event_type": "view",
        },
        "review_write": {
            "category": "engagement",
            "prob": 0.05,
            "conversion_impact": 0.1,
            "event_type": "click",
        },
        "recommendation_click": {
            "category": "catalog",
            "prob": 0.25,
            "conversion_impact": 0.4,
            "event_type": "click",
        },
        "category_browse": {
            "category": "catalog",
            "prob": 0.6,
            "conversion_impact": 0.2,
            "event_type": "click",
        },
    }

    # Pre-compute choice arrays for better performance
    pages = np.array(["home", "product", "category", "search", "cart"])
    categories = np.array(["electronics", "clothing", "books", "home", "sports"])
    search_queries = np.array(["laptop", "shoes", "novel", "furniture", "fitness"])
    filter_types = np.array(["price_range", "brand", "rating", "category"])

    events = []
    event_counter = 0

    # Convert to numpy for faster iteration
    sessions_data = sessions_df.to_numpy()
    total_sessions = len(sessions_data)

    # Feature definitions with usage patterns
    features = {
        "product_search": {"category": "search", "prob": 0.8, "conversion_impact": 0.3},
        "product_view": {"category": "catalog", "prob": 0.9, "conversion_impact": 0.5},
        "add_to_cart": {
            "category": "conversion",
            "prob": 0.3,
            "conversion_impact": 0.8,
        },
        "cart_view": {"category": "conversion", "prob": 0.4, "conversion_impact": 0.6},
        "wishlist_add": {
            "category": "engagement",
            "prob": 0.15,
            "conversion_impact": 0.2,
        },
        "product_compare": {
            "category": "catalog",
            "prob": 0.2,
            "conversion_impact": 0.4,
        },
        "filter_apply": {"category": "search", "prob": 0.5, "conversion_impact": 0.2},
        "sort_apply": {"category": "search", "prob": 0.3, "conversion_impact": 0.1},
        "review_read": {"category": "catalog", "prob": 0.4, "conversion_impact": 0.3},
        "review_write": {
            "category": "engagement",
            "prob": 0.05,
            "conversion_impact": 0.1,
        },
        "recommendation_click": {
            "category": "catalog",
            "prob": 0.25,
            "conversion_impact": 0.4,
        },
        "category_browse": {
            "category": "catalog",
            "prob": 0.6,
            "conversion_impact": 0.2,
        },
    }

    # Event types
    event_types = ["click", "view", "search", "filter", "purchase", "add", "remove"]

    # Pre-compute feature choices for performance optimization
    available_features = list(features.keys())
    feature_probs = np.array([features[f]["prob"] for f in available_features])
    feature_probs = feature_probs / feature_probs.sum()  # Normalize once

    # Pre-compute random choice arrays for better performance
    pages = np.array(["home", "product", "category", "search", "cart"])
    categories = np.array(["electronics", "clothing", "books", "home", "sports"])
    search_queries = np.array(["laptop", "shoes", "novel", "furniture", "fitness"])
    filter_types = np.array(["price_range", "brand", "rating", "category"])

    # Add progress reporting
    total_sessions = len(sessions_df)
    processed_sessions = 0

    for session in sessions_df.iter_rows(named=True):
        session_id = session["session_id"]
        user_id = session["user_id"]
        start_time = session["start_time"]
        end_time = session["end_time"]
        device_type = session["device_type"]

        # Progress reporting
        processed_sessions += 1
        if processed_sessions % 10000 == 0 or processed_sessions == total_sessions:
            print(f"  Processed {processed_sessions:,}/{total_sessions:,} sessions")

        # Determine number of events based on session duration and device
        session_duration_minutes = (end_time - start_time).total_seconds() / 60

        if device_type == "mobile":
            base_events_per_minute = 0.5
        elif device_type == "tablet":
            base_events_per_minute = 0.7
        else:
            base_events_per_minute = 1.0

        expected_events = int(session_duration_minutes * base_events_per_minute)
        num_events = max(
            1, min(expected_events, int(np.random.poisson(expected_events)))
        )

        # Generate events for this session
        current_time = start_time
        user_conversion_probability = 0.05  # Base conversion probability

        for event_num in range(num_events):
            # Select feature using pre-computed arrays (much faster!)
            feature_name = np.random.choice(available_features, p=feature_probs)

            # Determine event type
            if feature_name == "add_to_cart":
                event_type = "add"
            elif feature_name == "product_search":
                event_type = "search"
            elif feature_name in ["product_view", "review_read"]:
                event_type = "view"
            elif feature_name in ["filter_apply", "sort_apply"]:
                event_type = "filter"
            else:
                event_type = "click"

            # Random event time within session
            if event_num < num_events - 1:
                time_progress = (event_num + 1) / num_events
                max_event_time = start_time + timedelta(
                    seconds=time_progress * (end_time - start_time).total_seconds()
                )
                event_time = current_time + timedelta(seconds=np.random.exponential(60))
                event_time = min(event_time, max_event_time)
            else:
                event_time = end_time

            if event_time > end_time:
                break

            current_time = event_time

            # Generate event properties
            properties = {
                "device_type": device_type,
                "session_position": event_num / num_events,
                "feature_category": features[feature_name]["category"],
            }

            # Add specific properties based on feature
            if feature_name == "product_search":
                properties["search_query"] = f"term_{np.random.randint(1, 1000)}"
                properties["results_count"] = np.random.randint(5, 100)
                properties["conversion_impact"] = features[feature_name][
                    "conversion_impact"
                ]
                user_conversion_probability += 0.02

            elif feature_name == "product_view":
                properties["product_id"] = f"prod_{np.random.randint(1, 10000):05d}"
                properties["price_range"] = np.random.choice(
                    ["low", "medium", "high"], p=[0.3, 0.5, 0.2]
                )
                properties["conversion_impact"] = features[feature_name][
                    "conversion_impact"
                ]
                user_conversion_probability += 0.05

            elif feature_name == "add_to_cart":
                properties["product_id"] = f"prod_{np.random.randint(1, 10000):05d}"
                properties["quantity"] = np.random.randint(1, 5)
                properties["price"] = np.random.uniform(10, 500)
                properties["conversion_impact"] = features[feature_name][
                    "conversion_impact"
                ]
                user_conversion_probability += 0.15

            # Check for conversion event
            is_purchase = False
            if event_num == num_events - 1:  # Last event in session
                if np.random.random() < user_conversion_probability:
                    event_type = "purchase"
                    properties["order_value"] = np.random.uniform(25, 1000)
                    properties["items_count"] = np.random.randint(1, 10)
                    is_purchase = True

            events.append(
                {
                    "event_id": f"event_{event_counter:08d}",
                    "session_id": session_id,
                    "user_id": user_id,
                    "event_type": event_type,
                    "feature_name": feature_name if not is_purchase else "checkout",
                    "event_timestamp": event_time,
                    "properties": json.dumps(properties),
                }
            )

            event_counter += 1

            # Update conversion probability based on user behavior
            if "conversion_impact" in properties:
                user_conversion_probability += properties["conversion_impact"] * 0.01

    return pl.DataFrame(events)


def generate_funnel_events(user_events_df: pl.DataFrame):
    """Generate conversion funnel tracking events - optimized version."""

    np.random.seed(123)
    print("Generating conversion funnel events...")

    # Define funnel stages
    funnel_stages = [
        "page_view",
        "add_to_cart",
        "checkout_start",
        "payment_info",
        "order_confirmation",
    ]

    # Phase 1: Batch processing optimization - Get all purchase data in ONE operation
    print("  Processing purchase sessions...")
    purchase_events = user_events_df.filter(pl.col("event_type") == "purchase")

    # Extract all purchase session data at once
    purchase_session_data = purchase_events.select(
        ["session_id", "user_id", "event_timestamp"]
    ).unique(subset=["session_id"])

    num_purchase_sessions = len(purchase_session_data)
    print(f"  Found {num_purchase_sessions:,} purchase sessions")

    # Pre-allocate lists for better memory management
    estimated_purchase_events = num_purchase_sessions * len(funnel_stages)
    funnel_event_ids = []
    user_ids = []
    session_ids = []
    funnel_stages_list = []
    event_timestamps = []
    properties_list = []

    # Vectorized timestamp generation for purchase sessions
    base_offsets = np.random.randint(5, 30, size=num_purchase_sessions)
    stage_offsets = np.random.randint(1, 10, size=(num_purchase_sessions, 4))

    funnel_counter = 0
    processed_purchase = 0

    # Process purchase sessions in batches
    for idx in range(num_purchase_sessions):
        session_row = purchase_session_data.row(idx)
        session_id = session_row[0]
        user_id = session_row[1]
        purchase_time = session_row[2]

        # Generate timestamps for all funnel stages at once
        base_time = purchase_time - timedelta(minutes=int(base_offsets[idx]))

        # Build all funnel stages for this session
        for stage_idx, stage in enumerate(reversed(funnel_stages)):
            if stage == "order_confirmation":
                event_time = purchase_time
            else:
                offset = stage_offsets[idx, 4 - len(funnel_stages) + stage_idx]
                event_time = base_time - timedelta(minutes=int(offset))
                base_time = event_time

            funnel_event_ids.append(f"funnel_{funnel_counter:08d}")
            user_ids.append(user_id)
            session_ids.append(session_id)
            funnel_stages_list.append(stage)
            event_timestamps.append(event_time)

            # Generate properties efficiently
            properties = {
                "stage_order": funnel_stages.index(stage),
                "time_to_next_stage": int(
                    stage_offsets[idx, 4 - len(funnel_stages) + stage_idx]
                )
                if stage_idx > 0
                else 0,
            }
            properties_list.append(json.dumps(properties))

            funnel_counter += 1

        processed_purchase += 1
        if (
            processed_purchase % 10000 == 0
            or processed_purchase == num_purchase_sessions
        ):
            print(
                f"    Processed {processed_purchase:,}/{num_purchase_sessions:,} purchase sessions"
            )

    # Phase 2: Efficient non-purchase session processing
    print("  Processing non-purchase sessions...")

    # Get all non-purchase session data at once
    all_sessions = user_events_df.select(["session_id", "user_id"]).unique(
        subset=["session_id"]
    )
    non_purchase_sessions = all_sessions.filter(
        ~pl.col("session_id").is_in(purchase_session_data["session_id"])
    )

    if len(non_purchase_sessions) > 0:
        sample_size = min(len(non_purchase_sessions), max(1, num_purchase_sessions * 3))

        # Sample efficiently
        if len(non_purchase_sessions) <= sample_size:
            sample_non_purchase = non_purchase_sessions.to_numpy()
        else:
            sample_indices = np.random.choice(
                len(non_purchase_sessions), size=sample_size, replace=False
            )
            sample_non_purchase = non_purchase_sessions[sample_indices].to_numpy()

        print(f"    Sampling {len(sample_non_purchase):,} non-purchase sessions")

        processed_non_purchase = 0

        # Vectorized stage generation for non-purchase sessions
        max_stages = np.random.choice(
            [0, 1, 2], size=len(sample_non_purchase), p=[0.6, 0.3, 0.1]
        )

        for session_idx, (session_id, user_id) in enumerate(sample_non_purchase):
            max_stage = max_stages[session_idx]
            stages_for_session = funnel_stages[: max_stage + 1]

            # Get session start time efficiently
            session_start = (
                user_events_df.filter(pl.col("session_id") == session_id)
                .select(pl.col("event_timestamp").min())
                .item()
            )

            for stage_idx, stage in enumerate(stages_for_session):
                event_time = session_start + timedelta(
                    minutes=np.random.randint(stage_idx * 5, (stage_idx + 1) * 15)
                )

                funnel_event_ids.append(f"funnel_{funnel_counter:08d}")
                user_ids.append(user_id)
                session_ids.append(session_id)
                funnel_stages_list.append(stage)
                event_timestamps.append(event_time)
                properties_list.append(
                    json.dumps({"stage_order": stage_idx, "converted": False})
                )

                funnel_counter += 1

            processed_non_purchase += 1
            if processed_non_purchase % 5000 == 0 or processed_non_purchase == len(
                sample_non_purchase
            ):
                print(
                    f"    Processed {processed_non_purchase:,}/{len(sample_non_purchase):,} non-purchase sessions"
                )

    # Create DataFrame efficiently from pre-allocated lists
    print(f"  Creating DataFrame with {funnel_counter:,} funnel events...")
    return pl.DataFrame(
        {
            "funnel_event_id": funnel_event_ids,
            "user_id": user_ids,
            "session_id": session_ids,
            "funnel_stage": funnel_stages_list,
            "event_timestamp": event_timestamps,
            "properties": properties_list,
        }
    )


def generate_ab_tests():
    """Generate A/B test configurations and results."""

    np.random.seed(987)

    tests = [
        {
            "test_name": "homepage_hero_image",
            "description": "Testing different hero images on homepage",
            "variants": ["control", "variant_a", "variant_b"],
            "traffic_split": [34, 33, 33],
            "hypothesized_improvement": 0.15,
        },
        {
            "test_name": "add_to_cart_button_color",
            "description": "Testing different button colors for add to cart",
            "variants": ["control", "variant_a"],
            "traffic_split": [50, 50],
            "hypothesized_improvement": 0.08,
        },
        {
            "test_name": "checkout_process简化",
            "description": "Testing simplified checkout process",
            "variants": ["control", "variant_a"],
            "traffic_split": [50, 50],
            "hypothesized_improvement": 0.12,
        },
        {
            "test_name": "product_recommendations_algorithm",
            "description": "Testing new recommendation algorithm",
            "variants": ["control", "variant_a", "variant_b", "variant_c"],
            "traffic_split": [25, 25, 25, 25],
            "hypothesized_improvement": 0.10,
        },
    ]

    ab_test_results: list[dict] = []

    for test in tests:
        test_id = f"test_{len(ab_test_results) + 1:03d}"
        start_date = (
            datetime.now() - timedelta(days=np.random.randint(60, 180))
        ).date()
        end_date = start_date + timedelta(days=np.random.randint(14, 60))

        for variant in test["variants"]:
            base_users = 5000
            variant_users = int(
                base_users
                * (test["traffic_split"][test["variants"].index(variant)] / 100)
            )
            variant_users = int(variant_users * np.random.uniform(0.9, 1.1))

            base_conversion_rate = 0.05

            if variant == "control":
                conversion_rate = base_conversion_rate
            else:
                if np.random.random() < 0.4:
                    improvement = test["hypothesized_improvement"] * np.random.uniform(
                        0.5, 1.5
                    )
                    conversion_rate = base_conversion_rate * (1 + improvement)
                else:
                    decline = test["hypothesized_improvement"] * np.random.uniform(
                        -0.5, 0.2
                    )
                    conversion_rate = base_conversion_rate * (1 + decline)

            conversion_rate = max(0.01, min(0.15, conversion_rate))

            conversions = int(variant_users * conversion_rate)
            avg_conversion_value = np.random.uniform(50, 150)

            ab_test_results.append(
                {
                    "test_id": test_id,
                    "test_name": test["test_name"],
                    "variant": variant,
                    "test_status": "completed",
                    "start_date": start_date,
                    "end_date": end_date,
                    "participants": variant_users,
                    "conversions": conversions,
                    "conversion_rate": conversion_rate,
                    "avg_conversion_value": avg_conversion_value,
                    "converted": 1,
                }
            )

    return pl.DataFrame(ab_test_results)


def generate_feature_usage(user_events_df: pl.DataFrame):
    """Generate feature adoption and usage tracking data."""

    np.random.seed(654)

    feature_usage = []

    feature_events = user_events_df.filter(pl.col("feature_name").is_not_null())

    current_date = datetime.now().date()
    date_range = [current_date - timedelta(days=89 - i) for i in range(90)]

    feature_categories = {
        "search": ["product_search", "filter_apply", "sort_apply"],
        "catalog": [
            "product_view",
            "review_read",
            "product_compare",
            "category_browse",
        ],
        "conversion": ["add_to_cart", "cart_view"],
        "engagement": ["wishlist_add", "review_write", "recommendation_click"],
    }

    for feature_name in feature_events.get_column("feature_name").unique().to_list():
        category = "other"
        for cat, features in feature_categories.items():
            if feature_name in features:
                category = cat
                break

        for date in date_range:
            days_since_start = (date - date_range[0]).days

            max_users = 5000
            adoption_rate = 1 / (1 + np.exp(-0.1 * (days_since_start - 45)))
            daily_users = int(max_users * adoption_rate * np.random.uniform(0.8, 1.2))

            usage_events = daily_users * np.random.randint(1, 5)
            usage_duration = usage_events * np.random.uniform(10, 120)

            feature_usage.append(
                {
                    "feature_name": feature_name,
                    "feature_category": category,
                    "event_date": date,
                    "user_id": f"user_{np.random.randint(1, 50000):06d}",
                    "usage_duration_seconds": usage_duration,
                    "usage_events": usage_events,
                }
            )

    return pl.DataFrame(feature_usage)


def main():
    """Generate all product analytics data."""

    parser = argparse.ArgumentParser(
        description="Generate product analytics example data"
    )
    parser.add_argument(
        "--partitioned",
        action="store_true",
        help="Also write partitioned parquet outputs (year/month where applicable)",
    )
    parser.add_argument(
        "--partitioned-only",
        action="store_true",
        help="Write only partitioned parquet outputs (implies --partitioned)",
    )
    args = parser.parse_args()
    if args.partitioned_only:
        args.partitioned = True

    print("Generating product analytics data...")

    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)

    print("Generating user sessions...")
    sessions_df = generate_user_sessions()
    write_outputs(
        sessions_df,
        "user_sessions",
        "start_time",
        data_dir,
        args.partitioned,
        args.partitioned_only,
    )
    print(f"Generated {sessions_df.height:,} user sessions")

    print("Generating user events...")
    events_df = generate_user_events(sessions_df)
    write_outputs(
        events_df,
        "user_events",
        "event_timestamp",
        data_dir,
        args.partitioned,
        args.partitioned_only,
    )
    print(f"Generated {events_df.height:,} user events")

    print("Generating conversion funnel events...")
    funnel_df = generate_funnel_events(events_df)
    write_outputs(
        funnel_df,
        "funnel_events",
        "event_timestamp",
        data_dir,
        args.partitioned,
        args.partitioned_only,
    )
    print(f"Generated {funnel_df.height:,} funnel events")

    print("Generating A/B test data...")
    ab_tests_df = generate_ab_tests()
    write_outputs(
        ab_tests_df,
        "ab_tests",
        "start_date",
        data_dir,
        args.partitioned,
        args.partitioned_only,
    )
    print(f"Generated {ab_tests_df.height:,} A/B test results")

    print("Generating feature usage data...")
    feature_usage_df = generate_feature_usage(events_df)
    write_outputs(
        feature_usage_df,
        "feature_usage",
        "event_date",
        data_dir,
        args.partitioned,
        args.partitioned_only,
    )
    print(f"Generated {feature_usage_df.height:,} feature usage records")

    print("\nData Summary:")
    print(f"User Sessions: {sessions_df.height:,}")
    print(f"  - Unique users: {sessions_df['user_id'].n_unique():,}")
    print(
        f"  - Date range: {sessions_df['start_time'].min()} to {sessions_df['end_time'].max()}"
    )
    print(
        f"  - Device breakdown: {sessions_df.group_by('device_type').count().to_dict(as_series=False)}"
    )

    print(f"\nUser Events: {events_df.height:,}")
    print(f"  - Unique features: {events_df['feature_name'].n_unique():,}")
    print(
        f"  - Event types: {events_df.group_by('event_type').count().to_dict(as_series=False)}"
    )
    print(
        f"  - Purchase events: {events_df.filter(pl.col('event_type') == 'purchase').height:,}"
    )

    print(f"\nFunnel Events: {funnel_df.height:,}")
    print(
        f"  - Converting users: {funnel_df.filter(pl.col('funnel_stage') == 'order_confirmation')['user_id'].n_unique():,}"
    )
    print(
        f"  - Funnel stage distribution: {funnel_df.group_by('funnel_stage').count().to_dict(as_series=False)}"
    )

    print(f"\nA/B Tests: {ab_tests_df.height:,}")
    print(f"  - Number of tests: {ab_tests_df['test_name'].n_unique():,}")
    print(f"  - Total participants: {ab_tests_df['participants'].sum():,}")
    print(f"  - Average conversion rate: {ab_tests_df['conversion_rate'].mean():.2%}")

    print(f"\nFeature Usage: {feature_usage_df.height:,}")
    print(f"  - Unique features: {feature_usage_df['feature_name'].n_unique():,}")
    print(
        f"  - Feature categories: {feature_usage_df.group_by('feature_category').count().to_dict(as_series=False)}"
    )

    print("\nProduct analytics data generation complete!")


if __name__ == "__main__":
    main()
