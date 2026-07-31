"""
SQL Aggregation & Filtering Demonstration Script

Implements and executes 5 SQL Tasks:
1. Task 1: WHERE Filtering (Data quality checks before grouping)
2. Task 2: GROUP BY and Aggregation (Multi-dimensional aggregation)
3. Task 3: HAVING Filtering (Group filtering after aggregation)
4. Task 4: WHERE + HAVING Combined (Combining row and group filters)
5. Task 5: ORDER BY Ranking (Window functions and top-N ranking)
"""

import os
import sys
import re
from pathlib import Path
import pandas as pd
import numpy as np
from sqlalchemy import create_engine, event

# Ensure UTF-8 output encoding for Windows terminal compatibility
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "output" / "sql_aggregation.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)


def translate_to_sqlite(sql_query: str) -> str:
    """
    Translates PostgreSQL / ANSI SQL syntax to SQLite dialect.
    Handles:
      - DATE 'YYYY-MM-DD' -> 'YYYY-MM-DD'
      - DATE_TRUNC('month', col)::DATE -> date(col, 'start of month')
      - DATE_TRUNC('month', col) -> date(col, 'start of month')
      - ::DATE casting operator removal
    """
    sql = sql_query

    # 1. Replace DATE 'YYYY-MM-DD' literals
    sql = re.sub(r"DATE\s+'([0-9]{4}-[0-9]{2}-[0-9]{2})'", r"'\1'", sql, flags=re.IGNORECASE)

    # 2. DATE_TRUNC month casting
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

    # 3. Remove remaining Postgres cast operators
    sql = re.sub(r"::DATE", "", sql, flags=re.IGNORECASE)

    return sql


def register_sqlite_translator(engine):
    """Registers SQLAlchemy event listener for dynamic query translation."""
    @event.listens_for(engine, "before_cursor_execute", retval=True)
    def receive_before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        translated_statement = translate_to_sqlite(statement)
        return translated_statement, parameters


def seed_sample_data(engine):
    """
    Seeds realistic sample datasets for customers and transactions into SQLite.
    """
    np.random.seed(42)

    # 1. Customers Table (1000 customers across types and industries)
    customer_types = ["Enterprise", "SMB", "Startup"]
    industries = ["Technology", "Healthcare", "Finance", "Retail", "Education"]

    customers_list = []
    for cid in range(1, 1001):
        c_type = np.random.choice(customer_types, p=[0.35, 0.45, 0.20])
        ind = np.random.choice(industries)
        customers_list.append({
            "customer_id": cid,
            "customer_type": c_type,
            "industry": ind
        })

    df_customers = pd.DataFrame(customers_list)
    df_customers.to_sql("customers", engine, if_exists="replace", index=False)

    # 2. Transactions Table (15000 transactions starting from 2024-01-01)
    dates = pd.date_range(start="2024-01-01", end="2024-12-31", freq="D")
    statuses = ["completed", "completed", "completed", "completed", "pending", "failed"]

    transactions_list = []
    for tid in range(1, 15001):
        cid = np.random.randint(1, 1001)
        tx_date = pd.to_datetime(np.random.choice(dates)).strftime("%Y-%m-%d")
        status = np.random.choice(statuses)
        # 5% refunds/negative amounts
        amount = round(float(np.random.exponential(scale=1200.0) + 50.0), 2)
        if np.random.rand() < 0.05:
            amount = -amount

        transactions_list.append({
            "transaction_id": tid,
            "customer_id": cid,
            "transaction_date": tx_date,
            "amount": amount,
            "transaction_status": status
        })

    df_transactions = pd.DataFrame(transactions_list)
    df_transactions.to_sql("transactions", engine, if_exists="replace", index=False)
    print("✓ Successfully seeded sample dataset (1,000 customers, 15,000 transactions).")


def load_query(query_name: str) -> str:
    """Loads SQL query from queries/{query_name}.sql file."""
    path = BASE_DIR / "queries" / f"{query_name}.sql"
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def execute_and_display(engine, query_name: str, task_title: str):
    """Executes a SQL query and displays formatted results."""
    print("\n" + "=" * 80)
    print(f"Executing {task_title} ({query_name}.sql)")
    print("=" * 80)

    raw_sql = load_query(query_name)
    df_result = pd.read_sql(raw_sql, engine)

    print("\nQuery Output (First 10 Rows):")
    print(df_result.head(10).to_string(index=False))
    print(f"\nTotal Rows Returned: {len(df_result)}")
    return df_result


def main():
    print("=== SQL AGGREGATION PIPELINE ===")
    engine = create_engine(f"sqlite:///{DB_PATH}")
    register_sqlite_translator(engine)
    seed_sample_data(engine)

    # Task 1: WHERE Filtering
    t1_df = execute_and_display(engine, "where_filtering", "Task 1: WHERE Filtering")

    # Task 2: GROUP BY & Aggregation
    t2_df = execute_and_display(engine, "groupby_aggregation", "Task 2: GROUP BY & Aggregation")

    # Task 3: HAVING Filtering
    t3_df = execute_and_display(engine, "having_filtering", "Task 3: HAVING Filtering")

    # Task 4: WHERE + HAVING Combined
    t4_df = execute_and_display(engine, "where_having_combined", "Task 4: WHERE + HAVING Combined")

    # Task 5: ORDER BY Ranking
    t5_df = execute_and_display(engine, "orderby_ranking", "Task 5: ORDER BY Ranking")

    print("\n=== PIPELINE EXECUTION COMPLETE ===")


if __name__ == "__main__":
    main()
