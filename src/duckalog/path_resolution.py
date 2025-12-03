"""Path resolution utilities for Duckalog configuration files.

This module provides functions to detect, resolve, and validate relative paths
in configuration files, ensuring consistent behavior across different working
directories while maintaining security and cross-platform compatibility.

The main functions are:
- is_relative_path(): Detect if a path is relative
- resolve_relative_path(): Resolve relative paths to absolute paths
- validate_path_security(): Validate paths for security concerns
"""

from __future__ import annotations

import os
import re
from pathlib import Path

from .logging_utils import log_debug


def is_relative_path(path: str) -> bool:
    """Detect if a path is relative based on platform-specific rules.

    A path is considered relative if it:
    - Does not start with a protocol (http://, s3://, etc.)
    - Does not start with / on Unix systems
    - Does not start with a drive letter on Windows (C:, D:, etc.)
    - Is not already absolute according to pathlib

    Args:
        path: The path string to check

    Returns:
        True if the path is relative, False otherwise

    Examples:
        >>> is_relative_path("data/file.parquet")
        True
        >>> is_relative_path("/absolute/path/file.parquet")
        False
        >>> is_relative_path("C:\\data\\file.parquet")
        False
        >>> is_relative_path("s3://bucket/file.parquet")
        False
    """
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
        # Path might contain invalid characters for the current platform
        pass

    # Windows drive letter check (C:, D:, etc.)
    if re.match(r"^[a-zA-Z]:[\\\\/]", path):
        return False

    # Windows UNC path check (\\server\share)
    if path.startswith("\\\\"):
        return False

    return True


def resolve_relative_path(path: str, config_dir: Path) -> str:
    """Resolve a relative path to an absolute path relative to config directory.

    Args:
        path: The path to resolve (can be relative or absolute)
        config_dir: The directory containing the configuration file

    Returns:
        The resolved absolute path as a string

    Raises:
        ValueError: If the path resolution fails or violates security rules

    Examples:
        >>> resolve_relative_path("data/file.parquet", Path("/project/config"))
        '/project/config/data/file.parquet'
    """
    if not path or not path.strip():
        raise ValueError("Path cannot be empty")

    path = path.strip()

    # If path is already absolute, return as-is
    if not is_relative_path(path):
        return path

    # Resolve relative path against config directory
    try:
        config_dir = config_dir.resolve()
        resolved_path = config_dir / path
        resolved_path = resolved_path.resolve()

        log_debug(
            f"Resolved relative path: {path} -> {resolved_path}",
            config_dir=str(config_dir),
        )

        # Validate that the resolved path is within allowed roots
        if not is_within_allowed_roots(str(resolved_path), [config_dir]):
            raise ValueError(
                f"Path resolution violates security rules: '{path}' resolves to '{resolved_path}' "
                f"which is outside the allowed root '{config_dir}'. "
                f"All paths must remain within the configuration directory or its subdirectories."
            )

        return str(resolved_path)

    except (OSError, ValueError) as exc:
        raise ValueError(
            f"Failed to resolve path '{path}' relative to '{config_dir}': {exc}"
        ) from exc


def validate_path_security(path: str, config_dir: Path) -> bool:
    """Validate that resolved paths don't violate security boundaries.

    This function prevents directory traversal attacks by ensuring that
    resolved paths stay within the configuration file's directory tree.
    Remote URIs are considered safe and are not validated.

    Args:
        path: The path to validate (will be resolved if relative)
        config_dir: The directory containing the configuration file

    Returns:
        True if the path is safe, False otherwise

    Examples:
        >>> validate_path_security("data/file.parquet", Path("/project/config"))
        True
        >>> validate_path_security("../../../etc/passwd", Path("/project/config"))
        False
    """
    if not path or not path.strip():
        return False

    # Remote URIs are considered safe
    if not is_relative_path(path):
        # Check if it's a remote URI (has protocol)
        import re

        if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*://", path):
            return True

    try:
        # Resolve relative paths only
        if is_relative_path(path):
            resolved_path_str = resolve_relative_path(path, config_dir.resolve())
            resolved_path = Path(resolved_path_str)
        else:
            # For non-relative local paths, validate them
            resolved_path = Path(path).resolve()

        config_dir_resolved = config_dir.resolve()

        # Check if resolved path is within allowed roots using the new root-based validation
        try:
            if is_within_allowed_roots(str(resolved_path), [config_dir_resolved]):
                return True
            else:
                log_debug(
                    f"Path resolution security violation: {resolved_path} is outside allowed root {config_dir_resolved}"
                )
                return False
        except ValueError as exc:
            # Path resolution failed (invalid path)
            log_debug(
                f"Path resolution validation failed: {exc}",
                path=path,
                resolved_path=str(resolved_path),
            )
            return False

    except (OSError, ValueError, RuntimeError):
        return False


def is_windows_path_absolute(path: str) -> bool:
    """Check Windows-specific absolute path patterns.

    Args:
        path: The path string to check

    Returns:
        True if the path is absolute on Windows, False otherwise
    """
    # Drive letter: C:\path
    if re.match(r"^[a-zA-Z]:[\\\\/]", path):
        return True

    # UNC path: \\server\share
    if path.startswith("\\\\"):
        return True

    return False


def normalize_path_for_sql(path: str) -> str:
    """Normalize a path for use in SQL statements.

    This function ensures that paths are properly formatted for DuckDB SQL,
    handling path separator normalization and delegating quoting to the
    canonical quote_literal function.

    Args:
        path: The absolute path to normalize

    Returns:
        The normalized path suitable for SQL

    Examples:
        >>> normalize_path_for_sql("/path/to/file.parquet")
        "'/path/to/file.parquet'"
        >>> normalize_path_for_sql("C:\\path\\to\\file.parquet")
        "'C:\\path\\to\\file.parquet'"
    """
    if not path or not path.strip():
        raise ValueError("Path cannot be empty")

    path = path.strip()

    # Convert to Path object for normalization
    try:
        path_obj = Path(path)
        normalized = str(path_obj)
    except (OSError, ValueError):
        # If pathlib can't handle it, use as-is
        normalized = path

    # Import quote_literal from sql_generation to avoid circular imports
    from .sql_generation import quote_literal

    return quote_literal(normalized)


def is_within_allowed_roots(candidate_path: str, allowed_roots: list[Path]) -> bool:
    """Check if a resolved path is within any of the allowed root directories.

    This function implements the root-based path security model that replaces
    heuristic-based traversal checks. It uses Path.resolve() and os.path.commonpath
    for robust cross-platform validation.

    Args:
        candidate_path: The path to check (will be resolved to absolute)
        allowed_roots: List of Path objects representing allowed root directories

    Returns:
        True if the candidate path is within at least one allowed root, False otherwise

    Raises:
        ValueError: If the candidate path cannot be resolved (invalid path)
    """
    try:
        # Resolve the candidate path to absolute, following symlinks
        resolved_candidate = Path(candidate_path).resolve()
    except (OSError, ValueError, RuntimeError) as exc:
        raise ValueError(f"Cannot resolve path '{candidate_path}': {exc}") from exc

    # Resolve all allowed roots to absolute paths
    try:
        resolved_roots = [root.resolve() for root in allowed_roots]
    except (OSError, ValueError, RuntimeError) as exc:
        raise ValueError(f"Cannot resolve allowed root: {exc}") from exc

    # Check if candidate is within any allowed root
    for root in resolved_roots:
        try:
            # Use commonpath to find the common prefix
            common = Path(os.path.commonpath([resolved_candidate, root]))

            # If the common path equals the root, then candidate is within this root
            if common == root:
                return True

        except ValueError:
            # os.path.commonpath raises ValueError when paths are on different
            # drives (Windows) or have no common prefix - treat as not within root
            continue

    return False


def _is_reasonable_parent_traversal(
    original_path: str, resolved_path: str, config_dir: Path
) -> bool:
    """DEPRECATED: Use is_within_allowed_roots() instead.

    This function is kept for backward compatibility but is replaced by
    the more robust root-based validation approach in is_within_allowed_roots().

    Args:
        original_path: The original relative path string
        resolved_path: The resolved absolute path
        config_dir: The configuration directory

    Returns:
        True if the traversal is reasonable, False if excessive/dangerous
    """
    import warnings

    warnings.warn(
        "_is_reasonable_parent_traversal is deprecated and will be removed in a future version. "
        "Use is_within_allowed_roots() instead for more robust root-based path validation.",
        DeprecationWarning,
        stacklevel=2,
    )

    # Count the number of parent directory traversals (../)
    parent_traversal_count = original_path.count("../")

    # Allow up to 3 levels of parent traversal (reasonable for most project structures)
    # This covers cases like ../data/, ../../shared/, etc.
    max_allowed_traversal = 3

    if parent_traversal_count > max_allowed_traversal:
        log_debug(
            f"Excessive parent traversal blocked: {parent_traversal_count} levels in '{original_path}'",
            resolved_path=resolved_path,
            config_dir=str(config_dir),
        )
        return False

    # Additional check: ensure the resolved path doesn't go to obviously dangerous locations
    dangerous_patterns = [
        "/etc/",
        "/usr/",
        "/bin/",
        "/sbin/",
        "/var/log/",
        "/sys/",
        "/proc/",
    ]

    resolved_lower = resolved_path.lower()
    for pattern in dangerous_patterns:
        if pattern in resolved_lower:
            log_debug(
                f"Dangerous path pattern blocked: '{pattern}' in resolved path",
                original_path=original_path,
                resolved_path=resolved_path,
            )
            return False

    return True


def detect_path_type(path: str) -> str:
    """Detect the type of path for categorization.

    Args:
        path: The path string to analyze

    Returns:
        One of: 'relative', 'absolute', 'remote', 'invalid'
    """
    if not path or not path.strip():
        return "invalid"

    # Check for remote URIs with protocols
    if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*://", path):
        return "remote"

    # Check for absolute paths
    if not is_relative_path(path):
        return "absolute"

    # Otherwise it's relative
    return "relative"


def validate_file_accessibility(path: str) -> tuple[bool, str | None]:
    """Validate that a file path is accessible.

    Args:
        path: The file path to validate

    Returns:
        Tuple of (is_accessible, error_message)
    """
    if not path or not path.strip():
        return False, "Path cannot be empty"

    try:
        path_obj = Path(path)

        # Check if file exists
        if not path_obj.exists():
            return False, f"File does not exist: {path}"

        # Check if it's a file (not a directory)
        if not path_obj.is_file():
            return False, f"Path is not a file: {path}"

        # Check if file is readable
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
