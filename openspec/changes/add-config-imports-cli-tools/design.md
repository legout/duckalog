# Design: CLI Tooling for Config Imports

## Goals
- Provide CLI commands that make it easy to inspect and debug imported configurations.
- Build on top of the existing config loader and import-resolution logic without introducing
  new semantics.

## Import Graph Visualization

### Concept
- A command such as `duckalog show-imports <config>` will:
  - Load the specified root configuration path.
  - Resolve imports (local and remote) using the core import mechanisms.
  - Collect an import tree/graph structure showing which file imports which others.

### Output
- Start with a simple, text-based tree representation (for example):
  ```
  config/catalog.yaml
  ├── config/settings.yaml
  ├── views/users.yaml
  └── views/products.yaml
  ```
- Optionally include markers for remote URIs and cycles (if detected).

## Merged Config Preview

### Concept
- Reuse the same logic that `load_config()` uses after imports are resolved and merged.
- Provide a CLI option to output the merged configuration to stdout (or a file), possibly with
  filtering (e.g. only `views`, only `duckdb`).

### Considerations
- Ensure that any printing of configuration respects existing guidance around redacting secrets.
- Keep output deterministic to support tests and CI comparisons.

## Diagnostics

- The same traversal used for the graph can compute:
  - Maximum import depth.
  - Total number of imported files.
  - Locations of duplicate names detected by validation.
- These metrics can be surfaced via flags or additional CLI subcommands.

## Out of Scope
- Changing how imports themselves work; this design assumes `add-config-imports` and its
  extensions are already in place.
- Adding a graphical or web-based visualization (text output only for now).
