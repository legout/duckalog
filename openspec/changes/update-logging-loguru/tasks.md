## 1. Switch logging implementation to loguru

- [x] 1.1 Update the `errors-logging` spec to mention `loguru` as the
      implementation backend while keeping the public logging API stable.
- [x] 1.2 Add `loguru` as a dependency in the project configuration.
- [x] 1.3 Refactor `logging_utils` to use `loguru` for logging while
      preserving redaction semantics and helper function names.
- [x] 1.4 Adjust CLI/engine logging setup to rely on the updated helpers
      (avoid duplicate configuration with the stdlib where possible).
- [x] 1.5 Add or update tests to confirm log redaction still works and that
      switching the backend does not change observable log messages or error
      handling behavior.
