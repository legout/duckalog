# Tasks: Restructure Examples Ecosystem

## Phase 1: Foundation
**Goal**: Create shared utilities and main documentation

- [ ] **Task 1.1**: Create `_shared/data_generators/` directory structure
  - Create `__init__.py`
  - Create `users.py` (generate user/customer data)
  - Create `events.py` (generate event/log data)
  - Create `sales.py` (generate sales/order data)
  - Create `timeseries.py` (generate time-series data)
  - Add `faker` as development dependency

- [ ] **Task 1.2**: Create `_shared/utils.py` with validation helpers
  - Helper to check if duckalog is installed
  - Helper to verify DuckDB connection
  - Helper to run sample queries

- [ ] **Task 1.3**: Create main `examples/README.md`
  - Learning path overview
  - Category descriptions
  - Prerequisites section
  - Quick start instructions
  - Links to each category

- [ ] **Task 1.4**: Create `.gitignore` entries for generated data
  - `examples/*/data/*.parquet`
  - `examples/*/data/*.duckdb`
  - `examples/*/data/*.csv`
  - `examples/*/data/*.db`

## Phase 2: Getting Started Examples (01-getting-started)
**Goal**: Create 4 simple, beginner-friendly examples

- [ ] **Task 2.1**: Create `01-parquet-basics/`
  - Create directory structure
  - Create `README.md` (what, prerequisites, quick start)
  - Create `catalog.yaml` (simple parquet view)
  - Create `setup.py` (generate 100 user records)
  - Add `data/.gitkeep`

- [ ] **Task 2.2**: Create `02-csv-basics/`
  - Create directory structure
  - Create `README.md`
  - Create `catalog.yaml` (CSV file source)
  - Create `setup.py` (generate CSV from parquet)
  - Add `data/.gitkeep`

- [ ] **Task 2.3**: Create `03-duckdb-attachment/`
  - Create directory structure
  - Create `README.md`
  - Create `catalog.yaml` (attach existing DuckDB)
  - Create `setup.py` (create reference.duckdb)
  - Add `data/.gitkeep`

- [ ] **Task 2.4**: Create `04-sqlite-attachment/`
  - Create directory structure
  - Create `README.md`
  - Create `catalog.yaml` (attach SQLite DB)
  - Create `setup.py` (create legacy.db with data)
  - Add `data/.gitkeep`

## Phase 3: Intermediate Examples (02-intermediate)
**Goal**: Create 4 moderate-complexity examples

- [ ] **Task 3.1**: Create `01-sql-transformations/`
  - Create directory structure
  - Create `README.md`
  - Create `catalog.yaml` (with inline SQL)
  - Create `setup.py` (generate sample data)
  - Create `sql/` directory with external SQL files
    - `daily_metrics.sql`
    - `user_summary.sql`

- [ ] **Task 3.2**: Create `02-external-sql-files/`
  - Create directory structure
  - Create `README.md`
  - Create `catalog.yaml` (reference external SQL files)
  - Create `setup.py` (generate data)
  - Create `sql/` directory with complete SQL files
    - `report.sql`
    - `template.sql`

- [ ] **Task 3.3**: Create `03-multi-source-joins/`
  - Create directory structure
  - Create `README.md`
  - Create `catalog.yaml` (join parquet + duckdb)
  - Create `setup.py` (generate multiple sources)
  - Add `data/.gitkeep`

- [ ] **Task 3.4**: Create `04-semantic-layer/`
  - Create directory structure
  - Create `README.md`
  - Create `catalog.yaml` (basic semantic models)
  - Create `setup.py` (generate sample tables)
  - Add `data/.gitkeep`

## Phase 4: Advanced Examples (03-advanced)
**Goal**: Migrate existing + add new advanced examples

- [ ] **Task 4.1**: Create `01-semantic-layer-v2/`
  - Migrate from `semantic_layer_v2/`
  - Update `README.md` (clearer instructions)
  - Verify `catalog.yaml` works
  - Update `setup.py` if needed
  - Ensure no pre-built data files

- [ ] **Task 4.2**: Create `02-environment-variables/`
  - Migrate from `production-operations/environment-variables-security/`
  - Remove `.env` (keep only `.env.example`)
  - Update `README.md` (security best practices)
  - Verify catalog-dev.yaml and catalog-prod.yaml
  - Clean up large pre-built files

- [ ] **Task 4.3**: Create `03-performance-tuning/`
  - Migrate from `production-operations/duckdb-performance-settings/`
  - Update `README.md` (performance guide)
  - Verify all catalog configs work
  - Keep benchmark scripts
  - Remove pre-built databases

- [ ] **Task 4.4**: Create `04-iceberg/` (NEW)
  - Create directory structure
  - Create `README.md` (Iceberg setup)
  - Create `docker-compose.yaml` (MinIO for S3)
  - Create `catalog.yaml` (Iceberg table source)
  - Create `Makefile` (up, down, build, setup, clean)
  - Create `setup.py` (upload to MinIO)
  - Create `init.sql` (if needed for catalog)

- [ ] **Task 4.5**: Create `05-delta-lake/` (NEW)
  - Create directory structure
  - Create `README.md` (Delta Lake setup)
  - Create `docker-compose.yaml` (MinIO for S3)
  - Create `catalog.yaml` (Delta Lake source)
  - Create `Makefile` (up, down, build, setup, clean)
  - Create `setup.py` (create Delta Lake tables)
  - Create `init.sql` (if needed)

- [ ] **Task 4.6**: Create `06-shopfloor-production/` (NEW - conditional)
  - Only if setup is feasible
  - Research EOL testing data patterns
  - Create directory structure
  - Create `README.md` (manufacturing analytics)
  - Create `catalog.yaml` (production metrics)
  - Create `docker-compose.yaml` (if needed)
  - Create `setup.py` (generate production test data)
  - Create `Makefile` if external services needed

## Phase 5: External Services (04-external-services)
**Goal**: Create docker-based examples

- [ ] **Task 5.1**: Create `postgres/` example
  - Create directory structure
  - Create `README.md` (PostgreSQL integration)
  - Create `docker-compose.yaml` (postgres:15 with seed data)
  - Create `catalog.yaml` (attach PostgreSQL)
  - Create `Makefile` (up, down, build, setup, clean, test)
  - Create `setup.py` (seed database)
  - Create `init.sql` (sample data)
  - Create `validate.py` (test connection)

- [ ] **Task 5.2**: Create `s3-minio/` example
  - Create directory structure
  - Create `README.md` (S3 integration)
  - Create `docker-compose.yaml` (MinIO setup)
  - Create `catalog.yaml` (S3 parquet files)
  - Create `Makefile` (up, down, build, setup, clean, test)
  - Create `setup.py` (upload to MinIO)
  - Create `validate.py` (verify S3 access)

- [ ] **Task 5.3**: Create `multi-source-full/` example
  - Create directory structure
  - Create `README.md` (combining multiple sources)
  - Create `docker-compose.yaml` (postgres + minio)
  - Create `catalog.yaml` (parquet + postgres + s3)
  - Create `Makefile` (up, down, build, setup, clean, test)
  - Create `setup.py` (setup all sources)
  - Create `validate.py` (verify cross-source joins)

## Phase 6: Use Cases (05-use-cases)
**Goal**: Simplify existing business intelligence examples

- [ ] **Task 6.1**: Create `customer-analytics/`
  - Migrate from `business-intelligence/customer-analytics/`
  - Simplify `README.md` (focus on business value)
  - Streamline `catalog.yaml` (reduce complexity)
  - Update `setup.py` (smaller dataset if >10MB)
  - Remove large pre-built database
  - Keep validation logic

- [ ] **Task 6.2**: Create `product-analytics/`
  - Migrate from `business-intelligence/product-analytics/`
  - Simplify `README.md`
  - Update `catalog.yaml`
  - Update `setup.py`
  - Remove large files
  - Keep validation

- [ ] **Task 6.3**: Create `time-series/`
  - Migrate from `business-intelligence/time-series-analytics/`
  - Simplify `README.md`
  - Update `catalog.yaml`
  - Update `setup.py`
  - Remove large files
  - Keep validation

## Phase 7: Cleanup
**Goal**: Remove old structure and finalize

- [ ] **Task 7.1**: Remove CI/CD integration example
  - Delete `production-operations/ci-cd-integration/`
  - Note in migration notes

- [ ] **Task 7.2**: Move playground
  - Create `playground/playground.py`
  - Copy from root `playground.py`
  - Update imports if needed
  - Update README

- [ ] **Task 7.3**: Remove old folder structure
  - Delete `semantic_layer_v2/`
  - Delete `production-operations/` directory
  - Delete `business-intelligence/` directory
  - Delete `data-integration/` directory
  - Delete `simple_parquet/` directory

- [ ] **Task 7.4**: Remove pre-built data files
  - Remove all `*.duckdb` files from examples
  - Remove all `*.parquet` files from examples
  - Remove all `*.db` files from examples
  - Remove `sql-file-references-example.yaml`

- [ ] **Task 7.5**: Update root .gitignore
  - Ensure generated data is excluded
  - Add examples-specific patterns if needed

- [ ] **Task 7.6**: Final validation
  - Test each example's `setup.py`
  - Test each example's `duckalog build catalog.yaml`
  - Verify `README.md` instructions work
  - Check docker examples with `make up`
  - Validate with `duckalog validate catalog.yaml`

- [ ] **Task 7.7**: Update main documentation
  - Update main `README.md` to point to new examples
  - Update any links in `docs/`
  - Update CONTRIBUTING.md if it mentions examples

## Verification Tasks
**Goal**: Ensure everything works

- [ ] **Task A**: Test all getting-started examples (00:30)
- [ ] **Task B**: Test all intermediate examples (01:00)
- [ ] **Task C**: Test all advanced examples (02:00)
- [ ] **Task D**: Test docker examples with make commands (01:00)
- [ ] **Task E**: Validate repository size reduction (verify no large data files)

## Notes
- Each task should be independently verifiable
- Run validation after each task
- Use `git status` to track changes
- Test on clean checkout if possible
