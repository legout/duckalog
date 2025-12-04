# SQL Transformations

This example shows how to create SQL views and transformations in duckalog.

## What it demonstrates

- Inline SQL in catalog configuration
- Common Table Expressions (CTEs)
- Complex transformations and aggregations
- Reference external SQL files

## Prerequisites

- Python 3.12+
- duckalog installed (`pip install duckalog`)
- 50MB free disk space

## Quick Start

```bash
# 1. Navigate to this example
cd examples/02-intermediate/01-sql-transformations

# 2. Generate sample data
python setup.py

# 3. Build the catalog
duckalog build catalog.yaml

# 4. Query the transformed data
duckalog query "SELECT * FROM daily_metrics LIMIT 5"
duckalog query "SELECT * FROM user_summary WHERE total_events > 5"
```

## Expected Output

```bash
# After running setup.py:
Generated 100 users in data/users.parquet
Generated 1000 events in data/events.parquet

# After running duckalog build:
[INFO] Catalog built successfully: catalog.duckdb

# After duckalog query:
┌─────────────┬────────────┬─────────────┬──────────────┐
│ event_date  │ event_type │ event_count │ unique_users │
├─────────────┼────────────┼─────────────┼──────────────┤
│ 2024-12-01  │ page_view  │     45      │      30      │
└──────────────────────────────────────────────────────┘
```

## Key Concepts

### Inline SQL
```yaml
views:
  - name: daily_metrics
    sql: |
      WITH daily_stats AS (
        SELECT
          DATE_TRUNC('day', event_timestamp) AS event_date,
          event_type,
          COUNT(*) AS event_count,
          COUNT(DISTINCT user_id) AS unique_users
        FROM events
        GROUP BY DATE_TRUNC('day', event_timestamp), event_type
      )
      SELECT * FROM daily_stats
```

### External SQL Files
You can also reference external SQL files:
```yaml
views:
  - name: user_summary
    sql_file: "sql/user_summary.sql"
```

### Common Patterns

**Aggregations**:
```sql
COUNT(*), COUNT(DISTINCT column), SUM(amount), AVG(rating)
```

**Date/Time**:
```sql
DATE_TRUNC('day', timestamp), DATE_TRUNC('month', timestamp)
```

**Joins**:
```sql
FROM users u
LEFT JOIN events e ON u.id = e.user_id
```

**Conditional Logic**:
```sql
CASE WHEN condition THEN value ELSE default END
```

## Next Steps

- Try [02-external-sql-files](../02-external-sql-files/) to learn about external SQL references
- Try [03-multi-source-joins](../03-multi-source-joins/) to join multiple data sources
- Try [04-semantic-layer](../04-semantic-layer/) for business-friendly models

## Advanced Usage

### Subqueries
```sql
SELECT *
FROM (
  SELECT user_id, COUNT(*) AS event_count
  FROM events
  GROUP BY user_id
) subq
WHERE event_count > 10;
```

### Window Functions
```sql
SELECT
  user_id,
  event_type,
  COUNT(*) OVER (PARTITION BY user_id) AS user_total
FROM events;
```

### CTEs for Complex Logic
```sql
WITH active_users AS (
  SELECT user_id FROM events
  WHERE event_timestamp >= CURRENT_DATE - INTERVAL '30 days'
),
user_metrics AS (
  SELECT * FROM active_users
)
SELECT * FROM user_metrics;
```
