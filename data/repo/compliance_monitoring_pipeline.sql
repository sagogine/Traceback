-- Compliance Monitoring Pipeline
-- Purpose: Automated compliance monitoring and reporting
-- Owner: data-compliance team
-- SLA: Real-time (<10 seconds)

WITH audit_log_analysis AS (
    SELECT 
        log_id,
        user_id,
        action_type,
        resource_accessed,
        access_time,
        ip_address,
        user_role,
        CASE 
            WHEN action_type = 'UNAUTHORIZED_ACCESS' THEN 'CRITICAL'
            WHEN action_type = 'DATA_EXPORT' AND user_role NOT IN ('ADMIN', 'COMPLIANCE') THEN 'HIGH'
            WHEN access_time NOT BETWEEN '09:00:00' AND '17:00:00' THEN 'MEDIUM'
            ELSE 'LOW'
        END as risk_level
    FROM raw.audit_logs
    WHERE access_time >= CURRENT_DATE - INTERVAL '1 day'
),

data_access_patterns AS (
    SELECT 
        user_id,
        COUNT(*) as total_accesses,
        COUNT(DISTINCT resource_accessed) as unique_resources,
        COUNT(CASE WHEN action_type = 'DATA_EXPORT' THEN 1 END) as export_actions,
        MAX(access_time) as last_access_time
    FROM audit_log_analysis
    GROUP BY user_id
)

SELECT * FROM audit_log_analysis;