import streamlit as st
import pandas as pd
import plotly.graph_objects as go


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="BeyondClicks Interactive Analytics",
    page_icon="📊",
    layout="wide"
)


# =========================================================
# LOAD DATA
# =========================================================

DATA_FILE = "data/raw/orders.csv"

df = pd.read_csv(DATA_FILE)

df["order_date"] = pd.to_datetime(df["order_date"])


# =========================================================
# TITLE
# =========================================================

st.title("BeyondClicks — Interactive Analytics Dashboard")

st.write(
    "Explore order performance using interactive Plotly "
    "visualisations."
)


# =========================================================
# SIDEBAR FILTERS
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

filtered_df = df[
    df["amount"] >= amount_range
].copy()


# =========================================================
# SUMMARY
# =========================================================

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Total Revenue",
        f"${filtered_df['amount'].sum():,.2f}"
    )

with col2:
    st.metric(
        "Total Orders",
        f"{len(filtered_df):,}"
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
    rangeslider=dict(visible=True)
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