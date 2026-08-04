import os
import sys
import unittest
import importlib
import pandas as pd
from sqlalchemy import inspect

# Ensure root directory is in sys.path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# Import from assignment-33-python dynamically due to hyphen in filename
assignment = importlib.import_module("assignment-33-python")

def setUpModule():
    """Ensure database, views, and pre-aggregated tables are initialized."""
    assignment.main()

class TestDataLayer(unittest.TestCase):

    def test_datediff_function(self):
        """Verify the custom DATEDIFF SQL function logic in SQLite."""
        self.assertEqual(assignment.sqlite_datediff("2026-08-03", "2026-08-01"), 2)
        self.assertEqual(assignment.sqlite_datediff("2026-08-01", "2026-08-03"), -2)
        self.assertIsNone(assignment.sqlite_datediff(None, "2026-08-01"))

    def test_sql_translation(self):
        """Verify the interval/date translation helper regex checks."""
        sql = "AND o.order_date >= CURRENT_DATE - INTERVAL 30 DAY"
        translated = assignment.translate_to_sqlite(sql)
        self.assertIn("date('now', '-30 days')", translated)
        self.assertNotIn("INTERVAL 30 DAY", translated)

    def test_views_existence_and_columns(self):
        """Ensure both SQL views exist and return correct columns."""
        inspector = inspect(assignment.engine)
        views = inspector.get_view_names()
        self.assertIn("vw_active_customers", views)
        self.assertIn("vw_your_custom_metric", views)
        
        # Check columns of vw_active_customers
        columns = [c['name'] for c in inspector.get_columns("vw_active_customers")]
        self.assertIn("customer_id", columns)
        self.assertIn("order_count_30d", columns)
        self.assertIn("revenue_30d", columns)
        self.assertIn("days_since_order", columns)

        # Check columns of custom metric
        custom_cols = [c['name'] for c in inspector.get_columns("vw_your_custom_metric")]
        self.assertIn("customer_id", custom_cols)
        self.assertIn("total_spent", custom_cols)
        self.assertIn("days_inactive", custom_cols)
        self.assertIn("churn_risk", custom_cols)

    def test_aggregated_table_existence_and_timestamps(self):
        """Verify the pre-aggregated summary table is present and has valid timestamp records."""
        inspector = inspect(assignment.engine)
        tables = inspector.get_table_names()
        self.assertIn("agg_daily_metrics", tables)
        
        df = pd.read_sql("SELECT * FROM agg_daily_metrics", assignment.engine)
        self.assertFalse(df.empty)
        self.assertIn("updated_at", df.columns)
        self.assertTrue((df["updated_at"].notnull()).all())

    def test_active_customers_soft_deleted_filtering(self):
        """Ensure soft-deleted customers are correctly filtered out from the active customers view."""
        df = pd.read_sql("SELECT * FROM vw_active_customers WHERE customer_id = 104", assignment.engine)
        self.assertTrue(df.empty, "Soft-deleted customer 104 should be filtered out from the view")

    def test_custom_cohort_rules(self):
        """Validate that customer risk cohort views conform to business threshold logic."""
        df = pd.read_sql("SELECT * FROM vw_your_custom_metric", assignment.engine)
        self.assertFalse(df.empty, "Custom cohort should have high-value inactive customers")
        for _, row in df.iterrows():
            self.assertGreater(row['total_spent'], 500.0)
            self.assertGreater(row['days_inactive'], 30)

if __name__ == "__main__":
    unittest.main()
