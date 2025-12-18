# Change: Remove Redundant sql_integration.py File

## Why
The current configuration system has a completely redundant wrapper file `src/duckalog/config/sql_integration.py` that provides zero functionality beyond delegating to `loader.py`. This creates unnecessary indirection, circular import confusion, and maintenance burden.

## What Changes
- **REMOVE**: `src/duckalog/config/sql_integration.py` entirely (37 lines of pure redundancy)
- **UPDATE**: Any imports that reference `sql_integration.py` to use `loader.py` directly
- **MAINTAIN**: All existing functionality continues to work unchanged
- **PRESERVE**: Full backward compatibility through public API preservation

## Impact
- **Affected specs**: config
- **Affected code**: 
  - `src/duckalog/config/sql_integration.py` (remove completely)
  - `src/duckalog/config/loader.py` (update imports if any)
  - `src/duckalog/config/__init__.py` (remove exports if any)
- **Lines removed**: 37 lines of pure redundancy
- **Risk**: Very Low (pure removal with zero functional impact)
- **Benefits**: Eliminates circular import confusion, reduces maintenance burden, cleaner architecture