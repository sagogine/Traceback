-- Sales Orders Pipeline
-- Purpose: Transform raw order data into curated sales orders
-- Owner: data-sales team
-- SLA: 2 hours freshness

WITH cleaned_orders AS (
    SELECT 
        order_id,
        customer_id,
        product_id,
        order_date,
        quantity,
        unit_price,
        -- Data quality checks
        CASE 
            WHEN quantity > 0 AND unit_price > 0 THEN quantity * unit_price
            ELSE NULL 
        END AS gross_amount
    FROM raw.sales_orders
    WHERE 
        order_date >= CURRENT_DATE - INTERVAL '30 days'
        AND customer_id IS NOT NULL
        AND product_id IS NOT NULL
),

enriched_orders AS (
    SELECT 
        co.*,
        c.customer_name,
        c.customer_segment,
        p.product_name,
        p.category,
        -- Calculate net amount after refunds
        co.gross_amount - COALESCE(r.refund_amount, 0) AS net_amount
    FROM cleaned_orders co
    LEFT JOIN raw.customers c ON co.customer_id = c.customer_id
    LEFT JOIN raw.products p ON co.product_id = p.product_id
    LEFT JOIN raw.refunds r ON co.order_id = r.order_id
)

INSERT INTO curated.sales_orders
SELECT 
    order_id,
    customer_id,
    customer_name,
    customer_segment,
    product_id,
    product_name,
    category,
    order_date,
    quantity,
    unit_price,
    gross_amount,
    net_amount,
    CURRENT_TIMESTAMP AS processed_at
FROM enriched_orders
WHERE net_amount > 0;  -- Only include valid orders
