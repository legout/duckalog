## ADDED Requirements

### Requirement: Advanced Config Import Options
Config imports MUST support advanced options on top of the core imports feature, including selective imports, override behavior, and pattern-based file selection, when those options are configured.

#### Scenario: Section-specific imports
- **GIVEN** a configuration that uses section-specific imports to pull additional view definitions and DuckDB settings from separate files
- **WHEN** the configuration is loaded
- **THEN** the imported view definitions SHALL be merged only into the `views` section
- **AND** the imported DuckDB settings SHALL be merged only into the `duckdb` section
- **AND** sections not referenced by selective imports SHALL remain unaffected.

#### Scenario: Import override behavior
- **GIVEN** an import entry that is marked with an override flag (for example, `override: false`)
- **WHEN** the configuration is loaded and merged
- **THEN** values from that import SHALL fill in missing fields but SHALL NOT overwrite existing values from earlier imports or the main file
- **AND** imports without an override flag SHALL continue to use the default last-wins behavior for scalar values.

#### Scenario: Glob and exclude patterns
- **GIVEN** an import configuration that uses glob patterns to include multiple files under a directory and exclude specific ones
- **WHEN** the configuration is loaded
- **THEN** the glob patterns SHALL be expanded into a deterministic list of files
- **AND** any files matching exclude patterns SHALL be omitted from that list
- **AND** the resolved files SHALL be processed as if they were listed explicitly in `imports`, preserving the established merge and uniqueness rules.
