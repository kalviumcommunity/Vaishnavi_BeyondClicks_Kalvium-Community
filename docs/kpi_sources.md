# Beyond Clicks KPI Sources

## 1. Total Revenue

- **Business Question:** How much revenue was generated this month?
- **Source:** `data/raw/orders.csv`
- **Column:** `amount`
- **Calculation:** Sum of all order amounts for the current month.
- **Comparison:** Compared with the previous month.
- **Status Logic:** Increase is good, decrease is bad.

## 2. Active Users

- **Business Question:** How many customers were active this month?
- **Source:** `data/raw/orders.csv`
- **Column:** `customer_id`
- **Calculation:** Count of unique customers placing orders during the month.
- **Comparison:** Compared with the previous month.
- **Status Logic:** Increase is good, decrease is bad.

## 3. Average Order Value

- **Business Question:** What is the average value of each order?
- **Source:** `data/raw/orders.csv`
- **Column:** `amount`
- **Calculation:** Mean order amount for the month.
- **Comparison:** Compared with the previous month.
- **Status Logic:** Increase is good, decrease is bad.

## 4. Churn Rate

- **Business Question:** What percentage of customers were lost?
- **Source:** Not directly available in the current dataset.
- **Reason:** The dataset does not contain a customer status, cancellation, subscription, or churn field.
- **Implementation:** Marked as unavailable rather than hardcoding a value.
- **Future Requirement:** Add customer lifecycle/status data to calculate churn accurately.

## 5. Customer Satisfaction

- **Business Question:** How satisfied are customers?
- **Source:** Not available in the current dataset.
- **Reason:** There is no customer rating or satisfaction column.
- **Implementation:** Marked as unavailable rather than hardcoding a value.
- **Future Requirement:** Add customer survey/rating data.

# Data Validation

All available KPI calculations are generated dynamically from the Beyond Clicks dataset.

No KPI values are hardcoded.

The comparison period is calculated automatically from the latest date available in the dataset.