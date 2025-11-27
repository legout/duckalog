## ADDED Requirements

### Requirement: Remote config loading
The system SHALL support loading Duckalog configs from remote URIs via a filesystem abstraction (e.g., fsspec/obstore).

#### Scenario: S3 config URI
- **WHEN** a user supplies a config path like `s3://bucket/path/catalog.yaml`
- **THEN** the loader SHALL fetch the object contents, validate as YAML/JSON, and apply the existing config schema.
- **AND** authentication SHALL follow AWS-standard resolution (env, profile, IAM); embedding secrets in the URI is rejected.

#### Scenario: Other fsspec-compatible config URI
- **WHEN** a user supplies a config URI such as `gcs://bucket/path/catalog.yaml`, `abfs://container/path/catalog.yaml` (adlfs), `sftp://host/path/catalog.yaml`, or a github/https read-only URL
- **THEN** the loader SHALL fetch the content via the appropriate filesystem backend
- **AND** use that backend’s standard auth resolution (e.g., ADC for GCS, Azure env/managed identity for ADLS, SSH auth for SFTP)
- **AND** unsupported schemes SHALL fail fast with a clear message.

#### Scenario: HTTPS config URI
- **WHEN** a user supplies an https URL to a YAML/JSON config
- **THEN** the loader SHALL download it with TLS verification enabled by default
- **AND** timeouts and HTTP errors SHALL surface clear messages.

### Requirement: Optional dependencies and clear errors
Remote loading SHALL not break local-only users.

#### Scenario: Missing remote deps
- **WHEN** a remote URI is used but the required client library (e.g., fsspec with needed extra, obstore, or requests for https) is not installed
- **THEN** the system SHALL emit a clear error instructing how to install the appropriate optional extra and fail gracefully.

### Requirement: CLI parity
The CLI SHALL accept remote config URIs anywhere a config path is currently allowed.

#### Scenario: CLI remote path
- **WHEN** running `duckalog build|validate|ui` with a remote URI
- **THEN** the command SHALL behave the same as with a local file, after fetching and validating the remote content.
