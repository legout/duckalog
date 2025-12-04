# Design: Schema Support for Named Catalog Entities

## Goals
- Allow views (and related named entities) in Duckalog configs to declare an optional `schema` alongside `name`.
- Ensure DuckDB identifiers are consistently derived from `(schema, name)` without breaking existing catalogs.
- Enable semantic-layer references (for example, `base_view`, `joins.to_view`) to work with schema-qualified views.

## Non-Goals
- Changing DuckDB's default schema behaviour.
- Introducing global schema configuration beyond what is needed to support per-entity `schema`.

## Identifier Model
- Each view definition will optionally include a `schema` field.
- The canonical DuckDB identifier for a view will be derived as:
  - `"name"` when `schema` is omitted (current behaviour).
  - `"schema"."name"` when `schema` is provided.
- Uniqueness and reference resolution will use `(schema, name)` as the logical key, with `schema = <default>` when omitted.

## Backward Compatibility
- Existing configs that only specify `name` remain valid; their effective `schema` is treated as the default DuckDB schema.
- Existing semantic models that reference views by unqualified `base_view` continue to work when the referenced view has no `schema`.
- When `schema` is added to a view, semantic-layer references may either:
  - Continue to use the unqualified `name` if the view remains unique by name across schemas, or
  - Use a schema-qualified reference (exact rules to be captured in the spec deltas).

## Open Questions
- Should attachment and Iceberg catalog aliases also grow an optional `schema` field, or should schema be limited to views in the first iteration?
- How should conflicts be handled when the same `name` exists in multiple schemas but semantic-layer references remain unqualified?
- Do we need additional CLI options or diagnostics to surface schema-qualified view names to users?
