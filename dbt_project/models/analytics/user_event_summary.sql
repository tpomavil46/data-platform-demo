{{ config(materialized='table') }}

SELECT 
    user_id,
    SUM(CASE WHEN event_type = 'click' THEN event_count ELSE 0 END) as total_clicks,
    SUM(CASE WHEN event_type = 'view' THEN event_count ELSE 0 END) as total_views,
    SUM(CASE WHEN event_type = 'purchase' THEN event_count ELSE 0 END) as total_purchases,
    SUM(event_count) as total_events
FROM {{ source('streaming', 'user_events') }}
GROUP BY user_id
ORDER BY total_events DESC