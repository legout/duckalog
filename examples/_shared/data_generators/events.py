"""Generate event/log data using faker."""

import random
import sqlite3
from datetime import datetime, timedelta
from typing import Optional

import duckdb
import pandas as pd
from faker import Faker

fake = Faker()


def generate_events(
    size: str = "small",
    output_format: str = "parquet",
    output_path: str = "events.parquet",
    num_users: int = 100,
) -> None:
    """Generate event data with realistic fake data.

    Args:
        size: One of 'small' (1,000), 'medium' (10,000), or 'large' (100,000)
        output_format: One of 'parquet', 'csv', 'duckdb', or 'sqlite'
        output_path: Path for output file
        num_users: Number of unique users to reference
    """
    size_map = {
        "small": 1000,
        "medium": 10000,
        "large": 100000,
    }

    num_events = size_map.get(size.lower(), 1000)

    event_types = [
        "page_view",
        "click",
        "purchase",
        "signup",
        "login",
        "logout",
        "search",
        "add_to_cart",
        "remove_from_cart",
    ]

    events = []
    start_date = datetime.now() - timedelta(days=30)

    for i in range(num_events):
        event_time = start_date + timedelta(
            seconds=random.randint(0, 30 * 24 * 60 * 60)
        )

        events.append(
            {
                "event_id": i + 1,
                "user_id": random.randint(1, num_users),
                "event_type": random.choice(event_types),
                "event_timestamp": event_time,
                "properties": {
                    "page": fake.url(),
                    "user_agent": fake.user_agent(),
                    "ip_address": fake.ipv4(),
                },
            }
        )

    df = pd.DataFrame(events)

    if output_format.lower() == "parquet":
        df.to_parquet(output_path, index=False)
    elif output_format.lower() == "csv":
        df.to_csv(output_path, index=False)
    elif output_format.lower() == "duckdb":
        conn = duckdb.connect(output_path)
        conn.register("events_df", df)
        conn.execute("CREATE TABLE events AS SELECT * FROM events_df")
        conn.close()
    elif output_format.lower() == "sqlite":
        conn = sqlite3.connect(output_path)
        df.to_sql("events", conn, if_exists="replace", index=False)
        conn.close()
    else:
        raise ValueError(f"Unsupported output format: {output_format}")

    print(f"Generated {num_events} events in {output_path}")
