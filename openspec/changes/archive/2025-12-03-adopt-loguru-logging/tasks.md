# Tasks: adopt-loguru-logging

1. **Assess current logging utilities and call sites**
   - Inventory all imports of `logging` and existing helper functions (e.g. `get_logger`, `log_info`, `log_debug`, `log_error`).
   - Classify `print()` usage in `src/` as either user-facing behavior, debug output, or test-only diagnostics.

2. **Design loguru-backed logging abstraction**
   - Define how `loguru` is initialized (default sinks, levels, formatting) in a single module.
   - Decide how Duckalog exposes logging to callers (e.g. `get_logger("duckalog")`, module-level helpers) while hiding `loguru` specifics from most call sites.
   - Ensure the design supports redaction of secrets at DEBUG level per the `errors-logging` spec.

3. **Update specs for logging implementation details**
   - Add or modify requirements under the `errors-logging` spec to allow (and describe) a loguru-backed implementation.
   - Capture behavior around INFO/DEBUG levels, CLI verbosity flags, and secret redaction in scenarios referencing the new abstraction.

4. **Introduce loguru dependency and bootstrap module**
   - Add `loguru` as a runtime dependency in `pyproject.toml` with an appropriate version constraint.
   - Implement the logging bootstrap module (e.g. `duckalog.logging_utils`) that configures the loguru logger and exposes the public API.

5. **Migrate core modules to the new logging API**
   - Update `duckalog.cli` to use the new logging utilities for configuring verbosity instead of calling `logging.basicConfig` directly.
   - Update `duckalog.engine`, `duckalog.config.validators`, and any other modules using `logging` to rely on the central abstraction.
   - Ensure exception-handling paths still satisfy `errors-logging` requirements around context and chaining.

6. **Replace appropriate print() usage with logging**
   - In library modules under `src/duckalog/`, replace `print()` calls that reflect runtime progress or debug output with logging calls, preserving user-visible semantics where required by specs.
   - Leave or clearly document any remaining `print()` usage that is intentionally part of the CLI contract (e.g. direct user messages where printing is explicitly required by specs).

7. **Update tests and add new coverage for logging**
   - Adjust tests that rely on stdlib `logging` (e.g. via `caplog`) to account for loguru-backed behavior, either by using the abstraction or by bridging loguru and stdlib logging.
   - Add tests that validate INFO/DEBUG behavior, redaction of secret-like values, and CLI verbosity integration.

8. **Validate behavior and specs**
   - Run unit and integration tests to confirm logging and CLI behavior remain correct.
   - Run `openspec validate adopt-loguru-logging --strict` to ensure spec deltas are consistent and complete.
   - Document any user-visible logging behavior changes in `CHANGELOG.md` if necessary.
