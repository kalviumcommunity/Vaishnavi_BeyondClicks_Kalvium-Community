import os
from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd
from scipy import stats

# -------------------------------------------------
# Project Paths
# -------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DATA = BASE_DIR / "data" / "raw" / "customer_revenue.csv"
PROCESSED_DATA = BASE_DIR / "data" / "processed" / "customer_revenue_clean.csv"
OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)


def run_distribution_analysis():
    # Load dataset
    if RAW_DATA.exists():
        df = pd.read_csv(RAW_DATA)
        print(f"Loaded dataset from: {RAW_DATA}")
    elif PROCESSED_DATA.exists():
        df = pd.read_csv(PROCESSED_DATA)
        print(f"Loaded dataset from: {PROCESSED_DATA}")
    else:
        raise FileNotFoundError("Revenue dataset not found in data/raw/ or data/processed/")

    # Task 1: Distribution Plots (1 mark)
    print("=" * 60)
    print("TASK 1: DISTRIBUTION PLOTS")
    print("=" * 60)
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # Histogram
    axes[0].hist(df['revenue'], bins=50, edgecolor='black')
    axes[0].set_title('Revenue Distribution (Histogram)')
    axes[0].set_xlabel('Revenue')
    axes[0].set_ylabel('Frequency')

    # KDE
    df['revenue'].plot(kind='density', ax=axes[1])
    axes[1].set_title('Revenue Distribution (KDE)')
    axes[1].set_xlabel('Revenue')

    plt.tight_layout()
    plot_path = OUTPUT_DIR / 'revenue_distribution.png'
    plt.savefig(plot_path)
    plt.close()
    print(f"Saved distribution plot to: {plot_path}\n")

    # Task 2: Compute Skewness and Kurtosis (1 mark)
    print("=" * 60)
    print("TASK 2: COMPUTE SKEWNESS AND KURTOSIS")
    print("=" * 60)
    skewness = stats.skew(df['revenue'].dropna())
    kurtosis = stats.kurtosis(df['revenue'].dropna())

    print(f"Skewness: {skewness:.2f}")
    print(f"Kurtosis: {kurtosis:.2f}")

    if abs(skewness) > 1:
        print("Highly skewed - use median not mean")
    if kurtosis > 3:
        print("Heavy tails - expect outliers")
    print()

    # Task 3: Identify Abnormal Patterns (1 mark)
    print("=" * 60)
    print("TASK 3: IDENTIFY ABNORMAL PATTERNS")
    print("=" * 60)
    # Check for bimodality
    print("Descriptive Statistics:")
    print(df['revenue'].describe())
    print()

    # Percentiles show if distribution is bimodal
    percentiles = df['revenue'].quantile([0.25, 0.5, 0.75, 0.9, 0.95, 0.99])
    print("Percentiles:")
    print(percentiles)
    print()

    # Task 4: Compare Segment Distributions (1 mark)
    print("=" * 60)
    print("TASK 4: COMPARE SEGMENT DISTRIBUTIONS")
    print("=" * 60)
    high_value = df[df['revenue'] > df['revenue'].quantile(0.75)]
    low_value = df[df['revenue'] < df['revenue'].quantile(0.25)]

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    axes[0].hist(high_value['revenue'], bins=30, alpha=0.7, label='High-Value', color='green', edgecolor='black')
    axes[0].hist(low_value['revenue'], bins=30, alpha=0.7, label='Low-Value', color='blue', edgecolor='black')
    axes[0].legend()
    axes[0].set_title('Revenue: High vs Low Value Customers')
    axes[0].set_xlabel('Revenue')
    axes[0].set_ylabel('Frequency')

    high_value['revenue'].plot(kind='density', ax=axes[1], label='High-Value', color='green')
    low_value['revenue'].plot(kind='density', ax=axes[1], label='Low-Value', color='blue')
    axes[1].legend()
    axes[1].set_title('Revenue Density: High vs Low Value')
    axes[1].set_xlabel('Revenue')

    plt.tight_layout()
    segment_plot_path = OUTPUT_DIR / 'segment_distribution.png'
    plt.savefig(segment_plot_path)
    plt.close()
    print(f"Saved segment distribution plot to: {segment_plot_path}\n")

    # Compare metrics
    print(f"High-value: mean={high_value['revenue'].mean():.0f}, median={high_value['revenue'].median():.0f}")
    print(f"Low-value: mean={low_value['revenue'].mean():.0f}, median={low_value['revenue'].median():.0f}\n")

    # Task 5: Business Interpretation (1 mark)
    print("=" * 60)
    print("TASK 5: BUSINESS INTERPRETATION")
    print("=" * 60)
    interpretation = f"""
Revenue Distribution Analysis:

Skewness: {skewness:.2f} -> {"Highly right-skewed" if skewness > 1 else "Moderate"}
Mean: ${df['revenue'].mean():.0f}
Median: ${df['revenue'].median():.0f}
Interpretation: {'Most customers are small; few are huge enterprise accounts' if skewness > 1 else 'Balanced distribution'}

Kurtosis: {kurtosis:.2f} -> {"Fat tails (outliers)" if kurtosis > 3 else "Normal"}
Max: ${df['revenue'].max():.0f}
Top 1%: ${df['revenue'].quantile(0.99):.0f}

Business Action: {'Segment into small/enterprise for different strategies' if skewness > 1 else 'Uniform strategy'}
"""
    print(interpretation)


if __name__ == "__main__":
    run_distribution_analysis()
