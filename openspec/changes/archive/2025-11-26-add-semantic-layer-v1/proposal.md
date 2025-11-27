# Semantic Layer v1 (Metadata over Views)

## Why
- BI and analytics users often think in terms of business entities (Sales, Customers, Revenue) rather than physical DuckDB tables or low-level view names.
- Today, Duckalog captures physical/catalog structure well but has no first-class place to describe business-friendly dimensions and measures on top of existing views.
- A lightweight, config-driven semantic model fits Duckalog’s existing patterns (YAML/JSON + Pydantic) and can be consumed later by the web UI or other tools without introducing a separate semantic service.

## What Changes
- Extend the catalog configuration schema with an optional `semantic_models` section that describes business-level models on top of existing Duckalog views.
- Each semantic model:
  - references a single existing `views[].name` as its `base_view`,
  - defines a set of named dimensions (friendly columns) mapped directly to expressions over that base view,
  - defines a set of named measures (aggregations or expressions) also expressed over the base view,
  - and carries optional metadata such as labels, descriptions, and tags.
- Add Pydantic models and validation rules so that:
  - `semantic_models` are parsed and validated alongside the rest of the config,
  - model names are unique,
  - each `base_view` exists in `views`,
  - and dimension/measure names are unique within a model.
- Keep v1 focused on **metadata only**:
  - no new DuckDB views are created by the engine,
  - no automatic grouping, joins, or query generation is defined yet,
  - the semantic layer is available to Python callers and future UI features as structured metadata.

## Impact
- Backwards compatible: existing configs remain valid because `semantic_models` is optional.
- Small increase in configuration surface and Pydantic complexity, but no behavioural changes to catalog build, SQL generation, or CLI commands in v1.
- Provides a stable foundation for future changes that:
  - use semantic models in the web UI,
  - generate semantic views or queries,
  - and introduce more advanced concepts (joins, time dimensions, default filters) without breaking initial adopters.

