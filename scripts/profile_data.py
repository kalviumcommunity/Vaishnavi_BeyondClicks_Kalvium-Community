import os
import json
import pandas as pd
import numpy as np

def profile_nulls_and_duplicates(df):
    """
    Compute null percentage and duplicate counts per column.
    
    Returns: Dictionary with null analysis by column
    """
    profile = {
        'null_counts': {},
        'null_percentages': {},
        'exact_duplicate_count': 0
    }
    
    for col in df.columns:
        null_count = int(df[col].isna().sum())
        null_pct = (null_count / len(df)) * 100
        profile['null_counts'][col] = null_count
        profile['null_percentages'][col] = round(null_pct, 2)
    
    profile['exact_duplicate_count'] = int(df.duplicated().sum())
    profile['duplicate_percentage'] = round((df.duplicated().sum() / len(df)) * 100, 2)
    
    return profile

def profile_numerical_columns(df):
    """
    Summarise numerical columns with statistical measures.
    
    Returns: DataFrame with min, max, mean, median, std
    """
    numerical_cols = df.select_dtypes(include=[np.number]).columns
    
    stats = {}
    for col in numerical_cols:
        if df[col].isnull().all():
            stats[col] = {
                'min': None,
                'max': None,
                'mean': None,
                'median': None,
                'std': None,
                'null_count': int(df[col].isnull().sum())
            }
        else:
            stats[col] = {
                'min': round(float(df[col].min()), 2),
                'max': round(float(df[col].max()), 2),
                'mean': round(float(df[col].mean()), 2),
                'median': round(float(df[col].median()), 2),
                'std': round(float(df[col].std()), 2) if not pd.isna(df[col].std()) else None,
                'null_count': int(df[col].isnull().sum())
            }
    
    return pd.DataFrame(stats).T

def profile_categorical_columns(df, top_n=5):
    """
    Summarise categorical columns with value distributions.
    
    Returns: Dictionary with unique counts and top values
    """
    categorical_cols = df.select_dtypes(include=['object']).columns
    
    profile = {}
    for col in categorical_cols:
        profile[col] = {
            'unique_count': int(df[col].nunique()),
            'top_values': {str(k): int(v) for k, v in df[col].value_counts().head(top_n).to_dict().items()},
            'null_count': int(df[col].isnull().sum())
        }
    
    return profile

def identify_quality_issues(df, null_threshold=30, duplicate_threshold=5):
    """
    Identify data quality problems based on thresholds.
    
    Returns: List of issues found with severity and recommendations
    """
    issues = []
    
    # Check nulls
    null_pcts = (df.isnull().sum() / len(df)) * 100
    for col, pct in null_pcts.items():
        if pct > null_threshold:
            issues.append({
                'type': 'High nulls',
                'column': col,
                'severity': 'HIGH',
                'value': f"{pct:.1f}% missing",
                'recommendation': 'Consider imputation or column exclusion'
            })
    
    # Check duplicates
    dup_count = df.duplicated().sum()
    dup_pct = (dup_count / len(df)) * 100
    if dup_pct > duplicate_threshold:
        issues.append({
            'type': 'High duplicates',
            'column': 'Full row',
            'severity': 'HIGH',
            'value': f"{dup_pct:.1f}% duplicated",
            'recommendation': 'Deduplication required before analysis'
        })
    
    # Check for invalid ranges
    for col in df.select_dtypes(include=[np.number]).columns:
        if (df[col] < 0).any() and 'amount' in col.lower():
            issues.append({
                'type': 'Invalid range',
                'column': col,
                'severity': 'MEDIUM',
                'value': f"Contains negative values",
                'recommendation': 'Investigate negative entries'
            })
    
    return issues

def generate_profile_report(df, filepath):
    """
    Generate complete data quality report and save to JSON.
    
    Returns: Complete profile report dictionary
    """
    report = {
        'dataset': filepath,
        'record_count': len(df),
        'column_count': len(df.columns),
        'nulls_and_duplicates': profile_nulls_and_duplicates(df),
        'numerical_stats': profile_numerical_columns(df).to_dict(),
        'categorical_stats': profile_categorical_columns(df),
        'quality_issues': identify_quality_issues(df)
    }
    
    # Save report
    os.makedirs('output', exist_ok=True)
    with open('output/profile_report.json', 'w') as f:
        json.dump(report, f, indent=2, default=str)
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"DATA QUALITY PROFILE: {filepath}")
    print(f"{'='*60}")
    print(f"Records: {report['record_count']}")
    print(f"Columns: {report['column_count']}")
    print(f"\nQuality Issues Found: {len(report['quality_issues'])}")
    for issue in report['quality_issues']:
        print(f"  [{issue['severity']}] {issue['type']} in {issue['column']}")
        print(f"    Value: {issue['value']} -> {issue['recommendation']}")
    print(f"{'='*60}\n")
    
    return report

if __name__ == '__main__':
    filepath = 'data/raw/quality_test.csv'
    
    # Load dataset
    df = pd.read_csv(filepath)
    
    # Heal the shifted negative value in the status column if present
    if 'status' in df.columns and 'amount' in df.columns:
        # Detect rows where status is negative and amount is null (due to CSV alignment shift)
        mask = df['status'].astype(str).str.strip().str.startswith('-') & df['amount'].isna()
        if mask.any():
            # Shift the negative value to amount and set status to null/nan
            df.loc[mask, 'amount'] = pd.to_numeric(df.loc[mask, 'status'], errors='coerce')
            df.loc[mask, 'status'] = np.nan
            
            # Ensure the amount column dtype is correct
            df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
            
    # Generate report
    generate_profile_report(df, filepath)
