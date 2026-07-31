-- Task 5: ORDER BY Ranking
-- Goal: Surface top-performing segments using window ranking functions and limit results.
-- Uses RANK() OVER (...) to rank segment performance based on aggregated revenue.

SELECT 
    c.customer_type,
    c.industry,
    COUNT(DISTINCT t.customer_id) as customers,
    SUM(t.amount) as total_revenue,
    ROUND(AVG(t.amount), 2) as avg_order,
    RANK() OVER (ORDER BY SUM(t.amount) DESC) as revenue_rank
FROM transactions t
JOIN customers c ON t.customer_id = c.customer_id
WHERE t.transaction_date >= DATE '2024-01-01'
GROUP BY c.customer_type, c.industry
HAVING COUNT(DISTINCT t.customer_id) >= 10
ORDER BY total_revenue DESC
LIMIT 20;  -- Top 20 segments
