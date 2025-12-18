"""Shared SQL utility functions for Duckalog.

This module provides common SQL utilities that are used across multiple
components of Duckalog for consistent SQL generation and manipulation.
"""

from __future__ import annotations

from typing import Any


def quote_ident(value: str) -> str:
    """Quote a SQL identifier using double quotes.

    This helper wraps a string in double quotes and escapes any embedded
    double quotes according to SQL rules.

    Args:
        value: Identifier to quote (for example, a view or column name).

    Returns:
        The identifier wrapped in double quotes.

    Example:
        >>> quote_ident("events")
        '"events"'
    """

    escaped = value.replace('"', '""')
    return f'"{escaped}"'


def quote_literal(value: str) -> str:
    """Quote a SQL string literal using single quotes.

    This helper wraps a string in single quotes and escapes any embedded
    single quotes according to SQL rules.

    Args:
        value: String literal to quote (for example, a file path, secret, or connection string).

    Returns:
        The string wrapped in single quotes with proper escaping.

    Example:
        >>> quote_literal("path/to/file.parquet")
        "'path/to/file.parquet'"
        >>> quote_literal("user's data")
        "'user''s data'"
    """
    escaped = value.replace("'", "''")
    return f"'{escaped}'"


def render_options(options: dict[str, Any]) -> str:
    """Render a mapping of options into scan-function arguments.

    The resulting string is suitable for appending to a ``*_scan`` function
    call. Keys are sorted alphabetically to keep output deterministic.

    Args:
        options: Mapping of option name to value (str, bool, int, or float).

    Returns:
        A string that starts with ``, `` when options are present (for example,
        ``", hive_partitioning=TRUE"``) or an empty string when no options
        are provided.

    Raises:
        TypeError: If a value has a type that cannot be rendered safely.
    """

    if not options:
        return ""

    parts = []
    for key in sorted(options):
        value = options[key]
        if isinstance(value, bool):
            rendered = "TRUE" if value else "FALSE"
        elif isinstance(value, (int, float)) and not isinstance(value, bool):
            rendered = str(value)
        elif isinstance(value, str):
            rendered = quote_literal(value)
        else:
            raise TypeError(
                f"Unsupported option value for '{key}': {value!r}. Expected str, bool, int, or float."
            )
        parts.append(f"{key}={rendered}")

    return ", " + ", ".join(parts)


__all__ = [
    "quote_ident",
    "quote_literal",
    "render_options",
]
