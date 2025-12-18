# Change: Enhance SQL Public API Exports

## Why
The current public API in `src/duckalog/__init__.py` doesn't provide optimal organization and discoverability for SQL-related functionality. Users must understand internal module structure to access commonly used SQL utilities. Enhancing the public API will improve developer experience and make the API more discoverable.

## What Changes
- **ENHANCE**: `src/duckalog/__init__.py` SQL exports for better discoverability
- **ORGANIZE**: SQL functionality into logical groups (generation, utilities, loading)
- **ADD**: Convenience imports for commonly used SQL utilities
- **MAINTAIN**: 100% backward compatibility for all existing imports
- **PRESERVE**: All existing `__all__` exports without modification

## Impact
- **Affected specs**: config, python-api
- **Affected code**: 
  - `src/duckalog/__init__.py` (enhance exports and organization)
  - Documentation files (update examples)
- **Risk**: Very Low (pure additive enhancement)
- **Benefits**: Better API discoverability, improved developer experience, organized functionality