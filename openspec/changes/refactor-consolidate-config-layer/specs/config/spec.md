# Delta Spec: Config Module Consolidation

## MODIFIED Requirements

### Requirement: Path Resolution Functions
Path resolution utilities MUST be available as module-level functions in `config.py`.

#### Scenario: Path resolution from config module
- **GIVEN** a user imports path resolution functions
- **WHEN** they call `from duckalog.config import resolve_relative_path, is_relative_path`
- **THEN** the functions work identically to before
- **AND** they are implemented as private functions within config.py

#### Scenario: Security validation during path resolution
- **GIVEN** a config with relative paths
- **WHEN** `load_config()` is called
- **THEN** path security validation occurs
- **AND** dangerous paths (like `/etc/passwd`) are rejected

### Requirement: SQL File Loading
SQL file loading MUST be integrated into the config loading pipeline.

#### Scenario: SQL files loaded during config parsing
- **GIVEN** a config with sql_file references
- **WHEN** `load_config()` is called with `load_sql_files=True`
- **THEN** SQL content is loaded and merged into view configuration
- **AND** no separate SQLFileLoader object needed

#### Scenario: Template variable substitution
- **GIVEN** a SQL template file with `{{variable}}` placeholders
- **WHEN** config is loaded
- **THEN** variables are substituted from config data
- **AND** missing variables raise clear error

### Requirement: Logging Utilities
Simplified logging utilities MUST be available without external dependencies.

#### Scenario: Logging without loguru
- **GIVEN** a user uses duckalog logging functions
- **WHEN** messages are logged
- **THEN** redaction works correctly
- **AND** only stdlib logging is used (no loguru dependency)

