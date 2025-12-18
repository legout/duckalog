# API Reference

This section provides comprehensive API documentation for the Duckalog library, including both the traditional API and new modular architecture patterns with dependency injection support.

## Core API

The main Duckalog API provides convenience functions for common use cases:

::: duckalog

## New Architecture Patterns

### Configuration Loading API
The new `duckalog.config.api` module provides enhanced configuration loading with dependency injection support:

**Key Features:**
- **Dependency Injection**: Custom resolvers and processors
- **Request-Scoped Caching**: Performance optimization for batch operations
- **Enhanced Error Handling**: Better error context and recovery
- **Modular Design**: Clean separation of concerns

**Main Functions:**
- `load_config()`: Enhanced configuration loader with DI support
- `_load_config_from_local_file()`: Core local file loading logic

### Import Resolution Interfaces
The `duckalog.config.resolution` package provides extensible import resolution:

**Key Components:**
- `ImportResolver`: Interface for custom import resolution logic
- `ImportContext`: Tracks state during configuration loading
- `RequestContext`: Aggregates caches for single config load operations
- `request_cache_scope()`: Context manager for performance optimization

### Environment Processing
The `duckalog.config.resolution.env` module provides environment variable processing:

**Key Components:**
- `EnvProcessor`: Interface for custom environment processing
- `DefaultEnvProcessor`: Standard environment variable resolution
- `EnvCache`: Caching for environment variable lookups

## Configuration Models

### Core Models
These models define the structure of Duckalog configuration files:

- **`Config`**: Root configuration container
- **`DuckDBConfig`**: Database settings and pragmas
- **`AttachmentsConfig`**: External database attachments
- **`ViewConfig`**: Individual view definitions
- **`SecretConfig`**: Credential and secret management
- **`IcebergCatalogConfig`**: Iceberg catalog connections

### Advanced Models
Extended models for complex configurations:

- **`SemanticModelConfig`**: Semantic layer definitions
- **`SQLFileReference`**: External SQL file references
- **`SemanticDimensionConfig`**: Semantic dimension definitions
- **`SemanticMeasureConfig`**: Semantic measure definitions

## Import Patterns

### Recommended Modern Imports
```python
# New modular imports (recommended)
from duckalog.config.api import load_config
from duckalog.config.resolution.imports import request_cache_scope
from duckalog.config.resolution.base import ImportResolver, ImportContext
from duckalog.config.resolution.env import EnvProcessor

# Convenience functions (unchanged)
from duckalog import generate_sql, validate_config, connect_to_catalog

# Configuration models
from duckalog.config import Config, DuckDBConfig, ViewConfig
```

### Backward Compatibility
All existing import patterns continue to work without modification:

```python
# Legacy imports (still supported)
from duckalog import load_config  # Re-exports from new location
from duckalog.config import load_config  # Re-exports from new location
```

## Usage Patterns

### Basic Usage (Unchanged)
```python
from duckalog import load_config, build_catalog

# Load configuration
config = load_config("catalog.yaml")

# Build catalog
build_catalog("catalog.yaml")
```

### Advanced Usage with Dependency Injection
```python
from duckalog.config.api import load_config
from duckalog.config.resolution.imports import request_cache_scope
import fsspec

# Custom filesystem
filesystem = fsspec.filesystem("s3", key="...", secret="...")

# Load with custom dependencies
config = load_config(
    "s3://bucket/config.yaml",
    filesystem=filesystem,
    load_dotenv=False
)

# Batch loading with caching
with request_cache_scope() as context:
    configs = [load_config(f) for f in config_files]
```

### Custom Implementation
```python
from duckalog.config.resolution.base import ImportResolver, ImportContext

class CustomResolver(ImportResolver):
    def resolve(self, config_data: dict, context: ImportContext) -> dict:
        # Custom import resolution logic
        return resolved_config
```

## Utility Functions

### Core Functions
- **`load_config`**: Enhanced configuration loading with DI support
- **`build_catalog`**: Build DuckDB catalog from configuration
- **`validate_config`**: Validate configuration without building
- **`generate_sql`**: Generate SQL statements from configuration

### High-Level Convenience Functions
- **`connect_to_catalog`**: Connect to existing DuckDB catalog
- **`connect_to_catalog_cm`**: Context manager for catalog connections
- **`connect_and_build_catalog`**: Build and connect in one operation

## Command Line Interface

### Available Commands
- **`duckalog build`**: Build a DuckDB catalog from a configuration file
- **`duckalog validate`**: Validate a configuration file
- **`duckalog generate-sql`**: Generate SQL statements from a configuration file
- **`duckalog init`**: Initialize new configuration from templates

### Enhanced CLI Features
- **Shared Filesystem Options**: Centralized remote access configuration
- **Context Management**: Automatic filesystem object lifecycle management
- **Error Reporting**: Improved error messages and context

## Error Handling

### Core Exceptions
- **`ConfigError`**: Configuration validation or loading errors
- **`EngineError`**: Catalog building or execution errors

### Import Resolution Exceptions
- **`ImportError`**: General import resolution failures
- **`ImportFileNotFoundError`**: Imported file not found
- **`CircularImportError`**: Circular dependency detected
- **`ImportValidationError`**: Import content validation failures

### Path Security Exceptions
- **`PathResolutionError`**: Path security validation failures
- **`SQLFileError`**: SQL file processing errors
- **`SQLFileNotFoundError`**: SQL file not found
- **`SQLFilePermissionError`**: Permission denied for SQL file

## Performance Features

### Caching Architecture
- **Request-Scoped Caching**: Shared resolution across multiple loads
- **Import Resolution Caching**: Avoid re-processing imports
- **Environment Variable Caching**: Reuse resolved values
- **Path Resolution Caching**: Cache normalized paths

### Memory Management
- **Automatic Cache Cleanup**: Context-managed cache clearing
- **Import Chain Tracking**: Efficient circular dependency detection
- **Lightweight Context Objects**: Minimal overhead for tracking

## Security Features

### Enhanced Path Security
- **Rooted Resolution**: All paths relative to config location
- **Traversal Protection**: Prevent directory traversal attacks
- **Cross-Platform Support**: Consistent behavior across systems
- **Remote URI Support**: Secure handling of remote configurations

### Secret Management
- **Environment Variable Integration**: Secure credential handling
- **Automatic Redaction**: Sensitive data protection in logs
- **DuckDB Integration**: Direct mapping to CREATE SECRET statements

## Advanced Usage

### For detailed examples and advanced usage patterns, see:

- **[User Guide](../guides/index.md)**: Comprehensive usage documentation
- **[Examples](../examples/index.md)**: Real-world configuration examples
- **[Migration Guide](../how-to/migration.md)**: Migrate from legacy patterns
- **[Architecture Documentation](../explanation/architecture.md)**: Deep dive into system design

### Extensibility

- **Custom Import Resolvers**: Implement custom import loading logic
- **Custom Environment Processors**: Add specialized environment handling
- **Custom Filesystem Integration**: Support new protocols and backends
- **Plugin Architecture**: Extensible design for new features