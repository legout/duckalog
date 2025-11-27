"""Integration tests for the CLI init command."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest
import yaml
from typer.testing import CliRunner

from duckalog.cli import app


class TestCLIInitCommand:
    """Test the CLI init command functionality."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.runner = CliRunner()

    def test_init_creates_yaml_file_by_default(self) -> None:
        """Test that init creates a YAML file by default."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            result = self.runner.invoke(app, ["init"], cwd=temp_dir)

            assert result.exit_code == 0
            assert "✅ Created Duckalog configuration" in result.stdout

            # Check that catalog.yaml was created
            config_file = temp_path / "catalog.yaml"
            assert config_file.exists()

            # Check content is valid YAML
            content = yaml.safe_load(config_file.read_text())
            assert "version" in content
            assert "duckdb" in content
            assert "views" in content

    def test_init_creates_json_file_with_format_option(self) -> None:
        """Test that init creates a JSON file with --format json."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            result = self.runner.invoke(app, ["init", "--format", "json"], cwd=temp_dir)

            assert result.exit_code == 0
            assert "Format: JSON" in result.stdout

            # Check that catalog.json was created
            config_file = temp_path / "catalog.json"
            assert config_file.exists()

            # Check content is valid JSON
            content = json.loads(config_file.read_text())
            assert "version" in content
            assert "duckdb" in content
            assert "views" in content

    def test_init_with_custom_output_path(self) -> None:
        """Test that init creates file at custom output path."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            custom_file = temp_path / "my_config.yaml"

            result = self.runner.invoke(
                app, ["init", "--output", str(custom_file)], cwd=temp_dir
            )

            assert result.exit_code == 0
            assert custom_file.exists()
            assert "my_config.yaml" in result.stdout

    def test_init_with_custom_database_name(self) -> None:
        """Test that init uses custom database name."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            result = self.runner.invoke(
                app, ["init", "--database", "custom_db.duckdb"], cwd=temp_dir
            )

            assert result.exit_code == 0
            assert "Database: custom_db.duckdb" in result.stdout

            # Check the generated config
            config_file = temp_path / "catalog.yaml"
            content = yaml.safe_load(config_file.read_text())
            assert content["duckdb"]["database"] == "custom_db.duckdb"

    def test_init_with_custom_project_name(self) -> None:
        """Test that init uses custom project name."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            result = self.runner.invoke(
                app, ["init", "--project", "sales_analytics"], cwd=temp_dir
            )

            assert result.exit_code == 0

            # Check the generated config contains the project name
            config_file = temp_path / "catalog.yaml"
            content = config_file.read_text()
            assert "sales_analytics" in content

    def test_init_force_overwrite(self) -> None:
        """Test that init overwrites existing file with --force."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            config_file = temp_path / "catalog.yaml"

            # Create existing file
            config_file.write_text("existing content")

            result = self.runner.invoke(app, ["init", "--force"], cwd=temp_dir)

            assert result.exit_code == 0
            assert config_file.exists()

            # Check that content was overwritten
            content = yaml.safe_load(config_file.read_text())
            assert "version" in content  # New content

    def test_init_skip_existing(self) -> None:
        """Test that init skips existing file with --skip-existing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            config_file = temp_path / "catalog.yaml"

            # Create existing file
            original_content = "original content"
            config_file.write_text(original_content)

            result = self.runner.invoke(app, ["init", "--skip-existing"], cwd=temp_dir)

            assert result.exit_code == 0
            assert "already exists, skipping" in result.stdout
            assert config_file.read_text() == original_content

    def test_init_prompts_for_overwrite(self) -> None:
        """Test that init prompts for overwrite when file exists."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            config_file = temp_path / "catalog.yaml"

            # Create existing file
            config_file.write_text("existing content")

            # Simulate user refusing to overwrite
            result = self.runner.invoke(app, ["init"], input="n\n", cwd=temp_dir)

            assert result.exit_code == 0
            assert "Operation cancelled" in result.stdout
            assert config_file.read_text() == "existing content"

    def test_init_invalid_format_error(self) -> None:
        """Test that init shows error for invalid format."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            result = self.runner.invoke(
                app, ["init", "--format", "invalid"], cwd=temp_dir
            )

            assert result.exit_code == 1
            assert "Format must be 'yaml' or 'json'" in result.stdout

    def test_init_creates_nested_directories(self) -> None:
        """Test that init creates nested directories for output path."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            nested_file = temp_path / "nested" / "dir" / "config.yaml"

            result = self.runner.invoke(
                app, ["init", "--output", str(nested_file)], cwd=temp_dir
            )

            assert result.exit_code == 0
            assert nested_file.exists()
            assert nested_file.parent.exists()

    def test_init_verbose_output(self) -> None:
        """Test that init shows verbose output with --verbose."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            result = self.runner.invoke(app, ["init", "--verbose"], cwd=temp_dir)

            assert result.exit_code == 0
            assert "Next steps:" in result.stdout
            assert "duckalog validate" in result.stdout
            assert "duckalog build" in result.stdout

    def test_init_generated_config_is_valid(self) -> None:
        """Test that generated config can be validated."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create config
            result = self.runner.invoke(app, ["init"], cwd=temp_dir)
            assert result.exit_code == 0

            # Validate it using duckalog validate command
            config_file = temp_path / "catalog.yaml"
            validate_result = self.runner.invoke(
                app, ["validate", str(config_file)], cwd=temp_dir
            )

            assert validate_result.exit_code == 0
            assert "Config is valid" in validate_result.stdout

    def test_init_help_output(self) -> None:
        """Test that init help shows expected information."""
        result = self.runner.invoke(app, ["init", "--help"])

        assert result.exit_code == 0
        assert "Initialize a new Duckalog configuration file" in result.stdout
        assert "--format" in result.stdout
        assert "--output" in result.stdout
        assert "--database" in result.stdout
        assert "--project" in result.stdout
        assert "--force" in result.stdout
        assert "--skip-existing" in result.stdout
