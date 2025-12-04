# Multi-Source Joins

This example shows how to join data from multiple sources (Parquet + DuckDB) in duckalog.

## What it demonstrates

- Joining data across different sources
- Parquet files with attached DuckDB databases
- Cross-source queries and aggregations
- Data enrichment from multiple sources

## Prerequisites

- Python 3.12+
- duckalog installed (`pip install duckalog`)
- 50MB free disk space

## Quick Start

```bash
# 1. Navigate to this example
cd examples/02-intermediate/03-multi-source-joins

# 2. Generate sample data
python setup.py

# 3. Build the catalog
duckalog build catalog.yaml

# 4. Query the joined data
duckalog query "SELECT * FROM enriched_events LIMIT 5"
duckalog query "SELECT COUNT(*) FROM enriched_events WHERE u.country = 'US'"
```

## Expected Output

```bash
# After running setup.py:
Generated 100 users in data/users.parquet
Generated 100 users in data/reference.duckdb (profiles table)
Generated 1000 events in data/events.parquet

# After running duckalog build:
[INFO] Catalog built successfully: catalog.duckdb

# After duckalog query:
┌──────────────┬─────────────┬───────────┬────────────┐
│ event_id     │ user_id     │ user_name │ country    │
├──────────────┼─────────────┼───────────┼────────────┤
│      1       │      1      │  John Doe │    US      │
└─────────────────────────────────────────────────────┘
```

## Key Concepts

### Multiple Sources
```yaml
views:
  - name: users
    source: parquet
    uri: "data/users.parquet"

  - name: events
    source: parquet
    uri: "data/events.parquet"

attachments:
  duckdb:
    - alias: reference
      path: "data/reference.duckdb"
```

### Cross-Source Joins
```sql
-- Join parquet data with attached DuckDB data
SELECT
    e.event_id,
    e.user_id,
    u.name AS user_name,
    p.country AS profile_country,
    e.event_type
FROM events e
JOIN users u ON e.user_id = u.id
JOIN reference.profiles p ON e.user_id = p.id;
```

### Source Types
- **Parquet files** - Columnar storage, fast reads
- **CSV files** - Simple text format
- **DuckDB databases** - Analytics database with tables
- **SQLite databases** - Lightweight file-based database
- **PostgreSQL** - Full-featured relational database

## Next Steps

- Try [02-external-sql-files](../02-external-sql-files/) to learn about SQL organization
- Try [04-semantic-layer](../04-semantic-layer/) for business-friendly models
- Try [03-advanced/01-semantic-layer-v2](../03-advanced/01-semantic-layer-v2/) for advanced semantic models

## Advanced Usage

### Multiple Attachments
```yaml
attachments:
  duckdb:
    - alias: prod
      path: "data/production.duckdb"
    - alias: staging
      path: "data/staging.duckdb"
  sqlite:
    - alias: legacy
      path: "data/legacy.db"
```

### Complex Joins
```sql
-- Join across 3+ sources
SELECT
    u.name,
    p.bio,
    e.event_type,
    s.total_purchases
FROM users u
JOIN reference.profiles p ON u.id = p.id
JOIN events e ON u.id = e.user_id
JOIN sales_db.summary s ON u.id = s.user_id;
```

### Aggregations Across Sources
```sql
-- Aggregate data from multiple sources
SELECT
    u.country,
    COUNT(DISTINCT e.user_id) AS active_users,
    SUM(CASE WHEN e.event_type = 'purchase' THEN 1 ELSE 0 END) AS total_purchases
FROM users u
JOIN events e ON u.id = e.user_id
GROUP BY u.country
ORDER BY total_purchases DESC;
```
