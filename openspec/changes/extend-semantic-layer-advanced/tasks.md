## 1. Requirements & Spec
- [ ] Add `semantic-layer` spec deltas that describe v2 fields (`joins`, dimension `type`, `time_grains`, and `defaults`) and how they are validated.
- [ ] Clearly document that the new metadata is additive and does not yet imply automatic query generation or materialized semantic views.

## 2. Schema & Validation
- [ ] Extend the semantic model Pydantic types to include:
  - [ ] optional `joins` entries referencing other view names and join conditions,
  - [ ] optional dimension `type` and `time_grains`,
  - [ ] an optional `defaults` block with fields like `time_dimension` and `primary_measure`.
- [ ] Implement validation rules to ensure:
  - [ ] `joins[].to_view` references existing view names,
  - [ ] join `type` values are limited to a supported set (for example, `inner`, `left`),
  - [ ] `defaults.time_dimension` and `defaults.primary_measure` refer to defined dimensions/measures in the same model.

## 3. Documentation & Tests
- [ ] Update docs with an advanced semantic model example showing joins to a dimension view, a time dimension with grains, and a primary measure.
- [ ] Add tests that cover valid and invalid combinations of `joins`, dimension types, time grains, and defaults.
- [ ] Validate the updated change with `openspec validate extend-semantic-layer-advanced --strict`.

