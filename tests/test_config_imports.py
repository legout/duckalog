"""Tests for config import functionality."""

from __future__ import annotations

import os
import textwrap
from pathlib import Path

import pytest

from duckalog import load_config
from duckalog.errors import (
    CircularImportError,
    DuplicateNameError,
    ImportError,
    ImportFileNotFoundError,
)


def _write(path: Path, content: str) -> Path:
    path.write_text(textwrap.dedent(content))
    return path


def test_basic_import_single_file(tmp_path):
    """Test importing a single config file."""
    # Create imported file
    _write(
        tmp_path / "settings.yaml",
        """
        version: 1
        duckdb:
          database: imported.duckdb
        views:
          - name: imported_view
            sql: "SELECT 1"
        """,
    )

    # Create main file that imports settings
    config_path = _write(
        tmp_path / "catalog.yaml",
        """
        version: 1
        imports:
          - ./settings.yaml
        duckdb:
          database: main.duckdb
        views:
          - name: main_view
            sql: "SELECT 2"
        """,
    )

    config = load_config(str(config_path))

    # Should have both views
    assert len(config.views) == 2
    view_names = {v.name for v in config.views}
    assert "imported_view" in view_names
    assert "main_view" in view_names

    # Main config should override duckdb database
    assert config.duckdb.database == "main.duckdb"


def test_basic_import_multiple_files(tmp_path):
    """Test importing multiple config files."""
    # Create first imported file
    _write(
        tmp_path / "views1.yaml",
        """
        version: 1
        duckdb:
          database: base.duckdb
        views:
          - name: view1
            sql: "SELECT 1"
          - name: view2
            sql: "SELECT 2"
        """,
    )

    # Create second imported file
    _write(
        tmp_path / "views2.yaml",
        """
        version: 1
        duckdb:
          database: overridden.duckdb
        views:
          - name: view3
            sql: "SELECT 3"
        """,
    )

    # Create main file that imports both
    config_path = _write(
        tmp_path / "catalog.yaml",
        """
        version: 1
        imports:
          - ./views1.yaml
          - ./views2.yaml
        duckdb:
          database: main.duckdb
        views: []
        """,
    )

    config = load_config(str(config_path))

    # Should have all three views
    assert len(config.views) == 3
    view_names = {v.name for v in config.views}
    assert view_names == {"view1", "view2", "view3"}

    # Main config should have the final say on duckdb.database
    assert config.duckdb.database == "main.duckdb"


def test_nested_imports(tmp_path):
    """Test importing files that themselves have imports."""
    # Create base file
    _write(
        tmp_path / "base.yaml",
        """
        version: 1
        duckdb:
          database: base.duckdb
        views:
          - name: base_view
            sql: "SELECT 1"
        """,
    )

    # Create intermediate file that imports base
    _write(
        tmp_path / "intermediate.yaml",
        """
        version: 1
        imports:
          - ./base.yaml
        duckdb:
          database: intermediate.duckdb
        views:
          - name: intermediate_view
            sql: "SELECT 2"
        """,
    )

    # Create main file that imports intermediate
    config_path = _write(
        tmp_path / "catalog.yaml",
        """
        version: 1
        imports:
          - ./intermediate.yaml
        duckdb:
          database: main.duckdb
        views:
          - name: main_view
            sql: "SELECT 3"
        """,
    )

    config = load_config(str(config_path))

    # Should have all three views (base, intermediate, main)
    assert len(config.views) == 3
    view_names = {v.name for v in config.views}
    assert view_names == {"base_view", "intermediate_view", "main_view"}


def test_circular_import_detection(tmp_path):
    """Test that circular imports are detected."""
    # Create file A that imports B
    _write(
        tmp_path / "file_a.yaml",
        """
        version: 1
        imports:
          - ./file_b.yaml
        duckdb:
          database: a.duckdb
        views: []
        """,
    )

    # Create file B that imports A (circular!)
    _write(
        tmp_path / "file_b.yaml",
        """
        version: 1
        imports:
          - ./file_a.yaml
        duckdb:
          database: b.duckdb
        views: []
        """,
    )

    # Try to load file A - should fail with circular import error
    config_path = tmp_path / "file_a.yaml"

    with pytest.raises(CircularImportError) as exc_info:
        load_config(str(config_path))

    assert "Circular import detected" in str(exc_info.value)


def test_duplicate_view_names_across_imports(tmp_path):
    """Test that duplicate view names are detected across imports."""
    # Create first file with view
    _write(
        tmp_path / "views1.yaml",
        """
        version: 1
        duckdb:
          database: views1.duckdb
        views:
          - name: duplicate_view
            sql: "SELECT 1"
        """,
    )

    # Create second file with same view name
    _write(
        tmp_path / "views2.yaml",
        """
        version: 1
        duckdb:
          database: views2.duckdb
        views:
          - name: duplicate_view
            sql: "SELECT 2"
        """,
    )

    # Create main file that imports both
    config_path = _write(
        tmp_path / "catalog.yaml",
        """
        version: 1
        imports:
          - ./views1.yaml
          - ./views2.yaml
        duckdb:
          database: main.duckdb
        views: []
        """,
    )

    with pytest.raises(DuplicateNameError) as exc_info:
        load_config(str(config_path))

    assert "Duplicate view name(s) found" in str(exc_info.value)
    assert "duplicate_view" in str(exc_info.value)


def test_duplicate_semantic_model_names(tmp_path):
    """Test that duplicate semantic model names are detected."""
    # Create first file with semantic model
    _write(
        tmp_path / "models1.yaml",
        """
        version: 1
        duckdb:
          database: models1.duckdb
        views:
          - name: some_view
            sql: "SELECT 1"
        semantic_models:
          - name: users
            base_view: some_view
            measures:
              - name: count
                agg: count
        """,
    )

    # Create second file with same semantic model name
    _write(
        tmp_path / "models2.yaml",
        """
        version: 1
        duckdb:
          database: models2.duckdb
        views:
          - name: another_view
            sql: "SELECT 2"
        semantic_models:
          - name: users
            base_view: another_view
            measures:
              - name: total
                agg: sum
        """,
    )

    # Create main file that imports both
    config_path = _write(
        tmp_path / "catalog.yaml",
        """
        version: 1
        imports:
          - ./models1.yaml
          - ./models2.yaml
        duckdb:
          database: main.duckdb
        views: []
        """,
    )

    with pytest.raises(DuplicateNameError) as exc_info:
        load_config(str(config_path))

    assert "Duplicate semantic model name(s) found" in str(exc_info.value)


def test_duplicate_iceberg_catalog_names(tmp_path):
    """Test that duplicate Iceberg catalog names are detected."""
    # Create first file with catalog
    _write(
        tmp_path / "catalogs1.yaml",
        """
        version: 1
        duckdb:
          database: catalogs1.duckdb
        views: []
        iceberg_catalogs:
          - name: my_catalog
            warehouse: s3://warehouse1
        """,
    )

    # Create second file with same catalog name
    _write(
        tmp_path / "catalogs2.yaml",
        """
        version: 1
        duckdb:
          database: catalogs2.duckdb
        views: []
        iceberg_catalogs:
          - name: my_catalog
            warehouse: s3://warehouse2
        """,
    )

    # Create main file that imports both
    config_path = _write(
        tmp_path / "catalog.yaml",
        """
        version: 1
        imports:
          - ./catalogs1.yaml
          - ./catalogs2.yaml
        duckdb:
          database: main.duckdb
        views: []
        """,
    )

    with pytest.raises(DuplicateNameError) as exc_info:
        load_config(str(config_path))

    assert "Duplicate Iceberg catalog name(s) found" in str(exc_info.value)


def test_duplicate_attachment_aliases(tmp_path):
    """Test that duplicate attachment aliases are detected."""
    # Create first file with attachment
    _write(
        tmp_path / "attachments1.yaml",
        """
        version: 1
        attachments:
          duckdb:
            - alias: my_db
              database: db1.duckdb
        """,
    )

    # Create second file with same attachment alias
    _write(
        tmp_path / "attachments2.yaml",
        """
        version: 1
        attachments:
          duckdb:
            - alias: my_db
              database: db2.duckdb
        """,
    )

    # Create main file that imports both
    config_path = _write(
        tmp_path / "catalog.yaml",
        """
        version: 1
        imports:
          - ./attachments1.yaml
          - ./attachments2.yaml
        duckdb:
          database: main.duckdb
        views: []
        """,
    )

    with pytest.raises(DuplicateNameError) as exc_info:
        load_config(str(config_path))

    assert "Duplicate attachment alias(es) found" in str(exc_info.value)


def test_import_file_not_found(tmp_path):
    """Test that missing import files are detected."""
    # Create main file that imports non-existent file
    config_path = _write(
        tmp_path / "catalog.yaml",
        """
        version: 1
        imports:
          - ./nonexistent.yaml
        duckdb:
          database: main.duckdb
        views: []
        """,
    )

    with pytest.raises(ImportFileNotFoundError) as exc_info:
        load_config(str(config_path))

    assert "Imported file not found" in str(exc_info.value)


def test_import_with_env_var_in_path(monkeypatch, tmp_path):
    """Test environment variable interpolation in import paths."""
    monkeypatch.setenv("IMPORT_DIR", str(tmp_path))

    # Create imported file
    _write(
        tmp_path / "settings.yaml",
        """
        version: 1
        views:
          - name: env_view
            sql: "SELECT 1"
        """,
    )

    # Create main file that uses env var in import path
    config_path = _write(
        tmp_path / "catalog.yaml",
        """
        version: 1
        imports:
          - ${env:IMPORT_DIR}/settings.yaml
        duckdb:
          database: main.duckdb
        views: []
        """,
    )

    config = load_config(str(config_path))

    # Should have imported the view
    assert len(config.views) == 1
    assert config.views[0].name == "env_view"


def test_import_with_env_var_undefined(monkeypatch, tmp_path):
    """Test that undefined environment variables in import paths raise an error."""
    monkeypatch.delenv("NONEXISTENT_VAR", raising=False)

    # Create main file that uses undefined env var
    config_path = _write(
        tmp_path / "catalog.yaml",
        """
        version: 1
        imports:
          - ${env:NONEXISTENT_VAR}/settings.yaml
        duckdb:
          database: main.duckdb
        views: []
        """,
    )

    with pytest.raises(Exception):  # Should raise some error (likely ConfigError or ImportError)
        load_config(str(config_path))


def test_import_with_json_format(tmp_path):
    """Test importing JSON config files."""
    # Create imported JSON file
    (tmp_path / "settings.json").write_text(
        """{
          "version": 1,
          "duckdb": {
            "database": "json.duckdb"
          },
          "views": [
            {
              "name": "json_view",
              "sql": "SELECT 1"
            }
          ]
        }"""
    )

    # Create main YAML file that imports JSON
    config_path = _write(
        tmp_path / "catalog.yaml",
        """
        version: 1
        imports:
          - ./settings.json
        duckdb:
          database: main.duckdb
        views: []
        """,
    )

    config = load_config(str(config_path))

    # Should have imported the view from JSON
    assert len(config.views) == 1
    assert config.views[0].name == "json_view"


def test_empty_imports_list(tmp_path):
    """Test that empty imports list works (backward compatibility)."""
    # Create config with empty imports
    config_path = _write(
        tmp_path / "catalog.yaml",
        """
        version: 1
        imports: []
        duckdb:
          database: main.duckdb
        views:
          - name: main_view
            sql: "SELECT 1"
        """,
    )

    config = load_config(str(config_path))

    # Should work normally
    assert len(config.views) == 1
    assert config.views[0].name == "main_view"


def test_config_without_imports(tmp_path):
    """Test that configs without imports work normally (backward compatibility)."""
    # Create config without imports field
    config_path = _write(
        tmp_path / "catalog.yaml",
        """
        version: 1
        duckdb:
          database: main.duckdb
        views:
          - name: main_view
            sql: "SELECT 1"
        """,
    )

    config = load_config(str(config_path))

    # Should work normally
    assert len(config.views) == 1
    assert config.views[0].name == "main_view"


def test_merge_dict_deep_merge(tmp_path):
    """Test that dicts are deep merged, not overwritten."""
    # Create file with nested dict structure
    _write(
        tmp_path / "nested.yaml",
        """
        version: 1
        duckdb:
          database: base.duckdb
          extensions:
            - httpfs
        views: []
        attachments:
          duckdb:
            - alias: db1
              database: file1.duckdb
        """,
    )

    # Create main file with additional values in same sections
    config_path = _write(
        tmp_path / "catalog.yaml",
        """
        imports:
          - ./nested.yaml
        version: 1
        duckdb:
          extensions:
            - json
        attachments:
          duckdb:
            - alias: db2
              database: file2.duckdb
        """,
    )

    config = load_config(str(config_path))

    # Both extensions should be present
    assert "httpfs" in config.duckdb.extensions
    assert "json" in config.duckdb.extensions

    # Both attachments should be present
    assert len(config.attachments.duckdb) == 2
    aliases = {a.alias for a in config.attachments.duckdb}
    assert aliases == {"db1", "db2"}


def test_merge_lists_concatenate(tmp_path):
    """Test that lists are concatenated, not overwritten."""
    # Create file with list
    _write(
        tmp_path / "list.yaml",
        """
        version: 1
        duckdb:
          database: list.duckdb
          pragmas:
            - "SET option1=value1"
        views: []
        """,
    )

    # Create main file with additional items in same list
    config_path = _write(
        tmp_path / "catalog.yaml",
        """
        version: 1
        imports:
          - ./list.yaml
        duckdb:
          database: main.duckdb
          pragmas:
            - "SET option2=value2"
        """,
    )

    config = load_config(str(config_path))

    # Both pragmas should be present in order
    assert len(config.duckdb.pragmas) == 2
    assert "SET option1=value1" in config.duckdb.pragmas
    assert "SET option2=value2" in config.duckdb.pragmas


def test_import_with_semantic_models_and_views(tmp_path):
    """Test importing files with both semantic models and views."""
    # Create file with semantic model
    _write(
        tmp_path / "models.yaml",
        """
        version: 1
        duckdb:
          database: models.duckdb
        views:
          - name: base_view
            source: duckdb
            uri: ":memory:"
        semantic_models:
          - name: users_model
            base_view: base_view
            measures:
              - name: count
                agg: count
        """,
    )

    # Create main file
    config_path = _write(
        tmp_path / "catalog.yaml",
        """
        version: 1
        imports:
          - ./models.yaml
        duckdb:
          database: main.duckdb
        """,
    )

    config = load_config(str(config_path))

    # Should have both views and semantic models
    assert len(config.views) == 1
    assert config.views[0].name == "base_view"

    assert len(config.semantic_models) == 1
    assert config.semantic_models[0].name == "users_model"
    assert config.semantic_models[0].base_view == "base_view"


def test_multiple_files_same_import(tmp_path):
    """Test that the same import file is only loaded once (caching)."""
    # Create a file that will be imported multiple times
    _write(
        tmp_path / "common.yaml",
        """
        version: 1
        views:
          - name: common_view
            sql: "SELECT 1"
        """,
    )

    # Create file A that imports common
    _write(
        tmp_path / "file_a.yaml",
        """
        version: 1
        imports:
          - ./common.yaml
        duckdb:
          database: a.duckdb
        views:
          - name: view_a
            sql: "SELECT 2"
        """,
    )

    # Create file B that also imports common
    _write(
        tmp_path / "file_b.yaml",
        """
        version: 1
        imports:
          - ./common.yaml
        duckdb:
          database: b.duckdb
        views:
          - name: view_b
            sql: "SELECT 3"
        """,
    )

    # Create main file that imports both A and B
    config_path = _write(
        tmp_path / "catalog.yaml",
        """
        version: 1
        imports:
          - ./file_a.yaml
          - ./file_b.yaml
        duckdb:
          database: main.duckdb
        """,
    )

    config = load_config(str(config_path))

    # common_view should only appear once, even though it was imported twice
    view_names = [v.name for v in config.views]
    assert view_names.count("common_view") == 1
    assert "view_a" in view_names
    assert "view_b" in view_names


def test_import_with_subdirectory(tmp_path):
    """Test importing files from subdirectories."""
    # Create subdirectory
    subdir = tmp_path / "imports"
    subdir.mkdir()

    # Create file in subdirectory
    _write(
        subdir / "settings.yaml",
        """
        version: 1
        duckdb:
          database: subdir.duckdb
        views:
          - name: subdir_view
            sql: "SELECT 1"
        """,
    )

    # Create main file that imports from subdirectory
    config_path = _write(
        tmp_path / "catalog.yaml",
        """
        version: 1
        imports:
          - ./imports/settings.yaml
        duckdb:
          database: main.duckdb
        views: []
        """,
    )

    config = load_config(str(config_path))

    # Should have imported the view
    assert len(config.views) == 1
    assert config.views[0].name == "subdir_view"
