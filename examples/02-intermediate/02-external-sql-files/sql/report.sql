-- Customer Report
-- A comprehensive customer report with metrics

SELECT
    u.id AS customer_id,
    u.name,
    u.email,
    u.country,
    u.signup_date,
    COUNT(DISTINCT e.event_id) AS total_events,
    COUNT(DISTINCT CASE WHEN e.event_type = 'purchase' THEN e.event_id END) AS purchases,
    ROUND(AVG(CASE WHEN e.event_type = 'purchase' THEN 1.0 ELSE 0.0 END), 2) AS conversion_rate
FROM users u
LEFT JOIN events e ON u.id = e.user_id
GROUP BY
    u.id,
    u.name,
    u.email,
    u.country,
    u.signup_date
ORDER BY total_events DESC
LIMIT 100;
