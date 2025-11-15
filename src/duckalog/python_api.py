"""High-level Python convenience functions for Duckalog."""

from __future__ import annotations

from .config import ConfigError, load_config
from .sql_generation import generate_all_views_sql


def generate_sql(config_path: str) -> str:
    """Generate a full SQL script from a config file.

    This is a convenience wrapper around :func:`load_config` and
    :func:`generate_all_views_sql` that does not connect to DuckDB.

    Args:
        config_path: Path to the YAML/JSON configuration file.

    Returns:
        A multi-statement SQL script containing ``CREATE OR REPLACE VIEW``
        statements for all configured views.

    Raises:
        ConfigError: If the configuration file is invalid.

    Example:
        >>> from duckalog import generate_sql
        >>> sql = generate_sql("catalog.yaml")
        >>> print("CREATE VIEW" in sql)
        True
    """

    config = load_config(config_path)
    return generate_all_views_sql(config)


def validate_config(config_path: str) -> None:
    """Validate a configuration file without touching DuckDB.

    Args:
        config_path: Path to the YAML/JSON configuration file.

    Raises:
        ConfigError: If the configuration file is missing, malformed, or does
            not satisfy the schema and interpolation rules.

    Example:
        >>> from duckalog import validate_config
        >>> validate_config("catalog.yaml")  # raises on invalid config
    """

    try:
        load_config(config_path)
    except ConfigError:
        raise


__all__ = ["generate_sql", "validate_config"]
