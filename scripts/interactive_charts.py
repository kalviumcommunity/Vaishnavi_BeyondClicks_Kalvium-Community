import os
import pandas as pd
import plotly.graph_objects as go


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

OUTPUT_DIR = "interactive_charts"
DATA_FILE = "data/raw/orders.csv"

os.makedirs(OUTPUT_DIR, exist_ok=True)


# ---------------------------------------------------------
# Load BeyondClicks order data
# ---------------------------------------------------------

df = pd.read_csv(DATA_FILE)

df["order_date"] = pd.to_datetime(df["order_date"])

print("Loaded columns:")
print(df.columns.tolist())

print("\nFirst rows:")
print(df.head())


# ---------------------------------------------------------
# Prepare daily revenue data
# ---------------------------------------------------------

daily_revenue = (
    df.groupby("order_date")
    .agg(
        revenue=("amount", "sum"),
        order_count=("order_id", "count")
    )
    .reset_index()
    .sort_values("order_date")
)


# =========================================================
# TASK 1 — CHART 1
# Revenue Trend with Custom Hover Tooltip
# =========================================================

fig1 = go.Figure()

fig1.add_trace(
    go.Scatter(
        x=daily_revenue["order_date"],
        y=daily_revenue["revenue"],
        mode="lines+markers",
        name="Revenue",
        customdata=daily_revenue["order_count"],
        hovertemplate=(
            "<b>Date: %{x|%Y-%m-%d}</b><br>"
            "Revenue: $%{y:,.2f}<br>"
            "Orders: %{customdata:,}"
            "<extra></extra>"
        ),
        line=dict(width=2),
        marker=dict(size=8)
    )
)

fig1.update_layout(
    title="Daily Revenue Trend",
    xaxis_title="Date",
    yaxis_title="Revenue ($)",
    hovermode="x unified",
    height=550
)

fig1.update_xaxes(
    rangeslider=dict(visible=True),
    rangeselector=dict(
        buttons=[
            dict(count=1, label="1M", step="month", stepmode="backward"),
            dict(count=3, label="3M", step="month", stepmode="backward"),
            dict(count=6, label="6M", step="month", stepmode="backward"),
            dict(step="all", label="All")
        ]
    )
)

fig1.write_html(
    os.path.join(
        OUTPUT_DIR,
        "chart1_revenue_trend.html"
    )
)


# =========================================================
# TASK 1 — CHART 2
# Order Performance with Multi-Column Hover
# =========================================================

product_performance = (
    df.groupby("customer_id")
    .agg(
        revenue=("amount", "sum"),
        order_count=("order_id", "count"),
        average_order_value=("amount", "mean")
    )
    .reset_index()
)

fig2 = go.Figure()

fig2.add_trace(
    go.Bar(
        x=product_performance["customer_id"].astype(str),
        y=product_performance["revenue"],
        name="Revenue",
        customdata=product_performance[
            ["order_count", "average_order_value"]
        ],
        hovertemplate=(
            "<b>Customer: %{x}</b><br>"
            "Revenue: $%{y:,.2f}<br>"
            "Order Count: %{customdata[0]:,}<br>"
            "Average Order Value: $%{customdata[1]:,.2f}"
            "<extra></extra>"
        )
    )
)

fig2.update_layout(
    title="Customer Revenue Performance",
    xaxis_title="Customer ID",
    yaxis_title="Revenue ($)",
    height=550
)

fig2.write_html(
    os.path.join(
        OUTPUT_DIR,
        "chart2_product_performance.html"
    )
)


print("\nTask 1 completed!")
print("Created:")
print("- interactive_charts/chart1_revenue_trend.html")
print("- interactive_charts/chart2_product_performance.html")

# =========================================================
# TASK 2 — DROPDOWN FILTER
# =========================================================

customer_metrics = (
    df.groupby("customer_id")
    .agg(
        revenue=("amount", "sum"),
        order_count=("order_id", "count"),
        average_order_value=("amount", "mean")
    )
    .reset_index()
)

customers = customer_metrics["customer_id"].astype(str).tolist()

fig3 = go.Figure()

# Revenue
fig3.add_trace(
    go.Bar(
        x=customers,
        y=customer_metrics["revenue"],
        name="Revenue",
        marker=dict(color="#1f77b4"),
        visible=True,
        hovertemplate=(
            "<b>Customer: %{x}</b><br>"
            "Revenue: $%{y:,.2f}"
            "<extra></extra>"
        )
    )
)

# Order Count
fig3.add_trace(
    go.Bar(
        x=customers,
        y=customer_metrics["order_count"],
        name="Order Count",
        marker=dict(color="#ff7f0e"),
        visible=False,
        hovertemplate=(
            "<b>Customer: %{x}</b><br>"
            "Orders: %{y:,}"
            "<extra></extra>"
        )
    )
)

# Average Order Value
fig3.add_trace(
    go.Bar(
        x=customers,
        y=customer_metrics["average_order_value"],
        name="Average Order Value",
        marker=dict(color="#2ca02c"),
        visible=False,
        hovertemplate=(
            "<b>Customer: %{x}</b><br>"
            "Average Order Value: $%{y:,.2f}"
            "<extra></extra>"
        )
    )
)


# Dropdown menu
fig3.update_layout(
    title="Customer Performance — Revenue",
    xaxis_title="Customer ID",
    yaxis_title="Revenue ($)",
    height=550,

    updatemenus=[
        dict(
            active=0,
            x=0.0,
            y=1.15,
            xanchor="left",
            yanchor="top",

            buttons=[
                dict(
                    label="Revenue",
                    method="update",
                    args=[
                        {"visible": [True, False, False]},
                        {
                            "title": "Customer Performance — Revenue",
                            "yaxis": {
                                "title": "Revenue ($)"
                            }
                        }
                    ]
                ),

                dict(
                    label="Order Count",
                    method="update",
                    args=[
                        {"visible": [False, True, False]},
                        {
                            "title": "Customer Performance — Order Count",
                            "yaxis": {
                                "title": "Number of Orders"
                            }
                        }
                    ]
                ),

                dict(
                    label="Average Order Value",
                    method="update",
                    args=[
                        {"visible": [False, False, True]},
                        {
                            "title": "Customer Performance — Average Order Value",
                            "yaxis": {
                                "title": "Average Order Value ($)"
                            }
                        }
                    ]
                )
            ]
        )
    ]
)

fig3.write_html(
    os.path.join(
        OUTPUT_DIR,
        "chart3_metric_selector.html"
    )
)

print("- interactive_charts/chart3_metric_selector.html")

# =========================================================
# TASK 3 — ZOOM, PAN, RESET & SELECTION
# =========================================================

fig4 = go.Figure()

fig4.add_trace(
    go.Scatter(
        x=df["order_date"],
        y=df["amount"],
        mode="markers",
        name="Orders",
        customdata=df["order_id"],
        marker=dict(size=10),
        hovertemplate=(
            "<b>Date: %{x|%Y-%m-%d}</b><br>"
            "Order Amount: $%{y:,.2f}<br>"
            "Order ID: %{customdata}"
            "<extra></extra>"
        )
    )
)

fig4.update_layout(
    title="Order Amount Over Time — Interactive Exploration",
    xaxis_title="Order Date",
    yaxis_title="Order Amount ($)",
    height=600,

    # Initial interaction mode
    dragmode="zoom",

    # Show closest point on hover
    hovermode="closest",

    # Enable selection tools in the Plotly toolbar
    selectdirection="any"
)

fig4.write_html(
    os.path.join(
        OUTPUT_DIR,
        "chart4_interactive.html"
    ),
    config={
        "displayModeBar": True,
        "displaylogo": False,
        "modeBarButtonsToAdd": [
            "select2d",
            "lasso2d"
        ]
    }
)

print("- interactive_charts/chart4_interactive.html")
