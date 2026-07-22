import pandas as pd
import json
from pathlib import Path

# -------------------------------------------------
# Project Paths
# -------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

RAW_DATA = BASE_DIR / "data" / "raw" / "missing_data.csv"

PROCESSED_DATA = BASE_DIR / "data" / "processed" / "clean_missing_data.csv"

OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

# -------------------------------------------------
# Task 1 - Analyze Missing Values
# -------------------------------------------------
def analyze_missing_values(df):

    missing_analysis = pd.DataFrame({
        "Column": df.columns,
        "Null Count": df.isnull().sum().values,
        "Null Percentage": (
            df.isnull().sum() / len(df) * 100
        ).round(2).values,
        "Data Type": df.dtypes.values
    })

    print("=" * 70)
    print("BEFORE IMPUTATION - MISSING VALUE ANALYSIS")
    print("=" * 70)

    print(missing_analysis.to_string(index=False))

    print("\nTotal Rows :", len(df))
    print("Total Missing Values :", df.isnull().sum().sum())

    print("=" * 70)

    return missing_analysis


# -------------------------------------------------
# Task 2 - Numerical Imputation
# -------------------------------------------------
def impute_median(df, numerical_cols):

    df = df.copy()

    print("\nApplying Median Imputation")

    for col in numerical_cols:

        if col in df.columns and df[col].isnull().sum() > 0:

            median = df[col].median()

            count = df[col].isnull().sum()

            df[col] = df[col].fillna(median)

            print(f"✓ {col}: Filled {count} values using Median ({median})")

    return df


# -------------------------------------------------
# Task 2 - Mode Imputation
# -------------------------------------------------
def impute_mode(df, categorical_cols):

    df = df.copy()

    print("\nApplying Mode Imputation")

    for col in categorical_cols:

        if col in df.columns and df[col].isnull().sum() > 0:

            mode = df[col].mode()[0]

            count = df[col].isnull().sum()

            df[col] = df[col].fillna(mode)

            print(f"✓ {col}: Filled {count} values using Mode ({mode})")

    return df


# -------------------------------------------------
# Task 2 - Forward Fill
# -------------------------------------------------
def forward_fill(df, columns):

    df = df.copy()

    print("\nApplying Forward Fill")

    for col in columns:

        if col in df.columns and df[col].isnull().sum() > 0:

            count = df[col].isnull().sum()

            df[col] = df[col].ffill()

            print(f"✓ {col}: Forward Filled {count} values")

    return df


# -------------------------------------------------
# Task 2 - Drop Critical Rows
# -------------------------------------------------
def drop_missing_campaign(df):

    before = len(df)

    df = df.dropna(subset=["Campaign_ID"])

    removed = before - len(df)

    print(f"\n✓ Removed {removed} rows with missing Campaign_ID")

    return df


# -------------------------------------------------
# Task 3 - Document Decisions
# -------------------------------------------------
def document_imputation():

    decisions = {

        "Revenue": {

            "Strategy": "Median",

            "Reason":
                "Revenue is numerical and may contain outliers. "
                "Median preserves the overall distribution better than mean."

        },

        "Platform": {

            "Strategy": "Mode",

            "Reason":
                "Platform is categorical. Most frequent platform is used."

        },

        "Campaign_Type": {

            "Strategy": "Mode",

            "Reason":
                "Most campaigns belong to one common campaign type."

        },

        "Language": {

            "Strategy": "Mode",

            "Reason":
                "Language is categorical and mode maintains consistency."

        },

        "Engagement_Score": {

            "Strategy": "Median",

            "Reason":
                "Engagement score is numeric and median is resistant to outliers."

        },

        "Campaign_ID": {

            "Strategy": "Drop Rows",

            "Reason":
                "Campaign_ID uniquely identifies campaigns and cannot be guessed."

        }

    }

    with open(
        OUTPUT_DIR / "imputation_decisions.json",
        "w"
    ) as file:

        json.dump(decisions, file, indent=4)

    print("\n✓ Imputation decisions saved.")


# -------------------------------------------------
# Task 4 - Validation
# -------------------------------------------------
def validate(df_before, df_after):

    print("\n" + "=" * 70)

    print("AFTER IMPUTATION REPORT")

    print("=" * 70)

    print("Rows Before :", len(df_before))

    print("Rows After  :", len(df_after))

    print()

    print("Missing Before :", df_before.isnull().sum().sum())

    print("Missing After  :", df_after.isnull().sum().sum())

    print("\nRemaining Missing Values")

    print(df_after.isnull().sum())

    print("=" * 70)


# -------------------------------------------------
# Task 5 - Main Workflow
# -------------------------------------------------
if __name__ == "__main__":

    print("\nStarting Missing Value Detection & Imputation...\n")

    # Load data
    df = pd.read_csv(RAW_DATA)

    original_df = df.copy()

    # Step 1
    analyze_missing_values(df)

    # Step 2
    print("\nApplying Imputation Strategies...")

    df = drop_missing_campaign(df)

    df = impute_median(
        df,
        [
            "Revenue",
            "Engagement_Score"
        ]
    )

    df = impute_mode(
        df,
        [
            "Campaign_Type",
            "Platform",
            "Language"
        ]
    )

    # (Optional example of forward fill)
    # df = forward_fill(df, ["Date"])

    # Step 3
    document_imputation()

    # Step 4
    validate(original_df, df)

    # Step 5
    df.to_csv(PROCESSED_DATA, index=False)

    print("\n✓ Cleaned dataset saved successfully.")

    print(PROCESSED_DATA)