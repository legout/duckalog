# API Reference

This reference provides comprehensive documentation for the Duckalog Python API, including the new modular architecture patterns, dependency injection interfaces, and advanced usage patterns.

## Core API Overview

The main API provides both simple convenience functions and advanced patterns for custom implementations. With the new config-driven connection management system, the primary API now returns a `CatalogConnection` object for intelligent connection management.

### Core Functions

#### New: connect_to_catalog()

The primary function for connecting to catalogs with intelligent connection management:

```python
from duckalog import connect_to_catalog

# Basic usage - returns CatalogConnection object
conn = connect_to_catalog("catalog.yaml")

# Use as context manager for automatic cleanup
with connect_to_catalog("catalog.yaml") as conn:
    # conn is a CatalogConnection object
    result = conn.execute("SELECT COUNT(*) FROM users").fetchall()

# Force rebuild of all views
conn = connect_to_catalog("catalog.yaml", force_rebuild=True)

# Custom database path
conn = connect_to_catalog("catalog.yaml", db_path="custom.duckdb")
```

#### Key Features of CatalogConnection

- **Automatic Connection Management**: Handles connection pooling and reuse
- **Session State Restoration**: Automatically restores pragmas, settings, and attachments
- **Incremental Updates**: Only creates missing views for faster builds
- **Lazy Connection**: Database connection established only when needed
- **Context Manager Support**: Automatic cleanup when used with `with` statement

#### Legacy: connect_to_catalog_cm()

For backward compatibility, the context manager function still works:

```python
from duckalog import connect_to_catalog_cm

# Old style (still supported for compatibility)
with connect_to_catalog_cm("catalog.yaml") as conn:
    # conn is raw DuckDB connection (legacy behavior)
    result = conn.execute("SELECT * FROM users").fetchall()
```

### Legacy Functions

All existing functions continue to work but are deprecated in favor of the new connection management approach:

```python
from duckalog import (
    generate_sql,           # Generate SQL from config
    validate_config,        # Validate configuration
    connect_and_build_catalog,  # Legacy build + connect
)
```

::: duckalog

## New Connection Management Architecture

### CatalogConnection Class

The new `CatalogConnection` class is the primary interface for working with Duckalog catalogs. It provides intelligent connection management and session state restoration.

```python
from duckalog import connect_to_catalog

# Create connection
conn = connect_to_catalog("catalog.yaml")

# The connection manages:
# - Automatic catalog building
# - Connection pooling and reuse
# - Session state restoration
# - Incremental view updates
```

#### Key Methods

```python
# Execute SQL (returns DuckDB result)
result = conn.execute("SELECT * FROM users")

# Get raw DuckDB connection when needed
duckdb_conn = conn.get_connection()

# Force rebuild catalog
conn.rebuild_catalog()

# Check if connection is ready
is_ready = conn.is_ready()

# Get catalog metadata
metadata = conn.get_metadata()
```

#### Context Manager Usage

```python
# Recommended usage pattern
with connect_to_catalog("catalog.yaml") as conn:
    # Connection automatically managed
    # Pragmas, settings, and attachments restored
    # Cleanup performed on exit
    
    result = conn.execute("SELECT COUNT(*) FROM users").fetchone()
    print(f"Total users: {result[0]}")

# Connection automatically cleaned up
```

#### Session State Features

```python
with connect_to_catalog("catalog.yaml") as conn:
    # Session state is automatically restored:
    # - DuckDB pragmas
    # - Session settings  
    # - Database attachments
    # - Persistent secrets
    # - Custom functions
    
    # All views are available
    for table in conn.execute("SHOW TABLES").fetchall():
        print(f"Available view: {table[0]}")
```

## New Architecture Patterns

### Configuration Loading with Dependency Injection

The new `load_config()` function from `duckalog.config.api` provides enhanced configuration loading with dependency injection support:

```python
from duckalog.config.api import load_config

# Basic usage (same as before)
config = load_config("catalog.yaml")

# Advanced usage with custom dependencies
config = load_config(
    "catalog.yaml",
    sql_file_loader=custom_loader,
    filesystem=custom_fs,
    load_dotenv=False
)
```

### Request-Scoped Caching Context

The new architecture provides request-scoped caching for performance optimization:

```python
from duckalog.config.resolution.imports import request_cache_scope

# Use request context for caching
with request_cache_scope() as context:
    # All config loading within this scope shares caches
    config1 = load_config("config1.yaml")
    config2 = load_config("config2.yaml")  # Reuses resolved imports
```

## Import Patterns

### Recommended Import Patterns

```python
# New modular imports (recommended)
from duckalog.config.api import load_config
from duckalog.config.resolution.imports import request_cache_scope
from duckalog.config.resolution.base import ImportResolver, ImportContext
from duckalog.config.resolution.env import EnvProcessor, DefaultEnvProcessor

# High-level convenience functions (unchanged)
from duckalog import (
    generate_sql,
    validate_config,
    connect_to_catalog,
    connect_to_catalog_cm,
    connect_and_build_catalog,
)

# Configuration models
from duckalog.config import (
    Config,
    DuckDBConfig,
    AttachmentsConfig,
    ViewConfig,
    SecretConfig,
)
```

### Backward Compatibility Imports

All existing import patterns continue to work:

```python
# Legacy imports (still supported)
from duckalog import load_config  # Re-exports from config.api
from duckalog.config import load_config  # Re-exports from config.api

# Direct module imports
from duckalog.config.api import load_config  # New location
```

## Advanced Usage Examples

### Custom Dependency Injection

```python
from duckalog.config.resolution.base import ImportResolver, ImportContext
from duckalog.config.resolution.imports import DefaultImportResolver

# Create custom resolver
class CustomImportResolver(ImportResolver):
    def __init__(self, custom_config):
        self.custom_config = custom_config
    
    def resolve(self, config_data: dict, context: ImportContext) -> dict:
        # Custom import resolution logic
        return resolved_config

# Use with load_config
with request_cache_scope() as request_context:
    resolver = CustomImportResolver(custom_config)
    # Integrate with the loading process
```

### Connection Management Patterns

```python
from duckalog import connect_to_catalog

# Pattern 1: Single connection with multiple queries
conn = connect_to_catalog("catalog.yaml")
users = conn.execute("SELECT * FROM users").fetchall()
orders = conn.execute("SELECT * FROM orders").fetchall()

# Pattern 2: Context manager for automatic cleanup
with connect_to_catalog("catalog.yaml") as conn:
    # Process data with automatic connection management
    results = conn.execute("""
        SELECT u.username, COUNT(o.order_id) as order_count
        FROM users u
        LEFT JOIN orders o ON u.user_id = o.user_id
        GROUP BY u.username
    """).fetchall()

# Pattern 3: Multiple connections with connection pooling
with connect_to_catalog("analytics.yaml") as analytics_conn:
    with connect_to_catalog("warehouse.yaml") as warehouse_conn:
        # Both connections managed independently
        analytics_data = analytics_conn.execute("SELECT * FROM metrics").fetchall()
        warehouse_data = warehouse_conn.execute("SELECT * FROM inventory").fetchall()
```

### Performance Optimization

```python
# Incremental builds - only missing views created
conn = connect_to_catalog("catalog.yaml")  # Fast for subsequent runs

# Force rebuild when needed
conn = connect_to_catalog("catalog.yaml", force_rebuild=True)

# Connection reuse across operations
with connect_to_catalog("catalog.yaml") as conn:
    # Reuse same connection for multiple queries
    metadata = conn.get_metadata()  # Cached connection
    results = conn.execute("COMPLEX_QUERY").fetchall()
    # Connection reused, no reconnection overhead
```

### Custom Filesystem Implementations

```python
import fsspec
from duckalog import load_config

# Create custom filesystem
custom_fs = fsspec.filesystem(
    "myprotocol",
    key="access-key",
    secret="secret-key"
)

# Load config with custom filesystem
config = load_config(
    "myprotocol://bucket/config.yaml",
    filesystem=custom_fs
)

# Use with new connection management
from duckalog import connect_to_catalog
conn = connect_to_catalog(
    "myprotocol://bucket/config.yaml",
    filesystem=custom_fs
)
```

### Performance Optimization with Caching

```python
from duckalog.config.resolution.imports import request_cache_scope
from duckalog.config.api import load_config

# Batch load configurations efficiently
configs = []
with request_cache_scope() as context:
    for config_file in config_files:
        config = load_config(config_file)
        configs.append(config)
    # All configs share resolved imports and environment variables
```

### Custom Environment Processing

```python
from duckalog.config.resolution.env import EnvProcessor, DefaultEnvProcessor

class CustomEnvProcessor(EnvProcessor):
    def process(self, config_data: dict, load_dotenv: bool = True) -> dict:
        # Custom environment variable processing
        # e.g., add custom prefixes, special handling
        return processed_config

# Use with custom environment processor
env_processor = CustomEnvProcessor()
```

## Migration from Old Patterns

### From Legacy load_config

```python
# Old pattern (still works)
from duckalog import load_config
config = load_config("config.yaml")

# New pattern with same interface
from duckalog.config.api import load_config
config = load_config("config.yaml")

# New pattern with additional options
config = load_config(
    "config.yaml",
    resolve_paths=True,
    filesystem=custom_fs,
    load_dotenv=False
)
```

### Custom Implementation Patterns

```python
# For extending the configuration system
from duckalog.config.resolution.base import ImportResolver, ImportContext
from duckalog.config.api import _load_config_from_local_file

class MyCustomResolver(ImportResolver):
    def resolve(self, config_data: dict, context: ImportContext) -> dict:
        # Your custom logic here
        return config_data

# Use in custom loading scenarios
def my_custom_loader(path: str, **kwargs):
    return _load_config_from_local_file(
        path=path,
        sql_file_loader=kwargs.get("sql_file_loader"),
        resolve_paths=kwargs.get("resolve_paths", True),
        filesystem=kwargs.get("filesystem"),
        load_dotenv=kwargs.get("load_dotenv", True),
    )
```

## Configuration Models

### Core Models

The configuration models are now organized in the `duckalog.config` package:

::: duckalog.config.models

### Import Resolution Models

::: duckalog.config.resolution.base

### Environment Processing Models

::: duckalog.config.resolution.env

## Error Handling

The new architecture provides enhanced error handling with specific exception types:

### Configuration Errors

::: duckalog.errors

### Import Resolution Errors

::: duckalog.config.resolution.imports

## Performance Considerations

### Caching Benefits

- **Request-Scoped Caching**: Shared resolution across multiple config loads
- **Import Resolution Caching**: Avoid re-processing the same imports
- **Environment Variable Caching**: Reuse resolved environment values
- **Path Resolution Caching**: Cache normalized paths for reuse

### Memory Management

- **Automatic Cache Cleanup**: Request scopes automatically clear caches
- **Import Chain Tracking**: Prevent circular dependencies with minimal overhead
- **Efficient Context Management**: Lightweight context objects for tracking

## Security Features

### Enhanced Path Security

The new architecture maintains and enhances the existing security features:

- **Relative Path Resolution**: All paths resolved relative to config location
- **Security Boundary Validation**: Prevent directory traversal attacks
- **Cross-Platform Support**: Consistent behavior across operating systems
- **Remote URI Support**: Secure handling of remote configuration sources

### Dependency Injection Security

- **Controlled Interface**: Safe injection points for custom implementations
- **Validation Integration**: Custom resolvers participate in validation
- **Context Isolation**: Each request maintains isolated state
- **Audit Trail**: Track configuration resolution through contexts

## Testing Support

### Mockable Interfaces

All new interfaces are designed for easy testing:

```python
from unittest.mock import Mock
from duckalog.config.resolution.base import ImportResolver

# Create mock resolver for testing
mock_resolver = Mock(spec=ImportResolver)
mock_resolver.resolve.return_value = test_config

# Test with mocked dependencies
with request_cache_scope() as context:
    # Use mock resolver in tests
    pass
```

### Test Utilities

```python
# Test with temporary configurations
from tempfile import NamedTemporaryFile
from duckalog.config.api import load_config

with NamedTemporaryFile(mode='w', suffix='.yaml') as f:
    f.write(test_config_content)
    f.flush()
    config = load_config(f.name)
```

## Extensibility Points

### Custom Import Resolvers

Extend the import resolution system:

```python
class DatabaseImportResolver(ImportResolver):
    """Load imports from database instead of files."""
    
    def resolve(self, config_data: dict, context: ImportContext) -> dict:
        # Implement database-based import loading
        pass
```

### Custom Environment Processors

Add custom environment handling:

```python
class VaultEnvProcessor(EnvProcessor):
    """Load secrets from vault systems."""
    
    def process(self, config_data: dict, load_dotenv: bool = True) -> dict:
        # Implement vault integration
        pass
```

### Custom Filesystem Integration

Add support for new protocols:

```python
class CustomFilesystem:
    """Custom filesystem implementation."""
    
    def open(self, path, mode='r'):
        # Implement custom file access
        pass
```

