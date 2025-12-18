## ADDED Requirements

### Requirement: CLI Run Command
The CLI MUST provide a `run` command that serves as the primary entry point for config-driven catalog management with smart connection handling.

#### Scenario: Run command handles existing catalogs
- **GIVEN** a valid config file path and an existing DuckDB catalog
- **WHEN** `duckalog run catalog.yaml` is executed
- **THEN** the command SHALL restore session state (settings, attachments, temporary secrets)
- **AND** SHALL apply incremental updates (missing views, temporary secrets)
- **AND** SHALL exit with status code `0` on success

#### Scenario: Run command handles new catalogs
- **GIVEN** a valid config file path and no existing catalog
- **WHEN** `duckalog run catalog.yaml` is executed
- **THEN** the command SHALL perform a full catalog build
- **AND** SHALL create the catalog with proper session state
- **AND** SHALL exit with status code `0` on success

#### Scenario: Run command with force rebuild
- **GIVEN** a valid config file path and an existing catalog
- **WHEN** `duckalog run catalog.yaml --force-rebuild` is executed
- **THEN** the command SHALL perform a full catalog rebuild
- **AND** SHALL recreate all views regardless of existing state
- **AND** SHALL exit with status code `0` on success

### Requirement: CLI Backward Compatibility
The existing `build` command MUST remain available for explicit full rebuild operations while users transition to the new workflow.

#### Scenario: Build command remains functional
- **GIVEN** a valid config file path
- **WHEN** `duckalog build catalog.yaml` is executed
- **THEN** the command SHALL perform a full catalog rebuild
- **AND** SHALL behave identically to the current implementation
- **AND** SHALL not show deprecation warnings

## MODIFIED Requirements

### Requirement: CLI Help and Documentation
The CLI help text and documentation MUST be updated to reflect the new primary workflow while maintaining clarity about available options.

#### Scenario: Help text shows new primary command
- **GIVEN** a user runs `duckalog --help`
- **WHEN** the help text is displayed
- **THEN** `run` SHALL be listed prominently as the primary command
- **AND** `build` SHALL be available for explicit rebuilds
- **AND** the help SHALL briefly explain the difference between the commands

#### Scenario: Run command help
- **GIVEN** a user runs `duckalog run --help`
- **WHEN** command-specific help is displayed
- **THEN** the help SHALL describe smart connection behavior
- **AND** SHALL document the `--force-rebuild` option
- **AND** SHALL provide clear guidance on when to use `run` vs `build`

### Requirement: Python API Enhancement
The Python API SHALL provide both the new connection function and maintain the existing build function with appropriate guidance.

#### Scenario: New connect function available
- **GIVEN** user code imports from `duckalog`
- **WHEN** `connect_to_catalog("config.yaml")` is called
- **THEN** the function SHALL return a connection to the catalog with proper session state
- **AND** SHALL handle both new and existing catalogs appropriately
- **AND** SHALL support the same options as the CLI `run` command

#### Scenario: Existing build function maintained
- **GIVEN** user code that calls `build_catalog("config.yaml")`
- **WHEN** the function is executed
- **THEN** it SHALL behave identically to the current implementation
- **AND** SHALL not emit deprecation warnings (preserving existing behavior)
- **AND** SHALL continue to be available for explicit rebuild needs