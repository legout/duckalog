# Iceberg Tables

This example shows how to work with Apache Iceberg tables in duckalog.

## What it demonstrates

- Apache Iceberg table support
- Time travel capabilities
- Schema evolution
- Partitioning strategies

## Quick Start

```bash
# Start services
make up

# Generate data
make setup

# Build catalog
make build

# Query data
duckalog query "SELECT COUNT(*) FROM iceberg_table"
```

## Notes

This example requires Docker. See the Makefile for service management commands.
