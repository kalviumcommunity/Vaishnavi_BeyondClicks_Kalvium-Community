-- Task 1: WHERE Filtering
-- Goal: Filter data quality issues BEFORE grouping / aggregation.
-- WHERE operates on individual rows prior to any aggregation taking place.

SELECT 
    customer_id,
    SUM(amount) as annual_revenue,
    COUNT(*) as transaction_count
FROM transactions
WHERE transaction_date >= DATE '2024-01-01'  -- Date range filter: restricts calculation to relevant time window (2024 onwards)
  AND amount > 0                              -- Remove refunds/negative amounts: ensures revenue calculations reflect net positive sales only
  AND transaction_status = 'completed'        -- Valid transactions only: filters out pending, failed, or cancelled transactions
GROUP BY customer_id
ORDER BY annual_revenue DESC;
