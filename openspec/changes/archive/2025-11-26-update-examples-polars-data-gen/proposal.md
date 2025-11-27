# Change: Use Polars for Example Data Generation

## Why
- Pandas-based generators are slow and memory-heavy for larger example datasets and add an extra dependency footprint.
- Polars matches DuckDB's columnar workflow and improves write throughput, especially for parquet output.
- Partitioned parquet outputs make large performance/ops examples easier to scale and demo.

## What Changes
- Replace pandas with polars in all Python data generation scripts under `examples/`.
- Add partitioned parquet output options where datasets are large or time-based (e.g., performance and BI event data).
- Update example metadata/dependencies so users install `polars` instead of `pandas`; keep output compatibility with existing configs.

## Impact
- Affected specs: examples-data-generation (new capability for data generator standards)
- Affected code: example generators (`examples/**/generate*.py`, `examples/simple_parquet/gen_data.py`)
- Dependencies: add `polars` for examples; remove direct pandas reliance in generators.
