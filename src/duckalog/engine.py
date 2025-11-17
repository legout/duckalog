"""Duckalog catalog build engine."""

from __future__ import annotations

import logging
from typing import Optional

import duckdb

from .config import Config, load_config
from .logging_utils import get_logger, log_debug, log_info
from .sql_generation import generate_all_views_sql, generate_view_sql

logger = get_logger()


class EngineError(Exception):
    """Engine-level error raised during catalog builds.

    This exception wraps lower-level DuckDB errors, such as failures to
    connect to the database, attach external systems, or execute generated
    SQL statements.
    """


def build_catalog(
    config_path: str,
    db_path: Optional[str] = None,
    dry_run: bool = False,
    verbose: bool = False,
) -> Optional[str]:
    """Build or update a DuckDB catalog from a configuration file.

    This function is the high-level entry point used by both the CLI and
    Python API. It loads the config, optionally performs a dry-run SQL
    generation, or otherwise connects to DuckDB, sets up attachments and
    Iceberg catalogs, and creates or replaces configured views.

    Args:
        config_path: Path to the YAML/JSON configuration file.
        db_path: Optional override for ``duckdb.database`` in the config.
        dry_run: If ``True``, do not connect to DuckDB; instead generate and
            return the full SQL script for all views.
        verbose: If ``True``, enable more verbose logging via the standard
            logging module.

    Returns:
        The generated SQL script as a string when ``dry_run`` is ``True``,
        otherwise ``None`` when the catalog is applied to DuckDB.

    Raises:
        ConfigError: If the configuration file is invalid.
        EngineError: If connecting to DuckDB or executing SQL fails.

    Example:
        Build a catalog in-place::

            from duckalog import build_catalog

            build_catalog("catalog.yaml")

        Generate SQL without modifying the database::

            sql = build_catalog("catalog.yaml", dry_run=True)
            print(sql)
    """

    if verbose:
        logging.getLogger("duckalog").setLevel(logging.INFO)

    config = load_config(config_path)

    if dry_run:
        sql = generate_all_views_sql(config)
        log_info("Dry run SQL generation complete", views=len(config.views))
        return sql

    target_db = _resolve_db_path(config, db_path)
    log_info("Connecting to DuckDB", db_path=target_db)
    try:
        conn = duckdb.connect(target_db)
    except Exception as exc:  # pragma: no cover - duckdb handles errors
        raise EngineError(f"Failed to connect to DuckDB at {target_db}: {exc}") from exc

    try:
        _apply_duckdb_settings(conn, config, verbose)
        _setup_attachments(conn, config, verbose)
        _setup_iceberg_catalogs(conn, config, verbose)
        _create_views(conn, config, verbose)
    except EngineError:
        conn.close()
        raise
    except Exception as exc:  # pragma: no cover - wrapped for clarity
        conn.close()
        raise EngineError(f"DuckDB execution failed: {exc}") from exc

    conn.close()
    log_info("Catalog build complete", db_path=target_db)
    return None


def _resolve_db_path(config: Config, override: Optional[str]) -> str:
    if override:
        return override
    if config.duckdb.database:
        return config.duckdb.database
    return ":memory:"


def _create_secrets(
    conn: duckdb.DuckDBPyConnection, config: Config, verbose: bool
) -> None:
    """Create DuckDB secrets from configuration."""
    db_conf = config.duckdb
    if not db_conf.secrets:
        return

    log_info("Creating DuckDB secrets", count=len(db_conf.secrets))
    for index, secret in enumerate(db_conf.secrets, start=1):
        log_debug("Creating secret", index=index, type=secret.type, name=secret.name)

        # For now, we'll log the secret configuration but not actually create it
        # since CREATE SECRET syntax varies by DuckDB version and may not be available
        # This allows the configuration to be validated and documented
        log_info(
            "Secret configuration parsed",
            name=secret.name or secret.type,
            type=secret.type,
            provider=secret.provider,
            persistent=secret.persistent,
        )

        # TODO: Implement actual CREATE SECRET when syntax is stable
        # For now, we'll just log that we would create the secret
        secret_config = {
            "name": secret.name or secret.type,
            "type": secret.type,
            "provider": secret.provider,
            "persistent": secret.persistent,
        }

        if secret.provider == "config":
            if secret.type == "s3":
                if secret.key_id:
                    secret_config["key_id"] = secret.key_id
                if secret.secret:
                    secret_config["secret"] = "***REDACTED***"
                if secret.region:
                    secret_config["region"] = secret.region
                if secret.endpoint:
                    secret_config["endpoint"] = secret.endpoint
            elif secret.type == "azure":
                if secret.connection_string:
                    secret_config["connection_string"] = "***REDACTED***"
                else:
                    if secret.tenant_id:
                        secret_config["tenant_id"] = secret.tenant_id
                    if secret.account_name:
                        secret_config["account_name"] = secret.account_name
                    if secret.secret:
                        secret_config["secret"] = "***REDACTED***"
            elif secret.type == "http":
                if secret.key_id:
                    secret_config["key_id"] = secret.key_id
                if secret.secret:
                    secret_config["secret"] = "***REDACTED***"

        log_debug("Secret would be created", config=secret_config)


def _apply_duckdb_settings(
    conn: duckdb.DuckDBPyConnection, config: Config, verbose: bool
) -> None:
    db_conf = config.duckdb
    for ext in db_conf.install_extensions:
        log_info("Installing DuckDB extension", extension=ext)
        conn.install_extension(ext)
    for ext in db_conf.load_extensions:
        log_info("Loading DuckDB extension", extension=ext)
        conn.load_extension(ext)

    # Create secrets after extensions but before pragmas
    _create_secrets(conn, config, verbose)

    if db_conf.pragmas:
        log_info("Executing DuckDB pragmas", count=len(db_conf.pragmas))
    for index, pragma in enumerate(db_conf.pragmas, start=1):
        log_debug("Running pragma", index=index)
        conn.execute(pragma)

    # Apply settings after pragmas
    if db_conf.settings:
        settings_list = (
            db_conf.settings
            if isinstance(db_conf.settings, list)
            else [db_conf.settings]
        )
        log_info("Executing DuckDB settings", count=len(settings_list))
        for index, setting in enumerate(settings_list, start=1):
            log_debug("Running setting", index=index, setting=setting)
            conn.execute(setting)


def _setup_attachments(
    conn: duckdb.DuckDBPyConnection, config: Config, verbose: bool
) -> None:
    for duckdb_attachment in config.attachments.duckdb:
        clause = " (READ_ONLY)" if duckdb_attachment.read_only else ""
        log_info(
            "Attaching DuckDB database",
            alias=duckdb_attachment.alias,
            path=duckdb_attachment.path,
            read_only=duckdb_attachment.read_only,
        )
        conn.execute(
            f"ATTACH DATABASE '{_quote_literal(duckdb_attachment.path)}' AS \"{duckdb_attachment.alias}\"{clause}"
        )

    for sqlite_attachment in config.attachments.sqlite:
        log_info(
            "Attaching SQLite database",
            alias=sqlite_attachment.alias,
            path=sqlite_attachment.path,
        )
        conn.execute(
            f"ATTACH DATABASE '{_quote_literal(sqlite_attachment.path)}' AS \"{sqlite_attachment.alias}\" (TYPE SQLITE)"
        )

    for pg_attachment in config.attachments.postgres:
        log_info(
            "Attaching Postgres database",
            alias=pg_attachment.alias,
            host=pg_attachment.host,
            database=pg_attachment.database,
            user=pg_attachment.user,
        )
        log_debug(
            "Postgres attachment details",
            alias=pg_attachment.alias,
            user=pg_attachment.user,
            password=pg_attachment.password,
            options=pg_attachment.options,
        )
        clauses = [
            "TYPE POSTGRES",
            f"HOST '{_quote_literal(pg_attachment.host)}'",
            f"PORT {pg_attachment.port}",
            f"USER '{_quote_literal(pg_attachment.user)}'",
            f"PASSWORD '{_quote_literal(pg_attachment.password)}'",
            f"DATABASE '{_quote_literal(pg_attachment.database)}'",
        ]
        if pg_attachment.sslmode:
            clauses.append(f"SSLMODE '{_quote_literal(pg_attachment.sslmode)}'")
        for key, value in pg_attachment.options.items():
            clauses.append(f"{key.upper()} '{_quote_literal(str(value))}'")
        clause_sql = ", ".join(clauses)
        conn.execute(
            f"ATTACH DATABASE '{_quote_literal(pg_attachment.database)}' AS \"{pg_attachment.alias}\" ({clause_sql})"
        )


def _setup_iceberg_catalogs(
    conn: duckdb.DuckDBPyConnection, config: Config, verbose: bool
) -> None:
    for catalog in config.iceberg_catalogs:
        log_info(
            "Registering Iceberg catalog",
            name=catalog.name,
            catalog_type=catalog.catalog_type,
        )
        log_debug("Iceberg catalog options", name=catalog.name, options=catalog.options)
        options = []
        if catalog.uri:
            options.append(f"uri => '{_quote_literal(catalog.uri)}'")
        if catalog.warehouse:
            options.append(f"warehouse => '{_quote_literal(catalog.warehouse)}'")
        for key, value in catalog.options.items():
            options.append(f"{key} => '{_quote_literal(str(value))}'")
        options_sql = ", ".join(options)
        query = (
            "CALL iceberg_attach("
            f"'{_quote_literal(catalog.name)}', "
            f"'{_quote_literal(catalog.catalog_type)}'"
            f"{', ' + options_sql if options_sql else ''})"
        )
        conn.execute(query)


def _create_views(
    conn: duckdb.DuckDBPyConnection, config: Config, verbose: bool
) -> None:
    for view in config.views:
        sql = generate_view_sql(view)
        log_info("Creating or replacing view", name=view.name)
        conn.execute(sql)


__all__ = ["build_catalog", "EngineError"]


def _quote_literal(value: str) -> str:
    return value.replace("'", "''")
