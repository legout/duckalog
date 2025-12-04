# Proposal: Add Schema Support to Named Catalog Entities

## Why
Duckalog currently models named entities such as views, attachments, Iceberg catalogs, and semantic models using a single `name` field.
DuckDB, however, supports multi-part identifiers (catalog, schema, name) and users frequently want to address the same logical entity via an explicit schema-qualified name (for example, `my_schema.orders`) instead of relying solely on unqualified names (`orders`).

This proposal introduces **optional schema metadata** for named entities in the Duckalog configuration so that catalogs can be organized into schemas while preserving full backward compatibility for existing configs.

## What Changes
- Extend the catalog configuration schema to allow an optional `schema` field on view definitions.
- Define how Duckalog derives the DuckDB identifier for a view from `(schema, name)` and how this interacts with existing config and SQL generation.
- Extend configuration and semantic-layer specs so that semantic models and other named catalog entities can reference views and other objects that carry schema information.
- Clarify backward compatibility rules so that existing configs without `schema` continue to work unchanged, and unqualified references still resolve correctly.

## Out of Scope
- Changing default DuckDB schemas or catalogs.
- Introducing new attachment types or catalog types.
- Automatic migrations of existing configs to add `schema` fields.
- Any changes to runtime behavior beyond what is necessary to honor the new `schema` metadata in identifier generation and validation.

## Impact
- Users can organize Duckalog-managed objects into DuckDB schemas and reference them as `schema.name`.
- The configuration model remains additive and backward compatible: existing configs with only `name` continue to be valid.
- Semantic-layer metadata can reliably refer to schema-qualified views, reducing ambiguity when multiple views share the same `name` in different schemas.
