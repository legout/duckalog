# Config Imports Specification

## Purpose
Enable modular Duckalog configuration by allowing configuration files to import and merge content from other configuration files. This allows users to split large configuration files into smaller, more manageable pieces organized by domain, environment, or team.

## Requirements

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
The import feature MUST be fully backward compatible with existing single-file configurations.

#### Scenario: Existing config without imports works unchanged
- **GIVEN** an existing configuration file without an `imports` field
- **WHEN** the configuration is loaded with the new version
- **THEN** it loads exactly as before
- **AND** no import processing occurs

#### Scenario: Config with imports field but empty list works
- **GIVEN** a configuration file with:
  ```yaml
  imports: []
  
  duckdb:
    database: catalog.duckdb
  ```
- **WHEN** the configuration is loaded
- **THEN** it loads successfully
- **AND** behaves identically to a config without the `imports` field

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

## Implementation Details

### Configuration Model Changes
Add an optional `imports` field to the `Config` model:

```python
class Config(BaseModel):
    version: int
    duckdb: DuckDBConfig
    views: list[ViewConfig] = Field(default_factory=list)
    attachments: AttachmentsConfig = Field(default_factory=AttachmentsConfig)
    iceberg_catalogs: list[IcebergCatalogConfig] = Field(default_factory=list)
    semantic_models: list[SemanticModelConfig] = Field(default_factory=list)
    imports: list[str] = Field(default_factory=list)  # New field
```

### Loading Algorithm
1. Parse main config file
2. If `imports` field exists and is not empty:
   - For each import path in order:
     - Resolve path relative to importing file
     - Check for circular imports
     - Load imported config (recursively processing its imports)
     - Merge imported config into current config
3. Validate merged config
4. Return merged `Config` object

### Merging Implementation
Implement a deep merge function that:
- Handles scalar values (last wins)
- Deep merges dictionaries
- Concatenates lists
- Special handling for lists of named objects (views, semantic_models, etc.) to ensure uniqueness

### Error Messages
Provide clear error messages that:
- Indicate which file has the error
- Show import chain for nested imports
- Clearly indicate duplicate names with file locations
- Show resolved paths for file not found errors

## Testing Strategy

### Unit Tests
- Test basic import functionality
- Test merging strategies (scalars, objects, lists)
- Test duplicate detection
- Test cycle detection
- Test path resolution
- Test environment variable interpolation in paths

### Integration Tests
- Test CLI commands with imported configs
- Test Python API with imported configs
- Test with remote imports
- Test with hierarchical imports (imports that import other files)

### Security Tests
- Test path traversal prevention
- Test remote import security
- Test error handling for missing files

### Performance Tests
- Test deduplication of repeated imports
- Test efficient loading of nested imports
- Test memory usage with large import chains