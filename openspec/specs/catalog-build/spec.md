# catalog-build Specification

## Purpose
TBD - created by archiving change add-catalog-build-cli. Update Purpose after archive.
## Requirements
### Requirement: Build Catalog from Config
The system MUST provide a function to build or update a DuckDB catalog from a validated configuration.

#### Scenario: Catalog built from YAML config
- **GIVEN** a valid YAML config describing a DuckDB database path, attachments, Iceberg catalogs, and views
- **WHEN** `build_catalog(config_path)` is called
- **THEN** the system opens the configured DuckDB database (or `:memory:` if unspecified)
- **AND** applies pragmas, installs and loads extensions, sets up attachments and Iceberg catalogs
- **AND** creates or replaces all configured views.

#### Scenario: Idempotent catalog builds
- **GIVEN** a valid config and an existing DuckDB catalog file
- **WHEN** `build_catalog(config_path)` is run multiple times with the same inputs
- **THEN** the resulting catalog contains the same set of views with the same definitions
- **AND** no duplicate or unexpected views are created.

### Requirement: Dry-run SQL generation
The system MUST support generating the full set of `CREATE OR REPLACE VIEW` statements from a config without connecting to DuckDB.

#### Scenario: SQL generated without touching DB
- **GIVEN** a valid config file
- **WHEN** `build_catalog(config_path, dry_run=True)` is called
- **THEN** the system generates SQL for all views based on the config
- **AND** does not attempt to open a DuckDB connection
- **AND** returns or prints the generated SQL.

### Requirement: CLI Build Command
The CLI MUST expose a `build` command that applies a config to a DuckDB catalog file, with options for overriding the DB path, dry-run, and verbose logging.

#### Scenario: CLI build applies config
- **GIVEN** a valid config file path
- **WHEN** `duckalog build catalog.yaml --db-path my_catalog.duckdb` is executed
- **THEN** the command opens or creates `my_catalog.duckdb`
- **AND** applies the configuration to create or replace views
- **AND** exits with status code `0` on success.

#### Scenario: CLI build fails on engine error
- **GIVEN** a config with an invalid view or attachment that causes SQL execution to fail
- **WHEN** `duckalog build catalog.yaml` is executed
- **THEN** the command prints a clear error message derived from an `EngineError`
- **AND** exits with a non-zero status code.

### Requirement: CLI Generate-SQL Command
The CLI MUST expose a `generate-sql` command that validates the config and writes SQL to stdout or a specified file without connecting to DuckDB.

#### Scenario: SQL written to file
- **GIVEN** a valid config file path
- **AND** an output file path `create_views.sql`
- **WHEN** `duckalog generate-sql catalog.yaml --output create_views.sql` is executed
- **THEN** the command validates the config
- **AND** writes `CREATE OR REPLACE VIEW` statements for all views to `create_views.sql`
- **AND** does not connect to DuckDB.

### Requirement: CLI Validate Command
The CLI MUST expose a `validate` command that parses and validates a config (including env interpolation) and reports success or failure via exit code.

#### Scenario: Valid config returns success
- **GIVEN** a valid config file
- **WHEN** `duckalog validate catalog.yaml` is executed
- **THEN** the command prints a success message
- **AND** exits with status code `0`.

#### Scenario: Invalid config returns failure
- **GIVEN** a config with missing required fields or unresolved `${env:VAR}` placeholders
- **WHEN** `duckalog validate catalog.yaml` is executed
- **THEN** the command prints a descriptive error message
- **AND** exits with a non-zero status code.

### Requirement: Build and attach nested Duckalog configs
The catalog build process SHALL build any child Duckalog configs declared under `attachments.duckalog` before creating attachments on the parent connection, then ATTACH the resulting DuckDB catalog using the configured alias and read-only flag.

#### Scenario: Child catalog built then attached
- **GIVEN** a parent config `catalog.yaml` with `attachments.duckalog` pointing to `./child.yaml` and alias `ref_data`
- **AND** `child.yaml` defines `duckdb.database: "artifacts/ref.duckdb"` and its own views
- **WHEN** `build_catalog("catalog.yaml")` runs
- **THEN** the system builds `child.yaml` first, producing `artifacts/ref.duckdb`
- **AND** attaches that database as `ref_data` on the parent connection before creating parent views.

#### Scenario: Attachment reuse within a run
- **GIVEN** multiple entries reference the same resolved child config path
- **WHEN** `build_catalog` executes
- **THEN** the child config is built only once for the run
- **AND** its resulting database path is reused for each alias attachment.

#### Scenario: Cyclic attachment graph rejected
- **GIVEN** configs A and B that reference each other via `attachments.duckalog`
- **WHEN** `build_catalog` is invoked on A
- **THEN** the system detects the cycle during traversal
- **AND** fails with a clear cycle error before executing any attachment SQL.

#### Scenario: Dry-run skips child builds
- **GIVEN** `build_catalog(config_path, dry_run=True)`
- **WHEN** the config includes `attachments.duckalog`
- **THEN** child configs are parsed and validated to ensure paths and databases are resolvable
- **AND** no child catalog build or ATTACH statements are executed.

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

### Requirement: Path Security During Catalog Operations
All file paths used during catalog build operations MUST be validated against allowed roots to prevent unauthorized file system access.

#### Scenario: Local data file access validation
- **GIVEN** a catalog build that references local data files through view URIs
- **WHEN** relative paths like `"data/events.parquet"` or `"../shared/data/users.parquet"` are resolved
- **THEN** all resolved paths SHALL be validated to ensure they remain within allowed roots
- **AND** paths that resolve outside allowed roots SHALL cause the build to fail with a clear security error

#### Scenario: SQL file path validation
- **GIVEN** view definitions that reference external SQL files via `sql_file` field
- **WHEN** relative SQL file paths are resolved during configuration loading
- **THEN** the resolved SQL file paths SHALL be validated against allowed roots
- **AND** SQL files outside allowed roots SHALL not be accessible to the catalog build

#### Scenario: Attachment path validation
- **GIVEN** database attachments (DuckDB, SQLite) with relative paths
- **WHEN** attachment paths like `"./databases/reference.duckdb"` or `"../legacy/system.db"` are resolved
- **THEN** all resolved attachment paths SHALL be validated against allowed roots
- **AND** attachments with paths outside allowed roots SHALL cause build failure

#### Scenario: Export path validation
- **GIVEN** catalog export operations to local file paths
- **WHEN** export paths are specified as relative paths
- **THEN** the resolved export paths SHALL be validated to ensure they remain within allowed roots
- **AND** export paths outside allowed roots SHALL be rejected to prevent unauthorized file system writes

### Requirement: Safe SQL Generation for Views and Secrets
SQL generated from configuration for catalog builds MUST safely quote all configuration‑derived identifiers and string literals and MUST avoid interpolating unsupported secret option types.

#### Scenario: View SQL uses quoted identifiers
- **GIVEN** a config with views that reference attached databases or tables whose names contain spaces, reserved words, or other special characters
- **WHEN** SQL is generated for those views
- **THEN** database, schema, and table names are emitted as properly quoted identifiers
- **AND** attempts to inject additional SQL via these fields do not change the structure of the generated statement.

#### Scenario: Secret SQL uses safe literals and strict option types
- **GIVEN** a config with DuckDB secrets whose fields and options contain quotes or other special characters
- **WHEN** `CREATE SECRET` statements are generated for catalog builds or dry‑run SQL output
- **THEN** all string values are emitted as safely quoted literals
- **AND** numeric and boolean option values are rendered without quotes according to their type
- **AND** any secret option whose value type is not `bool`, `int`, `float`, or `str` causes validation or SQL generation to fail with a clear error instead of interpolating an unsafe representation.

### Requirement: Canonical SQL Quoting Helpers
The system MUST provide canonical functions for SQL construction that serve as the single source of truth for safe SQL generation.

#### Scenario: Canonical quoting API
- **GIVEN** a need to construct SQL from configuration-derived values
- **WHEN** developers need to quote identifiers or string literals for SQL
- **THEN** they MUST use the canonical `quote_ident(identifier: str) -> str` and `quote_literal(value: str) -> str` functions
- **AND** callers MUST pass raw strings and MUST NOT add their own surrounding quotes
- **AND** `quote_ident` MUST double any embedded `"` characters for identifier escaping
- **AND** `quote_literal` MUST double any embedded `'` characters for literal escaping

#### Scenario: Path normalization composes with quoting
- **GIVEN** a need to convert file paths to SQL literals
- **WHEN** `normalize_path_for_sql` is called
- **THEN** it MUST compose with the canonical quoting helpers rather than implementing its own quoting logic
- **AND** the function MUST focus on path normalization (via `pathlib.Path`) and delegate to `quote_literal` for quoting

#### Scenario: Consistent quoting across SQL generation
- **GIVEN** SQL generation code in `sql_generation.py`, `engine.py`, and related modules
- **WHEN** constructing SQL that includes configuration-derived identifiers or string literals
- **THEN** all code MUST use the canonical quoting helpers instead of ad-hoc string manipulation
- **AND** attachment aliases, database names, table names, and view names MUST be passed through `quote_ident`
- **AND** file paths, connection strings, secret values, and other string literals MUST be passed through `quote_literal`

### Engine Structure

The catalog build system SHALL use a `CatalogBuilder` orchestration class to manage the build process:

#### CatalogBuilder Design
- **Purpose**: Encapsulates the entire catalog build workflow into a single, testable class
- **Single Responsibility**: Each private method handles one specific aspect of the build process
- **Resource Management**: Ensures proper cleanup of temporary files and database connections
- **Error Handling**: Provides consistent error handling with clear context

#### CatalogBuilder Methods
- `_create_connection()`: Creates and configures DuckDB connection
- `_apply_pragmas()`: Installs extensions, loads extensions, applies pragmas and settings
- `_setup_attachments()`: Sets up DuckDB, SQLite, and Postgres attachments
- `_create_secrets()`: Creates configured DuckDB secrets
- `_create_views()`: Creates or replaces all configured views
- `_cleanup()`: Handles cleanup of temporary resources and connections

#### Dependency Resolution
The engine uses a depth-limited Depth-First Search (DFS) approach for config dependency resolution:

- **Cycle Detection**: Maintains a `visited` set of resolved config paths to detect cycles during traversal
- **Maximum Depth**: Enforces a configurable maximum depth (default: 5) to prevent runaway recursion
- **Path Tracking**: Tracks visited config paths to prevent rebuilding the same dependency multiple times within a single run
- **Hierarchical Semantics**: Preserves existing attachment hierarchy behavior where child configs are built before parent attachments

### Security Regression Tests

The catalog build process MUST include comprehensive regression tests to ensure that security vulnerabilities cannot be re-introduced through future changes to SQL generation and path resolution logic.

#### Requirement: SQL Security During Catalog Build
Catalog build operations MUST generate SQL that is resilient to injection attacks and maintains security boundaries throughout the build process.

##### Scenario: Dry-run SQL generation security
- **GIVEN** configurations with views and secrets containing potentially malicious values
- **WHEN** `generate_all_views_sql()` is called with `include_secrets=True`
- **THEN** the generated SQL SHALL be syntactically valid and secure
- **AND** malicious content SHALL remain safely quoted within identifiers and literals
- **AND** the SQL SHALL be identical to what would be executed in a live catalog build

##### Scenario: View creation SQL injection prevention
- **GIVEN** view configurations with table or database names containing SQL injection attempts
- **WHEN** catalog build creates views using these configurations
- **THEN** the generated `CREATE OR REPLACE VIEW` statements SHALL not be vulnerable to injection
- **AND** all identifiers SHALL be properly quoted
- **AND** no additional statements SHALL be created through injection attempts

##### Scenario: Secret creation during catalog build
- **GIVEN** catalog builds that create DuckDB secrets
- **WHEN** secrets are created using `CREATE SECRET` statements
- **THEN** all secret values SHALL be safely quoted as SQL literals
- **AND** secret options SHALL be validated for type safety
- **AND** errors in secret creation SHALL cause the build to fail with clear error messages

#### Requirement: Path Security During Catalog Build
Catalog build operations MUST enforce path security boundaries to prevent unauthorized file system access during the build process.

##### Scenario: Local file access during builds
- **GIVEN** catalog builds that access local files (parquet, delta, attachments, etc.)
- **WHEN** file paths are resolved and accessed during the build
- **THEN** all file access SHALL be restricted to allowed roots
- **AND** any attempts to access files outside allowed roots SHALL cause build failure
- **AND** the build error SHALL clearly indicate the security violation

##### Scenario: Attachment path validation during builds
- **GIVEN** catalog builds with database attachments using relative paths
- **WHEN** attachment paths are resolved and used to attach external databases
- **THEN** all resolved attachment paths SHALL be validated against allowed roots
- **AND** attachments with paths outside allowed roots SHALL cause build failure
- **AND** the security check SHALL occur before any database connection attempts

#### Requirement: Security Test Coverage Requirements
The project MUST maintain specific regression tests that cover the security behaviors defined in this and related specifications.

##### Scenario: Mandatory security test coverage
- **GIVEN** future changes to SQL generation, path resolution, or security-related functionality
- **WHEN** contributors modify security-sensitive code
- **THEN** the existing security regression tests MUST remain green
- **AND** new security-sensitive functionality MUST include appropriate regression tests
- **AND** the security test suite MUST be documented in contributor guidelines

##### Scenario: Security test isolation
- **GIVEN** security regression tests that use hostile inputs
- **WHEN** these tests are executed
- **THEN** they MUST NOT affect the test environment or other tests
- **AND** they MUST use temporary directories or sandboxed environments
- **AND** they MUST clean up any created files or resources after execution

### Requirement: Security Regression Tests for SQL and Paths
The project MUST include regression tests that exercise security‑sensitive behavior for SQL generation and path resolution, to prevent re‑introducing previously fixed vulnerabilities.

#### Scenario: SQL injection regression tests
- **GIVEN** view configurations and secrets whose names and values contain quotes, semicolons, comments, and other potentially dangerous characters
- **WHEN** SQL is generated for catalog builds or dry‑run modes
- **THEN** automated tests assert that the resulting SQL remains syntactically valid
- **AND** configuration‑derived values remain safely contained within quoted identifiers or literals
- **AND** no additional statements can be injected via these fields.

#### Scenario: Path traversal regression tests
- **GIVEN** configurations that reference local files using relative and absolute paths, including attempts to escape the config directory via `..` segments or platform‑specific forms
- **WHEN** path resolution helpers are invoked during config loading or catalog builds
- **THEN** automated tests assert that only paths within allowed roots (such as the config directory) are accepted
- **AND** paths that resolve outside allowed roots cause configuration errors rather than silent acceptance.

### Requirement: Engine Orchestration Structure and Cleanup
The catalog build engine MUST orchestrate connection setup, attachments, secrets, views, and exports through a cohesive component that ensures proper resource cleanup even when errors occur.

#### Scenario: Catalog build uses structured orchestration
- **GIVEN** a valid catalog configuration
- **WHEN** `build_catalog` is invoked via the CLI or Python API
- **THEN** the engine creates and configures a DuckDB connection, sets up attachments and secrets, creates views, and performs any configured export as a single orchestrated operation
- **AND** temporary resources such as intermediate files are tracked for cleanup instead of being managed ad‑hoc in multiple locations.

#### Scenario: Resources cleaned up on failure
- **GIVEN** a configuration that triggers an error during catalog build (for example, invalid SQL or attachment failure)
- **WHEN** `build_catalog` runs and raises an engine error
- **THEN** the engine still closes any open connections and attempts to delete temporary files created during the run
- **AND** the system does not leave behind orphaned temporary database files.

### Requirement: Shared CLI Filesystem Options
Filesystem‑related CLI options MUST be defined once and reused across all commands that accept a config path, so that behavior and help text remain consistent.

#### Scenario: Build, generate-sql, and validate share filesystem options
- **GIVEN** the `build`, `generate-sql`, and `validate` CLI commands
- **WHEN** a user passes filesystem options (such as protocol, credentials, or endpoints)
- **THEN** each command accepts the same set of filesystem‑related flags with the same defaults and help text
- **AND** those flags are parsed by a shared implementation that constructs the filesystem object used during config loading.

