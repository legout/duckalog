#!/usr/bin/env python3
"""
Product Analytics Data Generation Script

This script generates realistic product analytics data for demonstrating
conversion funnel analysis, A/B testing, user behavior analytics,
path analysis, and real-time metrics.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import json
import os
from pathlib import Path

def generate_user_sessions(start_date="2024-01-01", end_date="2024-12-31", num_users=50000):
    """Generate user session data with realistic engagement patterns."""

    np.random.seed(789)

    start_dt = datetime.strptime(start_date, "%Y-%m-%d")
    end_dt = datetime.strptime(end_date, "%Y-%m-%d")

    sessions = []

    # Device and acquisition distributions
    devices = ['desktop', 'mobile', 'tablet']
    device_probs = [0.55, 0.35, 0.10]

    acquisition_sources = ['organic_search', 'paid_search', 'social_media', 'direct', 'email', 'referral']
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
            if device_type == 'desktop':
                # Business hours peak for desktop
                hour = np.random.choice(
                    list(range(9, 18)),
                    p=[0.10, 0.12, 0.15, 0.18, 0.20, 0.15, 0.06, 0.03, 0.01]
                )
            else:
                # More varied hours for mobile
                hour = np.random.choice(list(range(24)))

            minute = np.random.randint(0, 60)
            second = np.random.randint(0, 60)

            start_time = current_date.replace(hour=hour, minute=minute, second=second)

            # Session duration based on device and user behavior
            if device_type == 'mobile':
                duration_minutes = np.random.exponential(5)  # Shorter mobile sessions
            elif device_type == 'tablet':
                duration_minutes = np.random.exponential(8)
            else:
                duration_minutes = np.random.exponential(12)  # Longer desktop sessions

            duration_minutes = max(1, min(duration_minutes, 120))  # 1 min to 2 hours
            end_time = start_time + timedelta(minutes=duration_minutes)

            # Geographic region (simplified)
            regions = ['North America', 'Europe', 'Asia Pacific', 'Latin America']
            region_weights = [0.45, 0.25, 0.20, 0.10]
            geographic_location = np.random.choice(regions, p=region_weights)

            sessions.append({
                'session_id': session_id,
                'user_id': user_id,
                'start_time': start_time.strftime('%Y-%m-%d %H:%M:%S'),
                'end_time': end_time.strftime('%Y-%m-%d %H:%M:%S'),
                'device_type': device_type,
                'acquisition_source': acquisition_source,
                'geographic_location': geographic_location
            })

            session_counter += 1

        current_date += timedelta(days=1)

    return pd.DataFrame(sessions)

def generate_user_events(sessions_df):
    """Generate detailed user interaction events."""

    np.random.seed(456)

    events = []
    event_counter = 0

    # Feature definitions with usage patterns
    features = {
        'product_search': {'category': 'search', 'prob': 0.8, 'conversion_impact': 0.3},
        'product_view': {'category': 'catalog', 'prob': 0.9, 'conversion_impact': 0.5},
        'add_to_cart': {'category': 'conversion', 'prob': 0.3, 'conversion_impact': 0.8},
        'cart_view': {'category': 'conversion', 'prob': 0.4, 'conversion_impact': 0.6},
        'wishlist_add': {'category': 'engagement', 'prob': 0.15, 'conversion_impact': 0.2},
        'product_compare': {'category': 'catalog', 'prob': 0.2, 'conversion_impact': 0.4},
        'filter_apply': {'category': 'search', 'prob': 0.5, 'conversion_impact': 0.2},
        'sort_apply': {'category': 'search', 'prob': 0.3, 'conversion_impact': 0.1},
        'review_read': {'category': 'catalog', 'prob': 0.4, 'conversion_impact': 0.3},
        'review_write': {'category': 'engagement', 'prob': 0.05, 'conversion_impact': 0.1},
        'recommendation_click': {'category': 'catalog', 'prob': 0.25, 'conversion_impact': 0.4},
        'category_browse': {'category': 'catalog', 'prob': 0.6, 'conversion_impact': 0.2}
    }

    # Event types
    event_types = ['click', 'view', 'search', 'filter', 'purchase', 'add', 'remove']

    for _, session in sessions_df.iterrows():
        session_id = session['session_id']
        user_id = session['user_id']
        start_time = datetime.strptime(session['start_time'], '%Y-%m-%d %H:%M:%S')
        end_time = datetime.strptime(session['end_time'], '%Y-%m-%d %H:%M:%S')
        device_type = session['device_type']

        # Determine number of events based on session duration and device
        session_duration_minutes = (end_time - start_time).total_seconds() / 60

        if device_type == 'mobile':
            base_events_per_minute = 0.5
        elif device_type == 'tablet':
            base_events_per_minute = 0.7
        else:
            base_events_per_minute = 1.0

        expected_events = int(session_duration_minutes * base_events_per_minute)
        num_events = max(1, min(expected_events, int(np.random.poisson(expected_events))))

        # Generate events for this session
        current_time = start_time
        user_conversion_probability = 0.05  # Base conversion probability

        for event_num in range(num_events):
            # Select feature based on probability
            available_features = list(features.keys())
            feature_probs = [features[f]['prob'] for f in available_features]
            feature_name = np.random.choice(available_features, p=np.array(feature_probs)/sum(feature_probs))

            # Determine event type
            if feature_name == 'add_to_cart':
                event_type = 'add'
            elif feature_name == 'product_search':
                event_type = 'search'
            elif feature_name in ['product_view', 'review_read']:
                event_type = 'view'
            elif feature_name in ['filter_apply', 'sort_apply']:
                event_type = 'filter'
            else:
                event_type = 'click'

            # Random event time within session
            if event_num < num_events - 1:
                time_progress = (event_num + 1) / num_events
                max_event_time = start_time + timedelta(seconds=time_progress * (end_time - start_time).total_seconds())
                event_time = current_time + timedelta(seconds=np.random.exponential(60))
                event_time = min(event_time, max_event_time)
            else:
                event_time = end_time

            if event_time > end_time:
                break

            current_time = event_time

            # Generate event properties
            properties = {
                'device_type': device_type,
                'session_position': event_num / num_events,
                'feature_category': features[feature_name]['category']
            }

            # Add specific properties based on feature
            if feature_name == 'product_search':
                properties['search_query'] = f"term_{np.random.randint(1, 1000)}"
                properties['results_count'] = np.random.randint(5, 100)
                properties['conversion_impact'] = features[feature_name]['conversion_impact']
                user_conversion_probability += 0.02

            elif feature_name == 'product_view':
                properties['product_id'] = f"prod_{np.random.randint(1, 10000):05d}"
                properties['price_range'] = np.random.choice(['low', 'medium', 'high'], p=[0.3, 0.5, 0.2])
                properties['conversion_impact'] = features[feature_name]['conversion_impact']
                user_conversion_probability += 0.05

            elif feature_name == 'add_to_cart':
                properties['product_id'] = f"prod_{np.random.randint(1, 10000):05d}"
                properties['quantity'] = np.random.randint(1, 5)
                properties['price'] = np.random.uniform(10, 500)
                properties['conversion_impact'] = features[feature_name]['conversion_impact']
                user_conversion_probability += 0.15

            # Check for conversion event
            is_purchase = False
            if event_num == num_events - 1:  # Last event in session
                if np.random.random() < user_conversion_probability:
                    event_type = 'purchase'
                    properties['order_value'] = np.random.uniform(25, 1000)
                    properties['items_count'] = np.random.randint(1, 10)
                    is_purchase = True

            events.append({
                'event_id': f"event_{event_counter:08d}",
                'session_id': session_id,
                'user_id': user_id,
                'event_type': event_type,
                'feature_name': feature_name if not is_purchase else 'checkout',
                'event_timestamp': event_time.strftime('%Y-%m-%d %H:%M:%S'),
                'properties': json.dumps(properties)
            })

            event_counter += 1

            # Update conversion probability based on user behavior
            if 'conversion_impact' in properties:
                user_conversion_probability += properties['conversion_impact'] * 0.01

    return pd.DataFrame(events)

def generate_funnel_events(user_events_df):
    """Generate conversion funnel tracking events."""

    np.random.seed(123)

    funnel_events = []
    funnel_stages = ['page_view', 'add_to_cart', 'checkout_start', 'payment_info', 'order_confirmation']

    # Get purchase events to work backwards from
    purchase_sessions = user_events_df[user_events_df['event_type'] == 'purchase']['session_id'].unique()

    for session_id in purchase_sessions:
        session_events = user_events_df[user_events_df['session_id'] == session_id]
        user_id = session_events['user_id'].iloc[0]

        # Get session timeline
        session_events = session_events.sort_values('event_timestamp')
        purchase_time = datetime.strptime(session_events[session_events['event_type'] == 'purchase']['event_timestamp'].iloc[0], '%Y-%m-%d %H:%M:%S')

        # Generate funnel events backwards from purchase
        current_time = purchase_time - timedelta(minutes=np.random.randint(5, 30))

        for i, stage in enumerate(reversed(funnel_stages)):
            if stage == 'order_confirmation':
                event_time = purchase_time
            else:
                event_time = current_time - timedelta(minutes=np.random.randint(1, 10))
                current_time = event_time

            funnel_events.append({
                'funnel_event_id': f"funnel_{len(funnel_events):08d}",
                'user_id': user_id,
                'session_id': session_id,
                'funnel_stage': stage,
                'event_timestamp': event_time.strftime('%Y-%m-%d %H:%M:%S'),
                'properties': json.dumps({
                    'stage_order': funnel_stages.index(stage),
                    'time_to_next_stage': np.random.randint(1, 60) if i > 0 else 0
                })
            })

    # Add non-converting funnel paths
    non_purchase_sessions = user_events_df[~user_events_df['session_id'].isin(purchase_sessions)]['session_id'].unique()
    sample_non_purchase = np.random.choice(non_purchase_sessions, size=min(len(non_purchase_sessions), len(purchase_sessions) * 3), replace=False)

    for session_id in sample_non_purchase:
        session_events = user_events_df[user_events_df['session_id'] == session_id]
        if len(session_events) == 0:
            continue

        user_id = session_events['user_id'].iloc[0]
        session_start = datetime.strptime(session_events['event_timestamp'].min(), '%Y-%m-%d %H:%M:%S')

        # Determine how far user gets in funnel
        max_stage = np.random.choice([0, 1, 2], p=[0.6, 0.3, 0.1])  # Most drop early
        stages_for_session = funnel_stages[:max_stage + 1]

        for i, stage in enumerate(stages_for_session):
            event_time = session_start + timedelta(minutes=np.random.randint(i * 5, (i + 1) * 15))

            funnel_events.append({
                'funnel_event_id': f"funnel_{len(funnel_events):08d}",
                'user_id': user_id,
                'session_id': session_id,
                'funnel_stage': stage,
                'event_timestamp': event_time.strftime('%Y-%m-%d %H:%M:%S'),
                'properties': json.dumps({
                    'stage_order': i,
                    'converted': False
                })
            })

    return pd.DataFrame(funnel_events)

def generate_ab_tests():
    """Generate A/B test configurations and results."""

    np.random.seed(987)

    # Test definitions
    tests = [
        {
            'test_name': 'homepage_hero_image',
            'description': 'Testing different hero images on homepage',
            'variants': ['control', 'variant_a', 'variant_b'],
            'traffic_split': [34, 33, 33],
            'hypothesized_improvement': 0.15
        },
        {
            'test_name': 'add_to_cart_button_color',
            'description': 'Testing different button colors for add to cart',
            'variants': ['control', 'variant_a'],
            'traffic_split': [50, 50],
            'hypothesized_improvement': 0.08
        },
        {
            'test_name': 'checkout_process简化',
            'description': 'Testing simplified checkout process',
            'variants': ['control', 'variant_a'],
            'traffic_split': [50, 50],
            'hypothesized_improvement': 0.12
        },
        {
            'test_name': 'product_recommendations_algorithm',
            'description': 'Testing new recommendation algorithm',
            'variants': ['control', 'variant_a', 'variant_b', 'variant_c'],
            'traffic_split': [25, 25, 25, 25],
            'hypothesized_improvement': 0.10
        }
    ]

    ab_test_results = []

    for test in tests:
        test_id = f"test_{len(ab_test_results) + 1:03d}"
        start_date = datetime.now() - timedelta(days=np.random.randint(60, 180))
        end_date = start_date + timedelta(days=np.random.randint(14, 60))

        for variant in test['variants']:
            # Generate test participants
            base_users = 5000
            variant_users = int(base_users * (test['traffic_split'][test['variants'].index(variant)] / 100))
            variant_users = int(variant_users * np.random.uniform(0.9, 1.1))

            # Generate conversions based on variant performance
            base_conversion_rate = 0.05  # 5% base conversion rate

            if variant == 'control':
                conversion_rate = base_conversion_rate
            else:
                # Some variants win, some lose
                if np.random.random() < 0.4:  # 40% chance variant performs better
                    improvement = test['hypothesized_improvement'] * np.random.uniform(0.5, 1.5)
                    conversion_rate = base_conversion_rate * (1 + improvement)
                else:
                    decline = test['hypothesized_improvement'] * np.random.uniform(-0.5, 0.2)
                    conversion_rate = base_conversion_rate * (1 + decline)

            conversion_rate = max(0.01, min(0.15, conversion_rate))

            conversions = int(variant_users * conversion_rate)

            # Generate conversion values
            avg_conversion_value = np.random.uniform(50, 150)

            ab_test_results.append({
                'test_id': test_id,
                'test_name': test['test_name'],
                'variant': variant,
                'test_status': 'completed',
                'start_date': start_date.strftime('%Y-%m-%d'),
                'end_date': end_date.strftime('%Y-%m-%d'),
                'participants': variant_users,
                'conversions': conversions,
                'conversion_rate': conversion_rate,
                'avg_conversion_value': avg_conversion_value,
                'converted': 1  # For use in statistical calculations
            })

    return pd.DataFrame(ab_test_results)

def generate_feature_usage(user_events_df):
    """Generate feature adoption and usage tracking data."""

    np.random.seed(654)

    # Extract feature usage from user events
    feature_usage = []

    # Get all unique features and their categories
    feature_events = user_events_df[user_events_df['feature_name'].notna()]

    # Simulate longer-term usage patterns
    current_date = datetime.now()
    date_range = pd.date_range(end=current_date, periods=90, freq='D')

    # Feature categories with adoption patterns
    feature_categories = {
        'search': ['product_search', 'filter_apply', 'sort_apply'],
        'catalog': ['product_view', 'review_read', 'product_compare', 'category_browse'],
        'conversion': ['add_to_cart', 'cart_view'],
        'engagement': ['wishlist_add', 'review_write', 'recommendation_click']
    }

    for feature_name in feature_events['feature_name'].unique():
        # Determine category
        category = 'other'
        for cat, features in feature_categories.items():
            if feature_name in features:
                category = cat
                break

        # Generate adoption curve (features grow over time)
        for date in date_range:
            days_since_start = (date - date_range[0]).days

            # Adoption follows S-curve
            max_users = 5000
            adoption_rate = 1 / (1 + np.exp(-0.1 * (days_since_start - 45)))  # Sigmoid
            daily_users = int(max_users * adoption_rate * np.random.uniform(0.8, 1.2))

            # Daily usage events
            usage_events = daily_users * np.random.randint(1, 5)
            usage_duration = usage_events * np.random.uniform(10, 120)  # 10 seconds to 2 minutes per event

            feature_usage.append({
                'feature_name': feature_name,
                'feature_category': category,
                'event_date': date.strftime('%Y-%m-%d'),
                'user_id': f"user_{np.random.randint(1, 50000):06d}",  # Simulated user tracking
                'usage_duration_seconds': usage_duration,
                'usage_events': usage_events
            })

    return pd.DataFrame(feature_usage)

def main():
    """Generate all product analytics data."""

    print("Generating product analytics data...")

    # Create data directory
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)

    # Generate user sessions
    print("Generating user sessions...")
    sessions_df = generate_user_sessions()
    sessions_df.to_parquet(data_dir / "user_sessions.parquet", index=False)
    print(f"Generated {len(sessions_df):,} user sessions")

    # Generate user events
    print("Generating user events...")
    events_df = generate_user_events(sessions_df)
    events_df.to_parquet(data_dir / "user_events.parquet", index=False)
    print(f"Generated {len(events_df):,} user events")

    # Generate funnel events
    print("Generating conversion funnel events...")
    funnel_df = generate_funnel_events(events_df)
    funnel_df.to_parquet(data_dir / "funnel_events.parquet", index=False)
    print(f"Generated {len(funnel_df):,} funnel events")

    # Generate A/B test data
    print("Generating A/B test data...")
    ab_tests_df = generate_ab_tests()
    ab_tests_df.to_parquet(data_dir / "ab_tests.parquet", index=False)
    print(f"Generated {len(ab_tests_df):,} A/B test results")

    # Generate feature usage data
    print("Generating feature usage data...")
    feature_usage_df = generate_feature_usage(events_df)
    feature_usage_df.to_parquet(data_dir / "feature_usage.parquet", index=False)
    print(f"Generated {len(feature_usage_df):,} feature usage records")

    # Summary statistics
    print("\nData Summary:")
    print(f"User Sessions: {len(sessions_df):,}")
    print(f"  - Unique users: {sessions_df['user_id'].nunique():,}")
    print(f"  - Date range: {sessions_df['start_time'].min()} to {sessions_df['end_time'].max()}")
    print(f"  - Device breakdown: {sessions_df['device_type'].value_counts().to_dict()}")

    print(f"\nUser Events: {len(events_df):,}")
    print(f"  - Unique features: {events_df['feature_name'].nunique():,}")
    print(f"  - Event types: {events_df['event_type'].value_counts().to_dict()}")
    print(f"  - Purchase events: {(events_df['event_type'] == 'purchase').sum():,}")

    print(f"\nFunnel Events: {len(funnel_df):,}")
    print(f"  - Converting users: {funnel_df[funnel_df['funnel_stage'] == 'order_confirmation']['user_id'].nunique():,}")
    print(f"  - Funnel stage distribution: {funnel_df['funnel_stage'].value_counts().to_dict()}")

    print(f"\nA/B Tests: {len(ab_tests_df):,}")
    print(f"  - Number of tests: {ab_tests_df['test_name'].nunique():,}")
    print(f"  - Total participants: {ab_tests_df['participants'].sum():,}")
    print(f"  - Average conversion rate: {ab_tests_df['conversion_rate'].mean():.2%}")

    print(f"\nFeature Usage: {len(feature_usage_df):,}")
    print(f"  - Unique features: {feature_usage_df['feature_name'].nunique():,}")
    print(f"  - Feature categories: {feature_usage_df['feature_category'].value_counts().to_dict()}")

    print("\nProduct analytics data generation complete!")

if __name__ == "__main__":
    main()