"""High-level Python convenience functions for Duckalog."""

from __future__ import annotations

import duckdb
from contextlib import contextmanager
from pathlib import Path
from collections.abc import Generator
from typing import Any, Optional

from .config import ConfigError, load_config
from .engine import build_catalog
from .sql_generation import generate_all_views_sql
from .connection import CatalogConnection, connect_to_catalog as _connect_to_catalog


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


def connect_to_catalog(
    config_path: str,
    database_path: str | None = None,
    read_only: bool = False,
    force_rebuild: bool = False,
) -> CatalogConnection:
    """Create a CatalogConnection instance that manages DuckDB connections with state restoration.

    This is the primary entry point for working with Duckalog catalogs in Python.
    It returns a :class:`CatalogConnection` instance which lazily establishes
    a DuckDB connection and automatically restores session state (pragmas,
    attachments, etc.) and performs incremental view updates.

    Args:
        config_path: Path to the YAML/JSON configuration file.
        database_path: Optional database path override.
        read_only: Open the connection in read-only mode for safety.
        force_rebuild: If True, all views will be recreated even if they exist.

    Returns:
        A :class:`CatalogConnection` instance.

    Example:
        Using as a context manager::

            from duckalog import connect_to_catalog
            with connect_to_catalog("catalog.yaml") as catalog:
                conn = catalog.get_connection()
                result = conn.execute("SELECT * FROM my_view").fetchall()

        Using for persistent state management::

            catalog = connect_to_catalog("catalog.yaml")
            conn1 = catalog.get_connection()
            # ... later ...
            conn2 = catalog.get_connection()  # Returns the same connection
            catalog.close()
    """
    return _connect_to_catalog(
        config_path=config_path,
        database_path=database_path,
        read_only=read_only,
        force_rebuild=force_rebuild,
    )


@contextmanager
def connect_to_catalog_cm(
    config_path: str,
    database_path: str | None = None,
    read_only: bool = False,
    force_rebuild: bool = False,
) -> Generator[duckdb.DuckDBPyConnection]:
    """Context manager that yields an active, state-restored DuckDB connection.

    This provides the same state restoration and incremental update benefits
    as :class:`CatalogConnection`, but yields the raw DuckDB connection object
    for convenience in simple scripts.

    Usage::

        from duckalog import connect_to_catalog_cm
        with connect_to_catalog_cm("catalog.yaml") as conn:
            data = conn.execute("SELECT * FROM users").fetchall()
            print(f"Found {len(data)} records")
        # Connection automatically closed here

    Args:
        config_path: Path to the YAML/JSON configuration file.
        database_path: Optional database path override.
        read_only: Open the connection in read-only mode for safety.
        force_rebuild: If True, all views will be recreated.

    Yields:
        An active DuckDB connection with catalog state restored.
    """
    with _connect_to_catalog(
        config_path=config_path,
        database_path=database_path,
        read_only=read_only,
        force_rebuild=force_rebuild,
    ) as catalog:
        yield catalog.get_connection()


def connect_and_build_catalog(
    config_path: str,
    database_path: str | None = None,
    dry_run: bool = False,
    verbose: bool = False,
    read_only: bool = False,
    **kwargs: Any,
) -> duckdb.DuckDBPyConnection | str | None:
    """Build a catalog and create a DuckDB connection in one operation.

    .. deprecated:: 0.6.0
        Use :func:`connect_to_catalog` or :func:`connect_to_catalog_cm` instead.
        Those functions provide smarter connection management and incremental updates.

    Args:
        config_path: Path to the YAML/JSON configuration file.
        database_path: Optional database path override.
        dry_run: If True, only validates configuration and returns SQL.
        verbose: Enable verbose logging during build process.
        read_only: Open the resulting connection in read-only mode.
        **kwargs: Additional keyword arguments.

    Returns:
        A DuckDB connection object for immediate use, or SQL string when dry_run=True.
    """
    import warnings

    warnings.warn(
        "connect_and_build_catalog() is deprecated. Use connect_to_catalog() instead.",
        DeprecationWarning,
        stacklevel=2,
    )

    if dry_run:
        return build_catalog(
            config_path,
            db_path=database_path,
            dry_run=True,
            verbose=verbose,
            filesystem=kwargs.get("filesystem"),
        )

    # Extract build kwargs that aren't for the connection
    build_kwargs = {k: v for k, v in kwargs.items() if k in ["filesystem"]}

    # Build first in read-write mode to ensure it exists and is up to date
    build_catalog(
        config_path=config_path,
        db_path=database_path,
        dry_run=False,
        verbose=verbose,
        **build_kwargs,
    )

    # Then return a connection in the requested mode
    catalog = _connect_to_catalog(
        config_path=config_path,
        database_path=database_path,
        read_only=read_only,
        force_rebuild=False,  # Already built above
    )
    return catalog.get_connection()


def validate_generated_config(content: str, format: str = "yaml") -> None:
    """Validate that generated configuration content can be loaded successfully."""
    from tempfile import NamedTemporaryFile

    try:
        with NamedTemporaryFile(mode="w", suffix=f".{format}", delete=False) as f:
            f.write(content)
            temp_path = f.name

        try:
            load_config(temp_path, load_sql_files=False)
        finally:
            import os

            os.unlink(temp_path)

    except Exception as exc:
        raise ConfigError(f"Generated configuration validation failed: {exc}") from exc


__all__ = [
    "CatalogConnection",
    "generate_sql",
    "validate_config",
    "connect_to_catalog",
    "connect_to_catalog_cm",
    "connect_and_build_catalog",
    "validate_generated_config",
]
