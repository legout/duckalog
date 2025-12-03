# Refactor: Simplify Engine and Catalog Build Orchestration

## Why

The engine layer currently contains complex functions responsible for:

- Config dependency resolution and cycle detection.
- DuckDB connection creation and configuration.
- Attachment setup (DuckDB, SQLite, Postgres, etc.).
- Secret creation.
- View creation and export handling.

Key routines like `build_catalog` and `build_config_with_dependencies` have grown large and multi-responsibility, making them harder to:

- Understand and modify safely.
- Test in isolation.
- Extend with new behaviors (for example, additional attachment types).

We want to refactor the engine into smaller, focused components without changing observable behavior.

## What Changes

- **Introduce a `CatalogBuilder` orchestration class**
  - Encapsulate the catalog build workflow in a class with methods for:
    - Connection creation and configuration.
    - Extension installation and loading.
    - Attachment setup.
    - Secret creation.
    - View creation and optional export.
    - Cleanup of temporary resources.
  - Keep the existing `build_catalog` function as a thin wrapper around `CatalogBuilder`.

- **Simplify config dependency resolution**
  - Replace complex dependency-graph logic with a simpler depth-limited DFS approach that:
    - Tracks visited config paths to detect cycles.
    - Enforces a maximum depth to avoid runaway recursion.
  - Ensure existing behaviors (for example, attachment hierarchy semantics) are preserved.

- **Clarify error handling and logging within the engine**
  - Align error handling with the `refactor-simplify-exceptions` change (shared exception hierarchy, consistent logging).
  - Reduce silent fallbacks and make failure modes explicit.

## Impact

- **Specs updated**
  - `specs/catalog-build/spec.md`:
    - Add an “Engine Structure” subsection describing `CatalogBuilder` and high-level responsibilities.
    - Clarify how dependency resolution works conceptually (cycles, max depth).

- **Implementation**
  - `src/duckalog/engine.py`:
    - Introduce `CatalogBuilder` and refactor existing functions to use it.
    - Simplify or replace `ConfigDependencyGraph` with a clearer structure.

- **Non-goals**
  - No change to the user-facing Python API or CLI shape.
  - No change to the semantics of what gets built; only internal structure and error handling are refactored.

## Risks and Trade-offs

- Refactoring core orchestration code carries some regression risk; this is mitigated by:
  - Relying on the existing test suite.
  - Adding focused tests for dependency resolution and orchestrated build steps as needed.

