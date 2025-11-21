#!/usr/bin/env python3
"""
Time-Series Analytics Data Generation Script

This script generates realistic time-series data for demonstrating
time-series analytics patterns including moving averages, trends,
seasonality, and forecasting.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os
from pathlib import Path

def generate_daily_sales(start_date="2022-01-01", end_date="2024-12-31"):
    """Generate daily sales data with trends and seasonality."""

    np.random.seed(42)

    start_dt = datetime.strptime(start_date, "%Y-%m-%d")
    end_dt = datetime.strptime(end_date, "%Y-%m-%d")

    # Create date range
    dates = pd.date_range(start=start_dt, end=end_dt, freq='D')

    # Product categories and regions
    categories = ['Electronics', 'Clothing', 'Home & Garden', 'Sports', 'Books', 'Toys']
    regions = ['North', 'South', 'East', 'West', 'Central']

    # Base sales patterns for different categories
    category_patterns = {
        'Electronics': {'base': 1000, 'seasonal_amp': 0.3, 'trend': 0.02},
        'Clothing': {'base': 800, 'seasonal_amp': 0.5, 'trend': 0.01},
        'Home & Garden': {'base': 600, 'seasonal_amp': 0.4, 'trend': 0.015},
        'Sports': {'base': 500, 'seasonal_amp': 0.6, 'trend': 0.025},
        'Books': {'base': 300, 'seasonal_amp': 0.2, 'trend': -0.005},
        'Toys': {'base': 400, 'seasonal_amp': 0.7, 'trend': 0.01}
    }

    data = []

    for date in dates:
        # Calculate seasonal factors
        day_of_year = date.timetuple().tm_yday
        day_of_week = date.weekday()

        # Annual seasonality (Christmas peak, summer dip for some categories)
        annual_seasonal = 1.0 + 0.3 * np.sin(2 * np.pi * day_of_year / 365.25)

        # Weekly seasonality (weekends higher for retail)
        weekly_seasonal = 1.0 + 0.2 * (1 if day_of_week >= 5 else -0.3)

        # Holiday effects (simplified)
        is_holiday = False
        holiday_boost = 1.0

        # Christmas period (Dec 15-25)
        if date.month == 12 and 15 <= date.day <= 25:
            holiday_boost = 2.5
            is_holiday = True
        # Black Friday (4th Thursday of November)
        elif date.month == 11 and date.weekday() == 3 and 22 <= date.day <= 28:
            holiday_boost = 3.0
            is_holiday = True
        # Summer vacation (July-August for some categories)
        elif date.month in [7, 8]:
            annual_seasonal *= 0.8

        for category in categories:
            for region in regions:
                pattern = category_patterns[category]

                # Base sales with trend
                days_since_start = (date - start_dt).days
                base_sales = pattern['base'] * (1 + pattern['trend']) ** (days_since_start / 365)

                # Apply seasonal patterns
                seasonal_factor = (annual_seasonal * weekly_seasonal * holiday_boost)

                # Regional variation
                region_multiplier = np.random.uniform(0.8, 1.2)

                # Random noise
                noise = np.random.lognormal(0, 0.15)

                # Calculate final sales
                sales_amount = base_sales * seasonal_factor * region_multiplier * noise
                sales_amount = max(50, sales_amount)  # Minimum sales

                # Calculate units sold (based on price range)
                avg_price = {
                    'Electronics': 150, 'Clothing': 40, 'Home & Garden': 80,
                    'Sports': 60, 'Books': 15, 'Toys': 25
                }[category]

                units_sold = int(sales_amount / avg_price * np.random.uniform(0.8, 1.2))
                units_sold = max(1, units_sold)

                # Promotion flag (more likely during holidays and weekends)
                promotion_prob = 0.1
                if is_holiday:
                    promotion_prob = 0.4
                elif day_of_week >= 5:
                    promotion_prob = 0.2

                promotion_flag = np.random.random() < promotion_prob
                if promotion_flag:
                    sales_amount *= np.random.uniform(1.1, 1.5)

                data.append({
                    'date': date.strftime('%Y-%m-%d'),
                    'product_id': f"PROD_{category[:3].upper()}_{region[:1].upper()}_{np.random.randint(1, 100):03d}",
                    'category': category,
                    'region': region,
                    'sales_amount': round(sales_amount, 2),
                    'units_sold': units_sold,
                    'promotion_flag': promotion_flag
                })

    return pd.DataFrame(data)

def generate_web_analytics(start_date="2023-01-01", end_date="2024-12-31"):
    """Generate web analytics data with realistic patterns."""

    np.random.seed(123)

    start_dt = datetime.strptime(start_date, "%Y-%m-%d")
    end_dt = datetime.strptime(end_date, "%Y-%m-%d")

    dates = pd.date_range(start=start_dt, end=end_dt, freq='D')

    data = []

    # Base metrics with growth trend
    base_sessions = 5000
    base_pageviews = 25000
    base_conversion_rate = 0.025

    for date in dates:
        day_of_week = date.weekday()
        day_of_year = date.timetuple().tm_yday

        # Weekly pattern (weekends lower for B2B, higher for B2C)
        if day_of_week >= 5:  # Weekend
            weekly_sessions_factor = 0.7
            weekly_conversion_factor = 0.8
        else:  # Weekday
            weekly_sessions_factor = 1.2
            weekly_conversion_factor = 1.1

        # Annual growth
        days_since_start = (date - start_dt).days
        growth_factor = 1.001 ** days_since_start  # ~36% annual growth

        # Seasonal patterns
        seasonal_factor = 1.0 + 0.1 * np.sin(2 * np.pi * day_of_year / 365.25)

        # Calculate metrics
        sessions = int(base_sessions * growth_factor * weekly_sessions_factor *
                      seasonal_factor * np.random.lognormal(0, 0.1))

        pageviews = int(base_pageviews * growth_factor * weekly_sessions_factor *
                       seasonal_factor * np.random.lognormal(0, 0.08))

        # Unique visitors (typically 60-80% of sessions)
        unique_visitors_ratio = np.random.uniform(0.6, 0.8)
        unique_visitors = int(sessions * unique_visitors_ratio)

        # Bounce rate (inverse correlation with engagement)
        base_bounce_rate = 0.45
        bounce_rate = base_bounce_rate + np.random.normal(0, 0.05)
        bounce_rate = max(0.2, min(0.8, bounce_rate))

        # Average session duration
        avg_duration = np.random.lognormal(2.5, 0.3)  # ~12 minutes average
        avg_duration = max(0.5, min(30, avg_duration))

        # Conversion rate (slightly correlated with session duration)
        conversion_rate = base_conversion_rate * weekly_conversion_factor * \
                         (1 + (avg_duration - 12) / 60) + np.random.normal(0, 0.003)
        conversion_rate = max(0.01, min(0.1, conversion_rate))

        data.append({
            'date': date.strftime('%Y-%m-%d'),
            'sessions': sessions,
            'pageviews': pageviews,
            'unique_visitors': unique_visitors,
            'bounce_rate': round(bounce_rate, 3),
            'avg_session_duration': round(avg_duration, 2),
            'conversion_rate': round(conversion_rate, 4)
        })

    return pd.DataFrame(data)

def generate_product_metrics(start_date="2023-01-01", end_date="2024-12-31"):
    """Generate product performance metrics over time."""

    np.random.seed(456)

    start_dt = datetime.strptime(start_date, "%Y-%m-%d")
    end_dt = datetime.strptime(end_date, "%Y-%m-%d")

    dates = pd.date_range(start=start_dt, end=end_dt, freq='D')

    # Products with different lifecycle stages
    products = [
        {'id': 'LAPTOP_PRO', 'name': 'Laptop Pro', 'category': 'Electronics', 'lifecycle': 'mature'},
        {'id': 'SMART_WATCH', 'name': 'Smart Watch', 'category': 'Electronics', 'lifecycle': 'growth'},
        {'id': 'RUNNING_SHOES', 'name': 'Running Shoes', 'category': 'Sports', 'lifecycle': 'stable'},
        {'id': 'WINTER_JACKET', 'name': 'Winter Jacket', 'category': 'Clothing', 'lifecycle': 'seasonal'},
        {'id': 'COFFEE_MAKER', 'name': 'Coffee Maker', 'category': 'Home', 'lifecycle': 'mature'},
        {'id': 'YOGA_MAT', 'name': 'Yoga Mat', 'category': 'Sports', 'lifecycle': 'growth'}
    ]

    data = []

    for date in dates:
        day_of_year = date.timetuple().tm_yday

        for product in products:
            # Base demand based on lifecycle
            lifecycle_factors = {
                'growth': 1.5,    # Growing demand
                'mature': 1.0,    # Stable demand
                'stable': 0.8,    # Slightly declining
                'seasonal': 0.6,  # Varies by season
                'decline': 0.4    # Declining demand
            }

            base_demand = lifecycle_factors.get(product['lifecycle'], 1.0)

            # Seasonal adjustments
            seasonal_multiplier = 1.0

            if product['category'] == 'Clothing' and product['name'] == 'Winter Jacket':
                # High demand in winter months
                if date.month in [11, 12, 1, 2]:
                    seasonal_multiplier = 3.0
                elif date.month in [3, 4, 10]:
                    seasonal_multiplier = 1.5
                else:
                    seasonal_multiplier = 0.3

            elif product['category'] == 'Sports':
                if product['name'] == 'Running Shoes':
                    # Higher in spring/summer
                    if date.month in [4, 5, 6, 7, 8, 9]:
                        seasonal_multiplier = 1.5
                    else:
                        seasonal_multiplier = 0.7
                elif product['name'] == 'Yoga Mat':
                    # Relatively stable with slight indoor preference in winter
                    if date.month in [12, 1, 2]:
                        seasonal_multiplier = 1.2
                    else:
                        seasonal_multiplier = 0.9

            # Calculate metrics
            views = int(np.random.poisson(100 * base_demand * seasonal_multiplier))
            clicks = int(views * np.random.uniform(0.02, 0.08))
            add_to_carts = int(clicks * np.random.uniform(0.3, 0.7))
            purchases = int(add_to_carts * np.random.uniform(0.4, 0.8))

            # Revenue (with some variation)
            avg_price = np.random.uniform(80, 120)  # Base price with variation
            if product['id'] == 'LAPTOP_PRO':
                avg_price *= 10
            elif product['id'] == 'SMART_WATCH':
                avg_price *= 3

            revenue = purchases * avg_price

            # Customer satisfaction (varies by product quality and price)
            base_satisfaction = {
                'LAPTOP_PRO': 4.2,
                'SMART_WATCH': 3.8,
                'RUNNING_SHOES': 4.1,
                'WINTER_JACKET': 4.0,
                'COFFEE_MAKER': 4.3,
                'YOGA_MAT': 4.4
            }

            satisfaction = base_satisfaction.get(product['id'], 4.0) + np.random.normal(0, 0.2)
            satisfaction = max(1.0, min(5.0, satisfaction))

            # Stock level (simplified inventory management)
            daily_stock_change = purchases - int(np.random.poisson(20))
            current_stock = max(50, 500 + daily_stock_change)

            data.append({
                'date': date.strftime('%Y-%m-%d'),
                'product_id': product['id'],
                'product_name': product['name'],
                'category': product['category'],
                'views': views,
                'clicks': clicks,
                'add_to_carts': add_to_carts,
                'purchases': purchases,
                'revenue': round(revenue, 2),
                'avg_customer_rating': round(satisfaction, 2),
                'stock_level': current_stock,
                'conversion_rate': round(purchases / views, 4) if views > 0 else 0
            })

    return pd.DataFrame(data)

def generate_operational_metrics(start_date="2023-01-01", end_date="2024-12-31"):
    """Generate operational KPIs and performance indicators."""

    np.random.seed(789)

    start_dt = datetime.strptime(start_date, "%Y-%m-%d")
    end_dt = datetime.strptime(end_date, "%Y-%m-%d")

    dates = pd.date_range(start=start_dt, end=end_dt, freq='D')

    data = []

    for date in dates:
        day_of_week = date.weekday()

        # Production metrics
        production_target = 1000
        production_efficiency = np.random.uniform(0.85, 1.05)
        actual_production = int(production_target * production_efficiency)

        # Quality metrics
        defect_rate = np.random.lognormal(-3, 0.3)  # ~5% average defect rate
        defect_rate = max(0.001, min(0.15, defect_rate))

        # Inventory metrics
        inventory_turnover = np.random.uniform(0.8, 1.2)
        stockout_incidents = np.random.poisson(2)

        # Delivery metrics
        on_time_delivery_rate = np.random.beta(15, 3)  # ~83% average
        avg_delivery_time = np.random.lognormal(2.5, 0.3)  # ~12 days average

        # Customer service metrics
        support_tickets = np.random.poisson(50)
        avg_resolution_time = np.random.lognormal(2.0, 0.4)  # ~7.5 hours average

        # Employee productivity
        employee_count = 150
        productivity_index = np.random.uniform(0.9, 1.1)

        # Energy consumption (varies by production)
        energy_consumption = actual_production * np.random.uniform(0.8, 1.2) * 5

        data.append({
            'date': date.strftime('%Y-%m-%d'),
            'production_target': production_target,
            'actual_production': actual_production,
            'production_efficiency': round(production_efficiency, 3),
            'defect_rate': round(defect_rate, 4),
            'quality_score': round(1 - defect_rate, 3),
            'inventory_turnover': round(inventory_turnover, 2),
            'stockout_incidents': stockout_incidents,
            'on_time_delivery_rate': round(on_time_delivery_rate, 3),
            'avg_delivery_time': round(avg_delivery_time, 1),
            'support_tickets': support_tickets,
            'avg_resolution_time_hours': round(avg_resolution_time, 1),
            'employee_count': employee_count,
            'productivity_index': round(productivity_index, 3),
            'energy_consumption_kwh': round(energy_consumption, 1),
            'downtime_minutes': np.random.poisson(30)
        })

    return pd.DataFrame(data)

def main():
    """Generate all time-series analytics data."""

    print("Generating time-series analytics data...")

    # Create data directory
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)

    # Generate daily sales data
    print("Generating daily sales data...")
    daily_sales_df = generate_daily_sales()
    daily_sales_df.to_parquet(data_dir / "daily_sales.parquet", index=False)
    print(f"Generated {len(daily_sales_df):,} daily sales records")

    # Generate web analytics data
    print("Generating web analytics data...")
    web_analytics_df = generate_web_analytics()
    web_analytics_df.to_parquet(data_dir / "web_analytics.parquet", index=False)
    print(f"Generated {len(web_analytics_df):,} web analytics records")

    # Generate product metrics data
    print("Generating product metrics data...")
    product_metrics_df = generate_product_metrics()
    product_metrics_df.to_parquet(data_dir / "product_metrics.parquet", index=False)
    print(f"Generated {len(product_metrics_df):,} product metrics records")

    # Generate operational metrics data
    print("Generating operational metrics data...")
    operational_metrics_df = generate_operational_metrics()
    operational_metrics_df.to_parquet(data_dir / "operational_metrics.parquet", index=False)
    print(f"Generated {len(operational_metrics_df):,} operational metrics records")

    # Summary statistics
    print("\nData Summary:")
    print(f"Daily Sales: {len(daily_sales_df):,} records")
    print(f"  - Date range: {daily_sales_df['date'].min()} to {daily_sales_df['date'].max()}")
    print(f"  - Categories: {daily_sales_df['category'].nunique()}")
    print(f"  - Regions: {daily_sales_df['region'].nunique()}")
    print(f"  - Total sales amount: ${daily_sales_df['sales_amount'].sum():,.2f}")

    print(f"\nWeb Analytics: {len(web_analytics_df):,} records")
    print(f"  - Total sessions: {web_analytics_df['sessions'].sum():,}")
    print(f"  - Total pageviews: {web_analytics_df['pageviews'].sum():,}")
    print(f"  - Average conversion rate: {web_analytics_df['conversion_rate'].mean():.3%}")

    print(f"\nProduct Metrics: {len(product_metrics_df):,} records")
    print(f"  - Products: {product_metrics_df['product_id'].nunique()}")
    print(f"  - Total revenue: ${product_metrics_df['revenue'].sum():,.2f}")
    print(f"  - Average rating: {product_metrics_df['avg_customer_rating'].mean():.2}")

    print(f"\nOperational Metrics: {len(operational_metrics_df):,} records")
    print(f"  - Average efficiency: {operational_metrics_df['production_efficiency'].mean():.1%}")
    print(f"  - Average quality score: {operational_metrics_df['quality_score'].mean():.1%}")
    print(f"  - Average delivery rate: {operational_metrics_df['on_time_delivery_rate'].mean():.1%}")

    print("\nTime-series analytics data generation complete!")

if __name__ == "__main__":
    main()