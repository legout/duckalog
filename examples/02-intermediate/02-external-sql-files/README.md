# External SQL Files

This example shows how to reference external SQL files in duckalog catalogs.

## What it demonstrates

- Referencing external SQL files
- SQL file organization
- Template variables in SQL files
- Maintaining SQL separately from configuration

## Prerequisites

- Python 3.12+
- duckalog installed (`pip install duckalog`)
- 50MB free disk space

## Quick Start

```bash
# 1. Navigate to this example
cd examples/02-intermediate/02-external-sql-files

# 2. Generate sample data
python setup.py

# 3. Build the catalog
duckalog build catalog.yaml

# 4. Query the data
duckalog query "SELECT * FROM customer_report LIMIT 5"
duckalog query "SELECT * FROM template_report"
```

## Expected Output

```bash
# After running setup.py:
Generated 100 users in data/users.parquet
Generated 1000 events in data/events.parquet

# After running duckalog build:
[INFO] Catalog built successfully: catalog.duckdb
```

## Key Concepts

### External SQL Reference
```yaml
views:
  - name: customer_report
    sql_file: "sql/report.sql"
```

### SQL File Organization
```
example/
├── sql/
│   ├── report.sql
│   ├── template.sql
│   └── analytics.sql
├── catalog.yaml
└── setup.py
```

### Template Variables
SQL files can use template syntax:
```sql
SELECT * FROM users
WHERE signup_date >= '{{start_date}}'::DATE
  AND signup_date <= '{{end_date}}'::DATE
```

### Benefits of External SQL
- Version control SQL separately
- Share SQL between multiple catalogs
- Use SQL IDEs/editors for better syntax highlighting
- Write longer, more complex SQL queries
- Keep configuration files clean and focused

## Next Steps

- Try [01-sql-transformations](../01-sql-transformations/) to see inline SQL
- Try [03-multi-source-joins](../03-multi-source-joins/) to join multiple sources
- Try [04-semantic-layer](../04-semantic-layer/) for semantic models

## Advanced Usage

### SQL Reuse
```yaml
# Use the same SQL in multiple views with different filters
- name: active_customers
  sql_file: "sql/report.sql"

- name: inactive_customers
  sql_file: "sql/report.sql"
```

### Complex Templates
```sql
-- sql/template.sql
{% if include_inactive %}
SELECT * FROM users
{% else %}
SELECT * FROM users WHERE is_active = true
{% endif %}
```
