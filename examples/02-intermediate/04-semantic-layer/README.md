# Semantic Layer (v1)

This example shows how to create business-friendly semantic models in duckalog.

## What it demonstrates

- Basic semantic model configuration
- Dimensions and measures
- Business-friendly naming
- User-facing abstraction layer

## Prerequisites

- Python 3.12+
- duckalog installed (`pip install duckalog`)
- 50MB free disk space

## Quick Start

```bash
# 1. Navigate to this example
cd examples/02-intermediate/04-semantic-layer

# 2. Generate sample data
python setup.py

# 3. Build the catalog
duckalog build catalog.yaml

# 4. Query using semantic models
duckalog query "SELECT * FROM customer_analytics LIMIT 5"
duckalog query "SELECT total_revenue, active_customers FROM revenue_summary"
```

## Expected Output

```bash
# After running setup.py:
Generated 100 customers in data/customers.parquet
Generated 500 sales in data/sales.parquet

# After running duckalog build:
[INFO] Catalog built successfully: catalog.duckdb
```

## Key Concepts

### Semantic Models
```yaml
semantic_models:
  - name: customer_analytics
    base_view: customers
    dimensions:
      - name: signup_date
        type: date
      - name: country
        type: string
    measures:
      - name: total_revenue
        expression: "SUM(s.total_amount)"
        agg: sum
      - name: order_count
        expression: "COUNT(*)"
        agg: count
```

### Business-Friendly Interface
```sql
-- Instead of complex SQL:
SELECT
    c.country,
    COUNT(*) AS total_customers,
    SUM(s.total_amount) AS total_revenue
FROM customers c
LEFT JOIN sales s ON c.id = s.customer_id
GROUP BY c.country;

-- Users can query:
SELECT total_revenue, active_customers FROM revenue_summary;
```

### Dimensions vs Measures
- **Dimensions** - How you slice/dice data (date, country, category)
- **Measures** - What you measure (count, sum, average)

## Next Steps

- Try [03-advanced/01-semantic-layer-v2](../../03-advanced/01-semantic-layer-v2/) for advanced features
- Try [05-use-cases/customer-analytics](../../05-use-cases/customer-analytics/) for real-world example

## Advanced Usage

### Multiple Dimensions
```yaml
dimensions:
  - name: signup_date
    type: date
  - name: country
    type: string
  - name: customer_segment
    type: string
```

### Calculated Measures
```yaml
measures:
  - name: conversion_rate
    expression: "purchases::DOUBLE / total_visits"
  - name: avg_order_value
    expression: "total_revenue / order_count"
```

### Hierarchies
```yaml
dimensions:
  - name: signup_date
    type: date
    time_grains:
      - year
      - quarter
      - month
```
