import os
import sys
import unittest
from pathlib import Path
import pandas as pd
from sqlalchemy import inspect, create_engine

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass


from scripts.sql_pipeline import (
    setup_database_connection,
    prepare_sample_cleaned_data,
    load_dataframe_to_table,
    validate_table_schema,
    query_and_return_results,
    load_cleaned_data_to_database,
)

BASE_DIR = Path(__file__).resolve().parent.parent
TEST_DB_PATH = BASE_DIR / "test_analytics.db"


class TestSQLPipeline(unittest.TestCase):

    def setUp(self):
        if TEST_DB_PATH.exists():
            try:
                os.remove(TEST_DB_PATH)
            except PermissionError:
                pass

    def tearDown(self):
        if TEST_DB_PATH.exists():
            try:
                os.remove(TEST_DB_PATH)
            except PermissionError:
                pass

    def test_task1_setup_database_connection(self):
        engine = setup_database_connection(TEST_DB_PATH)
        with engine.connect() as conn:
            self.assertIsNotNone(conn)

    def test_task2_load_dataframe_to_table(self):
        engine = setup_database_connection(TEST_DB_PATH)
        df_clean = prepare_sample_cleaned_data()
        rows_loaded = load_dataframe_to_table(df_clean, engine, "customers_cleaned")
        
        self.assertEqual(rows_loaded, len(df_clean))
        inspector = inspect(engine)
        self.assertIn("customers_cleaned", inspector.get_table_names())

    def test_task3_validate_schema(self):
        engine = setup_database_connection(TEST_DB_PATH)
        df_clean = prepare_sample_cleaned_data()
        load_dataframe_to_table(df_clean, engine, "customers_cleaned")

        columns, validation_results = validate_table_schema(engine, "customers_cleaned")
        
        col_names = [c["name"] for c in columns]
        self.assertIn("customer_id", col_names)
        self.assertIn("email", col_names)
        self.assertIn("signup_date", col_names)
        
        # Check datatype validation results
        self.assertTrue(validation_results["customer_id"])
        self.assertTrue(validation_results["email"])
        self.assertTrue(validation_results["signup_date"])

    def test_task4_query_and_return_results(self):
        engine = setup_database_connection(TEST_DB_PATH)
        df_clean = prepare_sample_cleaned_data()
        load_dataframe_to_table(df_clean, engine, "customers_cleaned")

        enterprise_df, summary_df = query_and_return_results(engine, "customers_cleaned")
        
        self.assertIsInstance(enterprise_df, pd.DataFrame)
        self.assertIsInstance(summary_df, pd.DataFrame)
        self.assertIn("customer_type", summary_df.columns)
        self.assertIn("avg_ltv", summary_df.columns)

    def test_task5_load_cleaned_data_to_database(self):
        df_clean = prepare_sample_cleaned_data()
        engine = load_cleaned_data_to_database(df_clean, "customers_cleaned", TEST_DB_PATH)
        
        self.assertIsNotNone(engine)
        res = pd.read_sql("SELECT COUNT(*) as ct FROM customers_cleaned", engine)
        self.assertEqual(res.iloc[0]["ct"], len(df_clean))


if __name__ == "__main__":
    unittest.main()
