-- Financial Reporting Pipeline
-- Purpose: Comprehensive financial data processing for compliance
-- Owner: data-finance team
-- SLA: Daily by 8 AM

WITH daily_transactions AS (
    SELECT 
        transaction_id,
        account_id,
        transaction_date,
        transaction_type,
        amount,
        description,
        reference_number,
        -- Financial controls
        CASE 
            WHEN amount = 0 THEN 'ZERO_AMOUNT'
            WHEN ABS(amount) > 1000000 THEN 'LARGE_TRANSACTION'
            WHEN transaction_type NOT IN ('DEBIT', 'CREDIT') THEN 'INVALID_TYPE'
            ELSE 'VALID'
        END as validation_status
    FROM raw.general_ledger
    WHERE transaction_date = CURRENT_DATE - INTERVAL '1 day'
),

account_balances AS (
    SELECT 
        account_id,
        SUM(CASE WHEN transaction_type = 'CREDIT' THEN amount ELSE -amount END) as current_balance,
        COUNT(*) as transaction_count,
        SUM(ABS(amount)) as total_activity
    FROM daily_transactions
    WHERE validation_status = 'VALID'
    GROUP BY account_id
),

reconciliation_summary AS (
    SELECT 
        'BANK_RECONCILIATION' as reconciliation_type,
        COUNT(*) as total_transactions,
        SUM(amount) as net_amount,
        COUNT(CASE WHEN validation_status != 'VALID' THEN 1 END) as validation_errors,
        CURRENT_DATE - INTERVAL '1 day' as reconciliation_date
    FROM daily_transactions
    WHERE account_id LIKE 'BANK_%'
)

SELECT * FROM reconciliation_summary;