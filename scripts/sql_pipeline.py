"""
SQL Database Integration Pipeline

Tasks Implemented:
1. Task 1: Setup Database Connection
2. Task 2: Load Cleaned DataFrame as Table
3. Task 3: Validate Schema
4. Task 4: Query and Return Results
5. Task 5: Make Loading Repeatable
"""

import os
import sys
from pathlib import Path
import pandas as pd
from sqlalchemy import create_engine, inspect, Integer, String, Date, Float

# Ensure UTF-8 output encoding for Windows terminal compatibility
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass


# Project Root Directory
BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "analytics.db"

# Documentation for PostgreSQL production connection (without hardcoded credentials):
# For production PostgreSQL deployments, use environment variables to build the connection URI:
# DB_USER = os.getenv("DB_USER", "postgres")
# DB_PASSWORD = os.getenv("DB_PASSWORD", "secret")
# DB_HOST = os.getenv("DB_HOST", "localhost")
# DB_PORT = os.getenv("DB_PORT", "5432")
# DB_NAME = os.getenv("DB_NAME", "analytics")
# postgres_uri = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
# engine = create_engine(postgres_uri)


def prepare_sample_cleaned_data() -> pd.DataFrame:
    """
    Prepare sample clean customer DataFrame matching required schema.
    
    Columns: customer_id, email, signup_date, customer_type, lifetime_value
    """
    raw_file = BASE_DIR / "data" / "raw" / "customer_segmentation_data.csv"
    if raw_file.exists():
        df = pd.read_csv(raw_file)
        df_clean = df[['customer_id', 'customer_type', 'lifetime_value']].copy()
        df_clean['email'] = df_clean['customer_id'].apply(lambda cid: f"customer_{cid}@example.com")
        df_clean['signup_date'] = pd.to_datetime('2023-01-01') + pd.to_timedelta(df_clean['customer_id'] % 365, unit='D')
        df_clean['signup_date'] = df_clean['signup_date'].dt.date
    else:
        df_clean = pd.DataFrame({
            'customer_id': [1001, 1002, 1003, 1004, 1005],
            'email': ['user1@example.com', 'user2@example.com', 'user3@example.com', 'user4@example.com', 'user5@example.com'],
            'signup_date': [pd.to_datetime('2023-01-15').date(), pd.to_datetime('2023-02-20').date(), pd.to_datetime('2023-03-10').date(), pd.to_datetime('2023-04-05').date(), pd.to_datetime('2023-05-12').date()],
            'customer_type': ['Enterprise', 'Startup', 'SMB', 'Enterprise', 'Startup'],
            'lifetime_value': [125000.50, 2500.00, 8500.75, 140000.00, 1800.25]
        })
    return df_clean


# ---------------------------------------------------------
# Task 1: Setup Database Connection
# ---------------------------------------------------------
def setup_database_connection(db_path=DB_PATH):
    """
    Task 1: Setup Database Connection
    Setup SQLite engine with SQLAlchemy and test connection.
    """
    connection_string = f"sqlite:///{db_path}"
    engine = create_engine(connection_string)

    # Test connection
    with engine.connect() as conn:
        print("✓ Database connection successful")

    return engine


# ---------------------------------------------------------
# Task 2: Load Cleaned DataFrame as Table
# ---------------------------------------------------------
def load_dataframe_to_table(df, engine, table_name="customers_cleaned"):
    """
    Task 2: Load Cleaned DataFrame as Table
    Loads df to database table with if_exists='replace', index=False.
    """
    dtype_mapping = {
        'customer_id': Integer(),
        'email': String(),
        'signup_date': Date(),
        'customer_type': String(),
        'lifetime_value': Float()
    }

    df.to_sql(table_name, engine, if_exists='replace', index=False, dtype=dtype_mapping)

    # Verify table created using inspector
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print("Existing tables in database:", tables)

    # Check row count via SQL query
    count = pd.read_sql(f"SELECT COUNT(*) as row_count FROM {table_name}", engine)
    rows_loaded = count.iloc[0]['row_count']
    print(f"Rows loaded: {rows_loaded}")

    return rows_loaded


# ---------------------------------------------------------
# Task 3: Validate Schema
# ---------------------------------------------------------
def validate_table_schema(engine, table_name="customers_cleaned"):
    """
    Task 3: Validate Schema
    Inspects table schema and validates expected column data types.
    """
    inspector = inspect(engine)
    columns = inspector.get_columns(table_name)

    print("\nTABLE SCHEMA:")
    for col in columns:
        not_null_str = 'NOT NULL' if col['nullable'] == False else ''
        print(f"  {col['name']:20} {str(col['type']):15} {not_null_str}")

    print("\nDATATYPE VALIDATION:")
    expected_types = {
        'customer_id': 'INTEGER',
        'email': 'VARCHAR',
        'signup_date': 'DATE'
    }

    validation_results = {}
    for col_name, expected_type in expected_types.items():
        matching_cols = [c['type'] for c in columns if c['name'] == col_name]
        if matching_cols:
            actual = matching_cols[0]
            status = '✓' if expected_type.upper() in str(actual).upper() else '✗'
            print(f"{status} {col_name}: {actual}")
            validation_results[col_name] = (status == '✓')
        else:
            print(f"✗ {col_name}: Column not found in table")
            validation_results[col_name] = False

    return columns, validation_results


# ---------------------------------------------------------
# Task 4: Query and Return Results
# ---------------------------------------------------------
def query_and_return_results(engine, table_name="customers_cleaned"):
    """
    Task 4: Query and Return Results
    Executes simple and complex aggregation SELECT queries.
    """
    query = f"SELECT * FROM {table_name} WHERE customer_type = 'Enterprise'"
    results = pd.read_sql(query, engine)

    print(f"\nRetrieved {len(results)} rows for Enterprise customers:")
    print(results.head())

    query_agg = f"""
SELECT 
    customer_type,
    COUNT(*) as count,
    AVG(lifetime_value) as avg_ltv
FROM {table_name}
GROUP BY customer_type
ORDER BY avg_ltv DESC
"""

    summary = pd.read_sql(query_agg, engine)
    print("\nSummary by segment:")
    print(summary)

    return results, summary


# ---------------------------------------------------------
# Task 5: Make Loading Repeatable
# ---------------------------------------------------------
def load_cleaned_data_to_database(df, table_name, database_path='analytics.db'):
    """
    Load cleaned DataFrame to database - repeatable function.

    Parameters:
        df (pd.DataFrame): Cleaned DataFrame to load into the database.
        table_name (str): Name of the target SQL table.
        database_path (str or Path): Path to SQLite database file.
            Note: For PostgreSQL production use, connection string format:
            'postgresql://<username>:<password>@<host>:<port>/<dbname>'
            configured securely via environment variables.

    Returns:
        sqlalchemy.engine.Engine: SQLAlchemy engine object for reuse.
    """
    dtype_mapping = {
        'customer_id': Integer(),
        'email': String(),
        'signup_date': Date(),
        'customer_type': String(),
        'lifetime_value': Float()
    }

    engine = create_engine(f'sqlite:///{database_path}')
    
    df.to_sql(table_name, engine, if_exists='replace', index=False, dtype=dtype_mapping)
    
    count = pd.read_sql(f"SELECT COUNT(*) as ct FROM {table_name}", engine)
    rows_loaded = count.iloc[0]['ct']
    
    print(f"✓ Loaded {rows_loaded} rows to {table_name}")
    return engine


def main():
    print("=== TASK 1: Setup Database Connection ===")
    engine = setup_database_connection()

    print("\n=== TASK 2: Load Cleaned DataFrame as Table ===")
    df_clean = prepare_sample_cleaned_data()
    load_dataframe_to_table(df_clean, engine)

    print("\n=== TASK 3: Validate Schema ===")
    validate_table_schema(engine)

    print("\n=== TASK 4: Query and Return Results ===")
    query_and_return_results(engine)

    print("\n=== TASK 5: Make Loading Repeatable ===")
    engine_repeatable = load_cleaned_data_to_database(df_clean, 'customers_cleaned', database_path=DB_PATH)
    results = pd.read_sql("SELECT * FROM customers_cleaned LIMIT 10", engine_repeatable)
    print("\nRepeatable load verification - Sample 10 rows:")
    print(results)


if __name__ == "__main__":
    main()
