import pandas as pd
from pathlib import Path

# ---------------------------------------------------------
# Project Paths
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

RAW_FILE = BASE_DIR / "data" / "raw" / "campaign_segment_data.csv"

PROCESSED_DIR = BASE_DIR / "data" / "processed"
PROCESSED_DIR.mkdir(exist_ok=True)

print("=" * 70)
print("GROUPBY AGGREGATION & SEGMENT INSIGHTS")
print("=" * 70)

# ---------------------------------------------------------
# Load Dataset
# ---------------------------------------------------------

df = pd.read_csv(RAW_FILE)

print("\nCampaign Dataset\n")
print(df)

# =========================================================
# TASK 1
# Single Level GroupBy
# =========================================================

print("\n" + "=" * 70)
print("TASK 1 : Campaign Type Aggregation")
print("=" * 70)

segment_metrics = df.groupby("Campaign_Type").agg({
    "Revenue": "sum",
    "Campaign_ID": "count",
    "Engagement_Score": "mean",
    "Conversions": "sum"
})

segment_metrics.columns = [
    "Total_Revenue",
    "Campaign_Count",
    "Average_Engagement",
    "Total_Conversions"
]

print(segment_metrics)

segment_metrics.to_csv(
    PROCESSED_DIR / "campaign_segment_summary.csv"
)

# =========================================================
# TASK 2
# Multi Level GroupBy
# =========================================================

print("\n" + "=" * 70)
print("TASK 2 : Campaign Type + Platform")
print("=" * 70)

multi_group = df.groupby(
    ["Campaign_Type", "Platform"]
).agg({
    "Revenue": "sum",
    "Campaign_ID": "count"
})

multi_group.columns = [
    "Total_Revenue",
    "Campaign_Count"
]

print(multi_group)

multi_group.to_csv(
    PROCESSED_DIR / "campaign_platform_summary.csv"
)

# =========================================================
# TASK 3
# Pivot Table
# =========================================================

print("\n" + "=" * 70)
print("TASK 3 : Revenue Pivot Table")
print("=" * 70)

pivot = pd.pivot_table(
    df,
    values="Revenue",
    index="Campaign_Type",
    columns="Platform",
    aggfunc="sum",
    fill_value=0
)

print(pivot)

pivot.to_csv(
    PROCESSED_DIR / "campaign_pivot_table.csv"
)

# =========================================================
# TASK 4
# Ranking
# =========================================================

print("\n" + "=" * 70)
print("TASK 4 : Revenue Ranking")
print("=" * 70)

segment_metrics["Revenue_Rank"] = (
    segment_metrics["Total_Revenue"]
    .rank(ascending=False, method="dense")
    .astype(int)
)

segment_metrics["Revenue_Contribution"] = (
    segment_metrics["Total_Revenue"]
    / segment_metrics["Total_Revenue"].sum()
    * 100
).round(2)

ranking = segment_metrics.sort_values(
    "Revenue_Rank"
)

print(ranking)

# =========================================================
# TASK 5
# Business Insights
# =========================================================

print("\n" + "=" * 70)
print("TASK 5 : Actionable Insights")
print("=" * 70)

insights = []

for campaign in ranking.index:

    row = ranking.loc[campaign]

    if row["Average_Engagement"] >= 90:
        action = "Excellent engagement. Increase campaign investment."

    elif row["Average_Engagement"] >= 80:
        action = "Good performance. Continue optimization."

    else:
        action = "Needs improvement. Review targeting and creatives."

    insights.append({
        "Campaign_Type": campaign,
        "Campaign_Count": int(row["Campaign_Count"]),
        "Total_Revenue": row["Total_Revenue"],
        "Average_Engagement": round(
            row["Average_Engagement"], 2
        ),
        "Revenue_Contribution (%)": round(
            row["Revenue_Contribution"], 2
        ),
        "Revenue_Rank": int(row["Revenue_Rank"]),
        "Business_Action": action
    })

insights_df = pd.DataFrame(insights)

print(insights_df)

insights_df.to_csv(
    PROCESSED_DIR / "campaign_segment_insights.csv",
    index=False
)

print("\n" + "=" * 70)
print("FILES GENERATED")
print("=" * 70)

print("✓ campaign_segment_summary.csv")
print("✓ campaign_platform_summary.csv")
print("✓ campaign_pivot_table.csv")
print("✓ campaign_segment_insights.csv")