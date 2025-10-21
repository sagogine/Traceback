-- Escalation Monitoring Pipeline
-- Purpose: Track incident escalation patterns and response times
-- Owner: data-platform team
-- SLA: Real-time monitoring

WITH incident_timeline AS (
    SELECT 
        incident_id,
        incident_type,
        severity_level,
        created_time,
        acknowledged_time,
        resolved_time,
        CASE 
            WHEN acknowledged_time IS NOT NULL THEN 
                EXTRACT(EPOCH FROM (acknowledged_time - created_time)) / 60
            ELSE NULL
        END as acknowledgment_minutes,
        CASE 
            WHEN resolved_time IS NOT NULL THEN 
                EXTRACT(EPOCH FROM (resolved_time - created_time)) / 60
            ELSE NULL
        END as resolution_minutes
    FROM raw.incident_logs
    WHERE created_time >= CURRENT_DATE - INTERVAL '30 days'
),

escalation_analysis AS (
    SELECT 
        severity_level,
        COUNT(*) as total_incidents,
        AVG(acknowledgment_minutes) as avg_acknowledgment_time,
        AVG(resolution_minutes) as avg_resolution_time,
        COUNT(CASE WHEN acknowledgment_minutes > 30 THEN 1 END) as late_acknowledgments,
        COUNT(CASE WHEN resolution_minutes > 240 THEN 1 END) as late_resolutions
    FROM incident_timeline
    WHERE acknowledgment_minutes IS NOT NULL
    GROUP BY severity_level
)

SELECT * FROM escalation_analysis;