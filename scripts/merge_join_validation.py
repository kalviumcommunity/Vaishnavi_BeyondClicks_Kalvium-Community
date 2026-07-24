import os
import json
import pandas as pd
from pathlib import Path

# -------------------------------------------------
# Project Paths
# -------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
CUSTOMERS_DATA = BASE_DIR / "data" / "raw" / "customers.csv"
ORDERS_DATA = BASE_DIR / "data" / "raw" / "orders.csv"
OUTPUT_DIR = BASE_DIR / "output"
PROCESSED_DIR = BASE_DIR / "data" / "processed"

OUTPUT_DIR.mkdir(exist_ok=True)
PROCESSED_DIR.mkdir(exist_ok=True)


def main():
    # Load raw datasets
    df_customers = pd.read_csv(CUSTOMERS_DATA)
    df_orders = pd.read_csv(ORDERS_DATA)

    print("=" * 60)
    print("TASK 1: EXPLICIT JOIN WITH ROW COUNT VALIDATION")
    print("=" * 60)
    print(f"Left: {len(df_customers)}")
    print(f"Right: {len(df_orders)}")

    df_merged = pd.merge(df_customers, df_orders, on='customer_id', how='left')

    print(f"Merged: {len(df_merged)}")
    print(f"Change: {len(df_merged) - len(df_customers)}")
    print()

    print("=" * 60)
    print("TASK 2: DETECT UNMATCHED KEYS")
    print("=" * 60)
    unmatched_customers = df_customers[~df_customers['customer_id'].isin(df_orders['customer_id'])]
    unmatched_orders = df_orders[~df_orders['customer_id'].isin(df_customers['customer_id'])]

    print(f"Customers without orders: {len(unmatched_customers)}")
    print(f"Orphaned orders: {len(unmatched_orders)}")

    unmatched_customers.to_csv(OUTPUT_DIR / 'unmatched_customers.csv', index=False)
    unmatched_orders.to_csv(OUTPUT_DIR / 'unmatched_orders.csv', index=False)
    print(f"Saved unmatched customers to: {OUTPUT_DIR / 'unmatched_customers.csv'}")
    print(f"Saved unmatched orders to: {OUTPUT_DIR / 'unmatched_orders.csv'}")
    print()

    print("=" * 60)
    print("TASK 3: COMPARE JOIN TYPES")
    print("=" * 60)
    inner = pd.merge(df_customers, df_orders, how='inner')
    left = pd.merge(df_customers, df_orders, how='left')
    outer = pd.merge(df_customers, df_orders, how='outer')

    print(f"Inner: {len(inner)}, Left: {len(left)}, Outer: {len(outer)}")
    print()

    print("=" * 60)
    print("TASK 4: VALIDATE NO UNEXPECTED DUPLICATION")
    print("=" * 60)
    # Check for unexpected column conflicts
    print(df_merged.columns)

    # If customer_id appears in both, verify merge key
    key_counts = df_merged['customer_id'].value_counts()
    print(f"Max orders per customer: {key_counts.max()}")
    print()

    print("=" * 60)
    print("TASK 5: DOCUMENT JOIN DECISION")
    print("=" * 60)
    join_report = {
        'join_type': 'left',
        'left_table': 'customers',
        'right_table': 'orders',
        'join_key': 'customer_id',
        'left_rows': len(df_customers),
        'right_rows': len(df_orders),
        'result_rows': len(df_merged),
        'unmatched_left': len(unmatched_customers),
        'unmatched_right': len(unmatched_orders),
        'reasoning': 'Left join preserves all customers; unmatched customers have no orders'
    }

    print(json.dumps(join_report, indent=2))

    # Save join report to output/join_report.json
    report_file = OUTPUT_DIR / 'join_report.json'
    with open(report_file, 'w') as f:
        json.dump(join_report, f, indent=2)
    print(f"\nSaved join report to: {report_file}")

    # Save merged dataset to data/processed/merged_customers_orders.csv
    merged_file = PROCESSED_DIR / 'merged_customers_orders.csv'
    df_merged.to_csv(merged_file, index=False)
    print(f"Saved merged dataset to: {merged_file}")


if __name__ == "__main__":
    main()
