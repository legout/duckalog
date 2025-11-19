## 1. Requirements & Spec
- [ ] Add `web-ui` spec deltas describing how semantic models appear in the dashboard when present and how the UI behaves when none are defined.
- [ ] Ensure the `web-ui` spec clearly separates semantic model display (this change) from any future semantic editing or automatic query generation.

## 2. UI Behaviour
- [ ] Add a semantic models section to the dashboard that lists each configured semantic model with its name, base view, and optional description.
- [ ] Add a detail view or pane for a selected semantic model showing its dimensions and measures, including labels and descriptions from the config.
- [ ] Use semantic labels (where available) in data preview or query-related panels when a semantic model context is active, while still allowing access to underlying view/column names when needed.
- [ ] Ensure that when `semantic_models` is absent, the dashboard hides semantic-specific UI elements or shows a clear “no semantic models configured” message without errors.

## 3. Documentation & Tests
- [ ] Update web UI documentation to explain the semantic models section, its read-only nature in this change, and how it relates to the underlying views.
- [ ] Add tests or smoke checks that:
  - [ ] verify semantic models are listed when present and omitted when not,
  - [ ] verify dimensions and measures appear correctly in the detail view,
  - [ ] and validate the change with `openspec validate add-semantic-layer-ui-features --strict`.

