import pandas as pd
from pathlib import Path
from datetime import datetime


# ============================================================
# CONFIGURATION
# ============================================================

DATA_PATH = Path("data/raw/orders.csv")


# ============================================================
# LOAD DATA
# ============================================================

def load_orders():
    """Load and prepare the orders dataset."""

    df = pd.read_csv(DATA_PATH)

    df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce")

    df = df.dropna(subset=["order_date", "amount", "customer_id"])

    return df


# ============================================================
# PERIOD HELPERS
# ============================================================

def get_month_data(df, year, month):
    """Return orders belonging to a specific month."""

    return df[
        (df["order_date"].dt.year == year)
        & (df["order_date"].dt.month == month)
    ].copy()


def get_previous_month(year, month):
    """Return the previous month and year."""

    if month == 1:
        return year - 1, 12

    return year, month - 1


# ============================================================
# KPI CALCULATIONS
# ============================================================

def calculate_revenue(df):
    """Calculate total revenue."""

    return df["amount"].sum()


def calculate_active_users(df):
    """Calculate unique customers active during the period."""

    return df["customer_id"].nunique()


def calculate_aov(df):
    """Calculate average order value."""

    if len(df) == 0:
        return 0

    return df["amount"].mean()


def calculate_change(current, previous):
    """Calculate percentage change."""

    if previous == 0:
        return 0

    return ((current - previous) / previous) * 100


# ============================================================
# TREND LOGIC
# ============================================================

def get_trend_indicator(change_pct, metric_name):
    """
    Determine trend direction and business status.

    Revenue, Active Users, AOV:
        Increase = Good
        Decrease = Bad

    Churn:
        Decrease = Good
        Increase = Bad
    """

    if metric_name == "Churn Rate":

        if change_pct < -2:
            return "↓", "green"

        elif change_pct > 2:
            return "↑", "red"

        else:
            return "→", "yellow"

    else:

        if change_pct > 2:
            return "↑", "green"

        elif change_pct < -2:
            return "↓", "red"

        else:
            return "→", "yellow"


# ============================================================
# MAIN KPI CALCULATION
# ============================================================

def calculate_kpis(df):
    """Calculate KPI values for current and previous month."""

    latest_date = df["order_date"].max()

    current_year = latest_date.year
    current_month = latest_date.month

    previous_year, previous_month = get_previous_month(
        current_year,
        current_month
    )

    current_df = get_month_data(
        df,
        current_year,
        current_month
    )

    previous_df = get_month_data(
        df,
        previous_year,
        previous_month
    )

    # Revenue
    current_revenue = calculate_revenue(current_df)
    previous_revenue = calculate_revenue(previous_df)

    revenue_change = calculate_change(
        current_revenue,
        previous_revenue
    )

    # Active users
    current_users = calculate_active_users(current_df)
    previous_users = calculate_active_users(previous_df)

    users_change = calculate_change(
        current_users,
        previous_users
    )

    # Average Order Value
    current_aov = calculate_aov(current_df)
    previous_aov = calculate_aov(previous_df)

    aov_change = calculate_change(
        current_aov,
        previous_aov
    )

    # Churn cannot be accurately calculated from this dataset
    # because there is no explicit customer churn/status field.
    current_churn = None
    previous_churn = None
    churn_change = None

    # Satisfaction is unavailable because the dataset
    # does not contain a rating/satisfaction column.
    current_satisfaction = None
    previous_satisfaction = None
    satisfaction_change = None

    kpis = pd.DataFrame({
        "Metric": [
            "Revenue",
            "Active Users",
            "AOV",
            "Churn Rate",
            "Satisfaction"
        ],

        "Current": [
            current_revenue,
            current_users,
            current_aov,
            current_churn,
            current_satisfaction
        ],

        "Prior": [
            previous_revenue,
            previous_users,
            previous_aov,
            previous_churn,
            previous_satisfaction
        ],

        "Change_Pct": [
            revenue_change,
            users_change,
            aov_change,
            churn_change,
            satisfaction_change
        ]
    })

    return kpis, current_year, current_month, previous_year, previous_month


# ============================================================
# DISPLAY
# ============================================================

if __name__ == "__main__":

    df = load_orders()

    kpis, current_year, current_month, previous_year, previous_month = calculate_kpis(df)

    print("\n========================================")
    print("BEYOND CLICKS KPI DASHBOARD")
    print("========================================")

    print(
        f"\nCurrent Period: "
        f"{current_year}-{current_month:02d}"
    )

    print(
        f"Previous Period: "
        f"{previous_year}-{previous_month:02d}"
    )

    print("\nKPI RESULTS")
    print("----------------------------------------")

    for _, row in kpis.iterrows():

        metric = row["Metric"]
        current = row["Current"]
        change = row["Change_Pct"]

        if pd.isna(current):
            print(f"{metric}: N/A")

        else:
            arrow, status = get_trend_indicator(
                change,
                metric
            )

            print(
                f"{metric}: "
                f"{current:,.2f} "
                f"{arrow} "
                f"{change:+.1f}% "
                f"[{status}]"
            )

    print("\n========================================")