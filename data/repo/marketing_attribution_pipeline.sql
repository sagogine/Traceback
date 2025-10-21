-- Marketing Attribution Pipeline
-- Purpose: Multi-touch attribution modeling for campaign ROI
-- Owner: data-marketing team
-- SLA: Weekly by Monday 9 AM

WITH customer_journey AS (
    SELECT 
        customer_id,
        touchpoint_id,
        touchpoint_date,
        channel,
        campaign_id,
        touchpoint_type,
        ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY touchpoint_date) as touchpoint_sequence,
        COUNT(*) OVER (PARTITION BY customer_id) as total_touchpoints
    FROM raw.marketing_touchpoints
    WHERE touchpoint_date >= CURRENT_DATE - INTERVAL '90 days'
),

conversion_events AS (
    SELECT 
        customer_id,
        conversion_date,
        conversion_value,
        conversion_type
    FROM raw.conversion_events
    WHERE conversion_date >= CURRENT_DATE - INTERVAL '90 days'
),

attribution_models AS (
    SELECT 
        cj.customer_id,
        cj.touchpoint_id,
        cj.channel,
        cj.campaign_id,
        cj.touchpoint_date,
        ce.conversion_value,
        ce.conversion_date,
        -- First Touch Attribution
        CASE WHEN cj.touchpoint_sequence = 1 THEN ce.conversion_value ELSE 0 END as first_touch_credit,
        -- Last Touch Attribution
        CASE WHEN cj.touchpoint_sequence = cj.total_touchpoints THEN ce.conversion_value ELSE 0 END as last_touch_credit,
        -- Linear Attribution
        CASE WHEN ce.conversion_value IS NOT NULL THEN ce.conversion_value / cj.total_touchpoints ELSE 0 END as linear_credit
    FROM customer_journey cj
    LEFT JOIN conversion_events ce ON cj.customer_id = ce.customer_id
)

SELECT * FROM attribution_models;