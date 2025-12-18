# Dependency Injection Guide for Duckalog Configuration Architecture

This guide provides a comprehensive overview of the new dependency injection patterns introduced in the refactored Duckalog configuration architecture. The new modular structure enables better testability, extensibility, and customization of configuration loading behavior.

## Table of Contents

1. [New Architecture Overview](#new-architecture-overview)
2. [Dependency Injection Interfaces](#dependency-injection-interfaces)
3. [Usage Patterns](#usage-patterns)
4. [Migration Examples](#migration-examples)
5. [Benefits of Dependency Injection](#benefits-of-dependency-injection)

## New Architecture Overview

The refactored configuration architecture is organized into modular components that follow dependency injection principles:

```
src/duckalog/config/
├── api.py                    # Public API orchestration
├── loading/                  # Configuration loading components
│   ├── base.py              # Abstract base classes
│   ├── file.py              # File-based loading (planned)
│   ├── remote.py            # Remote URI loading (planned)
│   └── sql.py               # SQL file processing
├── resolution/              # Configuration resolution components
│   ├── base.py              # Abstract base classes and protocols
│   ├── env.py               # Environment variable processing
│   └── imports.py           # Import resolution logic
├── security/                # Path security and validation
│   ├── base.py              # Abstract base classes
│   └── path.py              # Path resolution and validation
└── models.py                # Configuration data models
```

### Key Design Principles

- **Separation of Concerns**: Each module handles a specific aspect of configuration processing
- **Dependency Injection**: Components depend on abstractions, not concrete implementations
- **Backward Compatibility**: Existing code continues to work without changes
- **Extensibility**: Easy to customize behavior through implementation injection

## Dependency Injection Interfaces

### Loading Interfaces (`config.loading.base`)

#### `ConfigLoader`

Abstract base class for loading configuration data from various sources:

```python
from abc import ABC, abstractmethod
from typing import Any, Optional, Union
from pathlib import Path

class ConfigLoader(ABC):
    """Abstract base class for configuration loaders."""

    @abstractmethod
    def load(
        self, path: Union[str, Path], filesystem: Optional[Any] = None
    ) -> dict[str, Any]:
        """Load configuration from a source."""
        pass
```

#### `SQLFileLoader`

Abstract base class for loading SQL content from files:

```python
class SQLFileLoader(ABC):
    """Abstract base class for SQL file loaders."""

    @abstractmethod
    def load_sql(self, path: Union[str, Path], filesystem: Optional[Any] = None) -> str:
        """Load SQL content from a file."""
        pass
```

### Resolution Interfaces (`config.resolution.base`)

#### `EnvProcessor` (Protocol)

Interface for processing environment variables and .env files:

```python
from typing import Protocol, Any

@runtime_checkable
class EnvProcessor(Protocol):
    """Interface for environment variable processors."""

    def process(
        self, config_data: dict[str, Any], load_dotenv: bool = True
    ) -> dict[str, Any]:
        """Process environment variables and .env files."""
        ...
```

#### `ImportResolver` (Protocol)

Interface for resolving configuration imports:

```python
@runtime_checkable
class ImportResolver(Protocol):
    """Interface for configuration import resolvers."""

    def resolve(
        self, config_data: dict[str, Any], context: ImportContext
    ) -> dict[str, Any]:
        """Resolve imports within a configuration dictionary."""
        ...
```

#### `ImportContext`

Dataclass that tracks import state during configuration loading:

```python
@dataclass
class ImportContext:
    """Tracks import state during loading."""

    visited_files: set[str] = field(default_factory=set)
    import_stack: list[str] = field(default_factory=list)
    config_cache: dict[str, Any] = field(default_factory=dict)
    import_chain: list[str] = field(default_factory=list)
```

### Security Interfaces (`config.security.base`)

#### `PathValidator`

Abstract base class for validating path security:

```python
class PathValidator(ABC):
    """Abstract base class for path security validation."""

    @abstractmethod
    def validate(self, path: Union[str, Path]) -> None:
        """Validate that a path is secure and accessible."""
        pass
```

#### `PathResolver`

Abstract base class for resolving paths with security checks:

```python
class PathResolver(ABC):
    """Abstract base class for path resolution."""

    @abstractmethod
    def resolve(self, path: str, base_path: Optional[Union[str, Path]] = None) -> str:
        """Resolve a path to an absolute path with security checks."""
        pass
```

## Usage Patterns

### Using Default Implementations (Backward Compatibility)

The existing API continues to work without any changes:

```python
from duckalog.config import load_config

# Standard usage - uses default implementations
config = load_config("catalog.yaml")
print(f"Loaded {len(config.views)} views")
```

### Creating Custom Implementations

#### Custom Environment Processor

Create a custom environment processor that loads variables from a database:

```python
from typing import Any, Dict
from duckalog.config.resolution.base import EnvProcessor

class DatabaseEnvProcessor(EnvProcessor):
    """Custom environment processor that loads from a database."""
    
    def __init__(self, db_connection):
        self.db = db_connection
    
    def process(self, config_data: dict[str, Any], load_dotenv: bool = True) -> dict[str, Any]:
        if not load_dotenv:
            return config_data
            
        # Load environment variables from database
        env_vars = self._load_env_from_db()
        
        # Apply to config data
        return self._apply_env_vars(config_data, env_vars)
    
    def _load_env_from_db(self) -> dict[str, str]:
        # Custom logic to load from database
        with self.db.cursor() as cursor:
            cursor.execute("SELECT key, value FROM environment_variables")
            return {row[0]: row[1] for row in cursor.fetchall()}
    
    def _apply_env_vars(self, config_data: dict[str, Any], env_vars: dict[str, str]) -> dict[str, Any]:
        # Apply environment variables to config
        import os
        os.environ.update(env_vars)
        return config_data
```

#### Custom Path Resolver

Create a custom path resolver with enhanced security:

```python
from duckalog.config.security.base import PathResolver, PathValidator
from duckalog.config.security.path import DefaultPathResolver, validate_path_security
from pathlib import Path
from typing import Union, Optional

class EnhancedSecurityPathResolver(PathResolver):
    """Path resolver with enhanced security validation."""
    
    def __init__(self, allowed_patterns: list[str] = None):
        self.allowed_patterns = allowed_patterns or []
        self.delegate = DefaultPathResolver()
        self.validator = DefaultPathValidator()
    
    def resolve(self, path: str, base_path: Optional[Union[str, Path]] = None) -> str:
        # Validate against allowed patterns first
        if not self._is_pattern_allowed(path):
            raise ValueError(f"Path pattern not allowed: {path}")
        
        # Use delegate for standard resolution
        resolved = self.delegate.resolve(path, base_path)
        
        # Additional security validation
        self.validator.validate(resolved)
        
        return resolved
    
    def _is_pattern_allowed(self, path: str) -> bool:
        import re
        for pattern in self.allowed_patterns:
            if re.match(pattern, path):
                return True
        return False
```

#### Custom Config Loader

Create a custom config loader that supports additional file formats:

```python
import toml  # Requires tomli or similar library
from duckalog.config.loading.base import ConfigLoader
from typing import Any, Optional, Union
from pathlib import Path

class TomlConfigLoader(ConfigLoader):
    """Config loader that supports TOML format."""
    
    def load(self, path: Union[str, Path], filesystem: Optional[Any] = None) -> dict[str, Any]:
        if isinstance(path, str):
            path = Path(path)
            
        if not path.exists():
            raise FileNotFoundError(f"Config file not found: {path}")
        
        if filesystem is not None:
            content = filesystem.open(str(path), "r").read()
        else:
            content = path.read_text()
        
        # Parse TOML content
        try:
            return toml.loads(content)
        except Exception as e:
            raise ValueError(f"Failed to parse TOML config: {e}") from e
```

### Injecting Custom Dependencies

#### Using the API with Custom Implementations

The new API supports dependency injection for advanced use cases:

```python
from duckalog.config.api import load_config
from duckalog.config.resolution.imports import DefaultImportResolver, RequestContext
from duckalog.config.resolution.env import DefaultEnvProcessor, env_cache_scope

# Create custom context with enhanced capabilities
with env_cache_scope() as env_cache:
    request_context = RequestContext(env_cache=env_cache)
    
    # Use default resolver with custom context
    resolver = DefaultImportResolver(context=request_context)
    
    # Load config with custom resolver
    config_data = {
        "file_path": "catalog.yaml",
        "filesystem": None,
        "resolve_paths": True,
        "load_sql_files": True,
        "sql_file_loader": None,
        "load_dotenv": True
    }
    
    resolved_config = resolver.resolve(config_data, request_context.import_context)
```

#### Testing with Mock Implementations

Dependency injection makes testing much easier by allowing you to inject mock implementations:

```python
import pytest
from unittest.mock import Mock, MagicMock
from duckalog.config.resolution.base import EnvProcessor
from duckalog.config.resolution.imports import DefaultImportResolver, RequestContext

class MockEnvProcessor(EnvProcessor):
    def process(self, config_data: dict[str, Any], load_dotenv: bool = True) -> dict[str, Any]:
        # Mock environment processing
        config_data["test_env"] = "mock_value"
        return config_data

def test_config_loading_with_mock_env():
    # Create mock context
    mock_context = Mock()
    mock_context.env_cache = Mock()
    mock_context.import_context = Mock()
    
    # Create resolver with mock context
    resolver = DefaultImportResolver(context=mock_context)
    
    # Test data
    config_data = {
        "file_path": "test.yaml",
        "content": "views: []",
        "load_dotenv": True
    }
    
    # Test with mock
    result = resolver.resolve(config_data, mock_context.import_context)
    
    # Verify mock was called
    assert mock_context.import_context.visited_files.add.assert_called()
```

## Migration Examples

### Before: Custom Filesystem Implementation

```python
# Old approach - required modifying core logic
class CustomFileSystem:
    def open(self, path, mode='r'):
        # Custom file system logic
        pass
    
    def exists(self, path):
        # Custom existence check
        pass

# Had to pass through custom parameters
config = load_config("catalog.yaml", filesystem=CustomFileSystem())
```

### After: Dependency Injection with Custom Config Loader

```python
# New approach - inject custom implementation
from duckalog.config.loading.base import ConfigLoader

class CustomFileSystemLoader(ConfigLoader):
    def __init__(self, custom_fs):
        self.fs = custom_fs
    
    def load(self, path, filesystem=None):
        # Use custom filesystem directly
        if self.fs.exists(path):
            content = self.fs.open(path).read()
            import yaml
            return yaml.safe_load(content)
        return {}

# Use in testing or custom environments
custom_loader = CustomFileSystemLoader(CustomFileSystem())
# The system can now be extended without modifying core logic
```

### Before: Alternative Environment Processing

```python
# Old approach - had to modify environment variables globally
import os
os.environ.update(custom_env_vars)  # Affects entire application
config = load_config("catalog.yaml")
```

### After: Custom Environment Processor

```python
# New approach - scoped environment processing
from duckalog.config.resolution.base import EnvProcessor

class ScopedEnvProcessor(EnvProcessor):
    def __init__(self, scoped_env_vars):
        self.scoped_env = scoped_env_vars
    
    def process(self, config_data, load_dotenv=True):
        # Apply scoped environment variables without affecting global state
        original_env = os.environ.copy()
        try:
            os.environ.update(self.scoped_env)
            return config_data  # Process with scoped environment
        finally:
            os.environ.clear()
            os.environ.update(original_env)

# Use without affecting global state
scoped_processor = ScopedEnvProcessor({"DATABASE_URL": "test://localhost"})
```

### Before: Custom Path Resolution Strategies

```python
# Old approach - limited customization options
config = load_config("catalog.yaml", resolve_paths=True)  # Only boolean option
```

### After: Custom Path Resolution

```python
# New approach - inject custom path resolver
from duckalog.config.security.base import PathResolver

class CloudPathResolver(PathResolver):
    def resolve(self, path, base_path=None):
        if path.startswith("cloud://"):
            # Custom cloud path resolution
            return self._resolve_cloud_path(path)
        else:
            # Standard resolution
            return self._resolve_standard_path(path, base_path)
    
    def _resolve_cloud_path(self, path):
        # Custom logic for cloud paths
        pass
    
    def _resolve_standard_path(self, path, base_path):
        # Fallback to standard resolution
        from duckalog.config.security.path import DefaultPathResolver
        resolver = DefaultPathResolver()
        return resolver.resolve(path, base_path)

# Can be integrated with the loading system
cloud_resolver = CloudPathResolver()
```

## Benefits of Dependency Injection

### 1. Enhanced Testability

Dependency injection makes unit testing significantly easier:

- **Isolate Components**: Test individual components in isolation
- **Mock Dependencies**: Easily mock external dependencies
- **Control State**: Test with predictable, controlled state
- **No Side Effects**: Avoid modifying global state during tests

```python
# Easy testing with mocked dependencies
def test_config_loading():
    mock_loader = Mock(spec=ConfigLoader)
    mock_loader.load.return_value = {"views": []}
    
    # Test configuration loading logic with mock loader
    # No actual file I/O required
```

### 2. Improved Extensibility

The architecture allows for seamless extension of functionality:

- **Plugin Architecture**: Add new loaders, resolvers, and processors as plugins
- **Custom Implementations**: Replace any component with custom logic
- **Backward Compatibility**: Extend without breaking existing code
- **Feature Flags**: Enable/disable features through dependency injection

```python
# Easy to add new file format support
class XmlConfigLoader(ConfigLoader):
    def load(self, path, filesystem=None):
        # XML parsing logic
        pass

# Register and use without touching core code
```

### 3. Better Separation of Concerns

Each component has a single, well-defined responsibility:

- **Loading**: Responsible only for reading data from sources
- **Resolution**: Handles only import resolution logic
- **Security**: Focuses solely on path validation and security
- **Environment**: Manages environment variable processing exclusively

### 4. Configuration Flexibility

Different environments can use different implementations:

```python
# Development: Use local file system
dev_config = load_config("dev.yaml", loader=LocalFileLoader())

# Production: Use cloud storage
prod_config = load_config("prod.yaml", loader=CloudStorageLoader())

# Testing: Use in-memory loader
test_config = load_config("test.yaml", loader=MemoryLoader({"views": []}))
```

### 5. Performance Optimization

Dependency injection enables performance optimizations:

- **Lazy Loading**: Load dependencies only when needed
- **Caching**: Inject cached implementations
- **Pooling**: Use connection pools for database-backed loaders
- **Async Support**: Inject async implementations where needed

### 6. Maintenance and Debugging

The modular architecture makes maintenance easier:

- **Isolated Bugs**: Issues are contained to specific components
- **Clear Dependencies**: Easy to understand what each component needs
- **Gradual Migration**: Can update components incrementally
- **Better Logging**: Each component can provide detailed logging

## Advanced Usage Patterns

### Composition Root Pattern

Use a composition root to configure dependencies for your application:

```python
class ConfigurationFactory:
    """Factory for creating configured configuration loaders."""
    
    @staticmethod
    def create_for_environment(env: str):
        if env == "development":
            env_processor = DefaultEnvProcessor()
            path_resolver = DefaultPathResolver()
        elif env == "production":
            env_processor = ProductionEnvProcessor()
            path_resolver = SecurePathResolver(allowed_roots=["/app/config"])
        else:
            env_processor = MemoryEnvProcessor()
            path_resolver = InMemoryPathResolver()
        
        return DefaultImportResolver(
            context=RequestContext(
                env_cache=EnvCache(),
                import_context=ImportContext()
            )
        )

# Usage
factory = ConfigurationFactory()
resolver = factory.create_for_environment("production")
```

### Middleware Pattern

Create middleware-like processors for configuration:

```python
class ConfigProcessor(ABC):
    @abstractmethod
    def process(self, config_data: dict[str, Any]) -> dict[str, Any]:
        pass

class ValidationProcessor(ConfigProcessor):
    def process(self, config_data):
        # Validation logic
        return config_data

class LoggingProcessor(ConfigProcessor):
    def process(self, config_data):
        # Logging logic
        return config_data

class PipelineConfigLoader(ConfigLoader):
    def __init__(self, base_loader: ConfigLoader, processors: list[ConfigProcessor]):
        self.base_loader = base_loader
        self.processors = processors
    
    def load(self, path, filesystem=None):
        config = self.base_loader.load(path, filesystem)
        for processor in self.processors:
            config = processor.process(config)
        return config
```

This dependency injection architecture provides a solid foundation for building flexible, testable, and maintainable configuration loading systems while preserving backward compatibility and enabling future enhancements.