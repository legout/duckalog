## 1. Requirements & Spec
- [x] Add a `semantic-layer` specification with v1 requirements for semantic model structure, validation, and scope (metadata-only, single base view).
- [x] Add a `config` spec delta to document the new optional `semantic_models` section at the top level of the catalog configuration.

## 2. Schema & Validation
- [x] Introduce Pydantic models for semantic models, dimensions, and measures, and wire them into the main `Config` model.
- [x] Implement validation rules to enforce:
  - [x] unique semantic model names,
  - [x] `base_view` references an existing view name,
  - [x] dimension and measure names are unique within a semantic model.

## 3. Python API & Docs
- [x] Ensure semantic models are accessible from the loaded `Config` object (and, if needed, via light Python helper functions).
- [x] Update README / docs to describe the `semantic_models` section with a minimal example and clearly state v1's limitations (no joins, no automatic query generation).
- [x] Add tests covering config parsing, validation, and Python access for semantic models, and validate the change with `openspec validate add-semantic-layer-v1 --strict`.

