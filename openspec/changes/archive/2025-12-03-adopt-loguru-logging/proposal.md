# Change Proposal: Adopt Loguru for Duckalog Logging

## Summary
Duckalog will migrate from direct usage of Python's standard `logging` module to a centralized logging abstraction backed by `loguru`. This change keeps the existing public behavior (log levels, redaction guarantees, CLI verbosity flags) while simplifying configuration and creating a consistent logging surface for the library, CLI, and Python API.

## Why
Duckalog's current logging implementation uses Python's stdlib `logging` module directly across multiple modules, leading to:
- **Inconsistent configuration**: Logging is configured in `cli.py`, `engine.py`, and `config.validators` independently
- **Limited extensibility**: Adding new features like JSON formatting or file sinks requires changes in multiple places
- **Print statements**: Some library code still uses `print()` instead of proper logging
- **Maintenance burden**: Each module needs to handle logging configuration separately

Moving to a centralized `loguru`-backed abstraction addresses these issues while improving developer experience with better ergonomics and built-in features.

## Motivation
- **Consistency**: Logging is currently configured in multiple places (e.g. `cli`, `engine`, `config.validators`) using stdlib `logging`. Adopting `loguru` provides a single, opinionated logger with consistent formatting and behavior.
- **Developer experience**: `loguru` makes it easier to emit structured logs, capture exceptions, and adjust sinks/levels during debugging or integration into larger systems.
- **Extensibility**: A centralized logging utility layer simplifies future enhancements (e.g. JSON logs, file sinks, richer context) without touching every call site.
- **Print usage**: Some library and test code still uses `print()` for progress/debug output. Where appropriate for library behavior (not test harness output), these should be replaced by logging to align with the `errors-logging` spec.

## Scope
In scope:
- Introduce `loguru` as the library's underlying logging implementation.
- Provide a small logging utility module (or extend existing utilities) that exposes a stable API (`get_logger`, `log_info`, `log_debug`, `log_error`) used throughout Duckalog.
- Update library code (e.g. `config`, `engine`, CLI) to:
  - Stop importing and configuring stdlib `logging` directly at call sites.
  - Use the centralized logging utilities backed by `loguru`.
- Review and replace `print()` usage in the library (not tests) with appropriate logging calls, while preserving any user-visible semantics required by existing specs (e.g. CLI error messages).
- Maintain the guarantees in the `errors-logging` spec around log levels and secret redaction.

Out of scope (for this change):
- Changing the CLI surface area (flags, commands, or exit codes).
- Introducing new log sinks (files, remote backends) beyond what is needed for parity.
- Converting test helper `print()` calls that are only used for local debugging and not part of the product behavior, unless they interfere with or obscure logging behavior.

## What Changes
The following changes implement the loguru migration:

### Files Modified
1. **src/duckalog/config/validators.py**
   - Replace `import logging` with `from loguru import logger`
   - Update `get_logger()` to return loguru logger with binding
   - Refactor `_emit_std_logger()` to `_emit_loguru_logger()` using loguru
   - Maintain existing redaction logic

2. **src/duckalog/cli.py**
   - Remove `import logging`, add `from loguru import logger`
   - Rewrite `_configure_logging()` to use loguru configuration
   - Configure loguru handler with appropriate level and format

3. **src/duckalog/config/loader.py**
   - Remove duplicate logging stub functions (log_info, log_debug)
   - Remove unused `import logging`

4. **src/duckalog/engine.py**
   - Remove `import logging`
   - Remove direct logging.getLogger() call

5. **src/duckalog/config/models.py**
   - Remove unused `import logging`

6. **tests/test_logging_utils.py**
   - Update tests to work with loguru instead of caplog
   - Add tests for redaction logic and loguru interface

### No Changes to Public API
- All logging helper functions (`get_logger`, `log_info`, `log_debug`, `log_error`) maintain same signatures
- CLI verbosity flags work identically
- Redaction behavior unchanged

## Risks and Considerations
- **Dependency footprint**: `loguru` adds a new runtime dependency. The change must respect the "Minimal dependencies" constraint and be justified by better logging ergonomics.
- **Behavioral parity**: CLI users expect familiar verbosity flags and message formats. The migration must preserve, or deliberately and minimally refine, the existing experience.
- **Secret handling**: Existing requirements specify redaction of secret-like values in logs. The loguru integration must ensure these guarantees continue to hold.

## Acceptance Criteria
- Duckalog's logging behavior is defined via a central loguru-based utility layer and no core modules import stdlib `logging` directly for application logging.
- Library and CLI logs continue to respect INFO/DEBUG boundaries and redaction rules from the `errors-logging` spec.
- User-facing behavior of CLI error messages and exit codes is unchanged or clearly documented if improved.
- Library `print()` usage that surfaces runtime information to users is replaced with logging where consistent with specs; tests may continue to use `print()` for diagnostic output.
