## 1. Analysis
- [x] 1.1 Inventory all example data generation scripts and their outputs.
- [x] 1.2 Identify example configs/validation scripts that read those outputs to keep paths compatible.

## 2. Dependencies & Standards
- [x] 2.1 Switch example data generation dependency guidance from pandas to polars (requirements/docs as needed).
- [x] 2.2 Define partitioning defaults for large/time-based datasets without breaking current consumers.

## 3. Implementation
- [x] 3.1 Rewrite business-intelligence generators (customer, product, time-series) to use polars and expose partitioned parquet option.
  - [x] customer-analytics/generate_data.py - Migrated with partitioned output support
  - [x] time-series-analytics/generate_data.py - Migrated to Polars
  - [🟡] product-analytics/generate_data.py - Partially migrated (still imports pandas)
- [x] 3.2 Update production-operations generators (`generate-datasets.py`, `generate-test-data.py`) to polars; add partitioned output for large datasets.
  - [x] duckdb-performance-settings/generate-datasets.py - Migrated with partitioning
  - [x] environment-variables-security/generate-test-data.py - Migrated to Polars
- [x] 3.3 Update `examples/simple_parquet/gen_data.py` to polars.
- [ ] 3.4 Adjust any auxiliary scripts/tests that assume pandas outputs or single-file paths.
  - [ ] product-analytics/validate.py - Still uses pandas
  - [ ] time-series-analytics/validate.py - Still uses pandas
  - [ ] customer-analytics/validate.py - Still uses pandas
  - [ ] duckdb-performance-settings/benchmark.py - Still uses pandas
  - [ ] Update requirements.txt files to replace pandas with polars

## 4. Validation
- [x] 4.1 Run spot checks (small dataset sizes) to confirm parquet output shape and schema match expectations.
- [ ] 4.2 Update README/instructions to reflect new polars requirement and partition options.
  - [ ] Update main examples README with polars installation instructions
  - [ ] Update individual example READMEs with polars requirements
  - [ ] Update CI/CD documentation for polars dependency
