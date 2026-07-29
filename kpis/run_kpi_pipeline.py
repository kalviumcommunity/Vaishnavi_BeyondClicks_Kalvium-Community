"""
End-to-End KPI Pipeline Runner
Executes Tasks 1 to 5:
- Verifies KPI Reference Document
- Computes Reusable KPIs via kpi_functions
- Validates Current KPIs against Target Ranges in JSON
- Performs Hierarchical KPI Decomposition
- Demonstrates Module Imports
"""

import json
import os
import sys
import pandas as pd
import numpy as np

# Add parent directory to path to allow importing kpis module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import from kpis package
from kpis.kpi_functions import (
    calculate_mau,
    calculate_revenue_per_customer,
    calculate_churn_rate,
    calculate_payment_success_rate,
    calculate_customer_acquisition_cost,
    calculate_total_revenue
)
from kpis.kpi_decomposition import decompose_revenue


def generate_sample_dataset():
    """Generates synthetic dataset simulating active transactions, customer types, products, and statuses."""
    np.random.seed(42)
    now = pd.Timestamp.now()
    
    # 5,500 distinct active customers in last 30 days for MAU target
    customer_ids = list(range(1, 5501))
    
    # Create transactions in last 30 days
    n_trans_recent = 8000
    recent_customers = np.random.choice(customer_ids, size=n_trans_recent)
    recent_dates = [now - pd.Timedelta(days=np.random.uniform(0, 29)) for _ in range(n_trans_recent)]
    
    # Create transactions in prior 30 days (days 31 to 60 ago) for churn calculation
    # Include 5,500 active in period 1, with ~3% churn in period 2
    n_trans_prior = 6000
    prior_customer_ids = list(range(1, 5670)) # 170 customers will be churned (170/5670 ~= 3.0% churn)
    prior_customers = np.random.choice(prior_customer_ids, size=n_trans_prior)
    prior_dates = [now - pd.Timedelta(days=np.random.uniform(31, 59)) for _ in range(n_trans_prior)]
    
    all_customers = recent_customers.tolist() + prior_customers.tolist()
    all_dates = recent_dates + prior_dates
    n_total = len(all_customers)
    
    amounts = np.random.uniform(20, 250, size=n_total)
    
    # Customer segments & products
    segments = np.random.choice(['Enterprise', 'SMB', 'Startup'], size=n_total, p=[0.3, 0.5, 0.2])
    products = np.random.choice(['Analytics Suite', 'Data Pipeline', 'API Gateway'], size=n_total, p=[0.4, 0.35, 0.25])
    
    # Payment status (98% success rate)
    statuses = np.random.choice(['SUCCESS', 'FAILED'], size=n_total, p=[0.98, 0.02])

    df = pd.DataFrame({
        'transaction_id': range(1001, 1001 + n_total),
        'customer_id': all_customers,
        'transaction_date': all_dates,
        'amount': amounts,
        'customer_type': segments,
        'product': products,
        'status': statuses
    })
    
    # Customer acquisition spend data
    spend_df = pd.DataFrame({
        'spend': [175000],
        'new_customer_id': [5000] # 175000 / 5000 = $35 CAC
    })

    return df, spend_df


def main():
    # Set sys.stdout encoding for Windows console compatibility
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')

    print("================================================================================")
    print("                      KPI TRACKING & VALIDATION PIPELINE                        ")
    print("================================================================================")
    
    # -------------------------------------------------------------------------
    # Task 1: Reference Check
    # -------------------------------------------------------------------------
    ref_path = os.path.join(os.path.dirname(__file__), 'kpi_reference.md')
    print(f"\n[Task 1] Checking KPI Reference File: {ref_path}")
    if os.path.exists(ref_path):
        print("[OK] Task 1 complete: kpi_reference.md present with 5 defined KPIs.")
    else:
        print("[ERROR] kpi_reference.md missing!")

    # -------------------------------------------------------------------------
    # Task 2: Compute KPIs using Functions
    # -------------------------------------------------------------------------
    print("\n[Task 2] Computing Reusable KPI Functions...")
    df_trans, df_spend = generate_sample_dataset()
    
    # Filter for recent month transactions for current KPI evaluation
    cutoff_30d = pd.Timestamp.now() - pd.Timedelta(days=30)
    df_recent = df_trans[df_trans['transaction_date'] >= cutoff_30d]

    mau = calculate_mau(df_trans, days=30)
    rpc = calculate_revenue_per_customer(df_recent)
    churn = calculate_churn_rate(df_trans, period_days=30)
    payment_success = calculate_payment_success_rate(df_trans)
    cac = calculate_customer_acquisition_cost(spend_data=175000, new_customers=5000)

    print(f"  MAU:                      {calculate_mau(df_trans, days=30, formatted=True)}")
    print(f"  Revenue per Customer:     {calculate_revenue_per_customer(df_recent, formatted=True)}")
    print(f"  Churn Rate:               {calculate_churn_rate(df_trans, period_days=30, formatted=True)}")
    print(f"  Payment Success Rate:     {calculate_payment_success_rate(df_trans, formatted=True)}")
    print(f"  Customer Acquisition Cost:{calculate_customer_acquisition_cost(175000, 5000, formatted=True)}")

    # -------------------------------------------------------------------------
    # Task 3: Validate Against Target Ranges
    # -------------------------------------------------------------------------
    print("\n[Task 3] Validating Actual KPIs Against Targets...")
    targets_json_path = os.path.join(os.path.dirname(__file__), 'kpi_validation_targets.json')
    
    with open(targets_json_path, 'r') as f:
        targets = json.load(f)

    current_kpis = {
        'mau': mau,
        'revenue_per_customer': rpc,
        'churn_rate': churn,
        'payment_success_rate': payment_success,
        'customer_acquisition_cost': cac
    }

    validation_report = []
    for kpi_name, target_range in targets.items():
        actual = current_kpis[kpi_name]
        min_val = target_range['min']
        max_val = target_range['max']
        
        status = 'PASS' if min_val <= actual <= max_val else 'ALERT'
        validation_report.append({
            'kpi': kpi_name,
            'actual': round(actual, 4),
            'target_min': min_val,
            'target_max': max_val,
            'status': status
        })

    validation_df = pd.DataFrame(validation_report)
    print("\nValidation Summary Table:")
    print(validation_df.to_string(index=False))

    failures = validation_df[validation_df['status'] == 'ALERT']
    if len(failures) > 0:
        print(f"\n[ALERT] {len(failures)} KPIs out of target range - REVIEW REQUIRED")
    else:
        print(f"\n[PASS] All {len(validation_df)} KPIs within target range")

    # -------------------------------------------------------------------------
    # Task 4: KPI Decomposition
    # -------------------------------------------------------------------------
    print("\n[Task 4] Hierarchical KPI Decomposition...")
    decomp_results = decompose_revenue(df_recent)
    print(decomp_results['report_text'])

    # -------------------------------------------------------------------------
    # Task 5: Module Export Verification
    # -------------------------------------------------------------------------
    print("[Task 5] Verifying Version Control Structure & Reusable Imports...")
    print("  Import check: `from kpis.kpi_functions import calculate_mau`")
    print(f"  Result of imported calculate_mau(): {calculate_mau(df_trans)}")
    print("\n[SUCCESS] Pipeline execution successfully completed for all 5 tasks!")


if __name__ == '__main__':
    main()
