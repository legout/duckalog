## MODIFIED Requirements

### Requirement: Catalog Config Format
The catalog configuration MUST support the existing required keys and MAY include an optional top-level `semantic_models` section in addition to them.

#### Scenario: Optional semantic_models section
- **GIVEN** a YAML or JSON config with top-level keys `version`, `duckdb`, `views`, and an optional `semantic_models` array
- **WHEN** the configuration is loaded
- **THEN** it is parsed successfully into the `Config` model
- **AND** the `semantic_models` section is available as a typed collection when present
- **AND** configs that omit `semantic_models` remain valid with no behavioural change to catalog builds.
