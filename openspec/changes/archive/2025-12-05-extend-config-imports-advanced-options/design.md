# Design: Advanced Config Import Options

## Goals
- Build on top of the core imports implementation to provide:
  - Section-specific (selective) imports.
  - Explicit override semantics for imported configuration.
  - Glob and exclude patterns for concise multi-file imports.
- Keep behavior predictable and composable with the existing deep-merge and uniqueness rules.

## Selective Imports

### Concept
- Allow imports to target specific sections of the config rather than merging entire files.
- Example shapes (final syntax to be refined in implementation):
  ```yaml
  imports:
    views:
      - ./views/users.yaml
      - ./views/products.yaml
    duckdb:
      - ./config/duckdb-settings.yaml
  ```

### Behavior
- Each section listed under `imports` is merged only into the corresponding top-level key.
- Global `imports` (from the core feature) remain supported and can coexist, but their interaction
  with section-specific imports must be clearly defined in the spec and docs.

## Import Overrides

### Concept
- Add an optional flag (e.g. `override: false`) that controls whether values from an import may
  overwrite values from earlier layers (imports or main file).

### Behavior
- `override: true` (default): behaves as the current deep-merge semantics (last-wins for scalars).
- `override: false`: imported values only fill in missing fields but do not overwrite existing ones.
- Override semantics must be defined per-merge operation and documented clearly to avoid surprises.

## Glob and Exclude Patterns

### Concept
- Support pattern-based imports so that multiple files in a directory can be imported without
  listing each one explicitly.

### Behavior
- Glob expressions (e.g. `./views/*.yaml`) are expanded in a deterministic, platform-independent
  way using standard library helpers.
- Exclude patterns (e.g. `!./views/legacy.yaml`) allow certain matched files to be omitted.
- The resolved list of files is then treated as a sequence of normal imports in the established
  order, so all existing merge and uniqueness rules apply.

## Out of Scope
- Any change to the core semantics of deep merge or uniqueness that `add-config-imports` defines.
- Remote import behavior, which is covered by `extend-config-imports-remote`.
