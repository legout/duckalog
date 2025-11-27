# Semantic Layer Specification

## Purpose

The semantic layer provides business-friendly metadata on top of existing Duckalog views, allowing users to define dimensions and measures that map to underlying data columns and expressions. This enables business intelligence tools and analytics applications to work with intuitive, business-oriented concepts rather than raw technical SQL queries.
## Requirements
### Requirement: Define business-friendly semantic models
Users SHALL be able to define semantic models that wrap existing Duckalog views with business metadata.

#### Scenario: Create basic semantic model
- **WHEN** a user defines a semantic model with a name, base view, dimensions, and measures
- **THEN** the system SHALL validate that the base view exists and the semantic model is properly structured
- **AND** all dimensions and measures SHALL have unique names within the model

### Requirement: Support dimensions and measures
Users SHALL be able to define dimensions and measures with business-friendly names and expressions.

#### Scenario: Define dimension with expression
- **WHEN** a user defines a dimension with a name and SQL expression
- **THEN** the system SHALL validate that the expression is non-empty
- **AND** optional metadata like label, description, and type SHALL be stored

#### Scenario: Define measure with aggregation
- **WHEN** a user defines a measure with a name and aggregation expression
- **THEN** the system SHALL validate that the expression is non-empty
- **AND** optional metadata like label, description, and type SHALL be stored

### Requirement: Enforce uniqueness and reference validation
The system SHALL validate that all names are unique and references are correct.

#### Scenario: Validate name uniqueness
- **WHEN** loading semantic models
- **THEN** semantic model names SHALL be unique across all models
- **AND** dimension and measure names SHALL be unique within each model
- **AND** dimension and measure names SHALL not conflict within the same model

#### Scenario: Validate base view references
- **WHEN** a semantic model references a base view
- **THEN** the system SHALL ensure the view exists in the configuration
- **AND** SHALL raise a clear error if the view is missing

### Requirement: Support time dimensions with grains (v2)
Users SHALL be able to define time dimensions with supported time grains for drill-down operations.

#### Scenario: Define time dimension with grains
- **WHEN** a user defines a dimension with type "time" and time_grains
- **THEN** the system SHALL validate that all time_grains are from the supported set
- **AND** SHALL ensure time_grains are only specified for dimensions with type "time"

### Requirement: Support joins between views (v2)
Users SHALL be able to join semantic models to other views for enriched analytics.

#### Scenario: Define joins to dimension views
- **WHEN** a user defines joins with to_view, type, and on_condition
- **THEN** the system SHALL validate that to_view references an existing view
- **AND** SHALL validate that join type is one of: inner, left, right, full
- **AND** SHALL ensure the on_condition is a valid SQL expression

### Requirement: Support default configurations (v2)
Users SHALL be able to specify default settings for query builders and dashboards.

#### Scenario: Define default time dimension and measure
- **WHEN** a user specifies defaults with time_dimension and primary_measure
- **THEN** the system SHALL validate that these reference existing dimensions/measures in the same model
- **AND** SHALL ensure default time dimensions have type "time"

#### Scenario: Define default filters
- **WHEN** a user specifies default_filters
- **THEN** the system SHALL validate that filter dimensions exist in the model
- **AND** SHALL store the filter configuration for consumption by BI tools

### Requirement: Maintain backward compatibility (v2)
All v1 semantic models SHALL continue to work without changes.

#### Scenario: Load v1 semantic model with v2 schema
- **WHEN** loading a v1 semantic model (without joins, time_grains, or defaults)
- **THEN** the system SHALL accept the model without errors
- **AND** SHALL treat missing v2 fields as empty/unspecified
- **AND** SHALL apply all existing v1 validation rules

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

### Requirement: Metadata-only behaviour in v1
The initial semantic layer MUST NOT change catalog build behaviour or DuckDB views; it is metadata for higher-level tools.

#### Scenario: Catalog build unaffected by semantic_models
- **GIVEN** a valid config with one or more `semantic_models` defined
- **WHEN** a catalog is built using the existing Duckalog CLI or Python API
- **THEN** the set of DuckDB views created in the catalog is determined solely by the `views` section
- **AND** the presence of `semantic_models` does not cause additional views to be created or alter the SQL used for existing ones.

## v1 Scope

**Metadata only**: No new DuckDB views are created by the engine
**Single base view**: Each semantic model references exactly one existing view
**No automatic query generation**: Semantic models are for metadata consumption only
**No joins**: v1 does not support cross-view relationships

## Core Concepts

#### Semantic Model
A business entity that wraps an existing Duckalog view with friendly metadata.

**Required fields:**
- `name`: Unique identifier for the semantic model
- `base_view`: Name of an existing view in `views[]`
- `dimensions`: Set of named dimensions (optional)
- `measures`: Set of named measures (optional)

**Optional metadata:**
- `label`: Human-readable display name
- `description`: Detailed description
- `tags`: List of classification tags

#### Dimension
A business attribute that maps to an expression over the base view.

**Required fields:**
- `name`: Unique name within the semantic model
- `expression`: SQL expression referencing columns from the base view

**Optional metadata:**
- `label`: Human-readable display name
- `description`: Detailed description
- `type`: Data type hint (string, number, date, etc.)

#### Measure
A business metric that typically involves aggregation or calculation over the base view.

**Required fields:**
- `name`: Unique name within the semantic model
- `expression`: SQL expression (often aggregated) over the base view

**Optional metadata:**
- `label`: Human-readable display name
- `description`: Detailed description
- `type`: Data type hint (string, number, date, etc.)

### Validation Rules

1. **Semantic model names must be unique** across all semantic models
2. **Base view must exist** in the `views` section
3. **Dimension names must be unique** within a semantic model
4. **Measure names must be unique** within a semantic model
5. **Dimension and measure names cannot conflict** within the same semantic model

### Configuration Structure

```yaml
semantic_models:
  - name: sales
    base_view: sales_data
    label: "Sales Analysis"
    description: "Business metrics for sales analysis"
    tags: ["sales", "revenue"]
    dimensions:
      - name: order_date
        expression: "created_at::date"
        label: "Order Date"
        type: "date"
      - name: customer_region
        expression: "UPPER(customer_region)"
        label: "Customer Region"
        type: "string"
    measures:
      - name: total_revenue
        expression: "SUM(amount)"
        label: "Total Revenue"
        type: "number"
      - name: order_count
        expression: "COUNT(*)"
        label: "Order Count"
        type: "number"
```

## v2 Extensions

### New Features
- **Joins**: Optional joins to other views (typically dimensions)
- **Enhanced Dimensions**: Dimension type information and time grains
- **Defaults**: Default time dimension, primary measure, and default filters

### v2 Schema Extensions

#### Join
A relationship to another view for enriching the semantic model.

**Required fields:**
- `to_view`: Name of an existing view in `views[]`
- `type`: Join type (inner, left, right, full)
- `on_condition`: SQL join condition

**Example:**
```yaml
joins:
  - to_view: customers
    type: left
    on_condition: "sales.customer_id = customers.id"
```

#### Enhanced Dimension Types
Dimensions support enhanced type information and time grains.

**New dimension types:**
- `time`: Time dimensions with optional time grains
- `number`: Numeric dimensions
- `string`: Text dimensions
- `boolean`: Boolean dimensions
- `date`: Date dimensions

**Time grains (for time dimensions only):**
- `year`, `quarter`, `month`, `week`, `day`, `hour`, `minute`, `second`

**Example:**
```yaml
dimensions:
  - name: order_date
    expression: "created_at"
    type: "time"
    time_grains: ["year", "quarter", "month", "day"]
  - name: customer_region
    expression: "UPPER(customer_region)"
    type: "string"
```

#### Defaults
Default configuration for query builders and dashboards.

**Optional fields:**
- `time_dimension`: Default time dimension name (must reference a defined dimension)
- `primary_measure`: Default primary measure name (must reference a defined measure)
- `default_filters`: Optional list of default filters

**Example:**
```yaml
defaults:
  time_dimension: order_date
  primary_measure: total_revenue
  default_filters:
    - dimension: order_date
      operator: ">="
      value: "2024-01-01"
```

### v2 Validation Rules

**Join validation:**
1. `joins[].to_view` must reference an existing view in `views[]`
2. Join `type` must be one of: `inner`, `left`, `right`, `full`
3. `on_condition` must be a valid SQL expression

**Dimension validation:**
1. If `time_grains` is specified, dimension `type` must be `time`
2. `time_grains` values must be from the supported set

**Defaults validation:**
1. `defaults.time_dimension` must reference a defined dimension in the same model
2. `defaults.primary_measure` must reference a defined measure in the same model
3. `defaults.default_filters` must reference valid dimensions

### Backward Compatibility

All v2 features are **additive and optional**:
- Existing v1 semantic models remain valid without changes
- New fields (`joins`, enhanced `time_grains`, `defaults`) default to empty/unspecified
- No breaking changes to existing validation rules

### Configuration Structure (v2)

```yaml
semantic_models:
  - name: sales
    base_view: sales_data
    label: "Sales Analysis"
    description: "Business metrics for sales analysis"
    tags: ["sales", "revenue"]

    # v2: Optional joins to dimension views
    joins:
      - to_view: customers
        type: left
        on_condition: "sales.customer_id = customers.id"
      - to_view: products
        type: left
        on_condition: "sales.product_id = products.id"

    dimensions:
      - name: order_date
        expression: "created_at"
        type: "time"
        time_grains: ["year", "quarter", "month", "day"]
        label: "Order Date"
      - name: customer_region
        expression: "customers.region"
        type: "string"
        label: "Customer Region"
      - name: product_category
        expression: "products.category"
        type: "string"
        label: "Product Category"

    measures:
      - name: total_revenue
        expression: "SUM(sales.amount)"
        label: "Total Revenue"
        type: "number"
      - name: order_count
        expression: "COUNT(DISTINCT sales.id)"
        label: "Order Count"
        type: "number"

    # v2: Default configuration
    defaults:
      time_dimension: order_date
      primary_measure: total_revenue
      default_filters:
        - dimension: customer_region
          operator: "="
          value: "NORTH AMERICA"
```

## Future Extensions (Out of Scope for v2)

- Automatic query generation from semantic models
- Hierarchical dimensions
- Calculated measures referencing other measures
- Semantic view creation in DuckDB
- Advanced join handling (multi-way joins, join chaining)
- Time series operations and calculations