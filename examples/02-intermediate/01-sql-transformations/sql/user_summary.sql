-- User Summary Statistics
-- This SQL creates a comprehensive user summary with activity metrics

WITH user_activity AS (
    SELECT
        u.id,
        u.name,
        u.email,
        u.country,
        u.signup_date,
        u.is_active,
        COUNT(e.event_id) AS total_events,
        COUNT(CASE WHEN e.event_type = 'purchase' THEN 1 END) AS purchase_count,
        MAX(e.event_timestamp) AS last_activity
    FROM users u
    LEFT JOIN events e ON u.id = e.user_id
    GROUP BY
        u.id,
        u.name,
        u.email,
        u.country,
        u.signup_date,
        u.is_active
)
SELECT
    id,
    name,
    email,
    country,
    signup_date,
    is_active,
    total_events,
    COALESCE(purchase_count, 0) AS purchase_count,
    CASE
        WHEN last_activity IS NULL THEN 'Never'
        WHEN last_activity >= CURRENT_DATE - INTERVAL '7 days' THEN 'Active (7d)'
        WHEN last_activity >= CURRENT_DATE - INTERVAL '30 days' THEN 'Recent (30d)'
        ELSE 'Inactive'
    END AS activity_status
FROM user_activity
ORDER BY total_events DESC NULLS LAST;
