"""Generate small sample Parquet files for testing."""
from datetime import date, datetime, timedelta
from pathlib import Path

import polars as pl

base_path = Path(__file__).parent

def main() -> None:
    # Create sample data
    users_df = pl.DataFrame(
        {
            "user_id": range(1, 101),
            "name": [f"User {i}" for i in range(1, 101)],
            "signup_date": pl.date_range(
                date(2023, 1, 1),
                end=date(2023, 1, 1) + timedelta(days=99),
                interval="1d",
                eager=True,
            ),
            "region": ["US", "EU", "APAC"] * 33 + ["US"],
        }
    )

    events_df = pl.DataFrame(
        {
            "event_id": range(1, 1001),
            "user_id": [i % 100 + 1 for i in range(1000)],
            "event_type": ["page_view", "click", "purchase"] * 333 + ["page_view"],
            "timestamp": pl.datetime_range(
                datetime(2023, 1, 1, 0, 0, 0),
                end=datetime(2023, 1, 1, 0, 0, 0) + timedelta(hours=999),
                interval="1h",
                eager=True,
            ),
            "value": [i * 0.5 for i in range(1000)],
        }
    )

    data_dir = base_path / "data"
    data_dir.mkdir(exist_ok=True)

    users_df.write_parquet(data_dir / "users.parquet", compression="zstd")
    events_df.write_parquet(data_dir / "events.parquet", compression="zstd")


if __name__ == "__main__":
    main()
