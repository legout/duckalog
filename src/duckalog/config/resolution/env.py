"""Environment processing helpers with request-scoped caching.

This module extracts .env discovery/merging from the legacy loader and exposes
it behind the EnvProcessor protocol for dependency injection.
"""

from __future__ import annotations

import os
import re
import threading
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable, Optional

from dotenv import dotenv_values

from duckalog.errors import ConfigError
from ..validators import log_debug, log_info
from .base import EnvProcessor

# Regular expression pattern for environment variable interpolation
# Supports ${env:VAR} and ${env:VAR:default} syntax
ENV_PATTERN = re.compile(r"\$\{env:([A-Za-z_][A-Za-z0-9_]*)(?::([^}]*))?\}")


def _interpolate_env(value: Any) -> Any:
    """Recursively interpolate ${env:VAR} placeholders in config data.

    Args:
        value: The value to interpolate. Can be a string, list, dict, or other type.

    Returns:
        The interpolated value with environment variables resolved.

    Raises:
        ConfigError: If an environment variable is not set.
    """
    if isinstance(value, str):
        return ENV_PATTERN.sub(_replace_env_match, value)
    if isinstance(value, list):
        return [_interpolate_env(item) for item in value]
    if isinstance(value, dict):
        return {key: _interpolate_env(val) for key, val in value.items()}
    return value


def _replace_env_match(match: re.Match) -> str:
    """Replace environment variable match with its actual value.

    Args:
        match: Regular expression match object containing the variable name
               and optional default value.

    Returns:
        The value of the environment variable, or the default if provided.

    Raises:
        ConfigError: If the environment variable is not set and no default provided.
    """
    var_name = match.group(1)
    default = match.group(2)
    if var_name in os.environ:
        return os.environ[var_name]
    if default is not None:
        return default
    raise ConfigError(f"Environment variable '{var_name}' is not set")


@dataclass
class EnvCache:
    """Cache for loaded .env files to avoid duplicate filesystem access."""

    dotenv_cache: dict[str, tuple[dict[str, str], float]] = field(default_factory=dict)
    _lock: threading.RLock = field(default_factory=threading.RLock)

    def clear(self) -> None:
        with self._lock:
            self.dotenv_cache.clear()


@contextmanager
def env_cache_scope(cache: Optional[EnvCache] = None):
    """Context manager to provide request-scoped env cache."""
    cache = cache or EnvCache()
    try:
        yield cache
    finally:
        cache.clear()


_dotenv_max_depth = 10  # Maximum directory depth for .env file search


def _is_remote_uri(path: str) -> bool:
    try:
        from duckalog.remote_config import is_remote_uri as check_remote_uri

        return check_remote_uri(path)
    except ImportError:
        remote_schemes = [
            "http://",
            "https://",
            "s3://",
            "gcs://",
            "az://",
            "abfs://",
            "sftp://",
        ]
        return any(path.startswith(scheme) for scheme in remote_schemes)


def _find_dotenv_files(
    config_path: str,
    env_file_patterns: Optional[Iterable[str]] = None,
    filesystem: Optional[Any] = None,
) -> list[str]:
    if env_file_patterns is None:
        env_file_patterns = [".env"]
    config_file = Path(config_path)

    if _is_remote_uri(config_path):
        search_dir = Path.cwd()
    else:
        # For custom filesystems, we still want to resolve relative to the config file
        search_dir = config_file.parent

    found_files: list[str] = []
    current_dir = search_dir

    for _ in range(_dotenv_max_depth):
        for pattern in env_file_patterns:
            dotenv_path = current_dir / pattern
            path_str = str(dotenv_path)

            exists = False
            if filesystem is not None:
                try:
                    exists = filesystem.exists(path_str)
                except Exception:
                    pass
            else:
                exists = dotenv_path.exists() and dotenv_path.is_file()

            if exists:
                if filesystem is None:
                    try:
                        dotenv_path.stat()
                    except (OSError, PermissionError):
                        log_debug("Skipping unreadable .env file", path=path_str)
                        continue

                if path_str not in found_files:
                    found_files.append(path_str)

        parent = current_dir.parent
        if parent == current_dir:
            break
        current_dir = parent

    return list(reversed(found_files))


def _validate_dotenv_content(file_path: str, content: str) -> list[str]:
    warnings = []
    lines = content.split("\n")

    for line_num, line in enumerate(lines, 1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if "=" not in stripped:
            warnings.append(f"Line {line_num}: Invalid format (missing '=')")
            continue
        parts = stripped.split("=", 1)
        if len(parts) != 2:
            warnings.append(f"Line {line_num}: Invalid format")
            continue
        key, value = parts
        key = key.strip()
        value = value.strip()
        if not key:
            warnings.append(f"Line {line_num}: Empty key name")
        elif not key.replace("_", "").replace("-", "").isalnum():
            warnings.append(
                f"Line {line_num}: Invalid key name '{key}' (should be alphanumeric, underscore, or hyphen)"
            )
        elif key[0].isdigit():
            warnings.append(f"Line {line_num}: Key '{key}' starts with digit")
        secret_indicators = ["password", "secret", "key", "token", "private"]
        if any(indicator in key.lower() for indicator in secret_indicators):
            if not value:
                warnings.append(f"Line {line_num}: Secret '{key}' has empty value")
        if key.lower() in ["true", "false", "yes", "no"]:
            warnings.append(
                f"Line {line_num}: Key '{key}' looks like a boolean (consider using quotes)"
            )
        if len(value) > 1000:
            warnings.append(
                f"Line {line_num}: Very long value for '{key}' (length: {len(value)})"
            )

    return warnings


def _load_dotenv_file(
    file_path: str, cache: Optional[EnvCache] = None, filesystem: Optional[Any] = None
) -> dict[str, str]:
    cache = cache or EnvCache()
    try:
        if filesystem is None:
            mtime = os.path.getmtime(file_path)
            cache_key = os.path.abspath(file_path)
        else:
            try:
                # Some filesystems have 'info' or 'modified'
                if hasattr(filesystem, "modified"):
                    mtime = filesystem.modified(file_path).timestamp()
                elif hasattr(filesystem, "info"):
                    mtime = filesystem.info(file_path).get("mtime", 0)
                else:
                    mtime = 0
            except Exception:
                mtime = 0
            cache_key = f"{type(filesystem).__name__}:{file_path}"

        with cache._lock:
            if cache_key in cache.dotenv_cache:
                cached_vars, cached_mtime = cache.dotenv_cache[cache_key]
                if cached_mtime == mtime:
                    log_debug(
                        "Using cached .env variables",
                        file_path=file_path,
                        var_count=len(cached_vars),
                    )
                    return cached_vars

        if filesystem is not None:
            with filesystem.open(file_path, "r") as f:
                content = f.read()
            from io import StringIO

            dotenv_vars = dotenv_values(stream=StringIO(content))
        else:
            dotenv_vars = dotenv_values(file_path)
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

        dotenv_vars = {k: v for k, v in dotenv_vars.items() if v is not None}

        warnings = _validate_dotenv_content(file_path, content)
        for warning in warnings:
            log_debug(" .env validation warning", file_path=file_path, warning=warning)

        with cache._lock:
            cache.dotenv_cache[cache_key] = (dotenv_vars, mtime)
        log_debug("Loaded .env file", file_path=file_path, var_count=len(dotenv_vars))
        return dotenv_vars
    except OSError as exc:
        raise ConfigError(f"Failed to read .env file '{file_path}': {exc}") from exc
    except Exception as exc:
        raise ConfigError(f"Failed to parse .env file '{file_path}': {exc}") from exc


def _merge_dotenv_variables(
    dotenv_vars: dict[str, str], system_env_vars: set[str], allow_override: bool = False
) -> None:
    for key, value in dotenv_vars.items():
        if key in system_env_vars:
            continue
        if allow_override or key not in os.environ:
            os.environ[key] = value


def _load_dotenv_files_for_config(
    config_path: str,
    env_file_patterns: Optional[Iterable[str]] = None,
    *,
    cache: Optional[EnvCache] = None,
    filesystem: Optional[Any] = None,
) -> None:
    cache = cache or EnvCache()
    try:
        dotenv_files = _find_dotenv_files(config_path, env_file_patterns, filesystem)

        if not dotenv_files:
            log_debug("No .env files found for config", config_path=config_path)
            return

        log_info(
            "Loading .env files", config_path=config_path, file_count=len(dotenv_files)
        )
        system_env_vars = set(os.environ.keys())

        for dotenv_file in dotenv_files:
            try:
                dotenv_vars = _load_dotenv_file(
                    dotenv_file, cache=cache, filesystem=filesystem
                )
                _merge_dotenv_variables(
                    dotenv_vars, system_env_vars, allow_override=True
                )
                log_debug(
                    "Merged .env variables",
                    file_path=dotenv_file,
                    var_count=len(dotenv_vars),
                )
            except ConfigError as exc:
                log_info(
                    "Failed to load .env file (continuing with other files)",
                    file_path=dotenv_file,
                    error=str(exc),
                )
                # Continue processing other .env files but log at info level
                # to ensure configuration issues are visible to users

        log_info("Completed .env file loading", total_files=len(dotenv_files))

    except Exception as exc:
        log_info(
            "Non-critical error during .env file loading (continuing)",
            config_path=config_path,
            error=str(exc),
        )


class DefaultEnvProcessor(EnvProcessor):
    """EnvProcessor that mirrors legacy loader behavior."""

    def __init__(
        self,
        config_path: str,
        cache: Optional[EnvCache] = None,
        filesystem: Optional[Any] = None,
    ):
        self.config_path = str(config_path)
        self.cache = cache or EnvCache()
        self.filesystem = filesystem

    def process(
        self, config_data: dict[str, Any], load_dotenv: bool = True
    ) -> dict[str, Any]:
        if not load_dotenv:
            return config_data

        env_file_patterns = [".env"]
        try:
            raw_patterns = (
                config_data.get("env_files") if isinstance(config_data, dict) else None
            )
            if isinstance(raw_patterns, Iterable) and not isinstance(
                raw_patterns, (str, bytes)
            ):
                raw_list = list(raw_patterns)
                if raw_list:
                    env_file_patterns = [str(p) for p in raw_list]
        except Exception:
            pass

        _load_dotenv_files_for_config(
            self.config_path,
            env_file_patterns,
            cache=self.cache,
            filesystem=self.filesystem,
        )
        return config_data


__all__ = [
    "DefaultEnvProcessor",
    "EnvCache",
    "env_cache_scope",
    "_find_dotenv_files",
    "_load_dotenv_file",
    "_merge_dotenv_variables",
    "_load_dotenv_files_for_config",
    "_interpolate_env",
]
