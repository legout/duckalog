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
Each view definition MUST have a unique identifier within the catalog and EITHER a `sql` field OR a `source` field with the required attributes for that source type.

#### Scenario: Raw SQL view (no schema)
- **GIVEN** a view with `name: vip_users` and a non-empty `sql` string
- **AND** the view does not specify `schema`, `source`, `uri`, `database`, `table`, or `catalog`
- **WHEN** the configuration is validated
- **THEN** the view is accepted as a raw SQL view
- **AND** its canonical identifier in DuckDB is the unqualified view name (for example, `vip_users`).

#### Scenario: Raw SQL view with schema
- **GIVEN** a view with `name: vip_users`, `schema: analytics`, and a non-empty `sql` string
- **WHEN** the configuration is validated
- **THEN** the view is accepted as a raw SQL view
- **AND** its canonical identifier in DuckDB is the schema-qualified name (for example, `analytics.vip_users`).

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

#### Scenario: View name and schema uniqueness
- **GIVEN** a catalog configuration with multiple view entries
- **WHEN** the configuration is validated
- **THEN** the combination of `schema` (if provided) and `name` MUST be unique within the catalog
- **AND** if two views share the same `name` and `schema` values, validation SHALL fail with a clear error indicating the duplicate.

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

### Requirement: Configuration Loading Process
The configuration loading process SHALL be enhanced to include .env file loading while maintaining existing behavior.

#### Scenario: Configuration loading flow
- **GIVEN** a configuration file path is provided to `load_config()`
- **WHEN** the configuration is loaded
- **THEN** the following steps occur in order:
  1. Discover and load .env files from directory hierarchy
  2. Add .env variables to os.environ
  3. Load and parse the configuration file (existing behavior)
  4. Apply environment variable interpolation (existing behavior)
  5. Validate and return the configuration (existing behavior)

#### Scenario: Error handling integration
- **GIVEN** configuration loading encounters errors at various stages
- **WHEN** errors occur
- **THEN** errors are handled according to existing patterns
- **AND** .env file errors do not prevent configuration loading unless critical
- **AND** appropriate error messages are provided to users

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
The configuration layer MUST be implemented as a structured internal package under `duckalog.config` to improve maintainability while preserving the public API contract.

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

### Requirement: Path Security Boundaries for Local Files
Path resolution for local files MUST ensure that resolved paths remain within a defined set of allowed roots, and MUST reject configurations that attempt to escape those roots.

#### Scenario: Paths resolved within allowed roots
- **GIVEN** a config file located in a directory on the local filesystem
- **AND** view or attachment definitions that reference relative paths under that directory (for example, `\"data/users.parquet\"` or `\"./sql/views.sql\"`)
- **WHEN** the configuration is loaded and paths are resolved
- **THEN** the resolved absolute paths remain within the allowed roots (such as the config directory and any explicitly configured base directories)
- **AND** the configuration loads successfully.

#### Scenario: Paths escaping allowed roots are rejected
- **GIVEN** a config that references a path which resolves outside all allowed roots (for example, using `../` segments to reach system directories)
- **WHEN** the configuration is loaded and path resolution runs
- **THEN** the system raises a configuration or path‑resolution error
- **AND** does not attempt to access or use the resolved path.

### Requirement: Canonical SecretConfig Model
Duckalog configuration MUST represent DuckDB secrets using a single canonical `SecretConfig` model that covers all supported secret types and maps directly to DuckDB `CREATE SECRET` parameters.

#### Scenario: Secrets configured via SecretConfig
- **GIVEN** a catalog configuration that defines one or more DuckDB secrets
- **WHEN** the configuration is loaded and validated
- **THEN** each secret is represented as a `SecretConfig` instance with a `type` discriminator (such as `\"s3\"`, `\"azure\"`, `\"gcs\"`, `\"http\"`, `\"postgres\"`, or `\"mysql\"`)
- **AND** only fields defined on `SecretConfig` are used to drive DuckDB `CREATE SECRET` statements, with no reliance on duplicated or backend‑specific config models.

#### Scenario: Secret options use supported primitive types
- **GIVEN** a `SecretConfig` with an `options` dictionary
- **WHEN** the configuration is validated and secret SQL is generated
- **THEN** option values of type `bool`, `int`, `float`, and `str` are accepted and rendered into SQL according to the SQL generation rules
- **AND** option values of any other type are rejected with a clear configuration or type error rather than being interpolated unsafely.

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

### Requirement: Import Syntax
The system MUST support an optional `imports` field at the top level of a configuration file that lists other configuration files to import and merge.

#### Scenario: Basic imports with relative paths
- **GIVEN** a configuration file `main.yaml` with:
  ```yaml
  imports:
    - ./settings.yaml
    - ./views/users.yaml
    - ./views/products.yaml
  
  duckdb:
    database: catalog.duckdb
  ```
- **AND** the imported files exist and contain valid configuration
- **WHEN** the configuration is loaded
- **THEN** all imported files are loaded and their contents are merged into the main configuration
- **AND** relative paths are resolved relative to the importing file's directory
- **AND** the resulting configuration contains all sections from all imported files

#### Scenario: Imports with environment variables
- **GIVEN** a configuration file with:
  ```yaml
  imports:
    - ./secrets/${env:ENVIRONMENT}.yaml
    - ./config/${env:REGION}/settings.yaml
  ```
- **AND** the environment variables `ENVIRONMENT` and `REGION` are set
- **WHEN** the configuration is loaded
- **THEN** environment variables are interpolated in import paths before loading
- **AND** the resolved paths are used to locate the imported files

#### Scenario: Remote imports
- **GIVEN** a configuration file with:
  ```yaml
  imports:
    - s3://my-bucket/shared/settings.yaml
    - https://example.com/config/views.yaml
  ```
- **WHEN** the configuration is loaded
- **THEN** remote files are fetched using the same filesystem abstraction as remote config loading
- **AND** authentication follows the same rules as remote config loading

#### Scenario: No imports field
- **GIVEN** a configuration file without an `imports` field
- **WHEN** the configuration is loaded
- **THEN** it loads normally as a single-file configuration
- **AND** no merging occurs

#### Scenario: Empty imports list
- **GIVEN** a configuration file with:
  ```yaml
  imports: []
  
  duckdb:
    database: catalog.duckdb
  ```
- **WHEN** the configuration is loaded
- **THEN** it loads normally as a single-file configuration
- **AND** no merging occurs

### Requirement: Import Resolution Order
Imports MUST be processed in the order they appear, with later imports taking precedence over earlier ones for conflicting scalar values.

#### Scenario: Import order matters for scalar overrides
- **GIVEN** `base.yaml`:
  ```yaml
  duckdb:
    database: base.duckdb
    settings:
      - "threads = 4"
  ```
- **AND** `override.yaml`:
  ```yaml
  duckdb:
    database: override.duckdb
  ```
- **AND** `main.yaml`:
  ```yaml
  imports:
    - ./base.yaml
    - ./override.yaml
  ```
- **WHEN** the configuration is loaded
- **THEN** the resulting `duckdb.database` is `"override.duckdb"` (last wins)
- **AND** the resulting `duckdb.settings` is `["threads = 4"]` (merged from base)

#### Scenario: Main file overrides imports
- **GIVEN** `shared.yaml`:
  ```yaml
  duckdb:
    database: shared.duckdb
    settings:
      - "threads = 4"
  ```
- **AND** `main.yaml`:
  ```yaml
  imports:
    - ./shared.yaml
  
  duckdb:
    database: main.duckdb
  ```
- **WHEN** the configuration is loaded
- **THEN** the resulting `duckdb.database` is `"main.duckdb"` (main file wins over imports)
- **AND** the resulting `duckdb.settings` is `["threads = 4"]` (preserved from import)

### Requirement: Merging Strategy
The system MUST implement a deep merge strategy that combines configuration sections from multiple files.

#### Scenario: Deep merge of objects
- **GIVEN** `settings.yaml`:
  ```yaml
  duckdb:
    install_extensions: ["httpfs"]
    settings:
      - "threads = 4"
  ```
- **AND** `secrets.yaml`:
  ```yaml
  duckdb:
    secrets:
      - type: s3
        provider: config
        key_id: "${env:AWS_ACCESS_KEY_ID}"
        secret: "${env:AWS_SECRET_ACCESS_KEY}"
  ```
- **AND** `main.yaml`:
  ```yaml
  imports:
    - ./settings.yaml
    - ./secrets.yaml
  ```
- **WHEN** the configuration is loaded
- **THEN** the resulting configuration has:
  ```yaml
  duckdb:
    install_extensions: ["httpfs"]
    settings:
      - "threads = 4"
    secrets:
      - type: s3
        provider: config
        key_id: "${env:AWS_ACCESS_KEY_ID}"
        secret: "${env:AWS_SECRET_ACCESS_KEY}"
  ```

#### Scenario: List concatenation
- **GIVEN** `users.yaml`:
  ```yaml
  views:
    - name: users
      source: parquet
      uri: data/users.parquet
  ```
- **AND** `products.yaml`:
  ```yaml
  views:
    - name: products
      source: parquet
      uri: data/products.parquet
  ```
- **AND** `main.yaml`:
  ```yaml
  imports:
    - ./users.yaml
    - ./products.yaml
  ```
- **WHEN** the configuration is loaded
- **THEN** the resulting `views` list contains both views in order
- **AND** view names remain unique across all imports

#### Scenario: Scalar values are replaced (last wins)
- **GIVEN** `dev.yaml`:
  ```yaml
  duckdb:
    database: dev.duckdb
  ```
- **AND** `prod.yaml`:
  ```yaml
  duckdb:
    database: prod.duckdb
  ```
- **AND** `main.yaml`:
  ```yaml
  imports:
    - ./dev.yaml
    - ./prod.yaml
  ```
- **WHEN** the configuration is loaded
- **THEN** the resulting `duckdb.database` is `"prod.duckdb"` (last import wins)

### Requirement: Unique Name Validation
The system MUST validate that certain named entities remain unique across all imported files.

#### Scenario: Duplicate view names cause error
- **GIVEN** `file1.yaml`:
  ```yaml
  views:
    - name: users
      source: parquet
      uri: data/users.parquet
  ```
- **AND** `file2.yaml`:
  ```yaml
  views:
    - name: users
      source: csv
      uri: data/users.csv
  ```
- **AND** `main.yaml`:
  ```yaml
  imports:
    - ./file1.yaml
    - ./file2.yaml
  ```
- **WHEN** the configuration is loaded
- **THEN** validation fails with a clear error indicating duplicate view name `"users"`
- **AND** the error indicates which files contain the duplicate

#### Scenario: Duplicate semantic model names cause error
- **GIVEN** `file1.yaml`:
  ```yaml
  semantic_models:
    - name: sales
      base_view: orders
  ```
- **AND** `file2.yaml`:
  ```yaml
  semantic_models:
    - name: sales
      base_view: transactions
  ```
- **AND** `main.yaml`:
  ```yaml
  imports:
    - ./file1.yaml
    - ./file2.yaml
  ```
- **WHEN** the configuration is loaded
- **THEN** validation fails with a clear error indicating duplicate semantic model name `"sales"`

#### Scenario: Duplicate attachment aliases cause error
- **GIVEN** `file1.yaml`:
  ```yaml
  attachments:
    duckdb:
      - alias: ref
        path: ref1.duckdb
  ```
- **AND** `file2.yaml`:
  ```yaml
  attachments:
    duckdb:
      - alias: ref
        path: ref2.duckdb
  ```
- **AND** `main.yaml`:
  ```yaml
  imports:
    - ./file1.yaml
    - ./file2.yaml
  ```
- **WHEN** the configuration is loaded
- **THEN** validation fails with a clear error indicating duplicate attachment alias `"ref"`

#### Scenario: Duplicate iceberg catalog names cause error
- **GIVEN** `file1.yaml`:
  ```yaml
  iceberg_catalogs:
    - name: data_lake
      catalog_type: rest
  ```
- **AND** `file2.yaml`:
  ```yaml
  iceberg_catalogs:
    - name: data_lake
      catalog_type: hive
  ```
- **AND** `main.yaml`:
  ```yaml
  imports:
    - ./file1.yaml
    - ./file2.yaml
  ```
- **WHEN** the configuration is loaded
- **THEN** validation fails with a clear error indicating duplicate iceberg catalog name `"data_lake"`

### Requirement: Cycle Detection
The system MUST detect and reject circular imports to prevent infinite recursion.

#### Scenario: Direct self-import causes error
- **GIVEN** `circular.yaml`:
  ```yaml
  imports:
    - ./circular.yaml
  
  duckdb:
    database: catalog.duckdb
  ```
- **WHEN** the configuration is loaded
- **THEN** loading fails with a clear error indicating a circular import

#### Scenario: Indirect circular import causes error
- **GIVEN** `a.yaml` imports `b.yaml`
- **AND** `b.yaml` imports `c.yaml`
- **AND** `c.yaml` imports `a.yaml`
- **WHEN** `a.yaml` is loaded
- **THEN** loading fails with a clear error indicating the circular import chain

#### Scenario: Multiple imports of same file are allowed
- **GIVEN** `shared.yaml` with valid configuration
- **AND** `main.yaml`:
  ```yaml
  imports:
    - ./shared.yaml
    - ./shared.yaml  # Same file imported twice
  
  duckdb:
    database: catalog.duckdb
  ```
- **WHEN** the configuration is loaded
- **THEN** it loads successfully (duplicate imports are deduplicated)
- **AND** `shared.yaml` is only loaded once

### Requirement: Path Resolution
Import paths MUST be resolved relative to the importing file's directory, supporting both relative and absolute paths.

#### Scenario: Relative path resolution
- **GIVEN** directory structure:
  ```
  project/
    config/
      main.yaml
      settings.yaml
    data/
      views.yaml
  ```
- **AND** `config/main.yaml`:
  ```yaml
  imports:
    - ./settings.yaml
    - ../data/views.yaml
  ```
- **WHEN** the configuration is loaded
- **THEN** `./settings.yaml` resolves to `project/config/settings.yaml`
- **AND** `../data/views.yaml` resolves to `project/data/views.yaml`

#### Scenario: Absolute paths work as-is
- **GIVEN** `main.yaml`:
  ```yaml
  imports:
    - /etc/duckalog/settings.yaml
  ```
- **WHEN** the configuration is loaded
- **THEN** the absolute path `/etc/duckalog/settings.yaml` is used as-is

#### Scenario: Environment variable interpolation in paths
- **GIVEN** `ENVIRONMENT=production` is set
- **AND** `main.yaml`:
  ```yaml
  imports:
    - ./config/${env:ENVIRONMENT}.yaml
  ```
- **WHEN** the configuration is loaded
- **THEN** the path resolves to `./config/production.yaml` after interpolation

### Requirement: Error Handling
The system MUST provide clear error messages for import-related failures.

#### Scenario: Import file not found
- **GIVEN** `main.yaml`:
  ```yaml
  imports:
    - ./missing.yaml
  ```
- **WHEN** the configuration is loaded
- **THEN** loading fails with a clear error indicating the file `./missing.yaml` was not found
- **AND** the error includes the resolved absolute path

#### Scenario: Import file has syntax error
- **GIVEN** `broken.yaml` contains invalid YAML
- **AND** `main.yaml`:
  ```yaml
  imports:
    - ./broken.yaml
  ```
- **WHEN** the configuration is loaded
- **THEN** loading fails with a clear error indicating the syntax error in `./broken.yaml`
- **AND** the error includes the file path and line/column information if available

#### Scenario: Import file validation fails
- **GIVEN** `invalid.yaml` contains invalid configuration (e.g., missing required fields)
- **AND** `main.yaml`:
  ```yaml
  imports:
    - ./invalid.yaml
  ```
- **WHEN** the configuration is loaded
- **THEN** loading fails with a clear error indicating the validation failure in `./invalid.yaml`
- **AND** the error includes the file path

### Requirement: Backward Compatibility
All existing environment variable usage SHALL continue to work unchanged.

#### Scenario: Existing ${env:VAR} syntax unchanged
- **GIVEN** a configuration using `${env:DATABASE_URL}` syntax
- **AND** no .env files are present
- **WHEN** the configuration is loaded
- **THEN** behavior is identical to the previous version
- **AND** system environment variables are still accessed directly

#### Scenario: Existing environment variable precedence maintained
- **GIVEN** system environment variables set via export
- **WHEN** configuration is loaded with or without .env files
- **THEN** system environment variables maintain the same precedence as before
- **AND** no existing workflows are broken

#### Scenario: Configuration loading flow
- **GIVEN** a configuration file path is provided to `load_config()`
- **WHEN** the configuration is loaded
- **THEN** the following steps occur in order:
  1. Discover and load .env files from directory hierarchy
  2. Add .env variables to os.environ
  3. Load and parse the configuration file (existing behavior)
  4. Apply environment variable interpolation (existing behavior)
  5. Validate and return the configuration (existing behavior)

#### Scenario: Error handling integration
- **GIVEN** configuration loading encounters errors at various stages
- **WHEN** errors occur
- **THEN** errors are handled according to existing patterns
- **AND** .env file errors do not prevent configuration loading unless critical
- **AND** appropriate error messages are provided to users

### Requirement: Performance Considerations
Import processing MUST be efficient and avoid redundant work.

#### Scenario: Same file imported multiple times
- **GIVEN** `shared.yaml` with complex configuration
- **AND** `main.yaml`:
  ```yaml
  imports:
    - ./shared.yaml
    - ./shared.yaml
    - ./shared.yaml
  ```
- **WHEN** the configuration is loaded
- **THEN** `shared.yaml` is only loaded and parsed once
- **AND** the result is reused for all imports

#### Scenario: Nested imports are processed efficiently
- **GIVEN** `a.yaml` imports `b.yaml` and `c.yaml`
- **AND** `b.yaml` imports `d.yaml`
- **AND** `c.yaml` also imports `d.yaml`
- **WHEN** `a.yaml` is loaded
- **THEN** `d.yaml` is only loaded and parsed once
- **AND** the result is reused for both imports

### Requirement: CLI and API Compatibility
The import feature MUST work transparently through all existing interfaces.

#### Scenario: CLI commands work with imported configs
- **GIVEN** a configuration file with imports
- **WHEN** running `duckalog build config.yaml`
- **THEN** the command works exactly as with single-file configs
- **AND** all imported files are loaded and merged automatically

#### Scenario: Python API works with imported configs
- **GIVEN** a configuration file with imports
- **WHEN** calling `load_config("config.yaml")` from Python
- **THEN** it returns a merged `Config` object
- **AND** the caller doesn't need to know about imports

#### Scenario: Dry-run works with imported configs
- **GIVEN** a configuration file with imports
- **WHEN** running `duckalog build config.yaml --dry-run`
- **THEN** it generates SQL for the merged configuration
- **AND** all imported views are included

### Requirement: Security Considerations
Import paths MUST respect the same security boundaries as other path resolution.

#### Scenario: Import path traversal is prevented
- **GIVEN** a configuration file with:
  ```yaml
  imports:
    - ../../../etc/passwd
  ```
- **WHEN** the configuration is loaded
- **THEN** loading fails with a security error if the resolved path is outside allowed roots
- **AND** the error clearly indicates the security violation

#### Scenario: Remote imports use same security as remote configs
- **GIVEN** a configuration file with:
  ```yaml
  imports:
    - s3://bucket/config.yaml
  ```
- **WHEN** the configuration is loaded
- **THEN** remote loading follows the same security rules as remote config loading
- **AND** authentication is handled consistently

### Requirement: SQL File and Template Sources
View definitions MAY reference external SQL files or SQL templates in addition to inline SQL, but each view MUST declare at most one SQL source.

#### Scenario: View uses sql_file for external SQL
- **GIVEN** a config where a view includes a `sql_file` reference with a non-empty `path`
- **WHEN** `load_config()` is called with `load_sql_files=True`
- **THEN** the loader SHALL resolve the SQL file path relative to the config file directory (for non-remote paths)
- **AND** validate the resolved path using the existing path security rules
- **AND** read the file content and populate `view.sql` with the loaded SQL text
- **AND** clear the `sql_file` reference on the resulting configuration object.

#### Scenario: View uses sql_template with variables
- **GIVEN** a config where a view includes a `sql_template` reference with `path` and a `variables` mapping
- **WHEN** `load_config()` is called with `load_sql_files=True`
- **THEN** the loader SHALL load the template content from the referenced file
- **AND** perform placeholder substitution for `{{variable}}` markers using the provided `variables`
- **AND** raise a configuration or SQL file error if any placeholder has no corresponding variable value
- **AND** populate `view.sql` with the rendered SQL text, clearing the `sql_template` reference.

#### Scenario: Exclusive SQL source per view
- **GIVEN** a config where a view defines more than one SQL source among `sql`, `sql_file`, and `sql_template`
- **WHEN** the configuration is validated
- **THEN** validation SHALL fail with a clear error indicating that only one of `sql`, `sql_file`, or `sql_template` may be specified per view.

#### Scenario: Loading config without processing SQL files
- **GIVEN** a config that uses `sql_file` or `sql_template` on one or more views
- **WHEN** `load_config()` is called with `load_sql_files=False`
- **THEN** the configuration MAY be validated successfully without performing any SQL file IO or template processing
- **AND** the resulting `Config` instance SHALL preserve the `sql_file` and `sql_template` references for callers that wish to handle them explicitly.

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

### Requirement: Automatic .env File Discovery and Loading
When loading configuration files, duckalog SHALL automatically discover and load .env files from the directory hierarchy.

#### Scenario: Local config file with .env in same directory
- **GIVEN** a configuration file at `/project/config.yaml`
- **AND** a `.env` file exists at `/project/.env`
- **WHEN** the configuration is loaded via `load_config("/project/config.yaml")`
- **THEN** the .env file is automatically discovered and loaded
- **AND** variables from the .env file are added to the environment before configuration parsing

#### Scenario: Hierarchical .env file discovery
- **GIVEN** a configuration file at `/project/subdir/config.yaml`
- **AND** .env files exist at `/project/subdir/.env`, `/project/.env`, and `/.env`
- **WHEN** the configuration is loaded
- **THEN** all three .env files are discovered and loaded
- **AND** variables from `/project/subdir/.env` take precedence over `/project/.env`
- **AND** variables from `/project/.env` take precedence over `/.env`

#### Scenario: No .env files present
- **GIVEN** a configuration file at `/project/config.yaml`
- **AND** no .env files exist in the directory hierarchy
- **WHEN** the configuration is loaded
- **THEN** configuration loading proceeds normally without .env files
- **AND** no error messages are generated

### Requirement: Environment Variable Precedence
Variables from .env files SHALL be added to the environment with proper precedence over system environment variables.

#### Scenario: .env file overrides system environment
- **GIVEN** a system environment variable `DATABASE_URL="system_db"`
- **AND** a .env file contains `DATABASE_URL="file_db"`
- **WHEN** configuration is loaded with `${env:DATABASE_URL}`
- **THEN** the value resolves to `"file_db"` from the .env file
- **AND** the system environment variable is not modified

#### Scenario: System environment overrides .env file
- **GIVEN** a .env file contains `API_KEY="file_secret"`
- **AND** a system environment variable `API_KEY="system_secret"`
- **WHEN** configuration is loaded with `${env:API_KEY}`
- **THEN** the value resolves to `"system_secret"` from the environment
- **AND** .env file variables have lower precedence than system environment

#### Scenario: Default values work with .env variables
- **GIVEN** a .env file contains `FEATURE_FLAG="enabled"`
- **WHEN** configuration is loaded with `${env:FEATURE_FLAG:disabled}`
- **THEN** the value resolves to `"enabled"` from the .env file
- **AND** the default value `"disabled"` is only used if the variable is not set

### Requirement: .env File Format Support
Duckalog SHALL support standard .env file formats compatible with python-dotenv.

#### Scenario: Basic key-value pairs
- **GIVEN** a .env file with content:
  ```
  DATABASE_URL="postgresql://localhost/db"
  API_KEY=secret123
  DEBUG=true
  ```
- **WHEN** the .env file is loaded
- **THEN** three environment variables are set with the specified values
- **AND** quoted values have quotes removed
- **AND** unquoted values are treated as strings

#### Scenario: Comments and empty lines
- **GIVEN** a .env file with content:
  ```
  # This is a comment
  KEY1=value1
  
  KEY2=value2  # inline comment
  ```
- **WHEN** the .env file is loaded
- **THEN** only `KEY1` and `KEY2` are set as environment variables
- **AND** comment lines are ignored
- **AND** empty lines are ignored
- **AND** inline comments are supported

#### Scenario: Quoted values with special characters
- **GIVEN** a .env file with content:
  ```
  DATABASE_URL="postgresql://user:pass@localhost:5432/db"
  MESSAGE="Hello World"
  JSON_DATA='{"key": "value"}'
  ```
- **WHEN** the .env file is loaded
- **THEN** all values are parsed correctly with special characters preserved
- **AND** both single and double quotes are supported
- **AND** escape sequences in double quotes are handled properly

### Requirement: Security and Error Handling
Duckalog SHALL handle .env files securely and gracefully handle errors.

#### Scenario: Malformed .env file
- **GIVEN** a .env file contains invalid syntax:
  ```
  KEY1=value1
  INVALID LINE WITHOUT EQUALS
  KEY2=value2
  ```
- **WHEN** the .env file is loaded
- **THEN** the file loading logs a warning message
- **AND** valid key-value pairs are still loaded
- **AND** configuration loading continues without failure

#### Scenario: Permission denied on .env file
- **GIVEN** a .env file exists but has no read permissions
- **WHEN** duckalog attempts to load the .env file
- **THEN** a debug message is logged about the unreadable file
- **AND** configuration loading continues without the .env file
- **AND** no error is raised to the user

#### Scenario: Sensitive data handling
- **GIVEN** a .env file contains sensitive variables like passwords and API keys
- **WHEN** configuration is loaded with verbose logging enabled
- **THEN** the .env file path and variable count are logged
- **AND** the actual variable values are never logged
- **AND** sensitive content is protected from accidental exposure

### Requirement: Integration with Remote Configurations
.env file loading SHALL work appropriately with remote configuration files.

#### Scenario: Remote config file with local .env
- **GIVEN** a remote configuration URI `s3://bucket/config.yaml`
- **AND** a local .env file exists in the current working directory
- **WHEN** the remote configuration is loaded
- **THEN** the local .env file is loaded if the current directory contains one
- **AND** .env discovery starts from the current working directory for remote configs

#### Scenario: Remote .env files (future enhancement)
- **GIVEN** a remote configuration references remote .env files
- **WHEN** the configuration is loaded
- **THEN** only local .env files are supported initially
- **AND** remote .env file support can be added in future versions

### Requirement: Performance and Caching
.env file loading SHALL be efficient and avoid redundant filesystem operations.

#### Scenario: Multiple config files in same directory
- **GIVEN** two configuration files in `/project/config1.yaml` and `/project/config2.yaml`
- **AND** a .env file exists at `/project/.env`
- **WHEN** both configurations are loaded
- **THEN** the .env file is loaded only once and cached
- **AND** subsequent loads use the cached variables

#### Scenario: Directory search depth limit
- **GIVEN** a configuration file in a deeply nested directory structure
- **WHEN** .env file discovery searches parent directories
- **THEN** the search stops after 10 directory levels
- **AND** a warning is logged if the depth limit is reached

