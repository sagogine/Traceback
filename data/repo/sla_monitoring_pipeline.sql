-- SLA Monitoring Pipeline
-- Purpose: Track SLA compliance across all pipelines
-- Owner: data-platform team
-- SLA: Daily reporting

WITH pipeline_performance AS (
    SELECT 
        pipeline_id,
        pipeline_name,
        execution_date,
        start_time,
        end_time,
        CASE 
            WHEN end_time IS NULL THEN NULL
            ELSE EXTRACT(EPOCH FROM (end_time - start_time)) / 3600
        END as execution_hours,
        status,
        sla_hours
    FROM raw.pipeline_executions
    WHERE execution_date >= CURRENT_DATE - INTERVAL '7 days'
),

sla_compliance AS (
    SELECT 
        pipeline_id,
        pipeline_name,
        COUNT(*) as total_executions,
        COUNT(CASE WHEN status = 'SUCCESS' THEN 1 END) as successful_executions,
        COUNT(CASE WHEN execution_hours <= sla_hours THEN 1 END) as sla_compliant_executions,
        AVG(execution_hours) as avg_execution_time,
        sla_hours
    FROM pipeline_performance
    WHERE execution_hours IS NOT NULL
    GROUP BY pipeline_id, pipeline_name, sla_hours
)

SELECT * FROM sla_compliance;