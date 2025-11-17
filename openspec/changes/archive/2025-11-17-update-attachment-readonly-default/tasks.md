## 1. DuckDB attachment read-only default

- [x] 1.1 Update the `config` spec to state that `attachments.duckdb[].read_only` defaults to `True` when not provided.
- [x] 1.2 Change the `DuckDBAttachment` model and engine to honor the new default behavior.
- [x] 1.3 Add tests that verify default read-only behavior and explicitly configured read-write attachments.
