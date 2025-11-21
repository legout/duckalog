# Create sample Parquet files for testing
from pathlib import Path

import duckdb
import pandas as pd

base_path = Path(__file__).parent

# Create sample data
users_df = pd.DataFrame(
    {
        "user_id": range(1, 101),
        "name": [f"User {i}" for i in range(1, 101)],
        "signup_date": pd.date_range("2023-01-01", periods=100),
        "region": ["US", "EU", "APAC"] * 33 + ["US"],
    }
)

events_df = pd.DataFrame(
    {
        "event_id": range(1, 1001),
        "user_id": [i % 100 + 1 for i in range(1000)],
        "event_type": ["page_view", "click", "purchase"] * 333 + ["page_view"],
        "timestamp": pd.date_range("2023-01-01", periods=1000, freq="H"),
        "value": [i * 0.5 for i in range(1000)],
    }
)

# Save as Parquet
users_df.to_parquet(f"{base_path}/data/users.parquet")
events_df.to_parquet(f"{base_path}/data/events.parquet")
