# ADR-002: Eliminate Circular Dependencies

**Date**: 2024-12-18  
**Status**: Accepted  
**Deciders**: Duckalog Architecture Team

## Context

The original architecture had a circular import dependency:
- `remote_config.py` imported: `from .config import Config`
- `config/__init__.py` imported: `from duckalog.remote_config import is_remote_uri, load_config_from_uri`

This created several issues:
- **Initialization problems**: Modules couldn't be imported in certain orders
- **Testing difficulties**: Circular imports complicate mocking and testing
- **Fragile architecture**: Changes in one module could break another unexpectedly

## Decision

Eliminate the circular dependency by implementing lazy imports and type checking:

1. **Lazy Imports**: Move `Config` imports inside functions where needed
2. **TYPE_CHECKING**: Use conditional imports for type annotations only
3. **Clean Separation**: Restructure the dependency hierarchy to be acyclic

## Consequences

### Positive
- **Clean initialization**: Modules can be imported in any order
- **Better testing**: Easier to mock and test individual components
- **Maintainable architecture**: Clear, predictable dependency relationships
- **IDE support**: Better autocomplete and error detection

### Negative
- **Minor performance cost**: Lazy imports add small overhead
- **More verbose code**: Type checking conditions add complexity

### Neutral
- **No functional changes**: User-facing behavior remains identical
- **Better error messages**: Circular imports often cause confusing errors

## Implementation Details

```python
# Before (circular)
from .config import Config  # Circular!

# After (clean)
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .config.models import Config

# Use lazy import inside functions
def load_config_from_uri(uri: str) -> Config:
    from .config.models import Config  # Lazy import
    # ... function implementation
```

## References

- [ADR-001: Break Monolithic loader.py](adr-001-break-monolithic-loader.md)
- [Python typing documentation](https://docs.python.org/3/library/typing.html)