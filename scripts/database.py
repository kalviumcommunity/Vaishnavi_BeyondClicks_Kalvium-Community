import sqlite3
import pandas as pd
from pathlib import Path

# Project root
BASE_DIR = Path(__file__).resolve().parent.parent

# File paths
DATA_FILE = BASE_DIR / "data" / "processed" / "clean_campaign_data.csv"
OUTPUT_DIR = BASE_DIR / "output"

# Create output folder if it doesn't exist
OUTPUT_DIR.mkdir(exist_ok=True)

DB_FILE = OUTPUT_DIR / "marketing.db"

# Read processed dataset
df = pd.read_csv(DATA_FILE)

# Create SQLite database
conn = sqlite3.connect(DB_FILE)

df.to_sql(
    "campaigns",
    conn,
    if_exists="replace",
    index=False
)

conn.commit()
conn.close()

print("✅ SQLite database created successfully!")
print(f"Database Location: {DB_FILE}")