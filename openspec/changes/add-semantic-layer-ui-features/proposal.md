# Semantic Layer Features in Web UI

## Why
- The semantic layer introduces business-friendly models (dimensions, measures, labels) on top of Duckalog views, but today they are only available as configuration metadata.
- BI and non-technical users primarily interact with the system through the UI, so they benefit most from seeing and using semantic models instead of raw view and column names.
- Surfacing semantic models in the Datastar-powered dashboard makes it easier to understand the catalog, discover metrics, and run analyses without learning the physical schema.

## What Changes
- Extend the Datastar-based web UI so that, when a config includes `semantic_models`, the dashboard:
  - lists available semantic models alongside the existing catalog/views list,
  - shows per-model detail (dimensions, measures, labels, descriptions),
  - and uses semantic names and labels in relevant UI panels (for example, data previews or query helpers) instead of only raw column names.
- Keep the feature additive and safe:
  - when `semantic_models` is absent, the UI behaves as defined in the existing `web-ui` spec with no extra panels,
  - when semantic metadata is present, it is read-only in this change (no semantic editing yet) and used purely for display and discovery.

## Impact
- Dependent on the semantic layer being available in the configuration (`add-semantic-layer-v1`, and optionally `extend-semantic-layer-advanced` when those changes are implemented).
- No changes to catalog build behaviour or DuckDB views; this change only affects what the dashboard displays and how it labels information.
- Modest UI complexity increase: new panels or tabs for semantic models and some wiring to map semantic names back to underlying views/columns for display.

