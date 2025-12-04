# Duckalog Examples

Learn how to use Duckalog through practical examples, from basic concepts to advanced production patterns.

## Learning Path

This examples collection is organized into **5 progressive categories** to help you learn duckalog step-by-step:

### 📚 Categories

#### 1. [01-getting-started](/01-getting-started/) - **Beginner**
Start here if you're new to duckalog. These examples show basic concepts:

- **01-parquet-basics** - Read Parquet files and create simple views
- **02-csv-basics** - Work with CSV files
- **03-duckdb-attachment** - Attach existing DuckDB databases
- **04-sqlite-attachment** - Attach SQLite databases

**⏱️ Time**: 15 minutes | **💾 Setup**: None required

---

#### 2. [02-intermediate](/02-intermediate/) - **Intermediate**
Build on the basics with SQL transformations and multi-source setups:

- **01-sql-transformations** - SQL views, CTEs, and complex queries
- **02-external-sql-files** - Reference external SQL files
- **03-multi-source-joins** - Join data from multiple sources
- **04-semantic-layer** - Business-friendly semantic models

**⏱️ Time**: 30 minutes | **💾 Setup**: None required

---

#### 3. [03-advanced](/03-advanced/) - **Advanced**
Production-ready patterns and enterprise features:

- **01-semantic-layer-v2** - Advanced semantic modeling with joins
- **02-environment-variables** - Secure credential management
- **03-performance-tuning** - DuckDB optimization for large datasets
- **04-iceberg** - Apache Iceberg table support
- **05-delta-lake** - Delta Lake format integration

**⏱️ Time**: 45 minutes | **💾 Setup**: None required

---

#### 4. [04-external-services](/04-external-services/) - **Infrastructure**
Examples with external services (PostgreSQL, S3) using Docker:

- **postgres** - PostgreSQL integration with docker-compose
- **s3-minio** - S3-compatible storage (MinIO) with docker-compose
- **multi-source-full** - Combine PostgreSQL + S3 + local files

**⏱️ Time**: 60 minutes | **💾 Setup**: Docker required

---

#### 5. [05-use-cases](/05-use-cases/) - **Real-World Patterns**
Complete examples from analytics domains:

- **customer-analytics** - Cohort analysis, LTV, customer segmentation
- **product-analytics** - Funnels, A/B testing, user behavior
- **time-series** - Moving averages, forecasting, trend analysis

**⏱️ Time**: 60 minutes | **💾 Setup**: None required

---

## Prerequisites

### Required
- **Python 3.12+**
- **duckalog** installed: `pip install duckalog`

### For Docker Examples (Category 4)
- **Docker** installed
- **docker-compose** installed

### Recommended
- Basic understanding of SQL
- Familiarity with DuckDB (helpful but not required)

## Quick Start

### Method 1: Start with Getting Started (Recommended)

```bash
# 1. Navigate to the simplest example
cd 01-getting-started/01-parquet-basics

# 2. Generate sample data
python setup.py

# 3. Build the catalog
duckalog build catalog.yaml

# 4. Query the data
duckalog query "SELECT COUNT(*) FROM users"
```

### Method 2: Use Shared Data Generators

All examples use shared data generators you can use in your own projects:

```python
from _shared.data_generators import generate_users, generate_events

# Generate sample data
generate_users(size="small", output_format="parquet", output_path="users.parquet")
generate_events(size="small", output_format="parquet", output_path="events.parquet")
```

## Example Structure

Every example follows a consistent pattern:

```
example-name/
├── README.md          # What it demonstrates, prerequisites, quick start
├── catalog.yaml       # Duckalog configuration
├── setup.py           # Data generation script
├── validate.py        # Optional: validation script
├── sql/               # Optional: external SQL files
│   ├── view1.sql
│   └── view2.sql
├── data/              # Generated data (not in git)
│   └── .gitkeep
└── Makefile           # For docker-based examples only
```

## Data Generation

All data is generated on-demand using the `faker` library. No large files are included in git.

Each example's `setup.py` script:
1. Generates realistic sample data
2. Saves to `data/` directory
3. Cleans up automatically with `make clean` (docker examples)

### Data Sizes
- **small** - 100-1,000 records (fast)
- **medium** - 1,000-10,000 records (realistic)
- **large** - 10,000-100,000 records (performance testing)

## Common Commands

```bash
# Generate data
python setup.py

# Build catalog
duckalog build catalog.yaml

# Validate catalog
duckalog validate catalog.yaml

# Query data
duckalog query "SELECT * FROM users LIMIT 10"

# Docker examples only
make up      # Start services
make build   # Build catalog
make clean   # Remove generated data and stop services
```

## Troubleshooting

### duckalog not found
```bash
pip install duckalog
```

### Python version error
```bash
python --version  # Should be 3.12+
```

### Docker examples failing
```bash
# Ensure Docker is running
docker ps

# Check docker-compose version
docker-compose --version
```

### Permission errors on data files
```bash
# Clean and regenerate
rm -rf data/*
python setup.py
```

## What's Next?

1. **Complete all examples** in a category before moving to the next
2. **Experiment** with modifying `catalog.yaml` files
3. **Try combining** concepts from different examples
4. **Read the docs** at https://duckalog.readthedocs.io
5. **Build your own** catalogs using the patterns you've learned

## Additional Resources

- [Duckalog Documentation](https://duckalog.readthedocs.io)
- [DuckDB Documentation](https://duckdb.org/docs/)
- [GitHub Repository](https://github.com/legout/duckalog)

## Contributing

See issues labeled with `good-first-issue` for beginner-friendly contributions.

---

**Questions?** Open an issue on [GitHub](https://github.com/legout/duckalog/issues)

**Found a bug?** Please report it [here](https://github.com/legout/duckalog/issues/new)
