-- Task 2: GROUP BY and Aggregation
-- Goal: Group data across multiple dimensions and calculate multiple key aggregate metrics.
-- Note: The WHERE clause filters individual transaction rows BEFORE they are grouped by customer_type and month.

SELECT 
    c.customer_type,
    DATE_TRUNC('month', t.transaction_date)::DATE as month,
    COUNT(DISTINCT t.customer_id) as unique_customers,
    COUNT(*) as transaction_count,
    SUM(t.amount) as monthly_revenue,
    AVG(t.amount) as avg_transaction
FROM transactions t
JOIN customers c ON t.customer_id = c.customer_id
WHERE t.transaction_date >= DATE '2024-01-01'  -- WHERE filters records first (only transactions from 2024-01-01 onward are included in groups)
GROUP BY c.customer_type, DATE_TRUNC('month', t.transaction_date)
ORDER BY month DESC;
