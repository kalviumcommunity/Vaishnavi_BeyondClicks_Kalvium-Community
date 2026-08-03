import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="BeyondClicks - Campaign Dashboard",
    page_icon="📊",
    layout="wide"
)

# ============================================================
# LOAD DATA
# ============================================================

DATA_FILE = "data/processed/feature_engineered_campaign_data.csv"

df = pd.read_csv(DATA_FILE)

df["Date"] = pd.to_datetime(df["Date"])

# ============================================================
# TITLE
# ============================================================

st.title("BeyondClicks - Marketing Campaign Performance Dashboard")
st.caption("Campaign performance, engagement, activation and revenue analysis")

# ============================================================
# SIDEBAR FILTERS
# ============================================================

st.sidebar.header("Dashboard Filters")

# Customer Segment
segments = ["All"] + sorted(df["Customer_Segment"].dropna().unique().tolist())
selected_segment = st.sidebar.selectbox(
    "Customer Segment",
    segments
)

# Campaign Type
campaign_types = ["All"] + sorted(df["Campaign_Type"].dropna().unique().tolist())
selected_campaign = st.sidebar.selectbox(
    "Campaign Type",
    campaign_types
)

# Platform
platforms = ["All"] + sorted(df["Platform"].dropna().unique().tolist())
selected_platform = st.sidebar.selectbox(
    "Platform",
    platforms
)

# Date range
min_date = df["Date"].min().date()
max_date = df["Date"].max().date()

selected_dates = st.sidebar.date_input(
    "Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

# ============================================================
# APPLY FILTERS
# ============================================================

filtered_df = df.copy()

if selected_segment != "All":
    filtered_df = filtered_df[
        filtered_df["Customer_Segment"] == selected_segment
    ]

if selected_campaign != "All":
    filtered_df = filtered_df[
        filtered_df["Campaign_Type"] == selected_campaign
    ]

if selected_platform != "All":
    filtered_df = filtered_df[
        filtered_df["Platform"] == selected_platform
    ]

if len(selected_dates) == 2:
    start_date, end_date = selected_dates

    filtered_df = filtered_df[
        (filtered_df["Date"].dt.date >= start_date)
        & (filtered_df["Date"].dt.date <= end_date)
    ]

# ============================================================
# LEVEL 1 - KPI SUMMARY
# ============================================================

st.header("Level 1 - Campaign Status")

total_revenue = filtered_df["Revenue"].sum()
activated_users = filtered_df["Activated_Users"].sum()
avg_ctr = filtered_df["CTR"].mean()
avg_activation = filtered_df["Activation_Rate"].mean()
avg_roi = filtered_df["ROI"].mean()

# Compare with previous period
previous_df = df.copy()

if len(selected_dates) == 2:

    start_date, end_date = selected_dates

    period_days = (end_date - start_date).days + 1

    previous_start = start_date - pd.Timedelta(days=period_days)
    previous_end = start_date - pd.Timedelta(days=1)

    previous_df = previous_df[
        (previous_df["Date"].dt.date >= previous_start)
        & (previous_df["Date"].dt.date <= previous_end)
    ]

# Calculate previous values
previous_revenue = previous_df["Revenue"].sum()
previous_activated = previous_df["Activated_Users"].sum()
previous_ctr = previous_df["CTR"].mean()
previous_activation = previous_df["Activation_Rate"].mean()
previous_roi = previous_df["ROI"].mean()


def percentage_change(current, previous):
    if previous == 0:
        return 0
    return ((current - previous) / previous) * 100


revenue_change = percentage_change(
    total_revenue,
    previous_revenue
)

activated_change = percentage_change(
    activated_users,
    previous_activated
)

ctr_change = percentage_change(
    avg_ctr,
    previous_ctr
)

activation_change = percentage_change(
    avg_activation,
    previous_activation
)

roi_change = percentage_change(
    avg_roi,
    previous_roi
)

# KPI cards
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric(
        "Total Revenue",
        f"${total_revenue:,.0f}",
        f"{revenue_change:+.2f}%"
    )

with col2:
    st.metric(
        "Activated Users",
        f"{activated_users:,.0f}",
        f"{activated_change:+.2f}%"
    )

with col3:
    st.metric(
        "Average CTR",
        f"{avg_ctr:.2f}%",
        f"{ctr_change:+.2f}%"
    )

with col4:
    st.metric(
        "Activation Rate",
        f"{avg_activation:.2f}%",
        f"{activation_change:+.2f}%"
    )

with col5:
    st.metric(
        "Average ROI",
        f"{avg_roi:.2f}",
        f"{roi_change:+.2f}%"
    )

st.divider()

# ============================================================
# LEVEL 2 - TRENDS
# ============================================================

st.header("Level 2 - Performance Trends")

filtered_df["Month"] = filtered_df["Date"].dt.to_period("M").astype(str)

monthly = (
    filtered_df
    .groupby("Month")
    .agg(
        Revenue=("Revenue", "sum"),
        CTR=("CTR", "mean"),
        Activation_Rate=("Activation_Rate", "mean")
    )
    .reset_index()
)

# ------------------------------------------------------------
# Chart 1 - Revenue Trend
# ------------------------------------------------------------

st.subheader("Monthly Revenue Trend")

fig1, ax1 = plt.subplots(figsize=(12, 4))

ax1.plot(
    monthly["Month"],
    monthly["Revenue"],
    marker="o"
)

ax1.set_title("Monthly Revenue Trend")
ax1.set_xlabel("Month")
ax1.set_ylabel("Revenue ($)")
ax1.tick_params(axis="x", rotation=45)
ax1.grid(True, alpha=0.3)

st.pyplot(fig1)

# ------------------------------------------------------------
# Chart 2 - CTR Trend
# ------------------------------------------------------------

st.subheader("Monthly Click-Through Rate Trend")

fig2, ax2 = plt.subplots(figsize=(12, 4))

ax2.plot(
    monthly["Month"],
    monthly["CTR"],
    marker="o"
)

ax2.set_title("Monthly CTR Trend")
ax2.set_xlabel("Month")
ax2.set_ylabel("CTR (%)")
ax2.tick_params(axis="x", rotation=45)
ax2.grid(True, alpha=0.3)

st.pyplot(fig2)

# ------------------------------------------------------------
# Chart 3 - Activation Rate Trend
# ------------------------------------------------------------

st.subheader("Monthly Activation Rate Trend")

fig3, ax3 = plt.subplots(figsize=(12, 4))

ax3.plot(
    monthly["Month"],
    monthly["Activation_Rate"],
    marker="o"
)

ax3.set_title("Monthly Activation Rate Trend")
ax3.set_xlabel("Month")
ax3.set_ylabel("Activation Rate (%)")
ax3.tick_params(axis="x", rotation=45)
ax3.grid(True, alpha=0.3)

st.pyplot(fig3)

st.divider()

# ============================================================
# LEVEL 3 - SEGMENT ANALYSIS
# ============================================================

st.header("Level 3 - Segment Performance")

col1, col2 = st.columns(2)

# ------------------------------------------------------------
# Revenue by Customer Segment
# ------------------------------------------------------------

segment_revenue = (
    filtered_df
    .groupby("Customer_Segment")["Revenue"]
    .sum()
    .sort_values(ascending=True)
)

with col1:

    st.subheader("Revenue by Customer Segment")

    fig4, ax4 = plt.subplots(figsize=(8, 5))

    ax4.barh(
        segment_revenue.index,
        segment_revenue.values
    )

    ax4.set_xlabel("Revenue ($)")
    ax4.set_ylabel("Customer Segment")
    ax4.set_title("Revenue by Customer Segment")

    for i, value in enumerate(segment_revenue.values):
        ax4.text(
            value,
            i,
            f" ${value:,.0f}",
            va="center"
        )

    st.pyplot(fig4)

# ------------------------------------------------------------
# ROI by Campaign Type
# ------------------------------------------------------------

campaign_roi = (
    filtered_df
    .groupby("Campaign_Type")["ROI"]
    .mean()
    .sort_values(ascending=True)
)

with col2:

    st.subheader("Average ROI by Campaign Type")

    fig5, ax5 = plt.subplots(figsize=(8, 5))

    ax5.barh(
        campaign_roi.index,
        campaign_roi.values
    )

    ax5.set_xlabel("Average ROI")
    ax5.set_ylabel("Campaign Type")
    ax5.set_title("Average ROI by Campaign Type")

    for i, value in enumerate(campaign_roi.values):
        ax5.text(
            value,
            i,
            f" {value:.2f}",
            va="center"
        )

    st.pyplot(fig5)

st.divider()

# ============================================================
# LEVEL 4 - DETAIL / PROGRESSIVE DISCLOSURE
# ============================================================

st.header("Level 4 - Detailed Campaign Explorer")

st.write(
    f"Showing **{len(filtered_df):,}** campaign records "
    "based on the selected filters."
)

display_columns = [
    "Campaign_ID",
    "Campaign_Type",
    "Target_Audience",
    "Platform",
    "Impressions",
    "Clicks",
    "Signups",
    "Activated_Users",
    "Revenue",
    "ROI",
    "Customer_Segment",
    "Date",
    "CTR",
    "Signup_Rate",
    "Activation_Rate"
]

st.dataframe(
    filtered_df[display_columns],
    use_container_width=True
)

# ============================================================
# DOWNLOAD
# ============================================================

csv_data = filtered_df.to_csv(index=False)

st.download_button(
    label="Download Filtered Campaign Data",
    data=csv_data,
    file_name="filtered_campaign_data.csv",
    mime="text/csv"
)

# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "BeyondClicks | Marketing Campaign Activation Analytics Dashboard"
)