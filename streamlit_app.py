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
# LOAD DATA
# =========================================================

df = load_orders()
df["order_date"] = pd.to_datetime(df["order_date"])

kpis, current_year, current_month, previous_year, previous_month = calculate_kpis(df)

# =========================================================
# SIDEBAR NAVIGATION
# =========================================================

st.sidebar.title("Navigation")

page = st.sidebar.radio(
    "Go to",
    [
        "Overview",
        "Trends",
        "Data Explorer"
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

    st.write(
        f"**Current Period:** {current_year}-{current_month:02d}  |  "
        f"**Previous Period:** {previous_year}-{previous_month:02d}"
    )

    st.header("Key Performance Indicators")

    cols = st.columns(5)

    # =========================================================
    # KPI CARDS
    # =========================================================

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

    # =========================================================
    # KPI DETAILS
    # =========================================================

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

    # =========================================================
    # ABOUT METRICS
    # =========================================================

    with st.expander("About These Metrics"):

        st.markdown("""
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

These KPIs compare the current reporting period with the previous period.
""")

# =========================================================
# TRENDS PAGE
# =========================================================

elif page == "Trends":

    st.title("📈 Trend Analysis")

    st.header("Interactive Analytics")

    st.subheader("Order Performance Over Time")

    st.write(
        "Explore order performance using an interactive Plotly visualization."
    )

    # -----------------------------------------------------
    # Sidebar Filter
    # -----------------------------------------------------

    st.sidebar.header("Filters")

    min_amount = float(df["amount"].min())
    max_amount = float(df["amount"].max())

    amount_range = st.sidebar.slider(
        "Minimum Order Amount",
        min_value=min_amount,
        max_value=max_amount,
        value=min_amount,
        step=1.0
    )

    filtered_df = df[
        df["amount"] >= amount_range
    ].copy()

    # -----------------------------------------------------
    # Summary Metrics
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
        st.metric(
            "Average Order Value",
            f"${filtered_df['amount'].mean():,.2f}"
        )

    st.divider()

    # -----------------------------------------------------
    # Plotly Chart
    # -----------------------------------------------------

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=filtered_df["order_date"],
            y=filtered_df["amount"],
            mode="markers",
            name="Orders",
            customdata=filtered_df[
                ["order_id", "customer_id"]
            ],
            hovertemplate=(
                "<b>Date: %{x|%Y-%m-%d}</b><br>"
                "Order Amount: $%{y:,.2f}<br>"
                "Order ID: %{customdata[0]}<br>"
                "Customer ID: %{customdata[1]}"
                "<extra></extra>"
            ),
            marker=dict(size=10)
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

    st.plotly_chart(
        fig,
        width="stretch"
    )

    with st.expander("About This Chart"):

        st.write(
            """
This chart displays individual customer orders over time.

Hover over a point to see:

- Order ID
- Customer ID
- Order Amount
- Order Date

Use the range slider and zoom controls to explore specific periods.
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
    # Sidebar Filter
    # -----------------------------------------------------

    st.sidebar.header("Filters")

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

    filtered_df = df[
        df["amount"] >= amount_range
    ].copy()

    # -----------------------------------------------------
    # Summary
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
    # Data Table
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
    # Expander
    # -----------------------------------------------------

    with st.expander("Dataset Information"):

        st.write("""
**Dataset Columns**

- **order_id** → Unique order identifier
- **customer_id** → Customer identifier
- **order_date** → Date when the order was placed
- **amount** → Order value in USD

Use the sidebar filter to display only orders above a selected amount.
""")

    st.divider()

    st.header("Download")

    csv = filtered_df.to_csv(index=False)

    st.download_button(
        label="📥 Download Filtered Orders",
        data=csv,
        file_name="filtered_orders.csv",
        mime="text/csv"
    )


