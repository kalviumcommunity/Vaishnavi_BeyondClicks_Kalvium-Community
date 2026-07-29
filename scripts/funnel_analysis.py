import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# =========================================================
# PROJECT PATHS
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent

RAW_FILE = BASE_DIR / "data" / "raw" / "funnel_campaign_data.csv"

PROCESSED_DIR = BASE_DIR / "data" / "processed"
OUTPUT_DIR = BASE_DIR / "output"

PROCESSED_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

print("=" * 70)
print("BEYOND CLICKS - FUNNEL ANALYSIS & DROP-OFF DETECTION")
print("=" * 70)

# =========================================================
# LOAD DATA
# =========================================================

df = pd.read_csv(RAW_FILE)

print("\nCampaign Funnel Dataset")
print(df)

# =========================================================
# TASK 1
# DEFINE FUNNEL STAGES
# =========================================================

print("\n" + "=" * 70)
print("TASK 1 : FUNNEL STAGES")
print("=" * 70)

stages = {
    "Impressions": df["Impressions"].sum(),
    "Clicks": df["Clicks"].sum(),
    "Signups": df["Signups"].sum(),
    "Activations": df["Activations"].sum()
}

print("\nFunnel Stage Counts:")

for stage, count in stages.items():
    print(f"{stage}: {count:,}")

# =========================================================
# TASK 2
# DROP-OFF CALCULATION
# =========================================================

print("\n" + "=" * 70)
print("TASK 2 : DROP-OFF ANALYSIS")
print("=" * 70)

stage_names = list(stages.keys())
stage_values = list(stages.values())

drop_off = []

for i in range(len(stage_values) - 1):

    current_stage = stage_names[i]
    next_stage = stage_names[i + 1]

    current_users = stage_values[i]
    next_users = stage_values[i + 1]

    users_lost = current_users - next_users

    drop_rate = (users_lost / current_users) * 100

    completion_rate = (next_users / current_users) * 100

    drop_off.append({
        "From_Stage": current_stage,
        "To_Stage": next_stage,
        "Users_Before": current_users,
        "Users_After": next_users,
        "Users_Lost": users_lost,
        "Completion_Rate": round(completion_rate, 2),
        "Drop_Rate": round(drop_rate, 2)
    })

funnel_df = pd.DataFrame(drop_off)

print("\nDrop-Off Report")
print(funnel_df)

# Find biggest drop by percentage
biggest_drop_idx = funnel_df["Drop_Rate"].idxmax()

biggest_drop = funnel_df.loc[biggest_drop_idx]

print("\nBiggest Drop-Off:")
print(biggest_drop)

# =========================================================
# TASK 3
# FUNNEL VISUALIZATION
# =========================================================

print("\n" + "=" * 70)
print("TASK 3 : FUNNEL VISUALIZATION")
print("=" * 70)

plt.figure(figsize=(10, 6))

bars = plt.bar(
    stage_names,
    stage_values
)

plt.title("BeyondClicks Marketing Funnel")
plt.xlabel("Funnel Stage")
plt.ylabel("Count")

# Add numbers above bars
for bar, value in zip(bars, stage_values):

    plt.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height(),
        f"{value:,}",
        ha="center",
        va="bottom"
    )

plt.xticks(rotation=20)
plt.tight_layout()

chart_path = OUTPUT_DIR / "funnel_chart.png"

plt.savefig(chart_path, dpi=150)

plt.close()

print(f"✓ Funnel chart saved: {chart_path}")

# =========================================================
# TASK 4
# BUSINESS IMPACT
# =========================================================

print("\n" + "=" * 70)
print("TASK 4 : BUSINESS IMPACT")
print("=" * 70)

# Estimated business value of one activation
value_per_activation = 100

impact_analysis = []

for _, row in funnel_df.iterrows():

    users_lost = row["Users_Lost"]

    revenue_impact = users_lost * value_per_activation

    if revenue_impact >= 100000:
        priority = "HIGH"
    elif revenue_impact >= 50000:
        priority = "MEDIUM"
    else:
        priority = "LOW"

    impact_analysis.append({
        "Drop_Point":
            f"{row['From_Stage']} -> {row['To_Stage']}",

        "Users_Lost":
            users_lost,

        "Revenue_Impact":
            revenue_impact,

        "Priority":
            priority
    })

impact_df = pd.DataFrame(impact_analysis)

print("\nBusiness Impact Analysis")
print(impact_df)

# =========================================================
# CAMPAIGN-LEVEL FUNNEL ANALYSIS
# =========================================================

print("\n" + "=" * 70)
print("CAMPAIGN LEVEL FUNNEL ANALYSIS")
print("=" * 70)

campaign_analysis = df.copy()

campaign_analysis["CTR"] = (
    campaign_analysis["Clicks"]
    / campaign_analysis["Impressions"]
    * 100
).round(2)

campaign_analysis["Signup_Rate"] = (
    campaign_analysis["Signups"]
    / campaign_analysis["Clicks"]
    * 100
).round(2)

campaign_analysis["Activation_Rate"] = (
    campaign_analysis["Activations"]
    / campaign_analysis["Signups"]
    * 100
).round(2)

campaign_analysis["Overall_Conversion_Rate"] = (
    campaign_analysis["Activations"]
    / campaign_analysis["Impressions"]
    * 100
).round(2)

print(campaign_analysis)

# =========================================================
# TASK 5
# ACTIONABLE RECOMMENDATION
# =========================================================

print("\n" + "=" * 70)
print("TASK 5 : ACTIONABLE RECOMMENDATION")
print("=" * 70)

highest_impact = impact_df.loc[
    impact_df["Revenue_Impact"].idxmax()
]

recommendation = f"""
BEYOND CLICKS FUNNEL OPTIMIZATION

BIGGEST BOTTLENECK:
{highest_impact["Drop_Point"]}

Users Lost:
{highest_impact["Users_Lost"]:,}

Estimated Business Impact:
${highest_impact["Revenue_Impact"]:,}

Priority:
{highest_impact["Priority"]}

RECOMMENDED ACTION:

1. Investigate why users are dropping at this stage.
2. Check campaign landing pages and user experience.
3. Check whether the signup-to-activation journey is too complex.
4. Test a simplified conversion flow using A/B testing.
5. Monitor the activation rate after the change.

SUCCESS CRITERIA:

Improve the completion rate at the bottleneck stage by at least 10%.

EXPECTED IMPACT:

A 10% recovery of the lost users could produce approximately
{int(highest_impact["Users_Lost"] * 0.10):,} additional conversions.

Estimated additional business value:
${int(highest_impact["Users_Lost"] * 0.10 * value_per_activation):,}
"""

print(recommendation)

# =========================================================
# SAVE OUTPUT FILES
# =========================================================

funnel_summary = pd.DataFrame({
    "Stage": stage_names,
    "Users": stage_values
})

funnel_summary.to_csv(
    PROCESSED_DIR / "funnel_summary.csv",
    index=False
)

funnel_df.to_csv(
    PROCESSED_DIR / "funnel_dropoff_report.csv",
    index=False
)

campaign_analysis.to_csv(
    PROCESSED_DIR / "campaign_funnel_analysis.csv",
    index=False
)

# Save text report
report_path = OUTPUT_DIR / "funnel_analysis.txt"

with open(report_path, "w", encoding="utf-8") as file:

    file.write("BEYOND CLICKS FUNNEL ANALYSIS\n")
    file.write("=" * 60 + "\n\n")

    file.write("FUNNEL STAGES\n")

    for stage, count in stages.items():
        file.write(f"{stage}: {count:,}\n")

    file.write("\nDROP-OFF ANALYSIS\n")
    file.write(funnel_df.to_string(index=False))

    file.write("\n\nBUSINESS IMPACT\n")
    file.write(impact_df.to_string(index=False))

    file.write("\n\nRECOMMENDATION\n")
    file.write(recommendation)

print("\n" + "=" * 70)
print("FILES GENERATED")
print("=" * 70)

print("✓ funnel_summary.csv")
print("✓ funnel_dropoff_report.csv")
print("✓ campaign_funnel_analysis.csv")
print("✓ funnel_chart.png")
print("✓ funnel_analysis.txt")

print("\n✓ Funnel analysis completed successfully.")