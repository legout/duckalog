# Design: Engine Simplification and CatalogBuilder

## Goals

- Decompose the engine into smaller, testable units.
- Keep the public behavior of `build_catalog` and related APIs unchanged.

## CatalogBuilder structure

The `CatalogBuilder` class encapsulates the catalog build workflow:

```python
class CatalogBuilder:
    def __init__(self, config: Config, *, dry_run: bool = False, filesystem=None):
        self.config = config
        self.dry_run = dry_run
        self.filesystem = filesystem
        self.conn = None
        self.temp_paths: list[Path] = []

    def build(self) -> BuildResult:
        try:
            self._create_connection()
            self._apply_pragmas()
            self._install_and_load_extensions()
            self._setup_attachments()
            self._create_secrets()
            self._create_views()
            return self._export_if_needed()
        finally:
            self._cleanup()
```

Each private method has a single responsibility and can be tested independently where practical.

`build_catalog` becomes a thin wrapper:

```python
def build_catalog(config: Config, *, dry_run: bool = False, filesystem=None) -> BuildResult:
    return CatalogBuilder(config, dry_run=dry_run, filesystem=filesystem).build()
```

## Dependency resolution

Config dependency resolution moves from a complex graph structure to a simpler DFS:

- Maintain a `visited` set of resolved config paths.
- For each attachment that points to another config:
  - Resolve its path.
  - Check for cycles using `visited`.
  - Recurse with an incremented depth counter.
- Enforce a maximum depth (configurable, with a sensible default).

Conceptually:

```python
def build_with_dependencies(path: str, *, max_depth: int = 5, _depth: int = 0, _visited: set[str] | None = None):
    ...
```

This design is conceptually aligned with the earlier review suggestions and reduces complexity while preserving behavior.

