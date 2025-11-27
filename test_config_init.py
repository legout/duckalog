"""Tests for configuration template generation."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest
import yaml

from duckalog.config_init import (
    ConfigFormat,
    create_config_template,
    validate_generated_config,
)
from duckalog.config import ConfigError, load_config


class TestCreateConfigTemplate:
    """Test the create_config_template function."""

    def test_yaml_template_generation(self) -> None:
        """Test generating a YAML configuration template."""
        content = create_config_template(format="yaml")

        # Check that it's a string
        assert isinstance(content, str)

        # Check that it contains expected sections
        assert "version: 1" in content
        assert "duckdb:" in content
        assert "views:" in content
        assert "database: analytics_catalog.duckdb" in content

        # Check that it starts with comments
        assert "# Duckalog Configuration" in content

    def test_json_template_generation(self) -> None:
        """Test generating a JSON configuration template."""
        content = create_config_template(format="json")

        # Check that it's a string
        assert isinstance(content, str)

        # Parse as JSON to ensure it's valid
        parsed = json.loads(content)

        # Check structure
        assert parsed["version"] == 1
        assert "duckdb" in parsed
        assert "views" in parsed
        assert parsed["duckdb"]["database"] == "analytics_catalog.duckdb"
        assert len(parsed["views"]) >= 2  # Should have example views

    def test_custom_parameters(self) -> None:
        """Test generating template with custom parameters."""
        content = create_config_template(
            format="yaml", database_name="custom.db", project_name="my_project"
        )

        assert "database: custom.db" in content
        assert "my_project" in content

    def test_invalid_format(self) -> None:
        """Test that invalid format raises ValueError."""
        with pytest.raises(ValueError, match="Format must be 'yaml' or 'json'"):
            create_config_template(format="invalid")

    def test_output_path_writing(self) -> None:
        """Test writing template to a file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir) / "test_config.yaml"

            content = create_config_template(format="yaml", output_path=str(temp_path))

            # Check file was created
            assert temp_path.exists()

            # Check content matches
            file_content = temp_path.read_text()
            assert file_content == content

    def test_output_path_creates_directories(self) -> None:
        """Test that output path creates parent directories."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir) / "nested" / "dir" / "test_config.json"

            create_config_template(format="json", output_path=str(temp_path))

            # Check file and directories were created
            assert temp_path.exists()
            assert temp_path.parent.exists()

    def test_template_content_structure(self) -> None:
        """Test that generated template has the expected structure."""
        content = create_config_template(format="yaml")
        parsed = yaml.safe_load(content)

        # Check required top-level fields
        assert "version" in parsed
        assert "duckdb" in parsed
        assert "views" in parsed

        # Check version is positive integer
        assert parsed["version"] == 1

        # Check duckdb configuration
        duckdb_config = parsed["duckdb"]
        assert "database" in duckdb_config
        assert "pragmas" in duckdb_config
        assert isinstance(duckdb_config["pragmas"], list)

        # Check views
        views = parsed["views"]
        assert isinstance(views, list)
        assert len(views) >= 2

        # Check each view has required fields
        for view in views:
            assert "name" in view
            assert hasattr(
                view.get("source") or view.get("sql", ""), "__len__"
            )  # Either source or sql


class TestValidateGeneratedConfig:
    """Test the validate_generated_config function."""

    def test_validate_valid_yaml_config(self) -> None:
        """Test validating a valid YAML configuration."""
        content = create_config_template(format="yaml")

        # Should not raise any exceptions
        validate_generated_config(content, format="yaml")

    def test_validate_valid_json_config(self) -> None:
        """Test validating a valid JSON configuration."""
        content = create_config_template(format="json")

        # Should not raise any exceptions
        validate_generated_config(content, format="json")

    def test_validate_invalid_yaml_config(self) -> None:
        """Test validating an invalid YAML configuration."""
        invalid_content = "invalid: yaml: content: ["

        with pytest.raises(
            ConfigError, match="Generated configuration validation failed"
        ):
            validate_generated_config(invalid_content, format="yaml")

    def test_validate_invalid_json_config(self) -> None:
        """Test validating an invalid JSON configuration."""
        invalid_content = '{"invalid": json content}'

        with pytest.raises(
            ConfigError, match="Generated configuration validation failed"
        ):
            validate_generated_config(invalid_content, format="json")

    def test_validate_invalid_duckalog_config(self) -> None:
        """Test validating a syntactically valid but Duckalog-invalid config."""
        invalid_content = """
version: -1
duckdb: {}
views: []
"""

        with pytest.raises(
            ConfigError, match="Generated configuration validation failed"
        ):
            validate_generated_config(invalid_content, format="yaml")


class TestTemplateLoading:
    """Test that generated templates can be loaded with load_config."""

    def test_load_generated_yaml_config(self) -> None:
        """Test that a generated YAML config can be loaded."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir) / "test_config.yaml"

            create_config_template(format="yaml", output_path=str(temp_path))

            # Should be able to load without errors
            config = load_config(str(temp_path), load_sql_files=False)

            # Check basic properties
            assert config.version == 1
            assert config.duckdb.database == "analytics_catalog.duckdb"
            assert len(config.views) >= 2

    def test_load_generated_json_config(self) -> None:
        """Test that a generated JSON config can be loaded."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir) / "test_config.json"

            create_config_template(format="json", output_path=str(temp_path))

            # Should be able to load without errors
            config = load_config(str(temp_path), load_sql_files=False)

            # Check basic properties
            assert config.version == 1
            assert config.duckdb.database == "analytics_catalog.duckdb"
            assert len(config.views) >= 2

    def test_template_has_example_content(self) -> None:
        """Test that template includes educational example content."""
        content = create_config_template(format="yaml")

        # Check for educational comments
        assert "Key sections:" in content
        assert "Data source types supported" in content

        # Check for example views
        parsed = yaml.safe_load(content)
        view_names = [view["name"] for view in parsed["views"]]

        assert any("example" in name.lower() for name in view_names)
        assert any("parquet" in name.lower() for name in view_names)
