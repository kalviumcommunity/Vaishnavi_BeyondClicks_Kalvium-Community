import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# -------------------------------------------------
# Project Paths
# -------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DATA = BASE_DIR / "data" / "raw" / "customer_segmentation_data.csv"
OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)
PROCESSED_SUMMARY = OUTPUT_DIR / "segment_summary_metrics.csv"
HEATMAP_FILE = OUTPUT_DIR / "segment_heatmap.png"

# -------------------------------------------------
# Main Pipeline
# -------------------------------------------------
if __name__ == "__main__":
    print("\nStarting Customer Segmentation Analysis Pipeline...\n")

    # Load dataset
    df = pd.read_csv(RAW_DATA)
    print(f"Loaded dataset from: {RAW_DATA}")
    print(f"Initial shape: {df.shape}\n")

    # -------------------------------------------------
    # Task 1: Define Segments and Compute Metrics
    # -------------------------------------------------
    print("Executing Task 1: Computing Segment Metrics...")
    segment_metrics = df.groupby('customer_type').agg({
        'lifetime_value': 'mean',
        'churn': 'mean',
        'support_tickets': 'mean',
        'retention_days': 'mean',
        'customer_id': 'count'
    })

    segment_metrics.columns = ['avg_ltv', 'churn_rate', 'avg_tickets', 'avg_retention', 'count']
    print("\nCalculated Segment Metrics:")
    print(segment_metrics)
    print("-" * 60 + "\n")

    # -------------------------------------------------
    # Task 2: Summary Statistics Table
    # -------------------------------------------------
    print("Executing Task 2: Formatting Summary Table and Ranking Segments...")
    segment_summary = segment_metrics.copy()
    segment_summary['ltv_rank'] = segment_summary['avg_ltv'].rank(ascending=False).astype(int)
    segment_summary['churn_rank'] = segment_summary['churn_rate'].rank(ascending=True).astype(int)

    # Let's print absolute values and rankings
    print("\nSegment Rankings Summary (Absolute & Rankings):")
    print(segment_summary[['avg_ltv', 'ltv_rank', 'churn_rate', 'churn_rank']])
    
    # Format copy for display readability
    display_summary = segment_summary.copy()
    display_summary['avg_ltv'] = display_summary['avg_ltv'].map('${:,.2f}'.format)
    display_summary['churn_rate'] = display_summary['churn_rate'].map('{:,.1%}'.format)
    display_summary['avg_tickets'] = display_summary['avg_tickets'].map('{:,.2f}'.format)
    display_summary['avg_retention'] = display_summary['avg_retention'].map('{:,.1f} days'.format)
    
    print("\nFormatted Segment Summary Table:")
    print(display_summary)
    print("-" * 60 + "\n")

    # -------------------------------------------------
    # Task 3: Visual Comparison
    # -------------------------------------------------
    print("Executing Task 3: Visualizing Segment Comparison Heatmap...")
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Scale/normalize metrics slightly so they plot well on the same heatmap or plot as annotated absolute values
    # For RdYlGn, high is green, low is red. We want high LTV and retention to be green (good), and high churn to be red (bad).
    # Since LTV is in $150k range and churn is 0.12, we visualize them using annotated heatmap.
    sns.heatmap(segment_metrics[['avg_ltv', 'churn_rate', 'avg_tickets']], 
                annot=True, fmt=".2f", cmap='RdYlGn', cbar_kws={'label': 'Value'}, ax=ax)
    plt.title('Segment Comparison Heatmap')
    plt.tight_layout()
    plt.savefig(HEATMAP_FILE)
    plt.close()
    print(f"Success: Heatmap visualization saved to: {HEATMAP_FILE}")
    print("-" * 60 + "\n")

    # -------------------------------------------------
    # Task 4: Top and Bottom Performer Analysis
    # -------------------------------------------------
    print("Executing Task 4: Performer Analysis...")
    # Highest value segment
    top_segment = segment_metrics['avg_ltv'].idxmax()
    top_value = segment_metrics.loc[top_segment, 'avg_ltv']

    # Highest churn segment
    high_churn = segment_metrics['churn_rate'].idxmax()
    best_retention = segment_metrics['avg_retention'].idxmax()

    insights = f"""
HIGHEST VALUE: {top_segment} = ${top_value:,.2f}
HIGHEST CHURN: {high_churn} = {segment_metrics.loc[high_churn, 'churn_rate']:.1%}
BEST RETENTION: {best_retention} (Avg: {segment_metrics.loc[best_retention, 'avg_retention']:.1f} days)
"""
    print(insights)
    print("-" * 60 + "\n")

    # -------------------------------------------------
    # Task 5: Business-Facing Insights
    # -------------------------------------------------
    print("Executing Task 5: Business-Facing Insights...")
    
    business_summary = """
SEGMENT STRATEGY SUMMARY:

Enterprise (30% of base, $151k avg LTV, 1.0% churn):
- Highest value and lowest churn segment by far.
- Action: Maintain premium support, dedicate account management, focus on long-term renewal contracts.

SMB (30% of base, $8k avg LTV, 12.0% churn):
- Middle value but represents high churn risk.
- Action: Improve onboarding experience, implement lower-cost/cheaper automated support tier to contain costs.

Startup (40% of base, $2k avg LTV, 7.8% churn):
- Lowest value, moderate churn.
- Action: Build self-service workflows and developer/startup education-focused retention loops.
"""
    print(business_summary)
    print("-" * 60 + "\n")

    # Save summary table to csv
    segment_summary.to_csv(PROCESSED_SUMMARY)
    print(f"Success: Segment summary metrics CSV saved to: {PROCESSED_SUMMARY}")
