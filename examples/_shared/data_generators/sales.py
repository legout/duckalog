"""Generate sales/order data using faker."""

import random
import sqlite3
from datetime import datetime, timedelta
from typing import Optional

import duckdb
import pandas as pd
from faker import Faker

fake = Faker()


def generate_sales(
    size: str = "small",
    output_format: str = "parquet",
    output_path: str = "sales.parquet",
    num_customers: int = 100,
) -> None:
    """Generate sales data with realistic fake data.

    Args:
        size: One of 'small' (500), 'medium' (5,000), or 'large' (50,000)
        output_format: One of 'parquet', 'csv', 'duckdb', or 'sqlite'
        output_path: Path for output file
        num_customers: Number of unique customers to reference
    """
    size_map = {
        "small": 500,
        "medium": 5000,
        "large": 50000,
    }

    num_sales = size_map.get(size.lower(), 500)

    statuses = ["pending", "processing", "shipped", "delivered", "cancelled"]

    sales = []
    start_date = datetime.now() - timedelta(days=365)

    for i in range(num_sales):
        order_date = fake.date_between_dates(
            date_start=start_date, date_end=datetime.now()
        )
        quantity = random.randint(1, 5)
        unit_price = round(random.uniform(10.0, 500.0), 2)

        sales.append(
            {
                "order_id": i + 1,
                "customer_id": random.randint(1, num_customers),
                "product_id": random.randint(1, 50),
                "quantity": quantity,
                "unit_price": unit_price,
                "total_amount": round(quantity * unit_price, 2),
                "order_date": order_date,
                "status": random.choice(statuses),
            }
        )

    df = pd.DataFrame(sales)

    if output_format.lower() == "parquet":
        df.to_parquet(output_path, index=False)
    elif output_format.lower() == "csv":
        df.to_csv(output_path, index=False)
    elif output_format.lower() == "duckdb":
        conn = duckdb.connect(output_path)
        conn.register("sales_df", df)
        conn.execute("CREATE TABLE sales AS SELECT * FROM sales_df")
        conn.close()
    elif output_format.lower() == "sqlite":
        conn = sqlite3.connect(output_path)
        df.to_sql("sales", conn, if_exists="replace", index=False)
        conn.close()
    else:
        raise ValueError(f"Unsupported output format: {output_format}")

    print(f"Generated {num_sales} sales records in {output_path}")
