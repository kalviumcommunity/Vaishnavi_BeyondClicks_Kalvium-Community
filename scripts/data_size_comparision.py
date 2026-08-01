import pandas as pd
from pathlib import Path

# File paths
raw_path = Path("data/raw/nykaa_campaign_data.csv")
processed_path = Path("data/processed/clean_campaign_data.csv")

# Load datasets
raw_df = pd.read_csv(raw_path)
processed_df = pd.read_csv(processed_path)

print("=" * 60)
print("BEYONDCLICKS - RAW VS PROCESSED DATA COMPARISON")
print("=" * 60)

# Shape
print("\nRAW DATA")
print(f"Rows    : {raw_df.shape[0]}")
print(f"Columns : {raw_df.shape[1]}")
print(f"Size    : {raw_df.shape}")

print("\nPROCESSED DATA")
print(f"Rows    : {processed_df.shape[0]}")
print(f"Columns : {processed_df.shape[1]}")
print(f"Size    : {processed_df.shape}")

# Difference
print("\nSIZE DIFFERENCE")
print(f"Rows removed    : {raw_df.shape[0] - processed_df.shape[0]}")
print(f"Column change   : {processed_df.shape[1] - raw_df.shape[1]}")

# Missing values
print("\nMISSING VALUES")

print("\nRaw:")
print(raw_df.isnull().sum())

print("\nProcessed:")
print(processed_df.isnull().sum())

# Duplicate rows
print("\nDUPLICATES")
print(f"Raw duplicates       : {raw_df.duplicated().sum()}")
print(f"Processed duplicates : {processed_df.duplicated().sum()}")

print("\n" + "=" * 60)