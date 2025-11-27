"""Duckalog catalog build engine."""

from __future__ import annotations

import logging
import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

import duckdb

from .config import Config, load_config
from .logging_utils import get_logger, log_debug, log_info
from .path_resolution import is_relative_path, resolve_relative_path
from .sql_generation import generate_all_views_sql, generate_view_sql

# Optional imports for remote export functionality
try:
    import fsspec
    from urllib.parse import urlparse

    FSSPEC_AVAILABLE = True
except ImportError:
    fsspec = None  # type: ignore
    urlparse = None  # type: ignore
    FSSPEC_AVAILABLE = False

logger = get_logger()

# Supported remote export URI schemes for catalog export
REMOTE_EXPORT_SCHEMES = {
    "s3://": "Amazon S3",
    "gs://": "Google Cloud Storage",
    "gcs://": "Google Cloud Storage",
    "abfs://": "Azure Blob Storage",
    "adl://": "Azure Data Lake Storage",
    "sftp://": "SFTP Server",
}


@dataclass
class BuildResult:
    """Result of building a Duckalog config."""
    database_path: str
    config_path: str
    was_built: bool  # True if newly built, False if cached


class ConfigDependencyGraph:
    """Manages Duckalog config dependencies and detects cycles."""

    def __init__(self):
        self.visiting: Set[str] = set()
        self.visited: Set[str] = set()
        self.build_cache: Dict[str, BuildResult] = {}

    def build_config_with_dependencies(
        self,
        config_path: str,
        dry_run: bool = False,
        parent_alias: Optional[str] = None,
        database_override: Optional[str] = None
    ) -> BuildResult:
        """Build config with all its dependencies recursively."""
        config_path = str(Path(config_path).resolve())

        # Check cache first
        if config_path in self.build_cache:
            cached_result = self.build_cache[config_path]
            log_debug(
                "Using cached build result",
                config_path=config_path,
                database_path=cached_result.database_path,
            )
            return cached_result

        # Detect cycles
        if config_path in self.visiting:
            cycle_path = " -> ".join(self.visiting) + f" -> {config_path}"
            raise EngineError(f"Cyclic attachment detected: {cycle_path}")

        self.visiting.add(config_path)

        try:
            # Load the child config
            child_config = load_config(config_path)

            # Validate that child config has a durable database
            child_db_path = child_config.duckdb.database
            if child_db_path == ":memory:":
                if parent_alias:
                    raise EngineError(
                        f"Child config '{config_path}' uses in-memory database. "
                        f"Child configs must use persistent database paths for attachments. "
                        f"Found in attachment '{parent_alias}'."
                    )
                else:
                    raise EngineError(
                        f"Child config '{config_path}' uses in-memory database. "
                        "Child configs must use persistent database paths for attachments."
                    )

            # Apply database override from parent if provided
            effective_db_path = child_db_path
            if database_override:
                effective_db_path = database_override
                log_info(
                    "Using database override for child config",
                    config_path=config_path,
                    original_path=child_db_path,
                    override_path=effective_db_path
                )
            else:
                # Resolve child's database path relative to child config directory
                if is_relative_path(effective_db_path):
                    child_config_dir = Path(config_path).parent
                    effective_db_path = str(child_config_dir / effective_db_path)
                    log_debug(
                        "Resolved child database path",
                        config_path=config_path,
                        original_db=child_db_path,
                        resolved_db=effective_db_path
                    )

            # Recursively build nested Duckalog attachments
            nested_results = {}
            for duckalog_attachment in child_config.attachments.duckalog:
                nested_config_path = duckalog_attachment.config_path
                log_info(
                    "Building nested Duckalog attachment",
                    parent_config=config_path,
                    child_config=nested_config_path,
                    alias=duckalog_attachment.alias,
                )

                nested_result = self.build_config_with_dependencies(
                    nested_config_path, dry_run, duckalog_attachment.alias
                )
                nested_results[duckalog_attachment.alias] = nested_result

            # Handle building the database
            if dry_run:
                # In dry run, we just return the theoretical result
                result = BuildResult(
                    database_path=effective_db_path,
                    config_path=config_path,
                    was_built=True
                )
            else:
                # Actually build the database (for both parent and child configs)
                target_db = effective_db_path
                if not Path(target_db).parent.exists():
                    Path(target_db).parent.mkdir(parents=True, exist_ok=True)

                log_info(
                    "Building child catalog",
                    config_path=config_path,
                    database_path=target_db,
                )

                # Create child connection and setup
                child_conn = duckdb.connect(target_db)
                try:
                    _apply_duckdb_settings(child_conn, child_config, False)
                    _setup_attachments(child_conn, child_config, False)

                    # Setup nested Duckalog attachments that were built during dependency resolution
                    for duckalog_attachment in child_config.attachments.duckalog:
                        if duckalog_attachment.alias in nested_results:
                            nested_result = nested_results[duckalog_attachment.alias]

                            clause = " (READ_ONLY)" if duckalog_attachment.read_only else ""
                            log_info(
                                "Attaching built DuckDB child catalog",
                                alias=duckalog_attachment.alias,
                                database_path=nested_result.database_path,
                                read_only=duckalog_attachment.read_only,
                            )
                            child_conn.execute(
                                f"ATTACH DATABASE '{_quote_literal(nested_result.database_path)}' "
                                f"AS \"{duckalog_attachment.alias}\"{clause}"
                            )

                    _setup_iceberg_catalogs(child_conn, child_config, False)
                    _create_views(child_conn, child_config, False)
                finally:
                    child_conn.close()

                result = BuildResult(
                    database_path=effective_db_path,
                    config_path=config_path,
                    was_built=True
                )

            self.build_cache[config_path] = result
            return result

        finally:
            self.visiting.remove(config_path)
            self.visited.add(config_path)


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
    filesystem: Optional[Any] = None,
) -> Optional[str]:
    """Build or update a DuckDB catalog from a configuration file.

    This function is the high-level entry point used by both the CLI and
    Python API. It loads the config, optionally performs a dry-run SQL
    generation, or otherwise connects to DuckDB, sets up attachments and
    Iceberg catalogs, and creates or replaces configured views.

    Args:
        config_path: Path to the YAML/JSON configuration file.
        db_path: Optional override for ``duckdb.database`` in the config.
            Can be a local path or remote URI (s3://, gs://, gcs://, abfs://, adl://, sftp://).
        dry_run: If ``True``, do not connect to DuckDB; instead generate and
            return the full SQL script for all views.
        verbose: If ``True``, enable more verbose logging via the standard
            logging module.
        filesystem: Optional pre-configured fsspec filesystem object for remote export
            authentication. If not provided, default authentication will be used.

    Returns:
        The generated SQL script as a string when ``dry_run`` is ``True``,
        otherwise ``None`` when the catalog is applied to DuckDB.

    Raises:
        ConfigError: If the configuration file is invalid.
        EngineError: If connecting to DuckDB or executing SQL fails, or if remote export fails.

    Example:
        Build a catalog in-place::

            from duckalog import build_catalog

            build_catalog("catalog.yaml")

        Build and export to remote storage::

            build_catalog("catalog.yaml", db_path="s3://my-bucket/catalog.duckdb")

        Generate SQL without modifying the database::

            sql = build_catalog("catalog.yaml", dry_run=True)
            print(sql)
    """

    if verbose:
        logging.getLogger("duckalog").setLevel(logging.INFO)

    config = load_config(config_path)

    if dry_run:
        # Validate Duckalog attachments in dry run mode
        if config.attachments.duckalog:
            dependency_graph = ConfigDependencyGraph()
            for duckalog_attachment in config.attachments.duckalog:
                try:
                    dependency_graph.build_config_with_dependencies(
                        duckalog_attachment.config_path, dry_run=True
                    )
                except EngineError as exc:
                    raise EngineError(
                        f"Dry run validation failed for Duckalog attachment "
                        f"'{duckalog_attachment.alias}': {exc}"
                    ) from exc

        sql = generate_all_views_sql(config)
        log_info("Dry run SQL generation complete", views=len(config.views))
        return sql

    target_db = _resolve_db_path(config, db_path)

    # Handle remote export: create temp file locally, then upload
    remote_uri = None
    temp_file = None

    if is_remote_export_uri(target_db):
        if not FSSPEC_AVAILABLE:
            raise EngineError(
                "Remote export requires fsspec. Install with: pip install duckalog[remote]"
            )
        remote_uri = target_db
        # Create temporary file for local database creation
        temp_file = tempfile.NamedTemporaryFile(suffix='.duckdb', delete=False)
        temp_file.close()
        target_db = temp_file.name
        log_info("Building catalog locally for remote export", temp_file=target_db, remote_uri=remote_uri)

    # Handle Duckalog attachments separately from regular attachments
    dependency_graph = ConfigDependencyGraph()
    duckalog_results = {}

    if config.attachments.duckalog:
        log_info(
            "Building Duckalog attachment dependencies",
            count=len(config.attachments.duckalog)
        )

        for duckalog_attachment in config.attachments.duckalog:
            try:
                # Resolve database override path if provided
                database_override = None
                if duckalog_attachment.database:
                    database_override = duckalog_attachment.database
                    if is_relative_path(database_override):
                        # Resolve override path relative to parent config directory
                        parent_config_dir = Path(config_path).parent
                        try:
                            database_override = resolve_relative_path(database_override, parent_config_dir)
                        except Exception as exc:
                            raise EngineError(
                                f"Failed to resolve database override '{duckalog_attachment.database}' "
                                f"for attachment '{duckalog_attachment.alias}': {exc}"
                            ) from exc

                result = dependency_graph.build_config_with_dependencies(
                    duckalog_attachment.config_path, dry_run, duckalog_attachment.alias, database_override
                )
                duckalog_results[duckalog_attachment.alias] = result

            except EngineError as exc:
                raise EngineError(
                    f"Failed to build Duckalog attachment '{duckalog_attachment.alias}' "
                    f"from '{duckalog_attachment.config_path}': {exc}"
                ) from exc

    log_info("Connecting to DuckDB", db_path=target_db)
    conn = None
    try:
        conn = duckdb.connect(target_db)
    except Exception as exc:  # pragma: no cover - duckdb handles errors
        # Clean up temp file on connection failure
        if temp_file:
            try:
                Path(temp_file.name).unlink()
            except Exception:
                pass  # Best effort cleanup
        raise EngineError(f"Failed to connect to DuckDB at {target_db}: {exc}") from exc

    try:
        _apply_duckdb_settings(conn, config, verbose)

        # Setup regular attachments (DuckDB, SQLite, Postgres)
        if config.attachments.duckdb or config.attachments.sqlite or config.attachments.postgres:
            _setup_attachments(conn, config, verbose)

        # Setup built Duckalog attachments
        if duckalog_results:
            log_info("Attaching built Duckalog catalogs", count=len(duckalog_results))
            for duckalog_attachment in config.attachments.duckalog:
                if duckalog_attachment.alias in duckalog_results:
                    result = duckalog_results[duckalog_attachment.alias]
                    clause = " (READ_ONLY)" if duckalog_attachment.read_only else ""
                    log_info(
                        "Attaching Duckalog child catalog",
                        alias=duckalog_attachment.alias,
                        database_path=result.database_path,
                        read_only=duckalog_attachment.read_only,
                    )
                    attach_command = (
                        f"ATTACH DATABASE '{_quote_literal(result.database_path)}' "
                        f"AS \"{duckalog_attachment.alias}\"{clause}"
                    )
                    log_debug("Executing attach command", command=attach_command)
                    conn.execute(attach_command)
                    log_debug("Attach command completed successfully")

                    # Verify the attachment actually worked
                    databases = conn.execute("PRAGMA database_list").fetchall()
                    attached_aliases = [row[1] for row in databases]
                    if duckalog_attachment.alias not in attached_aliases:
                        raise EngineError(
                            f"Failed to attach Duckalog catalog '{duckalog_attachment.alias}'. "
                            f"Expected alias not found in attached databases: {attached_aliases}"
                        )
                    log_debug("Attachment verified", alias=duckalog_attachment.alias, attached_databases=attached_aliases)

        _setup_iceberg_catalogs(conn, config, verbose)
        _create_views(conn, config, verbose)
    except EngineError:
        conn.close()
        # Clean up temp file on engine error
        if temp_file:
            try:
                Path(temp_file.name).unlink()
            except Exception:
                pass  # Best effort cleanup
        raise
    except Exception as exc:  # pragma: no cover - wrapped for clarity
        conn.close()
        # Clean up temp file on unexpected error
        if temp_file:
            try:
                Path(temp_file.name).unlink()
            except Exception:
                pass  # Best effort cleanup
        raise EngineError(f"DuckDB execution failed: {exc}") from exc

    conn.close()

    # Upload to remote storage if needed
    if remote_uri:
        try:
            _upload_to_remote(Path(temp_file.name), remote_uri, filesystem)
            log_info("Remote export complete", remote_uri=remote_uri)
        finally:
            # Always clean up temp file
            try:
                Path(temp_file.name).unlink()
            except Exception:
                pass  # Best effort cleanup
    else:
        log_info("Catalog build complete", db_path=target_db)

    return None


def is_remote_export_uri(path: str) -> bool:
    """Check if a path is a remote export URI that requires upload.

    Args:
        path: The path to check

    Returns:
        True if the path is a remote export URI, False otherwise
    """
    if not path or not FSSPEC_AVAILABLE:
        return False

    return any(path.startswith(scheme) for scheme in REMOTE_EXPORT_SCHEMES)


def _upload_to_remote(local_file: Path, remote_uri: str, filesystem=None) -> None:
    """Upload local database file to remote storage using fsspec.

    Args:
        local_file: Path to the local database file to upload
        remote_uri: Remote URI to upload to (e.g., s3://bucket/catalog.duckdb)
        filesystem: Optional pre-configured fsspec filesystem object

    Raises:
        EngineError: If upload fails due to missing dependencies, auth, or network issues
    """
    if not FSSPEC_AVAILABLE:
        raise EngineError(
            "Remote export requires fsspec. Install with: pip install duckalog[remote]"
        )

    try:
        # Use provided filesystem or create one from the URI
        if filesystem is None:
            # Extract protocol from URI for filesystem creation
            parsed = urlparse(remote_uri)
            protocol = parsed.scheme

            # Create filesystem with default authentication
            filesystem = fsspec.filesystem(protocol)

        log_info("Uploading catalog to remote storage", remote_uri=remote_uri)

        # Stream upload to minimize memory usage
        with open(local_file, 'rb') as local_f:
            with filesystem.open(remote_uri, 'wb') as remote_f:
                shutil.copyfileobj(local_f, remote_f)

        log_info("Upload complete", remote_uri=remote_uri)

    except Exception as exc:
        raise EngineError(f"Failed to upload catalog to {remote_uri}: {exc}") from exc


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


__all__ = ["build_catalog", "EngineError", "is_remote_export_uri"]


def _quote_literal(value: str) -> str:
    return value.replace("'", "''")
