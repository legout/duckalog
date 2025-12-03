## ADDED Requirements

### Requirement: Shared CLI Filesystem Options
Filesystem‑related CLI options MUST be defined once and reused across all commands that accept a config path, so that behavior and help text remain consistent.

#### Scenario: Build, generate-sql, and validate share filesystem options
- **GIVEN** the `build`, `generate-sql`, and `validate` CLI commands
- **WHEN** a user passes filesystem options (such as protocol, credentials, or endpoints)
- **THEN** each command accepts the same set of filesystem‑related flags with the same defaults and help text
- **AND** those flags are parsed by a shared implementation that constructs the filesystem object used during config loading.

