# Semantic Layer v2 (Joins, Time Dimensions, Defaults)

## Why
- Once semantic models exist as metadata over a single base view, users quickly need richer semantics to support realistic BI use cases.
- Common requirements include:
  - joining facts to dimensions via declared relationships,
  - declaring time dimensions and supported time grains,
  - and specifying default measures and filters to drive query builders and dashboards.
- Adding these concepts as a second, explicit iteration keeps v1 simple while giving a clear path to more expressive semantic models.

## What Changes
- Extend the `semantic_models` schema to support:
  - optional `joins` to other views (typically dimensions), including join type and join condition,
  - dimension `type` information (for example, `time`, `number`, `string`) and optional `time_grains` for time dimensions,
  - a `defaults` section per model (for example, `time_dimension`, `primary_measure`, and optional default filters).
- Keep this change focused on modelling and metadata:
  - no automatic query generation or grouping logic is mandated yet,
  - but the additional metadata is structured so future changes can compile it into SQL or power the web UI.

## Impact
- Backwards compatible with v1: all existing `semantic_models` remain valid; the new fields are optional and additive.
- Slightly richer configuration and validation in the `semantic-layer` capability, with no change to catalog build or existing views.
- Provides a more complete semantic description for consumers such as:
  - the planned Datastar web UI,
  - future query-building helpers or APIs,
  - or external tools that want to introspect Duckalog semantic models.

