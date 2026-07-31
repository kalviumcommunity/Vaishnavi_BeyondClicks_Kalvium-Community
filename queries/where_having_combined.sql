-- Task 4: WHERE + HAVING Combined
-- Goal: Real-world query combining row-level data quality filters (WHERE) and group-level business threshold filters (HAVING).
-- Business Logic:
-- 1. WHERE: Ensure input transactions are valid (2024+, completed status, positive amount > 0).
-- 2. GROUP BY: Aggregate metrics by customer_type segment.
-- 3. HAVING: Filter out small/insignificant customer segments (requires >= 100 unique customers AND > $100,000 segment revenue).

SELECT 
    c.customer_type,
    COUNT(DISTINCT t.customer_id) as segment_customers,
    SUM(t.amount) as segment_revenue,
    ROUND(AVG(t.amount), 2) as avg_order_value
FROM transactions t
JOIN customers c ON t.customer_id = c.customer_id
WHERE t.transaction_date >= DATE '2024-01-01'      -- WHERE: Date range validity filter
  AND t.transaction_status = 'completed'           -- WHERE: Data quality filter (completed orders only)
  AND t.amount > 0                                 -- WHERE: Logical validity filter (remove refunds/zero-value rows)
GROUP BY c.customer_type
HAVING COUNT(DISTINCT t.customer_id) >= 100       -- HAVING: Minimum customer segment size threshold
  AND SUM(t.amount) > 100000                       -- HAVING: Business revenue threshold filter
ORDER BY segment_revenue DESC;
