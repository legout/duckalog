## ADDED Requirements

### Requirement: Config Loader Helper Functions and Dispatch
The configuration API MUST provide a clear contract for loading configs from local files and remote URIs via `load_config`, `_load_config_from_local_file`, and `load_config_from_uri`.

#### Scenario: load_config dispatches between local and remote loaders
- **GIVEN** a `path_or_uri` value passed to `load_config`
- **WHEN** `path_or_uri` is a local filesystem path
- **THEN** `load_config` delegates to an internal helper such as `_load_config_from_local_file` for reading and validating the configuration
- **AND** when `path_or_uri` is a remote URI (for example, starting with `\"s3://\"` or `\"https://\"`)
- **THEN** `load_config` delegates to `load_config_from_uri` instead.

#### Scenario: load_config_from_uri is publicly accessible and uses filesystem abstraction
- **GIVEN** a remote config URI and an appropriate filesystem or client
- **WHEN** `load_config_from_uri` is called directly or via `load_config`
- **THEN** it fetches the config contents using the provided filesystem abstraction
- **AND** applies the same environment interpolation, path resolution, and validation rules as local config loading
- **AND** is exposed from the `duckalog.config` module so that tests and advanced callers can patch or call it explicitly.

