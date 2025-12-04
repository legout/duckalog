#!/usr/bin/env python3
"""
Customer Analytics Data Generation Script

This script generates realistic customer data for demonstrating
customer analytics patterns including cohort analysis, LTV calculations,
and customer segmentation.
"""

import argparse
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
    date_col: str,
    data_dir: Path,
    partitioned: bool,
    partitioned_only: bool,
) -> None:
    file_path = data_dir / f"{name}.parquet"
    partition_dir = data_dir / f"{name}_partitioned"

    if not partitioned_only:
        df.write_parquet(file_path, compression="zstd")

    if partitioned:
        df_with_parts = df.with_columns(
            pl.col(date_col).dt.year().alias("year"),
            pl.col(date_col).dt.month().alias("month"),
        )
        write_partitioned_dataset(df_with_parts, partition_dir, ["year", "month"])


def generate_customers(num_customers=10000, start_date="2022-01-01"):
    """Generate customer profiles with realistic data."""

    np.random.seed(42)  # For reproducible data

    # Customer acquisition channels with realistic distribution
    channels = [
        "organic",
        "paid_search",
        "social_media",
        "referral",
        "email_campaign",
        "direct",
    ]
    channel_probs = [0.25, 0.20, 0.15, 0.20, 0.10, 0.10]

    # Customer segments
    segments = ["enterprise", "smb", "consumer", "startup"]
    segment_probs = [0.15, 0.35, 0.40, 0.10]

    # Geographic regions
    regions = [
        "North America",
        "Europe",
        "Asia Pacific",
        "Latin America",
        "Middle East",
    ]
    region_probs = [0.40, 0.30, 0.15, 0.10, 0.05]

    # Company sizes for B2B customers
    company_sizes = ["1-10", "11-50", "51-200", "201-500", "501-1000", "1000+"]

    # Initial plans
    plans = ["basic", "pro", "enterprise", "trial"]
    plan_probs = [0.30, 0.40, 0.20, 0.10]

    # Generate signup dates with realistic distribution (more recent signups)
    start_dt = datetime.strptime(start_date, "%Y-%m-%d")
    end_dt = datetime.now()

    # Use exponential distribution for more recent signups
    signup_days = np.random.exponential(scale=365, size=num_customers)
    signup_days = np.clip(signup_days, 0, (end_dt - start_dt).days)
    signup_dates = [start_dt + timedelta(days=int(days)) for days in signup_days]

    customers = []
    for i in range(num_customers):
        customer_id = f"CUST_{i + 1:06d}"
        segment = np.random.choice(segments, p=segment_probs)

        # B2B segments get company sizes
        company_size = None
        if segment in ["enterprise", "smb"]:
            company_size = np.random.choice(company_sizes)

        # Plan selection based on segment
        if segment == "enterprise":
            plan_probs_adj = [0.05, 0.15, 0.75, 0.05]
        elif segment == "smb":
            plan_probs_adj = [0.15, 0.55, 0.25, 0.05]
        else:
            plan_probs_adj = plan_probs

        initial_plan = np.random.choice(plans, p=plan_probs_adj)

        customers.append(
            {
                "customer_id": customer_id,
                "signup_date": signup_dates[i].date(),
                "acquisition_channel": np.random.choice(channels, p=channel_probs),
                "customer_segment": segment,
                "geographic_region": np.random.choice(regions, p=region_probs),
                "company_size": company_size,
                "initial_plan": initial_plan,
            }
        )

    return pl.DataFrame(customers)


def generate_orders(customers: pl.DataFrame, orders_per_customer_range=(1, 50)):
    """Generate order data with realistic patterns."""

    orders = []
    order_id = 1

    for customer in customers.iter_rows(named=True):
        # Number of orders based on customer segment and age
        customer_signup = customer["signup_date"]
        if isinstance(customer_signup, str):
            customer_signup = datetime.strptime(customer_signup, "%Y-%m-%d").date()
        customer_age_days = (datetime.now().date() - customer_signup).days

        # Segment-based order frequency
        if customer["customer_segment"] == "enterprise":
            base_orders = np.random.randint(5, 30)
            order_frequency = customer_age_days / 30  # Monthly orders
        elif customer["customer_segment"] == "smb":
            base_orders = np.random.randint(2, 15)
            order_frequency = customer_age_days / 45  # Less frequent
        else:
            base_orders = np.random.randint(1, 8)
            order_frequency = customer_age_days / 60  # Even less frequent

        # Limit orders based on customer age
        max_orders = int(min(base_orders, order_frequency))
        if max_orders == 0:
            continue

        num_orders = np.random.randint(min(1, max_orders), max_orders + 1)

        # Generate order dates
        signup_date = datetime.combine(customer_signup, datetime.min.time())

        for i in range(num_orders):
            # Orders are more likely to happen after some initial period
            min_days = min(7, i * 30)  # Minimum days between orders
            max_days = int((datetime.now() - signup_date).days)

            if max_days <= min_days:
                break

            order_day = np.random.randint(min_days, max_days + 1)
            order_date = signup_date + timedelta(days=order_day)

            # Order value based on customer segment
            if customer["customer_segment"] == "enterprise":
                base_value = np.random.normal(500, 200)
            elif customer["customer_segment"] == "smb":
                base_value = np.random.normal(100, 50)
            else:
                base_value = np.random.normal(50, 25)

            order_value = max(10, base_value)  # Minimum order value

            # Product categories
            categories = [
                "software_license",
                "consulting",
                "support",
                "training",
                "additional_features",
            ]
            category_weights = [0.3, 0.2, 0.2, 0.1, 0.2]
            product_category = np.random.choice(categories, p=category_weights)

            # Order types with realistic progression
            if i == 0:
                order_type = "new"
            elif (
                i >= num_orders - 2 and np.random.random() < 0.1
            ):  # 10% chance of churn
                order_type = "churn"
            elif np.random.random() < 0.3:  # 30% chance of expansion
                order_type = "expansion"
            else:
                order_type = "renewal"

            # Discount based on order type and customer segment
            if order_type == "new":
                discount = np.random.uniform(0, 0.2)  # Up to 20% for new customers
            elif customer["customer_segment"] == "enterprise":
                discount = np.random.uniform(0.1, 0.3)  # Enterprise gets discounts
            else:
                discount = np.random.uniform(0, 0.15)

            discount_amount = round(order_value * discount, 2)

            orders.append(
                {
                    "order_id": f"ORD_{order_id:08d}",
                    "customer_id": customer["customer_id"],
                    "order_date": order_date.date(),
                    "order_value": round(order_value, 2),
                    "product_category": product_category,
                    "order_type": order_type,
                    "discount_amount": discount_amount,
                }
            )

            order_id += 1

    return pl.DataFrame(orders)


def generate_events(customers: pl.DataFrame, events_per_customer_range=(10, 100)):
    """Generate user engagement events."""

    events = []
    event_id = 1

    event_types = [
        "login",
        "feature_usage",
        "purchase",
        "support_ticket",
        "page_view",
        "download",
        "webinar_attended",
        "demo_request",
    ]
    event_weights = [0.25, 0.20, 0.05, 0.10, 0.15, 0.10, 0.10, 0.05]

    for customer in customers.iter_rows(named=True):
        customer_signup = customer["signup_date"]
        if isinstance(customer_signup, str):
            customer_signup = datetime.strptime(customer_signup, "%Y-%m-%d").date()
        customer_age_days = (datetime.now().date() - customer_signup).days

        # Event frequency based on customer segment
        if customer["customer_segment"] == "enterprise":
            events_per_day = 2.5
        elif customer["customer_segment"] == "smb":
            events_per_day = 1.0
        else:
            events_per_day = 0.5

        total_events = int(
            customer_age_days * events_per_day * np.random.uniform(0.5, 1.5)
        )
        total_events = max(5, total_events)  # Minimum 5 events per customer

        signup_date = datetime.combine(customer_signup, datetime.min.time())

        for i in range(total_events):
            # Generate event timestamp
            event_day = np.random.randint(0, customer_age_days + 1)
            event_hour = np.random.randint(8, 18)  # Business hours
            event_minute = np.random.randint(0, 60)

            event_datetime = signup_date + timedelta(
                days=event_day, hours=event_hour, minutes=event_minute
            )

            event_type = np.random.choice(event_types, p=event_weights)

            # Event value for specific event types
            event_value = None
            if event_type == "purchase":
                event_value = np.random.uniform(50, 500)
            elif event_type == "support_ticket":
                event_value = np.random.uniform(25, 150)  # Cost of support

            # Session ID (group events by day for simplicity)
            session_id = f"session_{customer['customer_id']}_{event_day}"

            events.append(
                {
                    "event_id": f"EVENT_{event_id:08d}",
                    "customer_id": customer["customer_id"],
                    "event_date": event_datetime,
                    "event_type": event_type,
                    "event_value": round(event_value, 2) if event_value else None,
                    "session_id": session_id,
                }
            )

            event_id += 1

    return pl.DataFrame(events)


def generate_subscriptions(customers: pl.DataFrame):
    """Generate subscription data for recurring revenue analysis."""

    subscriptions = []
    subscription_id = 1

    tiers = ["basic", "pro", "enterprise"]
    tier_prices = {"basic": 29, "pro": 99, "enterprise": 299}

    for customer in customers.iter_rows(named=True):
        # Not all customers have subscriptions
        if np.random.random() < 0.2:  # 80% have subscriptions
            continue

        customer_signup = customer["signup_date"]
        if isinstance(customer_signup, str):
            customer_signup = datetime.strptime(customer_signup, "%Y-%m-%d").date()
        customer_age_days = (datetime.now().date() - customer_signup).days

        # Tier selection based on customer segment
        if customer["customer_segment"] == "enterprise":
            tier_probs = [0.05, 0.25, 0.70]
        elif customer["customer_segment"] == "smb":
            tier_probs = [0.20, 0.60, 0.20]
        else:
            tier_probs = [0.60, 0.35, 0.05]

        subscription_tier = np.random.choice(tiers, p=tier_probs)
        monthly_price = tier_prices[subscription_tier]

        # Billing cycle
        billing_cycle = np.random.choice(["monthly", "annual"], p=[0.7, 0.3])
        if billing_cycle == "annual":
            monthly_price = round(monthly_price * 10, 0)  # Annual discount

        # Start date (typically close to signup)
        signup_date = datetime.combine(customer_signup, datetime.min.time())
        start_delay = np.random.randint(0, 30)  # Start within 30 days of signup
        start_date = signup_date + timedelta(days=start_delay)

        # End date (some may have ended/churned)
        if np.random.random() < 0.15:  # 15% have churned
            max_duration = min(customer_age_days, 365)
            if max_duration > 30:
                subscription_duration = np.random.randint(30, max_duration + 1)
            else:
                subscription_duration = max_duration
            end_date = start_date + timedelta(days=subscription_duration)
            status = "churned"
        else:
            end_date = None
            status = "active"

        subscriptions.append(
            {
                "subscription_id": f"SUB_{subscription_id:06d}",
                "customer_id": customer["customer_id"],
                "start_date": start_date.date(),
                "end_date": end_date.date() if end_date else None,
                "monthly_price": monthly_price,
                "subscription_tier": subscription_tier,
                "billing_cycle": billing_cycle,
                "status": status,
            }
        )

        subscription_id += 1

    return pl.DataFrame(subscriptions)


def main():
    """Generate all customer analytics data."""

    parser = argparse.ArgumentParser(
        description="Generate customer analytics example data"
    )
    parser.add_argument(
        "--partitioned",
        action="store_true",
        help="Also write partitioned parquet outputs (year/month) alongside single files",
    )
    parser.add_argument(
        "--partitioned-only",
        action="store_true",
        help="Write only partitioned parquet outputs (implies --partitioned)",
    )
    args = parser.parse_args()
    if args.partitioned_only:
        args.partitioned = True

    print("Generating customer analytics data...")

    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)

    print("Generating customers...")
    customers_df = generate_customers(num_customers=10000)
    write_outputs(
        customers_df,
        "customers",
        "signup_date",
        data_dir,
        args.partitioned,
        args.partitioned_only,
    )
    print(f"Generated {customers_df.height:,} customers")

    print("Generating orders...")
    orders_df = generate_orders(customers_df)
    write_outputs(
        orders_df,
        "orders",
        "order_date",
        data_dir,
        args.partitioned,
        args.partitioned_only,
    )
    print(f"Generated {orders_df.height:,} orders")

    print("Generating events...")
    events_df = generate_events(customers_df)
    write_outputs(
        events_df,
        "events",
        "event_date",
        data_dir,
        args.partitioned,
        args.partitioned_only,
    )
    print(f"Generated {events_df.height:,} events")

    print("Generating subscriptions...")
    subscriptions_df = generate_subscriptions(customers_df)
    write_outputs(
        subscriptions_df,
        "subscriptions",
        "start_date",
        data_dir,
        args.partitioned,
        args.partitioned_only,
    )
    print(f"Generated {subscriptions_df.height:,} subscriptions")

    print("\nData Summary:")
    print(f"Customers: {customers_df.height:,}")
    print(f"Orders: {orders_df.height:,}")
    print(f"Events: {events_df.height:,}")
    print(f"Subscriptions: {subscriptions_df.height:,}")

    total_revenue = orders_df["order_value"].sum()
    avg_order_value = orders_df["order_value"].mean()
    paying_customers = orders_df["customer_id"].n_unique()

    print("\nRevenue Metrics:")
    print(f"Total Revenue: ${total_revenue:,.2f}")
    print(f"Average Order Value: ${avg_order_value:.2f}")
    print(f"Paying Customers: {paying_customers:,}")
    print(f"Conversion Rate: {paying_customers / customers_df.height * 100:.1f}%")

    active_subscriptions = subscriptions_df.filter(pl.col("status") == "active")
    mrr = active_subscriptions["monthly_price"].sum()

    print("\nSubscription Metrics:")
    print(f"Active Subscriptions: {active_subscriptions.height:,}")
    print(f"Monthly Recurring Revenue: ${mrr:,.2f}")

    print("\nCustomer analytics data generation complete!")


if __name__ == "__main__":
    main()
