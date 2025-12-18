## 1. Create SQL Utilities Module
- [ ] 1.1 Create `src/duckalog/sql_utils.py` with shared SQL utilities
- [ ] 1.2 Move `quote_ident()`, `quote_literal()`, `render_options()` functions from `sql_generation.py`
- [ ] 1.3 Copy function implementations exactly (preserve signatures, docstrings, behavior)
- [ ] 1.4 Add proper module docstring and `__all__` exports
- [ ] 1.5 Ensure module has no external dependencies

## 2. Update SQL Generation Module
- [ ] 2.1 Remove function definitions from `sql_generation.py` (keep implementations for copying)
- [ ] 2.2 Add imports from `sql_utils.py` for the moved functions
- [ ] 2.3 Remove deprecated `_quote_literal()` function entirely
- [ ] 2.4 Update `__all__` exports in `sql_generation.py`
- [ ] 2.5 Verify all dependent code continues to work

## 3. Update Dependent Files
- [ ] 3.1 Update imports in `src/duckalog/engine.py` to use `sql_utils.py`
- [ ] 3.2 Update imports in `src/duckalog/config/validators.py` to use `sql_utils.py`
- [ ] 3.3 Update any other files importing these functions
- [ ] 3.4 Update `src/duckalog/__init__.py` exports to reflect new module structure
- [ ] 3.5 Ensure backward compatibility for all existing imports

## 4. Testing and Validation
- [ ] 4.1 Run full test suite to ensure no regressions
- [ ] 4.2 Verify that all SQL generation functions work identically
- [ ] 4.3 Check that quoting behavior remains unchanged
- [ ] 4.4 Validate that import analysis shows consolidation benefits
- [ ] 4.5 Run type checking and linting tools

## 5. Documentation and Cleanup
- [ ] 5.1 Update any documentation referencing the old import paths
- [ ] 5.2 Add migration notes for internal API consumers
- [ ] 5.3 Verify that the new module structure is clear and maintainable
- [ ] 5.4 Test that the consolidation achieves the intended benefits