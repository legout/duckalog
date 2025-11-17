## Why

Duckalog currently uses the standard library `logging` module plus custom
helpers in `logging_utils.py` for redaction and structured details. While this
is sufficient, the PRD expects clear, structured logging and future
observability features. Using `loguru` as the underlying logging backend can
simplify configuration, provide richer formatting and context, and make it
easier to route logs to different sinks while preserving the existing
error/logging contract.

Adopting `loguru` behind the existing logging helpers keeps the public
interface stable (`log_info`, `log_debug`, `log_error`) while gaining more
flexibility for advanced users and future changes.

## What Changes

- Introduce `loguru` as the internal logging backend for Duckalog.
- Update the `errors-logging` capability spec to clarify that:
  - The public logging API is still the helper functions in
    `logging_utils.py`.
  - The implementation uses `loguru` under the hood for routing and
    formatting.
- Update `logging_utils` to:
  - Initialize a `loguru` logger with sane defaults.
  - Preserve the existing redaction behavior for sensitive fields.
  - Provide a thin compatibility layer for code that expects the standard
    library logger (e.g., `get_logger`).
- Ensure the CLI and engine use the updated helpers rather than configuring
  `logging` directly where possible.

## Impact

- Keeps the public behavior (log levels, redaction guarantees) consistent with
  the existing `errors-logging` spec.
- Simplifies future enhancements such as structured logs, multiple sinks, or
  per-command logging configuration.
- Adds a new dependency (`loguru`) but confines its usage to the logging layer
  so that the rest of the codebase remains decoupled from the choice of
  logging backend.

