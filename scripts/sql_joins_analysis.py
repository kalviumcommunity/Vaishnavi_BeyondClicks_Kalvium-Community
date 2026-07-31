import sqlite3
from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent

RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"
RESULT_DIR = PROCESSED_DIR / "sql_join_results"

RESULT_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH = PROCESSED_DIR / "beyondclicks_joins.db"


print("=" * 70)
print("BEYONDCLICKS - SQL JOINS & MULTI-TABLE ANALYSIS")
print("=" * 70)


# ============================================================
# 1. LOAD DATA
# ============================================================

customers = pd.read_csv(RAW_DIR / "sql_join_customers.csv")
orders = pd.read_csv(RAW_DIR / "sql_join_orders.csv")
order_items = pd.read_csv(RAW_DIR / "sql_join_order_items.csv")
products = pd.read_csv(RAW_DIR / "sql_join_products.csv")

print(f"\nCustomers: {len(customers)}")
print(f"Orders: {len(orders)}")
print(f"Order Items: {len(order_items)}")
print(f"Products: {len(products)}")


# ============================================================
# 2. CREATE SQLITE DATABASE
# ============================================================

conn = sqlite3.connect(DB_PATH)

customers.to_sql("customers", conn, if_exists="replace", index=False)
orders.to_sql("orders", conn, if_exists="replace", index=False)
order_items.to_sql("order_items", conn, if_exists="replace", index=False)
products.to_sql("products", conn, if_exists="replace", index=False)

print("\nSQLite database created successfully.")


# ============================================================
# TASK 1: LEFT JOIN WITH ROW COUNT VALIDATION
# ============================================================

print("\n" + "=" * 70)
print("TASK 1: LEFT JOIN WITH ROW COUNT VALIDATION")
print("=" * 70)

task1_query = """
SELECT
    c.customer_id,
    c.customer_type,
    COUNT(DISTINCT o.order_id) AS order_count,
    COALESCE(SUM(o.order_amount), 0) AS total_spent
FROM customers c
LEFT JOIN orders o
    ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.customer_type
ORDER BY total_spent DESC;
"""

task1 = pd.read_sql_query(task1_query, conn)

task1.to_csv(
    RESULT_DIR / "task1_left_join.csv",
    index=False
)

customers_count = len(customers)
joined_rows = len(task1)

print(task1)

print(f"\nBefore join: {customers_count} customers")
print(f"After join: {joined_rows} customer-level rows")
print(
    f"Change: {joined_rows - customers_count} "
    f"({((joined_rows - customers_count) / customers_count) * 100:.1f}%)"
)

print(
    "\nExplanation: "
    "The LEFT JOIN preserves every customer. "
    "Multiple orders belong to the same customer, so the raw join "
    "can contain multiple rows per customer. "
    "The grouped result returns one row per customer."
)


# ============================================================
# TASK 2: DETECT UNMATCHED KEYS
# ============================================================

print("\n" + "=" * 70)
print("TASK 2: DETECT UNMATCHED KEYS")
print("=" * 70)


no_orders_query = """
SELECT
    c.customer_id,
    c.customer_type,
    c.signup_date
FROM customers c
LEFT JOIN orders o
    ON c.customer_id = o.customer_id
WHERE o.order_id IS NULL
ORDER BY c.signup_date;
"""

no_orders = pd.read_sql_query(no_orders_query, conn)

no_orders.to_csv(
    RESULT_DIR / "task2_customers_without_orders.csv",
    index=False
)


orphaned_query = """
SELECT
    o.order_id,
    o.customer_id,
    o.order_date
FROM orders o
LEFT JOIN customers c
    ON o.customer_id = c.customer_id
WHERE c.customer_id IS NULL
ORDER BY o.order_date;
"""

orphaned = pd.read_sql_query(orphaned_query, conn)

orphaned.to_csv(
    RESULT_DIR / "task2_orphaned_orders.csv",
    index=False
)


print("\nCustomers without orders:")
print(no_orders)

print(
    f"\nCustomers without orders: {len(no_orders)} "
    f"({(len(no_orders) / customers_count) * 100:.1f}%)"
)

print("\nOrphaned orders:")
print(orphaned)

print(f"\nOrphaned orders: {len(orphaned)}")

if len(orphaned) > 0:
    print(
        "⚠️ Orphaned records found - investigate customer_id mismatch."
    )


# ============================================================
# TASK 3: COMPARE JOIN TYPES
# ============================================================

print("\n" + "=" * 70)
print("TASK 3: COMPARE JOIN TYPES")
print("=" * 70)


inner_query = """
SELECT
    c.customer_id,
    o.order_id,
    o.order_amount
FROM customers c
INNER JOIN orders o
    ON c.customer_id = o.customer_id;
"""

left_query = """
SELECT
    c.customer_id,
    o.order_id,
    o.order_amount
FROM customers c
LEFT JOIN orders o
    ON c.customer_id = o.customer_id;
"""


# SQLite does not support FULL OUTER JOIN directly.
# We emulate it using LEFT JOIN + unmatched right rows.

full_query = """
SELECT
    c.customer_id,
    o.order_id,
    o.order_amount
FROM customers c
LEFT JOIN orders o
    ON c.customer_id = o.customer_id

UNION ALL

SELECT
    c.customer_id,
    o.order_id,
    o.order_amount
FROM orders o
LEFT JOIN customers c
    ON c.customer_id = o.customer_id
WHERE c.customer_id IS NULL;
"""


inner = pd.read_sql_query(inner_query, conn)
left = pd.read_sql_query(left_query, conn)
full = pd.read_sql_query(full_query, conn)


inner.to_csv(
    RESULT_DIR / "task3_inner_join.csv",
    index=False
)

left.to_csv(
    RESULT_DIR / "task3_left_join.csv",
    index=False
)

full.to_csv(
    RESULT_DIR / "task3_full_outer_join.csv",
    index=False
)


print(f"INNER JOIN: {len(inner)} rows")
print(f"LEFT JOIN:  {len(left)} rows")
print(f"FULL JOIN:  {len(full)} rows")

assert len(left) >= len(inner)
assert len(full) >= len(left)

print("\n✓ Join relationship validation passed.")


# ============================================================
# TASK 4: MULTI-TABLE JOIN
# ============================================================

print("\n" + "=" * 70)
print("TASK 4: MULTI-TABLE JOIN")
print("=" * 70)


task4_query = """
SELECT
    c.customer_id,
    c.customer_type,
    o.order_id,
    o.order_date,
    oi.product_id,
    p.product_name,
    oi.quantity,
    oi.unit_price,
    (oi.quantity * oi.unit_price) AS line_total
FROM customers c
LEFT JOIN orders o
    ON c.customer_id = o.customer_id
LEFT JOIN order_items oi
    ON o.order_id = oi.order_id
LEFT JOIN products p
    ON oi.product_id = p.product_id
WHERE c.customer_type = 'Enterprise'
ORDER BY o.order_date DESC;
"""

task4 = pd.read_sql_query(task4_query, conn)

task4.to_csv(
    RESULT_DIR / "task4_multi_table_join.csv",
    index=False
)

print(task4)


# Validate line totals against order_items
product_total = task4["line_total"].sum()

expected_total_query = """
SELECT SUM(quantity * unit_price)
FROM order_items oi
JOIN orders o
    ON oi.order_id = o.order_id
JOIN customers c
    ON o.customer_id = c.customer_id
WHERE c.customer_type = 'Enterprise';
"""

expected_total = pd.read_sql_query(
    expected_total_query,
    conn
).iloc[0, 0]

print(f"\nCalculated multi-table total: {product_total}")
print(f"Expected Enterprise total: {expected_total}")

assert abs(product_total - expected_total) < 0.01

print("✓ Multi-table join validated - no unexpected duplication.")


# ============================================================
# TASK 5: JOIN VALIDATION SUMMARY
# ============================================================

print("\n" + "=" * 70)
print("TASK 5: JOIN VALIDATION SUMMARY")
print("=" * 70)


validation = pd.DataFrame([
    {
        "table": "customers",
        "rows": len(customers),
        "key": "customer_id",
        "role": "Primary customer table"
    },
    {
        "table": "orders",
        "rows": len(orders),
        "key": "customer_id",
        "role": "Customer orders"
    },
    {
        "table": "order_items",
        "rows": len(order_items),
        "key": "order_id",
        "role": "Order line items"
    },
    {
        "table": "products",
        "rows": len(products),
        "key": "product_id",
        "role": "Product information"
    }
])

validation.to_csv(
    RESULT_DIR / "task5_validation_summary.csv",
    index=False
)

print(validation)


# ============================================================
# FINAL SUMMARY
# ============================================================

documentation = """
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
"""

with open(
    BASE_DIR / "docs" / "sql_joins_multi_table.md",
    "w",
    encoding="utf-8"
) as f:
    f.write(documentation)


conn.close()

print("\n" + "=" * 70)
print("ANALYSIS COMPLETED SUCCESSFULLY")
print("=" * 70)

print(f"\nDatabase:")
print(DB_PATH)

print("\nResults saved to:")
print(RESULT_DIR)

print("\nGenerated files:")
for file in sorted(RESULT_DIR.iterdir()):
    print(f" - {file.name}")