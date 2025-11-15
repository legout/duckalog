"""Duckalog catalog build engine."""

from __future__ import annotations

import logging
from typing import Optional

import duckdb

from .config import Config, load_config
from .sql_generation import generate_all_views_sql, generate_view_sql
from .logging_utils import get_logger, log_debug, log_info

logger = get_logger()


class EngineError(Exception):
    """Raised when DuckDB engine operations fail."""


def build_catalog(
    config_path: str,
    db_path: Optional[str] = None,
    dry_run: bool = False,
    verbose: bool = False,
) -> Optional[str]:
    """Build or update a DuckDB catalog from a config file.

    Returns the generated SQL string when ``dry_run`` is True, otherwise None.
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


def _apply_duckdb_settings(conn: duckdb.DuckDBPyConnection, config: Config, verbose: bool) -> None:
    db_conf = config.duckdb
    for ext in db_conf.install_extensions:
        log_info("Installing DuckDB extension", extension=ext)
        conn.install_extension(ext)
    for ext in db_conf.load_extensions:
        log_info("Loading DuckDB extension", extension=ext)
        conn.load_extension(ext)
    if db_conf.pragmas:
        log_info("Executing DuckDB pragmas", count=len(db_conf.pragmas))
    for index, pragma in enumerate(db_conf.pragmas, start=1):
        log_debug("Running pragma", index=index)
        conn.execute(pragma)


def _setup_attachments(conn: duckdb.DuckDBPyConnection, config: Config, verbose: bool) -> None:
    for attachment in config.attachments.duckdb:
        clause = " (READ_ONLY)" if attachment.read_only else ""
        log_info(
            "Attaching DuckDB database",
            alias=attachment.alias,
            path=attachment.path,
            read_only=attachment.read_only,
        )
        conn.execute(
            f"ATTACH DATABASE '{_quote_literal(attachment.path)}' AS \"{attachment.alias}\"{clause}"
        )

    for attachment in config.attachments.sqlite:
        log_info("Attaching SQLite database", alias=attachment.alias, path=attachment.path)
        conn.execute(
            f"ATTACH DATABASE '{_quote_literal(attachment.path)}' AS \"{attachment.alias}\" (TYPE SQLITE)"
        )

    for attachment in config.attachments.postgres:
        log_info(
            "Attaching Postgres database",
            alias=attachment.alias,
            host=attachment.host,
            database=attachment.database,
            user=attachment.user,
        )
        log_debug(
            "Postgres attachment details",
            alias=attachment.alias,
            user=attachment.user,
            password=attachment.password,
            options=attachment.options,
        )
        clauses = [
            "TYPE POSTGRES",
            f"HOST '{_quote_literal(attachment.host)}'",
            f"PORT {attachment.port}",
            f"USER '{_quote_literal(attachment.user)}'",
            f"PASSWORD '{_quote_literal(attachment.password)}'",
            f"DATABASE '{_quote_literal(attachment.database)}'",
        ]
        if attachment.sslmode:
            clauses.append(f"SSLMODE '{_quote_literal(attachment.sslmode)}'")
        for key, value in attachment.options.items():
            clauses.append(f"{key.upper()} '{_quote_literal(str(value))}'")
        clause_sql = ", ".join(clauses)
        conn.execute(
            f"ATTACH DATABASE '{_quote_literal(attachment.database)}' AS \"{attachment.alias}\" ({clause_sql})"
        )


def _setup_iceberg_catalogs(conn: duckdb.DuckDBPyConnection, config: Config, verbose: bool) -> None:
    for catalog in config.iceberg_catalogs:
        log_info("Registering Iceberg catalog", name=catalog.name, catalog_type=catalog.catalog_type)
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


def _create_views(conn: duckdb.DuckDBPyConnection, config: Config, verbose: bool) -> None:
    for view in config.views:
        sql = generate_view_sql(view)
        log_info("Creating or replacing view", name=view.name)
        conn.execute(sql)


__all__ = ["build_catalog", "EngineError"]


def _quote_literal(value: str) -> str:
    return value.replace("'", "''")
