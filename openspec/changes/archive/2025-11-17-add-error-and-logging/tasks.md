## 1. Error handling and logging behavior

- [x] 1.1 Implement `ConfigError` and `EngineError` exception classes and use them consistently in config loading and engine code.
- [x] 1.2 Ensure CLI commands catch these errors, print clear messages, and exit with appropriate status codes.
- [x] 1.3 Implement logging helpers that emit high-level INFO logs and more detailed DEBUG logs while redacting secrets.
- [x] 1.4 Add tests that verify error types, exit codes, and that secret values are not present in INFO-level logs.
