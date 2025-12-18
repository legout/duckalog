# Change: Refactor API Organization for Better Maintainability

## Why
The current codebase has grown organically with some architectural inconsistencies:
- `config.py` serves as a re-export layer that duplicates the `config/` package structure
- `python_api.py` contains mixed concerns (convenience functions + connection management)
- CLI and Python API have overlapping but inconsistent interfaces
- Import paths are confusing with both `config` module and `config.py` file

This refactoring will improve code organization, reduce duplication, and make the API more intuitive while maintaining full backwards compatibility.

## What Changes
- **BREAKING**: Consolidate configuration loading into a single, clear API
- **BREAKING**: Reorganize Python API functions by concern (generation, validation, connection)
- **BREAKING**: Simplify import paths and eliminate confusing dual structures
- Add comprehensive deprecation warnings with migration guides
- Update documentation and examples to use new patterns

## Impact
- Affected specs: config, python-api, cli
- Affected code: `src/duckalog/`, tests, examples, documentation
- Migration risk: Low (deprecation warnings + compatibility layer)
- Timeline: 2-3 releases with deprecation warnings, then breaking changes
