# Data Dictionary

## Dataset Overview
This dataset contains customer transaction records updated daily from the CRM system.
- **Last Updated**: 2025-05-21
- **Maintained By**: Data Engineering Team

---

## Columns

### customer_id
- **Type**: Integer
- **Business Meaning**: Unique customer identifier from CRM system
- **Example**: `12456`
- **Null Handling**: Never null (primary key)
- **Related KPI**: Customer tracking, lifetime value calculation
- **Updates**: Assigned when customer is created in CRM

### trnx_amt  
- **Type**: Float
- **Business Meaning**: Revenue from a single transaction
- **Example**: `150.99`
- **Unit**: USD
- **Null Handling**: Very rare - investigate if found
- **Related KPI**: Monthly revenue, average transaction value, customer lifetime value
- **Updates**: Set when transaction completes

### purchase_date
- **Type**: Datetime
- **Business Meaning**: Date and time when transaction occurred (UTC timezone)
- **Example**: `2025-01-15`
- **Null Handling**: Never null (required field)
- **Related KPI**: Sales velocity, purchase timing
- **Updates**: Set when transaction completes

### cust_segment
- **Type**: String
- **Business Meaning**: Customer market segment (B2B/B2C/SMB)
- **Valid Values**: `B2B`, `B2C`, `SMB`
- **Example**: `B2B`
- **Null Handling**: If null, classify as `UNKNOWN`
- **Related KPI**: Segment revenue, segment churn rate
- **Updates**: Monthly from CRM classification

### flag_churn
- **Type**: Integer
- **Business Meaning**: Churn indicator (0 = retained, 1 = churned within 90 days following this transaction)
- **Example**: `0`
- **Null Handling**: Never null (required for training predictive retention models)
- **Related KPI**: Churn rate prediction, retention rate
- **Updates**: Calculated daily based on 90-day inactivity window

---

## Column to KPI Mapping

### Monthly Revenue
- **Formula**: `SUM(trnx_amt)`
- **Related Columns**: `trnx_amt`, `Date` (mapped as `purchase_date`)
- **Why It Matters**: Tracks total company revenue
- **Update Frequency**: Daily

### Sales Velocity  
- **Formula**: `COUNT(transactions) / days`
- **Related Columns**: `purchase_date`
- **Why It Matters**: Measures sales activity rate and momentum
- **Update Frequency**: Weekly

### Segment Revenue
- **Formula**: `SUM(trnx_amt)` grouped by `cust_segment`
- **Related Columns**: `trnx_amt`, `cust_segment`
- **Why It Matters**: Identifies most profitable market segments
- **Update Frequency**: Monthly

### Churn Rate
- **Formula**: `SUM(flag_churn) / total_customers`
- **Related Columns**: `flag_churn`, `customer_id`
- **Why It Matters**: Critical retention metric
- **Update Frequency**: Quarterly

### Customer Lifetime Value (LTV)
- **Formula**: `SUM(trnx_amt)` grouped by `customer_id`
- **Related Columns**: `trnx_amt`, `customer_id`
- **Why It Matters**: Measures overall user value to the business and guides retention target spending
- **Update Frequency**: Weekly

---

## Ambiguous Columns & Resolutions

### Column: flag_churn
- **Original Ambiguity**: Does it mean "currently churned" or "will churn in future"?
- **Resolved Meaning**: Binary indicator of whether customer churned in 90 days following this transaction
- **Business Interpretation**: Historical churn flag used for training predictive retention models
- **Proposed Rename**: `has_churned_90d`
- **Risk If Misunderstood**: Models trained on wrong definition produce unreliable predictions

### Column: segment (appearing in data as cust_segment)
- **Original Ambiguity**: Is this market segment, customer segment, product segment, or geographic region?
- **Resolved Meaning**: Customer market segment (B2B, B2C, SMB) - determines go-to-market strategy
- **Business Interpretation**: Informs pricing strategy and sales approach
- **Proposed Rename**: `market_segment`
- **Risk If Misunderstood**: Revenue analysis by wrong dimension produces misleading segment performance

---

## Column Relationships

### Revenue per Customer
- **Definition**: `SUM(trnx_amt)` grouped by `customer_id`
- **How It Matters**: Identifies high-value customers for retention focus and upsell opportunities
- **Example**: "Top 10% of customers generate 50% of revenue"
- **Related Columns**: `customer_id`, `trnx_amt`, `cust_segment`

### Churn by Segment  
- **Definition**: `SUM(flag_churn) / SUM(all customers)` grouped by `cust_segment`
- **How It Matters**: Identifies which segments have highest churn risk requiring intervention
- **Example**: "SMB segment has 25% churn vs 10% for B2B"
- **Related Columns**: `flag_churn`, `cust_segment`, `customer_id`

### Revenue Velocity
- **Definition**: Rolling sum of `trnx_amt` over 30-day windows
- **How It Matters**: Tracks sales momentum and growth rate trends
- **Example**: "Monthly revenue velocity trending up 15% quarter-over-quarter"
- **Related Columns**: `trnx_amt`, `purchase_date`
