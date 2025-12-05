## ADDED Requirements

### Requirement: CLI Import Inspection
The Duckalog CLI MUST provide commands or options to inspect configuration imports without building a catalog.

#### Scenario: Show import graph
- **GIVEN** a catalog configuration that uses `imports` to pull in other files
- **WHEN** a user runs a CLI command such as `duckalog show-imports config.yaml`
- **THEN** the CLI SHALL display a tree or graph of imports starting from `config.yaml`
- **AND** the output SHALL include each imported file or URI at least once.

#### Scenario: Show merged configuration
- **GIVEN** a catalog configuration that uses imports
- **WHEN** a user runs a CLI command or option to preview the merged configuration
- **THEN** the CLI SHALL resolve all imports and output the resulting merged configuration or a clear summary of it
- **AND** the output SHALL reflect the same configuration that would be used by catalog build commands.
