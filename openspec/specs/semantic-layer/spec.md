# Semantic Layer Specification

## Overview

The semantic layer provides business-friendly metadata on top of existing Duckalog views, allowing users to define dimensions and measures that map to underlying data columns and expressions.

## v1 Requirements

### Scope
- **Metadata only**: No new DuckDB views are created by the engine
- **Single base view**: Each semantic model references exactly one existing view
- **No automatic query generation**: Semantic models are for metadata consumption only
- **No joins**: v1 does not support cross-view relationships

### Core Concepts

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

## Future Extensions (Out of Scope for v1)

- Joins between semantic models
- Time dimension handling
- Default filters
- Automatic query generation
- Hierarchical dimensions
- Calculated measures referencing other measures
- Semantic view creation in DuckDB