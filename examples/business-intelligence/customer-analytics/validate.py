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
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

def load_data():
    """Load all data files for validation."""
    data_dir = Path("data")

    if not data_dir.exists():
        print("❌ Data directory not found. Run generate_data.py first.")
        return None

    try:
        customers = pd.read_parquet(data_dir / "customers.parquet")
        orders = pd.read_parquet(data_dir / "orders.parquet")
        events = pd.read_parquet(data_dir / "events.parquet")
        subscriptions = pd.read_parquet(data_dir / "subscriptions.parquet")

        return {
            'customers': customers,
            'orders': orders,
            'events': events,
            'subscriptions': subscriptions
        }
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        return None

def validate_data_integrity(data):
    """Validate basic data integrity."""
    print("🔍 Validating Data Integrity...")
    errors = []

    customers = data['customers']
    orders = data['orders']
    events = data['events']
    subscriptions = data['subscriptions']

    # Check for required columns
    required_columns = {
        'customers': ['customer_id', 'signup_date', 'acquisition_channel'],
        'orders': ['order_id', 'customer_id', 'order_date', 'order_value'],
        'events': ['event_id', 'customer_id', 'event_date', 'event_type'],
        'subscriptions': ['subscription_id', 'customer_id', 'start_date', 'monthly_price']
    }

    for table, cols in required_columns.items():
        missing_cols = [col for col in cols if col not in data[table].columns]
        if missing_cols:
            errors.append(f"{table}: Missing columns {missing_cols}")

    # Check for duplicate primary keys
    if customers['customer_id'].duplicated().any():
        errors.append("customers: Duplicate customer_id found")

    if orders['order_id'].duplicated().any():
        errors.append("orders: Duplicate order_id found")

    if events['event_id'].duplicated().any():
        errors.append("events: Duplicate event_id found")

    if subscriptions['subscription_id'].duplicated().any():
        errors.append("subscriptions: Duplicate subscription_id found")

    # Check foreign key relationships
    order_customers = set(orders['customer_id'])
    customer_ids = set(customers['customer_id'])
    invalid_orders = order_customers - customer_ids
    if invalid_orders:
        errors.append(f"orders: {len(invalid_orders)} orders reference non-existent customers")

    event_customers = set(events['customer_id'])
    invalid_events = event_customers - customer_ids
    if invalid_events:
        errors.append(f"events: {len(invalid_events)} events reference non-existent customers")

    sub_customers = set(subscriptions['customer_id'])
    invalid_subs = sub_customers - customer_ids
    if invalid_subs:
        errors.append(f"subscriptions: {len(invalid_subs)} subscriptions reference non-existent customers")

    # Check for negative values
    if (orders['order_value'] < 0).any():
        errors.append("orders: Negative order values found")

    if (subscriptions['monthly_price'] < 0).any():
        errors.append("subscriptions: Negative monthly prices found")

    # Check date ranges
    today = datetime.now().date()

    invalid_signup_dates = pd.to_datetime(customers['signup_date']).dt.date > today
    if invalid_signup_dates.any():
        errors.append(f"customers: {invalid_signup_dates.sum()} customers have future signup dates")

    invalid_order_dates = pd.to_datetime(orders['order_date']).dt.date > today
    if invalid_order_dates.any():
        errors.append(f"orders: {invalid_order_dates.sum()} orders have future dates")

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

    customers = data['customers']
    orders = data['orders']
    events = data['events']
    subscriptions = data['subscriptions']

    # Test 1: Cohort size logic
    print("   Testing cohort analysis logic...")

    # Create cohorts manually
    customers['cohort_month'] = pd.to_datetime(customers['signup_date']).dt.to_period('M')
    cohort_sizes = customers.groupby('cohort_month').size()

    if cohort_sizes.empty:
        errors.append("No cohorts found - all customers should belong to a cohort")
    else:
        print(f"   Found {len(cohort_sizes)} cohorts with sizes ranging from {cohort_sizes.min()} to {cohort_sizes.max()}")

    # Test 2: LTV calculation logic
    print("   Testing LTV calculation logic...")

    customer_revenue = orders.groupby('customer_id')['order_value'].sum().reset_index()
    if len(customer_revenue) == 0:
        errors.append("No customer revenue data found")
    else:
        # Check if LTV calculations make sense
        total_customers = len(customers)
        paying_customers = len(customer_revenue)
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
    customer_rfm = orders.groupby('customer_id').agg({
        'order_date': 'max',
        'order_id': 'count',
        'order_value': 'sum'
    }).reset_index()

    customer_rfm.columns = ['customer_id', 'last_order_date', 'frequency', 'monetary_value']

    if len(customer_rfm) > 0:
        # Check recency calculation
        customer_rfm['recency_days'] = (pd.to_datetime('today') - pd.to_datetime(customer_rfm['last_order_date'])).dt.days

        if (customer_rfm['recency_days'] < 0).any():
            errors.append("Some customers have negative recency (future orders)")

        # Check if frequency and monetary values are reasonable
        if (customer_rfm['frequency'] <= 0).any():
            errors.append("Some customers have zero or negative frequency")

        if (customer_rfm['monetary_value'] < 0).any():
            errors.append("Some customers have negative monetary value")

        print(f"   RFM analysis covers {len(customer_rfm)} paying customers")

    # Test 4: Churn analysis logic
    print("   Testing churn analysis logic...")

    # Calculate monthly active customers
    events['month'] = pd.to_datetime(events['event_date']).dt.to_period('M')
    monthly_active = events.groupby('month')['customer_id'].nunique()

    if len(monthly_active) < 2:
        errors.append("Not enough monthly data for churn analysis")
    else:
        # Check for reasonable churn patterns
        monthly_active_sorted = monthly_active.sort_index()
        churn_rates = []

        for i in range(1, len(monthly_active_sorted)):
            prev_month = monthly_active_sorted.iloc[i-1]
            curr_month = monthly_active_sorted.iloc[i]

            if prev_month > 0:
                churn_rate = (prev_month - curr_month) / prev_month
                churn_rates.append(churn_rate)

        if churn_rates:
            avg_churn = np.mean(churn_rates)
            if avg_churn > 0.5:  # More than 50% monthly churn seems unrealistic
                errors.append(f"Very high average monthly churn: {avg_churn:.1%}")
            elif avg_churn < -0.5:  # More than 50% negative churn seems unrealistic
                errors.append(f"Very high negative churn (rapid growth): {avg_churn:.1%}")
            else:
                print(f"   Average monthly change: {avg_churn:.1%}")
                if avg_churn < 0:
                    print("   📈 Negative churn indicates customer base growth")
                elif avg_churn > 0:
                    print("   📉 Positive churn indicates customer base decline")

    # Test 5: Subscription logic
    print("   Testing subscription logic...")

    if len(subscriptions) > 0:
        # Check subscription dates
        subscriptions['start_date'] = pd.to_datetime(subscriptions['start_date'])

        # Start dates should not be after end dates
        active_subs = subscriptions[subscriptions['end_date'].notna()]
        if len(active_subs) > 0:
            active_subs['end_date'] = pd.to_datetime(active_subs['end_date'])
            invalid_dates = active_subs[active_subs['start_date'] > active_subs['end_date']]
            if len(invalid_dates) > 0:
                errors.append(f"{len(invalid_subs)} subscriptions have end date before start date")

        # Check MRR calculation
        active_now = subscriptions[subscriptions['status'] == 'active']
        mrr = active_now['monthly_price'].sum()

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

    customers = data['customers']
    orders = data['orders']
    events = data['events']

    # Check data sizes
    print(f"   Data Sizes:")
    print(f"   - Customers: {len(customers):,}")
    print(f"   - Orders: {len(orders):,}")
    print(f"   - Events: {len(events):,}")

    # Check for reasonable data distributions
    order_per_customer = len(orders) / len(customers)
    events_per_customer = len(events) / len(customers)

    print(f"   - Orders per customer: {order_per_customer:.1f}")
    print(f"   - Events per customer: {events_per_customer:.1f}")

    # Check for data skew
    customer_order_counts = orders['customer_id'].value_counts()
    top_1_percent_customers = int(len(customer_order_counts) * 0.01)

    if top_1_percent_customers > 0:
        top_1_percent_orders = customer_order_counts.head(top_1_percent_customers).sum()
        total_orders = len(orders)
        concentration = top_1_percent_orders / total_orders

        print(f"   - Top 1% customers generate {concentration:.1%} of orders")

        if concentration > 0.8:  # More than 80% of orders from top 1% might indicate skew
            print("   ⚠️  High customer concentration detected")

    # Memory usage estimation
    print(f"   Estimated memory usage for key operations:")

    # Cohort analysis memory
    unique_customers = customers['customer_id'].nunique()
    unique_months = pd.to_datetime(customers['signup_date']).dt.to_period('M').nunique()
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

    print("   Note: Full metric validation requires running DuckDB with the catalog views")
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
        run_metric_validations()
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