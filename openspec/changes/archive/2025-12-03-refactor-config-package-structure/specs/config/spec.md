## ADDED Requirements

### Requirement: Stable Config Module Public API
The `duckalog.config` module MUST provide a stable public API for configuration models and helpers, regardless of its internal file layout.

#### Scenario: Public config API remains stable across refactors
- **GIVEN** user code that imports `Config`, `SecretConfig`, and `load_config` from `duckalog.config`
- **WHEN** the internal implementation of the config layer is refactored into multiple modules or packages
- **THEN** those imports continue to work without modification
- **AND** the behavior of loading and validating configs remains consistent with the config specification.

