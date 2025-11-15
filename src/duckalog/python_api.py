"""High-level Python convenience functions for Duckalog."""

from __future__ import annotations

from .config import ConfigError, load_config
from .sql_generation import generate_all_views_sql


def generate_sql(config_path: str) -> str:
    """Load a config from ``config_path`` and return the full CREATE VIEW SQL."""

    config = load_config(config_path)
    return generate_all_views_sql(config)


def validate_config(config_path: str) -> None:
    """Validate a configuration file, raising ConfigError on failure."""

    try:
        load_config(config_path)
    except ConfigError:
        raise


__all__ = ["generate_sql", "validate_config"]
