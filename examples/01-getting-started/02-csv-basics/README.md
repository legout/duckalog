# CSV Basics

This example shows how to work with CSV files in duckalog.

## What it demonstrates

- Reading CSV files as data sources
- Working with delimited data
- CSV-specific configuration options
- Converting between formats

## Prerequisites

- Python 3.12+
- duckalog installed (`pip install duckalog`)
- 50MB free disk space

## Quick Start

```bash
# 1. Navigate to this example
cd examples/01-getting-started/02-csv-basics

# 2. Generate sample data
python setup.py

# 3. Build the catalog
duckalog build catalog.yaml

# 4. Query the data
duckalog query "SELECT COUNT(*) FROM customers"
duckalog query "SELECT * FROM customers LIMIT 5"
```

## Expected Output

```bash
# After running setup.py:
Generated 100 users in data/customers.csv

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

### CSV File Source
```yaml
views:
  - name: customers
    source: csv
    uri: "data/customers.csv"
    settings:
      SAMPLE_SIZE: 1000000
```

The `settings` section allows you to configure how DuckDB reads the CSV file.

### CSV Configuration
Common CSV settings:
- `SAMPLE_SIZE` - Number of bytes to sample for type inference
- `DELIM` - Field delimiter (default: comma)
- `HEADER` - Whether first row is header (default: true)
- `AUTO_DETECT` - Automatically detect CSV options (default: true)

## Next Steps

- Try [01-parquet-basics](../01-parquet-basics/) to see Parquet format
- Try [03-duckdb-attachment](../03-duckdb-attachment/) to attach DuckDB databases
- Try [04-sqlite-attachment](../04-sqlite-attachment/) to work with SQLite

## Advanced Usage

### Custom Delimiter
Edit `catalog.yaml` to use a custom delimiter:
```yaml
views:
  - name: customers
    source: csv
    uri: "data/customers.tsv"
    settings:
      DELIM: "\t"
```

### Multiple CSV Files
```yaml
views:
  - name: customers
    source: csv
    uri: "data/customers/*.csv"
```

Note: DuckDB can read multiple CSV files with a glob pattern.
