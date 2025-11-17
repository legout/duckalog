## Why

The PRD defines `ConfigError`, `EngineError`, and logging behavior, but these guarantees are not yet captured in OpenSpec, making error handling and observability behavior implicit rather than contractually defined.

Formalizing error and logging behavior is important for callers (CLI and Python) and for security (avoiding leaked secrets in logs).

## What Changes

- Introduce an `errors-logging` capability spec that defines:
  - When `ConfigError` vs `EngineError` MUST be raised.
  - How the CLI maps errors to exit codes and user-visible messages.
  - Logging levels and what information is allowed at INFO vs DEBUG.
- Capture security-related logging constraints, especially around secrets resolved from environment variables.

## Impact

- Gives users a predictable error model and logging behavior they can rely on in automation and monitoring.
- Reduces the risk of accidental secret exposure in logs.
- Makes future changes to error or logging behavior reviewable via OpenSpec.

