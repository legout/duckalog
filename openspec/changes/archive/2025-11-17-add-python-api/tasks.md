## 1. Python API functions

- [x] 1.1 Implement `generate_sql(config_path: str) -> str` as a thin wrapper around `load_config` and `generate_all_views_sql`.
- [x] 1.2 Implement `validate_config(config_path: str) -> None` that loads and validates a config, raising `ConfigError` on failure without connecting to DuckDB.
- [x] 1.3 Add unit tests for `generate_sql` and `validate_config` to verify behavior on valid and invalid configs, including env interpolation errors.
