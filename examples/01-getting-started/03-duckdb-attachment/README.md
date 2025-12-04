# DuckDB Attachment

This example shows how to attach existing DuckDB databases in duckalog.

## What it demonstrates

- Attaching existing DuckDB databases
- Querying attached database tables
- Read-only vs read-write attachments
- Referencing tables from attached databases

## Prerequisites

- Python 3.12+
- duckalog installed (`pip install duckalog`)
- 50MB free disk space

## Quick Start

```bash
# 1. Navigate to this example
cd examples/01-getting-started/03-duckdb-attachment

# 2. Generate sample data (creates reference.duckdb)
python setup.py

# 3. Build the catalog (attaches the DuckDB file)
duckalog build catalog.yaml

# 4. Query the attached data
duckalog query "SELECT COUNT(*) FROM reference.users"
duckalog query "SELECT * FROM reference.products LIMIT 5"
```

## Expected Output

```bash
# After running setup.py:
Generated 100 users in data/reference.duckdb (users table)
Generated 100 products in data/reference.duckdb (products table)

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

### Database Attachment
```yaml
attachments:
  duckdb:
    - alias: reference
      path: "data/reference.duckdb"
      read_only: true
```

This attaches `data/reference.duckdb` with the alias `reference`.

### Querying Attached Tables
```sql
-- Access attached table using alias.table_name
SELECT COUNT(*) FROM reference.users;

-- You can also query without alias in some cases
SELECT * FROM products;
```

### Read-Only vs Read-Write
- `read_only: true` - You can query but not modify the attached database
- `read_only: false` - You can both query and modify

## Next Steps

- Try [01-parquet-basics](../01-parquet-basics/) to see Parquet files
- Try [02-csv-basics](../02-csv-basics/) for CSV format
- Try [04-sqlite-attachment](../04-sqlite-attachment/) for SQLite databases

## Advanced Usage

### Multiple Attachments
You can attach multiple databases:
```yaml
attachments:
  duckdb:
    - alias: prod
      path: "data/production.duckdb"
    - alias: staging
      path: "data/staging.duckdb"
```

### Cross-Database Joins
```sql
-- Join tables from different attached databases
SELECT u.name, p.product_name
FROM reference.users u
JOIN reference.products p ON u.id = p.owner_id;
```
