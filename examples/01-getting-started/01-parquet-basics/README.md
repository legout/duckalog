# Parquet Basics

This example shows how to create views from Parquet files in duckalog.

## What it demonstrates

- Reading Parquet files as data sources
- Creating simple views
- Basic catalog structure
- Running queries on the generated catalog

## Prerequisites

- Python 3.12+
- duckalog installed (`pip install duckalog`)
- 50MB free disk space

## Quick Start

```bash
# 1. Navigate to this example
cd examples/01-getting-started/01-parquet-basics

# 2. Generate sample data
python setup.py

# 3. Build the catalog
duckalog build catalog.yaml

# 4. Query the data
duckalog query "SELECT COUNT(*) FROM users"
duckalog query "SELECT * FROM users LIMIT 5"
```

## Expected Output

```bash
# After running setup.py:
Generated 100 users in data/users.parquet

# After running duckalog build:
[INFO] Catalog built successfully: catalog.duckdb

# After duckalog query:
┌──────────────┐
│ COUNT_STAR() │
│   int64      │
├──────────────┤
│    100       │
└────────────────
```

## Key Concepts

### Parquet File Source
```yaml
views:
  - name: users
    source: parquet
    uri: "data/users.parquet"
```

This creates a view called `users` that reads from `data/users.parquet`.

### View Definition
The view name (`users`) becomes the table name you can query in DuckDB.

### Simple Query
```sql
SELECT COUNT(*) FROM users;
SELECT name, email FROM users WHERE is_active = true;
```

## Next Steps

- Try [02-csv-basics](../02-csv-basics/) to learn about CSV files
- Try [03-duckdb-attachment](../03-duckdb-attachment/) to attach existing DuckDB databases
- Try [04-sqlite-attachment](../04-sqlite-attachment/) to work with SQLite databases

## Advanced Usage

### Modify the Data
```python
# Edit setup.py to generate different data sizes
generate_users(size="medium", output_path="data/users.parquet")
```

### Add More Views
Edit `catalog.yaml` to add more views:
```yaml
views:
  - name: users
    source: parquet
    uri: "data/users.parquet"
  - name: events
    source: parquet
    uri: "data/events.parquet"
```
