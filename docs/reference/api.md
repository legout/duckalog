# API Reference

This section documents the core API functions and classes in Duckalog, with a focus on path resolution features.

## Connection Helper API

### connect_to_catalog()

Connect to an existing DuckDB database created by Duckalog.

```python
from duckalog import connect_to_catalog

# Connect to an existing catalog
conn = connect_to_catalog("catalog.yaml")

# Use the connection for queries
result = conn.execute("SELECT * FROM some_table").fetchall()
conn.close()

# With path override
conn = connect_to_catalog("catalog.yaml", database_path="analytics.db")

# With read-only mode
conn = connect_to_catalog("catalog.yaml", read_only=True)
```

**Parameters:**
- `config_path` (str): Path to YAML/JSON configuration file for an existing catalog
- `database_path` (str, optional): Database path override. If not provided, uses path from configuration
- `read_only` (bool, optional): Open connection in read-only mode for safety. Default: False

**Returns:**
- `duckdb.DuckDBPyConnection`: Active DuckDB connection object ready for query execution

**Raises:**
- `ConfigError`: If configuration file is invalid
- `FileNotFoundError`: If specified database file doesn't exist
- `duckdb.Error`: If connection or queries fail

### connect_to_catalog_cm()

Context manager version of `connect_to_catalog()` for automatic connection cleanup.

```python
from duckalog import connect_to_catalog_cm

with connect_to_catalog_cm("catalog.yaml") as conn:
    data = conn.execute("SELECT * FROM users").fetchall()
    print(f"Found {len(data)} records")
# Connection is automatically closed here
```

**Parameters:**
- `config_path` (str): Path to YAML/JSON configuration file for an existing catalog
- `database_path` (str, optional): Database path override
- `read_only` (bool, optional): Open connection in read-only mode for safety. Default: False

**Yields:**
- `duckdb.DuckDBPyConnection`: Active DuckDB connection that will be closed automatically

**Raises:**
- `ConfigError`: If configuration file is invalid
- `FileNotFoundError`: If specified database file doesn't exist
- `duckdb.Error`: If connection or queries fail

### connect_and_build_catalog()

Build a catalog and create a DuckDB connection in one operation.

```python
from duckalog import connect_and_build_catalog

# Build catalog and start querying immediately
conn = connect_and_build_catalog("catalog.yaml")
data = conn.execute("SELECT * FROM important_table").fetchall()
print(f"Found {len(data)} records")
conn.close()

# Validate only (dry run)
sql = connect_and_build_catalog("catalog.yaml", dry_run=True)
print("SQL generation completed, no database created")

# Custom database path
conn = connect_and_build_catalog("catalog.yaml", database_path="analytics.db")
print("Connected to custom database: analytics.db")
```

**Parameters:**
- `config_path` (str): Path to the YAML/JSON configuration file
- `database_path` (str, optional): Database path override
- `dry_run` (bool, optional): If True, only validates configuration and returns SQL. Default: False
- `verbose` (bool, optional): Enable verbose logging during build process. Default: False
- `read_only` (bool, optional): Open the resulting connection in read-only mode. Default: False
- `**kwargs`: Additional keyword arguments

**Returns:**
- `duckdb.DuckDBPyConnection | str | None`: Connection object for immediate use, or SQL string when `dry_run=True`

**Raises:**
- `ConfigError`: If the configuration file is invalid
- `EngineError`: If catalog building or connection fails
- `FileNotFoundError`: If the resulting database file doesn't exist (after build)

## SQL File Loading API

### SQLFileLoader

Loads SQL content from external files and processes templates.

```python
from duckalog import SQLFileLoader

loader = SQLFileLoader()

# Load raw SQL content
sql = loader.load_sql_file(
    file_path="./queries/users.sql",
    config_file_path="catalog.yaml"
)

# Load SQL with template processing
sql = loader.load_sql_file(
    file_path="./queries/filtered_users.sql",
    config_file_path="catalog.yaml",
    variables={"min_date": "2023-01-01", "status": "active"},
    as_template=True
)
```

#### Methods

##### load_sql_file()

Load SQL content from a file and optionally process as a template.

**Parameters:**
- `file_path` (str): Path to SQL file (can be relative or absolute)
- `config_file_path` (str): Path to config file for resolving relative paths
- `variables` (dict, optional): Dictionary of variables for template substitution. Default: None
- `as_template` (bool, optional): Whether to process file content as a template. Default: False
- `filesystem` (object, optional): Optional filesystem object for file I/O operations

**Returns:**
- `str`: The loaded SQL content (processed if template, raw otherwise)

**Raises:**
- `SQLFileError`: If file cannot be loaded or processed

#### Template Processing

SQLFileLoader supports simple template substitution using `{variable}` syntax:

```sql
-- filtered_users.sql
SELECT * FROM users 
WHERE created_at >= '{min_date}'
  AND status = '{status}'
  AND region = '{region}'
```

```python
loader = SQLFileLoader()
sql = loader.load_sql_file(
    file_path="./filtered_users.sql",
    config_file_path="catalog.yaml",
    variables={
        "min_date": "2023-01-01",
        "status": "active", 
        "region": "US"
    },
    as_template=True
)

# Result: SELECT * FROM users WHERE created_at >= '2023-01-01' AND status = 'active' AND region = 'US'
```

#### Path Resolution

SQLFileLoader automatically resolves relative paths relative to the configuration file directory:

```python
# If catalog.yaml is in /project/config/
# and filtered_users.sql is specified as ./queries/filtered_users.sql
# The loader will look for: /project/config/queries/filtered_users.sql
```

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
- `ConfigError`: Configuration parsing or validation errors (inherits from `DuckalogError`)

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

### Root-Based Path Security Functions

#### is_within_allowed_roots()

Check if a resolved path is within any of the allowed root directories using robust cross-platform validation.

```python
from duckalog.path_resolution import is_within_allowed_roots
from pathlib import Path

config_dir = Path("/project/config")
allowed_roots = [config_dir]

# Check if a path is within allowed roots
is_safe = is_within_allowed_roots("/project/config/data/file.parquet", allowed_roots)
# Returns: True

is_unsafe = is_within_allowed_roots("/etc/passwd", allowed_roots)  
# Returns: False

is_traversal_blocked = is_within_allowed_roots("../../../etc/passwd", allowed_roots)
# Returns: False (path traversal blocked)
```

**Parameters:**
- `candidate_path` (str): The path to check (will be resolved to absolute)
- `allowed_roots` (list[Path]): List of Path objects representing allowed root directories

**Returns:**
- `bool`: True if the candidate path is within at least one allowed root, False otherwise

**Raises:**
- `ValueError`: If the candidate path cannot be resolved (invalid path)

**Security Features:**
- Uses `Path.resolve()` to follow symlinks and get canonical paths
- Uses `os.path.commonpath()` for robust cross-platform path comparison  
- Prevents all forms of path traversal attacks regardless of encoding or separators
- Handles Windows drive letters and UNC paths correctly

## SQL Generation API

### SQL Quoting Functions

#### quote_ident()

Quote a SQL identifier using double quotes with proper escaping.

```python
from duckalog import quote_ident

# Quote simple identifiers
assert quote_ident("events") == '"events"'

# Quote identifiers with spaces
assert quote_ident("daily users") == '"daily users"'

# Quote identifiers with quotes (escapes embedded quotes)
assert quote_ident('user "events"') == '"user ""events"""'
```

**Parameters:**
- `identifier` (str): Identifier to quote

**Returns:**
- `str`: Identifier wrapped in double quotes with proper escaping

#### quote_literal()

Quote a SQL string literal using single quotes with proper escaping.

```python
from duckalog import quote_literal

# Quote simple strings
assert quote_literal("user's data") == "'user''s data'"

# Quote file paths
assert quote_literal("path/to/file.parquet") == "'path/to/file.parquet'"

# Quote SQL statements
assert quote_literal("SELECT * FROM table") == "'SELECT * FROM table'"

# Quote empty strings
assert quote_literal("") == "''"
```

**Parameters:**
- `value` (str): String literal to quote

**Returns:**
- `str`: String wrapped in single quotes with proper escaping

#### generate_view_sql()

Generate a `CREATE OR REPLACE VIEW` statement for a view configuration.

```python
from duckalog import ViewConfig, generate_view_sql

view = ViewConfig(
    name="test_view",
    source="duckdb",
    database="my_db",
    table="users"
)

sql = generate_view_sql(view)
# Returns: CREATE OR REPLACE VIEW "test_view" AS SELECT * FROM "my_db"."users";
```

**Parameters:**
- `view` (ViewConfig): View configuration to generate SQL for

**Returns:**
- `str`: SQL statement creating the view with proper quoting

#### generate_secret_sql()

Generate `CREATE SECRET` statement for a secret configuration with proper escaping.

```python
from duckalog import SecretConfig, generate_secret_sql

secret = SecretConfig(
    type="s3",
    name="prod_s3",
    provider="config",
    key_id="user's key",  # Contains single quote
    secret="secret'with'quotes"
)

sql = generate_secret_sql(secret)
# Returns: CREATE SECRET prod_s3 (TYPE S3, KEY_ID 'user''s key', SECRET 'secret''with''quotes')
```

**Parameters:**
- `secret` (SecretConfig): Secret configuration to generate SQL for

**Returns:**
- `str`: SQL statement creating the secret with proper escaping

**Note:** This function enforces strict type checking for secret options and will raise `TypeError` for unsupported types (non-bool, int, float, or str values).

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

Duckalog uses a consistent exception hierarchy based on `DuckalogError` as the base class for all library exceptions. This provides a unified error handling interface and makes it easy to catch all Duckalog-specific errors.

### Base Exception

#### DuckalogError

Base exception for all Duckalog-specific errors. You can catch this class to handle any Duckalog-related error, or catch more specific subclasses for targeted error handling.

```python
from duckalog import DuckalogError

try:
    config = load_config("catalog.yaml")
    build_catalog(config)
except DuckalogError as e:
    # Handle any Duckalog-specific error
    print(f"Duckalog error: {e}")
```

### Configuration Errors

#### ConfigError

Raised for configuration-related errors including parsing, validation, and path resolution failures. Inherits from `DuckalogError`.

```python
from duckalog import load_config, ConfigError

try:
    config = load_config("catalog.yaml")
except ConfigError as e:
    print(f"Configuration error: {e}")
```

**Common scenarios:**
- Missing required configuration fields
- Invalid YAML/JSON syntax
- Unresolved environment variable placeholders (`${env:VAR}`)
- Invalid view definitions

#### PathResolutionError

Raised specifically when path resolution fails due to security or access issues. Inherits from `ConfigError`.

```python
from duckalog import PathResolutionError, resolve_relative_path
from pathlib import Path

try:
    resolved = resolve_relative_path("../../../etc/passwd", Path("/project/config"))
except PathResolutionError as e:
    print(f"Path resolution failed: {e}")
    print(f"Original path: {e.original_path}")
    print(f"Resolved path: {e.resolved_path}")
```

#### RemoteConfigError

Raised when remote configuration loading fails. Inherits from `ConfigError`.

```python
from duckalog import RemoteConfigError, load_config_from_uri

try:
    config = load_config_from_uri("s3://bucket/config.yaml")
except RemoteConfigError as e:
    print(f"Remote config error: {e}")
```

### SQL File Errors

#### SQLFileError

Base exception for SQL file-related errors. Inherits from `DuckalogError`.

```python
from duckalog import SQLFileError

try:
    # Operations that load SQL from files
    pass
except SQLFileError as e:
    print(f"SQL file error: {e}")
```

**Subclasses for specific SQL file errors:**
- `SQLFileNotFoundError`: Referenced SQL file does not exist
- `SQLFilePermissionError`: SQL file cannot be read due to permissions
- `SQLFileEncodingError`: SQL file has invalid encoding
- `SQLFileSizeError`: SQL file exceeds size limits
- `SQLTemplateError`: Template processing fails

### Engine Errors

#### EngineError

Raised during catalog builds when DuckDB operations fail. Inherits from `DuckalogError`.

```python
from duckalog import EngineError, build_catalog

try:
    build_catalog("catalog.yaml")
except EngineError as e:
    print(f"Engine error: {e}")
```

**Common scenarios:**
- DuckDB connection failures
- SQL execution errors
- Attachment setup failures
- Extension installation/loading errors
- Secret creation failures

### Exception Chaining

All Duckalog exceptions support proper exception chaining to preserve the original error context:

```python
from duckalog import EngineError

try:
    # Some operation that fails
    raise ValueError("Original database connection failed")
except ValueError as exc:
    raise EngineError("Failed to connect to DuckDB") from exc
```

This preserves the full traceback and makes debugging much easier.

## Generated API Documentation

This section is generated from the Duckalog source code using mkdocstrings.

::: duckalog

