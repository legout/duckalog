# Change: Consolidate Configuration Code Duplication

## Why
The current configuration system has significant code duplication across multiple modules:
- **Environment interpolation**: Duplicate implementations in `config/loader.py` and `config/interpolation.py` 
- **Logging functions**: Duplicated in `config/validators.py` and `duckalog/logging_utils.py`
- **SQL file loading**: Similar logic scattered across `config/loader.py`, `config/sql_integration.py`, and `config/remote_config.py`
- **Path resolution**: Functions scattered across `config/validators.py`, `config/loader.py`, and `config/sql_integration.py`

This duplication creates maintenance burden, inconsistent behavior, and approximately **245 lines of redundant code**. Consolidating these will improve maintainability and reduce bug potential.

## What Changes
- **REMOVE**: Duplicate `_interpolate_env` function from `config/loader.py` 
- **UNIFY**: All logging functions to use `duckalog/logging_utils.py` as single source of truth
- **CONSOLIDATE**: SQL file loading logic into shared utilities
- **MERGE**: Path resolution functions into coherent module structure
- **UPDATE**: All imports to reference consolidated implementations
- **MAINTAIN**: Full backward compatibility through public API preservation

## Impact
- **Affected specs**: config
- **Affected code**: 
  - `src/duckalog/config/loader.py` (remove ~25 lines)
  - `src/duckalog/config/validators.py` (remove ~40 lines) 
  - `src/duckalog/config/sql_integration.py` (merge into loader)
  - `src/duckalog/config/interpolation.py` (become single source)
- **Lines removed**: ~150-200 lines of duplicated code
- **Risk**: Low (mechanical consolidation with existing tests)
- **Benefits**: Single source of truth, easier maintenance, reduced bugs
