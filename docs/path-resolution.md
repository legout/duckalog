# Path Resolution Guide

This guide explains how Duckalog handles relative and absolute paths in configuration files, ensuring consistent behavior across different working environments.

## Overview

Duckalog automatically resolves relative paths to absolute paths during configuration processing. This ensures that catalogs work consistently regardless of where the `duckalog` command is executed from.

## How Path Resolution Works

### Resolution Algorithm

1. **Path Detection**: Determine if a path is relative, absolute, or a remote URI
2. **Relative Path Resolution**: Resolve relative paths against the configuration file's directory
3. **Security Validation**: Ensure resolved paths don't escape safe boundaries
4. **Path Normalization**: Normalize paths for SQL generation

### Path Types

#### Relative Paths (Automatically Resolved)
```yaml
views:
  - name: users
    source: parquet
    uri: "data/users.parquet"  # → /path/to/config/data/users.parquet
    description: "Relative to config directory"

  - name: events
    source: parquet
    uri: "./events.parquet"     # → /path/to/config/events.parquet
    description: "Current directory relative to config"

  - name: shared
    source: parquet
    uri: "../shared/data.parquet"  # → /path/to/shared/data.parquet
    description: "Parent directory relative to config"
```

#### Absolute Paths (Preserved Unchanged)
```yaml
views:
  - name: fixed_data
    source: parquet
    uri: "/absolute/path/data.parquet"  # Used as-is
    description: "Unix absolute path"

  - name: windows_data
    source: parquet
    uri: "C:\\data\\file.parquet"  # Used as-is
    description: "Windows absolute path"
```

#### Remote URIs (Not Modified)
```yaml
views:
  - name: s3_data
    source: parquet
    uri: "s3://my-bucket/data/file.parquet"  # Used as-is
    description: "S3 URI"

  - name: http_data
    source: parquet
    uri: "https://example.com/data/file.parquet"  # Used as-is
    description: "HTTP URL"

  - name: gcs_data
    source: parquet
    uri: "gs://bucket/data/file.parquet"  # Used as-is
    description: "Google Cloud Storage URI"
```

## Security Features

### Directory Traversal Protection

Duckalog prevents malicious path patterns that could escape the configuration directory:

```yaml
# These patterns are blocked for security:
views:
  - name: blocked1
    source: parquet
    uri: "../../../etc/passwd"  # ❌ Blocked: excessive parent traversal

  - name: blocked2
    source: parquet
    uri: "/etc/passwd"  # ❌ Blocked: dangerous system path
```

### Allowed Patterns

```yaml
# These patterns are safe and allowed:
views:
  - name: normal_relative
    source: parquet
    uri: "data/file.parquet"  # ✅ Safe: within config directory

  - name: reasonable_parent
    source: parquet
    uri: "../shared/file.parquet"  # ✅ Safe: reasonable parent traversal

  - name: subdirectory
    source: parquet
    uri: "subdir/deep/nested/file.parquet"  # ✅ Safe: within bounds
```

## Cross-Platform Compatibility

### Windows Paths
- **Drive Letters**: `C:\`, `D:\` paths are treated as absolute
- **UNC Paths**: `\\server\share` paths are preserved
- **Path Separators**: Both `/` and `\` are supported

### Unix/Linux/macOS Paths
- **Absolute Paths**: Paths starting with `/` are absolute
- **Relative Paths**: Everything else follows relative resolution rules

### Examples

```yaml
# Windows
views:
  - name: windows_absolute
    source: parquet
    uri: "C:\\Users\\data\\file.parquet"  # Absolute, used as-is

  - name: windows_relative
    source: parquet
    uri: "data\\file.parquet"  # Resolved to config dir + data\file.parquet

# Unix/macOS
views:
  - name: unix_absolute
    source: parquet
    uri: "/home/user/data/file.parquet"  # Absolute, used as-is

  - name: unix_relative
    source: parquet
    uri: "data/file.parquet"  # Resolved to config dir + data/file.parquet
```

## Best Practices

### 1. Use Relative Paths for Local Data
```yaml
# Recommended: Relative paths for project data
views:
  - name: users
    source: parquet
    uri: "data/users.parquet"  # ✅ Portable and predictable
```

### 2. Organize Data by Purpose
```yaml
# Recommended: Structured data organization
views:
  - name: raw_events
    source: parquet
    uri: "raw-data/events/*.parquet"

  - name: processed_metrics
    source: parquet
    uri: "processed/metrics/daily/*.parquet"

  - name: reference_lookup
    source: parquet
    uri: "reference/lookup-tables/*.parquet"
```

### 3. Use Environment Variables for External Paths
```yaml
# For external dependencies, use environment variables
attachments:
  duckdb:
    - alias: reference
      path: "${env:REFERENCE_DB_PATH:./reference.duckdb}"
      read_only: true

views:
  - name: external_data
    source: parquet
    uri: "${env:DATA_ROOT}/external/file.parquet"
```

### 4. Keep Configuration and Data Together
```yaml
# Project structure:
# my-project/
# ├── catalog.yaml          # Configuration file
# ├── data/
# │   ├── users.parquet
# │   └── events.parquet
# └── processed/
#     └── metrics.parquet

# In catalog.yaml:
views:
  - name: users
    source: parquet
    uri: "data/users.parquet"  # Resolves to my-project/data/users.parquet

  - name: metrics
    source: parquet
    uri: "processed/metrics.parquet"  # Resolves to my-project/processed/metrics.parquet
```

## Migration from Absolute Paths

If you have existing configurations with absolute paths, you can migrate to relative paths:

### Before (Absolute Paths)
```yaml
version: 1
views:
  - name: users
    source: parquet
    uri: "/home/project/data/users.parquet"  # Absolute path
```

### After (Relative Paths)
```yaml
version: 1
views:
  - name: users
    source: parquet
    uri: "data/users.parquet"  # Relative to config location
```

### Migration Steps

1. **Move data files** relative to your config file location
2. **Update paths** in your configuration from absolute to relative
3. **Test** the configuration to ensure paths resolve correctly

## Troubleshooting

### Common Issues

#### Path Not Found
```bash
# Error: File does not exist
# Solution: Check that data files exist in the expected location
```

#### Security Violation
```bash
# Error: Path resolution violates security rules
# Solution: Avoid excessive parent directory traversal (../../../)
```

#### Platform Differences
```yaml
# Windows-specific issue:
uri: "data\\file.parquet"  # Use forward slashes for cross-platform compatibility
uri: "data/file.parquet"   # ✅ Better: works on all platforms
```

### Debugging Path Resolution

To troubleshoot path issues:

1. **Verify file existence**: Ensure data files exist in the expected locations
2. **Check path patterns**: Use forward slashes for cross-platform compatibility
3. **Validate security**: Avoid excessive parent directory traversal
4. **Test resolution**: Run from different working directories to verify consistency

## API Reference

### Path Resolution Functions

#### `is_relative_path(path: str) -> bool`
Detects if a path is relative based on platform-specific rules.

#### `resolve_relative_path(path: str, config_dir: Path) -> str`
Resolves a relative path to an absolute path relative to the configuration directory.

#### `validate_path_security(path: str, config_dir: Path) -> bool`
Validates that resolved paths don't violate security boundaries.

#### `normalize_path_for_sql(path: str) -> str`
Normalizes a path for use in SQL statements, handling quoting and formatting.

### Integration Points

Path resolution is automatically applied during:
- **Configuration Loading**: All config files have paths resolved during validation
- **SQL Generation**: Resolved paths are used in generated SQL statements
- **Attachment Processing**: Attachment paths are resolved for local files

## Examples

See the `examples/` directory for comprehensive examples of path resolution in action:

- **Simple Parquet**: Basic relative path usage
- **Multi-Source Analytics**: Complex path patterns across different sources
- **Environment Variables Security**: External path management
- **DuckDB Performance Settings**: Optimized path structures

For hands-on learning, try these examples:
```bash
cd examples/simple_parquet
python gen_data.py
duckalog build catalog.yml

cd examples/data-integration/multi-source-analytics
python generate_data.py
duckalog build catalog.yaml
```