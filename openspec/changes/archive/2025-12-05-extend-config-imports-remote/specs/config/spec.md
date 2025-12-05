## ADDED Requirements

### Requirement: Remote Config Imports
Duckalog configuration imports MUST support remote URIs in addition to local file paths, reusing the existing remote configuration loading mechanisms.

#### Scenario: Import config from remote URI
- **GIVEN** a configuration file with an `imports` entry that references a remote URI such as:
  ```yaml
  imports:
    - s3://my-bucket/shared/settings.yaml
  ```
- **WHEN** the configuration is loaded
- **THEN** the remote file SHALL be fetched using the same infrastructure as remote config loading
- **AND** its contents SHALL be parsed and merged into the main configuration using the standard deep-merge rules.

#### Scenario: Mixed local and remote imports
- **GIVEN** a configuration file that includes both local and remote paths in `imports`
- **WHEN** the configuration is loaded
- **THEN** all imported configs SHALL be merged into a single configuration according to the same merge and uniqueness rules defined for local imports
- **AND** the order of imports (local vs remote) SHALL determine last-wins behavior for scalar values.

#### Scenario: Remote import failure reporting
- **GIVEN** a configuration file with an `imports` entry that references a remote URI which cannot be fetched or parsed
- **WHEN** the configuration is loaded
- **THEN** loading SHALL fail with a configuration error that includes the failing URI and a short description of the failure
- **AND** the underlying error SHALL be preserved via exception chaining.
