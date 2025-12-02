# Refactor: Simplify and Standardize Exceptions

## Why

Duckalog currently uses a mix of:

- Domain-specific exceptions (`ConfigError`, `EngineError`, `RemoteConfigError`, `SQLFileError`).
- Generic `Exception` and bare `except Exception` blocks (some of which are silent).

This leads to:

- Inconsistent error handling patterns.
- Harder-to-debug failures (missing context, missing exception chaining).
- Unclear guidance for contributors about which exceptions to raise and when.

We want a small, clear exception hierarchy and consistent usage across modules.

## What Changes

- **Define a base exception hierarchy**
  - Introduce `DuckalogError` as the base class for all library exceptions.
  - Ensure existing domain-specific exceptions subclass `DuckalogError`.

- **Standardize error handling patterns**
  - Replace bare `except Exception` blocks with:
    - Targeted exception types where possible, or
    - `except Exception as exc:` that:
      - Logs context using the logging utilities.
      - Raises an appropriate `DuckalogError` subclass with `from exc` to preserve tracebacks.
  - Eliminate silent `pass` blocks for error handling outside of exceptional fallback cases that are explicitly documented.

- **Clarify error behavior in specs**
  - Update specs to:
    - Document the primary exception types users should expect from common operations.
    - Require that low-level errors be wrapped in domain-specific exceptions with clear messages.

## Impact

- **Specs updated**
  - `specs/errors-logging/spec.md`:
    - Expanded to describe the exception hierarchy and expected patterns.
  - Other specs (config, catalog-build, remote-config, etc.):
    - Updated to reference the new hierarchy where relevant.

- **Implementation**
  - `src/duckalog/errors.py` (or similar module):
    - Central definition of `DuckalogError` and its subclasses.
  - Updates across modules (`config.py`, `engine.py`, `remote_config.py`, `sql_file_loader.py`, etc.) to use the standardized exceptions and patterns.

- **Non-goals**
  - No change to the high-level semantics of when operations fail; only error types and messages are standardized.

## Risks and Trade-offs

- Some callers that were previously catching generic exceptions may need to be updated to catch the appropriate `DuckalogError` subclasses; this is acceptable and desirable for clarity.

