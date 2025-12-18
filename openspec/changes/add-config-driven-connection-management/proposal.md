# Change: Add Config-Driven Connection Management

## Why
DuckDB settings and attachments are session-only and must be reapplied on every database connection. The current build-once approach cannot support the desired config-driven workflow where catalogs maintain state across sessions.

## What Changes
- Add new `CatalogConnection` class to manage per-connection state restoration
- Modify catalog building to support incremental updates vs full rebuilds
- Add session state management for settings, attachments, and views
- **BREAKING**: Change entry point behavior from build-only to smart connect/apply
- Add secrets persistence option (opt-in, not default)

## Impact
- Affected specs: catalog-build, config
- Affected code: src/duckalog/engine.py, src/duckalog/cli.py, src/duckalog/python_api.py
- User workflow: `duckalog run config.yaml` becomes primary entry point