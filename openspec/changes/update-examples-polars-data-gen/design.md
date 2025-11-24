## Context
- Example data generators currently use pandas and write single parquet files.
- Large examples (e.g., performance datasets with 1M–10M rows) are memory-heavy; pandas slows generation and write throughput.
- DuckDB reads parquet/IPC efficiently and supports directory-based partitioned datasets.

## Goals / Non-Goals
- Goals: migrate generators to polars (eager API) for speed + lower memory; add partitioned parquet output option for large/time-based datasets; keep existing configs working.
- Non-Goals: rewrite validation scripts or benchmarks to rely solely on partitioned outputs; change business logic of data generation.

## Decisions
- Use `polars` eager DataFrames; stick to Python lists/NumPy -> `pl.DataFrame` for clarity and determinism.
- Preserve existing single-file outputs for backward compatibility; add `--partitioned` flag (or similar per script) that writes partitioned parquet to a sibling directory (e.g., `data/orders_partitioned/`).
- For large performance datasets, allow partitioning by date (year/month) when flag is set to reduce file sizes; still emit single file unless `--partitioned-only` is chosen to avoid doubling disk usage.
- Keep dependency surface limited: add `polars` and remove pandas from generators; only use NumPy for random generation where already present.

## Risks / Trade-offs
- Dual outputs (single + partitioned) can increase disk usage; mitigated by optional flags.
- Validation scripts that expect single files must continue to work; hence single-file outputs stay default.
- Polars introduces new dependency; ensure requirement docs reference it.

## Open Questions
- Should CI examples consume partitioned datasets by default? (Not changing in this iteration to keep scope minimal.)
