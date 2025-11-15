"""Duckalog public API."""

from .config import (
    AttachmentsConfig,
    Config,
    ConfigError,
    DuckDBAttachment,
    DuckDBConfig,
    IcebergCatalogConfig,
    PostgresAttachment,
    SQLiteAttachment,
    ViewConfig,
    load_config,
)
from .engine import EngineError, build_catalog
from .sql_generation import (
    generate_all_views_sql,
    generate_view_sql,
    quote_ident,
    render_options,
)
from .python_api import generate_sql, validate_config

__all__ = [
    "Config",
    "ConfigError",
    "DuckDBConfig",
    "AttachmentsConfig",
    "DuckDBAttachment",
    "SQLiteAttachment",
    "PostgresAttachment",
    "IcebergCatalogConfig",
    "ViewConfig",
    "load_config",
    "build_catalog",
    "EngineError",
    "generate_sql",
    "validate_config",
    "quote_ident",
    "render_options",
    "generate_view_sql",
    "generate_all_views_sql",
]
