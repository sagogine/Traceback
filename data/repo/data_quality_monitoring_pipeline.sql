-- Data Quality Monitoring Pipeline
-- Purpose: Automated data quality checks and monitoring
-- Owner: data-quality team
-- SLA: Hourly checks

WITH quality_checks AS (
    SELECT 
        table_name,
        check_type,
        check_date,
        total_records,
        failed_records,
        CASE 
            WHEN total_records > 0 THEN failed_records / total_records
            ELSE 0
        END as failure_rate,
        CASE 
            WHEN failed_records / total_records > 0.01 THEN 'CRITICAL'
            WHEN failed_records / total_records > 0.001 THEN 'HIGH'
            WHEN failed_records / total_records > 0.0001 THEN 'MEDIUM'
            ELSE 'LOW'
        END as quality_status
    FROM raw.data_quality_results
    WHERE check_date >= CURRENT_DATE - INTERVAL '1 day'
),

quality_summary AS (
    SELECT 
        table_name,
        COUNT(*) as total_checks,
        COUNT(CASE WHEN quality_status = 'CRITICAL' THEN 1 END) as critical_issues,
        COUNT(CASE WHEN quality_status = 'HIGH' THEN 1 END) as high_issues,
        AVG(failure_rate) as avg_failure_rate
    FROM quality_checks
    GROUP BY table_name
)

SELECT * FROM quality_summary;