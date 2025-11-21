# Semantic Layer v2 Example

This example demonstrates the new semantic layer v2 features including joins, time dimensions with time grains, and default configurations.

## Features Demonstrated

### 1. Joins Between Views
The `sales_analytics` semantic model joins the base `sales_orders` view with `customers` and `products` dimension views to provide enriched analytics:

```yaml
joins:
  - to_view: customers
    type: left
    on_condition: "sales_orders.customer_id = customers.id"
  - to_view: products
    type: left
    on_condition: "sales_orders.product_id = products.id"
```

### 2. Time Dimensions with Time Grains
The `order_date` dimension is typed as "time" with supported time grains for drill-down operations:

```yaml
- name: order_date
  expression: "sales_orders.order_date"
  type: "time"
  time_grains: ["year", "quarter", "month", "week", "day"]
```

### 3. Default Configuration
The semantic model includes default settings that can be used by query builders and dashboards:

```yaml
defaults:
  time_dimension: order_date
  primary_measure: total_revenue
  default_filters:
    - dimension: order_date
      operator: ">="
      value: "2024-01-01"
      description: "Show data from 2024 onwards"
```

## Usage

### Load and Validate Configuration
```bash
duckalog validate examples/semantic_layer_v2/catalog.yaml
```

### Generate SQL
```bash
duckalog generate-sql examples/semantic_layer_v2/catalog.yaml
```

### Build Catalog
```bash
duckalog build examples/semantic_layer_v2/catalog.yaml --output sales_analytics.duckdb
```

## Semantic Models

### Sales Analytics
- **Base View**: `sales_orders`
- **Joins**: `customers`, `products`
- **Time Dimension**: `order_date` with drill-down support
- **Primary Measure**: `total_revenue`
- **Default Filters**: Orders from 2024 onwards, exclude unknown regions

### Customer Analytics
- **Base View**: `customers`
- **Focus**: Customer demographics and segmentation
- **Primary Measure**: `customer_count`
- **No Joins**: Standalone customer analytics

## Key Benefits

1. **Enriched Data**: Joins allow semantic models to combine data from multiple views
2. **Time Intelligence**: Time dimensions with grains support drill-down and roll-up operations
3. **Better UX**: Default configurations provide sensible starting points for BI tools
4. **Backward Compatibility**: All v1 semantic models continue to work unchanged
5. **Metadata-Only**: No automatic query generation required; metadata can be consumed by external tools

## Validation Rules

The semantic layer enforces comprehensive validation:

- **Join Validation**: All joined views must exist and join types must be valid
- **Time Grain Validation**: Time grains can only be specified for time dimensions
- **Default Validation**: Default dimensions/measures must exist in the same model
- **Type Safety**: Dimension types and time grains are validated against supported values

This example shows how semantic layer v2 provides a richer, more expressive way to model business intelligence scenarios while maintaining backward compatibility with existing v1 configurations.