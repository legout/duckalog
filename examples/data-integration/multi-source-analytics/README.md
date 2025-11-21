# Multi-Source Analytics

[Category: Data Integration]
[Difficulty: Level 3 🟠]

## Business Context

This example demonstrates how to build a comprehensive analytics platform that unifies data from multiple sources. In real-world scenarios, data often lives across different systems:
- **Raw events** in cloud storage (cost-effective, high-volume)
- **Reference data** in local databases (fast access)
- **Legacy systems** in SQLite/PostgreSQL (existing infrastructure)
- **Data lake tables** in Iceberg format (processed analytics data)

This example shows how to bring all these sources together into a single DuckDB catalog that enables rich cross-source analytics.

## What You'll Learn

- Configure multiple data source types (Parquet, DuckDB, SQLite, PostgreSQL, Iceberg)
- Use environment variables for secure credential management
- Create progressive data enrichment through view composition
- Implement advanced analytics with cross-source joins
- Build executive KPI reporting with window functions
- Apply performance optimization techniques

## Prerequisites

- Python 3.9+ with Duckalog installed
- Basic understanding of SQL and database concepts
- Familiarity with cloud storage concepts (helpful but not required)

## Setup Instructions

### 1. Generate Sample Data

```bash
# Create synthetic data for all sources
python data/generate.py --rows 10000 --output data/
```

### 2. Build the Analytics Catalog

```bash
# Validate configuration
duckalog validate catalog.yaml

# Build the unified catalog
duckalog build catalog.yaml
```

### 3. Explore the Results

```bash
# Connect to DuckDB and explore
duckdb multi_source_analytics.duckdb

# Sample queries to try:
SELECT * FROM daily_kpi_report ORDER BY event_date DESC LIMIT 10;

SELECT event_type, COUNT(*) as events
FROM enriched_events
WHERE DATE(timestamp) >= CURRENT_DATE - INTERVAL 7 DAYS
GROUP BY event_type
ORDER BY events DESC;
```

## Expected Results

After running this example, you'll have:

- **`multi_source_analytics.duckdb`**: Unified catalog with all views
- **12 integrated views**: From raw data to executive KPIs
- **Synthetic datasets**: Events, users, products in multiple formats
- **Cross-source analytics**: Rich insights from combined data sources

### Key Views Created

1. **Raw Data Views**: `raw_events`, `user_profiles`, `product_data`
2. **Enriched Views**: `enriched_events` (joins across sources)
3. **Analytics Views**: `event_metrics`, `user_activity_summary`
4. **Executive Views**: `daily_kpi_report` (KPI dashboard data)

## Learning Path

- **Next examples**: [customer-analytics](../business-intelligence/customer-analytics/), [time-series](../business-intelligence/time-series/)
- **Prerequisites**: [simple-parquet](../simple_parquet/), [semantic-layer-v2](../semantic_layer_v2/)

## Key Concepts Demonstrated

- **Multi-Source Integration**: Unifying Parquet, DuckDB, SQLite, PostgreSQL
- **Progressive Enrichment**: Building from raw to enriched analytics
- **Secure Configuration**: Environment-based credential management
- **Performance Optimization**: Memory limits, threading, read-only attachments
- **Advanced Analytics**: Window functions, JSON processing, business KPIs