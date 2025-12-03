# Refactor: Consolidate Config Layer

## Summary
Consolidate the configuration layer by merging related modules (`path_resolution.py`, `sql_file_loader.py`) into `config.py` to reduce complexity and improve maintainability. This reduces cognitive load and eliminates circular dependencies.

## Problem Statement
The current architecture separates configuration handling across multiple modules:
- `config.py` (1,353 lines) - Pydantic models and validation
- `path_resolution.py` (366 lines) - Path utilities and security
- `sql_file_loader.py` (440 lines) - SQL file processing
- `logging_utils.py` (118 lines) - Logging utilities

This separation creates:
- Unnecessary abstraction layers
- Circular import dependencies
- Scattered validation logic
- Difficult to trace data flow
- Mental overhead for contributors

## Proposed Solution
Consolidate `path_resolution.py` and `sql_file_loader.py` into `config.py`:

### Phase 1: Merge Path Resolution
- Move path resolution functions into `config.py` as module-level functions
- Path-related utilities become private functions (prefixed with `_`)
- Eliminate duplicate path security validation

### Phase 2: Merge SQL File Loader
- Integrate SQL file loading into config loading pipeline
- SQL file loading becomes part of `load_config()` function
- Simplify SQL file loader classes to pure functions

### Phase 3: Simplify Logging
- Replace `logging_utils.py` abstraction with direct `logging` module usage
- Remove loguru dependency from core library
- Keep simple redaction function in `config.py`

## Benefits
- **Reduced complexity**: ~1,200 lines in unified config module vs 1,800 across 3 modules
- **Better maintainability**: All config logic in one place
- **Clearer data flow**: Fewer transformations and indirection
- **Eliminated circular dependencies**: Remove import cycles
- **Faster understanding**: Contributors don't need to navigate multiple modules

## Breaking Changes
None for public API. Internal refactoring only.

## Files Modified
- `src/duckalog/config.py` - Expand to include path and SQL file handling
- `src/duckalog/path_resolution.py` - **REMOVED**
- `src/duckalog/sql_file_loader.py` - **REMOVED**
- `src/duckalog/logging_utils.py` - **REMOVED**
- Update imports in: `cli.py`, `python_api.py`, `remote_config.py`

## Test Impact
- No test changes required (tests use public API)
- Path resolution tests moved to test_config.py
- SQL file loader tests integrated into config tests

## Risks
- **Low**: All changes are refactoring, no behavior changes
- Existing tests validate functionality
- Gradual migration possible (keep old modules as shims initially)