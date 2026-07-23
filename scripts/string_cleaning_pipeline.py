import json
import pandas as pd
from pathlib import Path

# -------------------------------------------------
# Project Paths
# -------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

RAW_DATA = BASE_DIR / "data" / "raw" / "string_dirty_data.csv"

PROCESSED_DATA = BASE_DIR / "data" / "processed" / "clean_string_data.csv"

OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

REPORT_FILE = OUTPUT_DIR / "string_cleaning_report.json"


# -------------------------------------------------
# Strip Whitespace
# -------------------------------------------------

def strip_all_strings(df):

    print("\nRemoving Leading and Trailing Spaces...\n")

    string_cols = df.select_dtypes(include="object").columns

    report = {}

    for col in string_cols:

        before = df[col].value_counts(dropna=False).to_dict()

        df[col] = df[col].str.strip()

        after = df[col].value_counts(dropna=False).to_dict()

        report[col] = {
            "before_unique": len(before),
            "after_unique": len(after)
        }

        print(f"{col}: {len(before)} → {len(after)} unique values")

    return df, report


# -------------------------------------------------
# Normalize Case
# -------------------------------------------------

def normalize_case(df, columns):

    print("\nNormalizing Text to Lowercase...\n")

    for col in columns:

        df[col] = df[col].str.lower()

        print(f"✓ {col}")

    return df


# -------------------------------------------------
# Remove Special Characters
# -------------------------------------------------

def remove_special_characters(df, columns):

    print("\nRemoving Special Characters...\n")

    pattern = r"[^a-zA-Z0-9 ]"

    for col in columns:

        df[col] = df[col].str.replace(
            pattern,
            "",
            regex=True
        )

        print(f"✓ {col}")

    return df


# -------------------------------------------------
# Mapping Dictionaries
# -------------------------------------------------

campaign_map = {
    "social media": "Social Media",
    "socialmedia": "Social Media",
    "social-media": "Social Media",
    "paid ads": "Paid Ads",
    "paidads": "Paid Ads",
    "email": "Email",
    "influencer": "Influencer"
}

platform_map = {
    "instagram": "Instagram",
    "facebook": "Facebook",
    "youtube": "YouTube",
    "google": "Google"
}

language_map = {
    "english": "English",
    "hindi": "Hindi"
}


# -------------------------------------------------
# Standardize Labels
# -------------------------------------------------

def standardize_categories(df):

    print("\nApplying Mapping Dictionaries...\n")

    df["Campaign_Type"] = df["Campaign_Type"].replace(campaign_map)

    df["Platform"] = df["Platform"].replace(platform_map)

    df["Language"] = df["Language"].replace(language_map)

    print("✓ Campaign_Type standardized")
    print("✓ Platform standardized")
    print("✓ Language standardized")

    return df


# -------------------------------------------------
# Reusable Function
# -------------------------------------------------

def clean_text_column(
    series,
    lowercase=True,
    strip=True,
    remove_special=False,
    mapping=None
):

    result = series.copy()

    if result.isna().any():

        print(
            f"Warning: {result.isna().sum()} null values found."
        )

    if strip:

        result = result.str.strip()

    if lowercase:

        result = result.str.lower()

    if remove_special:

        result = result.str.replace(
            r"[^a-zA-Z0-9 ]",
            "",
            regex=True
        )

    if mapping:

        result = result.replace(mapping)

    return result


# -------------------------------------------------
# Save Report
# -------------------------------------------------

def save_report(report):

    with open(REPORT_FILE, "w") as file:

        json.dump(report, file, indent=4)

    print("\n✓ Cleaning report saved.")


# -------------------------------------------------
# Main
# -------------------------------------------------

if __name__ == "__main__":

    print("\nStarting String Cleaning Pipeline...\n")

    df = pd.read_csv(RAW_DATA)

    print("\nDataset Before Cleaning\n")
    print(df.head())

    print("\nCampaign Type Counts Before")
    print(df["Campaign_Type"].value_counts(dropna=False))

    print("\nPlatform Counts Before")
    print(df["Platform"].value_counts(dropna=False))

    # Task 1
    df, report = strip_all_strings(df)

    # Task 2
    df = normalize_case(
        df,
        [
            "Campaign_Type",
            "Platform",
            "Language"
        ]
    )

    # Task 3
    df = remove_special_characters(
        df,
        [
            "Campaign_Type",
            "Platform"
        ]
    )

    # Task 4
    df = standardize_categories(df)

    # Task 5 (Reusable Function Demo)

    print("\nApplying Reusable Cleaning Function...\n")

    df["Campaign_Type"] = clean_text_column(
        df["Campaign_Type"],
        lowercase=False,
        strip=False,
        remove_special=False,
        mapping=campaign_map
    )

    df["Platform"] = clean_text_column(
        df["Platform"],
        lowercase=False,
        strip=False,
        remove_special=False,
        mapping=platform_map
    )

    df["Language"] = clean_text_column(
        df["Language"],
        lowercase=False,
        strip=False,
        remove_special=False,
        mapping=language_map
    )

    print("\nCampaign Type Counts After")
    print(df["Campaign_Type"].value_counts())

    print("\nPlatform Counts After")
    print(df["Platform"].value_counts())

    print("\nDataset After Cleaning\n")
    print(df.head())

    df.to_csv(
        PROCESSED_DATA,
        index=False
    )

    save_report(report)

    print("\n✓ Cleaned dataset saved successfully.")
    print(PROCESSED_DATA)