## 1. Query validation
- [x] 1.1 Replace naive semicolon/keyword checks with a safer approach (e.g., `sqlparse` single-statement check or DuckDB `PRAGMA disable_unsafe_alter` + `read_only` execution wrapper).
- [x] 1.2 Add tests covering semicolons inside strings/comments and DDL/DML detection.

## 2. Task result lifecycle
- [x] 2.1 Add max size/TTL eviction for `_task_results` to prevent memory leaks.
- [x] 2.2 Expose a lightweight endpoint or internal cleanup trigger for tests.

## 3. Config write simplification
- [x] 3.1 Collapse `_write_config_preserving_format` / `_write_config_atomic` into a single atomic write helper.
- [x] 3.2 Keep YAML/JSON branching minimal; drop ruamel-specific branch unless available, falling back cleanly.

## 4. Static assets visibility
- [x] 4.1 Emit a log warning when `static/` is missing instead of silent skip.

## 5. Validation
- [x] 5.1 Unit tests for new helpers and task eviction logic.
- [x] 5.2 Smoke test `duckalog ui` start-up with and without static assets present.
