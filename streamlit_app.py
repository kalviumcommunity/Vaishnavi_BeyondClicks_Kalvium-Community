import streamlit as st
import pandas as pd
import plotly.graph_objects as go


from scripts.kpi_dashboard import (
    load_orders,
    calculate_kpis,
    get_trend_indicator
)


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="BeyondClicks Analytics Dashboard",
    page_icon="📊",
    layout="wide"
)

# =========================================================
# SESSION STATE INITIALIZATION
# =========================================================

# Stores the user's selected minimum order amount
# so the filter survives Streamlit reruns.
if "selected_min_order_amount" not in st.session_state:
    st.session_state["selected_min_order_amount"] = None

# Tracks which analytics workflow step is completed.
if "analytics_workflow_step" not in st.session_state:
    st.session_state["analytics_workflow_step"] = 1

# Stores the calculated revenue from the confirmed filter.
if "filtered_analysis_revenue" not in st.session_state:
    st.session_state["filtered_analysis_revenue"] = 0.0

# =========================================================
# LOAD DEFAULT BEYONDCLICKS DATA
# =========================================================

df = load_orders()

df["order_date"] = pd.to_datetime(df["order_date"])


# =========================================================
# KPI CALCULATIONS
# =========================================================

kpis, current_year, current_month, previous_year, previous_month = (
    calculate_kpis(df)
)


# =========================================================
# SIDEBAR NAVIGATION
# =========================================================

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


# =========================================================
# OVERVIEW PAGE
# =========================================================

if page == "Overview":

    st.title("📊 BeyondClicks Analytics Dashboard")

    st.caption(
        "Business Performance Summary"
    )


    # -----------------------------------------------------
    # KPI PERIOD
    # -----------------------------------------------------

    st.write(
        f"**Current Period:** {current_year}-{current_month:02d}  |  "
        f"**Previous Period:** {previous_year}-{previous_month:02d}"
    )


    # -----------------------------------------------------
    # KPI CARDS
    # -----------------------------------------------------

    st.header("Key Performance Indicators")

    cols = st.columns(5)


    for col, (_, row) in zip(cols, kpis.iterrows()):

        metric = row["Metric"]
        current = row["Current"]
        change = row["Change_Pct"]


        with col:

            if pd.isna(current):

                st.metric(
                    label=metric,
                    value="N/A",
                    delta="Unavailable"
                )

            else:

                if metric == "Revenue":

                    value = f"${current:,.2f}"

                elif metric == "AOV":

                    value = f"${current:,.2f}"

                elif metric == "Active Users":

                    value = f"{int(current):,}"

                elif metric == "Churn Rate":

                    value = f"{current:.1f}%"

                elif metric == "Satisfaction":

                    value = f"{current:.1f}/5"

                else:

                    value = str(current)


                arrow, color = get_trend_indicator(
                    change,
                    metric
                )


                st.metric(
                    label=metric,
                    value=value,
                    delta=f"{arrow} {change:+.1f}%"
                )


    st.divider()


    # -----------------------------------------------------
    # KPI DETAILS
    # -----------------------------------------------------

    st.header("KPI Details")

    display_df = kpis.copy()


    display_df["Change"] = display_df["Change_Pct"].apply(
        lambda x:
        "N/A"
        if pd.isna(x)
        else f"{x:+.1f}%"
    )


    st.dataframe(
        display_df[
            [
                "Metric",
                "Current",
                "Prior",
                "Change"
            ]
        ],
        width="stretch"
    )


    st.divider()


    # -----------------------------------------------------
    # ABOUT METRICS
    # -----------------------------------------------------

    with st.expander("About These Metrics"):

        st.markdown(
            """
            ### Revenue
            Total sales generated during the selected period.

            ### Active Users
            Number of unique customers who placed orders.

            ### Average Order Value (AOV)
            Average revenue generated per order.

            ### Churn Rate
            Percentage of customers who did not return.

            ### Satisfaction
            Placeholder KPI for future customer feedback analysis.

            These KPIs compare the current reporting period
            with the previous period.
            """
        )


# =========================================================
# TRENDS PAGE
# =========================================================

elif page == "Trends":

    st.title("📈 Trend Analysis")

    st.header("Interactive Analytics")

    st.subheader("Order Performance Over Time")

    st.write(
        "Explore order performance using an interactive "
        "Plotly visualization."
    )


    # -----------------------------------------------------
    # SIDEBAR FILTER
    # -----------------------------------------------------

    st.sidebar.header("Trend Filters")

    min_amount = float(df["amount"].min())
    max_amount = float(df["amount"].max())


   # =========================================================
    # PERSISTENT ORDER AMOUNT FILTER
    # =========================================================

    if st.session_state["selected_min_order_amount"] is None:
        st.session_state["selected_min_order_amount"] = min_amount

    amount_range = st.sidebar.slider(
        "Minimum Order Amount",
        min_value=min_amount,
        max_value=max_amount,
        value=st.session_state["selected_min_order_amount"],
        step=1.0
    )

    # Save the user's selection in session state
    st.session_state["selected_min_order_amount"] = amount_range

    # -----------------------------------------------------
    # FILTER DATA
    # -----------------------------------------------------

    filtered_df = df[
        df["amount"] >= amount_range
    ].copy()


    # -----------------------------------------------------
    # SUMMARY METRICS
    # -----------------------------------------------------

    col1, col2, col3 = st.columns(3)


    with col1:

        st.metric(
            "Filtered Revenue",
            f"${filtered_df['amount'].sum():,.2f}"
        )


    with col2:

        st.metric(
            "Filtered Orders",
            f"{len(filtered_df):,}"
        )


    with col3:

        average_order = filtered_df["amount"].mean()

        st.metric(
            "Average Order Value",
            f"${average_order:,.2f}"
        )


    st.divider()


    # -----------------------------------------------------
    # PLOTLY CHART
    # -----------------------------------------------------

    fig = go.Figure()


    fig.add_trace(
        go.Scatter(
            x=filtered_df["order_date"],
            y=filtered_df["amount"],
            mode="markers",
            name="Orders",

            customdata=filtered_df[
                [
                    "order_id",
                    "customer_id"
                ]
            ],

            hovertemplate=(
                "<b>Date: %{x|%Y-%m-%d}</b><br>"
                "Order Amount: $%{y:,.2f}<br>"
                "Order ID: %{customdata[0]}<br>"
                "Customer ID: %{customdata[1]}"
                "<extra></extra>"
            ),

            marker=dict(
                size=10
            )
        )
    )


    fig.update_layout(
        title="Orders Over Time",
        xaxis_title="Order Date",
        yaxis_title="Order Amount ($)",
        height=550,
        hovermode="closest",
        dragmode="zoom"
    )


    # -----------------------------------------------------
    # DATE RANGE SELECTOR
    # -----------------------------------------------------

    fig.update_xaxes(

        rangeselector=dict(

            buttons=[

                dict(
                    count=1,
                    label="1M",
                    step="month",
                    stepmode="backward"
                ),

                dict(
                    count=3,
                    label="3M",
                    step="month",
                    stepmode="backward"
                ),

                dict(
                    count=6,
                    label="6M",
                    step="month",
                    stepmode="backward"
                ),

                dict(
                    step="all",
                    label="All"
                )

            ]
        ),

        rangeslider=dict(
            visible=True
        )
    )


    # -----------------------------------------------------
    # DISPLAY CHART
    # -----------------------------------------------------

    st.plotly_chart(
        fig,
        width="stretch"
    )


    # -----------------------------------------------------
    # CHART INFORMATION
    # -----------------------------------------------------

    with st.expander("About This Chart"):

        st.write(
            """
            This chart displays individual customer orders
            over time.

            Hover over a point to see:

            - Order ID
            - Customer ID
            - Order Amount
            - Order Date

            Use the range slider and zoom controls to explore
            specific periods.
            """
        )


# =========================================================
# DATA EXPLORER PAGE
# =========================================================

elif page == "Data Explorer":

    st.title("📂 Data Explorer")

    st.header("Order Dataset")

    st.subheader("Filter and Explore Orders")


    # -----------------------------------------------------
    # SIDEBAR FILTER
    # -----------------------------------------------------

    st.sidebar.header("Explorer Filters")

    min_amount = float(df["amount"].min())
    max_amount = float(df["amount"].max())


    amount_range = st.sidebar.slider(
        "Minimum Order Amount",
        min_value=min_amount,
        max_value=max_amount,
        value=min_amount,
        step=1.0,
        key="explorer_slider"
    )


    # -----------------------------------------------------
    # FILTER DATA
    # -----------------------------------------------------

    filtered_df = df[
        df["amount"] >= amount_range
    ].copy()


    # -----------------------------------------------------
    # SUMMARY
    # -----------------------------------------------------

    col1, col2 = st.columns(2)


    with col1:

        st.metric(
            "Orders Displayed",
            len(filtered_df)
        )


    with col2:

        st.metric(
            "Total Revenue",
            f"${filtered_df['amount'].sum():,.2f}"
        )


    st.divider()


    # -----------------------------------------------------
    # DATA TABLE
    # -----------------------------------------------------

    st.dataframe(
        filtered_df[
            [
                "order_id",
                "customer_id",
                "order_date",
                "amount"
            ]
        ],
        width="stretch"
    )


    # -----------------------------------------------------
    # DATASET INFORMATION
    # -----------------------------------------------------

    with st.expander("Dataset Information"):

        st.write(
            """
            **Dataset Columns**

            - **order_id** → Unique order identifier
            - **customer_id** → Customer identifier
            - **order_date** → Date when the order was placed
            - **amount** → Order value in USD

            Use the sidebar filter to display only orders
            above a selected amount.
            """
        )


    st.divider()


    # -----------------------------------------------------
    # DOWNLOAD
    # -----------------------------------------------------

    st.header("Download")

    csv = filtered_df.to_csv(
        index=False
    )


    st.download_button(
        label="📥 Download Filtered Orders",
        data=csv,
        file_name="filtered_orders.csv",
        mime="text/csv"
    )


# =========================================================
# UPLOAD DATASET PAGE - ASSIGNMENT 2.52
# =========================================================

elif page == "Upload Dataset":

    st.title("📤 Dataset Upload & Preview")

    st.caption(
        "Upload your own CSV or JSON dataset and "
        "start exploring it immediately."
    )


    # =====================================================
    # TASK 1 - FILE UPLOADER
    # =====================================================

    st.header("Upload Dataset")

    uploaded_file = st.file_uploader(
        "Choose a CSV or JSON file",
        type=["csv", "json"],
        help="Supported formats: CSV and JSON"
    )


    # -----------------------------------------------------
    # NO FILE UPLOADED
    # -----------------------------------------------------

    if uploaded_file is None:

        st.info(
            "Upload a CSV or JSON file to begin."
        )


    # -----------------------------------------------------
    # FILE UPLOADED
    # -----------------------------------------------------

    else:

        try:

            # ---------------------------------------------
            # LOAD CSV
            # ---------------------------------------------

            if uploaded_file.name.lower().endswith(".csv"):

                uploaded_df = pd.read_csv(
                    uploaded_file
                )


            # ---------------------------------------------
            # LOAD JSON
            # ---------------------------------------------

            elif uploaded_file.name.lower().endswith(".json"):

                uploaded_df = pd.read_json(
                    uploaded_file
                )


            # ---------------------------------------------
            # UNSUPPORTED FILE
            # ---------------------------------------------

            else:

                st.error(
                    "Unsupported file type. "
                    "Please upload a CSV or JSON file."
                )

                st.stop()


            # ---------------------------------------------
            # EMPTY FILE CHECK
            # ---------------------------------------------

            if uploaded_df.empty:

                st.warning(
                    "The uploaded file is empty. "
                    "Please upload a file containing data."
                )

                st.stop()


            # ---------------------------------------------
            # SUCCESS MESSAGE
            # ---------------------------------------------

            st.success(
                f"Loaded: {uploaded_file.name} "
                f"({len(uploaded_df):,} rows, "
                f"{len(uploaded_df.columns):,} columns)"
            )

            # =========================================================
            # TASK 2 - AUTOMATIC DATASET PREVIEW
            # =========================================================

            st.divider()

            st.header("Dataset Preview")

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric(
                    "Rows",
                    f"{len(uploaded_df):,}"
                )

            with col2:
                st.metric(
                    "Columns",
                    f"{len(uploaded_df.columns):,}"
                )

            with col3:

                total_nulls = uploaded_df.isnull().sum().sum()

                total_cells = (
                    uploaded_df.shape[0]
                    * uploaded_df.shape[1]
                )

                null_pct = (
                    (total_nulls / total_cells) * 100
                    if total_cells > 0
                    else 0
                )

                st.metric(
                    "Null %",
                    f"{null_pct:.1f}%"
                )


            st.subheader("First 10 Rows")

            st.dataframe(
                uploaded_df.head(10),
                width="stretch"
            )


            st.subheader("Column Summary")

            column_summary = pd.DataFrame({
                "Column": uploaded_df.columns,
                "Type": uploaded_df.dtypes.astype(str).values,
                "Non-Null": uploaded_df.notnull().sum().values,
                "Null Count": uploaded_df.isnull().sum().values,
                "Null %": (
                    uploaded_df.isnull().sum()
                    / len(uploaded_df)
                    * 100
                ).round(1).values
            })

            st.dataframe(
                column_summary,
                width="stretch"
            )

            # =========================================================
            # TASK 3 - BASIC DESCRIPTIVE STATISTICS
            # =========================================================

            st.divider()

            st.subheader("Descriptive Statistics")

            numeric_df = uploaded_df.select_dtypes(include="number")

            if numeric_df.empty:

                st.info(
                    "No numeric columns are available "
                    "for descriptive statistics."
                )

            else:

                st.dataframe(
                    numeric_df.describe(),
                    width="stretch"
                )

            # =========================================================
            # TASK 5 - QUICK EXPLORATION OF UPLOADED DATA
            # =========================================================

            st.divider()

            st.header("Quick Exploration")

            numeric_columns = uploaded_df.select_dtypes(
                include="number"
            ).columns.tolist()


            if numeric_columns:

                selected_column = st.selectbox(
                    "Select a numeric column to explore",
                    numeric_columns
                )

                st.subheader(
                    f"Distribution of {selected_column}"
                )

                st.bar_chart(
                    uploaded_df[selected_column]
                    .value_counts()
                    .head(20)
                )

            else:

                st.info(
                    "No numeric columns are available "
                    "for quick exploration."
                )
        # ---------------------------------------------
        # INVALID FILE HANDLING
        # ---------------------------------------------

        except Exception as e:

            st.error(
                "Could not read this file. "
                "Please check that the CSV or JSON format is valid "
                "and try again."
            )

            st.stop()

        # -------------------------------------------------
        # ROWS / COLUMNS / NULL %
        # -------------------------------------------------

        col1, col2, col3 = st.columns(3)


        with col1:

            st.metric(
                "Rows",
                f"{len(uploaded_df):,}"
            )


        with col2:

            st.metric(
                "Columns",
                f"{len(uploaded_df.columns):,}"
            )


        with col3:

            total_nulls = (
                uploaded_df.isnull()
                .sum()
                .sum()
            )

            total_cells = (
                uploaded_df.shape[0]
                * uploaded_df.shape[1]
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
                "Overall Null %",
                f"{null_pct:.1f}%"
            )


        # =================================================
        # FIRST 10 ROWS
        # =================================================

        st.subheader("First 10 Rows")

        st.dataframe(
            uploaded_df.head(10),
            width="stretch"
        )


        # =================================================
        # COLUMN SUMMARY
        # =================================================

        st.subheader("Column Summary")


        column_summary = pd.DataFrame(
            {
                "Column": uploaded_df.columns,

                "Type": (
                    uploaded_df
                    .dtypes
                    .astype(str)
                    .values
                ),

                "Non-Null": (
                    uploaded_df
                    .notnull()
                    .sum()
                    .values
                ),

                "Null Count": (
                    uploaded_df
                    .isnull()
                    .sum()
                    .values
                ),

                "Null %": (
                    uploaded_df
                    .isnull()
                    .sum()
                    / len(uploaded_df)
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


        # =================================================
        # TASK 3 - DESCRIPTIVE STATISTICS
        # =================================================

        st.divider()

        st.subheader(
            "Descriptive Statistics"
        )


        numeric_columns = (
            uploaded_df
            .select_dtypes(
                include="number"
            )
            .columns
            .tolist()
        )


        if numeric_columns:

            st.dataframe(
                uploaded_df[
                    numeric_columns
                ].describe(),
                width="stretch"
            )

        else:

            st.info(
                "No numeric columns were found. "
                "Descriptive statistics are available "
                "for numeric columns only."
            )


        # =================================================
        # TASK 5 - QUICK EXPLORATION
        # =================================================

        st.divider()

        st.header(
            "Quick Exploration"
        )


        if numeric_columns:

            selected_column = st.selectbox(
                "Select a numeric column to visualize",
                numeric_columns
            )


            # ---------------------------------------------
            # FILTER
            # ---------------------------------------------

            selected_values = uploaded_df[
                selected_column
            ].dropna()


            if not selected_values.empty:

                min_value = float(
                    selected_values.min()
                )

                max_value = float(
                    selected_values.max()
                )


                if min_value < max_value:

                    selected_range = st.slider(
                        "Filter values",
                        min_value=min_value,
                        max_value=max_value,
                        value=(
                            min_value,
                            max_value
                        ),
                        key="upload_range"
                    )


                    filtered_upload_df = uploaded_df[
                        uploaded_df[
                            selected_column
                        ].between(
                            selected_range[0],
                            selected_range[1]
                        )
                    ].copy()


                else:

                    filtered_upload_df = uploaded_df.copy()


                # -----------------------------------------
                # FILTERED SUMMARY
                # -----------------------------------------

                col1, col2, col3 = st.columns(3)


                with col1:

                    st.metric(
                        "Filtered Rows",
                        f"{len(filtered_upload_df):,}"
                    )


                with col2:

                    st.metric(
                        "Minimum",
                        f"{selected_values.min():,.2f}"
                    )


                with col3:

                    st.metric(
                        "Maximum",
                        f"{selected_values.max():,.2f}"
                    )


                # -----------------------------------------
                # CHART
                # -----------------------------------------

                st.subheader(
                    f"Distribution of {selected_column}"
                )


                st.bar_chart(
                    filtered_upload_df[
                        selected_column
                    ].value_counts()
                    .head(20)
                )


                # -----------------------------------------
                # FILTERED DATA
                # -----------------------------------------

                with st.expander(
                    "View Filtered Uploaded Data"
                ):

                    st.dataframe(
                        filtered_upload_df,
                        width="stretch"
                    )


            else:

                st.warning(
                    f"The selected column "
                    f"'{selected_column}' contains "
                    "no usable numeric values."
                )


        else:

            st.info(
                "Upload a dataset containing numeric "
                "columns to enable quick visualization."
            )
# =========================================================
# MULTI-STEP ANALYTICS WORKFLOW
# =========================================================

# This workflow is used on the Trends page because
# filtered_df is created there.

if page == "Trends":

    st.divider()

    st.header("Analytics Workflow")

    # =====================================================
    # STEP 1 - CONFIRM FILTER
    # =====================================================

    st.subheader("Step 1: Confirm Order Filter")

    # Read the persisted minimum order amount.
    # This value survives Streamlit reruns.
    selected_amount = st.session_state[
        "selected_min_order_amount"
    ]

    st.write(
        f"Current minimum order amount: "
        f"${selected_amount:,.2f}"
    )

    if st.button("Confirm Filter"):

        # Move the workflow to Step 2.
        st.session_state[
            "analytics_workflow_step"
        ] = 2

        # Store the calculated revenue so it
        # persists across Streamlit reruns.
        st.session_state[
            "filtered_analysis_revenue"
        ] = filtered_df["amount"].sum()

        st.success(
            "Order filter confirmed successfully!"
        )

    # =====================================================
    # STEP 2 - FILTERED ANALYSIS
    # =====================================================

    if st.session_state[
        "analytics_workflow_step"
    ] >= 2:

        st.subheader("Step 2: Filtered Analysis")

        # Read the selected filter from session state.
        selected_amount = st.session_state[
            "selected_min_order_amount"
        ]

        st.write(
            f"Analysing orders with amount ≥ "
            f"${selected_amount:,.2f}"
        )

        # Read the stored revenue result.
        analysis_revenue = st.session_state[
            "filtered_analysis_revenue"
        ]

        # Calculate the number of filtered orders.
        analysis_orders = len(filtered_df)

        # Calculate average order value.
        if not filtered_df.empty:
            analysis_aov = filtered_df["amount"].mean()
        else:
            analysis_aov = 0

        # -------------------------------------------------
        # ANALYSIS METRICS
        # -------------------------------------------------

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

    # =====================================================
    # RESET WORKFLOW
    # =====================================================

    if st.sidebar.button("Reset Workflow"):

        # Clear only the session state values
        # belonging to this analytics workflow.
        for key in [
            "selected_min_order_amount",
            "analytics_workflow_step",
            "filtered_analysis_revenue"
        ]:

            if key in st.session_state:
                del st.session_state[key]

        # Rerun the application so the default
        # session state values are recreated.
        st.rerun()
        
        # =================================================
        # DOWNLOAD UPLOADED DATA
        # =================================================

        st.divider()

        st.header(
            "Download Uploaded Dataset"
        )


        uploaded_csv = uploaded_df.to_csv(
            index=False
        )


        st.download_button(
            label="📥 Download Dataset as CSV",
            data=uploaded_csv,
            file_name="uploaded_dataset.csv",
            mime="text/csv"
        )