# Design: Exception Hierarchy and Usage

## Goals

- Provide a consistent, discoverable exception hierarchy for Duckalog.
- Ensure exceptions carry context and preserve original tracebacks.

## Proposed hierarchy

```python
class DuckalogError(Exception):
    """Base exception for all Duckalog errors."""

class ConfigError(DuckalogError):
    """Configuration-related errors."""

class EngineError(DuckalogError):
    """Catalog build / engine errors."""

class RemoteConfigError(ConfigError):
    """Remote configuration loading errors."""

class SQLFileError(DuckalogError):
    """Errors related to SQL file loading/parsing."""
```

Additional subclasses can be added where helpful (for example, `PathResolutionError` inheriting from `ConfigError`).

## Usage patterns

- When catching lower-level exceptions:

```python
try:
    ...
except SomeLibraryError as exc:
    log_error("Failed to perform X", error=str(exc), context=...)
    raise EngineError("Failed to perform X") from exc
```

- Avoid:
  - Bare `except Exception` without logging or re-raising.
  - Raising generic `Exception` in library code.

## Spec alignment

- `specs/errors-logging/spec.md` will:
  - List the main exception types and scenarios.
  - Encourage users to catch `DuckalogError` (or subclasses) when handling library-specific failures.

