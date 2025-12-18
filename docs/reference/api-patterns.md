# API Patterns

This guide covers the new API patterns in Duckalog's modular architecture, including dependency injection, request-scoped caching, and advanced customization options.

## Overview

The new Duckalog architecture provides:

- **Dependency Injection**: Customizable components for configuration loading
- **Request-Scoped Caching**: Performance optimization for batch operations  
- **Modular Design**: Clean separation of concerns with extensible interfaces
- **Backward Compatibility**: All existing patterns continue to work

## Basic vs Advanced Patterns

### Basic Pattern (Recommended for Most Users)

The basic pattern uses the high-level convenience functions:

```python
from duckalog import load_config, build_catalog, generate_sql

# Load configuration (same as before)
config = load_config("catalog.yaml")

# Build catalog (same as before)  
build_catalog("catalog.yaml")

# Generate SQL (same as before)
sql = generate_sql("catalog.yaml")
```

### Advanced Pattern (For Custom Implementations)

The advanced pattern provides fine-grained control over the loading process:

```python
from duckalog.config.api import load_config
from duckalog.config.resolution.imports import request_cache_scope
import fsspec

# Custom filesystem for remote access
filesystem = fsspec.filesystem("s3", key="access_key", secret="secret_key")

# Enhanced configuration loading
config = load_config(
    "s3://bucket/config.yaml",
    filesystem=filesystem,
    load_dotenv=False,
    sql_file_loader=custom_loader
)

# Batch processing with caching
configs = []
with request_cache_scope() as context:
    for config_file in config_files:
        config = load_config(config_file)
        configs.append(config)
```

## Dependency Injection Patterns

### 1. Custom Filesystem Implementation

Create custom filesystem backends for specialized storage systems:

```python
import fsspec
from duckalog.config.api import load_config

# Custom filesystem with special configuration
custom_fs = fsspec.filesystem(
    "myprotocol",
    endpoint="https://my-storage.example.com",
    auth_token="secret-token",
    timeout=30
)

# Use custom filesystem for configuration loading
config = load_config(
    "myprotocol://configs/analytics.yaml",
    filesystem=custom_fs
)
```

### 2. Custom SQL File Loader

Implement custom SQL file loading for specialized template processing:

```python
from typing import Dict, Any
from duckalog.config.api import load_config

class CustomSQLFileLoader:
    """Custom SQL loader with template processing."""
    
    def load_sql_file(self, file_path: str, context: Dict[str, Any]) -> str:
        # Custom template processing logic
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Apply custom template variables
        for key, value in context.items():
            content = content.replace(f"{{{{{key}}}}}", str(value))
        
        return content

# Use with load_config
sql_loader = CustomSQLFileLoader()
config = load_config(
    "catalog.yaml",
    sql_file_loader=sql_loader
)
```

### 3. Custom Environment Processing

Implement custom environment variable resolution:

```python
from duckalog.config.resolution.env import EnvProcessor, DefaultEnvProcessor
from duckalog.config.resolution.base import ImportContext

class VaultEnvProcessor(EnvProcessor):
    """Load environment variables from vault systems."""
    
    def process(self, config_data: dict, load_dotenv: bool = True) -> dict:
        # Process vault-based secrets first
        config_data = self._resolve_vault_secrets(config_data)
        
        # Fall back to standard environment processing
        default_processor = DefaultEnvProcessor()
        return default_processor.process(config_data, load_dotenv)
    
    def _resolve_vault_secrets(self, config_data: dict) -> dict:
        # Implement vault resolution logic
        # e.g., ${vault:secret/path:key} → actual value
        return config_data

# Use with the configuration loading system
env_processor = VaultEnvProcessor()
```

### 4. Custom Import Resolution

Implement specialized import resolution logic:

```python
from duckalog.config.resolution.base import ImportResolver, ImportContext
from duckalog.config.resolution.imports import DefaultImportResolver

class DatabaseImportResolver(ImportResolver):
    """Load configuration imports from database instead of files."""
    
    def __init__(self, db_connection):
        self.db = db_connection
    
    def resolve(self, config_data: dict, context: ImportContext) -> dict:
        imports = config_data.get('imports', [])
        
        for import_spec in imports:
            if isinstance(import_spec, str) and import_spec.startswith('db://'):
                # Load from database: db://table_name/id
                table_name, config_id = import_spec[5:].split('/')
                imported_config = self._load_from_db(table_name, config_id)
                
                # Merge imported configuration
                config_data = self._merge_configs(config_data, imported_config)
        
        # Handle regular file imports with default resolver
        default_resolver = DefaultImportResolver(context.import_context)
        return default_resolver.resolve(config_data, context)
    
    def _load_from_db(self, table_name: str, config_id: str) -> dict:
        query = f"SELECT config_json FROM {table_name} WHERE id = ?"
        cursor = self.db.execute(query, (config_id,))
        result = cursor.fetchone()
        return json.loads(result[0]) if result else {}
    
    def _merge_configs(self, base: dict, imported: dict) -> dict:
        # Implement configuration merging logic
        return {**imported, **base}

# Use with request context
from duckalog.config.resolution.imports import request_cache_scope

with request_cache_scope() as context:
    db_resolver = DatabaseImportResolver(db_connection)
    # Integration would happen through custom loading logic
```

## Request-Scoped Caching Patterns

### 1. Batch Configuration Loading

Efficiently load multiple related configurations:

```python
from duckalog.config.api import load_config
from duckalog.config.resolution.imports import request_cache_scope

def load_catalog_configs(config_files: list[str]) -> list[Config]:
    """Load multiple configurations with shared caching."""
    configs = []
    
    with request_cache_scope() as context:
        for config_file in config_files:
            try:
                config = load_config(config_file)
                configs.append(config)
                print(f"Loaded: {config_file}")
            except Exception as e:
                print(f"Failed to load {config_file}: {e}")
    
    return configs

# Usage
config_files = [
    "base.yaml",
    "analytics/views.yaml", 
    "analytics/attachments.yaml",
    "reports/views.yaml"
]

configs = load_catalog_configs(config_files)
```

### 2. Performance Monitoring

Monitor caching effectiveness:

```python
import time
from duckalog.config.resolution.imports import request_cache_scope, RequestContext

def timed_config_loading(config_files: list[str]) -> dict:
    """Load configurations with performance metrics."""
    metrics = {
        'total_time': 0,
        'configs_loaded': 0,
        'cache_hits': 0,
        'cache_misses': 0
    }
    
    start_time = time.time()
    
    with request_cache_scope() as context:
        # Track cache statistics
        initial_imports = len(context.import_context.visited_files)
        
        for config_file in config_files:
            file_start = time.time()
            try:
                config = load_config(config_file)
                file_time = time.time() - file_start
                metrics['configs_loaded'] += 1
                print(f"{config_file}: {file_time:.3f}s")
            except Exception as e:
                print(f"Error loading {config_file}: {e}")
        
        final_imports = len(context.import_context.visited_files)
        metrics['cache_hits'] = final_imports - len(config_files)
        metrics['cache_misses'] = len(config_files)
    
    metrics['total_time'] = time.time() - start_time
    return metrics

# Usage
metrics = timed_config_loading(config_files)
print(f"Total time: {metrics['total_time']:.3f}s")
print(f"Cache hits: {metrics['cache_hits']}")
```

### 3. Conditional Cache Usage

Use caching strategically based on configuration relationships:

```python
from pathlib import Path
from duckalog.config.api import load_config
from duckalog.config.resolution.imports import request_cache_scope

def load_config_smart(config_path: str, use_cache: bool = True) -> Config:
    """Load configuration with optional caching based on complexity."""
    
    # Detect configuration complexity
    with open(config_path, 'r') as f:
        content = f.read()
    
    has_imports = 'imports:' in content
    is_large_file = len(content) > 10000  # 10KB threshold
    
    # Use caching for complex configurations
    if use_cache and (has_imports or is_large_file):
        with request_cache_scope() as context:
            print(f"Loading {config_path} with caching enabled")
            return load_config(config_path)
    else:
        print(f"Loading {config_path} without caching (simple config)")
        return load_config(config_path)

# Usage
config1 = load_config_smart("simple.yaml", use_cache=False)
config2 = load_config_smart("complex.yaml", use_cache=True)
```

## Custom Implementation Patterns

### 1. Configuration Validation Pipeline

Create custom validation pipelines:

```python
from duckalog.config.api import load_config
from duckalog.config.resolution.base import ImportResolver, ImportContext
from typing import List, Callable

class ValidationPipeline(ImportResolver):
    """Applies multiple validation steps during import resolution."""
    
    def __init__(self, validators: List[Callable], context: ImportContext):
        self.validators = validators
        self.context = context
        self.default_resolver = DefaultImportResolver(context)
    
    def resolve(self, config_data: dict, context: ImportContext) -> dict:
        # Apply validation pipeline
        for validator in self.validators:
            config_data = validator(config_data)
        
        # Continue with standard resolution
        return self.default_resolver.resolve(config_data, context)

def validate_naming_conventions(config_data: dict) -> dict:
    """Validate configuration naming conventions."""
    views = config_data.get('views', [])
    
    for view in views:
        view_name = view.get('name', '')
        if not view_name.islower():
            raise ValueError(f"View name '{view_name}' should be lowercase")
    
    return config_data

def validate_required_secrets(config_data: dict) -> dict:
    """Validate that required secrets are configured."""
    if 'secrets' not in config_data:
        views_with_secrets = [
            v for v in config_data.get('views', [])
            if v.get('source') in ['s3', 'gcs', 'azure']
        ]
        
        if views_with_secrets:
            raise ValueError("Secrets configuration required for cloud storage views")
    
    return config_data

# Usage
validators = [
    validate_naming_conventions,
    validate_required_secrets
]

with request_cache_scope() as context:
    pipeline = ValidationPipeline(validators, context.import_context)
    # Integration would need custom loading logic
```

### 2. Configuration Transformation Pipeline

Apply transformations during loading:

```python
from typing import Dict, Any

class ConfigTransformer:
    """Applies transformations during configuration loading."""
    
    def __init__(self, transformations: Dict[str, Callable]):
        self.transformations = transformations
    
    def transform(self, config_data: dict) -> dict:
        """Apply all registered transformations."""
        for pattern, transformer in self.transformations.items():
            if self._matches_pattern(config_data, pattern):
                config_data = transformer(config_data)
        
        return config_data
    
    def _matches_pattern(self, config_data: dict, pattern: str) -> bool:
        """Check if configuration matches transformation pattern."""
        # Simple pattern matching - can be enhanced
        return pattern in str(config_data).lower()

# Example transformations
def add_environment_prefix(config_data: dict) -> dict:
    """Add environment prefix to all view names."""
    import os
    env = os.getenv('DEPLOYMENT_ENV', 'dev')
    
    views = config_data.get('views', [])
    for view in views:
        original_name = view.get('name', '')
        view['name'] = f"{env}_{original_name}"
    
    return config_data

def normalize_paths(config_data: dict) -> dict:
    """Normalize all file paths to use forward slashes."""
    def normalize_path(path):
        return path.replace('\\', '/') if path else path
    
    # Normalize paths in views
    for view in config_data.get('views', []):
        if 'uri' in view:
            view['uri'] = normalize_path(view['uri'])
    
    return config_data

# Usage
transformations = {
    'environment': add_environment_prefix,
    'windows': normalize_paths
}

transformer = ConfigTransformer(transformations)
# Apply during loading process
```

## Error Handling Patterns

### 1. Graceful Degradation

Handle configuration errors gracefully:

```python
from duckalog.config.api import load_config
from duckalog.errors import ConfigError, ImportError

def load_config_with_fallback(primary_path: str, fallback_path: str = None) -> Config:
    """Load configuration with fallback options."""
    
    try:
        return load_config(primary_path)
    except ConfigError as e:
        print(f"Failed to load primary config {primary_path}: {e}")
        
        if fallback_path:
            try:
                print(f"Attempting fallback config: {fallback_path}")
                return load_config(fallback_path)
            except ConfigError as fallback_error:
                print(f"Fallback config also failed: {fallback_error}")
                raise ConfigError(f"Both primary and fallback configs failed: {e}, {fallback_error}")
        
        raise

def load_partial_configs(config_paths: list[str]) -> dict:
    """Load multiple configurations, continuing on individual failures."""
    results = {
        'successful': [],
        'failed': [],
        'configs': {}
    }
    
    for config_path in config_paths:
        try:
            config = load_config(config_path)
            results['successful'].append(config_path)
            results['configs'][config_path] = config
        except Exception as e:
            results['failed'].append((config_path, str(e)))
            print(f"Failed to load {config_path}: {e}")
    
    return results

# Usage
try:
    config = load_config_with_fallback("production.yaml", "default.yaml")
except ConfigError as e:
    print(f"Configuration loading failed: {e}")
    # Handle appropriately

partial_results = load_partial_configs(config_files)
print(f"Loaded {len(partial_results['successful'])}/{len(config_files)} configs")
```

### 2. Comprehensive Error Reporting

Provide detailed error context:

```python
import traceback
from typing import Dict, Any

class ConfigLoadError(Exception):
    """Enhanced configuration loading error with context."""
    
    def __init__(self, message: str, config_path: str, context: Dict[str, Any] = None):
        super().__init__(message)
        self.config_path = config_path
        self.context = context or {}
        self.traceback = traceback.format_exc()

def load_config_with_context(config_path: str, **kwargs) -> Config:
    """Load configuration with enhanced error context."""
    
    context = {
        'config_path': config_path,
        'load_time': time.time(),
        'kwargs': kwargs,
        'working_directory': os.getcwd()
    }
    
    try:
        config = load_config(config_path, **kwargs)
        context['load_success'] = True
        return config
    
    except Exception as e:
        context['load_success'] = False
        context['error_type'] = type(e).__name__
        context['error_message'] = str(e)
        
        # Add additional context for debugging
        if os.path.exists(config_path):
            stat = os.stat(config_path)
            context['file_size'] = stat.st_size
            context['file_modified'] = stat.st_mtime
        
        raise ConfigLoadError(
            f"Failed to load configuration: {e}",
            config_path,
            context
        ) from e

# Usage
try:
    config = load_config_with_context("complex.yaml", filesystem=custom_fs)
except ConfigLoadError as e:
    print(f"Configuration error: {e}")
    print(f"Config path: {e.config_path}")
    print(f"Context: {e.context}")
    if e.traceback:
        print(f"Traceback:\n{e.traceback}")
```

## Testing Patterns

### 1. Mock Configuration Loading

Create mock configurations for testing:

```python
from unittest.mock import Mock, patch
from tempfile import NamedTemporaryFile
import yaml
import json

def create_test_config(config_data: dict, format: str = 'yaml') -> str:
    """Create temporary configuration file for testing."""
    suffix = f'.{format}'
    
    with NamedTemporaryFile(mode='w', suffix=suffix, delete=False) as f:
        if format == 'yaml':
            yaml.dump(config_data, f)
        elif format == 'json':
            json.dump(config_data, f)
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        return f.name

def test_config_loading():
    """Test configuration loading with mock data."""
    
    # Create test configuration
    test_config = {
        'version': 1,
        'duckdb': {'database': ':memory:'},
        'views': [
            {
                'name': 'test_view',
                'sql': 'SELECT 1 as test_column'
            }
        ]
    }
    
    # Create temporary config file
    config_path = create_test_config(test_config)
    
    try:
        # Test loading
        config = load_config(config_path)
        
        # Assertions
        assert config.version == 1
        assert len(config.views) == 1
        assert config.views[0].name == 'test_view'
        
        print("Configuration loading test passed")
        
    finally:
        # Cleanup
        import os
        os.unlink(config_path)

# Usage
test_config_loading()
```

### 2. Mock External Dependencies

Test with mocked filesystem and other dependencies:

```python
from unittest.mock import Mock, patch
import pytest

def test_config_with_mock_filesystem():
    """Test configuration loading with mocked filesystem."""
    
    # Mock filesystem
    mock_fs = Mock()
    mock_fs.open.return_value.__enter__.return_value.read.return_value = """
    version: 1
    duckdb:
      database: :memory:
    views: []
    """
    
    # Mock config content
    test_config = {
        'version': 1,
        'duckdb': {'database': ':memory:'},
        'views': []
    }
    
    with patch('duckalog.config.api._load_config_from_local_file') as mock_load:
        mock_load.return_value = Mock(**test_config)
        
        config = load_config(
            "s3://bucket/config.yaml",
            filesystem=mock_fs
        )
        
        # Verify the mock was called with correct parameters
        mock_load.assert_called_once()
        call_args = mock_load.call_args
        assert 'filesystem' in call_args.kwargs
        assert call_args.kwargs['filesystem'] == mock_fs

# Usage
test_config_with_mock_filesystem()
```

## Migration Patterns

### 1. Gradual Migration from Legacy Patterns

Migrate existing code gradually while maintaining compatibility:

```python
# Legacy code pattern (to be migrated)
def load_and_build_legacy(config_path: str):
    """Legacy pattern using old imports."""
    from duckalog import load_config, build_catalog
    
    config = load_config(config_path)
    build_catalog(config_path)
    return config

# Migrated code with new patterns
def load_and_build_modern(config_path: str, use_new_features: bool = False):
    """Modern pattern with optional new features."""
    from duckalog.config.api import load_config as new_load_config
    from duckalog import build_catalog
    
    if use_new_features:
        # Use new enhanced loading
        config = new_load_config(
            config_path,
            resolve_paths=True,
            load_dotenv=True
        )
    else:
        # Use legacy-compatible loading
        from duckalog import load_config as legacy_load_config
        config = legacy_load_config(config_path)
    
    build_catalog(config_path)
    return config

# Wrapper for backward compatibility
def load_and_build(config_path: str, enable_new_features: bool = False):
    """Unified interface supporting both legacy and new patterns."""
    
    if enable_new_features:
        return load_and_build_modern(config_path, use_new_features=True)
    else:
        return load_and_build_legacy(config_path)

# Usage
# Legacy usage (unchanged)
config = load_and_build("catalog.yaml")

# New features usage
config = load_and_build("catalog.yaml", enable_new_features=True)
```

### 2. Feature Detection

Detect available features and adapt accordingly:

```python
def detect_new_features() -> dict:
    """Detect which new features are available."""
    features = {
        'dependency_injection': False,
        'request_scoped_caching': False,
        'custom_resolvers': False,
        'enhanced_errors': False
    }
    
    try:
        from duckalog.config.api import load_config
        features['dependency_injection'] = True
    except ImportError:
        pass
    
    try:
        from duckalog.config.resolution.imports import request_cache_scope
        features['request_scoped_caching'] = True
    except ImportError:
        pass
    
    try:
        from duckalog.config.resolution.base import ImportResolver
        features['custom_resolvers'] = True
    except ImportError:
        pass
    
    try:
        from duckalog.errors import ConfigLoadError
        features['enhanced_errors'] = True
    except ImportError:
        pass
    
    return features

def adaptive_config_loading(config_path: str):
    """Adapt configuration loading based on available features."""
    features = detect_new_features()
    
    if features['dependency_injection'] and features['request_scoped_caching']:
        # Use new advanced pattern
        from duckalog.config.api import load_config
        from duckalog.config.resolution.imports import request_cache_scope
        
        with request_cache_scope() as context:
            return load_config(config_path)
    
    else:
        # Fall back to legacy pattern
        from duckalog import load_config
        return load_config(config_path)

# Usage
features = detect_new_features()
print(f"Available features: {features}")

config = adaptive_config_loading("catalog.yaml")
```

## Best Practices

### 1. Configuration Organization

Organize configurations for maintainability:

```python
# Configuration loading utilities
class ConfigManager:
    """Centralized configuration management."""
    
    def __init__(self, base_config_path: str):
        self.base_config_path = base_config_path
        self._config_cache = {}
    
    def load_config_with_cache(self, config_path: str, use_cache: bool = True) -> Config:
        """Load configuration with optional caching."""
        
        if use_cache and config_path in self._config_cache:
            return self._config_cache[config_path]
        
        config = load_config(config_path)
        
        if use_cache:
            self._config_cache[config_path] = config
        
        return config
    
    def reload_config(self, config_path: str) -> Config:
        """Force reload of configuration."""
        if config_path in self._config_cache:
            del self._config_cache[config_path]
        
        return self.load_config_with_cache(config_path, use_cache=True)

# Usage
config_manager = ConfigManager("base.yaml")
config = config_manager.load_config_with_cache("analytics.yaml")
```

### 2. Resource Management

Proper resource cleanup for advanced usage:

```python
from contextlib import contextmanager

@contextmanager
def config_session(config_paths: list[str]):
    """Context manager for configuration loading sessions."""
    
    with request_cache_scope() as context:
        try:
            configs = {}
            for config_path in config_paths:
                configs[config_path] = load_config(config_path)
            
            yield configs, context
            
        finally:
            # Cleanup handled automatically by request_cache_scope
            pass

# Usage
with config_session(config_files) as (configs, context):
    # Use configurations
    for path, config in configs.items():
        print(f"Loaded {path}: {len(config.views)} views")
    
    # Context automatically cleaned up
```

### 3. Performance Optimization

Optimize configuration loading for performance:

```python
import concurrent.futures
from typing import List

def parallel_config_loading(config_paths: List[str], max_workers: int = 4) -> List[Config]:
    """Load multiple configurations in parallel when appropriate."""
    
    # Check if configs are independent (no shared imports)
    independent_configs = []
    for config_path in config_paths:
        # Simple heuristic - can be enhanced
        if not _has_imports(config_path):
            independent_configs.append(config_path)
    
    if not independent_configs:
        # Use sequential loading with caching
        with request_cache_scope() as context:
            return [load_config(path) for path in config_paths]
    
    # Parallel loading for independent configs
    configs = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_path = {
            executor.submit(load_config, path): path 
            for path in independent_configs
        }
        
        for future in concurrent.futures.as_completed(future_to_path):
            path = future_to_path[future]
            try:
                config = future.result()
                configs.append(config)
            except Exception as e:
                print(f"Failed to load {path}: {e}")
    
    return configs

def _has_imports(config_path: str) -> bool:
    """Check if configuration has imports."""
    try:
        with open(config_path, 'r') as f:
            content = f.read()
            return 'imports:' in content
    except:
        return True  # Assume has imports if can't check

# Usage
configs = parallel_config_loading(config_files, max_workers=8)
```

These patterns provide comprehensive guidance for using both the basic and advanced features of Duckalog's new architecture while maintaining backward compatibility with existing code.