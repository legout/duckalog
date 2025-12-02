"""Secret type configurations for DuckDB."""

from __future__ import annotations

from pydantic import BaseModel, Field


class S3SecretConfig(BaseModel):
    """S3 secret configuration."""

    key_id: str | None = None
    secret: str
    region: str | None = None
    endpoint: str | None = None


class AzureSecretConfig(BaseModel):
    """Azure secret configuration."""

    connection_string: str | None = None
    tenant_id: str | None = None
    client_id: str | None = None
    client_secret: str
    account_name: str | None = None


class GCSSecretConfig(BaseModel):
    """GCS secret configuration."""

    service_account_key: str
    json_key: str | None = None


class HTTPSecretConfig(BaseModel):
    """HTTP secret configuration."""

    bearer_token: str
    header: str | None = None


class PostgresSecretConfig(BaseModel):
    """PostgreSQL secret configuration."""

    connection_string: str | None = None
    host: str | None = None
    port: int | None = None
    database: str | None = None
    user: str | None = None
    password: str


class MySQLSecretConfig(BaseModel):
    """MySQL secret configuration."""

    connection_string: str | None = None
    host: str | None = None
    port: int | None = None
    database: str | None = None
    user: str | None = None
    password: str
