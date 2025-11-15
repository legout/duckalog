## Why

The PRD describes DuckDB attachments with a `read_only` flag that defaults to `True`, favoring safer, read-only access to attached databases unless explicitly overridden.

The current implementation defaults `DuckDBAttachment.read_only` to `False`, which means attached DuckDB files are writable by default. This diverges from the documented intent and is a less safe default for many catalog use cases.

## What Changes

- Update the `config` capability spec to clarify that `attachments.duckdb[].read_only` defaults to `True` when omitted.
- Adjust the `DuckDBAttachment` model and engine implementation so that attachments are opened with `READ_ONLY` unless `read_only: false` is explicitly configured.
- Add tests that cover both default read-only attachments and explicitly read-write attachments.

## Impact

- Aligns the implementation with the documented default behavior for DuckDB attachments.
- Reduces risk of accidental writes to reference catalogs when users omit `read_only`.
- Keeps writeable attachments available as an explicit, opt-in setting.

