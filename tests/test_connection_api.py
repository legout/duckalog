"""Tests for DuckDB connection API functions."""

from __future__ import annotations

import tempfile
from pathlib import Path


import duckdb
import pytest
import yaml

from duckalog import ConfigError, Config, ViewConfig
from duckalog.python_api import (
    connect_to_catalog,
    connect_to_catalog_cm,
)


@pytest.fixture
def sample_config():
    """Create a sample configuration for testing."""
    from duckalog import DuckDBConfig

    return Config(
        version=1,
        duckdb=DuckDBConfig(database=":memory:"),
        views=[
            ViewConfig(
                name="test_view",
                sql="SELECT 1 as id, 'test' as name",
                description="Test view",
                tags=["test"],
            ),
        ],
    )


@pytest.fixture
def sample_config_path(sample_config):
    """Create a temporary config file path."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        yaml.dump(sample_config.model_dump(), f, default_flow_style=False)
        return f.name


class TestConnectToCatalog:
    """Test cases for connect_to_catalog function."""

    def test_connect_to_existing_catalog(self, sample_config_path: str):
        """Test connecting to an existing catalog database."""
        # First build a catalog to connect to
        from duckalog.engine import build_catalog

        build_catalog(sample_config_path)

        # Now connect to it
        catalog = connect_to_catalog(sample_config_path)
        conn = catalog.get_connection()

        assert conn is not None
        assert isinstance(conn, duckdb.DuckDBPyConnection)

        # Test that we can execute queries
        result = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
        assert isinstance(result, list)

        catalog.close()

    def test_connect_with_database_path_override(self, sample_config_path: str):
        """Test connecting with a custom database path override."""
        # Use a path that doesn't exist yet so DuckDB creates it
        tmp_dir = tempfile.gettempdir()
        tmp_path = str(Path(tmp_dir) / "test_override.duckdb")
        if Path(tmp_path).exists():
            Path(tmp_path).unlink()

        try:
            # Create a database at the custom path
            conn = duckdb.connect(tmp_path)
            conn.execute("CREATE TABLE test_table (id INTEGER)")
            conn.close()

            # Connect using the override
            catalog = connect_to_catalog(sample_config_path, database_path=tmp_path)
            conn = catalog.get_connection()

            result = conn.execute("SELECT * FROM test_table").fetchall()
            assert result == []

            catalog.close()
        finally:
            Path(tmp_path).unlink(missing_ok=True)

    def test_connect_read_only_mode(self, sample_config):
        """Test connecting in read-only mode with a persistent database."""
        # We need a persistent database for read-only test, as :memory: doesn't support it
        with tempfile.NamedTemporaryFile(suffix=".duckdb", delete=False) as tmp:
            db_path = tmp.name
        Path(db_path).unlink()  # Delete so duckdb can create it

        sample_config.duckdb.database = db_path
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(sample_config.model_dump(), f, default_flow_style=False)
            cfg_path = f.name

        try:
            from duckalog.engine import build_catalog

            build_catalog(cfg_path)

            catalog = connect_to_catalog(cfg_path, read_only=True)
            conn = catalog.get_connection()

            # Should be able to read
            result = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
            assert isinstance(result, list)

            # Should not be able to write (this will raise an exception)
            with pytest.raises(duckdb.Error):
                conn.execute("CREATE TABLE test_table (id INTEGER)")

            catalog.close()
        finally:
            Path(db_path).unlink(missing_ok=True)
            Path(cfg_path).unlink(missing_ok=True)

    def test_connect_to_in_memory_database(self, sample_config_path: str):
        """Test connecting to an in-memory database."""
        catalog = connect_to_catalog(sample_config_path, database_path=":memory:")
        conn = catalog.get_connection()

        assert conn is not None
        assert isinstance(conn, duckdb.DuckDBPyConnection)

        # In-memory database should be empty
        result = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
        assert result == []

        catalog.close()

    def test_connect_nonexistent_database(self, sample_config_path: str):
        """Test connecting to a non-existent database raises FileNotFoundError."""
        catalog = connect_to_catalog(
            sample_config_path, database_path="/nonexistent/path.db"
        )
        with pytest.raises(FileNotFoundError, match="Database file not found"):
            catalog.get_connection()

    def test_connect_invalid_config(self):
        """Test connecting with invalid config raises ConfigError."""
        catalog = connect_to_catalog("/nonexistent/config.yaml")
        with pytest.raises(ConfigError):
            catalog.get_connection()


class TestConnectToCatalogCm:
    """Test cases for connect_to_catalog_cm context manager."""

    def test_context_manager_automatic_cleanup(self, sample_config_path: str):
        """Test that context manager automatically closes connection."""
        from duckalog.engine import build_catalog

        build_catalog(sample_config_path)

        with connect_to_catalog_cm(sample_config_path) as conn:
            assert conn is not None
            assert isinstance(conn, duckdb.DuckDBPyConnection)

            # Should be able to execute queries
            result = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
            assert isinstance(result, list)

        # Connection should be closed after exiting context
        # Trying to use it should raise an exception
        with pytest.raises(duckdb.Error):
            conn.execute("SELECT 1")

    def test_context_manager_with_exception(self, sample_config_path: str):
        """Test that context manager closes connection even when exception occurs."""
        from duckalog.engine import build_catalog

        build_catalog(sample_config_path)

        connection_ref = None
        with pytest.raises(ValueError):
            with connect_to_catalog_cm(sample_config_path) as conn:
                assert conn is not None
                connection_ref = conn
                raise ValueError("Test exception")

        # Connection should still be closed despite the exception
        if connection_ref is not None:
            with pytest.raises(duckdb.Error):
                connection_ref.execute("SELECT 1")

    def test_context_manager_with_path_override(self, sample_config_path: str):
        """Test context manager with database path override."""
        # Use a path that doesn't exist yet
        tmp_dir = tempfile.gettempdir()
        tmp_path = str(Path(tmp_dir) / "test_cm_override.duckdb")
        if Path(tmp_path).exists():
            Path(tmp_path).unlink()

        try:
            # Create a database at the custom path
            conn = duckdb.connect(tmp_path)
            conn.execute("CREATE TABLE test_table (id INTEGER)")
            conn.close()

            # Use context manager with override
            with connect_to_catalog_cm(
                sample_config_path, database_path=tmp_path
            ) as conn:
                result = conn.execute("SELECT * FROM test_table").fetchall()
                assert result == []
        finally:
            Path(tmp_path).unlink(missing_ok=True)


class TestIntegrationWorkflow:
    """Integration tests for complete user workflows."""

    def test_config_to_queries_workflow(self, sample_config_path: str):
        """Test complete workflow from config to executing queries."""
        # Method 1: Build then connect
        from duckalog.engine import build_catalog

        build_catalog(sample_config_path)

        catalog = connect_to_catalog(sample_config_path)
        conn = catalog.get_connection()

        # Execute some queries
        tables = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
        assert isinstance(tables, list)

        catalog.close()

    def test_context_manager_workflow(self, sample_config_path: str):
        """Test workflow using context manager for automatic cleanup."""
        with connect_to_catalog_cm(sample_config_path) as conn:
            tables = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
            assert isinstance(tables, list)

        # Connection is automatically closed

    def test_build_and_connect_context_manager_workflow(self, sample_config_path: str):
        """Test workflow combining build and connect with context manager."""
        # Build first, then use context manager
        from duckalog.engine import build_catalog
        build_catalog(sample_config_path)

        with connect_to_catalog_cm(sample_config_path) as conn:
            tables = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
            assert isinstance(tables, list)
