import sys
import pandas as pd
from pathlib import Path
from sqlalchemy import create_engine

# Ensure UTF-8 output encoding for Windows terminal compatibility
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass


# Project root
BASE_DIR = Path(__file__).resolve().parent.parent

# File paths
DATA_FILE = BASE_DIR / "data" / "processed" / "clean_campaign_data.csv"
OUTPUT_DIR = BASE_DIR / "output"

# Create output folder if it doesn't exist
OUTPUT_DIR.mkdir(exist_ok=True)

DB_FILE = OUTPUT_DIR / "marketing.db"

# Read processed dataset if available
if DATA_FILE.exists():
    df = pd.read_csv(DATA_FILE)

    # Create engine with SQLAlchemy
    engine = create_engine(f"sqlite:///{DB_FILE}")

    df.to_sql(
        "campaigns",
        engine,
        if_exists="replace",
        index=False
    )

    # Test connection and table creation
    with engine.connect() as conn:
        print("✓ Database connection successful")

    print("✅ SQLite database created successfully using SQLAlchemy!")
    print(f"Database Location: {DB_FILE}")
else:
    print(f"Data file not found at {DATA_FILE}")