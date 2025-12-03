## ADDED Requirements

### Requirement: Engine Orchestration Structure and Cleanup
The catalog build engine MUST orchestrate connection setup, attachments, secrets, views, and exports through a cohesive component that ensures proper resource cleanup even when errors occur.

#### Scenario: Catalog build uses structured orchestration
- **GIVEN** a valid catalog configuration
- **WHEN** `build_catalog` is invoked via the CLI or Python API
- **THEN** the engine creates and configures a DuckDB connection, sets up attachments and secrets, creates views, and performs any configured export as a single orchestrated operation
- **AND** temporary resources such as intermediate files are tracked for cleanup instead of being managed ad‑hoc in multiple locations.

#### Scenario: Resources cleaned up on failure
- **GIVEN** a configuration that triggers an error during catalog build (for example, invalid SQL or attachment failure)
- **WHEN** `build_catalog` runs and raises an engine error
- **THEN** the engine still closes any open connections and attempts to delete temporary files created during the run
- **AND** the system does not leave behind orphaned temporary database files.

