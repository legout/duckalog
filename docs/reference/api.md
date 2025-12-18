# API Reference

This reference provides comprehensive documentation for the Duckalog Python API, including the new modular architecture patterns, dependency injection interfaces, and advanced usage patterns.

## Core API Overview

The main API provides both simple convenience functions and advanced patterns for custom implementations:

::: duckalog

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

