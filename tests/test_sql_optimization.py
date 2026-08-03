"""
Unit Tests for SQL Query Refactoring & Optimization Pipeline
Verifies execution, result correctness, metric reduction, and CTE structure.
"""

import unittest
import numpy as np
import pandas as pd
from scripts.sql_optimization import (
    get_db_engine,
    seed_synthetic_data,
    run_task1,
    run_task2,
    run_task3,
    run_task4
)


class TestSQLOptimization(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Setup SQLite engine and seed synthetic database."""
        cls.engine = get_db_engine()
        seed_synthetic_data(cls.engine)

    def test_task1_explicit_columns(self):
        """Verify Task 1 column selection reduction and data matching."""
        orig_df, opt_df = run_task1(self.engine)
        
        # Check column reduction
        self.assertGreater(orig_df.shape[1], opt_df.shape[1])
        self.assertEqual(opt_df.shape[1], 7)
        self.assertIn('transaction_id', opt_df.columns)
        self.assertIn('customer_name', opt_df.columns)
        self.assertIn('country', opt_df.columns)
        self.assertIn('account_type', opt_df.columns)
        
        # Check matching core values
        self.assertTrue((orig_df['transaction_id'] == opt_df['transaction_id']).all())
        self.assertTrue((orig_df['amount'] == opt_df['amount']).all())

    def test_task2_filter_before_joins(self):
        """Verify Task 2 filtering before joins yields identical results."""
        inefficient_df, efficient_df = run_task2(self.engine)
        
        self.assertEqual(len(inefficient_df), len(efficient_df))
        self.assertTrue((inefficient_df['transaction_id'] == efficient_df['transaction_id']).all())
        self.assertTrue((inefficient_df['amount'] == efficient_df['amount']).all())

    def test_task3_cte_refactoring(self):
        """Verify Task 3 CTE refactoring produces identical segment metrics."""
        nested_df, cte_df = run_task3(self.engine)
        
        self.assertEqual(len(nested_df), len(cte_df))
        n_sorted = nested_df.sort_values('customer_segment').reset_index(drop=True)
        c_sorted = cte_df.sort_values('customer_segment').reset_index(drop=True)
        
        self.assertTrue(np.allclose(n_sorted['avg_transaction_value'], c_sorted['avg_transaction_value']))

    def test_task4_comparison_dataframe(self):
        """Verify Task 4 comparison DataFrame generation."""
        comp_df = run_task4()
        
        self.assertEqual(list(comp_df.columns), ['Metric', 'Original', 'Optimized'])
        self.assertEqual(len(comp_df), 5)


if __name__ == '__main__':
    unittest.main()
