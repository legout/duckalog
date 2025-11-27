## ADDED Requirements

### Requirement: Semantic model configuration
The system MUST allow users to define semantic models on top of existing Duckalog views via the catalog configuration file.

#### Scenario: Minimal semantic model over a base view
- **GIVEN** a config whose `views` section defines a view named `fct_sales`
- **AND** a `semantic_models` entry with `name: sales` and `base_view: fct_sales`
- **AND** empty or omitted `dimensions` and `measures`
- **WHEN** the configuration is loaded
- **THEN** the semantic model is parsed into the configuration without error
- **AND** the `base_view` reference is validated to point to an existing view name.

### Requirement: Dimensions and measures metadata
Semantic models MUST support first-class dimension and measure definitions for business-friendly naming and documentation.

#### Scenario: Dimensions mapped to base view expressions
- **GIVEN** a semantic model with `base_view: fct_sales`
- **AND** a `dimensions` list with entries providing at least `name` and `column` (an expression over the base view, such as `order_date` or `customer_id`)
- **WHEN** the configuration is validated
- **THEN** dimensions with non-empty `name` and `column` fields are accepted
- **AND** optional metadata such as `label`, `description`, and `tags` are preserved for later use.

#### Scenario: Measures mapped to base view expressions
- **GIVEN** a semantic model with `base_view: fct_sales`
- **AND** a `measures` list with entries providing at least `name` and `expression` (for example, `SUM(amount)` or `COUNT(DISTINCT order_id)`)
- **WHEN** the configuration is validated
- **THEN** measures with non-empty `name` and `expression` fields are accepted
- **AND** optional metadata such as `label`, `description`, and `format` are preserved for later use.

### Requirement: Semantic model validation and uniqueness
Semantic models MUST be validated for internal consistency and uniqueness within a single config file.

#### Scenario: Duplicate semantic model names rejected
- **GIVEN** a config with two `semantic_models` entries that share the same `name`
- **WHEN** the configuration is validated
- **THEN** validation fails with a clear error indicating that semantic model names must be unique.

#### Scenario: Duplicate dimension or measure names rejected per model
- **GIVEN** a semantic model whose `dimensions` or `measures` list contains multiple entries with the same `name`
- **WHEN** the configuration is validated
- **THEN** validation fails with a clear error indicating that dimension and measure names must be unique within a semantic model.

#### Scenario: Unknown base_view reference rejected
- **GIVEN** a semantic model with `base_view: missing_view`
- **WHEN** the configuration is validated
- **THEN** validation fails with a clear error stating that the referenced `base_view` does not correspond to any entry in `views`.

### Requirement: Metadata-only behaviour in v1
The initial semantic layer MUST NOT change catalog build behaviour or DuckDB views; it is metadata for higher-level tools.

#### Scenario: Catalog build unaffected by semantic_models
- **GIVEN** a valid config with one or more `semantic_models` defined
- **WHEN** a catalog is built using the existing Duckalog CLI or Python API
- **THEN** the set of DuckDB views created in the catalog is determined solely by the `views` section
- **AND** the presence of `semantic_models` does not cause additional views to be created or alter the SQL used for existing ones.

