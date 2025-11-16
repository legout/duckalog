-- User Summary Query
-- This is a simple SQL file that can be referenced in Duckalog configurations
-- using the sql_file or sql_template fields

SELECT
  u.user_id,
  u.name,
  u.email,
  u.created_at::DATE as signup_date,
  u.region,
  u.segment,
  COUNT(DISTINCT e.event_id) as total_events,
  COUNT(DISTINCT DATE(e.timestamp)) as active_days,
  MAX(e.timestamp) as last_activity,
  MIN(e.timestamp) as first_activity,
  COUNT(CASE WHEN e.event_type = 'purchase' THEN 1 END) as purchase_events,
  SUM(CASE WHEN e.event_type = 'purchase' THEN e.value ELSE 0 END) as total_purchase_value
FROM users u
LEFT JOIN events e ON u.user_id = e.user_id
WHERE u.created_at >= CURRENT_DATE - INTERVAL 90 DAYS
GROUP BY
  u.user_id,
  u.name,
  u.email,
  u.created_at,
  u.region,
  u.segment
ORDER BY total_events DESC, last_activity DESC

-- This query demonstrates:
-- - Multiple aggregations
-- - Date truncation and calculations
-- - Conditional aggregation with CASE statements
-- - JOIN operations
-- - Time-based filtering
-- - Proper ordering for analytics results
