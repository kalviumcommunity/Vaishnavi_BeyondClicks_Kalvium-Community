-- Task 3: HAVING Filtering
-- Goal: Filter aggregated customer GROUPS after grouping and calculation.
-- Distinction: WHERE filters individual rows BEFORE aggregation; HAVING filters entire groups AFTER aggregation.
-- Use WHERE for row-level quality checks (e.g. date boundaries); use HAVING when criteria depend on aggregate functions (e.g. SUM, COUNT).

SELECT 
    customer_id,
    COUNT(*) as transaction_count,
    SUM(amount) as annual_revenue
FROM transactions
WHERE transaction_date >= DATE '2024-01-01'     -- WHERE filters rows before aggregation
GROUP BY customer_id
HAVING SUM(amount) > 10000                      -- HAVING filters groups after aggregation (revenue threshold > $10k)
  AND COUNT(*) >= 5                             -- HAVING filters groups based on transaction count (minimum 5 purchases)
ORDER BY annual_revenue DESC;
