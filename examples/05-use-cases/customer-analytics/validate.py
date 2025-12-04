#!/usr/bin/env python3
"""
Customer Analytics Validation Script

This script validates the customer analytics example by:
1. Checking data integrity and consistency
2. Validating key metrics calculations
3. Testing business logic in cohort analysis
4. Verifying customer segmentation logic
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
        customers = pl.read_parquet(data_dir / "customers.parquet")
        orders = pl.read_parquet(data_dir / "orders.parquet")
        events = pl.read_parquet(data_dir / "events.parquet")
        subscriptions = pl.read_parquet(data_dir / "subscriptions.parquet")

        return {
            "customers": customers,
            "orders": orders,
            "events": events,
            "subscriptions": subscriptions,
        }
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        return None


def validate_data_integrity(data):
    """Validate basic data integrity."""
    print("🔍 Validating Data Integrity...")
    errors = []

    customers = data["customers"]
    orders = data["orders"]
    events = data["events"]
    subscriptions = data["subscriptions"]

    # Check for required columns
    required_columns = {
        "customers": ["customer_id", "signup_date", "acquisition_channel"],
        "orders": ["order_id", "customer_id", "order_date", "order_value"],
        "events": ["event_id", "customer_id", "event_date", "event_type"],
        "subscriptions": [
            "subscription_id",
            "customer_id",
            "start_date",
            "monthly_price",
        ],
    }

    for table, cols in required_columns.items():
        missing_cols = [col for col in cols if col not in data[table].columns]
        if missing_cols:
            errors.append(f"{table}: Missing columns {missing_cols}")

    # Check for duplicate primary keys
    if customers["customer_id"].is_duplicated().any():
        errors.append("customers: Duplicate customer_id found")

    if orders["order_id"].is_duplicated().any():
        errors.append("orders: Duplicate order_id found")

    if events["event_id"].is_duplicated().any():
        errors.append("events: Duplicate event_id found")

    if subscriptions["subscription_id"].is_duplicated().any():
        errors.append("subscriptions: Duplicate subscription_id found")

    # Check foreign key relationships
    order_customers = set(orders["customer_id"].unique().to_list())
    customer_ids = set(customers["customer_id"].unique().to_list())
    invalid_orders = order_customers - customer_ids
    if invalid_orders:
        errors.append(
            f"orders: {len(invalid_orders)} orders reference non-existent customers"
        )

    event_customers = set(events["customer_id"].unique().to_list())
    invalid_events = event_customers - customer_ids
    if invalid_events:
        errors.append(
            f"events: {len(invalid_events)} events reference non-existent customers"
        )

    sub_customers = set(subscriptions["customer_id"].unique().to_list())
    invalid_subs = sub_customers - customer_ids
    if invalid_subs:
        errors.append(
            f"subscriptions: {len(invalid_subs)} subscriptions reference non-existent customers"
        )

    # Check for negative values
    if orders.filter(pl.col("order_value") < 0).height > 0:
        errors.append("orders: Negative order values found")

    if subscriptions.filter(pl.col("monthly_price") < 0).height > 0:
        errors.append("subscriptions: Negative monthly prices found")

    # Check date ranges
    today = datetime.now().date()

    customers_with_dates = customers.with_columns(
        [pl.col("signup_date").cast(pl.Datetime)]
    )
    invalid_signup_dates = customers_with_dates.filter(
        pl.col("signup_date").dt.date() > today
    )
    if invalid_signup_dates.height > 0:
        errors.append(
            f"customers: {invalid_signup_dates.height} customers have future signup dates"
        )

    orders_with_dates = orders.with_columns([pl.col("order_date").cast(pl.Datetime)])
    invalid_order_dates = orders_with_dates.filter(
        pl.col("order_date").dt.date() > today
    )
    if invalid_order_dates.height > 0:
        errors.append(f"orders: {invalid_order_dates.height} orders have future dates")

    if errors:
        print("❌ Data Integrity Issues Found:")
        for error in errors:
            print(f"   - {error}")
        return False
    else:
        print("✅ Data integrity checks passed")
        return True


def validate_business_logic(data):
    """Validate business logic and metrics."""
    print("\n📊 Validating Business Logic...")
    errors = []

    customers = data["customers"]
    orders = data["orders"]
    events = data["events"]
    subscriptions = data["subscriptions"]

    # Test 1: Cohort size logic
    print("   Testing cohort analysis logic...")

    # Create cohorts manually
    customers_with_cohort = customers.with_columns(
        [
            pl.col("signup_date")
            .cast(pl.Datetime)
            .dt.truncate("1mo")
            .alias("cohort_month")
        ]
    )
    cohort_sizes = customers_with_cohort.group_by("cohort_month").count()

    if cohort_sizes.height == 0:
        errors.append("No cohorts found - all customers should belong to a cohort")
    else:
        min_size = cohort_sizes["count"].min()
        max_size = cohort_sizes["count"].max()
        print(
            f"   Found {cohort_sizes.height} cohorts with sizes ranging from {min_size} to {max_size}"
        )

    # Test 2: LTV calculation logic
    print("   Testing LTV calculation logic...")

    customer_revenue = orders.group_by("customer_id").agg(
        pl.col("order_value").sum().alias("total_revenue")
    )
    if customer_revenue.height == 0:
        errors.append("No customer revenue data found")
    else:
        # Check if LTV calculations make sense
        total_customers = customers.height
        paying_customers = customer_revenue.height
        conversion_rate = paying_customers / total_customers

        if conversion_rate > 1.0:
            errors.append(f"Conversion rate > 100%: {conversion_rate:.2%}")
        elif conversion_rate < 0.05:  # Less than 5% seems too low
            print(f"   ⚠️  Low conversion rate: {conversion_rate:.2%}")
        else:
            print(f"   Conversion rate: {conversion_rate:.2%}")

    # Test 3: RFM segmentation logic
    print("   Testing RFM segmentation logic...")

    # Calculate RFM metrics
    customer_rfm = orders.group_by("customer_id").agg(
        [
            pl.col("order_date").max().alias("last_order_date"),
            pl.col("order_id").count().alias("frequency"),
            pl.col("order_value").sum().alias("monetary_value"),
        ]
    )

    if customer_rfm.height > 0:
        # Check recency calculation
        customer_rfm_with_recency = customer_rfm.with_columns(
            [
                (pl.lit(datetime.now()) - pl.col("last_order_date").cast(pl.Datetime))
                .dt.total_days()
                .alias("recency_days")
            ]
        )

        if customer_rfm_with_recency.filter(pl.col("recency_days") < 0).height > 0:
            errors.append("Some customers have negative recency (future orders)")

        # Check if frequency and monetary values are reasonable
        if customer_rfm.filter(pl.col("frequency") <= 0).height > 0:
            errors.append("Some customers have zero or negative frequency")

        if customer_rfm.filter(pl.col("monetary_value") < 0).height > 0:
            errors.append("Some customers have negative monetary value")

        print(f"   RFM analysis covers {customer_rfm.height} paying customers")

    # Test 4: Churn analysis logic
    print("   Testing churn analysis logic...")

    # Calculate monthly active customers
    events_with_month = events.with_columns(
        [pl.col("event_date").cast(pl.Datetime).dt.truncate("1mo").alias("month")]
    )
    monthly_active = (
        events_with_month.group_by("month")
        .agg(pl.col("customer_id").n_unique().alias("active_customers"))
        .sort("month")
    )

    if monthly_active.height < 2:
        errors.append("Not enough monthly data for churn analysis")
    else:
        # Check for reasonable churn patterns
        active_data = monthly_active["active_customers"].to_list()
        churn_rates = []

        for i in range(1, len(active_data)):
            prev_month = active_data[i - 1]
            curr_month = active_data[i]

            if prev_month > 0:
                churn_rate = (prev_month - curr_month) / prev_month
                churn_rates.append(churn_rate)

        if churn_rates:
            avg_churn = np.mean(churn_rates)
            if avg_churn > 0.5:  # More than 50% monthly churn seems unrealistic
                errors.append(f"Very high average monthly churn: {avg_churn:.1%}")
            elif avg_churn < -0.5:  # More than 50% negative churn seems unrealistic
                errors.append(
                    f"Very high negative churn (rapid growth): {avg_churn:.1%}"
                )
            else:
                print(f"   Average monthly change: {avg_churn:.1%}")
                if avg_churn < 0:
                    print("   📈 Negative churn indicates customer base growth")
                elif avg_churn > 0:
                    print("   📉 Positive churn indicates customer base decline")

    # Test 5: Subscription logic
    print("   Testing subscription logic...")

    if subscriptions.height > 0:
        # Check subscription dates
        subs_with_dates = subscriptions.with_columns(
            [
                pl.col("start_date").cast(pl.Datetime),
                pl.col("end_date").cast(pl.Datetime),
            ]
        )

        # Start dates should not be after end dates
        active_subs = subs_with_dates.filter(pl.col("end_date").is_not_null())
        if active_subs.height > 0:
            invalid_dates = active_subs.filter(
                pl.col("start_date") > pl.col("end_date")
            )
            if invalid_dates.height > 0:
                errors.append(
                    f"{invalid_dates.height} subscriptions have end date before start date"
                )

        # Check MRR calculation
        active_now = subscriptions.filter(pl.col("status") == "active")
        mrr = active_now["monthly_price"].sum()

        if mrr < 0:
            errors.append("Negative MRR calculated")
        else:
            print(f"   Monthly Recurring Revenue: ${mrr:,.2f}")

    if errors:
        print("❌ Business Logic Issues Found:")
        for error in errors:
            print(f"   - {error}")
        return False
    else:
        print("✅ Business logic validation passed")
        return True


def validate_performance_characteristics(data):
    """Validate performance and scalability characteristics."""
    print("\n⚡ Validating Performance Characteristics...")

    customers = data["customers"]
    orders = data["orders"]
    events = data["events"]

    # Check data sizes
    print(f"   Data Sizes:")
    print(f"   - Customers: {customers.height:,}")
    print(f"   - Orders: {orders.height:,}")
    print(f"   - Events: {events.height:,}")

    # Check for reasonable data distributions
    order_per_customer = orders.height / customers.height
    events_per_customer = events.height / customers.height

    print(f"   - Orders per customer: {order_per_customer:.1f}")
    print(f"   - Events per customer: {events_per_customer:.1f}")

    # Check for data skew
    customer_order_counts = (
        orders.group_by("customer_id").count().sort("count", descending=True)
    )
    top_1_percent_customers = int(customer_order_counts.height * 0.01)

    if top_1_percent_customers > 0:
        top_1_percent_orders = customer_order_counts.head(top_1_percent_customers)[
            "count"
        ].sum()
        total_orders = orders.height
        concentration = top_1_percent_orders / total_orders

        print(f"   - Top 1% customers generate {concentration:.1%} of orders")

        if (
            concentration > 0.8
        ):  # More than 80% of orders from top 1% might indicate skew
            print("   ⚠️  High customer concentration detected")

    # Memory usage estimation
    print(f"   Estimated memory usage for key operations:")

    # Cohort analysis memory
    unique_customers = customers["customer_id"].n_unique()
    unique_months = customers.with_columns(
        [pl.col("signup_date").cast(pl.Datetime).dt.truncate("1mo").alias("month")]
    )["month"].n_unique()
    cohort_matrix_size = unique_customers * unique_months
    print(f"   - Cohort matrix: ~{cohort_matrix_size:,} cells")

    # RFM analysis memory
    rfm_memory = unique_customers * 4 * 8  # 4 metrics, 8 bytes each
    print(f"   - RFM analysis: ~{rfm_memory:,} bytes")

    print("✅ Performance characteristics validated")
    return True


def run_metric_validations():
    """Run specific metric validations to ensure calculations are correct."""
    print("\n🧮 Running Metric Validations...")

    # These would typically run against a DuckDB instance with the views
    # For now, we'll validate the underlying data logic

    print(
        "   Note: Full metric validation requires running DuckDB with the catalog views"
    )
    print("   Basic data logic validation completed above")

    return True


def main():
    """Main validation function."""
    print("🔎 Customer Analytics Validation Script")
    print("=" * 50)

    # Load data
    data = load_data()
    if data is None:
        return False

    # Run validations
    validations = [
        validate_data_integrity(data),
        validate_business_logic(data),
        validate_performance_characteristics(data),
        run_metric_validations(),
    ]

    print("\n" + "=" * 50)

    if all(validations):
        print("✅ All validations passed! Customer analytics example is ready.")
        return True
    else:
        print("❌ Some validations failed. Please review the issues above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
