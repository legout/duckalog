"""Configuration schema and loader for Duckalog catalogs."""

from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Literal, Optional, Union

import yaml
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    ValidationInfo,
    ValidationError,
    field_validator,
    model_validator,
)

from .logging_utils import log_debug, log_info
from .path_resolution import (
    PathResolutionError,
    is_relative_path,
    resolve_relative_path,
    validate_path_security,
)

if TYPE_CHECKING:  # pragma: no cover - used for type checking only
    from .sql_file_loader import SQLFileLoader


class ConfigError(Exception):
    """Configuration-related error.

    This exception is raised when a catalog configuration cannot be read,
    parsed, interpolated, or validated according to the Duckalog schema.

    Typical error conditions include:

    * The config file does not exist or cannot be read.
    * The file is not valid YAML/JSON.
    * Required fields are missing or invalid.
    * An environment variable placeholder cannot be resolved.
    """


EnvSource = Literal["parquet", "delta", "iceberg", "duckdb", "sqlite", "postgres"]
SecretType = Literal["s3", "azure", "gcs", "http", "postgres", "mysql"]
SecretProvider = Literal["config", "credential_chain"]
ENV_PATTERN = re.compile(r"\$\{env:([A-Za-z_][A-Za-z0-9_]*)\}")


class SecretConfig(BaseModel):
    """Configuration for a DuckDB secret.

    Attributes:
        type: Secret type (s3, azure, gcs, http, postgres, mysql).
        name: Optional name for the secret (defaults to type if not provided).
        provider: Secret provider (config or credential_chain).
        persistent: Whether to create a persistent secret. Defaults to False.
        scope: Optional scope prefix for the secret.
        key_id: Access key ID or username for authentication.
        secret: Secret key or password for authentication.
        region: Geographic region for cloud services.
        endpoint: Custom endpoint URL for cloud services.
        connection_string: Full connection string for databases.
        tenant_id: Azure tenant ID for authentication.
        account_name: Azure storage account name.
        database: Database name for database secrets.
        host: Database host for database secrets.
        port: Database port for database secrets.
        options: Additional key-value options for the secret.
    """

    type: SecretType
    name: Optional[str] = None
    provider: SecretProvider = "config"
    persistent: bool = False
    scope: Optional[str] = None
    key_id: Optional[str] = None
    secret: Optional[str] = None
    region: Optional[str] = None
    endpoint: Optional[str] = None
    connection_string: Optional[str] = None
    tenant_id: Optional[str] = None
    account_name: Optional[str] = None
    database: Optional[str] = None
    host: Optional[str] = None
    port: Optional[int] = None
    options: Dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(extra="forbid")

    @field_validator("name")
    @classmethod
    def _validate_name(cls, value: Optional[str]) -> Optional[str]:
        if value is not None:
            value = value.strip()
            if not value:
                raise ValueError("Secret name cannot be empty")
        return value

    @model_validator(mode="after")
    def _validate_secret_fields(self) -> "SecretConfig":
        """Validate required fields based on secret type and provider."""
        if self.type == "s3":
            if self.provider == "config":
                if not self.key_id or not self.secret:
                    raise ValueError("S3 config provider requires key_id and secret")
            # credential_chain provider doesn't require explicit credentials
        elif self.type == "azure":
            if self.provider == "config":
                if not self.connection_string and not (
                    self.tenant_id and self.account_name
                ):
                    raise ValueError(
                        "Azure config provider requires connection_string or (tenant_id and account_name)"
                    )
        elif self.type == "gcs":
            if self.provider == "config":
                if not self.key_id or not self.secret:
                    raise ValueError("GCS config provider requires key_id and secret")
        elif self.type == "http":
            if not self.key_id or not self.secret:
                raise ValueError(
                    "HTTP secret requires key_id (username) and secret (password)"
                )
        elif self.type in {"postgres", "mysql"}:
            if not self.connection_string and not (self.host and self.database):
                raise ValueError(
                    f"{self.type.upper()} secret requires connection_string or (host and database)"
                )
        return self


class DuckDBConfig(BaseModel):
    """DuckDB connection and session settings.

    Attributes:
        database: Path to the DuckDB database file. Defaults to ``":memory:"``.
        install_extensions: Names of extensions to install before use.
        load_extensions: Names of extensions to load in the session.
        pragmas: SQL statements (typically ``SET`` pragmas) executed after
            connecting and loading extensions.
        settings: DuckDB SET statements executed after pragmas. Can be a
            single string or list of strings.
        secrets: List of secret definitions for external services and databases.
    """

    database: str = ":memory:"
    install_extensions: List[str] = Field(default_factory=list)
    load_extensions: List[str] = Field(default_factory=list)
    pragmas: List[str] = Field(default_factory=list)
    settings: Union[str, List[str], None] = None
    secrets: List[SecretConfig] = Field(default_factory=list)

    @field_validator("settings")
    @classmethod
    def _validate_settings(
        cls, value: Union[str, List[str], None]
    ) -> Union[str, List[str], None]:
        if value is None:
            return None

        if isinstance(value, str):
            value = value.strip()
            if not value:
                return None
            # Basic validation for SET statement format
            if not value.upper().startswith("SET "):
                raise ValueError("Settings must be valid DuckDB SET statements")
            return value

        if isinstance(value, list):
            validated_settings = []
            for setting in value:
                if isinstance(setting, str):
                    setting = setting.strip()
                    if setting:  # Skip empty strings
                        if not setting.upper().startswith("SET "):
                            raise ValueError(
                                "Settings must be valid DuckDB SET statements"
                            )
                        validated_settings.append(setting)
                else:
                    raise ValueError("Settings list must contain only strings")
            return validated_settings if validated_settings else None

        raise ValueError("Settings must be a string or list of strings")

    model_config = ConfigDict(extra="forbid")


class DuckDBAttachment(BaseModel):
    """Configuration for attaching another DuckDB database.

    Attributes:
        alias: Alias under which the database will be attached.
        path: Filesystem path to the DuckDB database file.
        read_only: Whether the attachment should be opened in read-only mode.
            Defaults to ``True`` for safety.
    """

    alias: str
    path: str
    read_only: bool = True

    model_config = ConfigDict(extra="forbid")


class SQLiteAttachment(BaseModel):
    """Configuration for attaching a SQLite database.

    Attributes:
        alias: Alias under which the SQLite database will be attached.
        path: Filesystem path to the SQLite ``.db`` file.
    """

    alias: str
    path: str

    model_config = ConfigDict(extra="forbid")


class PostgresAttachment(BaseModel):
    """Configuration for attaching a Postgres database.

    Attributes:
        alias: Alias used inside DuckDB to reference the Postgres database.
        host: Hostname or IP address of the Postgres server.
        port: TCP port of the Postgres server.
        database: Database name to connect to.
        user: Username for authentication.
        password: Password for authentication.
        sslmode: Optional SSL mode (for example, ``require``).
        options: Extra key/value options passed to the attachment clause.
    """

    alias: str
    host: str
    port: int = Field(ge=1, le=65535)
    database: str
    user: str
    password: str
    sslmode: Optional[str] = None
    options: Dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(extra="forbid")


class DuckalogAttachment(BaseModel):
    """Configuration for attaching another Duckalog catalog config.

    Attributes:
        alias: Alias under which the child catalog will be attached.
        config_path: Path to the child Duckalog config file.
        database: Optional override for the child's database file path.
        read_only: Whether the attachment should be opened in read-only mode.
            Defaults to ``True`` for safety.
    """

    alias: str
    config_path: str
    database: Optional[str] = None
    read_only: bool = True

    @field_validator("alias")
    @classmethod
    def _validate_alias(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("Duckalog attachment alias cannot be empty")
        return value.strip()

    @field_validator("config_path")
    @classmethod
    def _validate_config_path(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("Duckalog attachment config_path cannot be empty")
        return value.strip()

    model_config = ConfigDict(extra="forbid")


class AttachmentsConfig(BaseModel):
    """Collection of attachment configurations.

    Attributes:
        duckdb: DuckDB attachment entries.
        sqlite: SQLite attachment entries.
        postgres: Postgres attachment entries.
        duckalog: Duckalog config attachment entries.
    """

    duckdb: List[DuckDBAttachment] = Field(default_factory=list)
    sqlite: List[SQLiteAttachment] = Field(default_factory=list)
    postgres: List[PostgresAttachment] = Field(default_factory=list)
    duckalog: List[DuckalogAttachment] = Field(default_factory=list)

    model_config = ConfigDict(extra="forbid")


class IcebergCatalogConfig(BaseModel):
    """Configuration for an Iceberg catalog.

    Attributes:
        name: Catalog name referenced by Iceberg views.
        catalog_type: Backend type (for example, ``rest``, ``hive``, ``glue``).
        uri: Optional URI used by certain catalog types.
        warehouse: Optional warehouse location for catalog data.
        options: Additional catalog-specific options.
    """

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


class SQLFileReference(BaseModel):
    """Reference to SQL content in an external file.

    Attributes:
        path: Path to the SQL file (relative or absolute).
        variables: Dictionary of variables for template substitution.
        as_template: Whether to process the file content as a template.
    """

    path: str = Field(..., description="Path to the SQL file")
    variables: Optional[Dict[str, Any]] = Field(
        default=None, description="Variables for template substitution"
    )
    as_template: bool = Field(
        default=False, description="Whether to process as template"
    )


class ViewConfig(BaseModel):
    """Definition of a single catalog view.

    A view can be defined in several ways:
    1. **Inline SQL**: Using the ``sql`` field with raw SQL text
    2. **SQL File**: Using ``sql_file`` to reference external SQL files
    3. **SQL Template**: Using ``sql_template`` for parameterized SQL files
    4. **Data Source**: Using ``source`` + required fields for direct data access
    5. **Source + SQL**: Using ``source`` for data access plus ``sql`` for transformations

    For data sources, the required fields depend on the source type:
    - Parquet/Delta: ``uri`` field is required
    - Iceberg: Either ``uri`` OR both ``catalog`` and ``table``
    - DuckDB/SQLite/Postgres: Both ``database`` and ``table`` are required

    When using SQL with a data source, the SQL will be applied as a transformation
    over the data from the specified source.

    Additional metadata fields such as ``description`` and ``tags`` do not affect
    SQL generation but are preserved for documentation and tooling.

    Attributes:
        name: Unique view name within the config.
        sql: Raw SQL text defining the view body.
        sql_file: Direct reference to a SQL file.
        sql_template: Reference to a SQL template file with variable substitution.
        source: Source type (e.g. ``"parquet"``, ``"iceberg"``, ``"duckdb"``).
        uri: URI for file- or table-based sources (Parquet/Delta/Iceberg).
        database: Attachment alias for attached-database sources.
        table: Table name (optionally schema-qualified) for attached sources.
        catalog: Iceberg catalog name for catalog-based Iceberg views.
        options: Source-specific options passed to scan functions.
        description: Optional human-readable description of the view.
        tags: Optional list of tags for classification.
    """

    name: str
    sql: Optional[str] = None
    sql_file: Optional[SQLFileReference] = None
    sql_template: Optional[SQLFileReference] = None
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
        has_sql_file = self.sql_file is not None
        has_sql_template = self.sql_template is not None
        has_source = self.source is not None

        # Count how many SQL sources are defined
        sql_sources = sum([has_sql, has_sql_file, has_sql_template])

        # Must have either SQL content or a data source
        if sql_sources == 0 and not has_source:
            raise ValueError("View must define either SQL content or a data source")

        # Cannot have multiple SQL sources
        if sql_sources > 1:
            raise ValueError(
                "View cannot have multiple SQL sources (sql, sql_file, sql_template). "
                "Use only one of these fields."
            )

        # Validate SQL file references
        if self.sql_file is not None:
            if not self.sql_file.path or not self.sql_file.path.strip():
                raise ValueError(f"View '{self.name}': sql_file.path cannot be empty")

        if self.sql_template is not None:
            if not self.sql_template.path or not self.sql_template.path.strip():
                raise ValueError(
                    f"View '{self.name}': sql_template.path cannot be empty"
                )

        # If we have SQL content, clean it up
        if isinstance(self.sql, str) and self.sql.strip():
            self.sql = self.sql.strip()

        # Validate data source configuration (if source is defined)
        if has_source:
            if self.source in {"parquet", "delta"}:
                if not self.uri:
                    raise ValueError(
                        f"View '{self.name}' requires a 'uri' for source '{self.source}'"
                    )
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


class SemanticDimensionConfig(BaseModel):
    """Definition of a semantic dimension.

    A dimension represents a business attribute that maps to an expression
    over the base view of a semantic model.

    Attributes:
        name: Unique dimension name within the semantic model.
        expression: SQL expression referencing columns from the base view.
        label: Human-readable display name.
        description: Optional detailed description.
        type: Optional data type hint (time, number, string, boolean, date).
        time_grains: Optional list of time grains for time dimensions.
    """

    name: str
    expression: str
    label: Optional[str] = None
    description: Optional[str] = None
    type: Optional[str] = None
    time_grains: List[str] = Field(default_factory=list)

    model_config = ConfigDict(extra="forbid")

    @field_validator("name")
    @classmethod
    def _validate_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Dimension name cannot be empty")
        return value

    @field_validator("expression")
    @classmethod
    def _validate_expression(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Dimension expression cannot be empty")
        return value

    @field_validator("type")
    @classmethod
    def _validate_type(cls, value: Optional[str]) -> Optional[str]:
        if value is not None:
            value = value.strip().lower()
            valid_types = {"time", "number", "string", "boolean", "date"}
            if value not in valid_types:
                raise ValueError(
                    f"Invalid dimension type '{value}'. Valid types are: {', '.join(sorted(valid_types))}"
                )
        return value

    @field_validator("time_grains")
    @classmethod
    def _validate_time_grains(cls, value: List[str], info: ValidationInfo) -> List[str]:
        if value:
            # Only allow time_grains for time dimensions
            if info.data.get("type") != "time":
                raise ValueError(
                    "time_grains can only be specified for time dimensions"
                )

            valid_grains = {
                "year",
                "quarter",
                "month",
                "week",
                "day",
                "hour",
                "minute",
                "second",
            }
            for grain in value:
                grain_clean = grain.strip().lower()
                if grain_clean not in valid_grains:
                    raise ValueError(
                        f"Invalid time grain '{grain}'. Valid grains are: {', '.join(sorted(valid_grains))}"
                    )

            # Return cleaned time grains
            return [grain.strip().lower() for grain in value]
        return value


class SemanticMeasureConfig(BaseModel):
    """Definition of a semantic measure.

    A measure represents a business metric that typically involves aggregation
    or calculation over the base view of a semantic model.

    Attributes:
        name: Unique measure name within the semantic model.
        expression: SQL expression (often aggregated) over the base view.
        label: Human-readable display name.
        description: Optional detailed description.
        type: Optional data type hint.
    """

    name: str
    expression: str
    label: Optional[str] = None
    description: Optional[str] = None
    type: Optional[str] = None

    model_config = ConfigDict(extra="forbid")

    @field_validator("name")
    @classmethod
    def _validate_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Measure name cannot be empty")
        return value

    @field_validator("expression")
    @classmethod
    def _validate_expression(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Measure expression cannot be empty")
        return value


class SemanticJoinConfig(BaseModel):
    """Definition of a semantic join.

    A join defines a relationship to another view for enriching the semantic model
    with additional data, typically dimension tables.

    Attributes:
        to_view: Name of an existing view in the views section to join to.
        type: Join type (inner, left, right, full).
        on_condition: SQL join condition expression.
    """

    to_view: str
    type: str
    on_condition: str

    model_config = ConfigDict(extra="forbid")

    @field_validator("to_view")
    @classmethod
    def _validate_to_view(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Join 'to_view' cannot be empty")
        return value

    @field_validator("type")
    @classmethod
    def _validate_type(cls, value: str) -> str:
        value = value.strip().lower()
        valid_types = {"inner", "left", "right", "full"}
        if value not in valid_types:
            raise ValueError(
                f"Invalid join type '{value}'. Valid types are: {', '.join(sorted(valid_types))}"
            )
        return value

    @field_validator("on_condition")
    @classmethod
    def _validate_on_condition(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Join 'on_condition' cannot be empty")
        return value


class SemanticDefaultsConfig(BaseModel):
    """Default configuration for a semantic model.

    Provides default settings for query builders and dashboards,
    such as the primary time dimension and default measures.

    Attributes:
        time_dimension: Default time dimension name.
        primary_measure: Default primary measure name.
        default_filters: Optional list of default filters.
    """

    time_dimension: Optional[str] = None
    primary_measure: Optional[str] = None
    default_filters: List[Dict[str, Any]] = Field(default_factory=list)

    model_config = ConfigDict(extra="forbid")

    @field_validator("time_dimension")
    @classmethod
    def _validate_time_dimension(cls, value: Optional[str]) -> Optional[str]:
        if value is not None:
            value = value.strip()
            if not value:
                raise ValueError("Default time dimension cannot be empty string")
        return value

    @field_validator("primary_measure")
    @classmethod
    def _validate_primary_measure(cls, value: Optional[str]) -> Optional[str]:
        if value is not None:
            value = value.strip()
            if not value:
                raise ValueError("Default primary measure cannot be empty string")
        return value


class SemanticModelConfig(BaseModel):
    """Definition of a semantic model.

    A semantic model provides business-friendly metadata on top of an existing
    Duckalog view, defining dimensions and measures for analytics and BI use cases.

    Attributes:
        name: Unique semantic model name within the config.
        base_view: Name of an existing view in the views section.
        dimensions: Optional list of dimension definitions.
        measures: Optional list of measure definitions.
        joins: Optional list of join definitions to other views.
        defaults: Optional default configuration for query builders.
        label: Human-readable display name.
        description: Optional detailed description.
        tags: Optional list of classification tags.
    """

    name: str
    base_view: str
    dimensions: List[SemanticDimensionConfig] = Field(default_factory=list)
    measures: List[SemanticMeasureConfig] = Field(default_factory=list)
    joins: List[SemanticJoinConfig] = Field(default_factory=list)
    defaults: Optional[SemanticDefaultsConfig] = None
    label: Optional[str] = None
    description: Optional[str] = None
    tags: List[str] = Field(default_factory=list)

    model_config = ConfigDict(extra="forbid")

    @field_validator("name")
    @classmethod
    def _validate_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Semantic model name cannot be empty")
        return value

    @field_validator("base_view")
    @classmethod
    def _validate_base_view(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Base view cannot be empty")
        return value

    @model_validator(mode="after")
    def _validate_uniqueness(self) -> "SemanticModelConfig":
        """Validate that dimension and measure names are unique within the model."""
        dimension_names = {dim.name for dim in self.dimensions}
        measure_names = {measure.name for measure in self.measures}

        # Check for duplicate dimension names
        if len(dimension_names) != len(self.dimensions):
            duplicates = [
                name
                for name in dimension_names
                if sum(1 for dim in self.dimensions if dim.name == name) > 1
            ]
            raise ValueError(
                f"Duplicate dimension name(s) found: {', '.join(duplicates)}"
            )

        # Check for duplicate measure names
        if len(measure_names) != len(self.measures):
            duplicates = [
                name
                for name in measure_names
                if sum(1 for measure in self.measures if measure.name == name) > 1
            ]
            raise ValueError(
                f"Duplicate measure name(s) found: {', '.join(duplicates)}"
            )

        # Check for conflicts between dimensions and measures
        conflicts = dimension_names.intersection(measure_names)
        if conflicts:
            raise ValueError(
                f"Dimension and measure name(s) conflict: {', '.join(sorted(conflicts))}"
            )

        # Validate defaults reference existing dimensions and measures
        if self.defaults:
            if self.defaults.time_dimension:
                if self.defaults.time_dimension not in dimension_names:
                    raise ValueError(
                        f"Default time dimension '{self.defaults.time_dimension}' does not exist in dimensions"
                    )
                # Verify the time dimension is actually typed as 'time'
                time_dim = next(
                    (
                        dim
                        for dim in self.dimensions
                        if dim.name == self.defaults.time_dimension
                    ),
                    None,
                )
                if time_dim and time_dim.type != "time":
                    raise ValueError(
                        f"Default time dimension '{self.defaults.time_dimension}' must have type 'time'"
                    )

            if self.defaults.primary_measure:
                if self.defaults.primary_measure not in measure_names:
                    raise ValueError(
                        f"Default primary measure '{self.defaults.primary_measure}' does not exist in measures"
                    )

            # Validate default filters reference existing dimensions
            for filter_def in self.defaults.default_filters:
                filter_dimension = filter_def.get("dimension")
                if filter_dimension and filter_dimension not in dimension_names:
                    raise ValueError(
                        f"Default filter dimension '{filter_dimension}' does not exist in dimensions"
                    )

        return self


class Config(BaseModel):
    """Top-level Duckalog configuration.

    Attributes:
        version: Positive integer describing the config schema version.
        duckdb: DuckDB session and connection settings.
        views: List of view definitions to create in the catalog.
        attachments: Optional attachments to external databases.
        iceberg_catalogs: Optional Iceberg catalog definitions.
        semantic_models: Optional semantic model definitions for business metadata.
    """

    version: int
    duckdb: DuckDBConfig
    views: List[ViewConfig]
    attachments: AttachmentsConfig = Field(default_factory=AttachmentsConfig)
    iceberg_catalogs: List[IcebergCatalogConfig] = Field(default_factory=list)
    semantic_models: List[SemanticModelConfig] = Field(default_factory=list)

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
            if (
                view.source == "iceberg"
                and view.catalog
                and view.catalog not in defined_catalogs
            ):
                missing_catalog_views.append(f"{view.name} -> {view.catalog}")
        if missing_catalog_views:
            details = ", ".join(missing_catalog_views)
            raise ValueError(
                "Iceberg view(s) reference undefined catalog(s): "
                f"{details}. Define each catalog under `iceberg_catalogs`."
            )

        # Validate semantic models
        semantic_model_names: Dict[str, int] = {}
        duplicates = []
        for semantic_model in self.semantic_models:
            if semantic_model.name in semantic_model_names:
                duplicates.append(semantic_model.name)
            else:
                semantic_model_names[semantic_model.name] = 1
        if duplicates:
            dup_list = ", ".join(sorted(set(duplicates)))
            raise ValueError(f"Duplicate semantic model name(s) found: {dup_list}")

        # Validate that semantic model base views exist
        view_names = {view.name for view in self.views}
        missing_base_views: List[str] = []
        for semantic_model in self.semantic_models:
            if semantic_model.base_view not in view_names:
                missing_base_views.append(
                    f"{semantic_model.name} -> {semantic_model.base_view}"
                )
        if missing_base_views:
            details = ", ".join(missing_base_views)
            raise ValueError(
                "Semantic model(s) reference undefined base view(s): "
                f"{details}. Define each view under `views`."
            )

        # Validate that semantic model joins reference existing views
        missing_join_views: List[str] = []
        for semantic_model in self.semantic_models:
            for join in semantic_model.joins:
                if join.to_view not in view_names:
                    missing_join_views.append(f"{semantic_model.name}.{join.to_view}")
        if missing_join_views:
            details = ", ".join(missing_join_views)
            raise ValueError(
                "Semantic model join(s) reference undefined view(s): "
                f"{details}. Define each view under `views`."
            )

        return self


def load_config(
    path: str,
    load_sql_files: bool = True,
    sql_file_loader: Optional["SQLFileLoader"] = None,
    resolve_paths: bool = True,
    filesystem: Optional[Any] = None,
) -> Config:
    """Load, interpolate, and validate a Duckalog configuration file.

    This helper is the main entry point for turning a YAML or JSON file into a
    validated :class:`Config` instance. It applies environment-variable
    interpolation and enforces the configuration schema.

    Args:
        path: Path to a YAML or JSON config file, or a remote URI.
        load_sql_files: Whether to load and process SQL from external files.
                      If False, SQL file references are left as-is for later processing.
        sql_file_loader: Optional SQLFileLoader instance for loading SQL files.
                        If None, a default loader will be created.
        resolve_paths: Whether to resolve relative paths to absolute paths.
                      If True, relative paths in view URIs and attachment paths
                      will be resolved relative to the config file's directory.
                      For remote configs, this defaults to False.
        filesystem: Optional fsspec filesystem object to use for remote operations.
                   If provided, this filesystem will be used instead of creating
                   a new one based on URI scheme. Useful for custom
                   authentication or advanced use cases.

    Returns:
        A validated :class:`Config` object.

    Raises:
        ConfigError: If the file cannot be read, is not valid YAML/JSON,
            fails schema validation, contains unresolved
            ``${env:VAR_NAME}`` placeholders, or if SQL file loading fails.

    Example:
        Load a catalog from ``catalog.yaml``::

            from duckalog import load_config

            config = load_config("catalog.yaml")
            print(len(config.views))

        Load a catalog from S3::

            config = load_config("s3://my-bucket/configs/catalog.yaml")
            print(len(config.views))

        Load a catalog with custom filesystem::

            import fsspec
            fs = fsspec.filesystem("s3", key="key", secret="secret", anon=False)
            config = load_config("s3://my-bucket/configs/catalog.yaml", filesystem=fs)
            print(len(config.views))
    """
    # Check if this is a remote URI
    try:
        from .remote_config import is_remote_uri, load_config_from_uri

        if is_remote_uri(path):
            # For remote URIs, use the remote loader
            # Default resolve_paths to False for remote configs
            return load_config_from_uri(
                uri=path,
                load_sql_files=load_sql_files,
                sql_file_loader=sql_file_loader,
                resolve_paths=False,  # Remote configs don't resolve relative paths by default
                filesystem=filesystem,  # Pass through filesystem parameter
            )
    except ImportError:
        # Remote functionality not available, continue with local loading
        pass

    # Local file loading
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

    # Resolve relative paths if requested
    if resolve_paths:
        config = _resolve_paths_in_config(config, config_path)

    # Load SQL from external files if requested
    if load_sql_files:
        config = _load_sql_files_from_config(config, config_path, sql_file_loader)

    log_info("Config loaded", path=str(config_path), views=len(config.views))
    return config


def _load_sql_files_from_config(
    config: Config,
    config_path: Path,
    sql_file_loader: Optional["SQLFileLoader"] = None,
) -> Config:
    """Load SQL content from external files referenced in the config.

    This function processes views that have sql_file or sql_template references,
    loading the actual SQL content from the referenced files and substituting
    template variables where applicable.

    Args:
        config: The configuration object to process
        config_path: Path to the configuration file (for relative path resolution)
        sql_file_loader: SQLFileLoader instance to use for loading files

    Returns:
        Updated configuration with SQL content loaded from files

    Raises:
        ConfigError: If SQL file loading fails
    """
    # Import here to avoid circular import
    from .sql_file_loader import SQLFileError, SQLFileLoader

    if sql_file_loader is None:
        sql_file_loader = SQLFileLoader()

    updated_views = []
    for view in config.views:
        if view.sql_file is not None:
            # Handle direct SQL file reference
            try:
                sql_content = sql_file_loader.load_sql_file(
                    file_path=view.sql_file.path,
                    config_file_path=str(config_path),
                    variables=view.sql_file.variables,
                    as_template=view.sql_file.as_template,
                )

                # Create new view with inline SQL
                updated_view = ViewConfig(
                    name=view.name,
                    sql=sql_content,
                    source=view.source,
                    uri=view.uri,
                    database=view.database,
                    table=view.table,
                    catalog=view.catalog,
                    options=view.options,
                    description=view.description,
                    tags=view.tags,
                )
                updated_views.append(updated_view)

            except SQLFileError as exc:
                raise ConfigError(
                    f"Failed to load SQL file for view '{view.name}': {exc}"
                ) from exc

        elif view.sql_template is not None:
            # Handle SQL template reference
            try:
                sql_content = sql_file_loader.load_sql_file(
                    file_path=view.sql_template.path,
                    config_file_path=str(config_path),
                    variables=view.sql_template.variables,
                    as_template=True,  # Templates are always processed as templates
                )

                # Create new view with inline SQL
                updated_view = ViewConfig(
                    name=view.name,
                    sql=sql_content,
                    source=view.source,
                    uri=view.uri,
                    database=view.database,
                    table=view.table,
                    catalog=view.catalog,
                    options=view.options,
                    description=view.description,
                    tags=view.tags,
                )
                updated_views.append(updated_view)

            except SQLFileError as exc:
                raise ConfigError(
                    f"Failed to load SQL template for view '{view.name}': {exc}"
                ) from exc

        else:
            # No SQL file reference, keep original view
            updated_views.append(view)

    # Create updated config with processed views
    updated_config = Config(
        version=config.version,
        duckdb=config.duckdb,
        attachments=config.attachments,
        iceberg_catalogs=config.iceberg_catalogs,
        views=updated_views,
        semantic_models=config.semantic_models,
    )

    log_info(
        "SQL files loaded",
        total_views=len(config.views),
        file_based_views=len(
            [
                v
                for v in updated_views
                if v.sql
                and v != next((ov for ov in config.views if ov.name == v.name), None)
            ]
        ),
    )

    return updated_config


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


def _resolve_paths_in_config(config: Config, config_path: Path) -> Config:
    """Resolve relative paths in a configuration to absolute paths.

    This function processes view URIs and attachment paths, resolving any
    relative paths to absolute paths relative to the configuration file's directory.

    Args:
        config: The loaded configuration object
        config_path: Path to the configuration file

    Returns:
        The configuration with resolved paths

    Raises:
        ConfigError: If path resolution fails due to security or access issues
    """
    from copy import deepcopy

    try:
        config_dict = config.model_dump(mode="python")
        config_dir = config_path.parent

        # Resolve paths in views
        if "views" in config_dict and config_dict["views"]:
            for view_data in config_dict["views"]:
                _resolve_view_paths(view_data, config_dir)

        # Resolve paths in attachments
        if "attachments" in config_dict and config_dict["attachments"]:
            _resolve_attachment_paths(config_dict["attachments"], config_dir)

        # Revalidate the config with resolved paths
        resolved_config = Config.model_validate(config_dict)

        log_debug(
            "Path resolution completed",
            config_path=str(config_path),
            views_count=len(resolved_config.views),
            attachments_count=len(
                resolved_config.attachments.duckdb
                + resolved_config.attachments.sqlite
                + resolved_config.attachments.postgres
                + resolved_config.attachments.duckalog
            ),
        )

        return resolved_config

    except Exception as exc:
        raise ConfigError(f"Path resolution failed: {exc}") from exc


def _resolve_view_paths(view_data: dict, config_dir: Path) -> None:
    """Resolve paths in a single view configuration.

    Args:
        view_data: Dictionary representation of a view
        config_dir: Configuration file directory

    Raises:
        PathResolutionError: If path resolution fails security validation
    """
    if "uri" in view_data and view_data["uri"]:
        original_uri = view_data["uri"]

        if is_relative_path(original_uri):
            # Resolve the path (security validation is handled within resolve_relative_path)
            try:
                resolved_uri = resolve_relative_path(original_uri, config_dir)
                view_data["uri"] = resolved_uri
                log_debug(
                    "Resolved view URI", original=original_uri, resolved=resolved_uri
                )
            except ValueError as exc:
                raise PathResolutionError(
                    f"Failed to resolve URI '{original_uri}': {exc}",
                    original_path=original_uri,
                ) from exc


def _resolve_attachment_paths(attachments_data: dict, config_dir: Path) -> None:
    """Resolve paths in attachment configurations.

    Args:
        attachments_data: Dictionary representation of attachments
        config_dir: Configuration file directory

    Raises:
        PathResolutionError: If path resolution fails security validation
    """
    # Resolve DuckDB attachment paths
    if "duckdb" in attachments_data and attachments_data["duckdb"]:
        for attachment in attachments_data["duckdb"]:
            if "path" in attachment and attachment["path"]:
                original_path = attachment["path"]

                if is_relative_path(original_path):
                    # Resolve the path (security validation is handled within resolve_relative_path)
                    try:
                        resolved_path = resolve_relative_path(original_path, config_dir)
                        attachment["path"] = resolved_path
                        log_debug(
                            "Resolved DuckDB attachment",
                            original=original_path,
                            resolved=resolved_path,
                        )
                    except ValueError as exc:
                        raise PathResolutionError(
                            f"Failed to resolve DuckDB attachment path '{original_path}': {exc}",
                            original_path=original_path,
                        ) from exc

    # Resolve SQLite attachment paths
    if "sqlite" in attachments_data and attachments_data["sqlite"]:
        for attachment in attachments_data["sqlite"]:
            if "path" in attachment and attachment["path"]:
                original_path = attachment["path"]

                if is_relative_path(original_path):
                    # Resolve the path (security validation is handled within resolve_relative_path)
                    try:
                        resolved_path = resolve_relative_path(original_path, config_dir)
                        attachment["path"] = resolved_path
                        log_debug(
                            "Resolved SQLite attachment",
                            original=original_path,
                            resolved=resolved_path,
                        )
                    except ValueError as exc:
                        raise PathResolutionError(
                            f"Failed to resolve SQLite attachment path '{original_path}': {exc}",
                            original_path=original_path,
                        ) from exc

    # Resolve Duckalog attachment paths
    if "duckalog" in attachments_data and attachments_data["duckalog"]:
        for attachment in attachments_data["duckalog"]:
            # Resolve config_path relative to parent config
            if "config_path" in attachment and attachment["config_path"]:
                original_path = attachment["config_path"]
                if is_relative_path(original_path):
                    try:
                        resolved_path = resolve_relative_path(original_path, config_dir)
                        attachment["config_path"] = resolved_path
                        log_debug(
                            "Resolved Duckalog attachment config path",
                            original=original_path,
                            resolved=resolved_path,
                        )
                    except ValueError as exc:
                        raise PathResolutionError(
                            f"Failed to resolve Duckalog attachment config_path '{original_path}': {exc}",
                            original_path=original_path,
                        ) from exc

            # Resolve database override relative to parent config
            if "database" in attachment and attachment["database"]:
                original_db = attachment["database"]
                if is_relative_path(original_db):
                    try:
                        resolved_db = resolve_relative_path(original_db, config_dir)
                        attachment["database"] = resolved_db
                        log_debug(
                            "Resolved Duckalog attachment database override",
                            original=original_db,
                            resolved=resolved_db,
                        )
                    except ValueError as exc:
                        raise PathResolutionError(
                            f"Failed to resolve Duckalog attachment database '{original_db}': {exc}",
                            original_path=original_db,
                        ) from exc


__all__ = [
    "Config",
    "ConfigError",
    "DuckDBConfig",
    "SecretConfig",
    "AttachmentsConfig",
    "DuckDBAttachment",
    "SQLiteAttachment",
    "PostgresAttachment",
    "DuckalogAttachment",
    "IcebergCatalogConfig",
    "ViewConfig",
    "SemanticModelConfig",
    "SemanticDimensionConfig",
    "SemanticMeasureConfig",
    "load_config",
]
