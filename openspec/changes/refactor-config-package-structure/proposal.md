# Refactor: Extract Config into a Package

## Why

The `config.py` module has grown large and multi-purpose, currently handling:

- Pydantic model definitions (core config schema).
- Environment variable interpolation.
- Path resolution orchestration.
- SQL file loading integration.
- Various validation routines and helpers.

This makes it harder to:

- Understand and modify individual responsibilities.
- Test specific behaviors in isolation.
- Avoid incidental coupling between unrelated concerns.

An earlier change (`refactor-consolidate-config-layer`) merged several modules into `config.py` to simplify dependencies. With that consolidation complete and behaviors stable, we now want to split `config.py` into a small internal package, while preserving the existing public API surface (`duckalog.config`).

## What Changes

- **Introduce a `duckalog.config` package**
  - Create `src/duckalog/config/` with:
    - `models.py` – Pydantic models and schema definitions.
    - `loader.py` – `load_config` and `_load_config_from_local_file` implementations.
    - `interpolation.py` – environment variable interpolation logic.
    - `validators.py` – complex validator functions factored out of models.
    - `sql_integration.py` – glue code for SQL file loading and path resolution.
  - Keep `duckalog.config` as the public import surface by:
    - Providing an `__init__.py` that imports and re-exports the existing names (e.g., `Config`, `load_config`, `SecretConfig`).

- **Update internal imports**
  - Adjust internal modules (engine, CLI, remote-config, etc.) to import from the `duckalog.config` package layout instead of a monolithic `config.py`, while preserving module-level import paths for external users.

- **Clarify responsibilities in specs**
  - Update the config spec to describe the logical separation:
    - Models vs loader vs interpolation vs validators vs SQL integration.
  - Document that these are internal organizational boundaries and that the high-level behavior (what `load_config` does) remains unchanged.

## Impact

- **Specs updated**
  - `specs/config/spec.md`:
    - Add a short “Implementation Structure” subsection describing the config package and its responsibilities.
  - `specs/catalog-build/spec.md`:
    - Optionally note that config loading is implemented via `duckalog.config.loader`.

- **Implementation**
  - `src/duckalog/config.py`:
    - Becomes a thin façade or is replaced by `src/duckalog/config/__init__.py` that maintains the existing public API.
  - New modules created under `src/duckalog/config/` as described above.

- **Non-goals**
  - No functional behavior changes to config loading, validation, or SQL generation semantics.
  - No changes to public import paths for consumers (`from duckalog import config` or `from duckalog.config import Config` continue to work).

## Risks and Trade-offs

- Moving code between modules can introduce import cycles if not carefully planned; the design will avoid cross-module imports that create cycles (for example, by centralizing model definitions in `models.py` and having other modules import them, not vice versa).
- Large file diffs may make this change harder to review; breaking work into smaller commits guided by the tasks list will help.

