"""Logging helpers with secret redaction for Duckalog."""

from __future__ import annotations

import logging
from typing import Any, Dict

LOGGER_NAME = "duckalog"
SENSITIVE_KEYWORDS = ("password", "secret", "token", "key", "pwd")


def get_logger(name: str = LOGGER_NAME) -> logging.Logger:
    """Return a logger configured for Duckalog.

    Args:
        name: Logger name. Defaults to the project-wide logger name.

    Returns:
        A :class:`logging.Logger` instance.
    """

    return logging.getLogger(name)


def _is_sensitive(key: str) -> bool:
    lowered = key.lower()
    return any(keyword in lowered for keyword in SENSITIVE_KEYWORDS)


def _redact_value(value: Any, key_hint: str = "") -> Any:
    if isinstance(value, dict):
        return {k: _redact_value(v, k) for k, v in value.items()}
    if isinstance(value, list):
        return [_redact_value(item, key_hint) for item in value]
    if isinstance(value, str) and _is_sensitive(key_hint):
        return "***REDACTED***"
    return value


def _log(level: int, message: str, **details: Any) -> None:
    logger = get_logger()
    if details:
        safe_details: Dict[str, Any] = {k: _redact_value(v, k) for k, v in details.items()}
        logger.log(level, "%s %s", message, safe_details)
    else:
        logger.log(level, message)


def log_info(message: str, **details: Any) -> None:
    """Log a redacted INFO-level message.

    Args:
        message: High-level message to log.
        **details: Structured key/value details to attach to the log message.
    """

    _log(logging.INFO, message, **details)


def log_debug(message: str, **details: Any) -> None:
    """Log a redacted DEBUG-level message.

    Args:
        message: Debug message to log.
        **details: Structured key/value details to attach to the log message.
    """

    _log(logging.DEBUG, message, **details)


def log_error(message: str, **details: Any) -> None:
    """Log a redacted ERROR-level message.

    Args:
        message: Error message to log.
        **details: Structured key/value details to attach to the log message.
    """

    _log(logging.ERROR, message, **details)


__all__ = ["get_logger", "log_info", "log_debug", "log_error"]
