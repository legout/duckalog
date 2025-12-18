## 1. Create SQL Utilities Module
- [x] 1.1 Create `src/duckalog/sql_utils.py` with shared SQL utilities
- [x] 1.2 Move `quote_ident()`, `quote_literal()`, `render_options()` functions from `sql_generation.py`
- [x] 1.3 Copy function implementations exactly (preserve signatures, docstrings, behavior)
- [x] 1.4 Add proper module docstring and `__all__` exports
- [x] 1.5 Ensure module has no external dependencies

## 2. Update SQL Generation Module
- [x] 2.1 Remove function definitions from `sql_generation.py` (keep implementations for copying)
- [x] 2.2 Add imports from `sql_utils.py` for the moved functions
- [x] 2.3 Remove deprecated `_quote_literal()` function entirely
- [x] 2.4 Update `__all__` exports in `sql_generation.py`
- [x] 2.5 Verify all dependent code continues to work

## 3. Update Dependent Files
- [x] 3.1 Update imports in `src/duckalog/engine.py` to use `sql_utils.py`
- [x] 3.2 Update imports in `src/duckalog/config/validators.py` to use `sql_utils.py`
- [x] 3.3 Update any other files importing these functions
- [x] 3.4 Update `src/duckalog/__init__.py` exports to reflect new module structure
- [x] 3.5 Ensure backward compatibility for all existing imports

## 4. Testing and Validation
- [x] 4.1 Run full test suite to ensure no regressions
- [x] 4.2 Verify that all SQL generation functions work identically
- [x] 4.3 Check that quoting behavior remains unchanged
- [x] 4.4 Validate that import analysis shows consolidation benefits
- [x] 4.5 Run type checking and linting tools

## 5. Documentation and Cleanup
- [x] 5.1 Update any documentation referencing the old import paths
- [x] 5.2 Add migration notes for internal API consumers
- [x] 5.3 Verify that the new module structure is clear and maintainable
- [x] 5.4 Test that the consolidation achieves the intended benefits