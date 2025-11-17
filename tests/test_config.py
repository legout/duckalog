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


def test_iceberg_view_catalog_reference_valid(tmp_path):
    config_path = _write(
        tmp_path / "catalog.yaml",
        """
        version: 1
        duckdb:
          database: catalog.duckdb
        iceberg_catalogs:
          - name: main_ic
            catalog_type: rest
        views:
          - name: iceberg_catalog_view
            source: iceberg
            catalog: main_ic
            table: analytics.orders
        """,
    )

    config = load_config(str(config_path))

    assert config.views[0].catalog == "main_ic"


def test_duckdb_attachment_read_only_default(tmp_path):
    config_path = _write(
        tmp_path / "catalog.yaml",
        """
        version: 1
        duckdb:
          database: catalog.duckdb
        attachments:
          duckdb:
            - alias: ref
              path: ./ref.duckdb
        views:
          - name: v1
            sql: "SELECT 1"
        """,
    )

    config = load_config(str(config_path))

    assert len(config.attachments.duckdb) == 1
    attachment = config.attachments.duckdb[0]
    assert attachment.alias == "ref"
    assert attachment.read_only is True


def test_duckdb_attachment_read_only_explicit_false(tmp_path):
    config_path = _write(
        tmp_path / "catalog.yaml",
        """
        version: 1
        duckdb:
          database: catalog.duckdb
        attachments:
          duckdb:
            - alias: ref
              path: ./ref.duckdb
              read_only: false
        views:
          - name: v1
            sql: "SELECT 1"
        """,
    )

    config = load_config(str(config_path))

    attachment = config.attachments.duckdb[0]
    assert attachment.read_only is False


def test_iceberg_view_catalog_reference_missing(tmp_path):
    config_path = _write(
        tmp_path / "catalog.yaml",
        """
        version: 1
        duckdb:
          database: catalog.duckdb
        iceberg_catalogs:
          - name: defined_ic
            catalog_type: rest
        views:
          - name: missing_catalog_view
            source: iceberg
            catalog: missing_ic
            table: analytics.orders
        """,
    )

    with pytest.raises(ConfigError) as exc:
        load_config(str(config_path))

    assert "missing_catalog_view" in str(exc.value)
    assert "missing_ic" in str(exc.value)


def test_sql_file_path_cannot_be_empty(tmp_path):
    config_path = _write(
        tmp_path / "catalog.yaml",
        """
        version: 1
        duckdb:
          database: catalog.duckdb
        views:
          - name: file_view
            sql_file:
              path: ""
        """,
    )

    with pytest.raises(ConfigError) as exc:
        load_config(str(config_path))

    assert "sql_file.path cannot be empty" in str(exc.value)


def test_sql_template_path_cannot_be_empty(tmp_path):
    config_path = _write(
        tmp_path / "catalog.yaml",
        """
        version: 1
        duckdb:
          database: catalog.duckdb
        views:
          - name: template_view
            sql_template:
              path: "   "
        """,
    )

    with pytest.raises(ConfigError) as exc:
        load_config(str(config_path))

    assert "sql_template.path cannot be empty" in str(exc.value)


def test_duckdb_settings_single_string(tmp_path):
    config_path = _write(
        tmp_path / "catalog.yaml",
        """
        version: 1
        duckdb:
          database: catalog.duckdb
          settings: "SET threads = 32"
        views:
          - name: test_view
            sql: "SELECT 1"
        """,
    )

    config = load_config(str(config_path))
    assert config.duckdb.settings == "SET threads = 32"


def test_duckdb_settings_list(tmp_path):
    config_path = _write(
        tmp_path / "catalog.yaml",
        """
        version: 1
        duckdb:
          database: catalog.duckdb
          settings:
            - "SET threads = 32"
            - "SET memory_limit = '1GB'"
        views:
          - name: test_view
            sql: "SELECT 1"
        """,
    )

    config = load_config(str(config_path))
    assert config.duckdb.settings == ["SET threads = 32", "SET memory_limit = '1GB'"]


def test_duckdb_settings_with_env_interpolation(monkeypatch, tmp_path):
    monkeypatch.setenv("THREAD_COUNT", "16")
    config_path = _write(
        tmp_path / "catalog.yaml",
        """
        version: 1
        duckdb:
          database: catalog.duckdb
          settings: "SET threads = ${env:THREAD_COUNT}"
        views:
          - name: test_view
            sql: "SELECT 1"
        """,
    )

    config = load_config(str(config_path))
    assert config.duckdb.settings == "SET threads = 16"


def test_duckdb_settings_empty_string(tmp_path):
    config_path = _write(
        tmp_path / "catalog.yaml",
        """
        version: 1
        duckdb:
          database: catalog.duckdb
          settings: ""
        views:
          - name: test_view
            sql: "SELECT 1"
        """,
    )

    config = load_config(str(config_path))
    assert config.duckdb.settings is None


def test_duckdb_settings_empty_list(tmp_path):
    config_path = _write(
        tmp_path / "catalog.yaml",
        """
        version: 1
        duckdb:
          database: catalog.duckdb
          settings: []
        views:
          - name: test_view
            sql: "SELECT 1"
        """,
    )

    config = load_config(str(config_path))
    assert config.duckdb.settings is None


def test_duckdb_settings_invalid_format_not_set(tmp_path):
    config_path = _write(
        tmp_path / "catalog.yaml",
        """
        version: 1
        duckdb:
          database: catalog.duckdb
          settings: "threads = 32"
        views:
          - name: test_view
            sql: "SELECT 1"
        """,
    )

    with pytest.raises(ConfigError) as exc:
        load_config(str(config_path))

    assert "Settings must be valid DuckDB SET statements" in str(exc.value)


def test_duckdb_settings_invalid_format_in_list(tmp_path):
    config_path = _write(
        tmp_path / "catalog.yaml",
        """
        version: 1
        duckdb:
          database: catalog.duckdb
          settings:
            - "SET threads = 32"
            - "memory_limit = '1GB'"
        views:
          - name: test_view
            sql: "SELECT 1"
        """,
    )

    with pytest.raises(ConfigError) as exc:
        load_config(str(config_path))

    assert "Settings must be valid DuckDB SET statements" in str(exc.value)


def test_duckdb_settings_no_settings(tmp_path):
    config_path = _write(
        tmp_path / "catalog.yaml",
        """
        version: 1
        duckdb:
          database: catalog.duckdb
        views:
          - name: test_view
            sql: "SELECT 1"
        """,
    )

    config = load_config(str(config_path))
    assert config.duckdb.settings is None


def test_duckdb_secrets_s3_config(tmp_path):
    config_path = _write(
        tmp_path / "catalog.yaml",
        """
        version: 1
        duckdb:
          database: catalog.duckdb
          secrets:
            - type: s3
              key_id: AKIAIOSFODNN7EXAMPLE
              secret: wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
              region: us-west-2
        views:
          - name: test_view
            sql: "SELECT 1"
        """,
    )

    config = load_config(str(config_path))
    assert len(config.duckdb.secrets) == 1
    secret = config.duckdb.secrets[0]
    assert secret.type == "s3"
    assert secret.key_id == "AKIAIOSFODNN7EXAMPLE"
    assert secret.secret == "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
    assert secret.region == "us-west-2"
    assert secret.provider == "config"
    assert secret.persistent is False


def test_duckdb_secrets_azure_persistent(tmp_path):
    config_path = _write(
        tmp_path / "catalog.yaml",
        """
        version: 1
        duckdb:
          database: catalog.duckdb
          secrets:
            - type: azure
              name: azure_prod
              provider: config
              persistent: true
              scope: 'prod/'
              connection_string: DefaultEndpointsProtocol=https;AccountName=myaccount;AccountKey=mykey;EndpointSuffix=core.windows.net
        views:
          - name: test_view
            sql: "SELECT 1"
        """,
    )

    config = load_config(str(config_path))
    assert len(config.duckdb.secrets) == 1
    secret = config.duckdb.secrets[0]
    assert secret.type == "azure"
    assert secret.name == "azure_prod"
    assert secret.provider == "config"
    assert secret.persistent is True
    assert secret.scope == "prod/"
    assert (
        secret.connection_string
        == "DefaultEndpointsProtocol=https;AccountName=myaccount;AccountKey=mykey;EndpointSuffix=core.windows.net"
    )


def test_duckdb_secrets_credential_chain(tmp_path):
    config_path = _write(
        tmp_path / "catalog.yaml",
        """
        version: 1
        duckdb:
          database: catalog.duckdb
          secrets:
            - type: s3
              name: s3_auto
              provider: credential_chain
              region: us-east-1
        views:
          - name: test_view
            sql: "SELECT 1"
        """,
    )

    config = load_config(str(config_path))
    assert len(config.duckdb.secrets) == 1
    secret = config.duckdb.secrets[0]
    assert secret.type == "s3"
    assert secret.name == "s3_auto"
    assert secret.provider == "credential_chain"
    assert secret.region == "us-east-1"
    assert secret.key_id is None
    assert secret.secret is None


def test_duckdb_secrets_http_basic_auth(tmp_path):
    config_path = _write(
        tmp_path / "catalog.yaml",
        """
        version: 1
        duckdb:
          database: catalog.duckdb
          secrets:
            - type: http
              name: api_auth
              key_id: myusername
              secret: mypassword
        views:
          - name: test_view
            sql: "SELECT 1"
        """,
    )

    config = load_config(str(config_path))
    assert len(config.duckdb.secrets) == 1
    secret = config.duckdb.secrets[0]
    assert secret.type == "http"
    assert secret.name == "api_auth"
    assert secret.key_id == "myusername"
    assert secret.secret == "mypassword"


def test_duckdb_secrets_postgres_connection_string(tmp_path):
    config_path = _write(
        tmp_path / "catalog.yaml",
        """
        version: 1
        duckdb:
          database: catalog.duckdb
          secrets:
            - type: postgres
              name: pg_prod
              connection_string: postgresql://user:password@localhost:5432/mydb
        views:
          - name: test_view
            sql: "SELECT 1"
        """,
    )

    config = load_config(str(config_path))
    assert len(config.duckdb.secrets) == 1
    secret = config.duckdb.secrets[0]
    assert secret.type == "postgres"
    assert secret.name == "pg_prod"
    assert secret.connection_string == "postgresql://user:password@localhost:5432/mydb"


def test_duckdb_secrets_with_env_interpolation(monkeypatch, tmp_path):
    monkeypatch.setenv("AWS_ACCESS_KEY", "AKIA123")
    monkeypatch.setenv("AWS_SECRET_KEY", "secret123")
    config_path = _write(
        tmp_path / "catalog.yaml",
        """
        version: 1
        duckdb:
          database: catalog.duckdb
          secrets:
            - type: s3
              key_id: ${env:AWS_ACCESS_KEY}
              secret: ${env:AWS_SECRET_KEY}
              region: us-west-2
        views:
          - name: test_view
            sql: "SELECT 1"
        """,
    )

    config = load_config(str(config_path))
    assert len(config.duckdb.secrets) == 1
    secret = config.duckdb.secrets[0]
    assert secret.key_id == "AKIA123"
    assert secret.secret == "secret123"


def test_duckdb_secrets_validation_s3_missing_fields(tmp_path):
    config_path = _write(
        tmp_path / "catalog.yaml",
        """
        version: 1
        duckdb:
          database: catalog.duckdb
          secrets:
            - type: s3
              key_id: AKIAIOSFODNN7EXAMPLE
              # Missing secret field
              region: us-west-2
        views:
          - name: test_view
            sql: "SELECT 1"
        """,
    )

    with pytest.raises(ConfigError) as exc:
        load_config(str(config_path))

    assert "S3 config provider requires key_id and secret" in str(exc.value)


def test_duckdb_secrets_validation_azure_missing_fields(tmp_path):
    config_path = _write(
        tmp_path / "catalog.yaml",
        """
        version: 1
        duckdb:
          database: catalog.duckdb
          secrets:
            - type: azure
              # Missing connection_string or tenant_id + account_name
              account_name: myaccount
        views:
          - name: test_view
            sql: "SELECT 1"
        """,
    )

    with pytest.raises(ConfigError) as exc:
        load_config(str(config_path))

    assert (
        "Azure config provider requires connection_string or (tenant_id and account_name)"
        in str(exc.value)
    )


def test_duckdb_secrets_validation_http_missing_fields(tmp_path):
    config_path = _write(
        tmp_path / "catalog.yaml",
        """
        version: 1
        duckdb:
          database: catalog.duckdb
          secrets:
            - type: http
              key_id: myusername
              # Missing secret field
        views:
          - name: test_view
            sql: "SELECT 1"
        """,
    )

    with pytest.raises(ConfigError) as exc:
        load_config(str(config_path))

    assert "HTTP secret requires key_id (username) and secret (password)" in str(
        exc.value
    )


def test_duckdb_secrets_empty_secrets(tmp_path):
    config_path = _write(
        tmp_path / "catalog.yaml",
        """
        version: 1
        duckdb:
          database: catalog.duckdb
          secrets: []
        views:
          - name: test_view
            sql: "SELECT 1"
        """,
    )

    config = load_config(str(config_path))
    assert config.duckdb.secrets == []


def test_duckdb_secrets_no_secrets(tmp_path):
    config_path = _write(
        tmp_path / "catalog.yaml",
        """
        version: 1
        duckdb:
          database: catalog.duckdb
        views:
          - name: test_view
            sql: "SELECT 1"
        """,
    )

    config = load_config(str(config_path))
    assert config.duckdb.secrets == []
