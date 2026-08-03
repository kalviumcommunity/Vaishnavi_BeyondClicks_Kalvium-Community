-- Task 3: Refactor Query 3 - Use CTEs for Readability
-- Description: Refactors complex nested subqueries into modular, self-contained Common Table Expressions (CTEs).
-- Performance & Maintainability Gain: Enhances code readability, simplifies unit testing of intermediate steps, and aids query planner optimization.

WITH recent_transactions AS (
    -- Step 1: Filter to recent transactions occurring in 2024 or later
    SELECT 
        transaction_id, 
        amount, 
        customer_id
    FROM transactions
    WHERE transaction_date >= '2024-01-01'
),
customer_with_segment AS (
    -- Step 2: Join recent transactions with customer segment metadata
    SELECT 
        rt.transaction_id,
        rt.amount,
        c.customer_segment
    FROM recent_transactions rt
    JOIN customers c ON rt.customer_id = c.id
),
segment_metrics AS (
    -- Step 3: Aggregate metrics by customer segment
    SELECT 
        customer_segment,
        COUNT(DISTINCT transaction_id) AS transaction_count,
        AVG(amount) AS avg_transaction_value,
        SUM(amount) AS total_revenue
    FROM customer_with_segment
    GROUP BY customer_segment
)
-- Final Output: Retrieve segment metrics sorted by highest average transaction value
SELECT 
    customer_segment,
    avg_transaction_value,
    transaction_count,
    total_revenue
FROM segment_metrics
ORDER BY avg_transaction_value DESC;
