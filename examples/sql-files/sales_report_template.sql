-- Sales Report Template
-- This template demonstrates Duckalog's template variable substitution feature
-- Variables can be provided via sql_template.variables in the configuration

WITH sales_data AS (
  SELECT
    s.sale_id,
    s.sale_date,
    s.amount,
    s.quantity,
    s.product_id,
    s.customer_id,
    p.product_name,
    p.category as product_category,
    p.brand,
    c.name as customer_name,
    c.email as customer_email,
    c.segment as customer_segment,
    c.country as customer_country,
    c.created_at as customer_since
  FROM sales s
  JOIN products p ON s.product_id = p.product_id
  JOIN customers c ON s.customer_id = c.customer_id
  WHERE s.sale_date BETWEEN '{{ start_date }}' AND '{{ end_date }}'
    AND s.amount >= {{ min_amount }}
    AND c.segment = '${env:CUSTOMER_SEGMENT}'
    AND c.country = '${env:CUSTOMER_COUNTRY}'
),

daily_metrics AS (
  SELECT
    DATE_TRUNC('{{ time_period }}', sale_date) as period_start,
    DATE(sale_date) as sale_date,
    COUNT(*) as total_transactions,
    COUNT(DISTINCT customer_id) as unique_customers,
    COUNT(DISTINCT product_id) as unique_products,
    SUM(amount) as total_revenue,
    SUM(quantity) as total_units_sold,
    AVG(amount) as avg_transaction_value,
    AVG(quantity) as avg_units_per_transaction,
    SUM(CASE WHEN amount >= {{ high_value_threshold }} THEN 1 ELSE 0 END) as high_value_transactions
  FROM sales_data
  GROUP BY DATE_TRUNC('{{ time_period }}', sale_date), DATE(sale_date)
),

product_performance AS (
  SELECT
    p.product_id,
    p.product_name,
    p.category,
    p.brand,
    COUNT(s.sale_id) as transaction_count,
    SUM(s.amount) as total_revenue,
    SUM(s.quantity) as units_sold,
    AVG(s.amount) as avg_transaction_value,
    MIN(s.amount) as min_sale_amount,
    MAX(s.amount) as max_sale_amount
  FROM products p
  LEFT JOIN sales_data s ON p.product_id = s.product_id
  GROUP BY p.product_id, p.product_name, p.category, p.brand
  HAVING COUNT(s.sale_id) > 0
  ORDER BY total_revenue DESC
),

customer_insights AS (
  SELECT
    c.customer_id,
    c.name as customer_name,
    c.segment,
    c.country,
    COUNT(s.sale_id) as total_purchases,
    SUM(s.amount) as lifetime_value,
    AVG(s.amount) as avg_purchase_value,
    MIN(s.sale_date) as first_purchase_date,
    MAX(s.sale_date) as last_purchase_date,
    DATE_PART('day', MAX(s.sale_date) - MIN(s.sale_date)) as customer_lifespan_days
  FROM customers c
  LEFT JOIN sales_data s ON c.customer_id = s.customer_id
  GROUP BY c.customer_id, c.name, c.segment, c.country
  HAVING COUNT(s.sale_id) > 0
  ORDER BY lifetime_value DESC
)

SELECT
  'Daily Summary' as report_section,
  d.period_start,
  d.sale_date,
  NULL as product_name,
  NULL as customer_name,
  d.total_transactions,
  d.unique_customers,
  d.unique_products,
  d.total_revenue,
  d.total_units_sold,
  d.avg_transaction_value,
  d.avg_units_per_transaction,
  d.high_value_transactions
FROM daily_metrics d

UNION ALL

SELECT
  'Product Performance' as report_section,
  NULL as period_start,
  NULL as sale_date,
  p.product_name,
  NULL as customer_name,
  p.transaction_count,
  NULL as unique_customers,
  NULL as unique_products,
  p.total_revenue,
  p.units_sold as total_units_sold,
  p.avg_transaction_value,
  NULL as avg_units_per_transaction,
  NULL as high_value_transactions
FROM product_performance p
WHERE p.total_revenue >= {{ product_revenue_threshold }}

UNION ALL

SELECT
  'Top Customers' as report_section,
  NULL as period_start,
  NULL as sale_date,
  NULL as product_name,
  c.customer_name,
  c.total_purchases,
  NULL as unique_customers,
  NULL as unique_products,
  c.lifetime_value,
  NULL as total_units_sold,
  c.avg_purchase_value,
  NULL as avg_units_per_transaction,
  NULL as high_value_transactions
FROM customer_insights c
WHERE c.lifetime_value >= {{ customer_ltv_threshold }}

ORDER BY
  report_section,
  CASE WHEN report_section = 'Daily Summary' THEN period_start END DESC,
  CASE WHEN report_section = 'Product Performance' THEN total_revenue END DESC,
  CASE WHEN report_section = 'Top Customers' THEN lifetime_value END DESC

-- Template Variables:
-- Configuration Variables (from sql_template.variables):
--   {{ start_date }} - Starting date for the report period (e.g., '2023-01-01')
--   {{ end_date }} - Ending date for the report period (e.g., '2023-12-31')
--   {{ min_amount }} - Minimum transaction amount to include (e.g., 10.00)
--   {{ time_period }} - Time grouping for daily metrics (day, week, month)
--   {{ high_value_threshold }} - Amount threshold for high-value transactions (e.g., 100.00)
--   {{ product_revenue_threshold }} - Minimum revenue to include product in report (e.g., 1000.00)
--   {{ customer_ltv_threshold }} - Minimum customer lifetime value (e.g., 500.00)
--
-- Environment Variables (from system environment):
--   CUSTOMER_SEGMENT - Customer segment to filter by (e.g., 'enterprise', 'smb')
--   CUSTOMER_COUNTRY - Country to filter customers by (e.g., 'US', 'DE', 'UK')
--
-- Usage Example in Duckalog config:
-- views:
--   - name: quarterly_sales_report
--     source: postgres
--     database: sales_db
--     sql_template:
--       path: "sales_report_template.sql"
--       variables:
--         start_date: "2023-01-01"
--         end_date: "2023-12-31"
--         min_amount: 25.00
--         time_period: "month"
--         high_value_threshold: 150.00
--         product_revenue_threshold: 5000.00
--         customer_ltv_threshold: 1000.00
--     description: "Comprehensive quarterly sales report with template variables"
--
-- This template demonstrates:
-- - Complex multi-section reporting with UNION ALL
-- - Common Table Expressions (CTEs) for organized queries
-- - Date/time functions and truncations
-- - Conditional aggregations
-- - Environment-aware filtering
-- - Parameterized thresholds and dates
-- - Realistic business analytics patterns
