# API Documentation Audit

This document audits the public API surface for Duckalog to ensure comprehensive, Google-style docstrings.

## Public API Scope

The following public APIs are exported from `duckalog.__init__` and require proper documentation:

### Core Configuration
- `Config` - Root configuration model
- `DuckDBConfig` - DuckDB database settings
- `AttachmentsConfig` - Database attachment configurations  
- `DuckDBAttachment` - DuckDB attachment configuration
- `SQLiteAttachment` - SQLite attachment configuration
- `PostgresAttachment` - PostgreSQL attachment configuration
- `IcebergCatalogConfig` - Iceberg catalog configuration
- `ViewConfig` - Individual view configuration
- `SecretConfig` - Secret management configuration
- `load_config` - Load configuration from file/URI
- `validate_generated_config` - Validate generated config templates
- `ConfigFormat` - Configuration format enum

### Catalog Building and Execution
- `build_catalog` - Build DuckDB catalog from configuration
- `generate_sql` - Generate SQL without execution  
- `validate_config` - Validate configuration syntax
- `connect_to_catalog` - Connect to existing catalog
- `connect_to_catalog_cm` - Connect to catalog (context manager)
- `connect_and_build_catalog` - Build and connect to catalog
- `load_config_from_uri` - Load configuration from remote URI

### SQL Generation and Utilities
- `generate_all_views_sql` - Generate all view SQL statements
- `generate_view_sql` - Generate individual view SQL
- `generate_secret_sql` - Generate secret creation SQL
- `quote_ident` - Quote SQL identifiers
- `quote_literal` - Quote SQL literals
- `render_options` - Render SQL options

### SQL File Processing
- `SQLFileLoader` - Load and process SQL files
- `create_config_template` - Generate configuration templates

### Error Handling
- `DuckalogError` - Base exception class
- `ConfigError` - Configuration-related errors
- `EngineError` - Catalog building errors
- `PathResolutionError` - Path resolution errors
- `RemoteConfigError` - Remote configuration errors
- `SQLFileError` - SQL file processing errors
- `SQLFileNotFoundError` - SQL file not found
- `SQLFilePermissionError` - SQL file permission issues
- `SQLFileEncodingError` - SQL file encoding problems
- `SQLFileSizeError` - SQL file size issues
- `SQLTemplateError` - SQL template processing errors

## Audit Status

| Symbol | Current Status | Needs | Priority |
|--------|----------------|-------|----------|
| `Config` | ✅ Model has docstrings | Example | High |
| `DuckDBConfig` | ✅ Model has docstrings | Example | Medium |
| `AttachmentsConfig` | ✅ Model has docstrings | Example | Medium |
| `DuckDBAttachment` | ✅ Model has docstrings | Example | Medium |
| `SQLiteAttachment` | ✅ Model has docstrings | Example | Medium |
| `PostgresAttachment` | ✅ Model has docstrings | Example | Medium |
| `IcebergCatalogConfig` | ✅ Model has docstrings | Example | Medium |
| `ViewConfig` | ✅ Model has docstrings | Example | High |
| `SecretConfig` | ✅ Model has docstrings | Example | High |
| `load_config` | ⚠️ Basic docstring | Example + Args + Returns | High |
| `validate_generated_config` | ⚠️ Basic docstring | Example + Args + Returns | Medium |
| `ConfigFormat` | ✅ Enum documented | - | Low |
| `build_catalog` | ⚠️ Basic docstring | Example + Args + Returns | High |
| `generate_sql` | ⚠️ Basic docstring | Example + Args + Returns | High |
| `validate_config` | ⚠️ Basic docstring | Example + Args + Returns | High |
| `connect_to_catalog` | ⚠️ Basic docstring | Example + Args + Returns | High |
| `connect_to_catalog_cm` | ⚠️ Basic docstring | Example + Args + Returns | High |
| `connect_and_build_catalog` | ⚠️ Basic docstring | Example + Args + Returns | High |
| `load_config_from_uri` | ⚠️ Basic docstring | Example + Args + Returns | High |
| `generate_all_views_sql` | ⚠️ Basic docstring | Args + Returns | Medium |
| `generate_view_sql` | ⚠️ Basic docstring | Args + Returns | Medium |
| `generate_secret_sql` | ⚠️ Basic docstring | Args + Returns | Medium |
| `quote_ident` | ⚠️ Basic docstring | Args + Returns | Low |
| `quote_literal` | ⚠️ Basic docstring | Args + Returns | Low |
| `render_options` | ⚠️ Basic docstring | Args + Returns | Low |
| `SQLFileLoader` | ⚠️ Basic docstring | Methods documentation | Medium |
| `create_config_template` | ⚠️ Basic docstring | Example + Args + Returns | High |
| `DuckalogError` | ✅ Exception documented | - | Low |
| `ConfigError` | ✅ Exception documented | - | Low |
| `EngineError` | ✅ Exception documented | - | Low |
| `PathResolutionError` | ✅ Exception documented | - | Low |
| `RemoteConfigError` | ✅ Exception documented | - | Low |
| `SQLFileError` | ✅ Exception documented | - | Low |
| `SQLFileNotFoundError` | ✅ Exception documented | - | Low |
| `SQLFilePermissionError` | ✅ Exception documented | - | Low |
| `SQLFileEncodingError` | ✅ Exception documented | - | Low |
| `SQLFileSizeError` | ✅ Exception documented | - | Low |
| `SQLTemplateError` | ✅ Exception documented | - | Low |

## Google Style Requirements

All docstrings should follow Google style with these sections when applicable:

- **Summary line**: Brief description (required)
- **Args**: Parameters with type and description (for functions)
- **Returns**: Return value with type and description (for functions)
- **Raises**: Exceptions that may be raised (for functions)
- **Examples**: Short, runnable examples (for user-facing functions)

## Priority Focus Areas

1. **High Priority**: Core user-facing functions need examples and complete Args/Returns
2. **Medium Priority**: Models and utilities need Args/Returns  
3. **Low Priority**: Simple utilities and exceptions need basic documentation

## Implementation Phases

1. **Phase 1**: Core functions (load_config, build_catalog, generate_sql, validate_config, connection helpers)
2. **Phase 2**: SQL generation utilities and models
3. **Phase 3**: Error classes and simple utilities