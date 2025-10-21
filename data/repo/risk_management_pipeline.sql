-- Risk Management Pipeline
-- Purpose: Comprehensive risk assessment and monitoring
-- Owner: data-risk team
-- SLA: Real-time (<30 seconds)

WITH transaction_risk AS (
    SELECT 
        transaction_id,
        customer_id,
        transaction_amount,
        transaction_date,
        transaction_type,
        CASE 
            WHEN transaction_amount > 100000 THEN 0.8
            WHEN transaction_amount > 50000 THEN 0.6
            WHEN transaction_amount > 10000 THEN 0.4
            ELSE 0.2
        END as amount_risk_score,
        CASE 
            WHEN transaction_type IN ('WIRE_TRANSFER', 'CASH_WITHDRAWAL') THEN 0.7
            WHEN transaction_type IN ('ONLINE_PAYMENT', 'CARD_PAYMENT') THEN 0.3
            ELSE 0.1
        END as type_risk_score
    FROM raw.transaction_data
    WHERE transaction_date >= CURRENT_DATE - INTERVAL '1 day'
),

customer_risk_profiles AS (
    SELECT 
        customer_id,
        customer_type,
        credit_score,
        account_age_days,
        CASE 
            WHEN credit_score < 600 THEN 0.9
            WHEN credit_score < 700 THEN 0.6
            WHEN credit_score < 800 THEN 0.3
            ELSE 0.1
        END as credit_risk_score
    FROM raw.customer_data
)

SELECT * FROM transaction_risk;