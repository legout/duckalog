## Why

The PRD specifies a minimum Python API surface (`build_catalog`, `generate_sql`, `validate_config`), but only `build_catalog` behavior is currently covered by an OpenSpec change.
Without an explicit API spec, it is harder for users to rely on `generate_sql` and `validate_config` as stable, documented entry points.

## What Changes

- Introduce a `python-api` capability spec that defines:
  - The signatures and behavior of `generate_sql(config_path: str) -> str` and `validate_config(config_path: str) -> None`.
  - Their relationship to lower-level building blocks (`load_config`, `generate_all_views_sql`, and config validation).
- Clarify that these functions are convenience wrappers that perform no side effects on DuckDB catalogs.

## Impact

- Provides a clear, documented Python API that matches the PRD’s functional requirements.
- Simplifies usage for pipeline and application developers who prefer Python calls over the CLI.
- Keeps API stability and behavior changes reviewable via OpenSpec.

