"""Configuration schema and loader for Duckalog catalogs."""

from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional

import yaml
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator, model_validator

from .logging_utils import log_debug, log_info


class ConfigError(Exception):
    """Raised when a catalog configuration cannot be parsed or validated."""


EnvSource = Literal["parquet", "delta", "iceberg", "duckdb", "sqlite", "postgres"]
ENV_PATTERN = re.compile(r"\$\{env:([A-Za-z_][A-Za-z0-9_]*)\}")


class DuckDBConfig(BaseModel):
    database: str = ":memory:"
    install_extensions: List[str] = Field(default_factory=list)
    load_extensions: List[str] = Field(default_factory=list)
    pragmas: List[str] = Field(default_factory=list)

    model_config = ConfigDict(extra="forbid")


class DuckDBAttachment(BaseModel):
    alias: str
    path: str
    read_only: bool = True

    model_config = ConfigDict(extra="forbid")


class SQLiteAttachment(BaseModel):
    alias: str
    path: str

    model_config = ConfigDict(extra="forbid")


class PostgresAttachment(BaseModel):
    alias: str
    host: str
    port: int = Field(ge=1, le=65535)
    database: str
    user: str
    password: str
    sslmode: Optional[str] = None
    options: Dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(extra="forbid")


class AttachmentsConfig(BaseModel):
    duckdb: List[DuckDBAttachment] = Field(default_factory=list)
    sqlite: List[SQLiteAttachment] = Field(default_factory=list)
    postgres: List[PostgresAttachment] = Field(default_factory=list)

    model_config = ConfigDict(extra="forbid")


class IcebergCatalogConfig(BaseModel):
    name: str
    catalog_type: str
    uri: Optional[str] = None
    warehouse: Optional[str] = None
    options: Dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(extra="forbid")

    @field_validator("name")
    @classmethod
    def _validate_name(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("Iceberg catalog name cannot be empty")
        return value


class ViewConfig(BaseModel):
    name: str
    sql: Optional[str] = None
    source: Optional[EnvSource] = None
    uri: Optional[str] = None
    database: Optional[str] = None
    table: Optional[str] = None
    catalog: Optional[str] = None
    options: Dict[str, Any] = Field(default_factory=dict)
    description: Optional[str] = None
    tags: List[str] = Field(default_factory=list)

    model_config = ConfigDict(extra="forbid")

    @field_validator("name")
    @classmethod
    def _validate_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("View name cannot be empty")
        return value

    @model_validator(mode="after")
    def _validate_definition(self) -> "ViewConfig":
        has_sql = bool(self.sql and self.sql.strip())
        has_source = self.source is not None

        if has_sql == has_source:
            raise ValueError("View must define exactly one of 'sql' or 'source'")

        if has_sql:
            self.sql = self.sql.strip()  # type: ignore[assignment]
            return self

        assert self.source is not None
        if self.source in {"parquet", "delta"}:
            if not self.uri:
                raise ValueError(f"View '{self.name}' requires a 'uri' for source '{self.source}'")
        elif self.source == "iceberg":
            has_uri = bool(self.uri)
            has_catalog_table = bool(self.catalog and self.table)
            if has_uri == has_catalog_table:
                raise ValueError(
                    "Iceberg views require either 'uri' OR both 'catalog' and 'table', but not both"
                )
        elif self.source in {"duckdb", "sqlite", "postgres"}:
            if not self.database or not self.table:
                raise ValueError(
                    f"View '{self.name}' with source '{self.source}' requires both 'database' and 'table'"
                )
        else:  # pragma: no cover - enforced by Literal
            raise ValueError(f"Unsupported view source '{self.source}'")

        return self


class Config(BaseModel):
    version: int
    duckdb: DuckDBConfig
    views: List[ViewConfig]
    attachments: AttachmentsConfig = Field(default_factory=AttachmentsConfig)
    iceberg_catalogs: List[IcebergCatalogConfig] = Field(default_factory=list)

    model_config = ConfigDict(extra="forbid")

    @field_validator("version")
    @classmethod
    def _version_positive(cls, value: int) -> int:
        if value <= 0:
            raise ValueError("Config version must be a positive integer")
        return value

    @model_validator(mode="after")
    def _validate_uniqueness(self) -> "Config":
        seen: Dict[str, int] = {}
        duplicates: List[str] = []
        for index, view in enumerate(self.views):
            if view.name in seen:
                duplicates.append(view.name)
            else:
                seen[view.name] = index
        if duplicates:
            dup_list = ", ".join(sorted(set(duplicates)))
            raise ValueError(f"Duplicate view name(s) found: {dup_list}")

        catalog_names: Dict[str, int] = {}
        duplicates = []
        for catalog in self.iceberg_catalogs:
            if catalog.name in catalog_names:
                duplicates.append(catalog.name)
            else:
                catalog_names[catalog.name] = 1
        if duplicates:
            dup_list = ", ".join(sorted(set(duplicates)))
            raise ValueError(f"Duplicate Iceberg catalog name(s) found: {dup_list}")

        missing_catalog_views: List[str] = []
        defined_catalogs = set(catalog_names.keys())
        for view in self.views:
            if view.source == "iceberg" and view.catalog and view.catalog not in defined_catalogs:
                missing_catalog_views.append(f"{view.name} -> {view.catalog}")
        if missing_catalog_views:
            details = ", ".join(missing_catalog_views)
            raise ValueError(
                "Iceberg view(s) reference undefined catalog(s): "
                f"{details}. Define each catalog under `iceberg_catalogs`."
            )

        return self


def load_config(path: str) -> Config:
    """Load a Duckalog config file, interpolate env vars, and validate it."""

    config_path = Path(path)
    if not config_path.exists():
        raise ConfigError(f"Config file not found: {path}")

    log_info("Loading config", path=str(config_path))
    try:
        raw_text = config_path.read_text()
    except OSError as exc:  # pragma: no cover - filesystem failures are rare
        raise ConfigError(f"Failed to read config file: {exc}") from exc

    suffix = config_path.suffix.lower()
    if suffix in {".yaml", ".yml"}:
        parsed = yaml.safe_load(raw_text)
    elif suffix == ".json":
        parsed = json.loads(raw_text)
    else:
        raise ConfigError("Config files must use .yaml, .yml, or .json extensions")

    if parsed is None:
        raise ConfigError("Config file is empty")
    if not isinstance(parsed, dict):
        raise ConfigError("Config file must define a mapping at the top level")

    log_debug("Raw config keys", keys=list(parsed.keys()))
    interpolated = _interpolate_env(parsed)

    try:
        config = Config.model_validate(interpolated)
    except ValidationError as exc:  # pragma: no cover - raised in tests
        raise ConfigError(exc.errors()) from exc

    log_info("Config loaded", path=str(config_path), views=len(config.views))
    return config


def _interpolate_env(value: Any) -> Any:
    """Recursively interpolate ${env:VAR} placeholders in config data."""

    if isinstance(value, str):
        return ENV_PATTERN.sub(_replace_env_match, value)
    if isinstance(value, list):
        return [_interpolate_env(item) for item in value]
    if isinstance(value, dict):
        return {key: _interpolate_env(val) for key, val in value.items()}
    return value


def _replace_env_match(match: re.Match[str]) -> str:
    var_name = match.group(1)
    try:
        return os.environ[var_name]
    except KeyError as exc:
        raise ConfigError(f"Environment variable '{var_name}' is not set") from exc


__all__ = [
    "Config",
    "ConfigError",
    "DuckDBConfig",
    "AttachmentsConfig",
    "DuckDBAttachment",
    "SQLiteAttachment",
    "PostgresAttachment",
    "IcebergCatalogConfig",
    "ViewConfig",
    "load_config",
]
