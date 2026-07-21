import pandas as pd
from pathlib import Path

# -----------------------------
# Project Paths
# -----------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

RAW_DATA = BASE_DIR / "data" / "raw" / "nykaa_campaign_data.csv"
JSON_DATA = BASE_DIR / "data" / "raw" / "sample_campaign.json"

# -----------------------------
# CSV Ingestion
# -----------------------------
def ingest_csv(filepath, delimiter=",", encoding="utf-8", dtype_dict=None):
    """
    Load a CSV file into a Pandas DataFrame.

    Args:
        filepath (str or Path): Path to the CSV file.
        delimiter (str): Column separator.
        encoding (str): Preferred file encoding.

    Returns:
        pd.DataFrame: Loaded dataset.
    """

    encodings = [encoding, "latin-1", "iso-8859-1", "cp1252"]

    for enc in encodings:
        try:
            df = pd.read_csv(
                filepath,
                delimiter=delimiter,
                encoding=enc,
                dtype=dtype_dict
            )

            print(f"✅ CSV loaded successfully using '{enc}' encoding.")
            return df

        except UnicodeDecodeError:
            continue

    raise ValueError(
        "Unable to read the file using the supported encodings."
    )


# -----------------------------
# JSON Ingestion
# -----------------------------
def ingest_json(filepath, is_nested=False):
    """
    Load a JSON file into a Pandas DataFrame.

    Args:
        filepath (str or Path): Path to JSON file.
        is_nested (bool): Flatten nested JSON if True.

    Returns:
        pd.DataFrame
    """

    try:
        df = pd.read_json(filepath)

        if is_nested:
            df = pd.json_normalize(df)
            print("✓ Flattened nested JSON.")

        print("✅ JSON loaded successfully.")
        return df

    except FileNotFoundError:
        print("JSON file not found.")
        raise


def ingest_csv_with_fallback(filepath, delimiters=[","], fallback_encodings=None):
    """
    Load CSV using multiple encodings and delimiters.
    """

    if fallback_encodings is None:
        fallback_encodings = [
            "utf-8",
            "latin-1",
            "iso-8859-1",
            "cp1252"
        ]

    for delimiter in delimiters:
        for encoding in fallback_encodings:
            try:
                df = pd.read_csv(
                    filepath,
                    delimiter=delimiter,
                    encoding=encoding
                )

                print(
                    f"✓ Loaded using delimiter='{delimiter}' encoding='{encoding}'"
                )

                return df

            except (UnicodeDecodeError, pd.errors.ParserError):
                continue

    raise ValueError("Unable to load CSV with supported encodings.")


# -----------------------------
# Ingestion Report
# -----------------------------
def document_ingestion(df, source):
    """
    Display a summary of the ingested dataset.
    """

    print("\n" + "=" * 50)
    print("INGESTION REPORT")
    print("=" * 50)

    print(f"Source : {source}")
    print(f"Rows   : {df.shape[0]}")
    print(f"Columns: {df.shape[1]}")

    print("\nColumn Names")
    print(df.columns.tolist())

    print("\nColumn Types")
    print(df.dtypes.to_string())

    print("\nFirst 5 Rows")
    print(df.head())

    print("\nNull Values")
    print(df.isnull().sum())


# -----------------------------
# Main Execution
# -----------------------------
if __name__ == "__main__":

    print("Starting Multi-Format Data Ingestion...\n")

    # Load CSV
    csv_df = ingest_csv(
        RAW_DATA,
        delimiter=",",
        encoding="utf-8"
    )

    document_ingestion(
        csv_df,
        RAW_DATA.name
    )

    # Load JSON
    json_df = ingest_json(JSON_DATA)

    document_ingestion(
        json_df,
        JSON_DATA.name
    )

    # Save CSV to processed folder
    csv_df.to_csv(
        BASE_DIR / "data" / "processed" / "campaign_ingested.csv",
        index=False
    )

    # Save JSON as CSV
    json_df.to_csv(
        BASE_DIR / "data" / "processed" / "campaign_json_ingested.csv",
        index=False
    )

    print("\n✓ All data ingested successfully.")