## REMOVED Requirements
### Requirement: Redundant SQL Integration Wrapper
**Reason**: The `sql_integration.py` file provides no functionality beyond delegating to `loader.py`, creating unnecessary indirection and circular import confusion
**Migration**: Use `loader.py` directly for all SQL file loading functionality

#### Scenario: No SQL integration wrapper module
- **WHEN** SQL file loading is required during config processing
- **THEN** the system SHALL import directly from `config.loader._load_sql_files_from_config`
- **AND** no intermediate `sql_integration.py` module SHALL exist
- **AND** all SQL file loading behavior SHALL remain identical to current implementation

#### Scenario: Configuration loading unchanged
- **WHEN** configurations with SQL file references are loaded
- **THEN** the behavior SHALL be identical to current implementation
- **AND** all existing SQL loading features SHALL continue to work
- **AND** template processing SHALL remain unchanged
- **AND** path resolution SHALL work identically