## 1. Consolidate Environment Variable Interpolation
- [ ] 1.1 Analyze both `_interpolate_env` implementations for differences
- [ ] 1.2 Remove duplicate from `config/loader.py` 
- [ ] 1.3 Update `config/loader.py` imports to use `config/interpolation.py`
- [ ] 1.4 Verify interpolation behavior remains identical
- [ ] 1.5 Update tests to reflect consolidated import path

## 2. Unify Logging Functions  
- [ ] 2.1 Remove duplicate logging functions from `config/validators.py`
- [ ] 2.2 Update `config/validators.py` to import from `duckalog/logging_utils.py`
- [ ] 2.3 Verify logging behavior and redaction logic unchanged
- [ ] 2.4 Update all config module imports to use consolidated logging

## 3. Consolidate SQL File Loading Logic
- [ ] 3.1 Analyze SQL loading patterns across `loader.py`, `sql_integration.py`, `remote_config.py`
- [ ] 3.2 Create shared SQL loading utilities in `config/loader.py`
- [ ] 3.3 Update `sql_integration.py` to use shared logic (or remove if now redundant)
- [ ] 3.4 Ensure `remote_config.py` uses consolidated approach
- [ ] 3.5 Test SQL loading behavior remains identical

## 4. Merge Path Resolution Functions
- [ ] 4.1 Create unified path resolution module structure
- [ ] 4.2 Consolidate `resolve_relative_path`, `_resolve_import_path`, and related functions
- [ ] 4.3 Update all modules to use consolidated path resolution
- [ ] 4.4 Verify path security validation remains intact
- [ ] 4.5 Test path resolution with various file structures

## 5. Validation and Testing
- [ ] 5.1 Run existing test suite to ensure no regressions
- [ ] 5.2 Add tests for consolidated import paths
- [ ] 5.3 Verify performance impact (should be neutral or positive)
- [ ] 5.4 Update documentation for any changed import paths
- [ ] 5.5 Create migration notes for internal API changes
