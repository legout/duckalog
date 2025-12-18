"""Configuration package for Duckalog catalogs.

This package provides a unified configuration layer that consolidates:
- Configuration schema definitions and validation (Pydantic models)
- Path resolution utilities with security validation
- SQL file loading and template processing
- Logging with automatic sensitive data redaction

The consolidation reduces complexity by eliminating separate modules for path resolution,
SQL file loading, and logging utilities, while maintaining the same public API.

## Key Functions

### Configuration Loading
- `load_config()`: Main entry point for loading configuration files
- `load_config_with_context()`: Load config with additional context information
- `load_config_with_schema()`: Load config using a custom schema class

### Path Resolution
- `is_relative_path()`: Detect if a path is relative
- `resolve_relative_path()`: Resolve relative paths to absolute paths
- `validate_path_security()`: Validate path security boundaries
- `normalize_path_for_sql()`: Normalize paths for SQL usage

### SQL File Processing
- Internal functions for loading SQL content from external files
- Template processing with variable substitution
- Security validation of SQL content

### Logging Utilities
- `log_info()`, `log_debug()`, `log_error()`: Redacted logging functions
- Automatic detection and redaction of sensitive data
"""

# Import all models and functions from the individual modules
# This maintains backward compatibility for existing imports

# Import models first (these are the foundation and don't have circular dependencies)
from .models import (
    Config,
    DuckDBConfig,
    SecretConfig,
    AttachmentsConfig,
    DuckDBAttachment,
    SQLiteAttachment,
    PostgresAttachment,
    DuckalogAttachment,
    IcebergCatalogConfig,
    ViewConfig,
    SemanticModelConfig,
    SemanticDimensionConfig,
    SemanticMeasureConfig,
    SemanticJoinConfig,
    SemanticDefaultsConfig,
    SQLFileReference,
)

# Import errors
from duckalog.errors import ConfigError

# Import path resolution and validation functions (these can import from models)
from .validators import (
    is_relative_path,
    resolve_relative_path,
    validate_path_security,
    normalize_path_for_sql,
    is_within_allowed_roots,
    is_windows_path_absolute,
    detect_path_type,
    validate_file_accessibility,
    log_info,
    log_debug,
    log_warning,
    log_error,
    get_logger,
)

# Import internal helper for testing compatibility
from .api import _load_config_from_local_file, load_config as api_load_config

from typing import Any, Optional


def _call_with_monkeypatched_callable(target, *args, **kwargs):
    """Helper to handle monkeypatched callables with func/return_value attributes."""
    if hasattr(target, "func") and target.func is not None:
        return target.func(*args, **kwargs)
    elif hasattr(target, "return_value") and target.return_value is not None:
        return target.return_value
    else:
        return target(*args, **kwargs)


def load_config(
    path: str,
    load_sql_files: bool = True,
    sql_file_loader: Optional[Any] = None,
    resolve_paths: bool = True,
    filesystem: Optional[Any] = None,
    load_dotenv: bool = True,
) -> Config:
    """Load, interpolate, and validate a Duckalog configuration file."""
    return api_load_config(
        path=path,
        load_sql_files=load_sql_files,
        sql_file_loader=sql_file_loader,
        resolve_paths=resolve_paths,
        filesystem=filesystem,
        load_dotenv=load_dotenv,
    )


# Define the public API - all symbols that should be available for import
__all__ = [
    # Configuration models
    "Config",
    "ConfigError",
    "DuckDBConfig",
    "SecretConfig",
    "AttachmentsConfig",
    "DuckDBAttachment",
    "SQLiteAttachment",
    "PostgresAttachment",
    "DuckalogAttachment",
    "IcebergCatalogConfig",
    "ViewConfig",
    "SemanticModelConfig",
    "SemanticDimensionConfig",
    "SemanticMeasureConfig",
    "SemanticJoinConfig",
    "SemanticDefaultsConfig",
    "SQLFileReference",
    # Configuration loading
    "load_config",
    "_load_config_from_local_file",
    # Path resolution functions
    "is_relative_path",
    "resolve_relative_path",
    "validate_path_security",
    "normalize_path_for_sql",
    "is_within_allowed_roots",
    "is_windows_path_absolute",
    "detect_path_type",
    "validate_file_accessibility",
    # Logging utilities
    "get_logger",
    "log_info",
    "log_debug",
    "log_warning",
    "log_error",
]
