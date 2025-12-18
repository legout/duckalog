"""Duckalog public API."""

# Configuration & Models
from .config import (
    AttachmentsConfig,
    Config,
    DuckDBAttachment,
    DuckDBConfig,
    IcebergCatalogConfig,
    PostgresAttachment,
    SQLFileReference,
    SQLiteAttachment,
    SecretConfig,
    SemanticDefaultsConfig,
    SemanticDimensionConfig,
    SemanticJoinConfig,
    SemanticMeasureConfig,
    SemanticModelConfig,
    ViewConfig,
    load_config,
)
from .config_init import (
    ConfigFormat,
    create_config_template,
    validate_generated_config,
)

# Core Connection & Engine
from .connection import CatalogConnection
from .engine import build_catalog
from .python_api import (
    connect_and_build_catalog,
    connect_to_catalog,
    connect_to_catalog_cm,
    generate_sql,
    validate_config,
)

# SQL Functionality
from . import sql_file_loader as sql_files
from . import sql_generation as sql
from . import sql_utils as utils
from .sql_file_loader import SQLFileLoader
from .sql_generation import (
    generate_all_views_sql,
    generate_secret_sql,
    generate_view_sql,
)
from .sql_utils import (
    quote_ident,
    quote_literal,
    render_options,
)

# Errors
from .errors import (
    ConfigError,
    EngineError,
    SQLFileEncodingError,
    SQLFileError,
    SQLFileNotFoundError,
    SQLFilePermissionError,
    SQLFileSizeError,
    SQLTemplateError,
)


# Convenience group for SQL functionality
class SQLGroup:
    """Unified access to all SQL-related functionality."""

    generate = sql
    utils = utils
    files = sql_files


__all__ = [
    # Connection & Engine
    "CatalogConnection",
    "connect_to_catalog",
    "connect_to_catalog_cm",
    "connect_and_build_catalog",
    "build_catalog",
    # Configuration & Models
    "Config",
    "load_config",
    "validate_config",
    "AttachmentsConfig",
    "DuckDBConfig",
    "DuckDBAttachment",
    "SQLiteAttachment",
    "PostgresAttachment",
    "IcebergCatalogConfig",
    "ViewConfig",
    "SecretConfig",
    "SemanticModelConfig",
    "SemanticDimensionConfig",
    "SemanticMeasureConfig",
    "SemanticJoinConfig",
    "SemanticDefaultsConfig",
    "SQLFileReference",
    # SQL Convenience Groups
    "SQLGroup",
    "sql",
    "utils",
    "sql_files",
    # SQL Generation
    "generate_sql",
    "generate_view_sql",
    "generate_all_views_sql",
    "generate_secret_sql",
    # SQL Utilities
    "quote_ident",
    "quote_literal",
    "render_options",
    # SQL File Loading
    "SQLFileLoader",
    # Configuration Initialization
    "create_config_template",
    "validate_generated_config",
    "ConfigFormat",
    # Errors
    "ConfigError",
    "EngineError",
    "SQLFileError",
    "SQLFileNotFoundError",
    "SQLFilePermissionError",
    "SQLFileEncodingError",
    "SQLFileSizeError",
    "SQLTemplateError",
]
