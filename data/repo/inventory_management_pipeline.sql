-- Inventory Management Pipeline
-- Purpose: Real-time inventory tracking and reorder management
-- Owner: data-operations team
-- SLA: Real-time (<5 minutes)

WITH current_stock AS (
    SELECT 
        product_id,
        warehouse_id,
        SUM(CASE WHEN transaction_type = 'IN' THEN quantity ELSE -quantity END) as current_quantity,
        MAX(transaction_date) as last_transaction_date
    FROM raw.inventory_transactions
    GROUP BY product_id, warehouse_id
),

stock_levels AS (
    SELECT 
        cs.*,
        p.product_name,
        p.reorder_point,
        p.max_stock_level,
        w.warehouse_name,
        w.location,
        -- Stock level classification
        CASE 
            WHEN cs.current_quantity < 10 THEN 'CRITICAL'
            WHEN cs.current_quantity < p.reorder_point THEN 'LOW'
            WHEN cs.current_quantity > p.max_stock_level THEN 'HIGH'
            ELSE 'NORMAL'
        END as stock_status,
        -- Days of stock remaining
        CASE 
            WHEN cs.current_quantity > 0 THEN 
                cs.current_quantity / NULLIF(daily_demand, 0)
            ELSE 0
        END as days_of_stock
    FROM current_stock cs
    JOIN raw.products p ON cs.product_id = p.product_id
    JOIN raw.warehouse_locations w ON cs.warehouse_id = w.warehouse_id
    LEFT JOIN (
        SELECT 
            product_id,
            AVG(daily_demand) as daily_demand
        FROM raw.demand_forecasts
        WHERE forecast_date >= CURRENT_DATE - INTERVAL '30 days'
        GROUP BY product_id
    ) df ON cs.product_id = df.product_id
),

reorder_recommendations AS (
    SELECT 
        *,
        CASE 
            WHEN stock_status IN ('CRITICAL', 'LOW') THEN 'AUTO_REORDER'
            WHEN stock_status = 'NORMAL' AND days_of_stock < 7 THEN 'MANUAL_REVIEW'
            ELSE 'NO_ACTION'
        END as reorder_action,
        CASE 
            WHEN stock_status IN ('CRITICAL', 'LOW') THEN 
                GREATEST(reorder_point * 2, current_quantity * 3)
            ELSE NULL
        END as suggested_order_quantity
    FROM stock_levels
)

SELECT * FROM reorder_recommendations;