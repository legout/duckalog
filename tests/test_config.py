"""Tests for the Duckalog configuration schema and loader."""

from __future__ import annotations

import json
import textwrap
from pathlib import Path

import pytest

from duckalog import ConfigError, load_config


def _write(path: Path, content: str) -> Path:
    path.write_text(textwrap.dedent(content))
    return path


def test_load_config_yaml_with_env_interpolation(monkeypatch, tmp_path):
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "AKIA123")
    config_path = _write(
        tmp_path / "catalog.yaml",
        """
        version: 1
        duckdb:
          database: catalog.duckdb
          pragmas:
            - "SET s3_access_key_id='${env:AWS_ACCESS_KEY_ID}'"
        views:
          - name: vip_users
            sql: "SELECT 1"
        """,
    )

    config = load_config(str(config_path))

    assert config.duckdb.pragmas == ["SET s3_access_key_id='AKIA123'"]


def test_load_config_json_parses(tmp_path):
    payload = {
        "version": 2,
        "duckdb": {"database": "test.duckdb"},
        "views": [
            {
                "name": "users",
                "source": "parquet",
                "uri": "s3://bucket/users/*.parquet",
                "options": {"hive_partitioning": True},
            }
        ],
    }
    config_path = tmp_path / "catalog.json"
    config_path.write_text(json.dumps(payload))

    config = load_config(str(config_path))

    assert config.version == 2
    assert config.views[0].source == "parquet"
    assert config.views[0].uri == "s3://bucket/users/*.parquet"


def test_missing_env_variable_raises(monkeypatch, tmp_path):
    monkeypatch.delenv("MISSING_SECRET", raising=False)
    config_path = _write(
        tmp_path / "catalog.yaml",
        """
        version: 1
        duckdb:
          database: catalog.duckdb
          pragmas:
            - "SET secret='${env:MISSING_SECRET}'"
        views:
          - name: v1
            sql: "SELECT 1"
        """,
    )

    with pytest.raises(ConfigError) as exc:
        load_config(str(config_path))

    assert "MISSING_SECRET" in str(exc.value)


def test_duplicate_view_names_rejected(tmp_path):
    config_path = _write(
        tmp_path / "catalog.yaml",
        """
        version: 1
        duckdb:
          database: catalog.duckdb
        views:
          - name: duplicate
            sql: "SELECT 1"
          - name: duplicate
            sql: "SELECT 2"
        """,
    )

    with pytest.raises(ConfigError) as exc:
        load_config(str(config_path))

    assert "Duplicate view name" in str(exc.value)


def test_view_and_attachment_field_validation(tmp_path):
    config_path = _write(
        tmp_path / "catalog.yaml",
        """
        version: 1
        duckdb:
          database: catalog.duckdb
        attachments:
          sqlite:
            - alias: legacy
        iceberg_catalogs:
          - name: missing_type
        views:
          - name: parquet_view
            source: parquet
        """,
    )

    with pytest.raises(ConfigError) as exc:
        load_config(str(config_path))

    message = str(exc.value).lower()
    assert "uri' for source" in message
    assert "field required" in message  # sqlite.path missing or catalog_type missing


def test_iceberg_view_requires_exclusive_fields(tmp_path):
    config_path = _write(
        tmp_path / "catalog.yaml",
        """
        version: 1
        duckdb:
          database: catalog.duckdb
        views:
          - name: iceberg_view
            source: iceberg
            uri: "s3://warehouse/table"
            catalog: wrong
            table: foo.bar
        """,
    )

    with pytest.raises(ConfigError) as exc:
        load_config(str(config_path))

    assert "either 'uri' OR both 'catalog' and 'table'" in str(exc.value)


def test_view_metadata_fields(tmp_path):
    config_path = _write(
        tmp_path / "catalog.yaml",
        """
        version: 1
        duckdb:
          database: catalog.duckdb
        views:
          - name: meta_view
            sql: "SELECT 1"
            description: "Primary metrics view"
            tags: [core, metrics]
        """,
    )

    config = load_config(str(config_path))

    view = config.views[0]
    assert view.description == "Primary metrics view"
    assert view.tags == ["core", "metrics"]
