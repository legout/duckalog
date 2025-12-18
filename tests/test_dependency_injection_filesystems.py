import os
import tempfile
from pathlib import Path
from typing import Any, Optional, Union
from unittest.mock import Mock, patch, MagicMock

import pytest
import yaml
from fsspec.implementations.memory import MemoryFileSystem

from duckalog.config import load_config, Config, ConfigError
from duckalog.sql_file_loader import SQLFileLoader
from duckalog.errors import PathResolutionError


class CustomMockFilesystem:
    """A minimal custom filesystem implementation for testing DI."""

    def __init__(self, files=None):
        self.files = files or {}
        self.exists_called = []
        self.open_called = []

    def exists(self, path: str) -> bool:
        self.exists_called.append(path)
        return path in self.files

    def open(self, path: str, mode: str = "r", **kwargs):
        self.open_called.append((path, mode))
        if path not in self.files:
            raise FileNotFoundError(f"File not found: {path}")

        content = self.files[path]

        # Simple mock file object
        class MockFile:
            def __init__(self, content):
                self.content = content

            def read(self):
                return self.content

            def __enter__(self):
                return self

            def __exit__(self, *args):
                pass

        return MockFile(content)


class TestDependencyInjectionFilesystems:
    """Comprehensive tests for dependency injection with various filesystem implementations."""

    @pytest.fixture
    def memory_fs(self):
        """Provide a clean memory filesystem for each test."""
        return MemoryFileSystem()

    def test_load_config_local_filesystem(self):
        """Test default behavior with local filesystem."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "catalog.yaml"
            config_data = {
                "version": 1,
                "duckdb": {"database": ":memory:"},
                "views": [{"name": "test_view", "sql": "SELECT 1"}],
            }
            config_path.write_text(yaml.dump(config_data))

            config = load_config(str(config_path))
            assert config.version == 1
            assert config.views[0].name == "test_view"

    def test_load_config_memory_filesystem(self, memory_fs):
        """Test loading config from fsspec memory filesystem."""
        config_path = "/config/catalog.yaml"
        config_data = {
            "version": 1,
            "duckdb": {"database": ":memory:"},
            "views": [{"name": "mem_view", "sql": "SELECT 1"}],
        }
        memory_fs.makedirs("/config", exist_ok=True)
        with memory_fs.open(config_path, "w") as f:
            f.write(yaml.dump(config_data))

        # We need to use load_config with the filesystem parameter
        config = load_config(config_path, filesystem=memory_fs)
        assert config.version == 1
        assert config.views[0].name == "mem_view"

    def test_load_config_custom_mock_filesystem(self):
        """Test loading config from a completely custom filesystem implementation."""
        config_path = "/custom/catalog.yaml"
        config_data = {
            "version": 1,
            "duckdb": {"database": ":memory:"},
            "views": [{"name": "custom_view", "sql": "SELECT 1"}],
        }
        mock_fs = CustomMockFilesystem({config_path: yaml.dump(config_data)})

        config = load_config(config_path, filesystem=mock_fs)
        assert config.version == 1
        assert config.views[0].name == "custom_view"
        assert config_path in mock_fs.exists_called
        assert (config_path, "r") in mock_fs.open_called

    def test_recursive_imports_on_memory_filesystem(self, memory_fs):
        """Test that DI works for recursive imports on a custom filesystem."""
        memory_fs.makedirs("/project", exist_ok=True)

        main_config_path = "/project/main.yaml"
        imported_config_path = "/project/imported.yaml"

        main_config_data = {
            "version": 1,
            "duckdb": {"database": ":memory:"},
            "imports": ["imported.yaml"],
            "views": [{"name": "main_view", "sql": "SELECT 1"}],
        }
        imported_config_data = {
            "version": 1,
            "duckdb": {"database": ":memory:"},
            "views": [{"name": "imported_view", "sql": "SELECT 2"}],
        }

        with memory_fs.open(main_config_path, "w") as f:
            f.write(yaml.dump(main_config_data))
        with memory_fs.open(imported_config_path, "w") as f:
            f.write(yaml.dump(imported_config_data))

        config = load_config(main_config_path, filesystem=memory_fs)
        assert len(config.views) == 2
        view_names = [v.name for v in config.views]
        assert "main_view" in view_names
        assert "imported_view" in view_names

    def test_sql_file_loading_on_memory_filesystem(self, memory_fs):
        """Test that SQL files are loaded from the injected filesystem."""
        memory_fs.makedirs("/project/sql", exist_ok=True)

        config_path = "/project/catalog.yaml"
        sql_path = "/project/sql/view.sql"

        config_data = {
            "version": 1,
            "duckdb": {"database": ":memory:"},
            "views": [{"name": "sql_view", "sql_file": {"path": "sql/view.sql"}}],
        }
        sql_content = "SELECT * FROM memory_table"

        with memory_fs.open(config_path, "w") as f:
            f.write(yaml.dump(config_data))
        with memory_fs.open(sql_path, "w") as f:
            f.write(sql_content)

        config = load_config(config_path, filesystem=memory_fs)
        assert config.views[0].sql == sql_content

    def test_env_file_loading_on_memory_filesystem(self, memory_fs):
        """Test .env file loading from different filesystem types."""
        memory_fs.makedirs("/project", exist_ok=True)
        config_path = "/project/catalog.yaml"
        env_path = "/project/.env"

        config_data = {
            "version": 1,
            "duckdb": {"database": ":memory:"},
            "views": [{"name": "env_view", "sql": "SELECT '${env:TEST_VAR}'"}],
        }
        env_content = "TEST_VAR=from_memory_fs"

        with memory_fs.open(config_path, "w") as f:
            f.write(yaml.dump(config_data))
        with memory_fs.open(env_path, "w") as f:
            f.write(env_content)

        with patch.dict(os.environ, {}):
            config = load_config(config_path, filesystem=memory_fs, load_dotenv=True)
            assert config.views[0].sql == "SELECT 'from_memory_fs'"

    def test_path_resolution_with_filesystem(self, memory_fs):
        """Test that path resolution handles virtual paths from custom filesystems."""
        memory_fs.makedirs("/project/data", exist_ok=True)
        config_path = "/project/catalog.yaml"
        data_path = "/project/data/test.parquet"

        config_data = {
            "version": 1,
            "duckdb": {"database": ":memory:"},
            "views": [
                {"name": "data_view", "source": "parquet", "uri": "data/test.parquet"}
            ],
        }

        with memory_fs.open(config_path, "w") as f:
            f.write(yaml.dump(config_data))
        memory_fs.touch(data_path)

        config = load_config(config_path, filesystem=memory_fs, resolve_paths=True)
        assert "data/test.parquet" in config.views[0].uri
        assert "/project/data/test.parquet" in config.views[0].uri

    def test_error_handling_invalid_filesystem(self):
        """Test that invalid filesystem implementations are handled gracefully."""

        class BrokenFilesystem:
            pass  # Missing open and exists

        with pytest.raises(
            ConfigError,
            match="filesystem object must provide 'open' and 'exists' methods",
        ):
            load_config("/some/path.yaml", filesystem=BrokenFilesystem())

    def test_filesystem_permission_error(self):
        """Test handling of filesystem permission errors."""
        mock_fs = MagicMock()
        mock_fs.exists.return_value = True
        mock_fs.open.side_effect = PermissionError("Access denied")

        with pytest.raises(ConfigError, match="Failed to read config file"):
            load_config("/some/path.yaml", filesystem=mock_fs)

    def test_request_scoped_caching_with_filesystem(self, memory_fs):
        """Verify that DI works with request-scoped caching."""
        memory_fs.makedirs("/project", exist_ok=True)
        config_path = "/project/catalog.yaml"

        config_data = {
            "version": 1,
            "duckdb": {"database": ":memory:"},
            "imports": ["catalog.yaml"],  # Circular import to test cache
            "views": [{"name": "test", "sql": "SELECT 1"}],
        }

        with memory_fs.open(config_path, "w") as f:
            f.write(yaml.dump(config_data))

        from duckalog.errors import CircularImportError

        with pytest.raises(CircularImportError):
            load_config(config_path, filesystem=memory_fs)

    def test_s3_filesystem_mock(self):
        """Test mock S3 filesystem integration."""
        mock_fs = MagicMock()
        mock_fs.protocol = "s3"
        # Setup mock for context manager
        mock_file = MagicMock()
        mock_file.read.return_value = (
            "version: 1\nduckdb:\n  database: ':memory:'\nviews: []"
        )
        mock_fs.open.return_value.__enter__.return_value = mock_file

        # Mock exists to avoid .env discovery issues
        def mock_exists(path):
            return not path.endswith(".env")

        mock_fs.exists.side_effect = mock_exists

        # When path is s3://, it should use the provided filesystem
        config = load_config("s3://bucket/config.yaml", filesystem=mock_fs)
        assert config.version == 1
        mock_fs.open.assert_called()

    def test_sql_file_loader_interface(self, memory_fs):
        """Test the SQLFileLoader interface directly with DI."""
        loader = SQLFileLoader()
        memory_fs.makedirs("/sql", exist_ok=True)
        with memory_fs.open("/sql/test.sql", "w") as f:
            f.write("SELECT {{val}}")

        content = loader.load_sql_file(
            file_path="test.sql",
            config_file_path="/sql/dummy.yaml",
            variables={"val": 42},
            as_template=True,
            filesystem=memory_fs,
        )
        assert content == "SELECT 42"


if __name__ == "__main__":
    pytest.main([__file__])
