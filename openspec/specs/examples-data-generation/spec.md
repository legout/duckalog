# examples-data-generation Specification

## Purpose
TBD - created by archiving change update-examples-polars-data-gen. Update Purpose after archive.
## Requirements
### Requirement: Polars Data Generation
Example data generation scripts SHALL use Polars for dataframe creation and parquet writes instead of pandas.

#### Scenario: Replace pandas with polars
- **WHEN** running any Python data generation script under `examples/`
- **THEN** the script SHALL import and use `polars` (not `pandas`) for dataframe operations and parquet output.
- **AND** required dependencies/documentation SHALL instruct users to install `polars` for these scripts.

### Requirement: Partitioned Output Option
Large or time-based example datasets SHALL support writing partitioned parquet outputs to improve scalability.

#### Scenario: Partition flag available
- **WHEN** generating datasets with a provided CLI/flag (e.g., `--partitioned`)
- **THEN** the script SHALL be able to write parquet data partitioned by an appropriate column (e.g., date/year/month) into a directory of files.
- **AND** the script SHALL keep or document a single-file output for backward compatibility unless a `--partitioned-only` option is chosen.

### Requirement: Hive Partition Format
Partitioned outputs SHALL use Hive-style directory structures and partitioning logic for compatibility with downstream readers.

#### Scenario: Hive-format directories
- **WHEN** a generator is invoked with `--partitioned` or `--partitioned-only`
- **THEN** the script SHALL write the partitioned dataset using `pyarrow.dataset.partitioning(..., flavor="hive")`
- **AND** each partition directory SHALL follow the `<column>=<value>` naming convention supported by Hive/partitioned readers.

### Requirement: Backward-Compatible Paths
Transition to polars SHALL preserve existing file paths so current configs and validation scripts continue to run.

#### Scenario: Existing paths remain valid
- **WHEN** users run the updated generators without partitioned-only options
- **THEN** the same parquet file paths (e.g., `data/orders.parquet`, `datasets/events_small.parquet`) SHALL be produced.
- **AND** any new partitioned outputs SHALL be placed alongside in clearly named directories (e.g., `orders_partitioned/`).

