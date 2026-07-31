import unittest
import pandas as pd
from sqlalchemy import create_engine
from scripts.sql_aggregation import (
    translate_to_sqlite,
    load_query,
    seed_sample_data,
    register_sqlite_translator
)

class TestSQLAggregation(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Set up in-memory database and seed sample data once for execution tests."""
        cls.engine = create_engine("sqlite:///:memory:")
        register_sqlite_translator(cls.engine)
        seed_sample_data(cls.engine)

    def test_translation_logic(self):
        """Test PostgreSQL to SQLite translation rules."""
        pg_sql_date = "SELECT * FROM transactions WHERE transaction_date >= DATE '2024-01-01'"
        sqlite_sql_date = translate_to_sqlite(pg_sql_date)
        self.assertIn(">= '2024-01-01'", sqlite_sql_date)
        self.assertNotIn("DATE '", sqlite_sql_date)

        pg_sql_trunc = "SELECT DATE_TRUNC('month', transaction_date)::DATE as month FROM transactions"
        sqlite_sql_trunc = translate_to_sqlite(pg_sql_trunc)
        self.assertIn("date(transaction_date, 'start of month')", sqlite_sql_trunc)
        self.assertNotIn("::DATE", sqlite_sql_trunc)

    def test_load_queries(self):
        """Verify all 5 SQL files load without errors and contain required SQL keywords."""
        q1 = load_query("where_filtering")
        q2 = load_query("groupby_aggregation")
        q3 = load_query("having_filtering")
        q4 = load_query("where_having_combined")
        q5 = load_query("orderby_ranking")

        self.assertIn("WHERE", q1)
        self.assertIn("GROUP BY", q2)
        self.assertIn("HAVING", q3)
        self.assertIn("WHERE", q4)
        self.assertIn("HAVING", q4)
        self.assertIn("RANK() OVER", q5)

    def test_task1_where_filtering(self):
        """Test Task 1: WHERE filtering execution."""
        q1 = load_query("where_filtering")
        df = pd.read_sql(q1, self.engine)
        self.assertFalse(df.empty)
        self.assertIn("customer_id", df.columns)
        self.assertIn("annual_revenue", df.columns)
        self.assertIn("transaction_count", df.columns)
        self.assertTrue((df["annual_revenue"] > 0).all())

    def test_task2_groupby_aggregation(self):
        """Test Task 2: GROUP BY and multi-metric aggregation."""
        q2 = load_query("groupby_aggregation")
        df = pd.read_sql(q2, self.engine)
        self.assertFalse(df.empty)
        self.assertIn("customer_type", df.columns)
        self.assertIn("month", df.columns)
        self.assertIn("unique_customers", df.columns)
        self.assertIn("monthly_revenue", df.columns)
        self.assertIn("avg_transaction", df.columns)

    def test_task3_having_filtering(self):
        """Test Task 3: HAVING clause group filtering."""
        q3 = load_query("having_filtering")
        df = pd.read_sql(q3, self.engine)
        self.assertFalse(df.empty)
        self.assertIn("customer_id", df.columns)
        self.assertTrue((df["annual_revenue"] > 10000).all())
        self.assertTrue((df["transaction_count"] >= 5).all())

    def test_task4_where_having_combined(self):
        """Test Task 4: Combined WHERE and HAVING filtering."""
        q4 = load_query("where_having_combined")
        df = pd.read_sql(q4, self.engine)
        self.assertIn("customer_type", df.columns)
        self.assertIn("segment_customers", df.columns)
        self.assertIn("segment_revenue", df.columns)
        # Verify HAVING thresholds are satisfied for any returned rows
        if not df.empty:
            self.assertTrue((df["segment_customers"] >= 100).all())
            self.assertTrue((df["segment_revenue"] > 100000).all())

    def test_task5_orderby_ranking(self):
        """Test Task 5: ORDER BY ranking with RANK() window function."""
        q5 = load_query("orderby_ranking")
        df = pd.read_sql(q5, self.engine)
        self.assertFalse(df.empty)
        self.assertIn("customer_type", df.columns)
        self.assertIn("industry", df.columns)
        self.assertIn("revenue_rank", df.columns)
        self.assertTrue((df["customers"] >= 10).all())
        # Check that top rank is 1
        self.assertEqual(df["revenue_rank"].iloc[0], 1)


if __name__ == "__main__":
    unittest.main()
