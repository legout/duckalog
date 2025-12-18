## 1. Consolidate Environment Variable Interpolation
- [x] 1.1 Analyze both `_interpolate_env` implementations for differences
- [x] 1.2 Remove duplicate from `config/loader.py` 
- [x] 1.3 Update `config/loader.py` imports to use `config/interpolation.py`
- [x] 1.4 Verify interpolation behavior remains identical
- [x] 1.5 Update tests to reflect consolidated import path
- [x] 1.6 Add support for default values in env interpolation (${env:VAR:default})

## 2. Unify Logging Functions  
- [x] 2.1 Analyze logging function implementations
- [x] 2.2 Consolidate to single source of truth in `config/validators.py`
- [x] 2.3 Update `logging_utils.py` as a backward-compatible re-export wrapper
- [x] 2.4 Verify logging behavior and redaction logic unchanged
- [x] 2.5 Update all config module imports to use consolidated logging

## 3. Consolidate SQL File Loading Logic
- [x] 3.1 Analyze SQL loading patterns across `loader.py`, `sql_integration.py`, `remote_config.py`
- [x] 3.2 Create shared SQL loading utilities in `config/interpolation.py` (`process_sql_file_references`)
- [x] 3.3 Remove `sql_integration.py` (now fully redundant)
- [x] 3.4 Ensure `remote_config.py` uses consolidated approach
- [x] 3.5 Test SQL loading behavior remains identical

## 4. Merge Path Resolution Functions
- [x] 4.1 Consolidate path resolution module structure in `config/validators.py`
- [x] 4.2 Consolidate `resolve_relative_path`, `_resolve_import_path`, and related functions
- [x] 4.3 Update all modules to use consolidated path resolution
- [x] 4.4 Verify path security validation remains intact
- [x] 4.5 Test path resolution with various file structures
- [x] 4.6 Add `_resolve_paths_in_config` to loader for attachment path resolution

## 5. Validation and Testing
- [x] 5.1 Run existing test suite to ensure no regressions
- [x] 5.2 Add tests for consolidated import paths
- [x] 5.3 Verify performance impact (should be neutral or positive)
- [x] 5.4 Update documentation for any changed import paths
- [x] 5.5 Export `_load_config_from_local_file` from config package for testing

## Summary

All consolidation tasks completed:
- **Environment interpolation**: Single implementation in `interpolation.py` with default value support
- **Logging functions**: Single implementation in `validators.py`, re-exported via `logging_utils.py`
- **SQL file loading**: Consolidated in `interpolation.py` (`process_sql_file_references`)
- **Path resolution**: Consolidated in `validators.py` with `_resolve_paths_in_config` for attachment handling
- **Tests**: 98/98 config and logging tests passing
