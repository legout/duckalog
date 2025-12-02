## MODIFIED Requirements
### Requirement: Use Modern Python Type Annotations
The codebase SHALL use modern Python type annotations (PEP 604 unions and built-in generics) instead of legacy typing imports.

#### Scenario: Union types use PEP 604 syntax
- **WHEN** a function parameter or return type uses a union
- **THEN** the code uses `str | int` syntax instead of `Union[str, int]`
- **AND** optional types use `str | None` instead of `Optional[str]`
- **AND** no `Union` imports remain in the codebase except in TYPE_CHECKING blocks

#### Scenario: Generic collections use built-in types
- **WHEN** a function parameter or return type uses generic collections
- **THEN** the code uses `list[int]` instead of `List[int]`
- **AND** the code uses `dict[str, Any]` instead of `Dict[str, Any]`
- **AND** the code uses `set[str]` instead of `Set[str]`
- **AND** the code uses `tuple[int, ...]` instead of `Tuple[int, ...]`
- **AND** no `List`, `Dict`, `Set`, `Tuple` imports remain except in TYPE_CHECKING blocks

#### Scenario: Callables and iterables use collections.abc
- **WHEN** a function parameter or return type uses callable or iterable types
- **THEN** the code imports from `collections.abc` instead of `typing`
- **AND** uses `collections.abc.Callable[[int], str]` instead of `typing.Callable[[int], str]`
- **AND** uses `collections.abc.Iterable[int]` instead of `typing.Iterable[int]`
- **AND** maintains TYPE_CHECKING imports for forward references when needed

#### Scenario: TYPE_CHECKING imports preserved
- **WHEN** forward references are needed for type annotations
- **THEN** `TYPE_CHECKING` imports are preserved and properly structured
- **AND** only necessary imports remain inside TYPE_CHECKING blocks
- **AND** runtime imports are minimized to only what's actually needed

#### Scenario: Complex type annotations remain clear
- **WHEN** complex nested types are used
- **THEN** the migration maintains readability and clarity
- **AND** type aliases are considered for very complex types if needed
- **AND** mypy type checking continues to pass without errors

#### Scenario: Test files follow same patterns
- **WHEN** test files use type annotations
- **THEN** they follow the same modern typing patterns as source code
- **AND** legacy typing imports are removed from test files
- **AND** test type annotations remain consistent with production code