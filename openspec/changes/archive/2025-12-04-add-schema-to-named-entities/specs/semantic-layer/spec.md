## MODIFIED Requirements

### Requirement: Semantic model configuration
Semantic models MUST be able to declare optional joins to other configured views so relationships between facts and dimensions are described in configuration.

#### Scenario: Semantic model with joins to other views (no schema)
- **GIVEN** a config where `views` includes `fct_sales` and `dim_customers` without `schema`
- **AND** a semantic model named `sales` with `base_view: fct_sales`
- **AND** a `joins` list containing an entry with `to_view: dim_customers`, a supported join `type` (for example, `left`), and a non-empty `on` join condition
- **WHEN** the configuration is validated
- **THEN** the join entry is accepted
- **AND** validation confirms that `to_view` matches an existing view identifier.

#### Scenario: Semantic model references schema-qualified base view
- **GIVEN** a config where `views` includes a view with `name: fct_sales` and `schema: analytics`
- **AND** a semantic model named `sales` with `base_view` referencing the same identifier (for example, `analytics.fct_sales` or an equivalent `(schema, name)` reference as defined by the implementation)
- **WHEN** the configuration is validated
- **THEN** the semantic model is accepted
- **AND** validation confirms that `base_view` resolves unambiguously to the existing view.

#### Scenario: Semantic model joins schema-qualified dimension view
- **GIVEN** a config where `views` includes `fct_sales` and `dim_customers` and at least one of these views specifies a `schema`
- **AND** a semantic model named `sales` with `base_view` pointing to `fct_sales`
- **AND** a `joins` list containing an entry whose `to_view` references the schema-qualified identifier for `dim_customers`
- **WHEN** the configuration is validated
- **THEN** the join entry is accepted
- **AND** validation confirms that `to_view` resolves unambiguously to an existing view.

#### Scenario: Conflicting view names across schemas
- **GIVEN** a config where two views share the same `name` but different `schema` values
- **AND** a semantic model whose `base_view` or `joins.to_view` uses an unqualified view name
- **WHEN** the configuration is validated
- **THEN** validation SHALL fail with a clear error indicating that the reference is ambiguous
- **AND** the error message SHALL instruct the user to use a schema-qualified identifier.
