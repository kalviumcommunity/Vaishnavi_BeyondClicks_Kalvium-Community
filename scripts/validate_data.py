import pandas as pd
import json
from pathlib import Path

# --------------------------------------------------
# Project Paths
# --------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

RAW_DATA = BASE_DIR / "data" / "raw" / "validation_data.csv"

PROCESSED_DATA = (
    BASE_DIR / "data" / "processed" / "validated_campaign_data.csv"
)

OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

FAILURE_FILE = OUTPUT_DIR / "validation_failures.csv"
REPORT_FILE = OUTPUT_DIR / "validation_report.json"


# --------------------------------------------------
# Load Dataset
# --------------------------------------------------
def load_data(filepath):
    print("Loading Validation Dataset...\n")
    return pd.read_csv(filepath)


# --------------------------------------------------
# Task 1 : Range Checks
# --------------------------------------------------
def range_checks(df):

    print("=" * 60)
    print("TASK 1 : RANGE CHECKS")
    print("=" * 60)

    df["valid_revenue"] = df["Revenue"] >= 0

    df["valid_engagement"] = (
        (df["Engagement_Score"] >= 0)
        & (df["Engagement_Score"] <= 100)
    )

    df["valid_roi"] = df["ROI"] >= 0

    df["valid_date"] = (
        pd.to_datetime(
            df["Date"],
            format="%d-%m-%Y",
            errors="coerce"
        )
        .notna()
    )

    print("Invalid Revenue :", (~df["valid_revenue"]).sum())
    print("Invalid Engagement :", (~df["valid_engagement"]).sum())
    print("Invalid ROI :", (~df["valid_roi"]).sum())
    print("Invalid Dates :", (~df["valid_date"]).sum())

    return df


# --------------------------------------------------
# Task 2 : Null Constraints
# --------------------------------------------------
def null_constraints(df):

    print("\n" + "=" * 60)
    print("TASK 2 : NULL CONSTRAINTS")
    print("=" * 60)

    df["valid_campaign_id"] = df["Campaign_ID"].notna()

    df["valid_platform"] = df["Platform"].notna()

    df["valid_campaign_type"] = df["Campaign_Type"].notna()

    df["valid_language"] = df["Language"].notna()

    print("Missing Campaign_ID :", (~df["valid_campaign_id"]).sum())
    print("Missing Platform :", (~df["valid_platform"]).sum())
    print("Missing Campaign_Type :", (~df["valid_campaign_type"]).sum())
    print("Missing Language :", (~df["valid_language"]).sum())

    return df


# --------------------------------------------------
# Task 3 : Format Validation
# --------------------------------------------------
def format_validation(df):

    print("\n" + "=" * 60)
    print("TASK 3 : FORMAT VALIDATION")
    print("=" * 60)

    df["valid_campaign_format"] = df["Campaign_ID"].str.match(
        r"^CMP\d{3}$",
        na=False
    )

    print(
        "Invalid Campaign IDs :",
        (~df["valid_campaign_format"]).sum()
    )

    return df


# --------------------------------------------------
# Task 4 : Business Rules
# --------------------------------------------------
def business_rules(df):

    print("\n" + "=" * 60)
    print("TASK 4 : BUSINESS RULES")
    print("=" * 60)

    df["valid_business"] = (
        (df["Revenue"] >= 0)
        & (df["ROI"] >= 0)
        & (df["Engagement_Score"] <= 100)
    )

    print(
        "Business Rule Violations :",
        (~df["valid_business"]).sum()
    )

    return df


# --------------------------------------------------
# Task 5 : Validation Report
# --------------------------------------------------
def validation_report(df):

    print("\n" + "=" * 60)
    print("TASK 5 : VALIDATION REPORT")
    print("=" * 60)

    validation_columns = [

        "valid_revenue",

        "valid_engagement",

        "valid_roi",

        "valid_date",

        "valid_campaign_id",

        "valid_platform",

        "valid_campaign_type",

        "valid_language",

        "valid_campaign_format",

        "valid_business"

    ]

    df["passes_all_checks"] = df[
        validation_columns
    ].all(axis=1)

    failures = df[
        ~df["passes_all_checks"]
    ]

    passed = df[
        df["passes_all_checks"]
    ]

    failures.to_csv(
        FAILURE_FILE,
        index=False
    )

    passed.to_csv(
        PROCESSED_DATA,
        index=False
    )

    report = {

        "Total Records": len(df),

        "Passed Records": len(passed),

        "Failed Records": len(failures),

        "Validation Rules": {

            "Revenue":
            "Must be >= 0",

            "ROI":
            "Must be >= 0",

            "Engagement_Score":
            "Must be between 0 and 100",

            "Campaign_ID":
            "Required and format CMP###",

            "Platform":
            "Cannot be null",

            "Campaign_Type":
            "Cannot be null",

            "Language":
            "Cannot be null",

            "Date":
            "Must follow DD-MM-YYYY"

        }

    }

    with open(
        REPORT_FILE,
        "w"
    ) as file:

        json.dump(
            report,
            file,
            indent=4
        )

    print("Total Records :", len(df))
    print("Passed :", len(passed))
    print("Failed :", len(failures))

    print("\nValidation report saved.")
    print(REPORT_FILE)

    print("\nValidation failures saved.")
    print(FAILURE_FILE)

    print("\nValidated dataset saved.")
    print(PROCESSED_DATA)


# --------------------------------------------------
# Main Program
# --------------------------------------------------
if __name__ == "__main__":

    print("\nStarting Data Validation Pipeline...\n")

    df = load_data(RAW_DATA)

    df = range_checks(df)

    df = null_constraints(df)

    df = format_validation(df)

    df = business_rules(df)

    validation_report(df)

    print("\n✓ Data Validation Completed Successfully.")