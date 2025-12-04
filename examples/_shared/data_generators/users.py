"""Generate user/customer data using faker."""

import sqlite3
from typing import Optional

import duckdb
import pandas as pd
from faker import Faker

fake = Faker()


def generate_users(
    size: str = "small",
    output_format: str = "parquet",
    output_path: str = "users.parquet",
) -> None:
    """Generate user data with realistic fake data.

    Args:
        size: One of 'small' (100), 'medium' (1,000), or 'large' (10,000)
        output_format: One of 'parquet', 'csv', 'duckdb', or 'sqlite'
        output_path: Path for output file
    """
    size_map = {
        "small": 100,
        "medium": 1000,
        "large": 10000,
    }

    num_users = size_map.get(size.lower(), 100)

    users = []
    for i in range(num_users):
        users.append(
            {
                "id": i + 1,
                "name": fake.name(),
                "email": fake.email(),
                "signup_date": fake.date_between(start_date="-2y", end_date="today"),
                "country": fake.country_code(),
                "is_active": fake.boolean(chance_of_getting_true=85),
            }
        )

    df = pd.DataFrame(users)

    if output_format.lower() == "parquet":
        df.to_parquet(output_path, index=False)
    elif output_format.lower() == "csv":
        df.to_csv(output_path, index=False)
    elif output_format.lower() == "duckdb":
        conn = duckdb.connect(output_path)
        conn.register("users_df", df)
        conn.execute("CREATE TABLE users AS SELECT * FROM users_df")
        conn.close()
    elif output_format.lower() == "sqlite":
        conn = sqlite3.connect(output_path)
        df.to_sql("users", conn, if_exists="replace", index=False)
        conn.close()
    else:
        raise ValueError(f"Unsupported output format: {output_format}")

    print(f"Generated {num_users} users in {output_path}")
