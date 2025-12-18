# Change: Create SQL Utilities Module for Shared Functions

## Why
The current codebase has shared SQL utilities (`quote_ident`, `quote_literal`, `render_options`) that are imported 50+ times across multiple files. This creates maintenance burden, potential for inconsistent behavior, and scattered dependencies. Consolidating these utilities into a single module will improve maintainability and provide a single source of truth.

## What Changes
- **CREATE**: `src/duckalog/sql_utils.py` with shared SQL utilities
- **MOVE**: `quote_ident()`, `quote_literal()`, `render_options()` from `sql_generation.py` to `sql_utils.py`
- **UPDATE**: `sql_generation.py` to import functions from `sql_utils.py`
- **UPDATE**: All dependent files to use consolidated utilities
- **REMOVE**: Deprecated `_quote_literal()` function
- **MAINTAIN**: Exact same function signatures and behavior

## Impact
- **Affected specs**: config
- **Affected code**: 
  - `src/duckalog/sql_utils.py` (new shared utilities module)
  - `src/duckalog/sql_generation.py` (update imports, remove function definitions)
  - `src/duckalog/engine.py` (update imports)
  - `src/duckalog/config/validators.py` (update imports)
  - `src/duckalog/__init__.py` (update exports)
- **Lines added**: ~100 lines for new module
- **Lines removed**: ~50 lines from deduplication
- **Risk**: Low (additive improvement with backward compatibility)
- **Benefits**: Single source of truth, reduced import complexity, easier maintenance