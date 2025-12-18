# Dependency Injection Examples

This document provides practical examples of using dependency injection patterns in the Duckalog configuration system.

## Table of Contents

- [Basic Examples](#basic-examples)
- [Advanced Integration](#advanced-integration)
- [Real-World Use Cases](#real-world-use-cases)
- [Testing Patterns](#testing-patterns)
- [Migration Examples](#migration-examples)

## Basic Examples

### Custom ConfigLoader

```python
from duckalog.config.loading.base import ConfigLoader
from duckalog.config.models import Config
from typing import Any

class CustomConfigLoader(ConfigLoader):
    """Custom config loader for database-backed configurations."""
    
    def __init__(self, database_url: str):
        self.database_url = database_url
    
    def load_config(self, path: str, **kwargs) -> Config:
        # Load configuration from database
        import sqlite3
        
        conn = sqlite3.connect(self.database_url)
        cursor = conn.cursor()
        cursor.execute("SELECT config_data FROM configs WHERE path = ?", (path,))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            import json
            config_data = json.loads(result[0])
            return Config.model_validate(config_data)
        else:
            raise FileNotFoundError(f"Config not found: {path}")

# Usage
custom_loader = CustomConfigLoader("sqlite:///configs.db")
config = custom_loader.load_config("production/catalog.yaml")
```

### Custom SQLFileLoader

```python
from duckalog.config.loading.base import SQLFileLoader

class TemplateSQLFileLoader(SQLFileLoader):
    """SQL file loader with Jinja2 template support."""
    
    def __init__(self, template_env):
        self.template_env = template_env
    
    def load_sql_file(self, path: str, variables: dict = None, **kwargs) -> str:
        from jinja2 import Template
        
        with open(path, 'r') as f:
            template_content = f.read()
        
        template = Template(template_content)
        return template.render(variables or {})

# Usage
from jinja2 import Environment, FileSystemLoader

template_env = Environment(loader=FileSystemLoader('templates/'))
sql_loader = TemplateSQLFileLoader(template_env)

config_data = {
    'views': [{
        'name': 'sales_report',
        'sql_file': {
            'path': 'templates/sales.sql',
            'variables': {'start_date': '2024-01-01'}
        }
    }]
}
```

## Advanced Integration

### S3 Filesystem Integration

```python
import fsspec
from duckalog.config.loading.base import ConfigLoader

class S3ConfigLoader(ConfigLoader):
    """Load configurations from S3."""
    
    def __init__(self, bucket: str, prefix: str = ""):
        self.bucket = bucket
        self.prefix = prefix
        self.fs = fsspec.filesystem('s3')
    
    def load_config(self, path: str, **kwargs) -> Config:
        full_path = f"s3://{self.bucket}/{self.prefix}{path}"
        
        if not self.fs.exists(full_path):
            raise FileNotFoundError(f"S3 config not found: {full_path}")
        
        with self.fs.open(full_path, 'r') as f:
            content = f.read()
        
        # Parse based on file extension
        if path.endswith('.json'):
            import json
            config_data = json.loads(content)
        elif path.endswith(('.yaml', '.yml')):
            import yaml
            config_data = yaml.safe_load(content)
        else:
            raise ValueError(f"Unsupported file format: {path}")
        
        return Config.model_validate(config_data)

# Usage
s3_loader = S3ConfigLoader("my-config-bucket", "environments/")
config = s3_loader.load_config("production/catalog.yaml")
```

### Database-Backed Environment Processing

```python
from duckalog.config.resolution.base import EnvProcessor

class DatabaseEnvProcessor(EnvProcessor):
    """Environment processor that stores variables in database."""
    
    def __init__(self, database_url: str):
        self.database_url = database_url
    
    def process_env_vars(self, env_vars: dict) -> dict:
        import sqlite3
        
        conn = sqlite3.connect(self.database_url)
        cursor = conn.cursor()
        
        # Fetch variables from database
        cursor.execute("SELECT key, value FROM env_vars")
        db_vars = {row[0]: row[1] for row in cursor.fetchall()}
        conn.close()
        
        # Merge with provided variables (DB takes precedence)
        result = env_vars.copy()
        result.update(db_vars)
        
        return result

# Usage
env_processor = DatabaseEnvProcessor("sqlite:///env_vars.db")
processed_vars = env_processor.process_env_vars({'USER': 'test'})
```

## Real-World Use Cases

### Multi-Tenant Application

```python
from duckalog.config.loading.base import ConfigLoader
from duckalog.config.resolution.base import EnvProcessor

class TenantAwareConfigLoader(ConfigLoader):
    """Load tenant-specific configurations."""
    
    def __init__(self, base_loader: ConfigLoader, tenant_id: str):
        self.base_loader = base_loader
        self.tenant_id = tenant_id
    
    def load_config(self, path: str, **kwargs) -> Config:
        # Add tenant prefix to path
        tenant_path = f"tenants/{self.tenant_id}/{path}"
        
        try:
            return self.base_loader.load_config(tenant_path, **kwargs)
        except FileNotFoundError:
            # Fallback to base configuration
            return self.base_loader.load_config(path, **kwargs)

# Usage
base_loader = S3ConfigLoader("configs-bucket")
tenant_loader = TenantAwareConfigLoader(base_loader, "tenant_123")

config = tenant_loader.load_config("catalog.yaml")
```

### CI/CD Pipeline with In-Memory Filesystem

```python
import fsspec
from duckalog.config.loading.base import ConfigLoader
from duckalog.config.resolution.base import EnvProcessor
import tempfile

class InMemoryConfigLoader(ConfigLoader):
    """Load configurations from in-memory filesystem for testing."""
    
    def __init__(self):
        self.fs = fsspec.filesystem('memory')
    
    def add_file(self, path: str, content: str):
        """Add a file to the in-memory filesystem."""
        with self.fs.open(path, 'w') as f:
            f.write(content)
    
    def load_config(self, path: str, **kwargs) -> Config:
        full_path = f"memory://{path}"
        
        if not self.fs.exists(full_path):
            raise FileNotFoundError(f"In-memory config not found: {path}")
        
        with self.fs.open(full_path, 'r') as f:
            content = f.read()
        
        # Parse content...
        import yaml
        config_data = yaml.safe_load(content)
        return Config.model_validate(config_data)

# Usage in tests
memory_loader = InMemoryConfigLoader()
memory_loader.add_file("test.yaml", """
version: 1
views:
  - name: test_view
    sql: "SELECT 1 as test"
""")

config = memory_loader.load_config("test.yaml")
```

## Testing Patterns

### Mock Filesystem for Testing

```python
from unittest.mock import MagicMock
import fsspec
from duckalog.config.loading.base import ConfigLoader

class MockConfigLoader(ConfigLoader):
    """Mock config loader for testing."""
    
    def __init__(self):
        self.fs = MagicMock(spec=fsspec.filesystem)
        self.configs = {}
    
    def add_config(self, path: str, config_data: dict):
        """Add a mock configuration."""
        self.configs[path] = config_data
    
    def load_config(self, path: str, **kwargs) -> Config:
        if path not in self.configs:
            raise FileNotFoundError(f"Mock config not found: {path}")
        
        return Config.model_validate(self.configs[path])

# Usage in tests
def test_config_loading():
    loader = MockConfigLoader()
    loader.add_config("test.yaml", {
        'version': 1,
        'views': [{'name': 'test', 'sql': 'SELECT 1'}]
    })
    
    config = loader.load_config("test.yaml")
    assert len(config.views) == 1
    assert config.views[0].name == "test"
```

### Testing with Custom Environment Variables

```python
from duckalog.config.resolution.base import EnvProcessor

class TestEnvProcessor(EnvProcessor):
    """Test environment processor with predictable behavior."""
    
    def __init__(self, variables: dict):
        self.variables = variables
    
    def process_env_vars(self, env_vars: dict) -> dict:
        result = env_vars.copy()
        result.update(self.variables)
        return result

# Usage in tests
def test_env_interpolation():
    processor = TestEnvProcessor({
        'DATABASE_URL': 'postgresql://test:test@localhost/test',
        'DEBUG': 'true'
    })
    
    config_data = {
        'database': '${DATABASE_URL}',
        'debug': '${DEBUG}'
    }
    
    processed = processor.process_env_vars(config_data)
    assert processed['database'] == 'postgresql://test:test@localhost/test'
    assert processed['debug'] == 'true'
```

## Migration Examples

### Gradual Migration from Old Pattern

```python
# Old pattern (still works)
from duckalog.config import load_config

config = load_config("catalog.yaml")  # Works fine

# New pattern with dependency injection
from duckalog.config.api import load_config as new_load_config
from duckalog.config.loading.base import ConfigLoader

class OptimizedConfigLoader(ConfigLoader):
    """Custom loader with optimizations."""
    
    def load_config(self, path: str, **kwargs) -> Config:
        # Your custom optimization logic here
        return new_load_config(path, **kwargs)

# Use the new pattern
custom_loader = OptimizedConfigLoader()
config = custom_loader.load_config("catalog.yaml")
```

### Before/After Custom Filesystem

```python
# Before (tightly coupled)
def load_config_with_s3(path: str):
    import fsspec
    fs = fsspec.filesystem('s3')
    
    with fs.open(f's3://bucket/{path}', 'r') as f:
        content = f.read()
    
    import yaml
    config_data = yaml.safe_load(content)
    return Config.model_validate(config_data)

# After (dependency injection)
from duckalog.config.loading.base import ConfigLoader

class S3ConfigLoader(ConfigLoader):
    def __init__(self, bucket: str):
        self.bucket = bucket
        self.fs = fsspec.filesystem('s3')
    
    def load_config(self, path: str, **kwargs) -> Config:
        with self.fs.open(f's3://{self.bucket}/{path}', 'r') as f:
            content = f.read()
        
        import yaml
        config_data = yaml.safe_load(content)
        return Config.model_validate(config_data)

# Usage
s3_loader = S3ConfigLoader("my-bucket")
config = s3_loader.load_config("catalog.yaml")
```

## Best Practices

### Error Handling

```python
from duckalog.errors import ConfigError

class RobustConfigLoader(ConfigLoader):
    """Config loader with comprehensive error handling."""
    
    def load_config(self, path: str, **kwargs) -> Config:
        try:
            # Your loading logic here
            pass
        except FileNotFoundError as e:
            raise ConfigError(f"Configuration file not found: {path}") from e
        except Exception as e:
            raise ConfigError(f"Failed to load configuration: {e}") from e
```

### Performance Optimization

```python
from functools import lru_cache

class CachedConfigLoader(ConfigLoader):
    """Config loader with built-in caching."""
    
    def __init__(self):
        self._cache = {}
    
    @lru_cache(maxsize=128)
    def load_config(self, path: str, **kwargs) -> Config:
        # Expensive loading operation
        return self._load_uncached(path, **kwargs)
    
    def _load_uncached(self, path: str, **kwargs) -> Config:
        # Your actual loading logic here
        pass
```

These examples demonstrate the flexibility and power of the new dependency injection architecture while maintaining backward compatibility with existing code.