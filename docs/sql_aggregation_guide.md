# SQL Aggregation, WHERE vs HAVING, and Ranking Guide

This guide details the core SQL aggregation concepts implemented across Tasks 1 to 5 in the `BeyondClicks` analytics platform.

---

## 1. Task 1: WHERE Filtering (Data Quality)

### Concept
`WHERE` filters individual rows **BEFORE** grouping or aggregation takes place. It is used to enforce data quality and clean raw data prior to calculating summaries.

### Requirements & Documentation
```sql
SELECT 
    customer_id,
    SUM(amount) as annual_revenue,
    COUNT(*) as transaction_count
FROM transactions
WHERE transaction_date >= DATE '2024-01-01'  -- Restricts date range to active reporting window
  AND amount > 0                              -- Removes negative refunds and non-revenue transactions
  AND transaction_status = 'completed'        -- Filters for valid, completed orders only
GROUP BY customer_id
ORDER BY annual_revenue DESC;
```

---

## 2. Task 2: GROUP BY and Aggregation

### Concept
`GROUP BY` collapses multiple rows into summary rows based on 2 or more grouping dimensions (`customer_type`, `month`). Aggregate functions calculate metrics across those collapsed rows.

### Query Structure
```sql
SELECT 
    c.customer_type,
    DATE_TRUNC('month', t.transaction_date)::DATE as month,
    COUNT(DISTINCT t.customer_id) as unique_customers,
    COUNT(*) as transaction_count,
    SUM(t.amount) as monthly_revenue,
    AVG(t.amount) as avg_transaction
FROM transactions t
JOIN customers c ON t.customer_id = c.customer_id
WHERE t.transaction_date >= DATE '2024-01-01'  -- WHERE filters rows before grouping
GROUP BY c.customer_type, DATE_TRUNC('month', t.transaction_date)
ORDER BY month DESC;
```

---

## 3. Task 3: HAVING Filtering

### Concept & Difference from WHERE
- **WHERE**: Evaluates predicate logic on individual rows before `GROUP BY`. Cannot contain aggregate functions (`SUM`, `COUNT`).
- **HAVING**: Evaluates predicate logic on aggregated groups **AFTER** `GROUP BY`. Must be used when filtering based on aggregate metrics.

### Query Structure
```sql
SELECT 
    customer_id,
    COUNT(*) as transaction_count,
    SUM(amount) as annual_revenue
FROM transactions
WHERE transaction_date >= DATE '2024-01-01'
GROUP BY customer_id
HAVING SUM(amount) > 10000                      -- Filters groups where total revenue > $10,000
  AND COUNT(*) >= 5                             -- Filters groups with at least 5 completed transactions
ORDER BY annual_revenue DESC;
```

---

## 4. Task 4: WHERE + HAVING Combined

### Concept
Real-world SQL queries combine `WHERE` and `HAVING` to achieve two distinct goals:
1. **WHERE**: Clean raw row-level data (data quality & logical validity).
2. **HAVING**: Filter meaningful aggregate segments (business thresholds & segment size).

### Query Structure
```sql
SELECT 
    c.customer_type,
    COUNT(DISTINCT t.customer_id) as segment_customers,
    SUM(t.amount) as segment_revenue,
    ROUND(AVG(t.amount), 2) as avg_order_value
FROM transactions t
JOIN customers c ON t.customer_id = c.customer_id
WHERE t.transaction_date >= DATE '2024-01-01'      -- WHERE: row filter
  AND t.transaction_status = 'completed'           -- WHERE: data quality
  AND t.amount > 0                                 -- WHERE: logical validity
GROUP BY c.customer_type
HAVING COUNT(DISTINCT t.customer_id) >= 100       -- HAVING: segment size threshold
  AND SUM(t.amount) > 100000                       -- HAVING: revenue threshold
ORDER BY segment_revenue DESC;
```

---

## 5. Task 5: ORDER BY Ranking

### Concept
Calculates segment ranking across multi-dimensional groupings using SQL window functions (`RANK() OVER (...)`).

### Query Structure
```sql
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
LIMIT 20;
```
