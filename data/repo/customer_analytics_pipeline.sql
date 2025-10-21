-- Customer Analytics Pipeline
-- Purpose: Generate customer behavior analytics
-- Owner: data-analytics team
-- Dependencies: curated.sales_orders, curated.customers

WITH customer_metrics AS (
    SELECT 
        customer_id,
        COUNT(DISTINCT order_date) AS active_days,
        COUNT(*) AS total_orders,
        SUM(net_amount) AS lifetime_value,
        AVG(net_amount) AS avg_order_value,
        MAX(order_date) AS last_order_date,
        MIN(order_date) AS first_order_date
    FROM curated.sales_orders
    WHERE order_date >= CURRENT_DATE - INTERVAL '90 days'
    GROUP BY customer_id
),

customer_segments AS (
    SELECT 
        customer_id,
        CASE 
            WHEN lifetime_value > 1000 THEN 'High Value'
            WHEN lifetime_value > 500 THEN 'Medium Value'
            ELSE 'Low Value'
        END AS value_segment,
        CASE 
            WHEN active_days >= 10 THEN 'Frequent'
            WHEN active_days >= 5 THEN 'Regular'
            ELSE 'Occasional'
        END AS frequency_segment
    FROM customer_metrics
)

INSERT INTO analytics.customer_behavior
SELECT 
    cm.customer_id,
    cm.active_days,
    cm.total_orders,
    cm.lifetime_value,
    cm.avg_order_value,
    cm.last_order_date,
    cm.first_order_date,
    cs.value_segment,
    cs.frequency_segment,
    CURRENT_TIMESTAMP AS processed_at
FROM customer_metrics cm
JOIN customer_segments cs ON cm.customer_id = cs.customer_id;
