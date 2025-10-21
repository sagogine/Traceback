-- Product Analytics Pipeline
-- Purpose: Comprehensive product usage analytics and user experience
-- Owner: data-product team
-- SLA: Real-time (<1 minute)

WITH user_interactions AS (
    SELECT 
        user_id,
        session_id,
        interaction_date,
        feature_name,
        interaction_type,
        duration_seconds,
        COUNT(*) OVER (PARTITION BY session_id) as session_length,
        SUM(duration_seconds) OVER (PARTITION BY session_id) as total_session_duration
    FROM raw.user_interactions
    WHERE interaction_date >= CURRENT_DATE - INTERVAL '7 days'
),

feature_usage AS (
    SELECT 
        feature_name,
        COUNT(DISTINCT user_id) as unique_users,
        COUNT(*) as total_interactions,
        AVG(duration_seconds) as avg_duration,
        COUNT(DISTINCT session_id) as unique_sessions,
        COUNT(DISTINCT CASE WHEN interaction_date >= CURRENT_DATE - INTERVAL '1 day' THEN user_id END) as daily_active_users,
        COUNT(DISTINCT CASE WHEN interaction_date >= CURRENT_DATE - INTERVAL '7 days' THEN user_id END) as weekly_active_users
    FROM user_interactions
    GROUP BY feature_name
)

SELECT * FROM feature_usage;