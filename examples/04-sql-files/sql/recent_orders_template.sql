-- Recent orders template
SELECT 
  order_id,
  customer_id,
  order_date,
  total_amount,
  status
FROM orders
WHERE order_date >= CURRENT_DATE - INTERVAL '{{days_back}}' days
  AND status != 'cancelled'
ORDER BY order_date DESC;