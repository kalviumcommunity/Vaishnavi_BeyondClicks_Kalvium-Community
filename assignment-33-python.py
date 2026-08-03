import os
import sys
import time
import re
import pandas as pd
from sqlalchemy import create_engine, text, event
from datetime import datetime, timedelta

# Ensure UTF-8 output encoding for Windows terminal compatibility
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Project Directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "output", "marketing.db")

# Custom SQLite datediff function
def sqlite_datediff(date1_str, date2_str):
    if date1_str is None or date2_str is None:
        return None
    try:
        # Extract date portion
        d1 = datetime.strptime(date1_str.split()[0], "%Y-%m-%d")
        d2 = datetime.strptime(date2_str.split()[0], "%Y-%m-%d")
        return (d1 - d2).days
    except Exception:
        return None

# Setup SQLite Database Engine
engine = create_engine(f"sqlite:///{DB_FILE}")

# Register custom functions on SQLite connect
@event.listens_for(engine, "connect")
def register_sqlite_functions(dbapi_connection, connection_record):
    dbapi_connection.create_function("DATEDIFF", 2, sqlite_datediff)

def translate_to_sqlite(sql):
    """Translates postgres/mysql interval syntax to sqlite format."""
    # CURRENT_DATE - INTERVAL 30 DAY
    sql = re.sub(
        r"CURRENT_DATE\s*-\s*INTERVAL\s*30\s*DAY",
        "date('now', '-30 days')",
        sql,
        flags=re.IGNORECASE
    )
    # CURRENT_DATE - INTERVAL 30 days
    sql = re.sub(
        r"CURRENT_DATE\s*-\s*INTERVAL\s*([0-9]+)\s*day(s)?",
        r"date('now', '-\1 days')",
        sql,
        flags=re.IGNORECASE
    )
    # interval 30 day
    sql = re.sub(
        r"INTERVAL\s*30\s*DAY",
        "'-30 days'",
        sql,
        flags=re.IGNORECASE
    )
    return sql

def execute_sql(sql_str):
    translated = translate_to_sqlite(sql_str)
    with engine.begin() as conn:
        # If there are multiple statements separated by semicolon (e.g. table create & insert)
        # execute them one by one
        statements = [s.strip() for s in translated.split(";") if s.strip()]
        for stmt in statements:
            conn.execute(text(stmt))

def seed_database():
    print("🌱 Seeding raw database tables...")
    cust_path = os.path.join(BASE_DIR, "data", "raw", "customers.csv")
    orders_path = os.path.join(BASE_DIR, "data", "raw", "orders.csv")
    
    # Customers
    df_c = pd.read_csv(cust_path)
    # Add missing customers present in orders
    missing_custs = pd.DataFrame([
        {'customer_id': 106, 'customer_name': 'Frank Miller', 'email': 'frank@example.com', 'signup_date': '2023-05-15'},
        {'customer_id': 107, 'customer_name': 'Grace Hopper', 'email': 'grace@example.com', 'signup_date': '2023-05-20'}
    ])
    df_c = pd.concat([df_c, missing_custs], ignore_index=True)
    df_c['segment'] = ['Enterprise', 'SMB', 'Startup', 'SMB', 'Enterprise', 'Startup', 'SMB']
    df_c['deleted_at'] = None
    # Set one customer as soft-deleted to verify WHERE filtering in views
    df_c.loc[df_c['customer_id'] == 104, 'deleted_at'] = datetime.now().strftime("%Y-%m-%d")
    df_c.to_sql('customers', engine, if_exists='replace', index=False)
    
    # Orders
    df_o = pd.read_csv(orders_path)
    df_o = df_o.rename(columns={'amount': 'order_amount'})
    
    # Align dates dynamically relative to current date
    now = datetime.now()
    dates_mapping = {
        1001: (now - timedelta(days=5)).strftime("%Y-%m-%d"),
        1002: (now - timedelta(days=12)).strftime("%Y-%m-%d"),
        1003: (now - timedelta(days=25)).strftime("%Y-%m-%d"),
        1004: (now - timedelta(days=40)).strftime("%Y-%m-%d"),
        1005: (now - timedelta(days=8)).strftime("%Y-%m-%d"),
        1006: (now - timedelta(days=70)).strftime("%Y-%m-%d")
    }
    df_o['order_date'] = df_o['order_id'].map(dates_mapping)
    
    # Add high-value older orders for churn cohorts view (total_spent > 500 and inactive > 30 days)
    extra_orders = pd.DataFrame([
        {'order_id': 1007, 'customer_id': 101, 'order_date': (now - timedelta(days=35)).strftime("%Y-%m-%d"), 'order_amount': 600.00},
        {'order_id': 1008, 'customer_id': 105, 'order_date': (now - timedelta(days=65)).strftime("%Y-%m-%d"), 'order_amount': 950.00}
    ])
    df_o = pd.concat([df_o, extra_orders], ignore_index=True)
    df_o.to_sql('orders', engine, if_exists='replace', index=False)
    print("✓ Seeding complete.")

def main():
    # Make sure output directory exists
    os.makedirs(os.path.join(BASE_DIR, "output"), exist_ok=True)
    
    # Seed DB first
    seed_database()

    print("\n=== TASK 1: Create Two SQL Views ===")
    
    # Drop views if they exist to support re-runs
    with engine.begin() as conn:
        conn.execute(text("DROP VIEW IF EXISTS vw_active_customers"))
        conn.execute(text("DROP VIEW IF EXISTS vw_your_custom_metric"))
        conn.execute(text("DROP TABLE IF EXISTS agg_daily_metrics"))

    # Load View 1 from SQL file
    view1_path = os.path.join(BASE_DIR, "database", "views", "vw_active_customers.sql")
    print(f"Loading View 1 from: {view1_path}")
    with open(view1_path, 'r', encoding='utf-8') as f:
        view1_sql = f.read()
    
    # Load View 2 from SQL file
    view2_path = os.path.join(BASE_DIR, "database", "views", "vw_your_custom_metric.sql")
    print(f"Loading View 2 from: {view2_path}")
    with open(view2_path, 'r', encoding='utf-8') as f:
        view2_sql = f.read()

    # Create the views
    print("Creating view: vw_active_customers...")
    execute_sql(view1_sql)
    print("Creating view: vw_your_custom_metric...")
    execute_sql(view2_sql)

    # Query the views to confirm they work
    active_customers = pd.read_sql("SELECT * FROM vw_active_customers LIMIT 10", engine)
    custom_metric = pd.read_sql("SELECT * FROM vw_your_custom_metric LIMIT 10", engine)

    print("\nView 1 columns:", active_customers.columns.tolist())
    print("View 2 columns:", custom_metric.columns.tolist())

    print("\n=== TASK 2: Create One Pre-Aggregated Summary Table ===")
    
    # Load table create & populate script
    agg_path = os.path.join(BASE_DIR, "database", "aggregations", "agg_daily_metrics.sql")
    print(f"Loading Aggregation Table definition from: {agg_path}")
    with open(agg_path, 'r', encoding='utf-8') as f:
        agg_sql = f.read()
        
    # Execute the table creation and insertion
    print("Creating and populating agg_daily_metrics...")
    execute_sql(agg_sql)

    # Verify
    agg_data = pd.read_sql("SELECT * FROM agg_daily_metrics ORDER BY aggregation_date DESC LIMIT 10", engine)
    print(f"Aggregated {len(agg_data)} rows:")
    print(agg_data)

    # Show that query against pre-aggregated table is instant
    start_time = time.time()
    result = pd.read_sql("SELECT metric_name, SUM(metric_value) FROM agg_daily_metrics GROUP BY metric_name", engine)
    elapsed = time.time() - start_time
    print(f"Query time: {elapsed*1000:.2f}ms")

    print("\n=== TASK 3: Query Views & Aggregated Tables from Python (Dashboard Simulation) ===")
    
    # Query View 1: Active Customers
    active_cust_query = translate_to_sqlite("""
        SELECT 
            customer_id, 
            customer_name, 
            revenue_30d,
            days_since_order
        FROM vw_active_customers
        WHERE days_since_order <= 30
        ORDER BY revenue_30d DESC
        LIMIT 20
    """)
    active_cust_df = pd.read_sql(active_cust_query, engine)
    print("Top 20 Active Customers (last 30 days):")
    print(active_cust_df)

    # Query View 2: Custom metric
    custom_result = pd.read_sql("SELECT * FROM vw_your_custom_metric LIMIT 20", engine)
    print("\nCustom Metric Results (Churn Risk Cohorts):")
    print(custom_result)

    # Query Pre-Aggregated Table
    agg_query = translate_to_sqlite("""
        SELECT 
            aggregation_date,
            metric_name,
            metric_value
        FROM agg_daily_metrics
        WHERE aggregation_date >= CURRENT_DATE - INTERVAL 30 DAY
        ORDER BY aggregation_date DESC
    """)
    agg_result = pd.read_sql(agg_query, engine)
    print("\nDaily Aggregated Metrics (last 30 days):")
    print(agg_result)

    # Demonstrate filtering capability
    active_by_segment = pd.read_sql("""
        SELECT 
            segment,
            COUNT(*) as customer_count,
            SUM(revenue_30d) as total_segment_revenue,
            AVG(revenue_30d) as avg_customer_revenue
        FROM vw_active_customers
        GROUP BY segment
        ORDER BY total_segment_revenue DESC
    """, engine)
    print("\nRevenue by Segment:")
    print(active_by_segment)

if __name__ == "__main__":
    main()
