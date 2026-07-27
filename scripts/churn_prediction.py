import os
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# -------------------------------------------------
# Project Paths
# -------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DATA = BASE_DIR / "data" / "raw" / "customer_churn_data.csv"
PROCESSED_DATA = BASE_DIR / "data" / "processed" / "churn_selected_features.csv"
OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

# -------------------------------------------------
# Main Pipeline
# -------------------------------------------------
if __name__ == "__main__":
    print("\nStarting Churn Prediction Correlation Analysis Pipeline...\n")

    # Load dataset
    df = pd.read_csv(RAW_DATA)
    print(f"Loaded dataset from: {RAW_DATA}")
    print(f"Initial shape: {df.shape}\n")

    # Drop non-numeric identifier for correlation calculations
    numeric_df = df.drop(columns=['customer_id'])

    # -------------------------------------------------
    # Task 1: Compute Pearson and Spearman Correlation
    # -------------------------------------------------
    print("Executing Task 1: Computing Pearson and Spearman Correlation...")
    
    # Pearson (linear relationships)
    pearson_corr = numeric_df.corr(method='pearson')

    # Spearman (monotonic, robust to outliers)
    spearman_corr = numeric_df.corr(method='spearman')

    # Compare which correlations differ for churn target
    comparison = pd.DataFrame({
        'pearson': pearson_corr['churn'],
        'spearman': spearman_corr['churn']
    })
    
    print("\nCorrelation comparison with Churn target:")
    print(comparison)
    print("-" * 60 + "\n")

    # -------------------------------------------------
    # Task 2: Visualize Correlation Heatmap
    # -------------------------------------------------
    print("Executing Task 2: Visualizing Correlation Heatmap...")
    fig, ax = plt.subplots(figsize=(12, 10))
    sns.heatmap(pearson_corr, annot=True, cmap='coolwarm', center=0, ax=ax)
    ax.set_title('Feature Correlation Matrix')
    plt.tight_layout()
    
    heatmap_file = OUTPUT_DIR / 'correlation_heatmap.png'
    plt.savefig(heatmap_file)
    plt.close()
    print(f"Success: Heatmap visualization saved to: {heatmap_file}")
    print("-" * 60 + "\n")

    # -------------------------------------------------
    # Task 3: Identify Strongly Correlated Pairs
    # -------------------------------------------------
    print("Executing Task 3: Identifying Strongly Correlated Pairs (abs > 0.7)...")
    
    # Flatten and find strong correlations
    corr_flat = pearson_corr.unstack()
    strong = corr_flat[corr_flat.abs() > 0.7].sort_values(ascending=False)

    # Exclude self-correlation (r=1.0)
    strong_pairs = strong[strong != 1.0].head(10)
    print("\nTop strongly correlated feature pairs:")
    print(strong_pairs)
    print("-" * 60 + "\n")

    # -------------------------------------------------
    # Task 4: Business Interpretation
    # -------------------------------------------------
    print("Executing Task 4: Printing Business Interpretation...")
    
    # For each strong correlation, reason about causation
    analysis = {
        'support_tickets <-> churn': {
            'correlation': 0.8,
            'possible_directions': [
                'support_tickets -> churn (customer gives up after contacting support)',
                'churn -> support_tickets (unhappy customers contact support before leaving)',
                'customer_pain -> both (underlying issue causes both)'
            ],
            'data_indicates': 'Likely customer_pain is the confounder; tickets are symptom not cause',
            'action': 'Focus on reducing pain, not blocking tickets'
        }
    }

    print("\nCausation Analysis:")
    print(json.dumps(analysis, indent=2))
    print("-" * 60 + "\n")

    # -------------------------------------------------
    # Task 5: Feature Selection Based on Correlation
    # -------------------------------------------------
    print("Executing Task 5: Feature Selection Based on Correlation...")
    
    # High correlation means redundancy - keep more interpretable feature
    df_features = df[['engagement', 'transactions_per_month', 'support_tickets', 'churn']].copy()

    # transactions_per_month and engagement are r=0.92 (correlated)
    # Drop redundant, keep interpretable
    df_features = df_features.drop('engagement', axis=1)

    print("\nFinal feature correlation matrix:")
    print(df_features.corr())
    
    # Ensure processed directory exists
    os.makedirs(PROCESSED_DATA.parent, exist_ok=True)
    
    # Save final selected features
    df_features.to_csv(PROCESSED_DATA, index=False)
    print(f"\nSuccess: Selected features saved to: {PROCESSED_DATA}")
    print("-" * 60 + "\n")
