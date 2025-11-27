## ADDED Requirements
### Requirement: Build and attach nested Duckalog configs
The catalog build process SHALL build any child Duckalog configs declared under `attachments.duckalog` before creating attachments on the parent connection, then ATTACH the resulting DuckDB catalog using the configured alias and read-only flag.

#### Scenario: Child catalog built then attached
- **GIVEN** a parent config `catalog.yaml` with `attachments.duckalog` pointing to `./child.yaml` and alias `ref_data`
- **AND** `child.yaml` defines `duckdb.database: "artifacts/ref.duckdb"` and its own views
- **WHEN** `build_catalog("catalog.yaml")` runs
- **THEN** the system builds `child.yaml` first, producing `artifacts/ref.duckdb`
- **AND** attaches that database as `ref_data` on the parent connection before creating parent views.

#### Scenario: Attachment reuse within a run
- **GIVEN** multiple entries reference the same resolved child config path
- **WHEN** `build_catalog` executes
- **THEN** the child config is built only once for the run
- **AND** its resulting database path is reused for each alias attachment.

#### Scenario: Cyclic attachment graph rejected
- **GIVEN** configs A and B that reference each other via `attachments.duckalog`
- **WHEN** `build_catalog` is invoked on A
- **THEN** the system detects the cycle during traversal
- **AND** fails with a clear cycle error before executing any attachment SQL.

#### Scenario: Dry-run skips child builds
- **GIVEN** `build_catalog(config_path, dry_run=True)`
- **WHEN** the config includes `attachments.duckalog`
- **THEN** child configs are parsed and validated to ensure paths and databases are resolvable
- **AND** no child catalog build or ATTACH statements are executed.
