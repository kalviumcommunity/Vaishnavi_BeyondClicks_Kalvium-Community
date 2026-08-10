import os
import sys
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from pathlib import Path

# Ensure UTF-8 output encoding for Windows compatibility
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Page Configuration
st.set_page_config(
    page_title="BeyondClicks • Marketing Activation Analytics Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Vibrant, Premium Executive CSS Styling
st.markdown(
    """
    <style>
    /* Global Page Container */
    .block-container {
        padding-top: 2.6rem;
        padding-bottom: 2.5rem;
        max-width: 96%;
    }
    
    /* Vibrant Gradient Brand Header */
    .brand-title {
        font-size: 2.2rem !important;
        font-weight: 800 !important;
        background: linear-gradient(135deg, #38bdf8 0%, #818cf8 50%, #c084fc 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0px !important;
    }
    
    .brand-subtitle {
        color: #94a3b8 !important;
        font-size: 0.95rem !important;
        margin-top: -4px !important;
        margin-bottom: 20px !important;
    }
    
    /* Custom KPI Cards with Vibrant Accent Top Border */
    .kpi-card {
        background-color: rgba(30, 41, 59, 0.45);
        border: 1px solid rgba(148, 163, 184, 0.18);
        border-radius: 12px;
        padding: 16px 18px;
        margin-bottom: 12px;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.15);
        backdrop-filter: blur(10px);
        position: relative;
        overflow: hidden;
    }
    
    .kpi-card-1 { border-top: 4px solid #38bdf8; }
    .kpi-card-2 { border-top: 4px solid #10b981; }
    .kpi-card-3 { border-top: 4px solid #818cf8; }
    .kpi-card-4 { border-top: 4px solid #f59e0b; }
    .kpi-card-5 { border-top: 4px solid #c084fc; }
    .kpi-card-6 { border-top: 4px solid #f43f5e; }

    .kpi-title {
        font-size: 0.8rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: #cbd5e1;
        margin-bottom: 4px;
    }
    .kpi-value {
        font-size: 1.75rem;
        font-weight: 800;
        line-height: 1.2;
        color: #f8fafc;
    }
    .kpi-delta-positive {
        font-size: 0.85rem;
        font-weight: 600;
        color: #34d399;
        margin-top: 6px;
    }
    .kpi-delta-negative {
        font-size: 0.85rem;
        font-weight: 600;
        color: #fb7185;
        margin-top: 6px;
    }
    .kpi-subtitle {
        font-size: 0.78rem;
        color: #94a3b8;
        margin-top: 2px;
    }

    /* Streamlit Tab Custom Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        border-bottom: 2px solid rgba(148, 163, 184, 0.2);
    }
    .stTabs [data-baseweb="tab"] {
        height: 46px;
        padding-left: 20px;
        padding-right: 20px;
        font-size: 0.95rem;
        font-weight: 600;
        border-radius: 8px 8px 0 0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "data/processed/feature_engineered_campaign_data.csv"

# Global Vibrant Palette
COLOR_PRIMARY = "#38bdf8"
COLOR_SUCCESS = "#10b981"
COLOR_WARNING = "#f59e0b"
COLOR_DANGER = "#f43f5e"
COLOR_INDIGO = "#818cf8"
COLOR_PURPLE = "#c084fc"

VIBRANT_PALETTE = ["#38bdf8", "#10b981", "#818cf8", "#f59e0b", "#c084fc", "#f43f5e", "#fb7185"]


@st.cache_data(show_spinner=False)
def load_campaign_data(filepath: Path) -> pd.DataFrame:
    """Loads and sanitizes marketing campaign performance data."""
    if not filepath.exists():
        return pd.DataFrame()

    df = pd.read_csv(filepath)
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df = df.dropna(subset=["Date"]).copy()

    if "Platform" in df.columns:
        df["Primary_Platform"] = df["Platform"].astype(str).apply(lambda x: x.split(",")[0].strip())
    else:
        df["Primary_Platform"] = "Unknown"

    numeric_columns = [
        "Impressions",
        "Clicks",
        "Signups",
        "Activated_Users",
        "Revenue",
        "Acquisition_Cost",
        "ROI",
        "CTR",
        "Signup_Rate",
        "Activation_Rate",
        "Click_to_Activation_Rate",
        "Revenue_per_Activated_User",
        "Cost_per_Activated_User",
        "Cost_per_Signup",
    ]

    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)

    if "CTR" not in df.columns and "Impressions" in df.columns and "Clicks" in df.columns:
        df["CTR"] = np.where(df["Impressions"] > 0, (df["Clicks"] / df["Impressions"]) * 100, 0.0)

    if "Signup_Rate" not in df.columns and "Clicks" in df.columns and "Signups" in df.columns:
        df["Signup_Rate"] = np.where(df["Clicks"] > 0, (df["Signups"] / df["Clicks"]) * 100, 0.0)

    if "Activation_Rate" not in df.columns and "Signups" in df.columns and "Activated_Users" in df.columns:
        df["Activation_Rate"] = np.where(df["Signups"] > 0, (df["Activated_Users"] / df["Signups"]) * 100, 0.0)

    if "Cost_per_Activated_User" not in df.columns and "Activated_Users" in df.columns and "Acquisition_Cost" in df.columns:
        df["Cost_per_Activated_User"] = np.where(df["Activated_Users"] > 0, df["Acquisition_Cost"] / df["Activated_Users"], 0.0)

    return df


def calculate_period_change(current_val: float, previous_val: float) -> float:
    """Calculates percentage change between periods."""
    if pd.isna(previous_val) or previous_val == 0:
        return 0.0
    return ((current_val - previous_val) / previous_val) * 100


def build_comparison_period(df: pd.DataFrame, start_date: pd.Timestamp, end_date: pd.Timestamp) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Splits data into current period and equal-length previous period."""
    period_days = max(1, (end_date - start_date).days + 1)
    previous_end = start_date - pd.Timedelta(days=1)
    previous_start = previous_end - pd.Timedelta(days=period_days - 1)

    current_df = df[(df["Date"] >= start_date) & (df["Date"] <= end_date)].copy()
    previous_df = df[(df["Date"] >= previous_start) & (df["Date"] <= previous_end)].copy()

    return current_df, previous_df


def render_custom_kpi(title: str, value: str, delta_pct: float, subtitle: str = "", card_idx: int = 1):
    """Renders a visually clean, colorful metric card."""
    delta_class = "kpi-delta-positive" if delta_pct >= 0 else "kpi-delta-negative"
    delta_symbol = "▲" if delta_pct >= 0 else "▼"
    delta_str = f"{delta_symbol} {abs(delta_pct):.1f}% vs prior period" if delta_pct != 0.0 else "• Stable"

    st.markdown(
        f"""
        <div class="kpi-card kpi-card-{card_idx}">
            <div class="kpi-title">{title}</div>
            <div class="kpi-value">{value}</div>
            <div class="{delta_class}">{delta_str}</div>
            <div class="kpi-subtitle">{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def apply_chart_theme(fig, height: int = 350, show_coloraxis: bool = False):
    """Applies a clean, non-overlapping layout to Plotly figures."""
    fig.update_layout(
        margin=dict(l=15, r=15, t=15, b=30),
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        coloraxis_showscale=show_coloraxis,
        hoverlabel=dict(bgcolor="#1e293b", font_color="#f8fafc", font_size=12),
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.18,
            xanchor="center",
            x=0.5
        )
    )
    fig.update_xaxes(showgrid=True, gridcolor="rgba(148, 163, 184, 0.12)", zeroline=False)
    fig.update_yaxes(showgrid=True, gridcolor="rgba(148, 163, 184, 0.12)", zeroline=False)
    return fig


def main() -> None:
    # Sidebar Setup
    st.sidebar.title("BeyondClicks")
    st.sidebar.caption("Marketing Activation Analytics")
    st.sidebar.divider()

    uploaded_file = st.sidebar.file_uploader("Upload Campaign Data (Optional CSV)", type=["csv"], key="user_file")

    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
            df = df.dropna(subset=["Date"]).copy()
            if "Platform" in df.columns:
                df["Primary_Platform"] = df["Platform"].astype(str).apply(lambda x: x.split(",")[0].strip())
            else:
                df["Primary_Platform"] = "Unknown"
            st.sidebar.success(f"Loaded: {uploaded_file.name}")
        except Exception as e:
            st.sidebar.error(f"Error reading CSV: {e}")
            df = load_campaign_data(DATA_PATH)
    else:
        df = load_campaign_data(DATA_PATH)

    if df.empty:
        st.error("Campaign dataset could not be loaded. Please ensure data file exists or upload a valid CSV.")
        st.stop()

    st.sidebar.subheader("Filter Controls")

    # Date Range Filter
    min_date = df["Date"].min().date()
    max_date = df["Date"].max().date()

    if "sel_dates" not in st.session_state:
        st.session_state["sel_dates"] = (min_date, max_date)

    selected_dates = st.sidebar.date_input(
        "Date Range",
        value=st.session_state["sel_dates"],
        min_value=min_date,
        max_value=max_date,
        key="sel_dates",
    )

    if isinstance(selected_dates, tuple) and len(selected_dates) == 2:
        start_date, end_date = selected_dates
    elif isinstance(selected_dates, tuple) and len(selected_dates) == 1:
        start_date = selected_dates[0]
        end_date = selected_dates[0]
    else:
        start_date = selected_dates
        end_date = selected_dates

    start_dt = pd.Timestamp(start_date)
    end_dt = pd.Timestamp(end_date)

    # Clean Selectbox Controls
    segment_options = ["All Segments"] + sorted(df["Customer_Segment"].dropna().astype(str).unique().tolist()) if "Customer_Segment" in df.columns else ["All Segments"]
    campaign_options = ["All Campaign Types"] + sorted(df["Campaign_Type"].dropna().astype(str).unique().tolist()) if "Campaign_Type" in df.columns else ["All Campaign Types"]
    platform_options = ["All Platforms"] + sorted(df["Primary_Platform"].dropna().astype(str).unique().tolist()) if "Primary_Platform" in df.columns else ["All Platforms"]

    selected_segment = st.sidebar.selectbox("Customer Segment", segment_options, key="sel_segment")
    selected_campaign = st.sidebar.selectbox("Campaign Type", campaign_options, key="sel_campaign")
    selected_platform = st.sidebar.selectbox("Platform / Channel", platform_options, key="sel_platform")

    # Robust Reset Button Implementation using on_click callback
    st.sidebar.markdown("<br>", unsafe_allow_html=True)

    def _reset_all_filters():
        # Update defaults in session_state via callback (safe API)
        st.session_state["sel_dates"] = (min_date, max_date)
        st.session_state["sel_segment"] = "All Segments"
        st.session_state["sel_campaign"] = "All Campaign Types"
        st.session_state["sel_platform"] = "All Platforms"

    st.sidebar.button("🔄 Reset All Filters", use_container_width=True, on_click=_reset_all_filters)

    # Apply Filters
    filtered_df = df[
        (df["Date"] >= start_dt) & (df["Date"] <= end_dt)
    ].copy()

    if selected_segment != "All Segments":
        filtered_df = filtered_df[filtered_df["Customer_Segment"] == selected_segment]

    if selected_campaign != "All Campaign Types":
        filtered_df = filtered_df[filtered_df["Campaign_Type"] == selected_campaign]

    if selected_platform != "All Platforms":
        filtered_df = filtered_df[filtered_df["Primary_Platform"] == selected_platform]

    if filtered_df.empty:
        st.warning("No data matches the current filters. Please adjust date range or selection criteria.")
        st.stop()

    # Period Comparison calculation
    current_df, previous_df = build_comparison_period(df, start_dt, end_dt)
    if selected_segment != "All Segments":
        current_df = current_df[current_df["Customer_Segment"] == selected_segment]
        previous_df = previous_df[previous_df["Customer_Segment"] == selected_segment]
    if selected_campaign != "All Campaign Types":
        current_df = current_df[current_df["Campaign_Type"] == selected_campaign]
        previous_df = previous_df[previous_df["Campaign_Type"] == selected_campaign]
    if selected_platform != "All Platforms":
        current_df = current_df[current_df["Primary_Platform"] == selected_platform]
        previous_df = previous_df[previous_df["Primary_Platform"] == selected_platform]

    # Core Metrics
    total_revenue = float(filtered_df["Revenue"].sum())
    previous_revenue = float(previous_df["Revenue"].sum()) if not previous_df.empty else 0.0

    total_activated = float(filtered_df["Activated_Users"].sum())
    previous_activated = float(previous_df["Activated_Users"].sum()) if not previous_df.empty else 0.0

    avg_activation_rate = float(filtered_df["Activation_Rate"].mean())
    prev_activation_rate = float(previous_df["Activation_Rate"].mean()) if not previous_df.empty else 0.0

    avg_ctr = float(filtered_df["CTR"].mean())
    prev_ctr = float(previous_df["CTR"].mean()) if not previous_df.empty else 0.0

    avg_roi = float(filtered_df["ROI"].mean())
    prev_roi = float(previous_df["ROI"].mean()) if not previous_df.empty else 0.0

    total_cost = float(filtered_df["Acquisition_Cost"].sum()) if "Acquisition_Cost" in filtered_df.columns else 0.0
    cost_per_activated = (total_cost / total_activated) if total_activated > 0 else 0.0
    prev_cost_per_act = (float(previous_df["Acquisition_Cost"].sum()) / previous_activated) if previous_activated > 0 else 0.0

    # Header Title
    st.markdown('<p class="brand-title">BeyondClicks • Marketing Activation Analytics</p>', unsafe_allow_html=True)
    st.markdown('<p class="brand-subtitle">Centralizing campaign analytics to optimize downstream user activation quality over vanity traffic.</p>', unsafe_allow_html=True)

    # Top Level Status KPI Grid with Accent Borders
    kpi_col1, kpi_col2, kpi_col3, kpi_col4, kpi_col5, kpi_col6 = st.columns(6)

    with kpi_col1:
        render_custom_kpi("Total Revenue", f"${total_revenue:,.0f}", calculate_period_change(total_revenue, previous_revenue), "Net customer revenue", 1)
    with kpi_col2:
        render_custom_kpi("Activated Users", f"{int(total_activated):,}", calculate_period_change(total_activated, previous_activated), "Quality converted users", 2)
    with kpi_col3:
        render_custom_kpi("Activation Rate", f"{avg_activation_rate:.1f}%", calculate_period_change(avg_activation_rate, prev_activation_rate), "Signup to Activation", 3)
    with kpi_col4:
        render_custom_kpi("Average CTR", f"{avg_ctr:.2f}%", calculate_period_change(avg_ctr, prev_ctr), "Click-through rate", 4)
    with kpi_col5:
        render_custom_kpi("Average ROI", f"{avg_roi:.2f}x", calculate_period_change(avg_roi, prev_roi), "Return on ad spend", 5)
    with kpi_col6:
        render_custom_kpi("Cost / Activated", f"${cost_per_activated:,.2f}", calculate_period_change(cost_per_activated, prev_cost_per_act), "Cost per active user", 6)

    st.markdown("<br>", unsafe_allow_html=True)

    # Executive Guidance Alert
    rev_per_act = total_revenue / total_activated if total_activated > 0 else 0.0
    if avg_activation_rate >= 55.0:
        st.success(f"🟢 **High Activation Quality**: Filtered campaigns convert **{avg_activation_rate:.1f}%** of signups into active customers, generating **${rev_per_act:,.2f}** revenue per activated user.")
    elif avg_activation_rate >= 40.0:
        st.info(f"🔵 **Moderate Activation**: Campaign performance is balanced (**{avg_activation_rate:.1f}%** activation rate). Reallocating spend from weak platforms to top performers will boost ROI.")
    else:
        st.warning(f"⚠️ **Vanity Traffic Risk**: Activation rate is low (**{avg_activation_rate:.1f}%**). High clicks are failing to convert downstream. Review campaign targeting.")

    # Multi-Tab Organization
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Executive Overview & Trends",
        "🚀 Platform & Channel Analytics",
        "👥 Audience & Segment Insights",
        "🔻 Conversion Funnel & Anomalies",
        "🔎 Campaign Explorer & Export"
    ])

    # ------------------------------------------------------------------
    # TAB 1: EXECUTIVE OVERVIEW & TRENDS
    # ------------------------------------------------------------------
    with tab1:
        st.markdown("### Executive Overview & Historical Trends")

        filtered_df["YearMonth"] = filtered_df["Date"].dt.to_period("M").astype(str)
        monthly_summary = filtered_df.groupby("YearMonth", as_index=False).agg(
            Revenue=("Revenue", "sum"),
            Activated_Users=("Activated_Users", "sum"),
            Activation_Rate=("Activation_Rate", "mean"),
            CTR=("CTR", "mean"),
            Acquisition_Cost=("Acquisition_Cost", "sum")
        )

        trend_c1, trend_c2 = st.columns(2)

        with trend_c1:
            st.subheader("Monthly Revenue vs Acquisition Spend ($)")
            fig_rev_trend = go.Figure()
            fig_rev_trend.add_trace(go.Scatter(
                x=monthly_summary["YearMonth"],
                y=monthly_summary["Revenue"],
                mode="lines+markers",
                name="Revenue ($)",
                line=dict(color=COLOR_PRIMARY, width=3, shape="spline"),
                marker=dict(size=7)
            ))
            fig_rev_trend.add_trace(go.Scatter(
                x=monthly_summary["YearMonth"],
                y=monthly_summary["Acquisition_Cost"],
                mode="lines+markers",
                name="Ad Spend ($)",
                line=dict(color=COLOR_WARNING, width=2, dash="dash", shape="spline"),
                marker=dict(size=6)
            ))
            apply_chart_theme(fig_rev_trend)
            fig_rev_trend.update_xaxes(title_text="Month")
            fig_rev_trend.update_yaxes(title_text="Amount ($)")
            st.plotly_chart(fig_rev_trend, use_container_width=True)

        with trend_c2:
            st.subheader("Activation Rate (%) vs CTR (%)")
            fig_act_trend = go.Figure()
            fig_act_trend.add_trace(go.Scatter(
                x=monthly_summary["YearMonth"],
                y=monthly_summary["Activation_Rate"],
                mode="lines+markers",
                name="Activation Rate (%)",
                line=dict(color=COLOR_SUCCESS, width=3, shape="spline"),
                marker=dict(size=7)
            ))
            fig_act_trend.add_trace(go.Scatter(
                x=monthly_summary["YearMonth"],
                y=monthly_summary["CTR"],
                mode="lines+markers",
                name="Click-Through Rate (%)",
                line=dict(color=COLOR_INDIGO, width=2, shape="spline"),
                marker=dict(size=6)
            ))
            apply_chart_theme(fig_act_trend)
            fig_act_trend.update_xaxes(title_text="Month")
            fig_act_trend.update_yaxes(title_text="Percentage (%)")
            st.plotly_chart(fig_act_trend, use_container_width=True)

        st.divider()

        st.subheader("Activation Quality Leaderboard by Category")
        st.caption("Summarizing activation performance and revenue across primary marketing categories.")

        category_summary = filtered_df.groupby(["Campaign_Type", "Primary_Platform"], as_index=False).agg(
            Revenue=("Revenue", "sum"),
            Activated_Users=("Activated_Users", "sum"),
            Activation_Rate=("Activation_Rate", "mean"),
            CTR=("CTR", "mean"),
            Avg_ROI=("ROI", "mean")
        ).sort_values("Revenue", ascending=False)

        category_summary["Quality_Tier"] = np.where(
            category_summary["Activation_Rate"] >= 55.0, "🟢 High Quality",
            np.where(category_summary["Activation_Rate"] >= 45.0, "🔵 Moderate", "⚠️ Vanity Risk")
        )

        st.dataframe(
            category_summary.rename(columns={
                "Campaign_Type": "Campaign Type",
                "Primary_Platform": "Primary Platform",
                "Activated_Users": "Activated Users",
                "Activation_Rate": "Activation Rate (%)",
                "CTR": "CTR (%)",
                "Avg_ROI": "Avg ROI (x)",
                "Quality_Tier": "Activation Quality"
            }),
            use_container_width=True
        )

    # ------------------------------------------------------------------
    # TAB 2: PLATFORM & CHANNEL PERFORMANCE
    # ------------------------------------------------------------------
    with tab2:
        st.markdown("### Platform & Marketing Channel Performance")

        platform_summary = filtered_df.groupby("Primary_Platform", as_index=False).agg(
            Revenue=("Revenue", "sum"),
            Acquisition_Cost=("Acquisition_Cost", "sum"),
            Activated_Users=("Activated_Users", "sum"),
            Activation_Rate=("Activation_Rate", "mean"),
            Avg_ROI=("ROI", "mean")
        ).sort_values("Revenue", ascending=False)

        platform_summary["Cost_per_Activated"] = np.where(
            platform_summary["Activated_Users"] > 0,
            platform_summary["Acquisition_Cost"] / platform_summary["Activated_Users"],
            0.0
        )

        p_col1, p_col2 = st.columns(2)

        with p_col1:
            st.subheader("Average Activation Rate (%) by Platform")
            fig_plat_act = px.bar(
                platform_summary.sort_values("Activation_Rate", ascending=True),
                x="Activation_Rate",
                y="Primary_Platform",
                orientation="h",
                color="Activation_Rate",
                color_continuous_scale="Tealgrn",
                text_auto=".1f"
            )
            apply_chart_theme(fig_plat_act, show_coloraxis=False)
            fig_plat_act.update_xaxes(title_text="Activation Rate (%)")
            fig_plat_act.update_yaxes(title_text="Platform")
            st.plotly_chart(fig_plat_act, use_container_width=True)

        with p_col2:
            st.subheader("Revenue vs Acquisition Spend by Platform")
            fig_plat_rev = go.Figure()
            fig_plat_rev.add_trace(go.Bar(
                x=platform_summary["Primary_Platform"],
                y=platform_summary["Revenue"],
                name="Revenue Generated ($)",
                marker_color=COLOR_PRIMARY
            ))
            fig_plat_rev.add_trace(go.Bar(
                x=platform_summary["Primary_Platform"],
                y=platform_summary["Acquisition_Cost"],
                name="Acquisition Cost ($)",
                marker_color=COLOR_WARNING
            ))
            apply_chart_theme(fig_plat_rev)
            fig_plat_rev.update_layout(barmode="group")
            fig_plat_rev.update_xaxes(title_text="Platform")
            fig_plat_rev.update_yaxes(title_text="Amount ($)")
            st.plotly_chart(fig_plat_rev, use_container_width=True)

        st.divider()

        st.subheader("Platform Efficiency Benchmark (Cost / Activated vs ROI)")
        fig_plat_eff = px.scatter(
            platform_summary,
            x="Cost_per_Activated",
            y="Avg_ROI",
            size="Revenue",
            color="Primary_Platform",
            text="Primary_Platform",
            size_max=45,
            color_discrete_sequence=VIBRANT_PALETTE,
            labels={"Cost_per_Activated": "Cost per Activated User ($)", "Avg_ROI": "Average Return on Investment (ROI)"}
        )
        fig_plat_eff.update_traces(textposition="top center")
        apply_chart_theme(fig_plat_eff, height=380)
        st.plotly_chart(fig_plat_eff, use_container_width=True)

    # ------------------------------------------------------------------
    # TAB 3: AUDIENCE & SEGMENT INSIGHTS (Fixed Legend/Title Overlap)
    # ------------------------------------------------------------------
    with tab3:
        st.markdown("### Customer Segment & Target Audience Analytics")

        s_col1, s_col2 = st.columns(2)

        with s_col1:
            if "Customer_Segment" in filtered_df.columns:
                st.subheader("Revenue Distribution by Customer Segment")
                seg_summary = filtered_df.groupby("Customer_Segment", as_index=False)["Revenue"].sum().sort_values("Revenue", ascending=False)

                fig_seg_pie = px.pie(
                    seg_summary,
                    names="Customer_Segment",
                    values="Revenue",
                    hole=0.45,
                    color_discrete_sequence=VIBRANT_PALETTE
                )
                fig_seg_pie.update_traces(textinfo="percent+label", hovertemplate="Segment: %{label}<br>Revenue: $%{value:,.0f}")
                apply_chart_theme(fig_seg_pie)
                st.plotly_chart(fig_seg_pie, use_container_width=True)

        with s_col2:
            if "Campaign_Type" in filtered_df.columns:
                st.subheader("Average ROI Multiple (x) by Campaign Type")
                camp_summary = filtered_df.groupby("Campaign_Type", as_index=False)["ROI"].mean().sort_values("ROI", ascending=True)

                fig_camp_roi = px.bar(
                    camp_summary,
                    x="ROI",
                    y="Campaign_Type",
                    orientation="h",
                    color="ROI",
                    color_continuous_scale="Blues",
                    text_auto=".2f"
                )
                apply_chart_theme(fig_camp_roi, show_coloraxis=False)
                fig_camp_roi.update_xaxes(title_text="ROI Multiple (x)")
                fig_camp_roi.update_yaxes(title_text="Campaign Type")
                st.plotly_chart(fig_camp_roi, use_container_width=True)

        st.divider()

        if "Target_Audience" in filtered_df.columns:
            st.subheader("Activated Users & Activation Quality by Target Audience")
            aud_summary = filtered_df.groupby("Target_Audience", as_index=False).agg(
                Revenue=("Revenue", "sum"),
                Activated_Users=("Activated_Users", "sum"),
                Activation_Rate=("Activation_Rate", "mean")
            ).sort_values("Revenue", ascending=False)

            fig_aud_bar = px.bar(
                aud_summary,
                x="Target_Audience",
                y="Activated_Users",
                color="Activation_Rate",
                color_continuous_scale="Viridis",
                text_auto=","
            )
            apply_chart_theme(fig_aud_bar, show_coloraxis=False)
            fig_aud_bar.update_xaxes(title_text="Target Audience")
            fig_aud_bar.update_yaxes(title_text="Activated Users")
            st.plotly_chart(fig_aud_bar, use_container_width=True)

    # ------------------------------------------------------------------
    # TAB 4: CONVERSION FUNNEL & ANOMALIES
    # ------------------------------------------------------------------
    with tab4:
        st.markdown("### Marketing Conversion Funnel & Anomaly Detection")

        total_impressions = float(filtered_df["Impressions"].sum()) if "Impressions" in filtered_df.columns else 0.0
        total_clicks = float(filtered_df["Clicks"].sum()) if "Clicks" in filtered_df.columns else 0.0
        total_signups = float(filtered_df["Signups"].sum()) if "Signups" in filtered_df.columns else 0.0
        total_active = float(filtered_df["Activated_Users"].sum()) if "Activated_Users" in filtered_df.columns else 0.0

        f_col1, f_col2 = st.columns([1.2, 0.8])

        with f_col1:
            st.subheader("Lifecycle Conversion Funnel")
            funnel_data = dict(
                number=[total_impressions, total_clicks, total_signups, total_active],
                stage=["1. Impressions", "2. Clicks", "3. Signups", "4. Activated Users"]
            )
            fig_funnel = px.funnel(funnel_data, x="number", y="stage", color_discrete_sequence=[COLOR_PRIMARY])
            apply_chart_theme(fig_funnel)
            st.plotly_chart(fig_funnel, use_container_width=True)

        with f_col2:
            st.subheader("Stage Conversion Rates")

            ctr_step = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0.0
            signup_step = (total_signups / total_clicks * 100) if total_clicks > 0 else 0.0
            activation_step = (total_active / total_signups * 100) if total_signups > 0 else 0.0
            overall_step = (total_active / total_impressions * 100) if total_impressions > 0 else 0.0

            st.metric("Impression ➔ Click (CTR)", f"{ctr_step:.2f}%")
            st.metric("Click ➔ Signup Rate", f"{signup_step:.2f}%")
            st.metric("Signup ➔ Activation Rate", f"{activation_step:.2f}%")
            st.metric("Overall End-to-End Conversion", f"{overall_step:.3f}%")

        st.divider()

        # Anomaly Detection: High CTR but Low Activation Rate
        st.subheader("🚨 Campaign Anomaly & Vanity Traffic Log")
        st.caption("Campaigns flagged for high click activity but poor downstream user activation (< 35%).")

        overall_mean_ctr = float(df["CTR"].mean())
        anomalies = filtered_df[(filtered_df["CTR"] > overall_mean_ctr) & (filtered_df["Activation_Rate"] < 35.0)].copy()

        if not anomalies.empty:
            st.error(f"Found **{len(anomalies):,}** campaign records exhibiting vanity traffic risk (High CTR, low activation).")

            anomaly_cols = [
                "Campaign_ID", "Campaign_Type", "Primary_Platform", "Customer_Segment",
                "Impressions", "Clicks", "Signups", "Activated_Users",
                "CTR", "Activation_Rate", "Acquisition_Cost", "Revenue"
            ]
            valid_anomaly_cols = [c for c in anomaly_cols if c in anomalies.columns]
            st.dataframe(
                anomalies[valid_anomaly_cols].sort_values("Acquisition_Cost", ascending=False).head(50),
                use_container_width=True
            )
        else:
            st.success("No critical vanity traffic anomalies detected in the current selection.")

    # ------------------------------------------------------------------
    # TAB 5: CAMPAIGN EXPLORER & EXPORT
    # ------------------------------------------------------------------
    with tab5:
        st.markdown("### Detailed Campaign Explorer & Data Export Hub")

        search_query = st.text_input("Search by Campaign ID, Type, Platform, or Segment", "", key="search_query")

        display_df = filtered_df.copy()
        if search_query:
            search_pattern = str(search_query).strip()
            mask = np.zeros(len(display_df), dtype=bool)
            for col in ["Campaign_ID", "Campaign_Type", "Platform", "Primary_Platform", "Customer_Segment", "Target_Audience"]:
                if col in display_df.columns:
                    mask = mask | display_df[col].astype(str).str.contains(search_pattern, case=False, na=False)
            display_df = display_df[mask]

        st.subheader(f"Matching Records ({len(display_df):,})")

        columns_to_show = [
            "Campaign_ID", "Campaign_Type", "Target_Audience", "Primary_Platform", "Customer_Segment",
            "Date", "Impressions", "Clicks", "Signups", "Activated_Users",
            "CTR", "Signup_Rate", "Activation_Rate", "ROI", "Revenue", "Acquisition_Cost"
        ]
        valid_cols = [c for c in columns_to_show if c in display_df.columns]

        table_df = display_df[valid_cols].copy()
        if "Date" in table_df.columns and pd.api.types.is_datetime64_any_dtype(table_df["Date"]):
            table_df["Date"] = table_df["Date"].dt.strftime("%Y-%m-%d")

        st.dataframe(table_df.sort_values("Revenue", ascending=False).head(200), use_container_width=True)

        st.divider()

        exp_col1, exp_col2 = st.columns(2)

        with exp_col1:
            st.subheader("📥 Export CSV Data")
            csv_bytes = table_df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="Download Filtered Data (CSV)",
                data=csv_bytes,
                file_name="beyondclicks_filtered_campaigns.csv",
                mime="text/csv",
                use_container_width=True
            )

        with exp_col2:
            st.subheader("🌐 Automated Analytics Report")
            if st.button("Generate HTML Executive Report", use_container_width=True):
                try:
                    from export_functions import export_analysis
                    summary_md = f"""## BeyondClicks Campaign Executive Summary
- **Total Revenue**: ${total_revenue:,.2f}
- **Activated Users**: {int(total_activated):,}
- **Average Activation Rate**: {avg_activation_rate:.2f}%
- **Average CTR**: {avg_ctr:.2f}%
- **Average ROI**: {avg_roi:.2f}x
"""
                    fig_trend_exp = px.line(monthly_summary, x="YearMonth", y="Revenue", title="Monthly Revenue Trend")
                    charts_exp = {"Revenue Trend": fig_trend_exp}
                    report_dir = export_analysis(table_df, summary_md, charts_exp, "output")
                    st.success(f"Report exported successfully to `{report_dir}`")
                except Exception as ex:
                    st.error(f"Could not generate report: {ex}")


if __name__ == "__main__":
    main()
