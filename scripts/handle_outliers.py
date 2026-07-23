import os
import numpy as np
import pandas as pd
from scipy import stats
from pathlib import Path

# -------------------------------------------------
# Project Paths
# -------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DATA = BASE_DIR / "data" / "raw" / "customer_revenue.csv"
PROCESSED_DATA = BASE_DIR / "data" / "processed" / "customer_revenue_clean.csv"
OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

# -------------------------------------------------
# Main Outlier Pipeline
# -------------------------------------------------
if __name__ == "__main__":
    print("\nStarting Outlier Detection and Handling Pipeline...\n")

    # Load dataset
    df = pd.read_csv(RAW_DATA)
    print(f"Loaded dataset from: {RAW_DATA}")
    print(f"Initial shape: {df.shape}\n")

    print("=" * 60)
    print("BEFORE CLEANING - DESCRIPTIVE STATISTICS")
    print("=" * 60)
    print(df.describe())
    print("=" * 60 + "\n")

    # Task 1: Z-Score Outlier Detection
    df['revenue_zscore'] = np.abs(stats.zscore(df['revenue']))
    z_outliers = df[df['revenue_zscore'] > 3]
    print(f"Z-score outliers: {len(z_outliers)}")

    # Task 2: IQR Outlier Detection
    Q1 = df['revenue'].quantile(0.25)
    Q3 = df['revenue'].quantile(0.75)
    IQR = Q3 - Q1

    lower = Q1 - 1.5 * IQR
    upper = Q3 + 1.5 * IQR

    df['is_outlier_iqr'] = (df['revenue'] < lower) | (df['revenue'] > upper)
    iqr_outliers_count = df['is_outlier_iqr'].sum()
    print(f"IQR outliers: {iqr_outliers_count}")

    # Task 3: Cap Outliers at Boundaries
    df['revenue_capped'] = df['revenue'].clip(lower=lower, upper=upper)
    print(f"\nRevenue Capping Verification:")
    print(f"  Before: min={df['revenue'].min()}, max={df['revenue'].max()}")
    print(f"  After:  min={df['revenue_capped'].min()}, max={df['revenue_capped'].max()}")

    # Task 4: Flag Outliers with Binary Column
    df['is_outlier'] = (df['is_outlier_iqr']) | (df['revenue_zscore'] > 3)
    normal = df[~df['is_outlier']]
    anomalies = df[df['is_outlier']]
    print(f"\nAnomalies Flagging Summary:")
    print(f"  Normal records: {len(normal)}")
    print(f"  Anomalies: {len(anomalies)}\n")

    # -------------------------------------------------
    # Column-Specific Handling Decisions
    # -------------------------------------------------
    # 1. Revenue column is capped at IQR boundaries (Task 3 strategy)
    # 2. Age column has impossible values (150+ years), so we remove these rows
    age_threshold = 120
    age_outliers_mask = df['age'] > age_threshold
    age_outliers_count = age_outliers_mask.sum()
    print(f"Age Outliers (age > {age_threshold}): {age_outliers_count}")

    # Apply handling decisions
    # Remove impossible age rows
    df_cleaned = df[~age_outliers_mask].copy()
    
    # Use capped revenue as clean revenue
    df_cleaned['revenue'] = df_cleaned['revenue_capped']

    # Keep only target columns for cleaned dataset
    clean_columns = ['customer_id', 'revenue', 'age']
    df_final = df_cleaned[clean_columns]

    # Task 5: Create Cleaning Log
    cleaning_log = [
        {
            'column': 'revenue',
            'method': 'IQR',
            'action': 'cap',
            'threshold_lower': lower,
            'threshold_upper': upper,
            'affected_rows': int(iqr_outliers_count),
            'date': pd.Timestamp.now()
        },
        {
            'column': 'age',
            'method': 'Logic Threshold',
            'action': 'remove',
            'threshold_lower': 0,
            'threshold_upper': age_threshold,
            'affected_rows': int(age_outliers_count),
            'date': pd.Timestamp.now()
        }
    ]

    log_df = pd.DataFrame(cleaning_log)
    log_file = OUTPUT_DIR / 'cleaning_log.csv'
    log_df.to_csv(log_file, index=False)
    print(f"\nSuccess: Cleaning log saved to: {log_file}")

    # Save cleaned dataset
    df_final.to_csv(PROCESSED_DATA, index=False)
    print(f"Success: Cleaned dataset saved to: {PROCESSED_DATA}\n")

    print("=" * 60)
    print("AFTER CLEANING - DESCRIPTIVE STATISTICS")
    print("=" * 60)
    print(df_final.describe())
    print("=" * 60 + "\n")
