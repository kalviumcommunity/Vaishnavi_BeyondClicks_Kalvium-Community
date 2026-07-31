import unittest
import pandas as pd
from sqlalchemy import create_engine
from scripts.reusable_queries import (
    translate_to_sqlite,
    load_query,
    validate_metrics,
    seed_sample_data,
    register_sqlite_translator
)

class TestReusableQueries(unittest.TestCase):

    def test_translation_logic(self):
        pg_sql = "SELECT DATE_TRUNC('month', transaction_date)::DATE as month, NOW() - INTERVAL '12 months' FROM transactions"
        sqlite_sql = translate_to_sqlite(pg_sql)
        self.assertIn("date(transaction_date, 'start of month')", sqlite_sql)
        self.assertNotIn("::DATE", sqlite_sql)

        pg_funnel = "SELECT DATE_TRUNC('day', created_at)::DATE FROM users WHERE created_at >= NOW() - INTERVAL '90 days'"
        sqlite_funnel = translate_to_sqlite(pg_funnel)
        self.assertIn("date(created_at)", sqlite_funnel)
        self.assertIn("datetime('now', '-90 days')", sqlite_funnel)

    def test_load_queries(self):
        mau = load_query('monthly_active_users')
        revenue = load_query('revenue_by_segment')
        funnel = load_query('conversion_funnel')
        
        self.assertIn("DATE_TRUNC", mau)
        self.assertIn("FILTER", mau)
        self.assertIn("customer_type", revenue)
        self.assertIn("conversion_pct", funnel)

    def test_validation_passes(self):
        # Valid dataframes
        mau_df = pd.DataFrame({'month': ['2026-07-01'], 'active_users': [10]})
        revenue_df = pd.DataFrame({'month': ['2026-07-01'], 'monthly_revenue': [100.0], 'order_count': [5]})
        funnel_df = pd.DataFrame({'signup_date': ['2026-07-01'], 'conversion_pct': [50.0]})
        
        self.assertTrue(validate_metrics(mau_df, revenue_df, funnel_df))

    def test_validation_fails_on_nulls(self):
        mau_df = pd.DataFrame({'month': [None], 'active_users': [10]})
        revenue_df = pd.DataFrame({'month': ['2026-07-01'], 'monthly_revenue': [100.0], 'order_count': [5]})
        funnel_df = pd.DataFrame({'signup_date': ['2026-07-01'], 'conversion_pct': [50.0]})
        
        with self.assertRaises(AssertionError):
            validate_metrics(mau_df, revenue_df, funnel_df)

    def test_validation_fails_on_negative_revenue(self):
        mau_df = pd.DataFrame({'month': ['2026-07-01'], 'active_users': [10]})
        revenue_df = pd.DataFrame({'month': ['2026-07-01'], 'monthly_revenue': [-5.0], 'order_count': [5]})
        funnel_df = pd.DataFrame({'signup_date': ['2026-07-01'], 'conversion_pct': [50.0]})
        
        with self.assertRaises(AssertionError):
            validate_metrics(mau_df, revenue_df, funnel_df)

    def test_validation_fails_on_invalid_conversion_pct(self):
        mau_df = pd.DataFrame({'month': ['2026-07-01'], 'active_users': [10]})
        revenue_df = pd.DataFrame({'month': ['2026-07-01'], 'monthly_revenue': [100.0], 'order_count': [5]})
        funnel_df = pd.DataFrame({'signup_date': ['2026-07-01'], 'conversion_pct': [150.0]})
        
        with self.assertRaises(AssertionError):
            validate_metrics(mau_df, revenue_df, funnel_df)

    def test_database_execution(self):
        engine = create_engine("sqlite:///:memory:")
        register_sqlite_translator(engine)
        seed_sample_data(engine)
        
        # Test executing translated query
        mau_query = load_query('monthly_active_users')
        mau_df = pd.read_sql(mau_query, engine)
        self.assertFalse(mau_df.empty)
        self.assertIn('active_users', mau_df.columns)
        self.assertIn('enterprise_users', mau_df.columns)
        self.assertIn('smb_users', mau_df.columns)

        revenue_query = load_query('revenue_by_segment')
        revenue_df = pd.read_sql(revenue_query, engine)
        self.assertFalse(revenue_df.empty)
        self.assertIn('monthly_revenue', revenue_df.columns)

        funnel_query = load_query('conversion_funnel')
        funnel_df = pd.read_sql(funnel_query, engine)
        self.assertFalse(funnel_df.empty)
        self.assertIn('conversion_pct', funnel_df.columns)

        # Full validation
        self.assertTrue(validate_metrics(mau_df, revenue_df, funnel_df))
