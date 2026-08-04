"""
SQL vs Python Insight Validation Pipeline
Implements Tasks 1-4:
- Task 1: Compute Three Metrics in Both SQL and Python
- Task 2: Identify and Document Discrepancies
- Task 3: Build Automated Validation Script
- Task 4: Investigate and Document Root Cause
"""

import os
import sys
import re
import pandas as pd
import numpy as np
from datetime import datetime, date, timedelta
from sqlalchemy import create_engine, text, event

# Ensure UTF-8 output encoding for Windows terminal compatibility
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
DB_PATH = os.path.join(PROJECT_ROOT, "analytics.db")

# Setup SQLAlchemy SQLite Engine
engine = create_engine(f"sqlite:///{DB_PATH}")

# Register custom MONTH function in SQLite to support MONTH(date_col) in queries
@event.listens_for(engine, "connect")
def register_sqlite_functions(dbapi_connection, connection_record):
    def month_func(date_str):
        if date_str is None:
            return None
        try:
            # Parse string date YYYY-MM-DD or timestamp
            d = datetime.strptime(str(date_str).split()[0], "%Y-%m-%d")
            return d.month
        except Exception:
            return None
    dbapi_connection.create_function("MONTH", 1, month_func)


def translate_to_sqlite(sql: str) -> str:
    """Translates Postgres/MySQL date interval syntax to SQLite syntax."""
    # CURRENT_DATE - INTERVAL 30 DAY -> date('now', '-30 days')
    sql = re.sub(
        r"CURRENT_DATE\s*-\s*INTERVAL\s*30\s*DAY",
        "date('now', '-30 days')",
        sql,
        flags=re.IGNORECASE
    )
    sql = re.sub(
        r"CURRENT_DATE\s*-\s*INTERVAL\s*([0-9]+)\s*DAY(S)?",
        r"date('now', '-\1 days')",
        sql,
        flags=re.IGNORECASE
    )
    return sql


def seed_database(engine):
    """Seed sample logins and orders tables into SQLite database."""
    print("🌱 Seeding logins and orders tables into analytics.db...")
    np.random.seed(42)
    today = date.today()

    # 1. Logins table (for Active Users 30d metric)
    # Users logged in over the last 60 days
    user_ids = np.random.randint(100, 200, size=500)
    days_ago = np.random.randint(0, 60, size=500)
    login_dates = [today - timedelta(days=int(d)) for d in days_ago]

    logins_df = pd.DataFrame({
        'login_id': range(1, 501),
        'user_id': user_ids,
        'login_date': [d.strftime('%Y-%m-%d') for d in login_dates]
    })
    logins_df.to_sql('logins', engine, if_exists='replace', index=False)

    # 2. Orders table (for AOV and Monthly Churn metrics)
    # Define Month N (current month) and Month N-1 (previous month)
    current_month_start = today.replace(day=1)
    if today.month == 1:
        prev_month_start = date(today.year - 1, 12, 1)
    else:
        prev_month_start = date(today.year, today.month - 1, 1)

    orders_list = []
    order_id = 1001

    # Cohort A: Active in Month N-1, Active in Month N (Retained) -> 30 customers
    for cust_id in range(1, 31):
        # Month N-1 order
        orders_list.append({
            'order_id': order_id,
            'customer_id': cust_id,
            'order_date': prev_month_start.strftime('%Y-%m-%d'),
            'order_amount': float(np.random.uniform(50, 200))
        })
        order_id += 1
        # Month N order
        orders_list.append({
            'order_id': order_id,
            'customer_id': cust_id,
            'order_date': current_month_start.strftime('%Y-%m-%d'),
            'order_amount': float(np.random.uniform(50, 200))
        })
        order_id += 1

    # Cohort B: Active in Month N-1, NOT Active in Month N (Churned) -> 20 customers
    for cust_id in range(31, 51):
        orders_list.append({
            'order_id': order_id,
            'customer_id': cust_id,
            'order_date': prev_month_start.strftime('%Y-%m-%d'),
            'order_amount': float(np.random.uniform(50, 200))
        })
        order_id += 1

    # Cohort C: Orders from Previous Year same month number to trigger MONTH() year-stripping bug!
    # e.g., orders in Month N-1 of previous year (same calendar month number, different year)
    prev_year_prev_month_start = date(today.year - 1, prev_month_start.month, 15)
    for cust_id in range(51, 69): # 18 customers
        orders_list.append({
            'order_id': order_id,
            'customer_id': cust_id,
            'order_date': prev_year_prev_month_start.strftime('%Y-%m-%d'),
            'order_amount': float(np.random.uniform(50, 200))
        })
        order_id += 1

    orders_df = pd.DataFrame(orders_list)
    orders_df.to_sql('orders', engine, if_exists='replace', index=False)
    print("✓ Seeding complete. Created 'logins' and 'orders' tables.")


def get_python_metrics(engine):
    """Compute all 3 metrics in Python using Pandas."""
    logins_df = pd.read_sql("SELECT * FROM logins", engine)
    orders_df = pd.read_sql("SELECT * FROM orders", engine)

    # Metric 1: Active Users (30-day)
    today = date.today()
    logins_df['login_date_dt'] = pd.to_datetime(logins_df['login_date']).dt.date
    active_cutoff = today - timedelta(days=30)
    active_users_py = logins_df[logins_df['login_date_dt'] >= active_cutoff]['user_id'].nunique()

    # Metric 2: Average Order Value (AOV)
    aov_py = float(orders_df['order_amount'].mean())

    # Metric 3: Customer Churn (Monthly)
    # Active in Month N-1 with spend > 0, but NOT active in Month N
    if today.month == 1:
        prev_year, prev_month = today.year - 1, 12
    else:
        prev_year, prev_month = today.year, today.month - 1

    curr_year, curr_month = today.year, today.month

    orders_df['order_date_dt'] = pd.to_datetime(orders_df['order_date'])

    c1_customers = orders_df[
        (orders_df['order_date_dt'].dt.year == prev_year) &
        (orders_df['order_date_dt'].dt.month == prev_month) &
        (orders_df['order_amount'] > 0)
    ]['customer_id'].unique()

    c2_customers = orders_df[
        (orders_df['order_date_dt'].dt.year == curr_year) &
        (orders_df['order_date_dt'].dt.month == curr_month)
    ]['customer_id'].unique()

    churned_py = len([c for c in c1_customers if c not in c2_customers])

    return {
        'active_users': active_users_py,
        'aov': round(aov_py, 2),
        'churn': churned_py
    }, logins_df, orders_df


# ---------------------------------------------------------
# Task 3: Build Automated Validation Script
# ---------------------------------------------------------
def validate_metrics(engine, use_fixed_sql=False, tolerance_pct=0.1):
    """
    Validate that SQL and Python compute identical metrics.
    
    Args:
        engine: SQLAlchemy database engine
        use_fixed_sql: If True, uses fixed SQL query for churn metric
        tolerance_pct: Acceptable percentage difference (default 0.1%)
    
    Returns:
        validation_report: DataFrame with all metrics and match status
    """
    # SQL Queries
    sql_query_active_users = translate_to_sqlite(
        "SELECT COUNT(DISTINCT user_id) as active_users FROM logins WHERE login_date >= CURRENT_DATE - INTERVAL 30 DAY;"
    )

    sql_query_aov = "SELECT AVG(order_amount) as aov FROM orders;"

    if not use_fixed_sql:
        # Original SQL query with MONTH() function bug
        sql_query_churn = """
        SELECT COUNT(DISTINCT c1.customer_id) as churned_customers
        FROM (
            SELECT DISTINCT customer_id
            FROM orders
            WHERE MONTH(order_date) = MONTH(CURRENT_DATE) - 1
              AND order_amount > 0
        ) c1
        LEFT JOIN (
            SELECT DISTINCT customer_id
            FROM orders
            WHERE MONTH(order_date) = MONTH(CURRENT_DATE)
        ) c2 ON c1.customer_id = c2.customer_id
        WHERE c2.customer_id IS NULL;
        """
    else:
        # Fixed SQL query with explicit year and month range comparison
        today = date.today()
        current_month_start = today.replace(day=1).strftime('%Y-%m-%d')
        if today.month == 1:
            prev_month_start = date(today.year - 1, 12, 1).strftime('%Y-%m-%d')
        else:
            prev_month_start = date(today.year, today.month - 1, 1).strftime('%Y-%m-%d')

        # Next month start for month N upper bound
        if today.month == 12:
            next_month_start = date(today.year + 1, 1, 1).strftime('%Y-%m-%d')
        else:
            next_month_start = date(today.year, today.month + 1, 1).strftime('%Y-%m-%d')

        sql_query_churn = f"""
        SELECT COUNT(DISTINCT c1.customer_id) as churned_customers
        FROM (
            SELECT DISTINCT customer_id
            FROM orders
            WHERE order_date >= '{prev_month_start}'
              AND order_date < '{current_month_start}'
              AND order_amount > 0
        ) c1
        LEFT JOIN (
            SELECT DISTINCT customer_id
            FROM orders
            WHERE order_date >= '{current_month_start}'
              AND order_date < '{next_month_start}'
        ) c2 ON c1.customer_id = c2.customer_id
        WHERE c2.customer_id IS NULL;
        """

    # Fetch Python Metrics
    py_metrics, logins_df, orders_df = get_python_metrics(engine)

    # Define metrics dictionary
    metrics = {
        'active_users': {
            'sql': sql_query_active_users,
            'python': lambda: py_metrics['active_users'],
            'tolerance': 0  # Counts must be exact
        },
        'aov': {
            'sql': sql_query_aov,
            'python': lambda: py_metrics['aov'],
            'tolerance': tolerance_pct  # Percentages allow 0.1% difference
        },
        'churn': {
            'sql': sql_query_churn,
            'python': lambda: py_metrics['churn'],
            'tolerance': 0  # Counts must be exact
        }
    }

    validation_report = []

    for metric_name, metric_def in metrics.items():
        sql_res = pd.read_sql(metric_def['sql'], engine).iloc[0, 0]
        sql_result = float(sql_res) if sql_res is not None else 0.0
        py_result = float(metric_def['python']())

        difference = abs(sql_result - py_result)
        pct_diff = round((difference / abs(sql_result)) * 100, 2) if sql_result != 0 else 0.0

        match = pct_diff <= metric_def['tolerance']

        validation_report.append({
            'Metric': metric_name,
            'SQL': round(sql_result, 2),
            'Python': round(py_result, 2),
            'Difference': round(difference, 2),
            'Pct_Difference': pct_diff,
            'Tolerance': metric_def['tolerance'],
            'Status': 'PASS' if match else 'FAIL',
            'Timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })

    report_df = pd.DataFrame(validation_report)
    return report_df


def main():
    print("================================================================================")
    print("                 TASK 1 & 2: DUAL-LAYER METRIC COMPUTATION                      ")
    print("================================================================================")

    # Seed Database
    seed_database(engine)

    print("\n--- Initial Validation Run (Original SQL Queries) ---")
    initial_report = validate_metrics(engine, use_fixed_sql=False)
    print(initial_report.to_string(index=False))

    print("\nDiscrepancies found:")
    for idx, row in initial_report.iterrows():
        if row['Status'] == 'FAIL' or row['Pct_Difference'] > row['Tolerance']:
            print(f"  ⚠️ {row['Metric']}: {row['Pct_Difference']}% difference (SQL={row['SQL']}, Python={row['Python']})")
        else:
            print(f"  ✓ {row['Metric']}: Match within tolerance")

    # Export Initial Validation Report
    report_csv_path = os.path.join(PROJECT_ROOT, 'validation_report.csv')
    initial_report.to_csv(report_csv_path, index=False)
    print(f"\n✓ Saved validation report to '{report_csv_path}'")

    print("\n================================================================================")
    print("             TASK 4: VALIDATION AFTER APPLYING FIXED SQL QUERY                  ")
    print("================================================================================")

    fixed_report = validate_metrics(engine, use_fixed_sql=True)
    print(fixed_report.to_string(index=False))

    print("\nPost-Fix Discrepancies status:")
    for idx, row in fixed_report.iterrows():
        if row['Status'] == 'FAIL':
            print(f"  ⚠️ {row['Metric']}: {row['Pct_Difference']}% difference")
        else:
            print(f"  ✓ {row['Metric']}: Match within tolerance")

    # Export Fixed Validation Report
    fixed_report.to_csv(report_csv_path, index=False)
    print(f"\n✓ Updated validation report to '{report_csv_path}'")


if __name__ == '__main__':
    main()
