## MODIFIED Requirements
### Requirement: Environment Variable Interpolation
The system SHALL use a single implementation of environment variable interpolation from `config/interpolation.py` for all configuration processing.

#### Scenario: Interpolation uses single source
- **WHEN** configuration loading requires environment variable interpolation
- **THEN** the system SHALL import `_interpolate_env` from `config/interpolation.py`
- **AND** no duplicate implementations SHALL exist in other modules
- **AND** behavior SHALL remain identical to current implementation

#### Scenario: Interpolation function accessible from config package
- **WHEN** code needs to access interpolation functionality
- **THEN** `from duckalog.config.interpolation import _interpolate_env` SHALL work
- **AND** the function SHALL be available through the config package public API

### Requirement: Logging Functions Consolidation
The system SHALL use `duckalog/logging_utils.py` as the single source of truth for all logging functions used in configuration processing.

#### Scenario: Logging functions imported from single location
- **WHEN** config modules require logging functionality
- **THEN** they SHALL import `log_info`, `log_debug`, `log_error`, `get_logger` from `duckalog/logging_utils`
- **AND** duplicate logging implementations SHALL be removed from `config/validators.py`
- **AND** all logging behavior SHALL remain unchanged

#### Scenario: Logging redaction preserved
- **WHEN** sensitive data is logged through config processing
- **THEN** the redaction logic SHALL work identically to current implementation
- **AND** keywords like "password", "secret", "token" SHALL be redacted from logs

### Requirement: SQL File Loading Consolidation
The system SHALL consolidate SQL file loading logic into shared utilities used by both local and remote configuration loading.

#### Scenario: Shared SQL loading utilities
- **WHEN** SQL file loading is required during config processing
- **THEN** the system SHALL use shared utilities from `config/loader.py`
- **AND** both local and remote configs SHALL use the same loading logic
- **AND** `config/sql_integration.py` SHALL either use shared utilities or be removed as redundant

#### Scenario: SQL loading behavior unchanged
- **WHEN** configurations with SQL file references are loaded
- **THEN** the behavior SHALL be identical to current implementation
- **AND** all existing SQL loading features SHALL continue to work
- **AND** template processing SHALL remain unchanged

### Requirement: Path Resolution Consolidation
The system SHALL consolidate path resolution functions into a coherent module structure with clear responsibilities.

#### Scenario: Path functions consolidated
- **WHEN** path resolution is required during config processing
- **THEN** functions like `resolve_relative_path`, `_resolve_import_path` SHALL be consolidated
- **AND** path security validation SHALL remain intact
- **AND** all path resolution SHALL use consistent logic

#### Scenario: Path security boundaries maintained
- **WHEN** paths are resolved during configuration loading
- **THEN** the security validation SHALL prevent path traversal attacks
- **AND** allowed roots validation SHALL continue to work as specified
- **AND** cross-platform path handling SHALL be preserved

## REMOVED Requirements
### Requirement: Duplicate Implementation Elimination
**Reason**: Code duplication creates maintenance burden and potential for inconsistent behavior
**Migration**: Use consolidated implementations from single source modules
