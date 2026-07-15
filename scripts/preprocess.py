import pandas as pd
from pathlib import Path

# -----------------------------
# Project Paths
# -----------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

RAW_DATA = BASE_DIR / "data" / "raw" / "nykaa_campaign_data.csv"
PROCESSED_DATA = BASE_DIR / "data" / "processed" / "clean_campaign_data.csv"

# -----------------------------
# Load Dataset
# -----------------------------
df = pd.read_csv(RAW_DATA)

# -----------------------------
# Explore Dataset
# -----------------------------
print("=" * 50)
print("FIRST 5 ROWS")
print("=" * 50)
print(df.head())

print("\nDataset Shape:")
print(df.shape)

print("\nColumn Names:")
print(df.columns.tolist())

print("\nMissing Values:")
print(df.isnull().sum())

print("\nDuplicate Rows:")
print(df.duplicated().sum())

# -----------------------------
# Data Preprocessing
# -----------------------------

# Rename columns according to project terminology
df.rename(columns={
    "Channel_Used": "Platform",
    "Leads": "Signups",
    "Conversions": "Activated_Users"
}, inplace=True)

# Convert Date column to datetime format
df["Date"] = pd.to_datetime(df["Date"], format="%d-%m-%Y")

# -----------------------------
# Save Clean Dataset
# -----------------------------
df.to_csv(PROCESSED_DATA, index=False)

print("\n✅ Clean dataset saved successfully!")
print(f"Location: {PROCESSED_DATA}")

print("\nUpdated Columns:")
print(df.columns.tolist())