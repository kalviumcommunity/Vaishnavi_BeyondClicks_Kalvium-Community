-- Table: agg_daily_metrics
-- Purpose: Pre-aggregated daily metrics summary table for faster dashboard queries
-- Business metric: Daily total revenue and order volume
-- Updated: Periodically (hourly or daily) via batch jobs
-- Used by: Executive KPIs dashboard, sales performance analytics
--
-- Columns:
--   aggregation_date: Date of the aggregated metrics
--   metric_name: Name of the business metric (e.g. 'total_revenue')
--   metric_value: Numeric value of the metric
--   row_count: Count of order rows aggregated for validation
--   updated_at: Timestamp when aggregation was computed

CREATE TABLE agg_daily_metrics (
    aggregation_date DATE,
    metric_name VARCHAR(100),
    metric_value NUMERIC,
    row_count INTEGER,
    updated_at TIMESTAMP
);

-- Aggregation Query to Populate Table
INSERT INTO agg_daily_metrics
SELECT 
    DATE(o.order_date) as aggregation_date,
    'total_revenue' as metric_name,
    SUM(o.order_amount) as metric_value,
    COUNT(*) as row_count,
    CURRENT_TIMESTAMP as updated_at
FROM orders o
GROUP BY DATE(o.order_date);
