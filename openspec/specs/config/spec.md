# config Specification

## Purpose
TBD - created by archiving change add-config-schema. Update Purpose after archive.
## Requirements
### Requirement: Catalog Config Format
The catalog configuration MUST support the existing required keys and MAY include an optional top-level `semantic_models` section in addition to them.

#### Scenario: Optional semantic_models section
- **GIVEN** a YAML or JSON config with top-level keys `version`, `duckdb`, `views`, and an optional `semantic_models` array
- **WHEN** the configuration is loaded
- **THEN** it is parsed successfully into the `Config` model
- **AND** the `semantic_models` section is available as a typed collection when present
- **AND** configs that omit `semantic_models` remain valid with no behavioural change to catalog builds.

### Requirement: Environment Variable Interpolation
The system MUST support `${env:VAR_NAME}` placeholders in any string value and resolve them from the process environment, failing fast when required variables are missing.

#### Scenario: Placeholder is resolved from environment
- **GIVEN** `AWS_ACCESS_KEY_ID` is set in the environment
- **AND** a config pragma value is `\"SET s3_access_key_id='${env:AWS_ACCESS_KEY_ID}'\"`
- **WHEN** the configuration is loaded
- **THEN** the placeholder is replaced with the value of `AWS_ACCESS_KEY_ID`
- **AND** the resulting `Config` instance contains the interpolated value.

#### Scenario: Missing environment variable causes error
- **GIVEN** `AWS_SECRET_ACCESS_KEY` is NOT set in the environment
- **AND** a config pragma value is `"SET s3_secret_access_key='${env:AWS_SECRET_ACCESS_KEY}'"`
- **WHEN** the configuration is loaded
- **THEN** configuration loading fails
- **AND** a `ConfigError` (inheriting from `DuckalogError`) is raised indicating the missing environment variable.

### Requirement: View Definitions and Sources
Each view definition MUST have a unique `name` and EITHER a `sql` field OR a `source` field with the required attributes for that source type.

#### Scenario: Raw SQL view
- **GIVEN** a view with `name: vip_users` and a non-empty `sql` string
- **AND** the view does not specify `source`, `uri`, `database`, `table`, or `catalog`
- **WHEN** the configuration is validated
- **THEN** the view is accepted as a raw SQL view.

#### Scenario: Parquet view with required uri
- **GIVEN** a view with `source: parquet` and a non-empty `uri`
- **WHEN** the configuration is validated
- **THEN** the view is accepted
- **AND** the `uri` value is required and cannot be empty.

#### Scenario: Iceberg view with either uri or catalog+table
- **GIVEN** a view with `source: iceberg`
- **AND** either a non-empty `uri`
- **OR** both `catalog` and `table` set
- **WHEN** the configuration is validated
- **THEN** the view is accepted
- **AND** configurations that mix `uri` with `catalog` or `table`, or omit both, are rejected.

#### Scenario: Attached database view requires database and table
- **GIVEN** a view with `source` set to `duckdb`, `sqlite`, or `postgres`
- **AND** both `database` (attachment alias) and `table` are provided
- **WHEN** the configuration is validated
- **THEN** the view is accepted
- **AND** configurations missing either `database` or `table` for these sources are rejected.

### Requirement: Attachments and Iceberg Catalogs
Attachments and Iceberg catalogs MUST follow the shapes defined by their configuration models and MUST be validated before any catalog build.

#### Scenario: DuckDB and SQLite attachments validated
- **GIVEN** `attachments.duckdb[]` entries with `alias`, `path`, and optional `read_only`
- **AND** `attachments.sqlite[]` entries with `alias` and `path`
- **WHEN** the configuration is validated
- **THEN** entries missing required fields are rejected with clear validation errors.

#### Scenario: Postgres attachments validated
- **GIVEN** `attachments.postgres[]` entries with `alias`, `host`, `port`, `database`, `user`, and `password`
- **WHEN** the configuration is validated
- **THEN** entries missing any required field are rejected with clear validation errors.

#### Scenario: Iceberg catalog definitions validated
- **GIVEN** `iceberg_catalogs[]` entries each with a `name`, `catalog_type`, and optional `uri`, `warehouse`, and `options`
- **WHEN** the configuration is validated
- **THEN** entries missing `name` or `catalog_type` are rejected
- **AND** invalid field types (e.g. non-object `options`) are rejected.

### Requirement: DuckDB Secrets Configuration
The system SHALL allow users to define DuckDB secrets in the catalog configuration file for accessing external services and databases using a unified `SecretConfig` model.

#### Scenario: SecretConfig unified model
- **WHEN** a user provides secret configurations using the `SecretConfig` model
- **THEN** the system SHALL use a single canonical model that supports all secret types (s3, azure, gcs, http, postgres, mysql)
- **AND** the `SecretConfig.type` field SHALL discriminate between different backend types
- **AND** backend-specific helper models SHALL be internal implementation details only

#### Scenario: S3 secret with CONFIG provider
- **WHEN** a user provides an S3 secret configuration with `type: s3`, `key_id`, `secret`, and optional `region`, `endpoint`
- **THEN** the system SHALL execute `CREATE SECRET` with the mapped parameters (KEY_ID, SECRET, REGION, ENDPOINT)

#### Scenario: Persistent secret with scope
- **WHEN** a user provides a persistent secret with `persistent: true` and optional `scope`
- **THEN** the system SHALL execute `CREATE PERSISTENT SECRET ... SCOPE 'prefix'` to create a scoped persistent secret

#### Scenario: Multiple secrets for same service type
- **WHEN** a user defines multiple S3 secrets with different scopes
- **THEN** the system SHALL create all secrets and allow DuckDB to automatically select the appropriate one based on path matching

#### Scenario: Secret with credential_chain provider
- **WHEN** a user provides a secret using `provider: credential_chain`
- **THEN** the system SHALL execute `CREATE SECRET ... PROVIDER credential_chain` to let DuckDB auto-fetch credentials

#### Scenario: Azure secret configuration with client credentials
- **WHEN** a user provides an Azure secret with `type: azure`, `tenant_id`, `client_id`, and `client_secret`
- **THEN** the system SHALL create the Azure secret type with the specified parameters (TENANT_ID, CLIENT_ID, SECRET)

#### Scenario: Azure secret configuration with connection string
- **WHEN** a user provides an Azure secret with `type: azure` and `connection_string`
- **THEN** the system SHALL create the Azure secret type using CONNECTION_STRING parameter

#### Scenario: Database secret for PostgreSQL with individual parameters
- **WHEN** a user provides a PostgreSQL secret with `type: postgres`, `host`, `database`, `user`, and `password`
- **THEN** the system SHALL create a postgres secret type with mapped parameters (HOST, DATABASE, USER, PASSWORD)

#### Scenario: Database secret with connection string
- **WHEN** a user provides a database secret with `connection_string` instead of individual parameters
- **THEN** the system SHALL use the CONNECTION_STRING parameter for the secret

#### Scenario: HTTP secret with bearer token
- **WHEN** a user provides an HTTP secret with `type: http` and `bearer_token`
- **THEN** the system SHALL create an http secret type with BEARER_TOKEN parameter

#### Scenario: HTTP secret with basic authentication
- **WHEN** a user provides an HTTP secret with `type: http`, `key_id` (username), and `secret` (password)
- **THEN** the system SHALL create an http secret type with USERNAME and PASSWORD parameters

#### Scenario: GCS secret with service account key
- **WHEN** a user provides a GCS secret with `type: gcs` and `service_account_key`
- **THEN** the system SHALL create a GCS secret type with SERVICE_ACCOUNT_KEY parameter

#### Scenario: Secret validation
- **WHEN** a user provides an invalid secret configuration (missing required fields for type)
- **THEN** the system SHALL raise a validation error during config loading

#### Scenario: Empty secrets configuration
- **WHEN** a user does not provide secrets or provides an empty list
- **THEN** the system SHALL continue without error and create no secrets

#### Scenario: Secrets with environment variables
- **WHEN** a user provides secret values using `${env:VAR_NAME}` syntax
- **THEN** the system SHALL interpolate environment variables before creating the secret

### Requirement: DuckDB Settings Configuration
The system SHALL allow users to define DuckDB session settings in the catalog configuration file.

#### Scenario: Single setting as string
- **WHEN** a user provides `duckdb.settings: "threads = 32"` in YAML config
- **THEN** the system SHALL execute `SET threads = 32` after applying pragmas

#### Scenario: Multiple settings as list
- **WHEN** a user provides `duckdb.settings: ["threads = 32", "memory_limit = '1GB'"]` in config
- **THEN** the system SHALL execute each SET statement in order after applying pragmas

#### Scenario: Settings with environment variables
- **WHEN** a user provides `duckdb.settings: "threads = ${env:THREAD_COUNT}"` in config
- **THEN** the system SHALL interpolate the environment variable before executing the SET statement

#### Scenario: Settings validation
- **WHEN** a user provides invalid settings syntax
- **THEN** the system SHALL raise a validation error during config loading

#### Scenario: Empty settings
- **WHEN** a user does not provide settings or provides an empty value
- **THEN** the system SHALL continue without error and apply no additional settings

### Requirement: Semantic Models Configuration
The system SHALL allow users to define optional semantic models that provide business-friendly metadata on top of existing views.

#### Scenario: Semantic model with dimensions and measures
- **WHEN** a user provides a `semantic_models` section with models containing `name`, `base_view`, `dimensions`, and `measures`
- **THEN** the system SHALL validate that each semantic model has a unique name
- **AND** the system SHALL validate that each `base_view` references an existing view in the `views` section
- **AND** the system SHALL validate that dimension and measure names are unique within each model

#### Scenario: Semantic model validation errors
- **WHEN** a user provides a semantic model with a duplicate name
- **THEN** the system SHALL raise a validation error indicating the duplicate semantic model name
- **WHEN** a user provides a semantic model with a `base_view` that doesn't exist
- **THEN** the system SHALL raise a validation error indicating the missing base view
- **WHEN** a user provides dimensions or measures with duplicate names within the same model
- **THEN** the system SHALL raise a validation error indicating the duplicate dimension/measure name

#### Scenario: Empty semantic models
- **WHEN** a user does not provide semantic models or provides an empty list
- **THEN** the system SHALL continue without error and no semantic models are available

#### Scenario: Semantic model metadata
- **WHEN** a user provides optional metadata like `label`, `description`, or `tags` on semantic models, dimensions, or measures
- **THEN** the system SHALL accept and preserve this metadata without validation beyond basic type checking

### Requirement: Duckalog config attachments
Duckalog configurations SHALL support attaching other Duckalog configs via `attachments.duckalog[]`, each entry providing an `alias`, a `config_path` to the child config file, an optional `database` override for the child catalog file, and an optional `read_only` flag that defaults to `true`.

#### Scenario: Valid nested config attachment accepted
- **GIVEN** a config with `attachments.duckalog` containing an entry with `alias: ref_data` and `config_path: ./ref/catalog.yaml`
- **AND** the referenced child config defines a `duckdb.database` file path (or the attachment supplies `database`)
- **WHEN** the configuration is loaded and validated
- **THEN** the attachment entry is accepted
- **AND** `read_only` defaults to `true` when omitted.

#### Scenario: Relative paths resolved for nested configs
- **GIVEN** a parent config located at `/projects/main/catalog.yaml`
- **AND** it declares `attachments.duckalog[0].config_path: "../shared/ref.yaml"` and `database: "./data/ref.duckdb"`
- **WHEN** the configuration is loaded
- **THEN** `config_path` resolves to `/projects/shared/ref.yaml`
- **AND** `database` resolves to `/projects/main/data/ref.duckdb`.

#### Scenario: Missing path or in-memory child rejected
- **GIVEN** a `attachments.duckalog` entry missing `alias` or `config_path`, **OR** referencing a child config whose effective database is `:memory:` without a `database` override
- **WHEN** the configuration is validated
- **THEN** validation fails with a clear error describing the missing field or requirement for a durable database path.

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

### Requirement: Config Loading API Contract
The system SHALL provide clear, documented responsibilities for config loading functions with predictable dispatch behavior and filesystem abstraction support.

#### Scenario: Public API entrypoint
- **GIVEN** a user calls `load_config(path_or_uri, *, filesystem=None, ...)` with either a local path or remote URI
- **WHEN** the function is invoked
- **THEN** it SHALL determine whether `path_or_uri` is local or remote based on URI scheme detection
- **AND** it SHALL delegate to the appropriate internal helper:
  - `_load_config_from_local_file` for local paths (no scheme detected)
  - `load_config_from_uri` for remote URIs (scheme like `s3://`, `http://`, etc. detected)

#### Scenario: Local file loading helper
- **GIVEN** `_load_config_from_local_file(path, *, filesystem=None, ...)` is called with a local file path
- **WHEN** the function executes
- **THEN** it SHALL be responsible for:
  - Path resolution and validation per security requirements
  - Reading YAML/JSON content from local disk or provided `filesystem` object
  - Environment variable interpolation
  - Pydantic model validation
- **AND** if `filesystem` is provided, it SHALL use filesystem-based I/O instead of direct file access
- **AND** if `filesystem` is `None`, it SHALL use default path-based file I/O

#### Scenario: Remote URI loading helper
- **GIVEN** `load_config_from_uri(uri, *, filesystem, ...)` is called with a remote URI
- **WHEN** the function executes
- **THEN** it SHALL be responsible for:
  - URI scheme validation and parsing
  - Remote content fetching using the provided `filesystem` or appropriate default
  - Content validation and parsing (YAML/JSON)
  - Environment variable interpolation and path resolution
  - Pydantic model validation
- **AND** it SHALL require a suitable `filesystem` object for protocols that need it
- **AND** it SHALL be exported from `duckalog.config` for direct testing and patching

#### Scenario: URI scheme detection
- **GIVEN** any path or URI string
- **WHEN** determining whether to use local or remote loading
- **THEN** the system SHALL consider it a remote URI if it matches a `<scheme>://` pattern
- **AND** common schemes SHALL include `s3://`, `http://`, `https://`, `gcs://`, `abfs://`, `sftp://`, and other fsspec-compatible protocols
- **AND** strings without schemes SHALL be treated as local file paths

#### Scenario: Filesystem interface requirements
- **GIVEN** a `filesystem` object passed to any config loading function
- **WHEN** the filesystem is used for I/O operations
- **THEN** it SHALL provide an fsspec-compatible interface with at minimum:
  - `open(path, mode='r')` method for reading file contents
  - `exists(path)` method for checking file existence
- **AND** for remote protocols, it SHALL understand the appropriate scheme and authentication methods
- **AND** if the filesystem object lacks required methods, the function SHALL raise a clear error describing the missing interface

#### Scenario: Filesystem parameter handling
- **GIVEN** local file loading with `filesystem=None`
- **WHEN** `_load_config_from_local_file` is called
- **THEN** it SHALL use standard Python file I/O (`open()`, `os.path.exists()`, etc.)
- **GIVEN** local file loading with a provided `filesystem` object
- **WHEN** `_load_config_from_local_file` is called
- **THEN** it SHALL use the filesystem's methods instead of direct file I/O
- **GIVEN** remote URI loading
- **WHEN** `load_config_from_uri` is called
- **THEN** it SHALL require an appropriate filesystem for the protocol or use sensible defaults where possible

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

### Requirement: Path Resolution Security
The system MUST enforce strict path security boundaries to prevent unauthorized file system access through path traversal attacks.

#### Scenario: Allowed roots model
- **GIVEN** a configuration file located at `/project/config/catalog.yaml`
- **WHEN** paths in the configuration are resolved to absolute paths
- **THEN** all resolved local file paths MUST be within the allowed roots
- **AND** the default allowed root set SHALL include the configuration directory (`/project/config/`)
- **AND** any resolved path outside these roots SHALL cause a configuration error

#### Scenario: Root-based path validation
- **GIVEN** a relative path `"../data/file.parquet"` in a configuration
- **WHEN** the path is resolved to `/project/data/file.parquet`
- **THEN** if `/project/data/` is under the configuration directory, the path SHALL be allowed
- **AND** if `/project/data/` is outside the configuration directory, the path SHALL be rejected
- **AND** the validation SHALL use `Path.resolve()` and `os.path.commonpath` for robust cross-platform checking

#### Scenario: Path traversal prevention
- **GIVEN** malicious paths attempting to escape the configuration directory
- **WHEN** paths like `"../../../etc/passwd"` or `"..\\..\\..\\windows\\system32\\config\\sam"` are resolved
- **THEN** the system SHALL reject these paths with a clear security error
- **AND** the error SHALL indicate the original path, resolved path, and allowed roots
- **AND** the system SHALL NOT attempt to "fix up" or modify the path to make it valid

#### Scenario: Cross-platform path handling
- **GIVEN** different path formats across Unix and Windows systems
- **WHEN** paths with mixed separators (`/` vs `\`), drive letters (`C:\\`), or UNC paths (`\\\\server\\share`) are processed
- **THEN** the root validation SHALL handle all these formats correctly
- **AND** Windows drive letter differences SHALL be treated as separate root contexts
- **AND** invalid or undecodable paths SHALL be rejected with descriptive errors

#### Scenario: Symlink resolution
- **GIVEN** file system paths that involve symbolic links
- **WHEN** paths are resolved using `Path.resolve()` which follows symlinks
- **THEN** the security check SHALL validate the final resolved path, not the intermediate path
- **AND** symlinks that point outside allowed roots SHALL be blocked

### Requirement: Safe Secret Configuration
Secret configurations MUST enforce strict typing for options and use safe SQL quoting for all string values.

#### Scenario: Secret options type enforcement
- **GIVEN** a DuckDB secret configuration with `options` field
- **WHEN** the options contain values of types `bool`, `int`, `float`, or `str`
- **THEN** the secret configuration SHALL be accepted and the values SHALL be rendered according to their type
- **AND** boolean values SHALL be rendered as `TRUE` or `FALSE` without quotes
- **AND** numeric values SHALL be rendered as-is without quotes
- **AND** string values SHALL be rendered using safe SQL literal quoting

#### Scenario: Secret options type rejection
- **GIVEN** a DuckDB secret configuration with `options` field containing unsupported types
- **WHEN** the configuration is validated or SQL is generated
- **THEN** the system SHALL raise a `TypeError` with a clear message indicating the unsupported option type
- **AND** the error message SHALL include the option key and the actual type that was rejected
- **AND** the system SHALL NOT attempt to interpolate an unsafe string representation

#### Scenario: Secret name and scope validation
- **GIVEN** a DuckDB secret configuration with `name` or `scope` fields
- **WHEN** SQL is generated for secret creation
- **THEN** these fields SHALL be treated as identifiers and passed through proper identifier quoting
- **AND** the system SHALL NOT allow untrusted input to bypass identifier quoting in these contexts

#### Scenario: Secret string field quoting
- **GIVEN** a DuckDB secret configuration with string fields (e.g., `key_id`, `secret`, `connection_string`, `host`, `database`, `user`, `password`, `scope`, `endpoint`, `region`)
- **WHEN** `CREATE SECRET` SQL statements are generated
- **THEN** all string values SHALL be emitted using safe SQL literal quoting that doubles embedded single quotes

### Requirement: Stable Config Module Public API
The `duckalog.config` module MUST provide a stable public API for configuration models and helpers, regardless of its internal file layout.

#### Scenario: Public config API remains stable across refactors
- **GIVEN** user code that imports `Config`, `SecretConfig`, and `load_config` from `duckalog.config`
- **WHEN** the internal implementation of the config layer is refactored into multiple modules or packages
- **THEN** those imports continue to work without modification
- **AND** the behavior of loading and validating configs remains consistent with the config specification.

### Implementation Structure
The configuration layer is implemented as a structured internal package under `duckalog.config` to improve maintainability while preserving the public API contract.

#### Package Layout
The `duckalog.config` package contains the following modules:

- **`models.py`**: Pydantic model definitions and schema validation (Config, SecretConfig, ViewConfig, etc.)
- **`loader.py`**: Configuration loading orchestration (`load_config`, `_load_config_from_local_file`, remote loading dispatch)
- **`interpolation.py`**: Environment variable interpolation logic (`${env:VAR}` placeholder resolution)
- **`validators.py`**: Complex validation helper functions and cross-field validation logic
- **`sql_integration.py`**: SQL file loading and path resolution integration
- **`__init__.py`**: Public API re-exports to maintain backward compatibility

#### Responsibilities and Dependencies
- **`models.py`** serves as the foundation and MUST NOT import from other config modules to prevent circular dependencies
- **`loader.py`** orchestrates the loading process and imports utilities from `interpolation.py`, `validators.py`, and `sql_integration.py`
- **`interpolation.py`**, **`validators.py`**, and **`sql_integration.py`** contain supporting logic and import models from `models.py` only
- **`__init__.py`** provides the public API surface by re-exporting all symbols that were previously available from the monolithic `config.py`

#### External API Compatibility
The public import surface remains unchanged:
- `from duckalog.config import Config, load_config, SecretConfig` continues to work
- `from duckalog import config` with subsequent `config.Config` access continues to work
- All existing configuration behaviors and validation rules remain identical

### Security Regression Tests

The system MUST maintain a comprehensive suite of regression tests to prevent security vulnerabilities from being re-introduced during future development and refactoring.

#### Requirement: SQL Injection Resilience Tests
SQL generation MUST be resilient to malicious input designed to inject additional SQL statements or alter the structure of generated queries.

##### Scenario: View identifier injection attempts
- **GIVEN** view configurations with names, databases, or tables containing quotes (`"`, `'`), semicolons (`;`), SQL comment markers (`--`, `/* */`), or SQL keywords
- **WHEN** `generate_view_sql()` and `generate_all_views_sql()` are called
- **THEN** the generated SQL SHALL remain syntactically valid
- **AND** malicious content SHALL remain safely contained within properly quoted identifiers
- **AND** no additional SQL statements SHALL be injected via these fields

##### Scenario: Secret SQL injection prevention
- **GIVEN** secret configurations with values containing quotes, backslashes, and other special characters
- **WHEN** `generate_secret_sql()` is called
- **THEN** all string values SHALL be properly quoted as SQL literals
- **AND** embedded quotes SHALL be doubled to prevent injection
- **AND** the generated CREATE SECRET statements SHALL be syntactically valid

##### Scenario: Secret option type enforcement
- **GIVEN** secret configurations with options containing unsupported value types (e.g., lists, dictionaries, objects)
- **WHEN** `generate_secret_sql()` is called
- **THEN** the system SHALL raise a `TypeError` with a clear message
- **AND** the error message SHALL include the problematic option key and the rejected type
- **AND** the system SHALL NOT interpolate an unsafe string representation

#### Requirement: Path Traversal Protection Tests
Path resolution MUST prevent unauthorized file system access through path traversal attacks and validate paths against security boundaries.

##### Scenario: Valid path acceptance
- **GIVEN** relative paths that resolve within the configuration directory or other allowed roots
- **WHEN** path resolution functions are called during config loading
- **THEN** these paths SHALL be accepted and normalized correctly
- **AND** no security errors SHALL be raised for legitimate paths

##### Scenario: Path traversal rejection
- **GIVEN** relative paths that attempt to escape allowed roots using `..` segments or platform-specific traversal patterns
- **WHEN** path resolution functions are called during config loading
- **THEN** these paths SHALL cause configuration errors
- **AND** the error messages SHALL be informative and indicate the problematic path
- **AND** the system SHALL NOT perform unauthorized file system access

##### Scenario: Cross-platform path security
- **GIVEN** different path formats across Unix and Windows systems (mixed separators, drive letters, UNC paths)
- **WHEN** path security validation is performed
- **THEN** the security checks SHALL handle all supported path formats correctly
- **AND** platform-specific traversal attempts SHALL be detected and rejected

