import os
import pandas as pd
from pathlib import Path

# -------------------------------------------------
# Project Paths
# -------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DATA = BASE_DIR / "data" / "raw" / "customer_transactions.csv"
PROCESSED_DATA = BASE_DIR / "data" / "processed" / "customer_features.csv"

# -------------------------------------------------
# Main Feature Engineering Pipeline
# -------------------------------------------------
if __name__ == "__main__":
    print("\nStarting Feature Engineering Pipeline...\n")

    # Load dataset
    df = pd.read_csv(RAW_DATA)
    print(f"Loaded dataset from: {RAW_DATA}")
    print(f"Initial shape: {df.shape}\n")

    # -------------------------------------------------
    # Task 1: Compute Ratio Features
    # -------------------------------------------------
    print("Executing Task 1: Computing Ratio Features...")
    df['transactions_per_month'] = df['total_transactions'] / (df['days_as_customer'] / 30)
    df['avg_spend_per_transaction'] = df['total_spent'] / df['total_transactions']
    df['lifetime_value_per_month'] = df['total_spent'] / (df['days_as_customer'] / 30)

    print("\nDescriptive statistics for ratio features:")
    print(df[['transactions_per_month', 'avg_spend_per_transaction']].describe())
    print("-" * 60 + "\n")

    # -------------------------------------------------
    # Task 2: Binning with Equal-Width Bins
    # -------------------------------------------------
    print("Executing Task 2: Equal-Width Binning...")
    df['engagement_tier'] = pd.cut(
        df['transactions_per_month'],
        bins=[0, 2, 10, float('inf')],
        labels=['low', 'medium', 'high']
    )

    print("\nEngagement tier distribution:")
    print(df['engagement_tier'].value_counts())
    print("-" * 60 + "\n")

    # -------------------------------------------------
    # Task 3: Binning with Quantiles
    # -------------------------------------------------
    print("Executing Task 3: Quantile Binning...")
    df['spend_quartile'] = pd.qcut(
        df['total_spent'],
        q=4,
        labels=['Q1', 'Q2', 'Q3', 'Q4']
    )

    print("\nSpend quartile distribution:")
    print(df['spend_quartile'].value_counts())
    print("-" * 60 + "\n")

    # -------------------------------------------------
    # Task 4: Composite Score (RFM)
    # -------------------------------------------------
    print("Executing Task 4: Generating Composite RFM Score...")
    df['recency_score'] = pd.qcut(df['days_since_last_purchase'], q=5, labels=[5, 4, 3, 2, 1])
    df['frequency_score'] = pd.qcut(df['purchase_count'], q=5, labels=[1, 2, 3, 4, 5])
    df['monetary_score'] = pd.qcut(df['total_spent'], q=5, labels=[1, 2, 3, 4, 5])

    df['rfm_score'] = (df['recency_score'].astype(int) + 
                       df['frequency_score'].astype(int) + 
                       df['monetary_score'].astype(int))
    
    print("\nRFM Score stats:")
    print(df['rfm_score'].describe())
    print("-" * 60 + "\n")

    # -------------------------------------------------
    # Task 5: Feature Validation
    # -------------------------------------------------
    print("Executing Task 5: Feature Validation...")
    # Check ranges are sensible
    print(f"Engagement tier distribution:\n{df['engagement_tier'].value_counts()}")
    print(f"RFM score range: {df['rfm_score'].min()}-{df['rfm_score'].max()}")

    # Ensure no NaNs introduced
    nan_counts = df[['engagement_tier', 'spend_quartile', 'rfm_score']].isna().sum()
    print(f"Missing values:\n{nan_counts}")
    print("-" * 60 + "\n")

    # Ensure processed directory exists
    os.makedirs(PROCESSED_DATA.parent, exist_ok=True)

    # Save to processed data folder
    df.to_csv(PROCESSED_DATA, index=False)
    print(f"Success: Engineered features saved to: {PROCESSED_DATA}")
