## MODIFIED Requirements
### Requirement: CLI API Integration
The CLI SHALL use the refactored internal APIs while maintaining identical command-line interface and behavior.

#### Scenario: CLI commands work unchanged
- **WHEN** user runs `duckalog build config.yaml`
- **THEN** command executes identically to before refactoring
- **AND** all CLI options and flags work the same
- **AND** output format unchanged

#### Scenario: CLI uses new internal structure
- **WHEN** CLI code imports internal modules
- **THEN** imports use new organized structure
- **AND** no circular dependencies introduced
- **AND** CLI maintainability improved

## ADDED Requirements
### Requirement: CLI Import Consistency
The CLI SHALL import from the new API structure to demonstrate best practices and ensure consistency.

#### Scenario: CLI imports match public API patterns
- **WHEN** CLI needs to load configuration
- **THEN** uses same import patterns as public API
- **AND** serves as example for users
- **AND** reduces maintenance burden

#### Scenario: No CLI-specific code paths
- **WHEN** CLI and Python API need same functionality
- **THEN** both use identical underlying code
- **AND** no duplication between CLI and library code
- **AND** changes benefit both interfaces
