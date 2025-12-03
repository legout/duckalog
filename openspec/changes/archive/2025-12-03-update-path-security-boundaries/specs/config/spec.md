## ADDED Requirements

### Requirement: Path Security Boundaries for Local Files
Path resolution for local files MUST ensure that resolved paths remain within a defined set of allowed roots, and MUST reject configurations that attempt to escape those roots.

#### Scenario: Paths resolved within allowed roots
- **GIVEN** a config file located in a directory on the local filesystem
- **AND** view or attachment definitions that reference relative paths under that directory (for example, `\"data/users.parquet\"` or `\"./sql/views.sql\"`)
- **WHEN** the configuration is loaded and paths are resolved
- **THEN** the resolved absolute paths remain within the allowed roots (such as the config directory and any explicitly configured base directories)
- **AND** the configuration loads successfully.

#### Scenario: Paths escaping allowed roots are rejected
- **GIVEN** a config that references a path which resolves outside all allowed roots (for example, using `../` segments to reach system directories)
- **WHEN** the configuration is loaded and path resolution runs
- **THEN** the system raises a configuration or path‑resolution error
- **AND** does not attempt to access or use the resolved path.

