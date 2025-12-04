# Design: Restructure Examples Ecosystem

## Architecture Overview

The new examples structure follows a **layered learning approach** with numbered categories ensuring clear progression:

```
examples/
├── README.md (learning path)
├── _shared/ (reusable utilities)
├── 01-getting-started/ (4 simple examples)
├── 02-intermediate/ (4 moderate examples)
├── 03-advanced/ (6 complex examples)
├── 04-external-services/ (3 docker-based)
├── 05-use-cases/ (3 real-world patterns)
└── playground/ (interactive exploration)
```

## Key Design Decisions

### 1. Numbered Categories
Using `01-`, `02-`, etc. ensures:
- Natural sorting in file explorers
- Clear learning sequence
- Easy cross-referencing

### 2. Shared Data Generators
Location: `_shared/data_generators/`

```python
# Shared generator interface
class DataGenerator:
    def generate(self, size: str) -> None:  # size: small, medium, large
        """Generate data files"""
    
    def cleanup(self) -> None:
        """Remove generated files"""
```

Using `faker` for realistic test data:
- Names, addresses, dates, product descriptions
- Configurable size (rows: 100, 1000, 10000)
- Outputs: parquet, csv, sqlite, duckdb

### 3. Docker Compose Integration
For external service examples:

**postgres/**:
```yaml
services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_USER: duckalog
      POSTGRES_PASSWORD: duckalog
      POSTGRES_DB: demo
    ports: ["5432:5432"]
volumes:
  postgres_data:
```

**s3-minio/**:
```yaml
services:
  minio:
    image: minio/minio:latest
    command: server /data --console-address ":9001"
    environment:
      MINIO_ROOT_USER: minioadmin
      MINIO_ROOT_PASSWORD: minioadmin
    ports: ["9000:9000", "9001:9001"]
  createbucket:
    image: minio/mc
    depends_on: [minio]
    entrypoint: >
      /bin/sh -c "
      mc alias set local http://minio:9000 minioadmin minioadmin &&
      mc mb local/sample-bucket &&
      exit 0
      "
```

**multi-source-full/**:
```yaml
services:
  postgres:
    image: postgres:15
  minio:
    image: minio/minio:latest
  duckalog:
    image: duckalog:latest
    depends_on: [postgres, minio]
    command: build catalog.yaml
```

### 4. Makefile Standardization
Each external service example includes a Makefile:

```makefile
.PHONY: up down build setup clean test

up:
    docker-compose up -d postgres
    @echo "PostgreSQL is ready on port 5432"

build:
    duckalog build catalog.yaml

setup:
    python setup.py

test:
    duckalog validate catalog.yaml
    python validate.py

clean:
    docker-compose down -v
    rm -rf data/*.duckdb data/*.parquet data/*.csv
```

### 5. Example Template
Consistent structure for every example:

```
<example-name>/
├── README.md              # What, prerequisites, quick start (3-5 commands)
├── catalog.yaml           # Duckalog configuration
├── setup.py               # Data generation script
├── validate.py            # Optional validation script
├── sql/                   # Optional: external SQL files
│   ├── view1.sql
│   └── view2.sql
├── data/                  # Generated data (not in git)
│   └── .gitkeep
└── Makefile               # For external service examples
```

### 6. Data File Management
- **No pre-built data** in git
- Only `.gitkeep` files in `data/` directories
- `setup.py` generates all data on demand
- Cleanup: `rm -rf examples/*/data/*.parquet examples/*/data/*.duckdb`

### 7. Migration Strategy
**Files to migrate**:
- `semantic_layer_v2/` → `03-advanced/01-semantic-layer-v2/`
- `production-operations/environment-variables-security/` → `03-advanced/02-environment-variables/`
- `production-operations/duckdb-performance-settings/` → `03-advanced/03-performance-tuning/`
- `business-intelligence/*/` → `05-use-cases/*/`

**Files to delete**:
- `production-operations/ci-cd-integration/` (removed per user decision)
- All `.duckdb`, `.parquet`, `.db` data files
- `sql-file-references-example.yaml` (incomplete)
- Old folder structure

### 8. Learn to Build Pattern
Each example follows a pattern:

1. **What it demonstrates**: One sentence overview
2. **Prerequisites**: What user needs (python, docker, etc.)
3. **Quick start**: 3-5 commands maximum
4. **Expected output**: What user should see
5. **Key concepts**: Important duckalog features used
6. **Next steps**: Where to go from here

Example:
```markdown
# Parquet Basics

This example shows how to create views from Parquet files.

## Prerequisites
- Python 3.12+
- duckalog installed
- 50MB free disk space

## Quick Start
```bash
cd 01-getting-started/01-parquet-basics
python setup.py
duckalog build catalog.yaml
duckalog query "SELECT COUNT(*) FROM user_events"
```

## Expected Output
- `data/users.parquet` created
- `catalog.duckdb` database created
- Query returns count of users

## Key Concepts
- Parquet file sources
- Basic view creation
- Simple SQL queries

## Next Steps
- Try 02-csv-basics for CSV format
- See 03-duckdb-attachment to attach existing databases
```

### 9. Testing Strategy
Each example includes:
- `setup.py` that can be run independently
- `validate.py` that checks the catalog was built correctly
- Optional `Makefile test` target for docker examples

### 10. Size Management
Examples designed for different use cases:

**Getting Started**: 10-100 rows of data
- Quick to generate
- Easy to understand
- Fast to run

**Intermediate**: 1,000-10,000 rows
- More realistic queries
- Better performance testing
- Joins across sources

**Advanced**: 10,000-100,000 rows
- Performance testing
- Complex transformations
- Production-like scenarios

**Use Cases**: Variable size
- Customer analytics: 10,000 customers
- Product analytics: 100,000 events
- Time series: 1 year of daily data

## Trade-offs

### Generator Library: faker vs polars
**Decision**: faker

**Rationale**:
- More realistic data (names, addresses, dates)
- Easy to configure row counts
- Better for user-facing examples
- polars used only for internal data manipulation

### Iceberg/Delta Lake Setup
**Decision**: Use MinIO for S3 compatibility

**Rationale**:
- No AWS credentials needed
- Runs locally via docker
- Still demonstrates S3 concepts
- Simpler than AWS-specific setup

### Delta Lake Alternative
**Decision**: Include Delta Lake with local filesystem + Delta Lake Python library

**Rationale**:
- Delta Lake is a major format
- Important for data engineering use cases
- Python library provides standalone Delta Lake support
- Can use local filesystem without S3

## Security Considerations

1. **No credentials in examples**: Use `.env.example` templates only
2. **Redact logs**: duckalog already handles this
3. **Environment isolation**: Each example uses isolated data directories
4. **No secrets in git**: `.env` files excluded via `.gitignore`

## Performance Considerations

1. **Lazy loading**: Data only generated when `setup.py` runs
2. **Cleanup scripts**: `make clean` removes all generated files
3. **Size limits**: Examples capped at reasonable sizes
4. **Parallel execution**: docker-compose starts services in dependency order

## Future Extensibility

The structure supports adding new categories:
- `06-ml-integration/` (feature stores)
- `07-streaming/` (real-time data)
- `08-federated-queries/` (cross-database)

Each category follows the same pattern: numbered folder, README, template structure.
