"""
Unit tests for insight_validation pipeline module.
Validates:
- Database seeding
- Dual-layer metric calculations
- Discrepancy flagging logic
- Reusable validate_metrics function and CSV export
"""

import os
import sys
import pytest
import pandas as pd
from sqlalchemy import create_engine

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from scripts.insight_validation import (
    engine,
    seed_database,
    get_python_metrics,
    validate_metrics
)


def test_seed_database():
    """Verify that seed_database populates logins and orders tables."""
    seed_database(engine)
    logins_count = pd.read_sql("SELECT COUNT(*) as ct FROM logins", engine).iloc[0, 0]
    orders_count = pd.read_sql("SELECT COUNT(*) as ct FROM orders", engine).iloc[0, 0]
    
    assert logins_count > 0, "logins table should not be empty"
    assert orders_count > 0, "orders table should not be empty"


def test_get_python_metrics():
    """Verify Python metric calculation helper returns expected dictionary keys."""
    metrics, logins_df, orders_df = get_python_metrics(engine)
    
    assert 'active_users' in metrics
    assert 'aov' in metrics
    assert 'churn' in metrics
    assert metrics['active_users'] > 0
    assert metrics['aov'] > 0
    assert metrics['churn'] >= 0


def test_validate_metrics_initial_discrepancy():
    """Verify that validate_metrics flags discrepancy in churn metric under initial SQL."""
    report = validate_metrics(engine, use_fixed_sql=False)
    
    assert isinstance(report, pd.DataFrame)
    assert len(report) == 3
    assert set(report.columns) == {
        'Metric', 'SQL', 'Python', 'Difference', 'Pct_Difference', 'Tolerance', 'Status', 'Timestamp'
    }
    
    # Churn should fail under initial SQL due to MONTH() bug
    churn_row = report[report['Metric'] == 'churn'].iloc[0]
    assert churn_row['Status'] == 'FAIL'
    assert churn_row['Pct_Difference'] > 0


def test_validate_metrics_fixed_sql():
    """Verify that validate_metrics passes all metrics after applying fixed SQL query."""
    report = validate_metrics(engine, use_fixed_sql=True)
    
    assert isinstance(report, pd.DataFrame)
    assert len(report) == 3
    
    # All metrics should pass
    failures = report[report['Status'] == 'FAIL']
    assert len(failures) == 0, f"All metrics should pass after SQL fix, but found failures:\n{failures}"


def test_validation_report_csv_generation(tmp_path):
    """Verify that validation report exports correctly to CSV format."""
    report = validate_metrics(engine, use_fixed_sql=True)
    csv_file = tmp_path / "test_report.csv"
    report.to_csv(csv_file, index=False)
    
    assert csv_file.exists()
    loaded_df = pd.read_csv(csv_file)
    assert len(loaded_df) == 3
    assert 'Status' in loaded_df.columns
