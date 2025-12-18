## MODIFIED Requirements
### Requirement: Configuration Loading API
The system SHALL provide a unified configuration loading API that eliminates duplication between config.py and config/ package, while maintaining backwards compatibility through deprecation warnings.

#### Scenario: Direct config package imports work
- **WHEN** user imports `from duckalog.config import load_config`
- **THEN** import succeeds without deprecation warning
- **AND** functionality remains identical

#### Scenario: Legacy config.py imports show deprecation
- **WHEN** user imports `from duckalog import load_config` (via config.py re-export)
- **THEN** import succeeds with deprecation warning
- **AND** warning guides to new import path
- **AND** functionality remains identical

#### Scenario: Config models accessible from single location
- **WHEN** user needs Config, ViewConfig, etc.
- **THEN** all models available from `duckalog.config` package
- **AND** no duplication between config.py and config/ package

## ADDED Requirements
### Requirement: Configuration API Deprecation Strategy
The system SHALL provide clear migration guidance for deprecated configuration imports with a minimum 2-release deprecation period.

#### Scenario: Deprecation warnings include migration guide
- **WHEN** deprecated import is used
- **THEN** warning includes specific new import path
- **AND** warning links to migration documentation
- **AND** warning can be suppressed for gradual migration

#### Scenario: Backwards compatibility maintained
- **WHEN** deprecated imports are used
- **THEN** all existing functionality works unchanged
- **AND** no breaking changes in minor versions
