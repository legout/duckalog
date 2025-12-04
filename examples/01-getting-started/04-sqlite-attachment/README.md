# SQLite Attachment

This example shows how to attach SQLite databases in duckalog.

## What it demonstrates

- Attaching SQLite databases
- Querying SQLite tables
- Working with legacy SQLite databases
- Cross-database compatibility

## Prerequisites

- Python 3.12+
- duckalog installed (`pip install duckalog`)
- 50MB free disk space

## Quick Start

```bash
# 1. Navigate to this example
cd examples/01-getting-started/04-sqlite-attachment

# 2. Generate sample data (creates legacy.db)
python setup.py

# 3. Build the catalog (attaches the SQLite database)
duckalog build catalog.yaml

# 4. Query the attached data
duckalog query "SELECT COUNT(*) FROM legacy.customers"
duckalog query "SELECT * FROM legacy.orders LIMIT 5"
```

## Expected Output

```bash
# After running setup.py:
Generated 100 users in data/legacy.db (customers table)
Generated 500 sales in data/legacy.db (orders table)

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

### SQLite Database Attachment
```yaml
attachments:
  sqlite:
    - alias: legacy
      path: "data/legacy.db"
```

This attaches `data/legacy.db` with the alias `legacy`.

### Querying SQLite Tables
```sql
-- Access SQLite table using alias.table_name
SELECT COUNT(*) FROM legacy.customers;

-- Query orders with joins
SELECT c.name, o.total_amount
FROM legacy.customers c
JOIN legacy.orders o ON c.id = o.customer_id;
```

### Common SQLite Use Cases
- Legacy system integration
- Application database extraction
- Local file-based databases
- Development/testing databases

## Next Steps

- Try [01-parquet-basics](../01-parquet-basics/) to see Parquet files
- Try [02-csv-basics](../02-csv-basics/) for CSV format
- Try [03-duckdb-attachment](../03-duckdb-attachment/) to attach DuckDB databases

## Advanced Usage

### Multiple SQLite Databases
```yaml
attachments:
  sqlite:
    - alias: app
      path: "data/application.db"
    - alias: reports
      path: "data/reporting.db"
```

### Complex Queries
```sql
-- Join SQLite data with Parquet data
SELECT s.name, p.total_amount
FROM sqlite_legacy.customers s
JOIN parquet_data.purchases p ON s.id = p.customer_id
WHERE s.is_active = true;
```
