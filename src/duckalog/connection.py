"""DuckDB connection management with session state restoration."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Optional

import duckdb

from .config import (
    Config,
    load_config,
    get_logger,
    log_debug,
    log_info,
    log_error,
    ConfigError,
)
from .engine import (
    _apply_catalog_state,
    _resolve_db_path,
    _create_views,
)
from .sql_generation import generate_view_sql
from .errors import EngineError

logger = get_logger()


class CatalogConnection:
    """Manages DuckDB connections with session state restoration and lazy initialization.

    This class ensures that every connection obtained through it has the correct
    catalog state (pragmas, settings, extensions, attachments, and secrets)
    applied, regardless of whether it's a new or existing connection.

    Attributes:
        config_path: Path to the Duckalog configuration file.
        database_path: Optional override for the DuckDB database path.
        read_only: Whether to open the connection in read-only mode.
        force_rebuild: If True, all views will be recreated even if they exist.
        config: The loaded and validated configuration.
        conn: The active DuckDB connection, or None if not initialized.
    """

    def __init__(
        self,
        config_path: str,
        database_path: Optional[str] = None,
        read_only: bool = False,
        force_rebuild: bool = False,
        filesystem: Optional[Any] = None,
        load_dotenv: bool = True,
    ):
        """Initialize the catalog connection manager.

        Args:
            config_path: Path to the Duckalog configuration file.
            database_path: Optional override for the DuckDB database path.
            read_only: Whether to open the connection in read-only mode.
            force_rebuild: If True, all views will be recreated even if they exist.
            filesystem: Optional fsspec filesystem object for remote file access.
            load_dotenv: If True, automatically load and process .env files.
        """
        # Only resolve if it's not a remote URI
        from .remote_config import is_remote_uri

        if is_remote_uri(config_path):
            self.config_path = config_path
        else:
            self.config_path = str(Path(config_path).resolve())

        self.database_path = database_path
        self.read_only = read_only
        self.force_rebuild = force_rebuild
        self.filesystem = filesystem
        self.load_dotenv = load_dotenv
        self.config: Optional[Config] = None
        self.conn: Optional[duckdb.DuckDBPyConnection] = None

    def get_connection(self) -> duckdb.DuckDBPyConnection:
        """Get the DuckDB connection, initializing it if necessary.

        This method establishes the connection lazily on the first call,
        restores the session state, and performs incremental updates.
        Subsequent calls return the same connection instance.

        Returns:
            An active DuckDB connection with catalog state restored.

        Raises:
            ConfigError: If loading the configuration fails.
            FileNotFoundError: If the database path is invalid or missing (for existing catalogs).
            EngineError: If connecting to DuckDB or restoring state fails.
        """
        if self.conn is not None:
            return self.conn

        try:
            if self.config is None:
                self.config = load_config(
                    self.config_path,
                    filesystem=self.filesystem,
                    load_dotenv=self.load_dotenv,
                )

            db_path = _resolve_db_path(self.config, self.database_path)

            # Compatibility check for existing tests
            if db_path != ":memory:" and not Path(db_path).exists() and self.read_only:
                # DuckDB would fail anyway, but we raise FileNotFoundError for compatibility
                # Wait, only if we are not creating it.
                # Actually, the old code raised FileNotFoundError if it didn't exist.
                pass

            # If it's not :memory: and doesn't exist, we might want to fail early if expected
            if db_path != ":memory:":
                p = Path(db_path)
                if not p.exists() and (
                    self.read_only or not self.force_rebuild and self.database_path
                ):
                    # This matches the behavior in the previous connect_to_catalog
                    raise FileNotFoundError(f"Database file not found: {db_path}")

            log_info(
                "Establishing lazy DuckDB connection",
                db_path=db_path,
                read_only=self.read_only,
            )

            try:
                self.conn = duckdb.connect(db_path, read_only=self.read_only)
            except duckdb.CatalogException as e:
                if "in-memory database in read-only mode" in str(e):
                    # In-memory databases cannot be read-only
                    log_debug("Falling back to read-write for in-memory database")
                    self.conn = duckdb.connect(db_path, read_only=False)
                else:
                    raise

            # Restore all session-specific state
            log_info("Restoring catalog session state")
            _apply_catalog_state(
                self.conn, self.config, create_views=False, verbose=False
            )
            self._update_views()

            log_info(
                "Catalog connection initialized successfully",
                db_path=db_path,
                views_count=len(self.config.views),
            )
            return self.conn

        except (ConfigError, FileNotFoundError):
            # Pass through known errors
            self.close()
            raise
        except Exception as exc:
            # Clean up if partially initialized
            self.close()
            if isinstance(exc, EngineError):
                raise
            raise EngineError(
                f"Failed to initialize catalog connection: {exc}"
            ) from exc

    def _update_views(self) -> None:
        """Incremental view creation: only create missing views unless force_rebuild is True."""
        if not self.conn or not self.config:
            return

        if self.force_rebuild:
            log_info("Force rebuild requested, recreating all views")
            try:
                _create_views(self.conn, self.config, verbose=False)
                return
            except Exception as e:
                log_error("Failed to rebuild views", error=str(e))
                raise EngineError(f"Failed to rebuild views: {e}") from e

        # Get existing views to avoid redundant creation
        log_debug("Checking for existing views (incremental update)")
        try:
            # Try duckdb_views() first (DuckDB-specific)
            existing_views = self.conn.execute(
                "SELECT view_name, schema_name FROM duckdb_views()"
            ).fetchall()
            existing_set = {(row[0], row[1]) for row in existing_views}
        except Exception:
            # Fallback to information_schema
            try:
                existing_views = self.conn.execute(
                    "SELECT table_name, table_schema FROM information_schema.views"
                ).fetchall()
                existing_set = {(row[0], row[1]) for row in existing_views}
            except Exception as e:
                log_error("Failed to query existing views", error=str(e))
                # If we can't check, assume we should try creating them all
                existing_set = set()

        views_to_create = []
        for view in self.config.views:
            schema = view.db_schema or "main"
            if (view.name, schema) not in existing_set:
                views_to_create.append(view)
            else:
                log_debug(
                    "View already exists, skipping", name=view.name, schema=schema
                )

        if views_to_create:
            log_info("Creating missing views", count=len(views_to_create))
            # Ensure schemas exist before creating views
            schemas_to_create = sorted(
                {v.db_schema for v in views_to_create if v.db_schema}
            )
            for schema in schemas_to_create:
                from .sql_generation import generate_create_schema_sql

                sql = generate_create_schema_sql(schema)
                log_debug("Creating schema if not exists", schema=schema)
                self.conn.execute(sql)

            for view in views_to_create:
                try:
                    sql = generate_view_sql(view)
                    self.conn.execute(sql)
                except Exception as e:
                    log_error("Failed to create view", name=view.name, error=str(e))
                    raise EngineError(
                        f"Failed to create view '{view.name}': {e}"
                    ) from e

    def close(self) -> None:
        """Clean up the DuckDB connection and resources."""
        if self.conn:
            log_debug("Closing catalog connection")
            try:
                self.conn.close()
            except Exception as e:
                log_debug("Error closing connection", error=str(e))
            self.conn = None

    def __enter__(self) -> "CatalogConnection":
        """Context manager support: returns the CatalogConnection instance."""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager support: ensures connection cleanup."""
        self.close()


def connect_to_catalog(
    config_path: str,
    database_path: Optional[str] = None,
    read_only: bool = False,
    force_rebuild: bool = False,
    filesystem: Optional[Any] = None,
    load_dotenv: bool = True,
) -> CatalogConnection:
    """Create and return a CatalogConnection instance.

    This helper function creates a CatalogConnection manager that handles
    lazy initialization and session state restoration.

    Example:
        >>> with connect_to_catalog("catalog.yaml") as catalog:
        ...     conn = catalog.get_connection()
        ...     result = conn.execute("SELECT * FROM my_view").fetchall()

    Args:
        config_path: Path to the Duckalog configuration file.
        database_path: Optional override for the DuckDB database path.
        read_only: Whether to open the connection in read-only mode.
        force_rebuild: If True, all views will be recreated even if they exist.
        filesystem: Optional fsspec filesystem object for remote file access.
        load_dotenv: If True, automatically load and process .env files.

    Returns:
        A CatalogConnection instance ready for use.
    """
    return CatalogConnection(
        config_path,
        database_path=database_path,
        read_only=read_only,
        force_rebuild=force_rebuild,
        filesystem=filesystem,
        load_dotenv=load_dotenv,
    )
