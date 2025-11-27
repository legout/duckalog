## ADDED Requirements

### Requirement: Remote catalog output
The system SHALL support writing the built DuckDB catalog to remote destinations using a filesystem abstraction (e.g., fsspec/obstore) so multiple backends can be supported.

#### Scenario: S3 output URI
- **WHEN** a user runs catalog build with `--output s3://bucket/path/catalog.duckdb`
- **THEN** the system SHALL build the catalog and upload the resulting DuckDB file to that S3 URI
- **AND** authentication SHALL follow AWS-standard resolution (env/profile/IAM); embedding secrets in the URI is rejected
- **AND** upload failures SHALL surface clear, actionable errors.

#### Scenario: Other fsspec-compatible output URI
- **WHEN** a user runs catalog build with a supported remote URI such as `gcs://bucket/path/catalog.duckdb`, `abfs://container/path/catalog.duckdb`, `sftp://host/path/catalog.duckdb`, or a read-only github/https destination if supported
- **THEN** the system SHALL attempt upload via the configured filesystem abstraction
- **AND** apply that backend’s standard auth resolution (e.g., gcloud/ADC for gcs, shared key/token for adlfs, ssh key/password for sftp)
- **AND** unsupported schemes SHALL fail fast with a clear message.

#### Scenario: Local default remains unchanged
- **WHEN** no remote URI is provided
- **THEN** the catalog SHALL continue to be written to the local path exactly as today.

### Requirement: Optional dependencies and clear errors (remote output)
Remote output SHALL not break local-only users.

#### Scenario: Missing remote deps for output
- **WHEN** a remote output URI is used but the required client library/extra (e.g., fsspec with the right extra, obstore, cloud SDK) is not installed
- **THEN** the system SHALL emit a clear error instructing how to install the appropriate optional extra and fail gracefully.

### Requirement: CLI parity (remote output)
The CLI SHALL accept remote output URIs anywhere a catalog output path is allowed.

#### Scenario: CLI remote output
- **WHEN** running `duckalog build ... --output s3://bucket/path/catalog.duckdb`
- **THEN** the command SHALL behave the same as with local output, producing the uploaded file on success.
