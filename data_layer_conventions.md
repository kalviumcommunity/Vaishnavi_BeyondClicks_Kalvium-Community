# Clean Data Layer Naming Conventions

This document outlines the database naming conventions applied to establish a unified "single source of truth" and optimize query performance across sales, customer success, and operations dashboards.

## Views

### Prefix
- All views are prefixed with `vw_` to distinguish them from base tables and materialized aggregates.

### Pattern
- `vw_[business_subject]_[metric_definition]`

### Applied Views
1. **`vw_active_customers`**
   - **Business Subject**: Customers
   - **Metric Definition**: Active within a rolling 30-day window (`order_count_30d`, `revenue_30d`, `days_since_order`)
   - **Dashboards Served**: Customer engagement, sales pipeline, retention analysis.
2. **`vw_churn_risk_cohorts`**
   - **Business Subject**: Churn Risk
   - **Metric Definition**: Customers who are historically high-value (> $500 spend) but have been inactive for over 30 days.
   - **Dashboards Served**: Customer success management, re-engagement campaigns.

---

## Pre-Aggregated Tables

### Prefix
- All pre-aggregated summary tables are prefixed with `agg_`.

### Pattern
- `agg_[grain]_[subject]`

### Applied Tables
1. **`agg_daily_metrics`**
   - **Grain**: Daily (`aggregation_date`)
   - **Subject**: Global key metrics (`total_revenue` etc.)
   - **Refreshed**: Periodically (e.g., daily or hourly)

---

## Columns in Aggregated Tables

To ensure transparency, reliability, and auditability:
- **`updated_at`**: Timestamp recording exactly when the aggregation was computed.
- **`row_count`**: Count of the underlying raw rows aggregated. Helps detect data loss or double-counting.
- **Grain Indicators**: Distinct dimension columns specifying the aggregation boundaries (e.g., `aggregation_date`, `metric_name`).

---

## Benefits

1. **Clear Object Classification**: The prefix immediately tells engineers and analysts whether they are querying a base table (`customers`), a live computed metric (`vw_active_customers`), or a cached aggregate (`agg_daily_metrics`).
2. **Prevention of Metric Drift**: By referencing a single view, different dashboards (sales vs. customer success) cannot differ in how they calculate active status or revenue.
3. **Optimized Dashboards**: Streamlit dashboards query the `agg_daily_metrics` table instantly (sub-millisecond execution) instead of scanning millions of records from raw order tables repeatedly.
