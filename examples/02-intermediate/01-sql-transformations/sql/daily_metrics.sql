-- Daily Aggregated Metrics
-- This SQL creates daily aggregated metrics from raw user events

WITH daily_stats AS (
    SELECT
        DATE_TRUNC('day', event_timestamp) AS event_date,
        event_type,
        COUNT(*) AS event_count,
        COUNT(DISTINCT user_id) AS unique_users
    FROM events
    GROUP BY
        DATE_TRUNC('day', event_timestamp),
        event_type
)
SELECT
    event_date,
    event_type,
    event_count,
    unique_users,
    ROUND(event_count::DOUBLE / unique_users, 2) AS events_per_user
FROM daily_stats
ORDER BY event_date DESC, event_count DESC;
