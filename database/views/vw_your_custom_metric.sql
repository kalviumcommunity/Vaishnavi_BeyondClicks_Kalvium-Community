-- View: vw_your_custom_metric (vw_churn_risk_cohorts)
-- Purpose: Identify high-value customers at risk of churning (no orders in 60+ days)
-- Business question answered: Which high-value customers (> $500 total spend) have not placed an order in the last 30 days and are at risk of churning?
-- Updated: Recalculates dynamically with each query
-- Used by: Customer success team for targeted re-engagement campaigns
-- 
-- Columns:
--   customer_id: Unique customer identifier
--   customer_name: Customer display name
--   segment: Customer market segment
--   total_spent: Total lifetime amount spent by the customer
--   last_order_date: Most recent order date
--   days_inactive: Days elapsed since the last order
--   churn_risk: Risk level classification (High, Medium, Low)

CREATE VIEW vw_your_custom_metric AS
SELECT 
    c.customer_id,
    c.customer_name,
    c.segment,
    SUM(o.order_amount) as total_spent,
    MAX(o.order_date) as last_order_date,
    DATEDIFF(CURRENT_DATE, MAX(o.order_date)) as days_inactive,
    CASE 
        WHEN DATEDIFF(CURRENT_DATE, MAX(o.order_date)) > 90 THEN 'High'
        WHEN DATEDIFF(CURRENT_DATE, MAX(o.order_date)) > 60 THEN 'Medium'
        ELSE 'Low'
    END as churn_risk
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
WHERE c.deleted_at IS NULL
GROUP BY c.customer_id, c.customer_name, c.segment
HAVING total_spent > 500.0 AND days_inactive > 30;
