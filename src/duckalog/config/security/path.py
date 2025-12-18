"""Path resolution and validation utilities with dependency injection support.

This module extracts the path security logic from the legacy loader/validator
implementations and exposes it through injectable resolver/validator classes.
"""

from __future__ import annotations

import os
import re
import threading
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Callable, Iterable, Optional, Union

from duckalog.errors import PathResolutionError

from .base import PathResolver, PathValidator

LogFn = Optional[Callable[..., None]]


def _noop_log(*_: Any, **__: Any) -> None:  # pragma: no cover - simple default
    """Default no-op logger to avoid optional checks."""


# Global state for path resolution caching
_path_cache = threading.local()


class PathResolutionCache:
    """Cache for resolved paths to avoid redundant syscalls."""

    def __init__(self) -> None:
        self._cache: dict[tuple[str, str], Path] = {}
        self._resolve_cache: dict[str, Path] = {}
        self.hits = 0
        self.misses = 0

    def get_resolved(self, path: str, base_dir: Path) -> Optional[Path]:
        """Get a resolved path from the cache."""
        key = (path, str(base_dir))
        result = self._cache.get(key)
        if result:
            self.hits += 1
        else:
            self.misses += 1
        return result

    def set_resolved(self, path: str, base_dir: Path, resolved: Path) -> None:
        """Set a resolved path in the cache."""
        key = (path, str(base_dir))
        self._cache[key] = resolved

    def get_path_resolve(self, path_str: str) -> Optional[Path]:
        """Get a Path.resolve() result from the cache."""
        result = self._resolve_cache.get(path_str)
        if result:
            self.hits += 1
        else:
            self.misses += 1
        return result

    def set_path_resolve(self, path_str: str, resolved: Path) -> None:
        """Set a Path.resolve() result in the cache."""
        self._resolve_cache[path_str] = resolved


@contextmanager
def path_resolution_context(cache: Optional[PathResolutionCache] = None):
    """Context manager to enable path resolution caching.

    This should be used during configuration loading operations to
    eliminate redundant path resolution syscalls.

    If a cache is already active, it reuses it instead of creating a new one.
    """
    if not hasattr(_path_cache, "current"):
        _path_cache.current = None

    token = _path_cache.current

    # Use provided cache, or existing active cache, or create new one
    active_cache = cache or token or PathResolutionCache()
    _path_cache.current = active_cache

    try:
        yield _path_cache.current
    finally:
        _path_cache.current = token


def get_current_path_cache() -> Optional[PathResolutionCache]:
    """Get the current path resolution cache if one is active."""
    return getattr(_path_cache, "current", None)


class DefaultPathResolver(PathResolver):
    """PathResolver that applies the existing security rules."""

    def __init__(self, log_debug: LogFn = None) -> None:
        self._log_debug = log_debug or _noop_log

    def _resolve_path_core(
        self, path: str, base_dir: Path, check_exists: bool = False
    ) -> Path:
        """Core path resolution logic shared by helpers."""
        if not path or not path.strip():
            raise ValueError("Path cannot be empty")

        path = path.strip()

        # Check cache if available
        cache = get_current_path_cache()
        if cache:
            cached_result = cache.get_resolved(path, base_dir)
            if cached_result:
                if check_exists and not cached_result.exists():
                    raise ValueError(f"Resolved path does not exist: {cached_result}")
                return cached_result

        # If path is already absolute, return as-is
        if not is_relative_path(path):
            # For remote URIs, return the original string to avoid path normalization
            if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*://", path):
                res = Path(path)
            else:
                res = Path(path)

            if cache:
                cache.set_resolved(path, base_dir, res)
            return res

        # Resolve relative path against base directory
        try:
            if cache:
                base_dir_resolved = cache.get_path_resolve(str(base_dir))
                if not base_dir_resolved:
                    base_dir_resolved = base_dir.resolve()
                    cache.set_path_resolve(str(base_dir), base_dir_resolved)

                resolved_path = (base_dir_resolved / path).resolve()
            else:
                base_dir_resolved = base_dir.resolve()
                resolved_path = (base_dir_resolved / path).resolve()

            if check_exists and not resolved_path.exists():
                raise ValueError(f"Resolved path does not exist: {resolved_path}")

            if cache:
                cache.set_resolved(path, base_dir, resolved_path)

            return resolved_path

        except (OSError, ValueError) as exc:
            raise ValueError(
                f"Failed to resolve path '{path}' relative to '{base_dir}': {exc}"
            ) from exc

    def resolve(
        self,
        path: str,
        base_path: Optional[Union[str, Path]] = None,
        check_exists: bool = False,
    ) -> str:
        base_dir = Path(base_path) if base_path is not None else Path.cwd()
        resolved = self._resolve_path_core(path, base_dir, check_exists=check_exists)
        self._log_debug(
            "Resolved path",
            original=path,
            resolved=str(resolved),
            base_dir=str(base_dir),
            check_exists=check_exists,
        )
        return str(resolved)


class DefaultPathValidator(PathValidator):
    """Validator that enforces allowed-root boundaries."""

    def __init__(
        self,
        path_resolver: Optional[DefaultPathResolver] = None,
        allowed_roots: Optional[Iterable[Union[str, Path]]] = None,
        log_debug: LogFn = None,
    ) -> None:
        self._resolver = path_resolver or DefaultPathResolver(log_debug=log_debug)
        self._allowed_roots = (
            [Path(p) for p in allowed_roots] if allowed_roots else None
        )
        self._log_debug = log_debug or _noop_log

    def validate(self, path: Union[str, Path]) -> None:
        base_dir = None
        if isinstance(path, Path):
            base_dir = path.parent
        if self._allowed_roots:
            base_dir = self._allowed_roots[0]

        if not validate_path_security(
            str(path), base_dir or Path.cwd(), allowed_roots=self._allowed_roots
        ):
            raise PathResolutionError(
                f"Path '{path}' is outside allowed roots",
                original_path=str(path),
            )
        self._log_debug("Path validated", path=str(path))


def is_relative_path(path: str) -> bool:
    """Detect if a path is relative based on platform rules."""
    if not path or not path.strip():
        return False

    # Check for protocols (http, s3, gs, https, etc.)
    if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*://", path):
        return False

    # Platform-specific checks
    try:
        if Path(path).is_absolute():
            return False
    except (OSError, ValueError):
        pass

    # Windows drive letter check (C:, D:, etc.)
    if re.match(r"^[a-zA-Z]:[\\/]|^[a-zA-Z]:$", path):
        return False

    # Windows UNC path check (\\server\share)
    if path.startswith("\\\\"):
        return False

    return True


def resolve_relative_path(
    path: str, config_dir: Path, *, log_debug: LogFn = None
) -> str:
    """Resolve a relative path to absolute using config directory."""
    if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*://", path):
        if log_debug:
            log_debug(
                "Skipping path resolution for remote URI",
                path=path,
                config_dir=str(config_dir),
            )
        return path

    resolver = DefaultPathResolver(log_debug=log_debug)
    resolved_path = resolver._resolve_path_core(path, config_dir, check_exists=False)

    if log_debug:
        log_debug(
            "Resolved relative path",
            original=path,
            resolved=str(resolved_path),
            config_dir=str(config_dir),
        )

    return str(resolved_path)


def is_within_allowed_roots(candidate_path: str, allowed_roots: list[Path]) -> bool:
    """Check if a resolved path is within allowed roots."""
    cache = get_current_path_cache()

    try:
        if cache:
            resolved_candidate = cache.get_path_resolve(candidate_path)
            if not resolved_candidate:
                resolved_candidate = Path(candidate_path).resolve()
                cache.set_path_resolve(candidate_path, resolved_candidate)
        else:
            resolved_candidate = Path(candidate_path).resolve()
    except (OSError, ValueError, RuntimeError) as exc:
        raise ValueError(f"Cannot resolve path '{candidate_path}': {exc}") from exc

    try:
        resolved_roots = []
        for root in allowed_roots:
            if cache:
                root_str = str(root)
                res_root = cache.get_path_resolve(root_str)
                if not res_root:
                    res_root = root.resolve()
                    cache.set_path_resolve(root_str, res_root)
                resolved_roots.append(res_root)
            else:
                resolved_roots.append(root.resolve())
    except (OSError, ValueError, RuntimeError) as exc:
        raise ValueError(f"Cannot resolve allowed root: {exc}") from exc

    for root in resolved_roots:
        try:
            common = Path(os.path.commonpath([resolved_candidate, root]))
            if common == root:
                return True
        except ValueError:
            continue
    return False


def validate_path_security(
    path: str,
    config_dir: Path,
    *,
    allowed_roots: Optional[Iterable[Union[str, Path]]] = None,
    log_debug: LogFn = None,
) -> bool:
    """Validate that resolved paths don't violate security boundaries."""
    if not path or not path.strip():
        return False

    if not is_relative_path(path):
        if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*://", path):
            return True

    cache = get_current_path_cache()

    try:
        if is_relative_path(path):
            config_dir_res = None
            if cache:
                config_dir_res = cache.get_path_resolve(str(config_dir))

            if not config_dir_res:
                config_dir_res = config_dir.resolve()
                if cache:
                    cache.set_path_resolve(str(config_dir), config_dir_res)

            resolved_path_str = resolve_relative_path(
                path, config_dir_res, log_debug=log_debug
            )
            resolved_path = Path(resolved_path_str)
        else:
            if cache:
                resolved_path = cache.get_path_resolve(path)
                if not resolved_path:
                    resolved_path = Path(path).resolve()
                    cache.set_path_resolve(path, resolved_path)
            else:
                resolved_path = Path(path).resolve()

        if cache:
            config_dir_resolved = cache.get_path_resolve(str(config_dir))
            if not config_dir_resolved:
                config_dir_resolved = config_dir.resolve()
                cache.set_path_resolve(str(config_dir), config_dir_resolved)
        else:
            config_dir_resolved = config_dir.resolve()

        roots = (
            [Path(r) for r in allowed_roots] if allowed_roots else [config_dir_resolved]
        )
        try:
            if is_within_allowed_roots(str(resolved_path), roots):
                return True
            if log_debug:
                log_debug(
                    "Path resolution security violation",
                    resolved_path=str(resolved_path),
                    allowed_roots=[str(r) for r in roots],
                )
            return False
        except ValueError as exc:
            if log_debug:
                log_debug(
                    "Path resolution validation failed",
                    path=path,
                    resolved_path=str(resolved_path),
                    error=str(exc),
                )
            return False
    except (OSError, ValueError, RuntimeError):
        return False


def normalize_path_for_sql(path: str) -> str:
    """Normalize a path for safe use in SQL statements."""
    if not path or not path.strip():
        raise ValueError("Path cannot be empty")

    path = path.strip()

    try:
        path_obj = Path(path)
        normalized = str(path_obj)
    except (OSError, ValueError):
        normalized = path

    from duckalog.sql_utils import quote_literal

    return quote_literal(normalized)


def is_windows_path_absolute(path: str) -> bool:
    """Check Windows-specific absolute path patterns."""
    if re.match(r"^[a-zA-Z]:[\\/]|^[a-zA-Z]:$", path):
        return True
    if path.startswith("\\\\"):
        return True
    return False


def detect_path_type(path: str) -> str:
    """Detect whether a path is relative, absolute, or remote."""
    if not path or not path.strip():
        return "invalid"

    if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*://", path):
        return "remote"

    if not is_relative_path(path):
        return "absolute"

    return "relative"


def validate_file_accessibility(path: str) -> tuple[bool, Optional[str]]:
    """Validate that a file path is accessible."""
    if not path or not path.strip():
        return False, "Path cannot be empty"

    try:
        path_obj = Path(path)

        if not path_obj.exists():
            return False, f"File does not exist: {path}"

        if not path_obj.is_file():
            return False, f"Path is not a file: {path}"

        try:
            with open(path_obj, "rb"):
                pass
        except PermissionError:
            return False, f"Permission denied reading file: {path}"
        except OSError as exc:
            return False, f"Error accessing file {path}: {exc}"

        return True, None

    except (OSError, ValueError) as exc:
        return False, f"Invalid path: {exc}"


__all__ = [
    "DefaultPathResolver",
    "DefaultPathValidator",
    "is_relative_path",
    "resolve_relative_path",
    "validate_path_security",
    "normalize_path_for_sql",
    "is_within_allowed_roots",
    "is_windows_path_absolute",
    "detect_path_type",
    "validate_file_accessibility",
    "path_resolution_context",
]
