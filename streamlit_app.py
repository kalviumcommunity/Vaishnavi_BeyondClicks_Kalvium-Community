import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from scripts.kpi_dashboard import (
    load_orders,
    calculate_kpis,
    get_trend_indicator
)

# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="BeyondClicks Analytics Dashboard",
    page_icon="📊",
    layout="wide"
)

# ============================================================
# SESSION STATE INITIALIZATION
# ============================================================

if "selected_min_order_amount" not in st.session_state:
    st.session_state["selected_min_order_amount"] = None

if "analytics_workflow_step" not in st.session_state:
    st.session_state["analytics_workflow_step"] = 1

if "filtered_analysis_revenue" not in st.session_state:
    st.session_state["filtered_analysis_revenue"] = 0.0

if "uploaded_data" not in st.session_state:
    st.session_state["uploaded_data"] = None

if "uploaded_file_name" not in st.session_state:
    st.session_state["uploaded_file_name"] = None


# ============================================================
# CACHED DEFAULT DATA LOADING
# ============================================================

@st.cache_data
def load_default_data():
    """
    Load the default BeyondClicks dataset.

    Streamlit caches this function so the dataset does not
    need to be loaded from disk on every widget interaction.
    """
    data = load_orders()
    return data.copy()


# ============================================================
# CACHED UPLOAD DATA LOADING
# ============================================================

@st.cache_data
def load_uploaded_data(file_bytes, file_name):
    """
    Load uploaded CSV or JSON data.

    The file bytes are part of the cache key, so uploading
    a different file automatically creates a new cached result.
    """

    if file_name.lower().endswith(".csv"):

        from io import BytesIO

        return pd.read_csv(
            BytesIO(file_bytes)
        )

    elif file_name.lower().endswith(".json"):

        from io import BytesIO

        return pd.read_json(
            BytesIO(file_bytes)
        )

    else:
        raise ValueError(
            "Only CSV and JSON files are supported."
        )


# ============================================================
# COLUMN DETECTION
# ============================================================

def find_column(df, possible_names):
    """
    Find a column using case-insensitive matching.
    """

    lower_columns = {
        str(column).lower(): column
        for column in df.columns
    }

    for name in possible_names:

        if name.lower() in lower_columns:
            return lower_columns[name.lower()]

    return None


def detect_columns(df):
    """
    Automatically detect important business columns.
    """

    revenue_column = find_column(
        df,
        [
            "revenue",
            "amount",
            "sales",
            "order_amount",
            "order_value",
            "price",
            "total"
        ]
    )

    date_column = find_column(
        df,
        [
            "date",
            "order_date",
            "transaction_date",
            "created_at",
            "timestamp"
        ]
    )

    customer_column = find_column(
        df,
        [
            "customer_id",
            "customer",
            "user_id",
            "user",
            "client_id"
        ]
    )

    segment_column = find_column(
        df,
        [
            "segment",
            "category",
            "customer_segment",
            "product_category",
            "region",
            "channel"
        ]
    )

    return {
        "revenue": revenue_column,
        "date": date_column,
        "customer": customer_column,
        "segment": segment_column
    }


# ============================================================
# PREPARE DATA
# ============================================================

def prepare_data(data):
    """
    Clean and prepare the dataset for dashboard analysis.
    """

    prepared = data.copy()

    columns = detect_columns(prepared)

    # --------------------------------------------------------
    # Convert date column
    # --------------------------------------------------------

    if columns["date"] is not None:

        prepared[columns["date"]] = pd.to_datetime(
            prepared[columns["date"]],
            errors="coerce"
        )

    # --------------------------------------------------------
    # Convert revenue column to numeric
    # --------------------------------------------------------

    if columns["revenue"] is not None:

        prepared[columns["revenue"]] = pd.to_numeric(
            prepared[columns["revenue"]],
            errors="coerce"
        )

    return prepared, columns


# ============================================================
# LOAD DEFAULT DATA
# ============================================================

try:

    default_df = load_default_data()

except Exception as error:

    st.error(
        "Could not load the default BeyondClicks dataset."
    )

    st.exception(error)

    st.stop()


default_df, default_columns = prepare_data(
    default_df
)


# ============================================================
# SIDEBAR NAVIGATION
# ============================================================

st.sidebar.title("Navigation")

page = st.sidebar.radio(
    "Go to",
    [
        "Overview",
        "Trends",
        "Data Explorer",
        "Upload Dataset"
    ]
)


# ============================================================
# DATA SOURCE
# ============================================================

if st.session_state["uploaded_data"] is not None:

    df = st.session_state["uploaded_data"].copy()

    data_source = (
        f"Uploaded: "
        f"{st.session_state['uploaded_file_name']}"
    )

else:

    df = default_df.copy()

    data_source = "Default BeyondClicks Dataset"


df, detected = prepare_data(df)


# ============================================================
# DATA SOURCE INFORMATION
# ============================================================

st.sidebar.divider()

st.sidebar.write("### Current Data Source")

st.sidebar.info(
    data_source
)


# ============================================================
# REQUIRED COLUMN INFORMATION
# ============================================================

revenue_column = detected["revenue"]
date_column = detected["date"]
customer_column = detected["customer"]
segment_column = detected["segment"]


# ============================================================
# OVERVIEW PAGE
# ============================================================

if page == "Overview":

    st.title(
        "📊 BeyondClicks Analytics Dashboard"
    )

    st.caption(
        "Real-Time Business Performance Dashboard"
    )

    st.info(
        "All metrics and visualizations update dynamically "
        "when the dataset or filters change."
    )

    # --------------------------------------------------------
    # DATA SOURCE
    # --------------------------------------------------------

    st.write(
        f"**Data Source:** {data_source}"
    )

    st.divider()

    # --------------------------------------------------------
    # VALIDATE REVENUE COLUMN
    # --------------------------------------------------------

    if revenue_column is None:

        st.error(
            "No revenue/order amount column was detected. "
            "Expected a column such as 'revenue', 'amount', "
            "'sales', or 'order_amount'."
        )

        st.stop()

    # --------------------------------------------------------
    # REACTIVE KPI DATA
    # --------------------------------------------------------

    overview_df = df.copy()

    total_revenue = overview_df[
        revenue_column
    ].sum()

    avg_order = overview_df[
        revenue_column
    ].mean()

    row_count = len(
        overview_df
    )

    if customer_column is not None:

        unique_customers = overview_df[
            customer_column
        ].nunique()

    else:

        unique_customers = 0

    total_cells = (
        overview_df.shape[0]
        * overview_df.shape[1]
    )

    total_nulls = (
        overview_df.isnull()
        .sum()
        .sum()
    )

    if total_cells > 0:

        null_pct = (
            total_nulls
            / total_cells
            * 100
        )

    else:

        null_pct = 0

    data_quality = (
        100 - null_pct
    )

    # --------------------------------------------------------
    # FIVE REACTIVE KPIs
    # --------------------------------------------------------

    st.header(
        "Key Performance Indicators"
    )

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:

        st.metric(
            "Revenue",
            f"${total_revenue:,.2f}"
        )

    with col2:

        if pd.isna(avg_order):

            avg_order_display = "$0.00"

        else:

            avg_order_display = (
                f"${avg_order:,.2f}"
            )

        st.metric(
            "Average Order",
            avg_order_display
        )

    with col3:

        st.metric(
            "Records",
            f"{row_count:,}"
        )

    with col4:

        st.metric(
            "Customers",
            f"{unique_customers:,}"
        )

    with col5:

        st.metric(
            "Data Quality",
            f"{data_quality:.1f}%"
        )

    st.divider()

    # --------------------------------------------------------
    # KPI EXPLANATION
    # --------------------------------------------------------

    with st.expander(
        "About These Metrics"
    ):

        st.markdown(
            f"""
            ### Revenue

            Total value from the `{revenue_column}` column.

            ### Average Order

            Average value of the `{revenue_column}` column.

            ### Records

            Number of rows currently present in the dataset.

            ### Customers

            Number of unique customers detected from the
            `{customer_column}` column.

            ### Data Quality

            Percentage of dataset cells that are not null.

            These values are calculated dynamically from
            the current dataset.
            """
        )


# ============================================================
# TRENDS PAGE
# ============================================================

elif page == "Trends":

    st.title(
        "📈 Real-Time Trend Analysis"
    )

    st.caption(
        "KPIs and charts react to filter changes."
    )

    # --------------------------------------------------------
    # VALIDATE REVENUE COLUMN
    # --------------------------------------------------------

    if revenue_column is None:

        st.error(
            "No revenue/order amount column was detected."
        )

        st.stop()

    # --------------------------------------------------------
    # FILTER SECTION
    # --------------------------------------------------------

    st.sidebar.header(
        "Trend Filters"
    )

    min_amount = float(
        df[revenue_column]
        .dropna()
        .min()
    )

    max_amount = float(
        df[revenue_column]
        .dropna()
        .max()
    )

    # --------------------------------------------------------
    # INITIALIZE SESSION STATE
    # --------------------------------------------------------

    if (
        st.session_state[
            "selected_min_order_amount"
        ]
        is None
    ):

        st.session_state[
            "selected_min_order_amount"
        ] = min_amount

    # --------------------------------------------------------
    # MINIMUM ORDER FILTER
    # --------------------------------------------------------

    amount_range = st.sidebar.slider(
        "Minimum Order Amount",
        min_value=min_amount,
        max_value=max_amount,
        value=float(
            st.session_state[
                "selected_min_order_amount"
            ]
        ),
        step=1.0
    )

    # Save filter state

    st.session_state[
        "selected_min_order_amount"
    ] = amount_range

    # --------------------------------------------------------
    # FILTER DATA
    # --------------------------------------------------------

    filtered_df = df[
        df[revenue_column] >= amount_range
    ].copy()

    # --------------------------------------------------------
    # EMPTY FILTER CHECK
    # --------------------------------------------------------

    if filtered_df.empty:

        st.warning(
            "No data matches the current filters. "
            "Try lowering the minimum order amount."
        )

        st.stop()

    # ========================================================
    # FIVE REACTIVE KPIs
    # ========================================================

    st.header(
        "Filtered KPI Metrics"
    )

    filtered_revenue = filtered_df[
        revenue_column
    ].sum()

    filtered_avg_order = filtered_df[
        revenue_column
    ].mean()

    filtered_records = len(
        filtered_df
    )

    if customer_column is not None:

        filtered_customers = filtered_df[
            customer_column
        ].nunique()

    else:

        filtered_customers = 0

    filtered_total_cells = (
        filtered_df.shape[0]
        * filtered_df.shape[1]
    )

    filtered_nulls = (
        filtered_df.isnull()
        .sum()
        .sum()
    )

    if filtered_total_cells > 0:

        filtered_null_pct = (
            filtered_nulls
            / filtered_total_cells
            * 100
        )

    else:

        filtered_null_pct = 0

    filtered_quality = (
        100 - filtered_null_pct
    )

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:

        st.metric(
            "Revenue",
            f"${filtered_revenue:,.2f}"
        )

    with col2:

        st.metric(
            "Average Order",
            f"${filtered_avg_order:,.2f}"
        )

    with col3:

        st.metric(
            "Records",
            f"{filtered_records:,}"
        )

    with col4:

        st.metric(
            "Customers",
            f"{filtered_customers:,}"
        )

    with col5:

        st.metric(
            "Data Quality",
            f"{filtered_quality:.1f}%"
        )

    st.divider()

    # ========================================================
    # CHART 1 - LINE CHART
    # ========================================================

    if date_column is not None:

        st.header(
            "Chart 1: Revenue Over Time"
        )

        trend_df = (
            filtered_df
            .dropna(
                subset=[
                    date_column,
                    revenue_column
                ]
            )
            .groupby(
                date_column
            )[revenue_column]
            .sum()
            .reset_index()
            .sort_values(
                date_column
            )
        )

        if not trend_df.empty:

            st.line_chart(
                trend_df.set_index(
                    date_column
                )[revenue_column]
            )

        else:

            st.info(
                "No valid date values are available "
                "for the trend chart."
            )

    else:

        st.info(
            "No date column was detected, so the "
            "time-series chart cannot be displayed."
        )

    st.divider()

    # ========================================================
    # CHART 2 - BAR CHART
    # ========================================================

    st.header(
        "Chart 2: Revenue by Segment"
    )

    if segment_column is not None:

        segment_df = (
            filtered_df
            .dropna(
                subset=[
                    segment_column,
                    revenue_column
                ]
            )
            .groupby(
                segment_column
            )[revenue_column]
            .sum()
            .reset_index()
            .sort_values(
                revenue_column,
                ascending=False
            )
        )

        if not segment_df.empty:

            st.bar_chart(
                segment_df.set_index(
                    segment_column
                )[revenue_column]
            )

        else:

            st.info(
                "No segment data is available "
                "for the current filter."
            )

    else:

        st.info(
            "No segment/category column was detected. "
            "The bar chart requires a categorical column."
        )

    st.divider()

    # ========================================================
    # CHART 3 - PLOTLY HISTOGRAM
    # ========================================================

    st.header(
        "Chart 3: Order Value Distribution"
    )

    histogram_df = filtered_df[
        [revenue_column]
    ].dropna()

    if not histogram_df.empty:

        fig = px.histogram(
            histogram_df,
            x=revenue_column,
            nbins=30,
            title="Order Value Distribution"
        )

        fig.update_layout(
            xaxis_title="Order Value",
            yaxis_title="Number of Orders",
            height=500
        )

        st.plotly_chart(
            fig,
            width="stretch"
        )

    else:

        st.info(
            "No numeric order values are available "
            "for the histogram."
        )

    # ========================================================
    # ANALYTICS WORKFLOW
    # ========================================================

    st.divider()

    st.header(
        "Analytics Workflow"
    )

    # --------------------------------------------------------
    # STEP 1
    # --------------------------------------------------------

    st.subheader(
        "Step 1: Confirm Order Filter"
    )

    selected_amount = st.session_state[
        "selected_min_order_amount"
    ]

    st.write(
        f"Current minimum order amount: "
        f"${selected_amount:,.2f}"
    )

    if st.button(
        "Confirm Filter"
    ):

        st.session_state[
            "analytics_workflow_step"
        ] = 2

        st.session_state[
            "filtered_analysis_revenue"
        ] = filtered_df[
            revenue_column
        ].sum()

        st.success(
            "Order filter confirmed successfully!"
        )

    # --------------------------------------------------------
    # STEP 2
    # --------------------------------------------------------

    if (
        st.session_state[
            "analytics_workflow_step"
        ] >= 2
    ):

        st.subheader(
            "Step 2: Filtered Analysis"
        )

        selected_amount = st.session_state[
            "selected_min_order_amount"
        ]

        st.write(
            f"Analysing orders with amount ≥ "
            f"${selected_amount:,.2f}"
        )

        analysis_revenue = st.session_state[
            "filtered_analysis_revenue"
        ]

        analysis_orders = len(
            filtered_df
        )

        if not filtered_df.empty:

            analysis_aov = filtered_df[
                revenue_column
            ].mean()

        else:

            analysis_aov = 0

        col1, col2, col3 = st.columns(3)

        with col1:

            st.metric(
                "Analysis Revenue",
                f"${analysis_revenue:,.2f}"
            )

        with col2:

            st.metric(
                "Analysis Orders",
                f"{analysis_orders:,}"
            )

        with col3:

            st.metric(
                "Analysis AOV",
                f"${analysis_aov:,.2f}"
            )

    # --------------------------------------------------------
    # RESET WORKFLOW
    # --------------------------------------------------------

    if st.sidebar.button(
        "Reset Workflow"
    ):

        st.session_state[
            "selected_min_order_amount"
        ] = None

        st.session_state[
            "analytics_workflow_step"
        ] = 1

        st.session_state[
            "filtered_analysis_revenue"
        ] = 0.0

        st.rerun()


# ============================================================
# DATA EXPLORER PAGE
# ============================================================

elif page == "Data Explorer":

    st.title(
        "📂 Data Explorer"
    )

    st.caption(
        "Explore the currently active dataset."
    )

    # --------------------------------------------------------
    # VALIDATE REVENUE COLUMN
    # --------------------------------------------------------

    if revenue_column is not None:

        st.sidebar.header(
            "Explorer Filters"
        )

        min_amount = float(
            df[revenue_column]
            .dropna()
            .min()
        )

        max_amount = float(
            df[revenue_column]
            .dropna()
            .max()
        )

        explorer_amount = st.sidebar.slider(
            "Minimum Order Amount",
            min_value=min_amount,
            max_value=max_amount,
            value=min_amount,
            step=1.0,
            key="explorer_slider"
        )

        explorer_df = df[
            df[revenue_column] >= explorer_amount
        ].copy()

    else:

        explorer_df = df.copy()

    # --------------------------------------------------------
    # EMPTY CHECK
    # --------------------------------------------------------

    if explorer_df.empty:

        st.warning(
            "No records match the current filter."
        )

        st.stop()

    # --------------------------------------------------------
    # SUMMARY
    # --------------------------------------------------------

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "Rows Displayed",
            f"{len(explorer_df):,}"
        )

    with col2:

        if revenue_column is not None:

            st.metric(
                "Total Revenue",
                f"${explorer_df[revenue_column].sum():,.2f}"
            )

        else:

            st.metric(
                "Total Revenue",
                "N/A"
            )

    with col3:

        st.metric(
            "Columns",
            f"{len(explorer_df.columns):,}"
        )

    st.divider()

    # --------------------------------------------------------
    # DATA TABLE
    # --------------------------------------------------------

    st.header(
        "Order Dataset"
    )

    st.dataframe(
        explorer_df,
        width="stretch"
    )

    # --------------------------------------------------------
    # DATASET INFORMATION
    # --------------------------------------------------------

    with st.expander(
        "Dataset Information"
    ):

        st.write(
            f"**Rows:** {len(explorer_df):,}"
        )

        st.write(
            f"**Columns:** {len(explorer_df.columns):,}"
        )

        st.write(
            f"**Revenue Column:** "
            f"{revenue_column or 'Not detected'}"
        )

        st.write(
            f"**Date Column:** "
            f"{date_column or 'Not detected'}"
        )

        st.write(
            f"**Customer Column:** "
            f"{customer_column or 'Not detected'}"
        )

        st.write(
            f"**Segment Column:** "
            f"{segment_column or 'Not detected'}"
        )

    st.divider()

    # --------------------------------------------------------
    # DOWNLOAD
    # --------------------------------------------------------

    st.header(
        "Download"
    )

    csv = explorer_df.to_csv(
        index=False
    )

    st.download_button(
        label="📥 Download Filtered Data",
        data=csv,
        file_name="filtered_orders.csv",
        mime="text/csv"
    )


# ============================================================
# UPLOAD DATASET PAGE
# ============================================================

elif page == "Upload Dataset":

    st.title(
        "📤 Dataset Upload & Preview"
    )

    st.caption(
        "Upload a CSV or JSON dataset and use it "
        "as the live dashboard data source."
    )

    # --------------------------------------------------------
    # FILE UPLOADER
    # --------------------------------------------------------

    uploaded_file = st.file_uploader(
        "Choose a CSV or JSON file",
        type=["csv", "json"],
        help="Supported formats: CSV and JSON"
    )

    # --------------------------------------------------------
    # NO FILE
    # --------------------------------------------------------

    if uploaded_file is None:

        st.info(
            "Upload a CSV or JSON file to replace "
            "the current dashboard dataset."
        )

        st.write(
            "The dashboard will automatically detect "
            "common columns such as:"
        )

        st.markdown(
            """
            - `revenue` / `amount`
            - `date` / `order_date`
            - `customer_id`
            - `segment` / `category`
            """
        )

    # --------------------------------------------------------
    # FILE UPLOADED
    # --------------------------------------------------------

    else:

        try:

            uploaded_df = load_uploaded_data(
                uploaded_file.getvalue(),
                uploaded_file.name
            )

            if uploaded_df.empty:

                st.warning(
                    "The uploaded file is empty."
                )

                st.stop()

            # ------------------------------------------------
            # STORE UPLOADED DATA
            # ------------------------------------------------

            st.session_state[
                "uploaded_data"
            ] = uploaded_df

            st.session_state[
                "uploaded_file_name"
            ] = uploaded_file.name

            st.success(
                f"Loaded {uploaded_file.name} successfully."
            )

            # ------------------------------------------------
            # PREPARE
            # ------------------------------------------------

            preview_df, preview_columns = prepare_data(
                uploaded_df
            )

            # ------------------------------------------------
            # DETECTED COLUMNS
            # ------------------------------------------------

            st.subheader(
                "Detected Columns"
            )

            detection_col1, detection_col2 = st.columns(2)

            with detection_col1:

                st.write(
                    f"**Revenue:** "
                    f"{preview_columns['revenue'] or 'Not detected'}"
                )

                st.write(
                    f"**Date:** "
                    f"{preview_columns['date'] or 'Not detected'}"
                )

            with detection_col2:

                st.write(
                    f"**Customer:** "
                    f"{preview_columns['customer'] or 'Not detected'}"
                )

                st.write(
                    f"**Segment:** "
                    f"{preview_columns['segment'] or 'Not detected'}"
                )

            st.divider()

            # ------------------------------------------------
            # FILE SUMMARY
            # ------------------------------------------------

            st.header(
                "Dataset Preview"
            )

            col1, col2, col3 = st.columns(3)

            with col1:

                st.metric(
                    "Rows",
                    f"{len(preview_df):,}"
                )

            with col2:

                st.metric(
                    "Columns",
                    f"{len(preview_df.columns):,}"
                )

            with col3:

                total_cells = (
                    preview_df.shape[0]
                    * preview_df.shape[1]
                )

                total_nulls = (
                    preview_df.isnull()
                    .sum()
                    .sum()
                )

                if total_cells > 0:

                    null_pct = (
                        total_nulls
                        / total_cells
                        * 100
                    )

                else:

                    null_pct = 0

                st.metric(
                    "Null %",
                    f"{null_pct:.1f}%"
                )

            # ------------------------------------------------
            # FIRST 10 ROWS
            # ------------------------------------------------

            st.subheader(
                "First 10 Rows"
            )

            st.dataframe(
                preview_df.head(10),
                width="stretch"
            )

            # ------------------------------------------------
            # COLUMN SUMMARY
            # ------------------------------------------------

            st.subheader(
                "Column Summary"
            )

            column_summary = pd.DataFrame(
                {
                    "Column": preview_df.columns,

                    "Type": (
                        preview_df
                        .dtypes
                        .astype(str)
                        .values
                    ),

                    "Non-Null": (
                        preview_df
                        .notnull()
                        .sum()
                        .values
                    ),

                    "Null Count": (
                        preview_df
                        .isnull()
                        .sum()
                        .values
                    ),

                    "Null %": (
                        preview_df
                        .isnull()
                        .sum()
                        / len(preview_df)
                        * 100
                    )
                    .round(1)
                    .values
                }
            )

            st.dataframe(
                column_summary,
                width="stretch"
            )

            # ------------------------------------------------
            # DESCRIPTIVE STATISTICS
            # ------------------------------------------------

            st.divider()

            st.subheader(
                "Descriptive Statistics"
            )

            numeric_df = preview_df.select_dtypes(
                include="number"
            )

            if numeric_df.empty:

                st.info(
                    "No numeric columns were found."
                )

            else:

                st.dataframe(
                    numeric_df.describe(),
                    width="stretch"
                )

            # ------------------------------------------------
            # ACTIVATE DATASET
            # ------------------------------------------------

            st.divider()

            st.success(
                "This uploaded dataset is now the active "
                "dashboard dataset. Go to Overview or Trends "
                "to see the KPIs and charts update."
            )

            if st.button(
                "🔄 Reload Dashboard With Uploaded Data"
            ):

                st.rerun()

        except Exception as error:

            st.error(
                "Could not read this file. "
                "Please check that the CSV or JSON format "
                "is valid."
            )

            st.exception(error)


# ============================================================
# FINAL SIDEBAR INFORMATION
# ============================================================

st.sidebar.divider()

st.sidebar.caption(
    "BeyondClicks • Real-Time KPI Dashboard"
)

st.sidebar.caption(
    "Data loading is cached with @st.cache_data."
)