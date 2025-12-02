# API Reference

This section documents the core API functions and classes in Duckalog, with a focus on path resolution features.

## Core Configuration API

### load_config()

Load, interpolate, and validate a Duckalog configuration file with optional path resolution.

```python
from duckalog import load_config

# Load with path resolution enabled (default)
config = load_config("catalog.yaml")

# Load with explicit path resolution control
config = load_config("catalog.yaml", resolve_paths=True)
config = load_config("catalog.yaml", resolve_paths=False)

# Load without processing SQL files (for validation)
config = load_config("catalog.yaml", load_sql_files=False)
```

**Parameters:**
- `path` (str): Path to YAML or JSON configuration file
- `load_sql_files` (bool, optional): Whether to load SQL from external files. Default: True
- `sql_file_loader` (SQLFileLoader, optional): Custom SQL file loader instance
- `resolve_paths` (bool, optional): Whether to resolve relative paths. Default: True

**Returns:**
- `Config`: Validated configuration object

**Raises:**
- `ConfigError`: Configuration parsing or validation errors

## Path Resolution API

### Path Detection Functions

#### is_relative_path()

Detect if a path is relative based on platform-specific rules.

```python
from duckalog.path_resolution import is_relative_path

# Returns True for relative paths
assert is_relative_path("data/file.parquet")
assert is_relative_path("../shared/data.parquet")

# Returns False for absolute paths and URIs
assert not is_relative_path("/absolute/path/file.parquet")
assert not is_relative_path("s3://bucket/file.parquet")
```

**Parameters:**
- `path` (str): Path string to check

**Returns:**
- `bool`: True if path is relative, False otherwise

#### detect_path_type()

Categorize paths by type for processing.

```python
from duckalog.path_resolution import detect_path_type

path_type = detect_path_type("../data/file.parquet")  # Returns: "relative"
path_type = detect_path_type("/absolute/file.parquet")  # Returns: "absolute"
path_type = detect_path_type("s3://bucket/file.parquet")  # Returns: "remote"
```

**Parameters:**
- `path` (str): Path string to analyze

**Returns:**
- `str`: One of "relative", "absolute", "remote", "invalid"

### Path Resolution Functions

#### resolve_relative_path()

Resolve a relative path to an absolute path relative to configuration directory.

```python
from duckalog.path_resolution import resolve_relative_path
from pathlib import Path

config_dir = Path("/project/config")
resolved = resolve_relative_path("data/file.parquet", config_dir)
# Returns: "/project/config/data/file.parquet"
```

**Parameters:**
- `path` (str): Path to resolve (relative or absolute)
- `config_dir` (Path): Directory containing the configuration file

**Returns:**
- `str`: Resolved absolute path

**Raises:**
- `ValueError`: If path resolution fails or violates security rules

### Security Validation Functions

#### validate_path_security()

Validate that resolved paths don't violate security boundaries.

```python
from duckalog.path_resolution import validate_path_security
from pathlib import Path

config_dir = Path("/project/config")

# Safe paths return True
assert validate_path_security("data/file.parquet", config_dir)
assert validate_path_security("../shared/data.parquet", config_dir)

# Dangerous paths return False
assert not validate_path_security("../../../etc/passwd", config_dir)
```

**Parameters:**
- `path` (str): Path to validate (will be resolved if relative)
- `config_dir` (Path): Directory containing the configuration file

**Returns:**
- `bool`: True if path is safe, False otherwise

#### validate_file_accessibility()

Validate that a file path is accessible and readable.

```python
from duckalog.path_resolution import validate_file_accessibility

accessible, error = validate_file_accessibility("/path/to/file.parquet")

if accessible:
    print("File is accessible")
else:
    print(f"File access error: {error}")
```

**Parameters:**
- `path` (str): File path to validate

**Returns:**
- `tuple[bool, str | None]`: (is_accessible, error_message)

### Path Normalization Functions

#### normalize_path_for_sql()

Normalize a path for use in SQL statements.

```python
from duckalog.path_resolution import normalize_path_for_sql

sql_path = normalize_path_for_sql("/path/to/file.parquet")
# Returns: "'/path/to/file.parquet'"

sql_path = normalize_path_for_sql("/path/file's_data.parquet")  
# Returns: "'/path/file''s_data.parquet'" (properly escaped)
```

**Parameters:**
- `path` (str): Absolute path to normalize

**Returns:**
- `str`: SQL-safe quoted path

## Configuration Models

### Config

Top-level configuration model with path resolution integration.

```python
from duckalog import load_config

config = load_config("catalog.yaml")

# Access configuration properties
print(config.version)
print(len(config.views))

# Views have resolved paths when resolution is enabled
for view in config.views:
    print(f"View: {view.name}, URI: {view.uri}")
```

### ViewConfig

Model for individual view definitions that may contain resolved paths.

```python
from duckalog.config import ViewConfig

# View with relative path (will be resolved during config loading)
view = ViewConfig(
    name="events",
    source="parquet", 
    uri="data/events.parquet"  # Relative path
)

# View with absolute path (unchanged during resolution)
view = ViewConfig(
    name="remote_data",
    source="parquet",
    uri="s3://bucket/events.parquet"  # Remote URI - unchanged
)
```

### AttachmentConfig

Models for database attachments with path resolution support.

```python
from duckalog.config import DuckDBAttachment, SQLiteAttachment

# DuckDB attachment with relative path
duckdb_attach = DuckDBAttachment(
    alias="reference_db",
    path="./databases/reference.duckdb",  # Will be resolved
    read_only=True
)

# SQLite attachment with relative path
sqlite_attach = SQLiteAttachment(
    alias="legacy_db", 
    path="../legacy/system.db"  # Will be resolved
)
```

## Exception Classes

### ConfigError

Raised for configuration-related errors including path resolution failures.

```python
from duckalog import load_config, ConfigError

try:
    config = load_config("catalog.yaml")
except ConfigError as e:
    print(f"Configuration error: {e}")
```

### PathResolutionError

Raised specifically when path resolution fails due to security or access issues.

```python
from duckalog.path_resolution import PathResolutionError, resolve_relative_path
from pathlib import Path

try:
    resolved = resolve_relative_path("../../../etc/passwd", Path("/project/config"))
except PathResolutionError as e:
    print(f"Path resolution failed: {e}")
    print(f"Original path: {e.original_path}")
    print(f"Resolved path: {e.resolved_path}")
```

## Generated API Documentation

This section is generated from the Duckalog source code using mkdocstrings.

::: duckalog

