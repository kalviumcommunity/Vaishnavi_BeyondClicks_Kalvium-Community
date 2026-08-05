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


# =========================================================
# TITLE
# =========================================================

st.title("📊 BeyondClicks Analytics Dashboard")

st.caption(
    "Business Performance Summary & Interactive Analytics"
)


# =========================================================
# KPI CALCULATIONS
# =========================================================

kpis, current_year, current_month, previous_year, previous_month = calculate_kpis(df)


# =========================================================
# KPI PERIOD
# =========================================================

st.write(
    f"**Current Period:** {current_year}-{current_month:02d}  |  "
    f"**Previous Period:** {previous_year}-{previous_month:02d}"
)


# =========================================================
# KPI CARDS
# =========================================================

st.subheader("Key Performance Indicators")

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


# =========================================================
# INTERACTIVE ANALYTICS
# =========================================================

st.header("Interactive Analytics")

st.write(
    "Explore order performance using interactive Plotly "
    "visualisations."
)


# =========================================================
# SIDEBAR FILTER
# =========================================================

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


# Filter data

filtered_df = df[
    df["amount"] >= amount_range
].copy()


# =========================================================
# SUMMARY METRICS FOR FILTERED DATA
# =========================================================

col1, col2, col3 = st.columns(3)

with col1:

    total_revenue = filtered_df["amount"].sum()

    st.metric(
        "Filtered Revenue",
        f"${total_revenue:,.2f}"
    )


with col2:

    total_orders = len(filtered_df)

    st.metric(
        "Filtered Orders",
        f"{total_orders:,}"
    )


with col3:

    average_order = filtered_df["amount"].mean()

    st.metric(
        "Average Order Value",
        f"${average_order:,.2f}"
    )


# =========================================================
# PLOTLY CHART
# =========================================================

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


# =========================================================
# DATE RANGE SELECTOR + RANGE SLIDER
# =========================================================

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


# =========================================================
# DISPLAY PLOTLY CHART
# =========================================================

st.plotly_chart(
    fig,
    width="stretch"
)


# =========================================================
# FILTER INFORMATION
# =========================================================

st.subheader("Filtered Orders")

st.write(
    f"Showing {len(filtered_df)} orders "
    f"with amount ≥ ${amount_range:,.2f}"
)


# =========================================================
# DATA TABLE
# =========================================================

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


# =========================================================
# KPI TABLE
# =========================================================

st.divider()

st.subheader("KPI Details")

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