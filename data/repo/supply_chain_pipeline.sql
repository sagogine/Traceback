-- Supply Chain Analytics Pipeline
-- Purpose: End-to-end supply chain optimization and monitoring
-- Owner: data-supply-chain team
-- SLA: Daily by 7 AM

WITH supplier_performance AS (
    SELECT 
        supplier_id,
        supplier_name,
        COUNT(*) as total_orders,
        AVG(delivery_time_days) as avg_delivery_time,
        COUNT(CASE WHEN delivery_date <= promised_date THEN 1 END) / COUNT(*) as on_time_delivery_rate,
        AVG(quality_score) as avg_quality_score,
        SUM(order_value) as total_order_value
    FROM raw.supplier_performance
    WHERE order_date >= CURRENT_DATE - INTERVAL '90 days'
    GROUP BY supplier_id, supplier_name
),

logistics_metrics AS (
    SELECT 
        route_id,
        origin_location,
        destination_location,
        COUNT(*) as total_shipments,
        AVG(transit_time_hours) as avg_transit_time,
        AVG(shipping_cost) as avg_shipping_cost,
        COUNT(CASE WHEN delivery_status = 'ON_TIME' THEN 1 END) / COUNT(*) as delivery_success_rate
    FROM raw.logistics_data
    WHERE shipment_date >= CURRENT_DATE - INTERVAL '30 days'
    GROUP BY route_id, origin_location, destination_location
)

SELECT * FROM supplier_performance;