
JOIN STRATEGY DOCUMENTATION

1. customers LEFT JOIN orders
Purpose:
Get every customer together with available order history.

Reason:
LEFT JOIN keeps customers who have no orders.

Validation:
Customer-level grouping ensures one output row per customer.

Business use:
Customer order history, customer segmentation and lifetime value.

2. Unmatched customer detection
Purpose:
Find customers without any orders.

Method:
LEFT JOIN followed by WHERE order_id IS NULL.

Business use:
Identify inactive customers and possible onboarding opportunities.

3. Orphaned order detection
Purpose:
Find orders whose customer_id does not exist in customers.

Method:
LEFT JOIN followed by WHERE customer_id IS NULL.

Business use:
Detect broken foreign-key relationships and data-quality problems.

4. INNER JOIN
Returns only customers and orders with matching customer_id values.

Business use:
Analysis where unmatched records should be excluded.

5. LEFT JOIN
Returns all customers and matching orders.

Business use:
Complete customer population analysis.

6. FULL OUTER JOIN
Returns all matched and unmatched records from both tables.

SQLite implementation:
FULL OUTER JOIN is simulated using UNION ALL of two LEFT JOIN queries.

Business use:
Complete reconciliation and data-quality investigation.

7. Multi-table join
customers -> orders -> order_items -> products

Purpose:
Trace complete data lineage from customer to order to product.

Validation:
Line totals are compared against the expected Enterprise order-item total.

Important:
One-to-many joins naturally increase rows. Aggregations must be performed
at the correct level to avoid double counting.
