# PostgreSQL Integration

This example shows how to attach and query PostgreSQL databases in duckalog.

## Quick Start

```bash
# Start PostgreSQL
make up

# Build catalog
make build

# Query data
duckalog query "SELECT COUNT(*) FROM pg_customers"
```

## Commands

- `make up` - Start PostgreSQL service
- `make build` - Build duckalog catalog
- `make clean` - Stop service and remove data
