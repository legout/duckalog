## 1. Input validation
- [x] 1.1 Reject binary/DB extensions (`.duckdb`, `.db`, `.sqlite`, etc.) in the UI entrypoint with a friendly message.
- [x] 1.2 Add UTF-8 sniff/UnicodeDecodeError guard in `_load_config`; return UIError with guidance to use YAML/JSON config.

## 2. Safety & correctness
- [x] 2.1 Quote view names in `_get_schema` using existing `_safe_identifier`.
- [x] 2.2 Remove duplicate `datastar_py` import block.

## 3. Clean-up (optional if time)
- [x] 3.1 Add small helper for JSON error responses to reduce repetition.

## 4. Validation
- [x] 4.1 Run `uv run duckalog ui <valid-catalog.yaml>` smoke test.
- [x] 4.2 Verify `uv run duckalog ui product_analytics.duckdb` now returns a clear error instead of traceback.
