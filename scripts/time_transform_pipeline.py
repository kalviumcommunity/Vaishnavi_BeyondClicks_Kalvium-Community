import sys
import json
import pandas as pd
import numpy as np
from pathlib import Path
import sys
import json
import pandas as pd
import numpy as np
from pathlib import Path

try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False

# Ensure stdout handles UTF-8 characters on Windows terminals
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# -------------------------------------------------
# Project Paths
# -------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DATA_PATH = BASE_DIR / "data" / "raw" / "transaction_time_data.csv"
PROCESSED_DATA_PATH = BASE_DIR / "data" / "processed" / "time_transformed_data.csv"
OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)
REPORT_FILE = OUTPUT_DIR / "time_transform_summary.json"
PLOT_FILE = OUTPUT_DIR / "hour_distribution.png"


def load_data(file_path=RAW_DATA_PATH):
    """Load raw dataset containing string timestamps."""
    print("=" * 70)
    print("LOADING RAW DATASET")
    print("=" * 70)
    df = pd.read_csv(file_path)
    print(f"Loaded {len(df)} records from {file_path.name}")
    print(f"Columns: {df.columns.tolist()}")
    print("Sample raw dates:")
    print(df[['customer_id', 'transaction_date', 'amount']].head(3).to_string())
    return df


def parse_timestamp_strings(df, column_name='transaction_date', date_format='%Y-%m-%d %H:%M:%S'):
    """
    Task 1: Parse Timestamp Strings with Explicit Format (1 mark)
    Convert string dates to datetime type with explicit format.
    Never use pd.to_datetime() without format (causes silent corruption).
    """
    print("\n" + "=" * 70)
    print("TASK 1: PARSE TIMESTAMP STRINGS WITH EXPLICIT FORMAT")
    print("=" * 70)
    print(f"Format specification used: '{date_format}'")
    
    df[column_name] = pd.to_datetime(
        df[column_name],
        format=date_format
    )

    # Verify
    print(f"Data type after conversion: {df[column_name].dtype}")
    assert str(df[column_name].dtype).startswith('datetime64'), f"Expected datetime64, got {df[column_name].dtype}"
    print("✓ Successfully parsed timestamp strings to datetime64[ns]")
    return df


def extract_time_features(df, date_col='transaction_date'):
    """
    Task 2: Extract Day-of-Week and Hour-of-Day (1 mark)
    Create time-of-day features for traffic/engagement analysis.
    """
    print("\n" + "=" * 70)
    print("TASK 2: EXTRACT DAY-OF-WEEK AND HOUR-OF-DAY")
    print("=" * 70)
    
    df['day_of_week'] = df[date_col].dt.day_name()
    df['hour'] = df[date_col].dt.hour

    # Distribution
    hourly_volume = df.groupby('hour').size()
    print("Hourly Volume Distribution:")
    print(hourly_volume)
    
    # Plot histogram showing hour distribution
    print("\nHourly Histogram Representation:")
    for h in range(0, 24):
        cnt = hourly_volume.get(h, 0)
        bar = "#" * cnt
        print(f"Hour {h:02d}: {bar} ({cnt})")

    if HAS_MATPLOTLIB:
        plt.figure(figsize=(8, 4))
        plt.hist(df['hour'], bins=range(0, 25), color='skyblue', edgecolor='black', align='left')
        plt.title('Transaction Hour Distribution')
        plt.xlabel('Hour of Day (0-23)')
        plt.ylabel('Transaction Count')
        plt.xticks(range(0, 24, 2))
        plt.grid(axis='y', alpha=0.3)
        plt.tight_layout()
        plt.savefig(PLOT_FILE)
        plt.close()
        print(f"✓ Saved hourly distribution histogram plot to {PLOT_FILE.name}")
    else:
        print("Note: Matplotlib not installed; printed console histogram instead.")
    
    return df, hourly_volume


def compute_weekly_resample(df, date_col='transaction_date', amount_col='amount'):
    """
    Task 3: Compute Week Number and Resample Data (1 mark)
    Enable weekly aggregations and trend analysis.
    """
    print("\n" + "=" * 70)
    print("TASK 3: COMPUTE WEEK NUMBER AND RESAMPLE DATA")
    print("=" * 70)
    
    df['week_num'] = df[date_col].dt.isocalendar().week

    # Resample for weekly metrics
    df_ts = df.set_index(date_col)
    weekly_revenue = df_ts[amount_col].resample('W').sum()
    print("Weekly Revenue Trend:")
    print(weekly_revenue)
    
    return df, weekly_revenue


def compute_recency_metric(df, date_col='transaction_date', customer_id_col='customer_id'):
    """
    Task 4: Compute Days-Since-Event Metric (1 mark)
    Build recency metrics for customer churn prediction.
    """
    print("\n" + "=" * 70)
    print("TASK 4: COMPUTE DAYS-SINCE-EVENT METRIC")
    print("=" * 70)
    
    today = pd.Timestamp.now()

    # By customer
    customer_last_purchase = df.groupby(customer_id_col)[date_col].transform('max')
    df['days_since_last_purchase'] = (today - customer_last_purchase).dt.days

    # Distribution
    print("Recency (Days Since Last Purchase) Summary:")
    print(df['days_since_last_purchase'].describe())
    
    # Identify customers with lowest/highest activity recency
    customer_recency = df.groupby(customer_id_col)['days_since_last_purchase'].min().reset_index()
    print("\nCustomer-Level Recency (Days):")
    print(customer_recency.to_string(index=False))
    
    return df, customer_recency


def build_time_indexed_aggregation(df, amount_col='amount'):
    """
    Task 5: Build Time-Indexed Aggregation (1 mark)
    Enable time-series analysis with multiple temporal dimensions.
    """
    print("\n" + "=" * 70)
    print("TASK 5: BUILD TIME-INDEXED AGGREGATION")
    print("=" * 70)
    
    # Multi-level groupby
    hourly_daily = df.groupby(['day_of_week', 'hour']).agg({
        amount_col: ['sum', 'count', 'mean']
    })
    print("Multi-level Groupby (day_of_week x hour):")
    print(hourly_daily.head(10))

    # Pivot for visualization
    pivot_table = pd.pivot_table(
        df,
        values=amount_col,
        index='hour',
        columns='day_of_week',
        aggfunc='sum'
    )
    print("\nPivot Table (Hour vs Day of Week Total Revenue):")
    print(pivot_table)
    
    return hourly_daily, pivot_table


def run_verification_tests(df):
    """Testing Instructions as specified in requirements."""
    print("\n" + "=" * 70)
    print("TESTING INSTRUCTIONS & VERIFICATION")
    print("=" * 70)
    
    # Test datetime parsing
    print(f"Min date: {df['transaction_date'].min()}")
    print(f"Max date: {df['transaction_date'].max()}")

    # Test feature extraction
    print(f"Days in dataset: {(df['transaction_date'].max() - df['transaction_date'].min()).days}")
    print(f"Hours with data: {df['hour'].unique()}")
    print(f"Weeks in dataset: {df['week_num'].nunique()}")

    # Test recency
    print(f"Min days since purchase: {df['days_since_last_purchase'].min()}")
    print(f"Max days since purchase: {df['days_since_last_purchase'].max()}")
    print("=" * 70)


def save_outputs(df, hourly_volume, weekly_revenue, pivot_table):
    """Save processed dataset and summary report."""
    PROCESSED_DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(PROCESSED_DATA_PATH, index=False)
    print(f"\n✓ Saved processed dataset to {PROCESSED_DATA_PATH}")
    
    summary_report = {
        "record_count": len(df),
        "date_range": {
            "min_date": str(df['transaction_date'].min()),
            "max_date": str(df['transaction_date'].max()),
            "total_days_span": int((df['transaction_date'].max() - df['transaction_date'].min()).days)
        },
        "unique_hours": sorted([int(x) for x in df['hour'].unique()]),
        "unique_weeks": sorted([int(x) for x in df['week_num'].unique()]),
        "recency_summary": {
            "min_days": int(df['days_since_last_purchase'].min()),
            "max_days": int(df['days_since_last_purchase'].max()),
            "mean_days": float(df['days_since_last_purchase'].mean())
        }
    }
    
    with open(REPORT_FILE, 'w', encoding='utf-8') as f:
        json.dump(summary_report, f, indent=2)
    print(f"✓ Saved summary report to {REPORT_FILE}")


def main():
    df = load_data()
    df = parse_timestamp_strings(df, column_name='transaction_date', date_format='%Y-%m-%d %H:%M:%S')
    df, hourly_volume = extract_time_features(df, date_col='transaction_date')
    df, weekly_revenue = compute_weekly_resample(df, date_col='transaction_date', amount_col='amount')
    df, customer_recency = compute_recency_metric(df, date_col='transaction_date', customer_id_col='customer_id')
    hourly_daily, pivot_table = build_time_indexed_aggregation(df, amount_col='amount')
    
    run_verification_tests(df)
    save_outputs(df, hourly_volume, weekly_revenue, pivot_table)


if __name__ == '__main__':
    main()
