# Spec: Shared Data Generators

## Summary
Define the shared data generation system using the `faker` library to create realistic test data across all examples.

## ADDED Requirements

### Requirement: Faker Library
The `faker` library **SHALL** be added as a development dependency.

#### Scenario: Installation**
```bash
uv add --dev faker
# or
pip install faker
```

#### Scenario: Import**
All data generators import from `faker`:
```python
from faker import Faker
fake = Faker()
```

---

### Requirement: User Generator
A user data generator **SHALL** exist at `_shared/data_generators/users.py`.

#### Scenario: Generate Users**
The generator creates user data with fields:
- `id` - Unique identifier (integer)
- `name` - Full name (string)
- `email` - Email address (string)
- `signup_date` - Date (date)
- `country` - Country code (string)
- `is_active` - Boolean status

#### Scenario: Size Parameters**
The generator accepts a `size` parameter:
- `small` - 100 records
- `medium` - 1,000 records
- `large` - 10,000 records

#### Scenario: Output Formats**
The generator can output to:
- Parquet file
- CSV file
- DuckDB table
- SQLite table

---

### Requirement: Events Generator
An event data generator **SHALL** exist at `_shared/data_generators/events.py`.

#### Scenario: Generate Events**
The generator creates event data with fields:
- `event_id` - Unique identifier (integer)
- `user_id` - Reference to user (integer)
- `event_type` - Event category (string)
- `event_timestamp` - DateTime
- `properties` - JSON properties

#### Scenario: Event Types**
Common event types:
- page_view
- click
- purchase
- signup
- login
- logout

#### Scenario: Size Parameters**
Similar to users: small (1,000), medium (10,000), large (100,000)

---

### Requirement: Sales Generator
A sales data generator **SHALL** exist at `_shared/data_generators/sales.py`.

#### Scenario: Generate Sales**
The generator creates sales data with fields:
- `order_id` - Unique identifier (integer)
- `customer_id` - Reference to customer (integer)
- `product_id` - Product identifier (integer)
- `quantity` - Number of items (integer)
- `unit_price` - Price per item (decimal)
- `total_amount` - Total cost (decimal)
- `order_date` - Date
- `status` - Order status (string)

---

### Requirement: Timeseries Generator
A time-series data generator **SHALL** exist at `_shared/data_generators/timeseries.py`.

#### Scenario: Generate Timeseries**
The generator creates time-series data with fields:
- `timestamp` - DateTime
- `metric_name` - Metric identifier (string)
- `value` - Numeric value (decimal)
- `category` - Optional category (string)

#### Scenario: Time Ranges**
Supports configurable time ranges:
- Daily data for 1 year
- Hourly data for 1 week
- Monthly data for 5 years

---

### Requirement: Utils Module
A utils module **SHALL** exist at `_shared/utils.py`.

#### Scenario: Duckalog Check**
```python
def check_duckalog_installed():
    """Verify duckalog is installed and available"""
```

#### Scenario: DuckDB Connection**
```python
def verify_duckdb(db_path):
    """Open DuckDB connection and verify it works"""
```

#### Scenario: Sample Query**
```python
def run_sample_query(db_path, query):
    """Execute a sample query and return results"""
```

---

### Requirement: Setup.py Integration
All examples **SHALL** use the shared generators via `setup.py`.

#### Scenario: Setup Script**
```python
from _shared.data_generators import users, events

# Generate data
users.generate(size="small", output_format="parquet", output_path="data/users.parquet")
events.generate(size="small", output_format="parquet", output_path="data/events.parquet")

print("Data generated successfully!")
```

---

## MODIFIED Requirements

### Requirement: Example Setup Scripts
Existing example setup scripts **SHALL** be updated to use shared generators.

#### Scenario: Migration**
When migrating examples, replace custom data generation with shared generators:
- Before: `gen_data.py` with custom polars code
- After: `setup.py` using `_shared.data_generators`

---

## Validation

**Check: Faker Available**
```python
from faker import Faker
fake = Faker()
print(fake.name())  # Should print a fake name
```

**Check: Shared Generators**
```python
from _shared.data_generators import users
users.generate(size="small", output_format="parquet", output_path="test.parquet")
# Should create test.parquet with 100 users
```

**Check: Setup Scripts**
```bash
cd examples/01-getting-started/01-parquet-basics
python setup.py
ls data/
# Should show generated parquet file
```
