# Time-Series Analytics Examples

This example demonstrates advanced time-series analytics patterns using Duckalog, including moving averages, trend analysis, growth rate calculations, forecasting, and seasonality detection.

## Business Context

Time-series analysis is crucial for understanding patterns over time and making data-driven predictions. This example shows how to:

- Analyze sales trends and seasonal patterns
- Calculate growth rates and compound annual growth rates (CAGR)
- Implement moving averages for smoothing volatile data
- Detect seasonality and cyclical patterns
- Create simple forecasts based on historical trends
- Perform period-over-period analysis (MoM, YoY, WoW)

## Use Cases

- **Retail Analytics**: Analyze sales patterns, seasonal demand, and inventory planning
- **Financial Services**: Track market trends, revenue growth, and performance metrics
- **Web Analytics**: Monitor user engagement, traffic patterns, and conversion rates
- **Manufacturing**: Analyze production metrics, quality trends, and operational KPIs

## Key Features

- **Moving Averages**: Simple, exponential, and weighted moving averages for trend smoothing
- **Growth Analysis**: Month-over-month, quarter-over-quarter, and year-over-year growth rates
- **Seasonality Detection**: Identify seasonal patterns and cyclical trends
- **Trend Analysis**: Linear regression and polynomial trend fitting
- **Forecasting**: Simple exponential smoothing and trend-based forecasts
- **Period Comparisons**: Customizable period-over-period analysis

## Configuration Overview

This example uses time-series sales and operational data:

```yaml
# Daily sales data with multiple dimensions
daily_sales:
  type: parquet
  path: data/daily_sales.parquet

# Website traffic and engagement metrics
web_analytics:
  type: parquet
  path: data/web_analytics.parquet

# Product performance over time
product_metrics:
  type: parquet
  path: data/product_metrics.parquet

# Operational KPIs and performance indicators
operational_metrics:
  type: parquet
  path: data/operational_metrics.parquet
```

## Views and Metrics

### Moving Averages
- 7-day, 30-day, and 90-day simple moving averages
- Exponential moving averages with different smoothing factors
- Weighted moving averages for trend emphasis

### Growth Analysis
- Month-over-month (MoM) growth rates
- Quarter-over-quarter (QoQ) growth rates
- Year-over-year (YoY) growth rates
- Compound annual growth rate (CAGR) calculations

### Seasonality Detection
- Seasonal decomposition using moving averages
- Month-over-month seasonal indices
- Quarterly and annual seasonal patterns
- Heatmap visualization of seasonal patterns

### Trend Analysis
- Linear trend fitting using regression
- Polynomial trend fitting for complex patterns
- Trend strength and significance testing
- Acceleration/deceleration analysis

### Forecasting
- Simple exponential smoothing (SES)
- Holt's linear trend method
- Seasonal decomposition-based forecasting
- Confidence intervals for predictions

## Data Model

### Daily Sales Schema
```sql
daily_sales:
- date (date): Date of the sales record
- product_id (string): Unique product identifier
- category (string): Product category
- sales_amount (decimal): Total sales amount
- units_sold (integer): Number of units sold
- region (string): Sales region
- promotion_flag (boolean): Whether promotion was active
```

### Web Analytics Schema
```sql
web_analytics:
- date (date): Date of analytics record
- sessions (integer): Number of sessions
- pageviews (integer): Number of page views
- unique_visitors (integer): Number of unique visitors
- bounce_rate (decimal): Website bounce rate
- avg_session_duration (decimal): Average session duration
- conversion_rate (decimal): Conversion rate
```

## Performance Considerations

- **Large Time-Series**: Efficient window function usage for moving averages
- **Complex Calculations**: Optimized SQL for seasonal decomposition
- **Memory Usage**: Streaming calculations for very large datasets
- **Query Performance**: Materialized views for frequently accessed calculations

## Usage Examples

### Basic Moving Average Analysis
```sql
-- View 30-day moving average for sales
SELECT
    date,
    sales_amount,
    moving_avg_30d,
    (sales_amount - moving_avg_30d) / moving_avg_30d * 100 as deviation_pct
FROM sales_moving_averages
WHERE date >= '2023-01-01'
ORDER BY date;
```

### Seasonal Pattern Analysis
```sql
-- View seasonal indices by month
SELECT
    month,
    avg_sales,
    seasonal_index,
   CASE
        WHEN seasonal_index > 1.1 THEN 'Peak Season'
        WHEN seasonal_index < 0.9 THEN 'Off Season'
        ELSE 'Normal'
    END as season_type
FROM sales_seasonal_patterns
ORDER BY month;
```

### Growth Rate Analysis
```sql
-- View YoY growth rates
SELECT
    DATE_TRUNC('year', date) as year,
    SUM(sales_amount) as annual_sales,
    LAG(SUM(sales_amount), 1) OVER (ORDER BY DATE_TRUNC('year', date)) as prev_year_sales,
    (SUM(sales_amount) - LAG(SUM(sales_amount), 1) OVER (ORDER BY DATE_TRUNC('year', date))) /
    LAG(SUM(sales_amount), 1) OVER (ORDER BY DATE_TRUNC('year', date)) * 100 as yoy_growth_pct
FROM daily_sales
GROUP BY DATE_TRUNC('year', date)
ORDER BY year;
```

## Technical Details

### Window Functions
- Optimized window frame specifications for performance
- Proper handling of NULL values and missing data
- Efficient calculations for large time windows

### Statistical Methods
- Standardized approaches for seasonal decomposition
- Proper handling of outliers and anomalies
- Validation and accuracy metrics for forecasts

### Data Preprocessing
- Automatic date handling and validation
- Handling of missing time periods
- Data quality checks and anomaly detection

## Related Examples

- [Customer Analytics](/business-intelligence/customer-analytics/) - Customer behavior over time
- [Multi-Source Analytics](/data-integration/multi-source-analytics/) - Complex data integration patterns
- [Production Operations](/production-operations/) - Performance monitoring

## Contributing

When contributing to this example:

1. Follow the established [contribution guidelines](/CONTRIBUTING.md)
2. Test changes with the provided validation script
3. Update documentation for any new analytical methods
4. Ensure data generation scripts produce realistic time-series patterns