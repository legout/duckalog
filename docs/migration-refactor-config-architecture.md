# Migration Guide: Configuration Architecture Refactor

This guide helps developers migrate from the monolithic `loader.py` architecture to the new modular configuration architecture. The refactoring improves maintainability, eliminates circular dependencies, and introduces dependency injection patterns while maintaining 100% backward compatibility.

## Table of Contents

1. [What Changed](#what-changed)
2. [Migration Paths](#migration-paths)
3. [Before/After Examples](#beforeafter-examples)
4. [Step-by-Step Migration](#step-by-step-migration)
5. [Testing Migration](#testing-migration)
6. [Rollback Strategy](#rollback-strategy)
7. [FAQ](#faq)

---

## What Changed

### Overview of Architectural Refactoring

The configuration system has been restructured from a monolithic 1670-line `loader.py` module into focused, single-responsibility modules:

#### Old Architecture
```
config/
├── loader.py          # 1670 lines - handled everything
├── __init__.py        # Re-exports and utilities
├── models.py          # Pydantic models
├── interpolation.py   # Environment variable processing
└── validators.py      # Path validation and utilities
```

#### New Architecture
```
config/
├── api.py             # Public API orchestration layer
├── loading/           # File and remote loading adapters
│   ├── __init__.py
│   ├── base.py        # Abstract base classes
│   ├── file.py        # Local file loading
│   ├── remote.py      # Remote URI loading
│   └── sql.py         # SQL file loading
├── resolution/        # Path and import resolution
│   ├── __init__.py
│   ├── base.py        # Abstract base classes and protocols
│   ├── env.py         # Environment variable processing
│   └── imports.py     # Import resolution logic
├── security/          # Path validation and security
│   ├── __init__.py
│   ├── base.py        # Abstract security classes
│   └── path.py        # Path security implementation
├── __init__.py        # Backward-compatible re-exports
├── models.py          # Pydantic models (unchanged)
├── interpolation.py   # Legacy compatibility
└── validators.py      # Legacy compatibility
└── loader.py          # Legacy compatibility (deprecated)
```

### Why the Changes Were Made

1. **Eliminated Circular Dependencies**: Removed circular import between `config/__init__.py` and `remote_config.py`
2. **Single Responsibility Principle**: Each module now has a focused, well-defined responsibility
3. **Improved Testability**: Dependency injection enables better mocking and testing
4. **Enhanced Extensibility**: Abstract base classes allow custom implementations
5. **Performance Optimizations**: Request-scoped caching reduces redundant operations
6. **Maintainability**: Clearer boundaries make the code easier to understand and modify

### Timeline and Compatibility

- **Phase 1** (Complete): New modular structure implemented alongside legacy code
- **Phase 2** (Current): Full backward compatibility maintained with deprecation warnings
- **Phase 3** (Future): Legacy code will be removed in a major version release
- **Migration Window**: 2-3 releases with gradual deprecation warnings

---

## Migration Paths

### No Changes Needed - What Continues Unchanged

The following patterns continue to work without any modifications:

#### 1. Standard Configuration Loading
```python
# Continues to work exactly as before
from duckalog.config import load_config, Config

config = load_config("catalog.yaml")
print(config.version)
print(len(config.views))
```

#### 2. Path Resolution Utilities
```python
# All existing imports and functions work unchanged
from duckalog.config import (
    is_relative_path,
    resolve_relative_path,
    validate_path_security,
)

if is_relative_path("./data/file.parquet"):
    abs_path = resolve_relative_path("./data/file.parquet")
    validate_path_security(abs_path)
```

#### 3. Basic Usage in Python API
```python
# High-level API calls work unchanged
from duckalog import generate_sql, validate_config

sql = generate_sql("catalog.yaml")
validate_config("catalog.yaml")
```

### Recommended Updates - What to Update for Better Performance

#### 1. Use New Dependency Injection Patterns
```python
# Old approach (still works)
from duckalog.config import load_config
config = load_config("catalog.yaml")

# New approach (recommended for custom implementations)
from duckalog.config.api import load_config as api_load_config
from duckalog.config.loading import ConfigLoader
from duckalog.config.resolution import ImportResolver

class MyCustomLoader(ConfigLoader):
    def load(self, path, filesystem=None):
        # Custom loading logic
        return custom_config_data

config = api_load_config(
    "catalog.yaml",
    filesystem=custom_filesystem,
    import_resolver=custom_resolver
)
```

#### 2. Leverage Request-Scoped Caching
```python
# Old approach (no explicit caching control)
from duckalog.config import load_config
config1 = load_config("catalog.yaml")
config2 = load_config("catalog.yaml")  # Loads again

# New approach (explicit caching scope)
from duckalog.config.resolution.imports import request_cache_scope

with request_cache_scope():
    config1 = load_config("catalog.yaml")
    config2 = load_config("catalog.yaml")  # Uses cache within scope
```

#### 3. Use Abstract Base Classes for Extensions
```python
# New: Implement custom filesystem with proper interface
from duckalog.config.loading.base import SQLFileLoader
from duckalog.config.security.base import PathValidator

class SecureSQLLoader(SQLFileLoader):
    def load_sql(self, path, filesystem=None):
        # Custom secure SQL loading
        return secure_sql_content

class StrictPathValidator(PathValidator):
    def validate(self, path):
        # Custom strict validation
        if not self.is_allowed_path(path):
            raise SecurityError(f"Path not allowed: {path}")
```

### Breaking Changes - Actual Breaking Changes

**There are currently no breaking changes.** All existing code continues to work unchanged. The following will change in a future major version:

#### Future Breaking Changes (Planned)
```python
# These imports will be deprecated and eventually removed:
from duckalog.config.loader import *  # Will be removed
from duckalog.config.interpolation import *  # Will be removed

# Use these instead:
from duckalog.config.resolution.env import *
from duckalog.config.loading import *
```

---

## Before/After Examples

### Import Patterns

#### Old Import Patterns (Still Work)
```python
# Direct imports from old modules
from duckalog.config.loader import _load_config_from_local_file
from duckalog.config.interpolation import _interpolate_env
from duckalog.config.validators import log_info, log_debug

# Public API imports (unchanged)
from duckalog.config import load_config, Config, ConfigError
```

#### New Import Patterns (Recommended)
```python
# Use the new modular structure
from duckalog.config.api import load_config
from duckalog.config.resolution.env import DefaultEnvProcessor
from duckalog.config.loading.base import ConfigLoader, SQLFileLoader
from duckalog.config.security.base import PathValidator

# Abstract base classes for extensions
from duckalog.config.resolution.base import ImportResolver, ImportContext
from duckalog.config.loading.base import ConfigLoader, SQLFileLoader
```

### Custom Implementation Examples

#### Old Custom Filesystem Implementation
```python
# Old approach: Monkey patching and internal access
from duckalog.config.loader import _load_config_from_local_file

class CustomFilesystem:
    def open(self, path, mode='r'):
        # Custom filesystem logic
        pass

# Use via internal function (fragile)
config = _load_config_from_local_file(
    "catalog.yaml",
    filesystem=CustomFilesystem()
)
```

#### New Custom Filesystem Implementation
```python
# New approach: Clean dependency injection
from duckalog.config.api import load_config
from duckalog.config.loading.base import ConfigLoader
from duckalog.config.resolution.base import ImportResolver

class S3ConfigLoader(ConfigLoader):
    def __init__(self, s3_client):
        self.s3_client = s3_client
    
    def load(self, path, filesystem=None):
        # Clean S3 loading implementation
        bucket, key = self._parse_s3_path(path)
        content = self.s3_client.get_object(Bucket=bucket, Key=key)['Body'].read()
        return yaml.safe_load(content)

class CustomImportResolver(ImportResolver):
    def __init__(self, config_loader):
        self.config_loader = config_loader
    
    def resolve(self, config_data, context):
        # Custom import resolution logic
        return resolved_config

# Clean usage
s3_loader = S3ConfigLoader(s3_client)
custom_resolver = CustomImportResolver(s3_loader)

config = load_config(
    "s3://my-bucket/config.yaml",
    filesystem=s3_loader,
    import_resolver=custom_resolver
)
```

### Testing Examples

#### Old Testing Pattern
```python
# Old approach: Mock internal functions
from unittest.mock import patch
from duckalog.config.loader import _load_config_from_local_file

@patch('duckalog.config.loader._resolve_paths_in_config')
def test_config_loading(mock_resolve):
    mock_resolve.return_value = resolved_config
    config = _load_config_from_local_file("test.yaml")
    assert config is not None
```

#### New Testing Pattern
```python
# New approach: Use dependency injection for clean testing
from unittest.mock import Mock
from duckalog.config.api import load_config
from duckalog.config.loading.base import ConfigLoader

class MockConfigLoader(ConfigLoader):
    def __init__(self, mock_data):
        self.mock_data = mock_data
    
    def load(self, path, filesystem=None):
        return self.mock_data

def test_config_loading_with_di():
    mock_loader = MockConfigLoader({"version": 1, "views": []})
    
    config = load_config("any-path.yaml", filesystem=mock_loader)
    assert config.version == 1
    assert len(config.views) == 0
```

---

## Step-by-Step Migration

### Step 1: Adopt New Import Patterns (Optional)

Gradually update imports to use the new modular structure:

```python
# Step 1a: Update new code to use new imports
# Instead of:
# from duckalog.config.loader import _load_config_from_local_file

# Use:
from duckalog.config.api import load_config

# Step 1b: For extensions, use abstract base classes
from duckalog.config.loading.base import ConfigLoader, SQLFileLoader
from duckalog.config.resolution.base import ImportResolver
```

### Step 2: Implement Custom Filesystems with New Patterns

If you have custom filesystem implementations:

```python
# Step 2a: Create a class that implements ConfigLoader
from duckalog.config.loading.base import ConfigLoader

class MyCustomFilesystem(ConfigLoader):
    def load(self, path, filesystem=None):
        # Your custom loading logic
        return config_data
    
    def open(self, path, mode='r'):
        # File-like interface implementation
        pass

# Step 2b: Use it with the new API
from duckalog.config.api import load_config

my_fs = MyCustomFilesystem()
config = load_config("my-path.yaml", filesystem=my_fs)
```

### Step 3: Use Request-Scoped Caching for Performance

For applications that load multiple configs:

```python
# Step 3a: Wrap related operations in cache scope
from duckalog.config.resolution.imports import request_cache_scope

with request_cache_scope():
    config1 = load_config("base.yaml")
    config2 = load_config("views.yaml")  # Shares cache with config1
    config3 = load_config("analytics.yaml")  # Shares cache

# Step 3b: For custom resolvers, respect the cache context
class CachedImportResolver(ImportResolver):
    def resolve(self, config_data, context):
        # Use context.import_context.config_cache for caching
        cache_key = self._get_cache_key(config_data)
        
        if cache_key in context.import_context.config_cache:
            return context.import_context.config_cache[cache_key]
        
        resolved = self._do_resolve(config_data)
        context.import_context.config_cache[cache_key] = resolved
        return resolved
```

### Step 4: Implement Custom Security Validation

For enhanced security requirements:

```python
# Step 4a: Implement custom path validator
from duckalog.config.security.base import PathValidator

class StrictSecurityValidator(PathValidator):
    def __init__(self, allowed_paths, blocked_patterns):
        self.allowed_paths = allowed_paths
        self.blocked_patterns = blocked_patterns
    
    def validate(self, path):
        # Custom security logic
        path_str = str(path)
        
        # Check blocked patterns
        for pattern in self.blocked_patterns:
            if pattern in path_str:
                raise SecurityError(f"Path blocked by pattern: {pattern}")
        
        # Check allowed paths
        if not any(path_str.startswith(allowed) for allowed in self.allowed_paths):
            raise SecurityError(f"Path not in allowed list: {path_str}")

# Step 4b: Use with config loading
from duckalog.config.api import load_config

validator = StrictSecurityValidator(
    allowed_paths=["/safe/data/", "/config/"],
    blocked_patterns=["..", "/etc/", "/var/"]
)

config = load_config(
    "config.yaml",
    path_validator=validator
)
```

### Step 5: Update Custom Environment Processing

For specialized environment variable handling:

```python
# Step 5a: Implement custom environment processor
from duckalog.config.resolution.base import EnvProcessor
from duckalog.config.resolution.env import EnvCache

class CustomEnvProcessor(EnvProcessor):
    def __init__(self, custom_mappings=None):
        self.custom_mappings = custom_mappings or {}
        self.cache = EnvCache()
    
    def process(self, config_data, load_dotenv=True):
        # Custom environment processing logic
        processed = config_data.copy()
        
        # Apply custom mappings
        for key, value in self.custom_mappings.items():
            if key in processed:
                processed[key] = self._substitute_vars(value)
        
        return processed

# Step 5b: Use with config loading
from duckalog.config.api import load_config

env_processor = CustomEnvProcessor({
    "database": "${DB_NAME}_${ENVIRONMENT}",
    "cache_dir": "/tmp/${PROJECT_NAME}/cache"
})

config = load_config(
    "config.yaml",
    env_processor=env_processor
)
```

---

## Testing Migration

### Update Tests for New Architecture

#### 1. Mock Dependency Injection
```python
# Old testing approach
from unittest.mock import patch
@patch('duckalog.config.loader._load_yaml_file')
def test_old_style(mock_load):
    mock_load.return_value = {"version": 1}
    # Test logic...

# New testing approach
from unittest.mock import Mock
from duckalog.config.api import load_config
from duckalog.config.loading.base import ConfigLoader

def test_new_style():
    mock_loader = Mock(spec=ConfigLoader)
    mock_loader.load.return_value = {"version": 1}
    
    config = load_config("any-path.yaml", filesystem=mock_loader)
    assert config.version == 1
```

#### 2. Test Custom Implementations
```python
# Test custom filesystem implementation
class TestCustomFilesystem:
    def test_custom_loader_integration(self):
        from duckalog.config.loading.base import ConfigLoader
        from duckalog.config.api import load_config
        
        class TestLoader(ConfigLoader):
            def load(self, path, filesystem=None):
                return {"version": 1, "views": []}
        
        loader = TestLoader()
        config = load_config("test.yaml", filesystem=loader)
        
        assert config.version == 1
        assert len(config.views) == 0
```

#### 3. Test Caching Behavior
```python
# Test request-scoped caching
def test_caching_behavior():
    from duckalog.config.resolution.imports import request_cache_scope
    from unittest.mock import Mock, call
    
    mock_loader = Mock()
    mock_loader.load.return_value = {"version": 1}
    
    with request_cache_scope():
        load_config("test.yaml", filesystem=mock_loader)
        load_config("test.yaml", filesystem=mock_loader)  # Should use cache
    
    # Should only be called once due to caching
    assert mock_loader.load.call_count == 1
```

#### 4. Test Security Features
```python
# Test custom security validation
def test_security_validation():
    from duckalog.config.security.base import PathValidator
    from duckalog.config.api import load_config
    
    class TestValidator(PathValidator):
        def validate(self, path):
            if "../../../etc/passwd" in str(path):
                raise SecurityError("Path traversal detected")
    
    validator = TestValidator()
    
    with pytest.raises(SecurityError):
        load_config("../../../etc/passwd", path_validator=validator)
```

### Performance Testing with Caching

```python
# Benchmark caching performance
import time
from duckalog.config.resolution.imports import request_cache_scope

def benchmark_cached_vs_uncached():
    # Test without caching
    start = time.time()
    for i in range(100):
        config = load_config("complex-config.yaml")
    uncached_time = time.time() - start
    
    # Test with caching
    start = time.time()
    with request_cache_scope():
        for i in range(100):
            config = load_config("complex-config.yaml")
    cached_time = time.time() - start
    
    print(f"Uncached: {uncached_time:.2f}s")
    print(f"Cached: {cached_time:.2f}s")
    print(f"Speedup: {uncached_time/cached_time:.1f}x")
```

---

## Rollback Strategy

### Temporary Revert Options

If you encounter issues with the new architecture, you have several rollback options:

#### 1. Use Legacy Import Paths
```python
# Fall back to legacy imports if needed
from duckalog.config.loader import _load_config_from_local_file
from duckalog.config.interpolation import _interpolate_env

# This will continue to work until the major version change
config = _load_config_from_local_file("catalog.yaml")
```

#### 2. Environment Variable for Legacy Mode
```python
# Set environment variable to use legacy implementation (if available)
import os
os.environ['DUCKALOG_USE_LEGACY_CONFIG'] = 'true'

from duckalog.config import load_config
config = load_config("catalog.yaml")  # Will use legacy implementation
```

#### 3. Direct Module Import
```python
# Import directly from legacy modules
import duckalog.config.loader as legacy_loader
config = legacy_loader.load_config_from_file("catalog.yaml")
```

### Feature Flags for Gradual Migration

```python
# Use feature flags to control migration
class ConfigMigrationManager:
    def __init__(self):
        self.use_new_architecture = os.getenv('USE_NEW_CONFIG_ARCH', 'false').lower() == 'true'
        self.enable_caching = os.getenv('ENABLE_CONFIG_CACHE', 'false').lower() == 'true'
    
    def load_config(self, path, **kwargs):
        if self.use_new_architecture:
            from duckalog.config.api import load_config as new_load
            
            if self.enable_caching:
                from duckalog.config.resolution.imports import request_cache_scope
                with request_cache_scope():
                    return new_load(path, **kwargs)
            else:
                return new_load(path, **kwargs)
        else:
            from duckalog.config import load_config as legacy_load
            return legacy_load(path, **kwargs)

# Usage
migration_manager = ConfigMigrationManager()
config = migration_manager.load_config("catalog.yaml")
```

### Compatibility Layers

```python
# Create compatibility layer for smooth transition
class CompatibilityLayer:
    @staticmethod
    def load_config_with_fallback(path, **kwargs):
        try:
            # Try new architecture first
            from duckalog.config.api import load_config
            return load_config(path, **kwargs)
        except Exception as e:
            # Fall back to legacy if new fails
            import warnings
            warnings.warn(f"New config architecture failed: {e}. Falling back to legacy.", 
                        DeprecationWarning)
            
            from duckalog.config import load_config as legacy_load
            return legacy_load(path, **kwargs)

# Usage
config = CompatibilityLayer.load_config_with_fallback("catalog.yaml")
```

---

## FAQ

### Common Questions About the Migration

#### Q: Do I need to update my existing code?
**A:** No. All existing code continues to work unchanged. The migration is optional for now, and you can gradually adopt new patterns when you're ready.

#### Q: Will there be performance improvements?
**A:** Yes, the new architecture includes request-scoped caching that can significantly improve performance for applications that load multiple configurations or handle complex import chains.

#### Q: What are the benefits of dependency injection?
**A:** Dependency injection makes your code more testable, enables better mocking, allows custom implementations, and reduces coupling between components.

#### Q: Can I still use internal functions like `_load_config_from_local_file`?
**A:** Yes, these functions are still available for backward compatibility, but they are deprecated and will be removed in a future major version.

#### Q: How do I implement custom filesystems now?
**A:** Implement the `ConfigLoader` abstract base class from `duckalog.config.loading.base` and pass it to `load_config()` via the `filesystem` parameter.

#### Q: What happened to the circular dependency issues?
**A:** The circular dependency between `config/__init__.py` and `remote_config.py` has been eliminated by moving remote URI detection to a separate utility module.

#### Q: Can I still use environment variable interpolation?
**A:** Yes, environment variable interpolation continues to work exactly as before. The new architecture provides the `EnvProcessor` protocol for custom environment processing if needed.

#### Q: How does request-scoped caching work?
**A:** The cache is active only within a specific load operation context and is cleared afterward, preventing memory leaks while improving performance for related operations.

#### Q: Are there any breaking changes in this release?
**A:** No, there are no breaking changes in this release. All changes are additive and maintain full backward compatibility.

#### Q: When will the legacy code be removed?
**A:** Legacy code will be removed in a future major version release, with deprecation warnings starting in the next minor version.

### Troubleshooting Migration Issues

#### Issue: Import Error for New Modules
**Problem:** `ImportError: No module named 'duckalog.config.loading'`

**Solution:** Ensure you're using the latest version of Duckalog. The new module structure is available in version X.X.X and later.

#### Issue: Custom Filesystem Not Working
**Problem:** Custom filesystem implementation not being called

**Solution:** Make sure your custom filesystem implements the `ConfigLoader` interface:
```python
from duckalog.config.loading.base import ConfigLoader

class MyFilesystem(ConfigLoader):
    def load(self, path, filesystem=None):
        # Your implementation
        pass
```

#### Issue: Caching Not Working
**Problem:** Performance not improving with caching

**Solution:** Ensure you're using the `request_cache_scope` context manager:
```python
from duckalog.config.resolution.imports import request_cache_scope

with request_cache_scope():
    config1 = load_config("file1.yaml")
    config2 = load_config("file2.yaml")  # Will share cache
```

#### Issue: Security Validation Errors
**Problem:** Getting security validation errors for valid paths

**Solution:** Check if you're using a custom path validator that might be too restrictive. The default security validation should work for most use cases.

#### Issue: Performance Regression
**Problem:** New architecture is slower than expected

**Solution:** Enable request-scoped caching and ensure you're not unnecessarily re-instantiating custom loaders or validators.

#### Issue: Circular Dependency Errors
**Problem:** Still seeing circular dependency warnings

**Solution:** This should not happen with the new architecture. If you see this, ensure you're not mixing old and new import patterns in a way that recreates the circular dependency.

### Getting Help

If you encounter issues during migration:

1. **Check the documentation**: Review the latest documentation for updated examples
2. **Search existing issues**: Check if someone else has encountered similar problems
3. **Create a minimal example**: Create a simple test case that demonstrates the issue
4. **Include version information**: Specify which version of Duckalog you're using
5. **Provide error traces**: Include full stack traces and error messages

---

## Next Steps

After completing your migration:

1. **Monitor performance**: Use the new caching features to optimize your application
2. **Clean up legacy imports**: Gradually remove deprecated import patterns
3. **Leverage new features**: Take advantage of dependency injection for better testability
4. **Update documentation**: Document any custom implementations using the new patterns
5. **Plan for future releases**: Prepare for the eventual removal of legacy code

The new architecture provides a solid foundation for future enhancements while maintaining the stability and compatibility that existing users depend on.