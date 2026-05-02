"""Validation and path resolution utilities for configuration processing.

This module owns config-level path rewriting (resolving relative paths in views
and attachments) and redacted logging.  Path-security primitives live in
``duckalog.config.security.path`` and should be imported directly from there.
"""

from pathlib import Path
from typing import Any

from loguru import logger
from duckalog.errors import ConfigError, PathResolutionError
from duckalog.config.security.path import (
    DefaultPathResolver,
    is_relative_path,
    resolve_relative_path,
    validate_path_security,
)


# Logging and redaction utilities
LOGGER_NAME = "duckalog"
SENSITIVE_KEYWORDS = ("password", "secret", "token", "key", "pwd")


def get_logger(name: str = LOGGER_NAME):
    """Return a logger configured for Duckalog."""
    return logger.bind(name=name)


def _is_sensitive(key: str) -> bool:
    """Check if a key contains sensitive information."""
    lowered = key.lower()
    return any(keyword in lowered for keyword in SENSITIVE_KEYWORDS)


def _redact_value(value: Any, key_hint: str = "") -> Any:
    """Redact sensitive values from log data."""
    if isinstance(value, dict):
        return {k: _redact_value(v, k) for k, v in value.items()}
    if isinstance(value, list):
        return [_redact_value(item, key_hint) for item in value]
    if isinstance(value, str) and _is_sensitive(key_hint):
        return "***REDACTED***"
    return value


def _emit_loguru_logger(
    level_name: str, message: str, safe_details: dict[str, Any]
) -> None:
    """Emit a log message using loguru."""
    if safe_details:
        logger.log(level_name, "{} {}", message, safe_details)
    else:
        logger.log(level_name, message)


def _log(level: int, message: str, **details: Any) -> None:
    """Log a redacted message."""
    safe_details: dict[str, Any] = {}
    if details:
        safe_details = {k: _redact_value(v, k) for k, v in details.items()}

    # Map stdlib logging levels to loguru
    level_map = {
        20: "INFO",  # logging.INFO
        10: "DEBUG",  # logging.DEBUG
        30: "WARNING",  # logging.WARNING
        40: "ERROR",  # logging.ERROR
    }
    level_name = level_map.get(level, "INFO")
    _emit_loguru_logger(level_name, message, safe_details)


def log_info(message: str, **details: Any) -> None:
    """Log a redacted INFO-level message."""
    _log(20, message, **details)


def log_debug(message: str, **details: Any) -> None:
    """Log a redacted DEBUG-level message."""
    _log(10, message, **details)


def log_warning(message: str, **details: Any) -> None:
    """Log a redacted WARNING-level message."""
    _log(30, message, **details)


def log_error(message: str, **details: Any) -> None:
    """Log a redacted ERROR-level message."""
    _log(40, message, **details)


# Internal path resolver for config-level path rewriting
_path_resolver = DefaultPathResolver(log_debug=log_debug)


def _resolve_path_core(path: str, base_dir: Path, check_exists: bool = False) -> Path:
    """Core path resolution logic shared between different path resolution functions.

    Args:
        path: The path to resolve
        base_dir: The base directory to resolve relative paths against
        check_exists: If True, check that the resolved path exists

    Returns:
        Resolved Path object

    Raises:
        ValueError: If path resolution fails
    """
    return _path_resolver._resolve_path_core(path, base_dir, check_exists=check_exists)


def _resolve_paths_in_config(config, config_path: Path):
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
    try:
        # Import Config here to avoid circular imports
        from duckalog.config.models import Config

        config_dict = config.model_dump(mode="python")
        config_dir = config_path.parent

        # Resolve paths in views
        if "views" in config_dict and config_dict["views"]:
            for view_data in config_dict["views"]:
                _resolve_view_paths(view_data, config_dir)

        # Resolve paths in attachments
        if "attachments" in config_dict and config_dict["attachments"]:
            _resolve_attachment_paths(config_dict["attachments"], config_dir)

        # Re-validate the config with resolved paths
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
            # Resolve the path first
            try:
                resolved_uri = resolve_relative_path(original_uri, config_dir)
                # Validate security on the resolved path (more secure)
                if not validate_path_security(resolved_uri, config_dir):
                    raise PathResolutionError(
                        f"Security validation failed for resolved URI '{resolved_uri}'",
                        original_path=original_uri,
                    )
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
