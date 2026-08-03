-- Task 2: Refactor Query 2 - Apply Filters Before JOINs
-- Description: Filters the high-cardinality transactions table using a CTE BEFORE performing costly multi-table JOINs.
-- Performance Gain: Minimizes intermediate hash join table size and drastically lowers CPU/memory consumption.

WITH filtered_trans AS (
    -- Pre-filter transactions table on date and amount prior to joining
    SELECT 
        transaction_id, 
        amount, 
        customer_id, 
        product_id, 
        transaction_date
    FROM transactions
    WHERE transaction_date >= '2024-01-01'
      AND amount > 100
)
SELECT 
    ft.transaction_id, 
    ft.amount, 
    c.customer_name, 
    p.product_name
FROM filtered_trans ft
JOIN customers c ON ft.customer_id = c.id
JOIN products p ON ft.product_id = p.id
WHERE c.country = 'USA'
LIMIT 5000;
