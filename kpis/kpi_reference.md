# KPI Reference Document

This reference document defines key performance indicators (KPIs) used across product, growth, finance, and engineering teams to track user engagement, monetization, retention, operational reliability, and customer acquisition efficiency.

---

## 1. Monthly Active Users (MAU)
* **Name**: Monthly Active Users (MAU)
* **Definition**: Distinct customers with at least one transaction in the last 30 days.
* **Formula**: `COUNT(DISTINCT customer_id) WHERE transaction_date >= TODAY() - 30 days`
* **Data Source**: `transactions` table (columns: `customer_id`, `transaction_date`)
* **Target Range**: `5,000 - 6,000`
* **Owner**: Product Manager
* **Update Frequency**: Daily
* **Notes**: Core indicator of product engagement and active customer base size; subject to seasonal dips in Q4.

---

## 2. Revenue per Customer (RPC)
* **Name**: Revenue per Customer (RPC)
* **Definition**: Average revenue generated per unique active customer within the evaluated period.
* **Formula**: `SUM(amount) / COUNT(DISTINCT customer_id)`
* **Data Source**: `transactions` table (columns: `customer_id`, `amount`)
* **Target Range**: `$90.00 - $110.00`
* **Owner**: Revenue Lead / Finance
* **Update Frequency**: Daily
* **Notes**: Measures monetization efficiency and monetization depth per customer; helps evaluate upsell effectiveness.

---

## 3. Churn Rate
* **Name**: Churn Rate
* **Definition**: Percentage of active customers in the baseline period (days 31 to 60 ago) who recorded zero transactions during the current period (last 30 days).
* **Formula**: `COUNT(active_p1 NOT IN active_p2) / COUNT(active_p1)`
* **Data Source**: `transactions` table (columns: `customer_id`, `transaction_date`)
* **Target Range**: `0.0% - 5.0%` (`0.00 - 0.05`)
* **Owner**: Customer Success Lead
* **Update Frequency**: Weekly / Monthly
* **Notes**: Primary metric for customer retention and subscription health; spikes indicate onboarding friction or customer dissatisfaction.

---

## 4. Payment Success Rate
* **Name**: Payment Success Rate
* **Definition**: Ratio of successful payment transactions to total attempted payment transactions.
* **Formula**: `COUNT(transactions WHERE status = 'SUCCESS') / COUNT(total_transactions)`
* **Data Source**: `transactions` table (columns: `status`, `transaction_id`)
* **Target Range**: `95.0% - 100.0%` (`0.95 - 1.00`)
* **Owner**: Payments Engineering / Operations
* **Update Frequency**: Real-time / Daily
* **Notes**: Critical operational reliability metric; drop below target directly causes immediate revenue loss and churn.

---

## 5. Customer Acquisition Cost (CAC)
* **Name**: Customer Acquisition Cost (CAC)
* **Definition**: Total spend on marketing and sales divided by the number of new customers acquired during the same period.
* **Formula**: `TOTAL_MARKETING_SPEND / COUNT(DISTINCT new_customer_id)`
* **Data Source**: `marketing_spend` & `customers` tables (columns: `spend`, `acquisition_date`, `customer_id`)
* **Target Range**: `$0.00 - $50.00`
* **Owner**: Growth Marketing Director
* **Update Frequency**: Monthly
* **Notes**: Essential metric for paid customer acquisition unit economics; must be lower than Customer Lifetime Value (LTV).
