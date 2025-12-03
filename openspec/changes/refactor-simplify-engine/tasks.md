## 1. Spec updates
- [x] 1.1 Update `specs/catalog-build/spec.md` with an "Engine Structure" subsection describing `CatalogBuilder`
- [x] 1.2 Document conceptual behavior for dependency resolution (cycles, max depth)

## 2. CatalogBuilder refactor
- [x] 2.1 Introduce `CatalogBuilder` in `engine.py` with clear method boundaries
- [x] 2.2 Refactor `build_catalog` to delegate to `CatalogBuilder`
- [x] 2.3 Ensure temporary file and resource cleanup is handled in one place (for example, a `cleanup` method or context manager)

## 3. Dependency resolution simplification
- [x] 3.1 Replace or simplify existing dependency-graph logic with a DFS-based approach
- [x] 3.2 Add tests for simple trees, diamonds, and cycle detection (hierarchical functionality tests added)
- [x] 3.3 Preserve existing semantics for attachment hierarchies and max depth

## 4. Testing and verification
- [x] 4.1 Run full test suite and confirm behavior is unchanged
- [x] 4.2 Add targeted tests around `CatalogBuilder` if gaps are found

