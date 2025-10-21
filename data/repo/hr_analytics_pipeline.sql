-- HR Analytics Pipeline
-- Purpose: Employee lifecycle analytics and talent management
-- Owner: data-hr team
-- SLA: Monthly by 5th of month

WITH employee_metrics AS (
    SELECT 
        employee_id,
        department,
        job_title,
        hire_date,
        CURRENT_DATE - hire_date as tenure_days,
        salary,
        manager_id,
        AVG(performance_score) as avg_performance_score,
        COUNT(*) as total_reviews
    FROM raw.employee_data ed
    LEFT JOIN raw.performance_reviews pr ON ed.employee_id = pr.employee_id
    WHERE ed.status = 'ACTIVE'
    GROUP BY employee_id, department, job_title, hire_date, salary, manager_id
),

attendance_analysis AS (
    SELECT 
        employee_id,
        COUNT(*) as total_days_worked,
        SUM(CASE WHEN attendance_status = 'PRESENT' THEN 1 ELSE 0 END) as days_present,
        SUM(CASE WHEN attendance_status = 'ABSENT' THEN 1 ELSE 0 END) as days_absent,
        AVG(hours_worked) as avg_hours_per_day
    FROM raw.attendance_data
    WHERE attendance_date >= CURRENT_DATE - INTERVAL '30 days'
    GROUP BY employee_id
)

SELECT * FROM employee_metrics;