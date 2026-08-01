import pandas as pd
import numpy as np
from pathlib import Path


# --------------------------------------------------
# File paths
# --------------------------------------------------

INPUT_FILE = Path("data/processed/clean_campaign_data.csv")
OUTPUT_FILE = Path(
    "data/processed/feature_engineered_campaign_data.csv"
)


# --------------------------------------------------
# Load processed data
# --------------------------------------------------

df = pd.read_csv(INPUT_FILE)

print("=" * 70)
print("BEYONDCLICKS - FEATURE ENGINEERING")
print("=" * 70)

print("\nProcessed dataset loaded successfully")
print(f"Rows: {len(df)}")
print(f"Columns before feature engineering: {len(df.columns)}")


# --------------------------------------------------
# Feature 1: Click-Through Rate
# --------------------------------------------------

df["CTR"] = np.where(
    df["Impressions"] > 0,
    (df["Clicks"] / df["Impressions"]) * 100,
    0
)


# --------------------------------------------------
# Feature 2: Signup Rate
# --------------------------------------------------

df["Signup_Rate"] = np.where(
    df["Clicks"] > 0,
    (df["Signups"] / df["Clicks"]) * 100,
    0
)


# --------------------------------------------------
# Feature 3: Activation Rate
# --------------------------------------------------

df["Activation_Rate"] = np.where(
    df["Signups"] > 0,
    (df["Activated_Users"] / df["Signups"]) * 100,
    0
)


# --------------------------------------------------
# Feature 4: Click-to-Activation Rate
# --------------------------------------------------

df["Click_to_Activation_Rate"] = np.where(
    df["Clicks"] > 0,
    (df["Activated_Users"] / df["Clicks"]) * 100,
    0
)


# --------------------------------------------------
# Feature 5: Revenue per Activated User
# --------------------------------------------------

df["Revenue_per_Activated_User"] = np.where(
    df["Activated_Users"] > 0,
    df["Revenue"] / df["Activated_Users"],
    0
)


# --------------------------------------------------
# Feature 6: Cost per Activated User
# --------------------------------------------------

df["Cost_per_Activated_User"] = np.where(
    df["Activated_Users"] > 0,
    df["Acquisition_Cost"] / df["Activated_Users"],
    0
)


# --------------------------------------------------
# Feature 7: Cost per Signup
# --------------------------------------------------

df["Cost_per_Signup"] = np.where(
    df["Signups"] > 0,
    df["Acquisition_Cost"] / df["Signups"],
    0
)


# --------------------------------------------------
# Round calculated features
# --------------------------------------------------

percentage_columns = [
    "CTR",
    "Signup_Rate",
    "Activation_Rate",
    "Click_to_Activation_Rate"
]

for column in percentage_columns:
    df[column] = df[column].round(2)


df["Revenue_per_Activated_User"] = (
    df["Revenue_per_Activated_User"].round(2)
)

df["Cost_per_Activated_User"] = (
    df["Cost_per_Activated_User"].round(2)
)

df["Cost_per_Signup"] = (
    df["Cost_per_Signup"].round(2)
)


# --------------------------------------------------
# Save feature-engineered dataset
# --------------------------------------------------

df.to_csv(OUTPUT_FILE, index=False)


# --------------------------------------------------
# Summary
# --------------------------------------------------

print("\nFeature engineering completed successfully.")

print(f"Rows: {len(df)}")
print(f"Columns after feature engineering: {len(df.columns)}")

print("\nNew features created:")

new_features = [
    "CTR",
    "Signup_Rate",
    "Activation_Rate",
    "Click_to_Activation_Rate",
    "Revenue_per_Activated_User",
    "Cost_per_Activated_User",
    "Cost_per_Signup"
]

for feature in new_features:
    print(f" - {feature}")

print(f"\nOutput saved to:")
print(OUTPUT_FILE)

print("\n" + "=" * 70)