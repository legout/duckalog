# Change: Add DuckDB Settings Support

## Why
Users need to configure DuckDB session settings (like `threads = 32`) alongside pragmas in their catalog configuration files. Currently, only pragmas are supported, but DuckDB has many important settings that affect performance and behavior that are not pragma statements.

## What Changes
- Add `settings` field to `DuckDBConfig` to accept DuckDB SET statements
- Extend engine to apply settings after pragmas
- Support both string (single setting) and list (multiple settings) formats
- **BREAKING**: None - this is additive functionality

## Impact
- Affected specs: config
- Affected code: src/duckalog/config.py, src/duckalog/engine.py