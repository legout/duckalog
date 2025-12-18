"""Validation and path resolution utilities for configuration processing.

This module contains complex validation helper functions and path resolution logic
used throughout the configuration system.
"""

import os
import re
from pathlib import Path
from typing import Any, Optional

from loguru import logger
from duckalog.errors import ConfigError, PathResolutionError
from duckalog.config.security.path import (
    DefaultPathResolver,
    DefaultPathValidator,
    detect_path_type as _detect_path_type_core,
    is_relative_path as _is_relative_path_core,
    is_windows_path_absolute as _is_windows_path_absolute_core,
    is_within_allowed_roots as _is_within_allowed_roots_core,
    normalize_path_for_sql as _normalize_path_for_sql_core,
    resolve_relative_path as _resolve_relative_path_core,
    validate_file_accessibility as _validate_file_accessibility_core,
    validate_path_security as _validate_path_security_core,
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


# Dependency-injected path helpers
_path_resolver = DefaultPathResolver(log_debug=log_debug)
_path_validator = DefaultPathValidator(
    path_resolver=_path_resolver, log_debug=log_debug
)

# Path resolution and validation functions


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


def is_relative_path(path: str) -> bool:
    """Detect if a path is relative based on platform-specific rules."""
    return _is_relative_path_core(path)


def resolve_relative_path(path: str, config_dir: Path) -> str:
    """Resolve a relative path to an absolute path relative to config directory."""
    return _resolve_relative_path_core(path, config_dir, log_debug=log_debug)


def validate_path_security(
    path: str, config_dir: Path, allowed_roots: Optional[list[Path]] = None
) -> bool:
    """Validate that resolved paths don't violate security boundaries."""
    return _validate_path_security_core(
        path,
        config_dir,
        allowed_roots=allowed_roots,
        log_debug=log_debug,
    )


def normalize_path_for_sql(path: str) -> str:
    """Normalize a path for use in SQL statements."""
    return _normalize_path_for_sql_core(path)


def is_within_allowed_roots(candidate_path: str, allowed_roots: list[Path]) -> bool:
    """Check if a resolved path is within any of the allowed root directories."""
    return _is_within_allowed_roots_core(candidate_path, allowed_roots)


def is_windows_path_absolute(path: str) -> bool:
    """Check Windows-specific absolute path patterns."""
    return _is_windows_path_absolute_core(path)


def detect_path_type(path: str) -> str:
    """Detect the type of path for categorization."""
    return _detect_path_type_core(path)


def validate_file_accessibility(path: str) -> tuple[bool, Optional[str]]:
    """Validate that a file path is accessible."""
    return _validate_file_accessibility_core(path)


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
