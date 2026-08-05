import unittest
import os
import shutil
import pandas as pd
import plotly.express as px
from export_functions import export_analysis, translate_to_sqlite

class TestExports(unittest.TestCase):

    def setUp(self):
        self.output_dir = "test_export_output"
        os.makedirs(self.output_dir, exist_ok=True)
        
    def tearDown(self):
        if os.path.exists(self.output_dir):
            shutil.rmtree(self.output_dir)

    def test_export_pipeline(self):
        """Verify that export_analysis generates all required files."""
        df = pd.DataFrame({
            'date': ['2026-08-01', '2026-08-02'],
            'customer_id': [1, 2],
            'value': [100, 200]
        })
        summary = "# Test Summary\n- Finding 1: Success"
        fig = px.line(x=[1, 2], y=[10, 20])
        charts = {'Test Chart': fig}
        
        report_dir = export_analysis(df, summary, charts, self.output_dir)
        self.assertTrue(os.path.exists(report_dir))
        
        required_files = ['cleaned_data.csv', 'summary_report.pdf', 'interactive_report.html', 'README.md']
        for fname in required_files:
            self.assertTrue(os.path.exists(os.path.join(report_dir, fname)), f"Missing expected file: {fname}")
            
        # Verify CSV content is intact
        df_read = pd.read_csv(os.path.join(report_dir, 'cleaned_data.csv'))
        self.assertEqual(len(df_read), 2)
        
    def test_sql_translation(self):
        """Verify Postgres date interval expression translates correctly to SQLite."""
        sql = "WHERE date >= CURRENT_DATE - INTERVAL 30 DAY"
        translated = translate_to_sqlite(sql)
        self.assertIn("date('now', '-30 days')", translated)
