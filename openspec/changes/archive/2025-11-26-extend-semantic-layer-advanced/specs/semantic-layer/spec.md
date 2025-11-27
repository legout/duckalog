## MODIFIED Requirements

### Requirement: Semantic model configuration
Semantic models MUST be able to declare optional joins to other configured views so relationships between facts and dimensions are described in configuration.

#### Scenario: Semantic model with joins to other views
- **GIVEN** a config where `views` includes `fct_sales` and `dim_customers`
- **AND** a semantic model named `sales` with `base_view: fct_sales`
- **AND** a `joins` list containing an entry with `to_view: dim_customers`, a supported join `type` (for example, `left`), and a non-empty `on` join condition
- **WHEN** the configuration is validated
- **THEN** the join entry is accepted
- **AND** validation confirms that `to_view` matches an existing view name
- **AND** unsupported join types or missing `on` conditions are rejected with clear errors.

### Requirement: Dimensions and measures metadata
Dimensions in semantic models MAY declare a type (such as `time`) and, for time dimensions, the system MUST support configuring valid time grains.

#### Scenario: Dimension types and time grains
- **GIVEN** a semantic model with one or more dimensions
- **AND** some dimensions declare `type: time` and a list of `time_grains` (for example, `day`, `month`)
- **WHEN** the configuration is validated
- **THEN** recognized dimension types and time grains are accepted
- **AND** unsupported types or invalid grain values are rejected with clear errors
- **AND** non-time dimensions MAY omit `time_grains` without error.

### Requirement: Semantic model validation and uniqueness
Semantic models MUST validate that any default fields reference existing dimensions and measures within the same model.

#### Scenario: Defaults reference existing fields
- **GIVEN** a semantic model that defines `dimensions` and `measures`
- **AND** a `defaults` block with `time_dimension` and `primary_measure` fields
- **WHEN** the configuration is validated
- **THEN** validation confirms that `defaults.time_dimension` refers to a defined dimension name in the same model
- **AND** `defaults.primary_measure` refers to a defined measure name in the same model
- **AND** unknown references cause validation to fail with a clear error.
