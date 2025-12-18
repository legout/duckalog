"""Dashboard state management and context."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

import duckdb
from loguru import logger

from duckalog.config import Config


@dataclass
class DashboardContext:
    """Context for the dashboard application.

    Manages configuration, database connection, and provides
    methods for querying the catalog.
    """

    config: Config
    config_path: str
    db_path: str | None = None
    row_limit: int = 1000
    _connection: duckdb.DuckDBPyConnection | None = field(default=None, repr=False)
    _startup_complete: bool = field(default=False, repr=False)

    def _get_timestamp(self) -> str:
        """Get current timestamp as ISO format string."""
        return datetime.now().isoformat()

    def __post_init__(self) -> None:
        """Initialize the database connection."""
        self._ensure_connection()

    def _ensure_connection(self) -> duckdb.DuckDBPyConnection:
        """Ensure database connection exists."""
        if self._connection is None:
            if self.db_path:
                self._connection = duckdb.connect(self.db_path, read_only=True)
                logger.debug(f"Connected to database: {self.db_path}")
            else:
                self._connection = duckdb.connect(":memory:")
                logger.debug("Connected to in-memory database")
        return self._connection

    @property
    def connection(self) -> duckdb.DuckDBPyConnection:
        """Get the database connection."""
        return self._ensure_connection()

    def get_views(self) -> list[dict[str, Any]]:
        """Get list of all views in the catalog."""
        views = []
        for view in self.config.views:
            views.append(
                {
                    "name": view.name,
                    "schema": view.db_schema or "main",
                    "description": view.description or "",
                    "source_type": view.source if view.source else "sql",
                }
            )
        return views

    def get_view(self, name: str) -> dict[str, Any] | None:
        """Get a specific view by name."""
        for view in self.config.views:
            if view.name == name:
                return {
                    "name": view.name,
                    "schema": view.db_schema or "main",
                    "description": view.description or "",
                    "source": view.source if view.source else "sql",
                    "sql": view.sql,
                }
        return None

    async def execute_query(
        self, sql: str, limit: int | None = None, batch_size: int = 50
    ) -> AsyncGenerator[tuple[list[str], list[tuple[Any, ...]]], None]:
        """Execute a SQL query and stream results in batches.

        Args:
            sql: SQL query to execute
            limit: Optional row limit (defaults to self.row_limit)
            batch_size: Number of rows to fetch per batch (default: 50)

        Yields:
            First yield: (column_names, []) - headers with empty rows
            Subsequent yields: ([], rows) - batches of row data

        Raises:
            ValueError: If query is not read-only
        """
        # Basic read-only check
        sql_upper = sql.strip().upper()
        if not sql_upper.startswith(("SELECT", "WITH", "SHOW", "DESCRIBE", "EXPLAIN")):
            raise ValueError("Only read-only queries are allowed")

        effective_limit = limit or self.row_limit

        # Create a queue to stream data from thread to async context
        queue: asyncio.Queue[tuple[list[str], list[tuple[Any, ...]]] | None] = asyncio.Queue()

        # Execute query in thread pool to avoid blocking event loop
        # Note: We create a new connection in the thread because DuckDB
        # connections are not thread-safe
        def _execute_stream():
            # Create a new connection for this thread
            if self.db_path:
                conn = duckdb.connect(self.db_path, read_only=True)
            else:
                conn = duckdb.connect(":memory:")
            try:
                result = conn.execute(sql)
                columns = [desc[0] for desc in result.description or []]

                # First put: column headers
                queue.put_nowait((columns, []))

                # Stream rows in batches
                rows_fetched = 0
                while rows_fetched < effective_limit:
                    batch = result.fetchmany(min(batch_size, effective_limit - rows_fetched))
                    if not batch:
                        break
                    rows_fetched += len(batch)
                    queue.put_nowait(([], batch))

                # Signal completion
                queue.put_nowait(None)
            except Exception:
                # Put error marker and re-raise
                queue.put_nowait(None)
                raise
            finally:
                conn.close()

        # Start the thread
        asyncio.create_task(asyncio.to_thread(_execute_stream))

        # Yield batches as they become available
        while True:
            batch = await queue.get()
            if batch is None:
                # End of stream or error
                break
            columns, rows = batch
            yield columns, rows

    def get_catalog_stats(self) -> dict[str, int]:
        """Get catalog statistics."""
        return {
            "total_views": len(self.config.views),
            "schemas": len(set(v.db_schema or "main" for v in self.config.views)),
        }

    def close(self) -> None:
        """Close the database connection."""
        if self._connection is not None:
            self._connection.close()
            self._connection = None
            logger.debug("Database connection closed")
