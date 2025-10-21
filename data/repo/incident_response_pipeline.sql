-- Incident Response Pipeline
-- Purpose: Automated incident detection and response
-- Owner: data-platform team
-- SLA: Real-time monitoring

WITH incident_detection AS (
    SELECT 
        pipeline_id,
        pipeline_name,
        failure_time,
        error_message,
        severity_level,
        CASE 
            WHEN error_message LIKE '%CRITICAL%' THEN 'P0'
            WHEN error_message LIKE '%HIGH%' THEN 'P1'
            WHEN error_message LIKE '%MEDIUM%' THEN 'P2'
            ELSE 'P3'
        END as incident_severity
    FROM raw.pipeline_logs
    WHERE failure_time >= CURRENT_DATE - INTERVAL '1 day'
        AND status = 'FAILED'
),

impact_assessment AS (
    SELECT 
        id.pipeline_id,
        id.pipeline_name,
        id.incident_severity,
        COUNT(DISTINCT ld.downstream_table) as affected_downstream_tables,
        COUNT(DISTINCT ld.dashboard_id) as affected_dashboards
    FROM incident_detection id
    LEFT JOIN raw.lineage_dependencies ld ON id.pipeline_id = ld.source_pipeline
    GROUP BY id.pipeline_id, id.pipeline_name, id.incident_severity
)

SELECT * FROM impact_assessment;