## 1. Requirements & Spec
- [x] Add `semantic-layer` spec deltas that describe v2 fields (`joins`, dimension `type`, `time_grains`, and `defaults`) and how they are validated.
- [x] Clearly document that the new metadata is additive and does not yet imply automatic query generation or materialized semantic views.

## 2. Schema & Validation
- [x] Extend the semantic model Pydantic types to include:
  - [x] optional `joins` entries referencing other view names and join conditions,
  - [x] optional dimension `type` and `time_grains`,
  - [x] an optional `defaults` block with fields like `time_dimension` and `primary_measure`.
- [x] Implement validation rules to ensure:
  - [x] `joins[].to_view` references existing view names,
  - [x] join `type` values are limited to a supported set (for example, `inner`, `left`),
  - [x] `defaults.time_dimension` and `defaults.primary_measure` refer to defined dimensions/measures in the same model.

## 3. Documentation & Tests
- [x] Update docs with an advanced semantic model example showing joins to a dimension view, a time dimension with grains, and a primary measure.
- [x] Add tests that cover valid and invalid combinations of `joins`, dimension types, time grains, and defaults.
- [x] Validate the updated change with `openspec validate extend-semantic-layer-advanced --strict`.

