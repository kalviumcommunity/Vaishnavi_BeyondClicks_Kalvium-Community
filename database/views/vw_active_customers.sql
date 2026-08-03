-- View: vw_active_customers
-- Purpose: Identify customers with recent activity (last 30 days)
-- Business metric: Customers active in rolling 30-day window
-- Updated: Automatically with each query (view recalculates)
-- Used by: Customer engagement dashboard, retention analysis
-- 
-- Columns:
--   customer_id: Unique customer identifier
--   customer_name: Customer display name
--   segment: Customer segment classification
--   order_count_30d: Number of orders in last 30 days
--   revenue_30d: Total revenue from last 30 days
--   last_order_date: Most recent order date
--   days_since_order: Days elapsed since last order

CREATE VIEW vw_active_customers AS
SELECT 
    c.customer_id,
    c.customer_name,
    c.segment,
    COUNT(DISTINCT o.order_id) as order_count_30d,
    SUM(o.order_amount) as revenue_30d,
    MAX(o.order_date) as last_order_date,
    DATEDIFF(CURRENT_DATE, MAX(o.order_date)) as days_since_order
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
    AND o.order_date >= CURRENT_DATE - INTERVAL 30 DAY
WHERE c.deleted_at IS NULL
GROUP BY c.customer_id, c.customer_name, c.segment;
