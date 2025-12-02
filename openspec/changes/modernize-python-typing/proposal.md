# Change: Modernize Python Type Annotations

## Why
The project currently uses legacy typing imports (`Union`, `Optional`, `List`, `Dict`, etc.) despite having Python 3.12+ as the minimum requirement. Modern Python type annotations (PEP 604 unions and built-in generics) provide cleaner, more readable code and reduce import overhead. The project conventions already document these practices, but the codebase hasn't been fully updated to match.

## What Changes
- **Replace Union with PEP 604 unions**: `Union[str, int]` → `str | int`, `Optional[str]` → `str | None`
- **Replace typing generics with built-ins**: `List[int]` → `list[int]`, `Dict[str, Any]` → `dict[str, Any]`, `Set[str]` → `set[str]`, `Tuple[int, ...]` → `tuple[int, ...]`
- **Use collections.abc for callables and iterables**: Replace `typing.Callable` and `typing.Iterable` with `collections.abc` imports
- **Update imports**: Remove unnecessary `typing` imports and add `collections.abc` imports where needed
- **Maintain TYPE_CHECKING imports**: Keep `TYPE_CHECKING` imports for forward references

## Impact
- **Affected specs**: None (this is a code style refactoring)
- **Affected code**: 13 source files with ~200+ legacy typing usages, plus test files
  - Highest priority: config.py (77 usages), cli.py (45 usages), dashboard/state.py (14 usages)
- **User Experience**: No functional changes, but cleaner, more modern codebase
- **Breaking Changes**: None - this is purely syntactic refactoring
- **Dependencies**: No new dependencies required (uses built-in Python features)

## Alternative Approaches Considered
1. **Gradual migration**: Could update files one by one over time (but inconsistent style during transition)
2. **Automated refactoring tool**: Could use tools like `pyupgrade` (but manual review needed for edge cases)
3. **Keep legacy typing**: Could maintain current style (but goes against documented conventions and modern Python practices)

The chosen approach performs a comprehensive migration to align the codebase with the documented conventions and modern Python typing best practices.