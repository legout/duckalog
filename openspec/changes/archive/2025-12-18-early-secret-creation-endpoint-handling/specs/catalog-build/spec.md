## ADDED Requirements

### Requirement: Early Secret Creation
DuckDB secrets SHALL be created before database attachments are set up to ensure credentials are available for remote attachments.

#### Scenario: S3 attachment with matching S3 secret
- **GIVEN** a configuration with an S3 secret for credentials `lodl`
- **AND** an attachment pointing to `s3://ewn/external-db.duckdb`
- **WHEN** the catalog is built
- **THEN** the S3 secret is created **before** the attachment is established
- **AND** the attachment can successfully access the S3 location using the configured credentials

#### Scenario: Main catalog build process order
- **GIVEN** a typical catalog configuration with secrets and attachments
- **WHEN** `CatalogBuilder.build()` is executed
- **THEN** the execution order is:
  1. `_setup_connection()` - Connect to DuckDB
  2. `_apply_pragmas()` - Apply DuckDB settings and extensions (no secrets)
  3. `_create_secrets()` - Create all configured secrets
  4. `_setup_attachments()` - Setup database attachments (can use secrets)
  5. `_create_views()` - Create configured views

#### Scenario: Child catalog build order
- **GIVEN** a Duckalog attachment configuration with nested dependencies
- **WHEN** `ConfigDependencyGraph._build_database()` is executed for child catalogs
- **THEN** child catalogs follow the same execution order as main catalogs
- **AND** secrets are available before any remote operations in child catalogs

### Requirement: Endpoint Protocol Normalization
S3 endpoint values SHALL have protocol prefixes (`http://`, `https://`) automatically stripped before being passed to DuckDB.

#### Scenario: Endpoint with HTTPS protocol
- **GIVEN** a configuration with `endpoint: "https://lodl.nes.siemens.de:8333"`
- **WHEN** the S3 secret is generated
- **THEN** the endpoint value `"lodl.nes.siemens.de:8333"` (without protocol) is passed to DuckDB
- **AND** the secret creation succeeds without connection errors

#### Scenario: Endpoint with HTTP protocol
- **GIVEN** a configuration with `endpoint: "http://internal-s3.local:9000"`
- **WHEN** the S3 secret is generated
- **THEN** the endpoint value `"internal-s3.local:9000"` (without protocol) is passed to DuckDB
- **AND** the secret creation succeeds

#### Scenario: Endpoint without protocol
- **GIVEN** a configuration with `endpoint: "lodl.nes.siemens.de:8333"`
- **WHEN** the S3 secret is generated
- **THEN** the endpoint value `"lodl.nes.siemens.de:8333"` is passed to DuckDB unchanged
- **AND** the secret creation succeeds

### Requirement: Secret Validation Enhancement
Configuration validation SHALL ensure secrets are properly configured before attempting operations that require them.

#### Scenario: Unresolved environment variable in secret
- **GIVEN** a configuration with `${env:MISSING_VAR}` in a secret field
- **AND** the environment variable `MISSING_VAR` is not set
- **WHEN** the configuration is loaded
- **THEN** a clear error message indicates the missing environment variable
- **AND** the build process fails before attempting any DuckDB operations

#### Scenario: Invalid endpoint format
- **GIVEN** a configuration with `endpoint: "not-a-valid-url"`
- **WHEN** the S3 secret is generated
- **THEN** the endpoint is passed to DuckDB as-is for validation
- **AND** any DuckDB-level validation errors are clearly reported

## MODIFIED Requirements

### Requirement: Build Process Execution Order
The catalog build execution order SHALL be modified to create secrets before attachments.

#### OLD Behavior
```
setup_connection() → apply_pragmas() → setup_attachments() → create_secrets() → create_views()
```

#### NEW Behavior
```
setup_connection() → apply_pragmas() → create_secrets() → setup_attachments() → create_views()
```

#### Impact: No Breaking Changes
- **GIVEN** any existing configuration
- **WHEN** the build process executes with the new order
- **THEN** all existing functionality continues to work as before
- **AND** only the internal timing of secret creation changes
- **AND** no configuration schema or API changes occur

### Requirement: Secret Creation Extraction
Secret creation SHALL be extracted from `_apply_duckdb_settings()` to enable independent execution timing.

#### OLD Behavior
```python
def _apply_duckdb_settings(conn, config, verbose):
    # Install/load extensions
    _create_secrets(conn, config, verbose)  # ← Mixed with other setup
    # Apply pragmas
    # Apply settings
```

#### NEW Behavior
```python
def _apply_duckdb_settings(conn, config, verbose):
    # Install/load extensions only
    # Apply pragmas only
    # Apply settings only

def _create_secrets(conn, config, verbose):
    # Create secrets independently
```

#### Impact: Method Separation
- **GIVEN** existing code that calls `_apply_duckdb_settings()`
- **WHEN** the method is refactored
- **THEN** the method behavior remains the same for extensions, pragmas, and settings
- **AND** secret creation is handled separately by `_create_secrets()`

## REMOVED Requirements

### Requirement: None
No existing requirements are being removed by this change. All current functionality is preserved with improved timing and protocol handling.