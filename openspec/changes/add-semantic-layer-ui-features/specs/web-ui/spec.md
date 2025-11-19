## ADDED Requirements

### Requirement: Semantic models section in dashboard
When semantic models are defined in the config, the web UI MUST surface them as a first-class section alongside the existing catalog and views list.

#### Scenario: Semantic models listed when present
- **GIVEN** a valid config that defines one or more `semantic_models`
- **WHEN** the user opens the catalog dashboard
- **THEN** the UI shows a semantic models section or tab listing each model by name
- **AND** each entry includes at least the semantic model name and its `base_view`
- **AND** optional labels or descriptions from the config are displayed when available.

#### Scenario: No semantic models panel when absent
- **GIVEN** a valid config that does not define any `semantic_models`
- **WHEN** the user opens the catalog dashboard
- **THEN** the UI does not show a semantic models section
- **OR** shows a minimal “no semantic models configured” message
- **AND** all other dashboard behaviour remains as defined by the existing `web-ui` specification.

### Requirement: Semantic model details view
The web UI MUST allow users to inspect the dimensions and measures of a selected semantic model in a dedicated view or panel.

#### Scenario: Dimensions and measures visible for selected model
- **GIVEN** a config with a semantic model that defines one or more dimensions and measures
- **WHEN** the user selects that semantic model in the dashboard
- **THEN** the UI shows a detail view listing its dimensions and measures
- **AND** each entry includes at least the semantic name and the underlying `column` or `expression`
- **AND** any configured labels or descriptions are displayed to help non-technical users understand the fields.

### Requirement: Semantic labels in data previews
When a semantic model context is active, the web UI MUST prefer semantic labels (where available) for column headings in data previews, while still allowing access to the physical schema when needed.

#### Scenario: Data preview uses semantic labels
- **GIVEN** a semantic model with dimensions and measures that have `label` metadata
- **AND** the dashboard provides a data preview or query result for that model’s `base_view`
- **WHEN** the preview is shown in the context of that semantic model
- **THEN** the column headings in the preview prefer the semantic `label` values where defined
- **AND** the underlying column or expression names remain accessible (for example, via tooltips or secondary text) for users who need to see the physical schema.
