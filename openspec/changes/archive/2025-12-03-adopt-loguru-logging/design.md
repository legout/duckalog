# Design: adopt-loguru-logging

## Overview
This design describes how Duckalog will adopt `loguru` as the underlying logging implementation while preserving the existing logging semantics defined in the `errors-logging` spec. The core idea is to centralize logging configuration and usage behind a small abstraction, so that most of the codebase does not depend directly on `loguru` or the stdlib `logging` module.

## Current State
- The `errors-logging` spec assumes use of the standard Python `logging` module and describes requirements around log levels (INFO/DEBUG) and secret redaction.
- Implementation-wise, Duckalog currently:
  - Configures logging in the CLI using `logging.basicConfig` and a simple `%(message)s` formatter.
  - Uses `logging.getLogger("duckalog")` and helper functions in `config`/`validators` to emit logs.
  - Uses some `print()` calls in `src/duckalog/` modules for debug or progress messages.

## Proposed Logging Abstraction

### Logging Utilities
Introduce or extend a module such as `duckalog.logging_utils` to serve as the single entry point for application logging:

- Responsibility:
  - Initialize and configure a `loguru` logger with default sinks and formatting suitable for CLI and library usage.
  - Provide helper functions that encapsulate logging behavior:
    - `get_logger(name: str = "duckalog")`
    - `log_info(message: str, **details)`
    - `log_debug(message: str, **details)`
    - `log_error(message: str, **details)`
  - Ensure helpers enforce redaction rules for secret-like values, consistent with the `errors-logging` spec.

- Implementation notes:
  - Use a single global `logger` instance from `loguru` configured with a human-readable format by default.
  - Provide a small internal utility to sanitize details (e.g. masking values that look like credentials or are explicitly marked as secrets).
  - Optionally, provide a compatibility bridge to stdlib logging if needed for third-party integration or tests that rely on `logging`.

### CLI Integration
- The CLI currently uses a `--verbose` flag to control logging verbosity.
- In the new design:
  - The CLI will delegate to `logging_utils` to configure verbosity.
  - For example, a `configure_logging(verbose: bool)` function can set appropriate `loguru` levels (e.g. INFO for default, DEBUG for verbose).
  - This keeps the CLI thin and aligns with the rest of the codebase.

### Engine and Config Layers
- Modules such as `engine` and `config.validators` will:
  - Stop importing `logging` directly.
  - Use `logging_utils.get_logger()` or the module-level helpers for emitting messages.
  - Continue to follow the `errors-logging` patterns for exception wrapping and context, but rely on the new abstraction for the actual log emission.

### Handling print() Usage
- Library modules in `src/duckalog/` that currently use `print()` for progress or debug output should switch to logging, unless the behavior is explicitly tied to a spec that requires direct printing.
- For example:
  - Printing SQL or counts during a verbose build may become DEBUG or INFO logs.
  - Any user-facing messages that are part of the CLI contract (per specs) can remain prints or be refactored to logging plus explicit `echo` where required.

## Secret Handling
- The existing `errors-logging` spec requires that sensitive values are not logged at INFO level and are redacted even at DEBUG when derived from secret-like sources.
- The design will:
  - Keep or centralize redaction logic in `logging_utils` so that any call to `log_info` / `log_debug` automatically applies redaction rules.
  - Ensure that context dictionaries (`**details`) are sanitized before being attached to the log message.

## Migration Strategy
1. Introduce the `loguru` dependency and the `logging_utils` abstraction.
2. Update CLI and core modules to use the new helpers instead of direct `logging` calls.
3. Replace relevant `print()` statements with logging calls where appropriate.
4. Adjust tests to reflect the new logging behavior and verify redaction/levels according to the spec.
5. Keep a thin compatibility shim if any external callers or tests still expect a stdlib `logging` logger named `duckalog`.

## Alternatives Considered
- **Stay on stdlib logging only**: Lower dependency footprint but keeps existing verbosity and configuration complexity, and does not leverage loguru's ergonomics.
- **Hybrid approach (loguru + logging)**: Possible bridge but more complex to reason about. The chosen design keeps a clear abstraction while allowing a thin compatibility layer for stdlib logging where necessary.
