"""Generate time-series data using faker."""

import random
import sqlite3
from datetime import datetime, timedelta
from typing import Optional

import duckdb
import numpy as np
import pandas as pd
from faker import Faker

fake = Faker()


def generate_timeseries(
    size: str = "small",
    output_format: str = "parquet",
    output_path: str = "timeseries.parquet",
    time_grain: str = "daily",
) -> None:
    """Generate time-series data with realistic fake data.

    Args:
        size: One of 'small' (1 year daily), 'medium' (1 year hourly), or 'large' (5 years daily)
        output_format: One of 'parquet', 'csv', 'duckdb', or 'sqlite'
        output_path: Path for output file
        time_grain: One of 'daily', 'hourly', or 'monthly'
    """
    size_map = {
        "small": {"days": 365, "hours": 0},
        "medium": {"days": 7, "hours": 24},
        "large": {"days": 365 * 5, "hours": 0},
    }

    params = size_map.get(size.lower(), {"days": 365, "hours": 0})

    metrics = [
        "cpu_usage",
        "memory_usage",
        "network_traffic",
        "disk_usage",
        "requests_per_second",
        "error_rate",
    ]

    categories = ["web", "api", "database", "cache", "storage"]

    data = []

    if time_grain.lower() == "daily":
        start_date = datetime.now() - timedelta(days=params["days"])
        for i in range(params["days"]):
            timestamp = start_date + timedelta(days=i)
            for metric in metrics:
                value = max(0, np.random.normal(50, 20))
                data.append(
                    {
                        "timestamp": timestamp,
                        "metric_name": metric,
                        "value": round(value, 2),
                        "category": random.choice(categories),
                    }
                )

    elif time_grain.lower() == "hourly":
        start_date = datetime.now() - timedelta(
            days=params["days"], hours=params["hours"]
        )
        for i in range(params["days"] * params["hours"]):
            timestamp = start_date + timedelta(hours=i)
            for metric in metrics:
                value = max(0, np.random.normal(50, 20))
                data.append(
                    {
                        "timestamp": timestamp,
                        "metric_name": metric,
                        "value": round(value, 2),
                        "category": random.choice(categories),
                    }
                )

    elif time_grain.lower() == "monthly":
        start_date = datetime.now() - timedelta(days=365 * params["days"])
        for i in range(params["days"]):
            timestamp = start_date + timedelta(days=i * 30)
            for metric in metrics:
                value = max(0, np.random.normal(50, 20))
                data.append(
                    {
                        "timestamp": timestamp,
                        "metric_name": metric,
                        "value": round(value, 2),
                        "category": random.choice(categories),
                    }
                )

    df = pd.DataFrame(data)

    if output_format.lower() == "parquet":
        df.to_parquet(output_path, index=False)
    elif output_format.lower() == "csv":
        df.to_csv(output_path, index=False)
    elif output_format.lower() == "duckdb":
        conn = duckdb.connect(output_path)
        conn.register("timeseries_df", df)
        conn.execute("CREATE TABLE timeseries AS SELECT * FROM timeseries_df")
        conn.close()
    elif output_format.lower() == "sqlite":
        conn = sqlite3.connect(output_path)
        df.to_sql("timeseries", conn, if_exists="replace", index=False)
        conn.close()
    else:
        raise ValueError(f"Unsupported output format: {output_format}")

    print(f"Generated {len(data)} time-series records in {output_path}")
