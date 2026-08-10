import streamlit as st
import pandas as pd
import numpy as np

# =========================================================
# Page Config
# =========================================================
st.set_page_config(
    page_title="BeyondClicks Analytics Dashboard",
    page_icon="📊",
    layout="wide"
)

st.title("📂 Dataset Uploader & Analyzer")
st.caption("Upload a CSV or JSON dataset to get an immediate preview, metrics, and basic statistics.")

# =========================================================
# File Uploader
# =========================================================
st.sidebar.header("Data Ingestion")
uploaded_file = st.sidebar.file_uploader("Upload your dataset", type=["csv", "json"])

# Initialize DataFrame
df = None

if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith(".csv"):
            raw_df = pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith(".json"):
            raw_df = pd.read_json(uploaded_file)
        else:
            st.error("Unsupported file type.")
            st.stop()

        if len(raw_df) == 0:
            st.warning("Uploaded file is empty.")
            st.stop()

        # Proactive column mapping to ensure downstream compatibility
        df = raw_df.copy()
        
        # 1. Map Date
        date_col = next((c for c in df.columns if "date" in c.lower() or "time" in c.lower()), None)
        if date_col:
            df["date"] = pd.to_datetime(df[date_col], errors='coerce')
        else:
            # Generate dummy dates if missing
            df["date"] = pd.date_range(start='2026-07-01', periods=len(df))
            
        # Fill any parsed date NaTs
        if df["date"].isnull().any():
            df["date"] = df["date"].fillna(pd.Timestamp('2026-07-01'))

        # 2. Map Segment
        segment_col = next((c for c in df.columns if "segment" in c.lower() or "type" in c.lower() or "cat" in c.lower()), None)
        if segment_col:
            df["segment"] = df[segment_col].astype(str)
        else:
            df["segment"] = np.random.choice(['Enterprise', 'SMB', 'Startup'], size=len(df))

        # 3. Map Revenue
        revenue_col = next((c for c in df.columns if "revenue" in c.lower() or "amount" in c.lower() or "spent" in c.lower() or "value" in c.lower()), None)
        if revenue_col:
            df["revenue"] = pd.to_numeric(df[revenue_col], errors='coerce').fillna(0.0)
        else:
            # Check for any numerical column as fallback
            num_cols = df.select_dtypes(include="number").columns
            if len(num_cols) > 0:
                df["revenue"] = df[num_cols[0]]
            else:
                df["revenue"] = np.random.uniform(50.0, 2000.0, size=len(df))

        st.sidebar.success(f"Loaded: {uploaded_file.name}")
        
    except Exception:
        st.error("Could not read this file. Check the format and try again.")
        st.stop()
else:
    st.sidebar.info("Using default sample dataset.")
    # Seed default dataset so the app never loads empty
    df = pd.DataFrame({
        'date': pd.date_range(start='2026-07-01', periods=100),
        'customer_id': list(range(1001, 1101)),
        'segment': ['Enterprise' if i % 3 == 0 else 'SMB' if i % 3 == 1 else 'Startup' for i in range(100)],
        'revenue': [float((i % 10) * 150 + 50) for i in range(100)],
        'support_interactions': [i % 6 for i in range(100)],
        'response_time_hours': [float(i % 5) + 1.5 for i in range(100)]
    })

# Ensure date is strictly datetime format
df["date"] = pd.to_datetime(df["date"])

# =========================================================
# Sidebar Filters (Task 1)
# =========================================================
st.sidebar.header("Filters")

# Date range picker
min_date = df["date"].min().date()
max_date = df["date"].max().date()
date_range = st.sidebar.date_input(
    "Date Range",
    value=(min_date, max_date),
    key="date_filter"
)

# Multi-select for segments
all_segments = df["segment"].unique().tolist()
selected_segments = st.sidebar.multiselect(
    "Segments",
    options=all_segments,
    default=all_segments,
    key="segment_filter"
)

# Revenue slider
min_val = float(df["revenue"].min())
max_val = float(df["revenue"].max())
min_rev, max_rev = st.sidebar.slider(
    "Revenue Range",
    min_value=int(min_val),
    max_value=int(max_val),
    value=(int(min_val), int(max_val)),
    key="revenue_filter"
)

# Reset Button (Task 5)
if st.sidebar.button("Reset Filters"):
    for key in ["date_filter", "segment_filter", "revenue_filter"]:
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()

# =========================================================
# Wire Widgets & Filter DataFrame (Task 2)
# =========================================================
# Handle single-date selection during picker interaction
if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date = date_range[0] if isinstance(date_range, tuple) else date_range
    end_date = start_date

start_dt = pd.Timestamp(start_date)
end_dt = pd.Timestamp(end_date)

filtered_df = df[
    (df["date"] >= start_dt)
    & (df["date"] <= end_dt)
    & (df["segment"].isin(selected_segments))
    & (df["revenue"] >= min_rev)
    & (df["revenue"] <= max_rev)
]

# Handle Empty Filter Combinations (Task 4)
if len(filtered_df) == 0:
    st.warning("No data matches the current filters. Try broadening your selection.")
    st.stop()

# =========================================================
# Display Results (Previews & Statistics)
# =========================================================
st.header("Dataset Preview")

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Rows", f"{len(filtered_df):,}")
with col2:
    st.metric("Columns", str(len(filtered_df.columns)))
with col3:
    total_cells = filtered_df.shape[0] * filtered_df.shape[1]
    null_pct = (filtered_df.isnull().sum().sum() / total_cells * 100) if total_cells > 0 else 0.0
    st.metric("Null %", f"{null_pct:.1f}%")

st.write(f"Showing {len(filtered_df):,} of {len(df):,} records")

st.subheader("First 20 Rows")
st.dataframe(filtered_df.head(20), use_container_width=True)

st.subheader("Column Summary")
summary = pd.DataFrame({
    "Column": filtered_df.columns,
    "Type": filtered_df.dtypes.astype(str).values,
    "Non-Null": filtered_df.notnull().sum().values,
    "Null Count": filtered_df.isnull().sum().values,
    "Null %": (filtered_df.isnull().sum() / len(filtered_df) * 100).round(1).values
})
st.dataframe(summary, use_container_width=True)

st.subheader("Descriptive Statistics")
st.dataframe(filtered_df.describe(), use_container_width=True)

# Simple demonstration of downstream usage (Task 5)
st.subheader("Quick Exploration")
numeric_cols = filtered_df.select_dtypes(include="number").columns.tolist()
if numeric_cols:
    selected_col = st.selectbox("Select a column to visualise", numeric_cols)
    st.bar_chart(filtered_df[selected_col].value_counts().head(20))
else:
    st.info("No numeric columns found for visualization.")
