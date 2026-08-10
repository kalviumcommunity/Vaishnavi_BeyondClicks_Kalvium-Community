import streamlit as st
import pandas as pd

# Page config
st.set_page_config(
    page_title="BeyondClicks Analytics Dashboard",
    page_icon="📊",
    layout="wide"
)

st.title("📂 Dataset Uploader & Analyzer")
st.caption("Upload a CSV or JSON dataset to get an immediate preview, metrics, and basic statistics.")

uploaded_file = st.file_uploader("Upload your dataset", type=["csv", "json"])

if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith(".json"):
            df = pd.read_json(uploaded_file)
        else:
            st.error("Unsupported file type.")
            st.stop()

        if len(df) == 0:
            st.warning("Uploaded file is empty.")
            st.stop()
            
    except Exception:
        st.error("Could not read this file. Check the format and try again.")
        st.stop()

    st.success("Loaded: " + uploaded_file.name
               + " (" + str(len(df)) + " rows, "
               + str(len(df.columns)) + " columns)")
               
    st.header("Dataset Preview")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Rows", f"{len(df):,}")
    with col2:
        st.metric("Columns", str(len(df.columns)))
    with col3:
        total_cells = df.shape[0] * df.shape[1]
        null_pct = (df.isnull().sum().sum() / total_cells * 100) if total_cells > 0 else 0.0
        st.metric("Null %", f"{null_pct:.1f}%")

    st.subheader("First 10 Rows")
    st.dataframe(df.head(10), use_container_width=True)

    st.subheader("Column Summary")
    summary = pd.DataFrame({
        "Column": df.columns,
        "Type": df.dtypes.astype(str).values,
        "Non-Null": df.notnull().sum().values,
        "Null Count": df.isnull().sum().values,
        "Null %": (df.isnull().sum() / len(df) * 100).round(1).values
    })
    st.dataframe(summary, use_container_width=True)

    st.subheader("Descriptive Statistics")
    st.dataframe(df.describe(), use_container_width=True)

    # Simple demonstration of downstream usage
    st.subheader("Quick Exploration")
    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    if numeric_cols:
        selected_col = st.selectbox("Select a column to visualise", numeric_cols)
        st.bar_chart(df[selected_col].value_counts().head(20))
    else:
        st.info("No numeric columns found for visualization.")
else:
    st.info("Upload a CSV or JSON file to begin.")
