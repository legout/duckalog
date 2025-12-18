# Change: Refactor Configuration Architecture for Maintainability

## Why
The configuration system suffers from architectural complexity that hinders maintainability:
- **`loader.py` complexity**: 1670 lines handling too many responsibilities (parsing, imports, validation, security)
- **Circular import risks**: `config/__init__.py` ↔ `remote_config.py` creates fragile initialization
- **SOLID violations**: Modules violate Single Responsibility and Interface Segregation principles
- **Import complexity**: Re-export patterns and conditional imports create confusing dependency chains

This refactoring will break down the monolithic `loader.py` into focused modules, eliminate circular dependencies, and establish clean architectural boundaries while maintaining full API compatibility.

## What Changes
- **SPLIT**: `loader.py` into focused modules: `api.py`, `loading/`, `resolution/`, `security/`
- **BREAK**: Circular import between `config/__init__.py` and `remote_config.py`
- **ESTABLISH**: Clean architectural boundaries with dependency injection patterns
- **IMPLEMENT**: Request-scoped caching for performance
- **CREATE**: Abstract base classes for extensibility
- **MAINTAIN**: 100% backward compatibility through deprecation strategy

## Impact
- **Affected specs**: config, python-api
- **Affected code**: 
  - `src/duckalog/config/` (major restructuring)
  - `src/duckalog/remote_config.py` (circular dependency resolution)
  - Tests and examples (updated import paths)
- **Architecture**: Clean separation of concerns, dependency injection, better testability
- **Risk**: Medium (architectural change requiring careful dependency management)
- **Timeline**: 2-3 releases with deprecation warnings
