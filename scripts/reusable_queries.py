"""
Reusable Queries Pipeline and Validation
Loads queries from .sql files, translates PostgreSQL syntax to SQLite dynamically,
executes them, and validates the returned metrics.
"""

import os
import sys
import re
from pathlib import Path
import pandas as pd
from sqlalchemy import create_engine, event

# Ensure UTF-8 output encoding for Windows terminal compatibility
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Project Directories
BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "output" / "reusable_analytics.db"

# Ensure output directory exists
DB_PATH.parent.mkdir(parents=True, exist_ok=True)


def translate_to_sqlite(sql_query: str) -> str:
    """
    Translates PostgreSQL syntax to SQLite dialect.
    Handles:
      - DATE_TRUNC('month', col)::DATE -> date(col, 'start of month')
      - DATE_TRUNC('month', col) -> date(col, 'start of month')
      - DATE_TRUNC('day', col)::DATE -> date(col)
      - DATE_TRUNC('day', col) -> date(col)
      - DATE_TRUNC('month', NOW()) - INTERVAL 'X months' -> date('now', 'start of month', '-X months')
      - NOW() - INTERVAL 'X days' -> datetime('now', '-X days')
      - ::DATE casting operator removal
      - NOW() -> date('now') or datetime('now') depending on context
    """
    sql = sql_query

    # 1. Translate compound interval expressions relative to NOW() first
    sql = re.sub(
        r"DATE_TRUNC\('month',\s*NOW\(\)\)\s*-\s*INTERVAL\s*'([0-9]+)\s+([a-zA-Z]+)'",
        r"date('now', 'start of month', '-\1 \2')",
        sql,
        flags=re.IGNORECASE
    )
    sql = re.sub(
        r"NOW\(\)\s*-\s*INTERVAL\s*'([0-9]+)\s+([a-zA-Z]+)'",
        r"datetime('now', '-\1 \2')",
        sql,
        flags=re.IGNORECASE
    )

    # 2. Translate DATE_TRUNC('month', col)::DATE or DATE_TRUNC('month', col)
    sql = re.sub(
        r"DATE_TRUNC\('month',\s*([a-zA-Z0-9._]+)\)::DATE",
        r"date(\1, 'start of month')",
        sql,
        flags=re.IGNORECASE
    )
    sql = re.sub(
        r"DATE_TRUNC\('month',\s*([a-zA-Z0-9._]+)\)",
        r"date(\1, 'start of month')",
        sql,
        flags=re.IGNORECASE
    )

    # 3. Translate DATE_TRUNC('day', col)::DATE or DATE_TRUNC('day', col)
    sql = re.sub(
        r"DATE_TRUNC\('day',\s*([a-zA-Z0-9._]+)\)::DATE",
        r"date(\1)",
        sql,
        flags=re.IGNORECASE
    )
    sql = re.sub(
        r"DATE_TRUNC\('day',\s*([a-zA-Z0-9._]+)\)",
        r"date(\1)",
        sql,
        flags=re.IGNORECASE
    )

    # 4. Translate remaining NOW() calls
    sql = re.sub(r"\bNOW\(\)", "datetime('now')", sql, flags=re.IGNORECASE)

    # 5. Remove remaining Postgres cast operators if any remain (e.g. value::DATE)
    sql = re.sub(r"::DATE", "", sql, flags=re.IGNORECASE)

    return sql



def register_sqlite_translator(engine):
    """
    Registers a SQLAlchemy event listener to automatically translate
    PostgreSQL syntax queries to SQLite syntax before execution.
    """
    @event.listens_for(engine, "before_cursor_execute", retval=True)
    def receive_before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        translated_statement = translate_to_sqlite(statement)
        return translated_statement, parameters


def seed_sample_data(engine):
    """
    Seeds realistic sample data into transactions, customers, and users tables
    to verify all SQL queries produce correct, meaningful results.
    """
    import numpy as np
    from datetime import datetime, timedelta

    np.random.seed(42)
    now = datetime.now()

    # 1. Seed Customers Table
    customers_list = [
        {"customer_id": cid, "customer_type": "Enterprise" if cid % 3 == 0 else "SMB"}
        for cid in range(1, 101)
    ]
    df_customers = pd.DataFrame(customers_list)
    df_customers.to_sql("customers", engine, if_exists="replace", index=False)

    # 2. Seed Transactions Table
    # Spread transactions over last 13 months
    transactions_list = []
    for order_id in range(1, 1001):
        cid = np.random.randint(1, 101)
        ctype = "Enterprise" if cid % 3 == 0 else "SMB"
        # transaction date from 13 months ago to today
        days_ago = np.random.randint(0, 400)
        tx_date = (now - timedelta(days=days_ago)).strftime("%Y-%m-%d")
        amount = round(float(np.random.exponential(scale=200.0) + 10.0), 2)
        transactions_list.append({
            "order_id": order_id,
            "customer_id": cid,
            "transaction_date": tx_date,
            "amount": amount,
            "customer_type": ctype
        })
    df_transactions = pd.DataFrame(transactions_list)
    df_transactions.to_sql("transactions", engine, if_exists="replace", index=False)

    # 3. Seed Users Table
    # Spread user creation over last 100 days
    users_list = []
    for uid in range(1, 501):
        days_ago = np.random.randint(0, 100)
        created_time = now - timedelta(days=days_ago, hours=np.random.randint(0, 24))
        created_at = created_time.strftime("%Y-%m-%d %H:%M:%S")
        
        # 80% verify email
        email_verified_at = None
        if np.random.rand() < 0.8:
            verify_delay = np.random.randint(1, 3600 * 48)  # up to 48 hours later
            email_verified_at = (created_time + timedelta(seconds=verify_delay)).strftime("%Y-%m-%d %H:%M:%S")
            
        # 40% make a purchase after verification
        first_purchase_at = None
        if email_verified_at is not None and np.random.rand() < 0.4:
            purchase_delay = np.random.randint(1, 3600 * 24 * 10)  # up to 10 days later
            first_purchase_at = (datetime.strptime(email_verified_at, "%Y-%m-%d %H:%M:%S") + 
                                 timedelta(seconds=purchase_delay)).strftime("%Y-%m-%d %H:%M:%S")
            
        users_list.append({
            "id": uid,
            "created_at": created_at,
            "email_verified_at": email_verified_at,
            "first_purchase_at": first_purchase_at
        })
    df_users = pd.DataFrame(users_list)
    df_users.to_sql("users", engine, if_exists="replace", index=False)
    print("✓ Successfully seeded sample data to local database.")


def load_query(query_name):
    """Load SQL query from file."""
    with open(f'queries/{query_name}.sql', 'r') as f:
        return f.read()


def validate_metrics(mau_df, revenue_df, funnel_df):
    """Validate metric computation."""
    
    # Check for nulls
    assert mau_df.isnull().sum().sum() == 0, "MAU has nulls"
    assert revenue_df.isnull().sum().sum() == 0, "Revenue has nulls"
    
    # Check value ranges
    assert (revenue_df['monthly_revenue'] > 0).all(), "Revenue <= 0"
    assert (funnel_df['conversion_pct'] >= 0).all() and (funnel_df['conversion_pct'] <= 100).all(), "Conversion out of range"
    
    # Check consistency
    for idx, row in revenue_df.iterrows():
        assert row['order_count'] > 0, "Zero orders"
        assert row['monthly_revenue'] > 0, "Zero revenue"
    
    print("✓ All metrics validated")
    return True


def main():
    print("=== TASK 4: Setting up Database and Translator ===")
    engine = create_engine(f"sqlite:///{DB_PATH}")
    register_sqlite_translator(engine)
    seed_sample_data(engine)

    print("\n=== TASK 4: Loading and Executing Queries ===")
    
    # Load and execute
    mau_query = load_query('monthly_active_users')
    mau = pd.read_sql(mau_query, engine)
    print("Monthly Active Users:")
    print(mau.head(10))

    revenue_query = load_query('revenue_by_segment')
    revenue = pd.read_sql(revenue_query, engine)
    print("\nRevenue by Segment:")
    print(revenue.head(10))

    funnel_query = load_query('conversion_funnel')
    funnel = pd.read_sql(funnel_query, engine)
    print("\nConversion Funnel:")
    print(funnel.head(10))

    print("\n=== TASK 5: Validating Query Results ===")
    validate_metrics(mau, revenue, funnel)


if __name__ == "__main__":
    main()
