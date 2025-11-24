# Path Resolution Feature

Duckalog's path resolution feature automatically resolves relative file paths to absolute paths relative to the configuration file location, providing consistent behavior across different working directories while maintaining security and cross-platform compatibility.

## Overview

The path resolution feature addresses common challenges when working with file-based data sources and database attachments:

- **Portability**: Configurations can be moved between environments without breaking file references
- **Consistency**: Paths are resolved consistently regardless of the current working directory
- **Security**: Built-in validation prevents directory traversal attacks while allowing reasonable parent directory access
- **Flexibility**: Works with relative paths, absolute paths, and remote URIs

## How It Works

### Automatic Detection and Resolution

When path resolution is enabled, Duckalog automatically:

1. **Detects** whether a path is relative or absolute
2. **Resolves** relative paths against the configuration file's directory
3. **Validates** the resolved path for security concerns
4. **Updates** the configuration with resolved absolute paths

### Supported Path Types

| Path Type | Example | Resolved |
|-----------|---------|----------|
| **Relative** | `data/file.parquet` | `/project/config/data/file.parquet` |
| **Parent Directory** | `../shared/data.parquet` | `/project/shared/data.parquet` |
| **Absolute** | `/absolute/path/file.parquet` | Unchanged |
| **Windows** | `C:\data\file.parquet` | Unchanged |
| **Remote URI** | `s3://bucket/file.parquet` | Unchanged |

### Security Validation

Path resolution includes comprehensive security validation:

- **Directory Traversal Protection**: Blocks excessive parent directory navigation (`../../../etc/passwd`)
- **Reasonable Traversal**: Allows limited parent directory access for legitimate use cases
- **Dangerous Pattern Detection**: Prevents access to system directories (`/etc/`, `/usr/`, etc.)
- **Cross-Platform Compatibility**: Handles Windows and Unix path conventions

## Configuration

### Enabling Path Resolution

Path resolution is controlled by the `resolve_paths` parameter when loading configuration:

```python
from duckalog import load_config

# Enable path resolution (default)
config = load_config("catalog.yaml", resolve_paths=True)

# Disable path resolution
config = load_config("catalog.yaml", resolve_paths=False)
```

### Command Line Interface

The CLI automatically enables path resolution:

```bash
# Path resolution enabled by default
duckalog build catalog.yaml

# Generate SQL with path resolution
duckalog generate-sql catalog.yaml
```

## Usage Examples

### Basic Relative Path Resolution

**Project Structure:**
```
analytics/
├── catalog.yaml
├── data/
│   ├── events.parquet
│   └── users.parquet
└── databases/
    └── reference.duckdb
```

**Configuration (`catalog.yaml`):**
```yaml
version: 1

duckdb:
  database: catalog.duckdb

attachments:
  duckdb:
    - alias: refdata
      path: ./databases/reference.duckdb
      read_only: true

views:
  - name: events
    source: parquet
    uri: data/events.parquet
    
  - name: users
    source: parquet
    uri: ./data/users.parquet
    
  - name: user_events
    sql: |
      SELECT 
        u.user_id,
        u.name,
        e.event_type,
        e.timestamp
      FROM users u
      JOIN events e ON u.user_id = e.user_id
```

**Result:** All relative paths are resolved to absolute paths relative to `catalog.yaml`.

### Parent Directory Access

**Project Structure:**
```
company/
├── shared/
│   └── reference_data/
│       └── customers.parquet
└── analytics/
    └── catalog.yaml
    └── data/
        └── events.parquet
```

**Configuration (`company/analytics/catalog.yaml`):**
```yaml
version: 1

duckdb:
  database: catalog.duckdb

views:
  - name: events
    source: parquet
    uri: ./data/events.parquet
    
  - name: customers
    source: parquet
    uri: ../shared/reference_data/customers.parquet
    
  - name: customer_events
    sql: |
      SELECT 
        c.customer_id,
        c.name,
        e.event_type,
        e.timestamp
      FROM customers c
      JOIN events e ON c.customer_id = e.customer_id
```

**Result:** 
- `./data/events.parquet` → `/company/analytics/data/events.parquet`
- `../shared/reference_data/customers.parquet` → `/company/shared/reference_data/customers.parquet`

### Mixed Path Types

```yaml
version: 1

duckdb:
  database: catalog.duckdb

views:
  # Local relative path - will be resolved
  - name: local_data
    source: parquet
    uri: ./data/local.parquet
    
  # Absolute path - unchanged
  - name: absolute_data
    source: parquet
    uri: /absolute/path/data.parquet
    
  # Remote URI - unchanged
  - name: remote_data
    source: parquet
    uri: s3://my-bucket/data/remote.parquet
    
  # Windows path - unchanged if on Windows
  - name: windows_data
    source: parquet
    uri: D:\data\windows.parquet
```

### Attachment Path Resolution

```yaml
version: 1

duckdb:
  database: catalog.duckdb

attachments:
  duckdb:
    - alias: ref_db
      path: ./reference.databases/analytics.duckdb
      read_only: true
      
  sqlite:
    - alias: legacy_db
      path: ../legacy/production.db

views:
  - name: ref_data
    source: duckdb
    database: ref_db
    table: customers
    
  - name: legacy_data
    source: sqlite
    database: legacy_db
    table: users
```

## Security Features

### Directory Traversal Protection

Path resolution automatically blocks dangerous path patterns:

```yaml
# ❌ BLOCKED - Excessive parent directory traversal
views:
  - name: malicious
    source: parquet
    uri: ../../../../etc/passwd
```

**Error:** `Path resolution violates security rules`

### Dangerous Location Detection

Access to system directories is automatically blocked:

```yaml
# ❌ BLOCKED - Attempts to access system directories
views:
  - name: system_config
    source: parquet
    uri: ../etc/config.parquet  # Resolves to /etc/config.parquet
```

### Reasonable Traversal Allowance

Limited parent directory access is permitted for legitimate use cases:

```yaml
# ✅ ALLOWED - Reasonable parent directory access
views:
  - name: shared_data
    source: parquet
    uri: ../shared/data.parquet  # Allowed: 1 level up
    
  - name: project_root_data
    source: parquet
    uri: ../../project_data/common.parquet  # Allowed: 2 levels up
```

## Migration Guide

### From Relative Paths

**Before (manual path management):**
```yaml
version: 1

views:
  - name: data
    source: parquet
    uri: /absolute/path/to/data.parquet  # Hard-coded absolute path
```

**After (with path resolution):**
```yaml
version: 1

views:
  - name: data
    source: parquet
    uri: ./data.parquet  # Relative path - automatically resolved
```

### Migration Steps

1. **Update Configuration Files**: Replace absolute paths with relative paths where appropriate
2. **Test Resolution**: Use `duckalog validate catalog.yaml` to ensure paths resolve correctly
3. **Enable Resolution**: Ensure `resolve_paths=True` (default setting)
4. **Verify Results**: Use `duckalog generate-sql catalog.yaml` to inspect resolved paths

## API Usage

### Programmatic Path Resolution

```python
from duckalog.path_resolution import (
    resolve_relative_path,
    is_relative_path,
    validate_path_security
)
from pathlib import Path

# Check if a path is relative
is_rel = is_relative_path("data/file.parquet")  # True
is_rel = is_relative_path("/absolute/file.parquet")  # False

# Resolve a relative path
config_dir = Path("/project/config")
resolved = resolve_relative_path("data/file.parquet", config_dir)
# Returns: "/project/config/data/file.parquet"

# Validate path security
is_safe = validate_path_security("data/file.parquet", config_dir)
# Returns: True
```

### Loading Configuration with Path Resolution

```python
from duckalog import load_config, ConfigError

try:
    # Load with path resolution enabled (default)
    config = load_config("catalog.yaml")
    
    # Load with path resolution explicitly disabled
    config = load_config("catalog.yaml", resolve_paths=False)
    
except ConfigError as e:
    print(f"Configuration error: {e}")
```

## Troubleshooting

### Common Issues

#### Path Resolution Failed

**Error:** `ConfigError: Path resolution failed`

**Solutions:**
1. Check if the path exists and is accessible
2. Verify the path doesn't violate security rules
3. Ensure the configuration file path is correct
4. Use absolute paths for system-level files

#### Security Violation

**Error:** `ValueError: Path resolution violates security rules`

**Solutions:**
1. Reduce the number of parent directory traversals (`../`)
2. Avoid system directories (`/etc/`, `/usr/`, etc.)
3. Use relative paths within reasonable bounds
4. Consider moving data files to a safer location

#### File Not Found After Resolution

**Error:** `DuckDB Error: Failed to open file`

**Solutions:**
1. Verify the resolved path points to an existing file
2. Check file permissions
3. Ensure the file is not a directory
4. Use `validate_file_accessibility()` to check before loading

### Debugging Path Resolution

```python
from duckalog.path_resolution import (
    is_relative_path,
    resolve_relative_path,
    detect_path_type
)
from pathlib import Path

# Debug path detection
path = "data/file.parquet"
print(f"Path type: {detect_path_type(path)}")  # "relative"
print(f"Is relative: {is_relative_path(path)}")  # True

# Debug resolution
config_dir = Path("/project/config")
try:
    resolved = resolve_relative_path(path, config_dir)
    print(f"Resolved path: {resolved}")
except ValueError as e:
    print(f"Resolution failed: {e}")
```

## Best Practices

### Configuration Structure

```
project/
├── config/
│   ├── catalog.yaml
│   └── catalog-dev.yaml
├── data/
│   ├── raw/
│   ├── processed/
│   └── external/
├── databases/
│   ├── reference.duckdb
│   └── cache.duckdb
└── sql/
    ├── views/
    └── procedures/
```

**Recommended Path Patterns:**
- Use `./data/` for project-specific data
- Use `../shared/` for shared project resources
- Use `./databases/` for local database files
- Avoid deep parent directory navigation

### Environment-Specific Configurations

```yaml
# config/catalog.yaml
version: 1

duckdb:
  database: catalog.duckdb

views:
  - name: local_data
    source: parquet
    uri: ./data/local.parquet  # Resolved relative to this config
```

### Testing Path Resolution

```python
# Test resolution before building
from duckalog import load_config, generate_sql

try:
    # Load and validate with resolution
    config = load_config("catalog.yaml")
    
    # Generate SQL to see resolved paths
    sql = generate_sql("catalog.yaml")
    print("Generated SQL with resolved paths:")
    print(sql)
    
except Exception as e:
    print(f"Path resolution issue: {e}")
```

## Performance Considerations

Path resolution adds minimal overhead to configuration loading:

- **CPU Impact**: Negligible for typical configurations
- **Memory Impact**: Minimal additional memory usage
- **I/O Impact**: File system access only for path resolution
- **Caching**: Resolved paths are cached in configuration objects

## Cross-Platform Compatibility

### Windows vs Unix Paths

Path resolution handles platform differences automatically:

```yaml
# Works on both Windows and Unix
views:
  - name: cross_platform_data
    source: parquet
    uri: ./data/file.parquet
```

### Best Practices for Cross-Platform

1. **Use forward slashes** in configuration files (works everywhere)
2. **Avoid platform-specific paths** when possible
3. **Test on target platforms** before deployment
4. **Use environment variables** for platform-specific configurations

---

*Last updated: Duckalog v0.2.0*