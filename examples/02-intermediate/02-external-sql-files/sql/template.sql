-- Template Report
-- This SQL uses template variables for dynamic reporting

{{sql_comment}}

SELECT
    *
FROM users
WHERE
    signup_date >= '{{start_date}}'::DATE
    AND signup_date <= '{{end_date}}'::DATE
    {% if country_filter %}
    AND country = '{{country_filter}}'
    {% endif %}
ORDER BY signup_date DESC;
