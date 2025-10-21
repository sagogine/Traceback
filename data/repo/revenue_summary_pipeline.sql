-- Revenue Summary Pipeline  
-- Purpose: Create daily revenue summaries for reporting
-- Owner: data-sales team
-- Dependencies: curated.sales_orders

WITH daily_revenue AS (
    SELECT 
        DATE(order_date) AS revenue_date,
        customer_segment,
        category,
        COUNT(*) AS order_count,
        SUM(net_amount) AS total_revenue,
        AVG(net_amount) AS avg_order_value,
        SUM(quantity) AS total_quantity
    FROM curated.sales_orders
    WHERE order_date >= CURRENT_DATE - INTERVAL '7 days'
    GROUP BY DATE(order_date), customer_segment, category
),

segment_totals AS (
    SELECT 
        revenue_date,
        customer_segment,
        SUM(total_revenue) AS segment_revenue,
        SUM(order_count) AS segment_orders
    FROM daily_revenue
    GROUP BY revenue_date, customer_segment
)

INSERT INTO curated.revenue_summary
SELECT 
    dr.revenue_date,
    dr.customer_segment,
    dr.category,
    dr.order_count,
    dr.total_revenue,
    dr.avg_order_value,
    dr.total_quantity,
    st.segment_revenue,
    st.segment_orders,
    CURRENT_TIMESTAMP AS processed_at
FROM daily_revenue dr
LEFT JOIN segment_totals st 
    ON dr.revenue_date = st.revenue_date 
    AND dr.customer_segment = st.customer_segment;
