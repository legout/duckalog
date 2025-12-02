"""Logging helpers with secret redaction for Duckalog."""

from __future__ import annotations

import logging
from typing import Any

_LOGURU_LOGGER: Any

try:  # pragma: no cover - exercised when loguru is installed
    from loguru import logger as _LOGURU_LOGGER

    _HAS_LOGURU = True
except Exception:  # pragma: no cover - fallback for environments without loguru
    _LOGURU_LOGGER = None
    _HAS_LOGURU = False


LOGGER_NAME = "duckalog"
SENSITIVE_KEYWORDS = ("password", "secret", "token", "key", "pwd")


def get_logger(name: str = LOGGER_NAME) -> logging.Logger:
    """Return a logger configured for Duckalog.

    When ``loguru`` is available, this returns the global loguru logger.
    Otherwise, it falls back to the standard-library logger with the given
    name. This keeps the public API stable while allowing the implementation
    to switch backends.

    Args:
        name: Logger name. Defaults to the project-wide logger name.

    Returns:
        A logger-like object suitable for logging messages.
    """

    if _HAS_LOGURU:
        return _LOGURU_LOGGER  # type: ignore[return-value]
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


def _emit_std_logger(level: int, message: str, safe_details: dict[str, Any]) -> None:
    logger = logging.getLogger(LOGGER_NAME)
    if safe_details:
        logger.log(level, "%s %s", message, safe_details)
    else:
        logger.log(level, message)


def _log(level: int, message: str, **details: Any) -> None:
    safe_details: dict[str, Any] = {}
    if details:
        safe_details = {k: _redact_value(v, k) for k, v in details.items()}

    if _HAS_LOGURU:
        text = f"{message} {safe_details}" if safe_details else message
        if level >= logging.ERROR:
            _LOGURU_LOGGER.error(text)
        elif level >= logging.INFO:
            _LOGURU_LOGGER.info(text)
        else:
            _LOGURU_LOGGER.debug(text)
        _emit_std_logger(level, message, safe_details)
        return

    _emit_std_logger(level, message, safe_details)


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
