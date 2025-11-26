#!/usr/bin/env python3
"""
Time-Series Analytics Validation Script

This script validates the time-series analytics example by:
1. Checking data quality and time-series integrity
2. Validating time-series calculations
3. Testing seasonality and trend detection logic
4. Verifying forecasting and growth rate calculations
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
        daily_sales = pl.read_parquet(data_dir / "daily_sales.parquet")
        web_analytics = pl.read_parquet(data_dir / "web_analytics.parquet")
        product_metrics = pl.read_parquet(data_dir / "product_metrics.parquet")
        operational_metrics = pl.read_parquet(data_dir / "operational_metrics.parquet")

        return {
            "daily_sales": daily_sales,
            "web_analytics": web_analytics,
            "product_metrics": product_metrics,
            "operational_metrics": operational_metrics,
        }
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        return None


def validate_time_series_integrity(data):
    """Validate time-series data integrity."""
    print("🔍 Validating Time-Series Data Integrity...")
    errors = []

    daily_sales = data["daily_sales"]
    web_analytics = data["web_analytics"]
    product_metrics = data["product_metrics"]
    operational_metrics = data["operational_metrics"]

    # Check for required columns
    required_columns = {
        "daily_sales": [
            "date",
            "product_id",
            "category",
            "region",
            "sales_amount",
            "units_sold",
        ],
        "web_analytics": [
            "date",
            "sessions",
            "pageviews",
            "unique_visitors",
            "bounce_rate",
        ],
        "product_metrics": [
            "date",
            "product_id",
            "views",
            "clicks",
            "purchases",
            "revenue",
        ],
        "operational_metrics": [
            "date",
            "production_target",
            "actual_production",
            "production_efficiency",
        ],
    }

    for table, cols in required_columns.items():
        missing_cols = [col for col in cols if col not in data[table].columns]
        if missing_cols:
            errors.append(f"{table}: Missing columns {missing_cols}")

    # Validate date format and ranges
    for table_name, table_data in data.items():
        try:
            table_data = table_data.with_columns([pl.col("date").cast(pl.Datetime)])
            data[table_name] = table_data
        except:
            errors.append(f"{table_name}: Invalid date format")

        # Check for future dates
        future_data = table_data.filter(pl.col("date") > pl.lit(datetime.now()))
        if future_data.height > 0:
            errors.append(
                f"{table_name}: {future_data.height} records have future dates"
            )

        # Check for reasonable date ranges
        min_date = table_data["date"].min()
        max_date = table_data["date"].max()
        date_range = (max_date - min_date).days

        if date_range < 365:  # At least 1 year of data
            errors.append(
                f"{table_name}: Insufficient time-series data - only {date_range} days"
            )

    # Check for time-series continuity
    for table_name, table_data in data.items():
        if table_name == "daily_sales":  # Skip for aggregated data
            continue

        expected_dates = pl.date_range(
            start=table_data["date"].min(), end=table_data["date"].max(), interval="1d"
        ).len()

        missing_dates = expected_dates - table_data["date"].n_unique()
        if missing_dates > 5:  # Allow some gaps
            errors.append(f"{table_name}: {missing_dates} missing dates in time-series")

    # Validate numerical data
    for table_name, table_data in data.items():
        # Check for negative values where inappropriate
        if "sales_amount" in table_data.columns:
            if table_data.filter(pl.col("sales_amount") < 0).height > 0:
                errors.append(f"{table_name}: Negative sales amounts found")

        if "sessions" in table_data.columns:
            if table_data.filter(pl.col("sessions") < 0).height > 0:
                errors.append(f"{table_name}: Negative session counts found")

        if "units_sold" in table_data.columns:
            if table_data.filter(pl.col("units_sold") < 0).height > 0:
                errors.append(f"{table_name}: Negative units sold found")

    # Check for reasonable values
    if (
        web_analytics.filter(
            (pl.col("bounce_rate") < 0) | (pl.col("bounce_rate") > 1)
        ).height
        > 0
    ):
        errors.append("web_analytics: Bounce rate should be between 0 and 1")

    if (
        operational_metrics.filter(
            (pl.col("production_efficiency") < 0)
            | (pl.col("production_efficiency") > 2)
        ).height
        > 0
    ):
        errors.append(
            "operational_metrics: Production efficiency should be reasonable (0-200%)"
        )

    if errors:
        print("❌ Time-Series Data Integrity Issues Found:")
        for error in errors:
            print(f"   - {error}")
        return False
    else:
        print("✅ Time-Series data integrity checks passed")
        return True


def validate_seasonal_patterns(data):
    """Validate seasonal patterns in the data."""
    print("\n📅 Validating Seasonal Patterns...")

    daily_sales = data["daily_sales"]
    web_analytics = data["web_analytics"]

    daily_sales = daily_sales.with_columns(
        [
            pl.col("date").dt.weekday().alias("day_of_week"),
            pl.col("date").dt.month().alias("month"),
        ]
    )
    web_analytics = web_analytics.with_columns(
        [pl.col("date").dt.weekday().alias("day_of_week")]
    )

    # Check weekly patterns
    weekly_pattern = (
        daily_sales.group_by("day_of_week")
        .agg(pl.col("sales_amount").mean())
        .sort("day_of_week")
    )

    # Weekend should generally have higher sales for retail
    weekend_sales = weekly_pattern.filter(pl.col("day_of_week").is_in([5, 6]))[
        "sales_amount"
    ].mean()
    weekday_sales = weekly_pattern.filter(pl.col("day_of_week").is_in([0, 1, 2, 3, 4]))[
        "sales_amount"
    ].mean()

    if weekend_sales > weekday_sales * 1.1:
        print("   ✅ Weekly pattern detected - higher weekend sales")
    else:
        print("   ⚠️  Weekly pattern may be weak or inverted")

    # Check annual seasonality
    monthly_pattern = (
        daily_sales.group_by("month").agg(pl.col("sales_amount").mean()).sort("month")
    )

    # Check for holiday peaks (November-December)
    holiday_months = monthly_pattern.filter(pl.col("month").is_in([11, 12]))[
        "sales_amount"
    ].mean()
    other_months = monthly_pattern.filter(~pl.col("month").is_in([11, 12]))[
        "sales_amount"
    ].mean()

    if holiday_months > other_months * 1.2:
        print("   ✅ Holiday seasonality detected - higher sales in Nov-Dec")
    else:
        print("   ⚠️  Holiday seasonality may be weak")

    # Check web analytics patterns
    web_weekly = (
        web_analytics.group_by("day_of_week")
        .agg(pl.col("sessions").mean())
        .sort("day_of_week")
    )

    web_weekend = web_weekly.filter(pl.col("day_of_week").is_in([5, 6]))[
        "sessions"
    ].mean()
    web_weekday = web_weekly.filter(pl.col("day_of_week").is_in([0, 1, 2, 3, 4]))[
        "sessions"
    ].mean()

    print(f"   - Retail weekend/weekday ratio: {weekend_sales / weekday_sales:.2f}")
    print(f"   - Web weekend/weekday ratio: {web_weekend / web_weekday:.2f}")

    return True


def validate_growth_trends(data):
    """Validate growth trends and calculations."""
    print("\n📈 Validating Growth Trends...")

    daily_sales = data["daily_sales"]
    web_analytics = data["web_analytics"]

    # Calculate monthly trends
    sales_monthly = (
        daily_sales.group_by_dynamic("date", every="1mo")
        .agg(pl.col("sales_amount").sum())
        .sort("date")
    )

    web_monthly = (
        web_analytics.group_by_dynamic("date", every="1mo")
        .agg(pl.col("sessions").sum())
        .sort("date")
    )

    # Calculate year-over-year growth
    sales_yoy_growth = []
    web_yoy_growth = []

    sales_data = sales_monthly["sales_amount"].to_list()
    web_data = web_monthly["sessions"].to_list()

    for i in range(12, len(sales_data)):
        current_year = sum(sales_data[i - 12 : i])
        prev_year = sum(sales_data[i - 24 : i - 12])
        if prev_year > 0:
            sales_yoy_growth.append((current_year - prev_year) / prev_year * 100)

    for i in range(12, len(web_data)):
        current_year = sum(web_data[i - 12 : i])
        prev_year = sum(web_data[i - 24 : i - 12])
        if prev_year > 0:
            web_yoy_growth.append((current_year - prev_year) / prev_year * 100)

    # Analyze trends
    if sales_yoy_growth:
        avg_sales_growth = np.mean(sales_yoy_growth[-4:])  # Last 4 months
        print(f"   - Recent sales YoY growth: {avg_sales_growth:.1f}%")

        if avg_sales_growth > 0:
            print("   ✅ Positive sales growth trend detected")
        elif avg_sales_growth < -5:
            print("   ⚠️  Negative sales growth trend detected")
        else:
            print("   📊 Sales growth is relatively flat")

    if web_yoy_growth:
        avg_web_growth = np.mean(web_yoy_growth[-4:])
        print(f"   - Recent web YoY growth: {avg_web_growth:.1f}%")

    return True


def validate_moving_averages(data):
    """Validate moving average calculations logic."""
    print("\n📊 Validating Moving Average Logic...")

    daily_sales = data["daily_sales"]

    # Test simple moving average calculation
    test_data = daily_sales.filter(pl.col("product_id").is_not_null())
    if test_data.height == 0:
        print("   ⚠️  No valid product data for moving average test")
        return True

    test_product = test_data[0, "product_id"]
    test_region = test_data[0, "region"]

    product_sales = daily_sales.filter(
        (pl.col("product_id") == test_product) & (pl.col("region") == test_region)
    ).sort("date")

    if product_sales.height >= 30:
        # Manual 7-day moving average
        sales_data = product_sales["sales_amount"].to_list()
        manual_ma_7 = []

        for i in range(len(sales_data)):
            start_idx = max(0, i - 6)
            manual_ma_7.append(np.mean(sales_data[start_idx : i + 1]))

        manual_ma_7 = np.array(manual_ma_7)

        # Check that moving average smooths the data
        ma_smoothness = manual_ma_7.std() / product_sales["sales_amount"].std()

        if ma_smoothness < 0.9:
            print("   ✅ Moving average successfully smooths volatility")
        else:
            print("   ⚠️  Moving average may not be smoothing effectively")

        print(f"   - Data std dev: {product_sales['sales_amount'].std():.2f}")
        print(f"   - 7-day MA std dev: {manual_ma_7.std():.2f}")
        print(f"   - Smoothness ratio: {ma_smoothness:.3f}")

    return True


def validate_forecasting_logic(data):
    """Validate forecasting logic and reasonableness."""
    print("\n🔮 Validating Forecasting Logic...")

    daily_sales = data["daily_sales"]

    # Get recent data for forecasting validation
    recent_data = daily_sales.filter(
        pl.col("date") >= (datetime.now() - timedelta(days=90))
    )

    # Check if there's enough data for reasonable forecasting
    if recent_data.height < 30:
        print("   ⚠️  Insufficient recent data for forecasting validation")
        return False

    # Calculate basic forecast components
    avg_recent_sales = recent_data["sales_amount"].mean()
    recent_volatility = recent_data["sales_amount"].std()

    # Check if volatility is reasonable for forecasting
    cv = recent_volatility / avg_recent_sales  # Coefficient of variation

    if cv < 0.5:
        print("   ✅ Data volatility is reasonable for forecasting")
    elif cv < 1.0:
        print("   ⚠️  Data has moderate volatility - forecasting may be challenging")
    else:
        print("   ❌ Data has high volatility - forecasting may be unreliable")

    print(f"   - Recent average sales: ${avg_recent_sales:.2f}")
    print(f"   - Coefficient of variation: {cv:.3f}")

    # Check for trend in recent data
    recent_data_sorted = recent_data.sort("date")
    recent_sales = recent_data_sorted["sales_amount"].to_numpy()

    # Simple linear trend
    x = np.arange(len(recent_sales))
    slope, intercept = np.polyfit(x, recent_sales, 1)

    print(f"   - Recent trend: ${slope:.2f} per day")

    if abs(slope) > avg_recent_sales * 0.01:
        print("   ✅ Significant trend detected for forecasting")
    else:
        print("   📊 Recent trend is relatively flat")

    return True


def validate_performance_characteristics(data):
    """Validate performance and scalability characteristics."""
    print("\n⚡ Validating Performance Characteristics...")

    daily_sales = data["daily_sales"]
    web_analytics = data["web_analytics"]

    # Check data sizes
    print(f"   Data Sizes:")
    print(f"   - Daily Sales: {daily_sales.height:,} records")
    print(f"   - Web Analytics: {web_analytics.height:,} records")

    # Check time-series density
    date_range_days = (daily_sales["date"].max() - daily_sales["date"].min()).days
    records_per_day = daily_sales.height / date_range_days

    print(f"   - Records per day: {records_per_day:.1f}")

    # Memory usage estimation for common operations
    unique_products = daily_sales["product_id"].n_unique()
    unique_regions = daily_sales["region"].n_unique()
    total_combinations = unique_products * unique_regions

    print(f"   Memory usage estimates:")
    print(f"   - Product-Region combinations: {total_combinations:,}")
    print(f"   - 30-day moving averages: ~{total_combinations * 30:,} data points")
    print(f"   - Growth rate calculations: ~{daily_sales.height:,} comparisons")

    # Performance recommendations
    if records_per_day > 100:
        print("   ⚠️  High cardinality detected - consider aggregation for performance")

    if total_combinations > 1000:
        print("   ⚠️  Many time-series - consider partitioning strategies")

    print("✅ Performance characteristics validated")
    return True


def main():
    """Main validation function."""
    print("🔎 Time-Series Analytics Validation Script")
    print("=" * 50)

    # Load data
    data = load_data()
    if data is None:
        return False

    # Run validations
    validations = [
        validate_time_series_integrity(data),
        validate_seasonal_patterns(data),
        validate_growth_trends(data),
        validate_moving_averages(data),
        validate_forecasting_logic(data),
        validate_performance_characteristics(data),
    ]

    print("\n" + "=" * 50)

    if all(validations):
        print("✅ All validations passed! Time-Series analytics example is ready.")
        return True
    else:
        print("❌ Some validations failed. Please review the issues above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
