import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter


# ============================================================
# BEYONDCLICKS - BUSINESS VISUALISATIONS
# Business Visualisation Principles Assignment
# ============================================================

# ------------------------------------------------------------
# Configuration
# ------------------------------------------------------------

INPUT_FILE = "data/processed/feature_engineered_campaign_data.csv"
OUTPUT_DIR = "output/visualisations"

os.makedirs(OUTPUT_DIR, exist_ok=True)


# ------------------------------------------------------------
# Consistent Colour Palette
# ------------------------------------------------------------

PALETTE = {
    "primary": "#1f77b4",
    "secondary": "#ff7f0e",
    "success": "#2ca02c",
    "danger": "#d62728",
    "neutral": "#7f7f7f",
    "purple": "#9467bd"
}

CHART_COLORS = [
    PALETTE["primary"],
    PALETTE["secondary"],
    PALETTE["success"],
    PALETTE["danger"],
    PALETTE["purple"]
]


# ------------------------------------------------------------
# Load Data
# ------------------------------------------------------------

print("=" * 70)
print("BEYONDCLICKS - BUSINESS VISUALISATIONS")
print("=" * 70)

df = pd.read_csv(INPUT_FILE)

df["Date"] = pd.to_datetime(df["Date"])

print(f"\nDataset loaded successfully")
print(f"Rows: {len(df):,}")
print(f"Columns: {len(df.columns)}")


# ============================================================
# CHART 1
# Revenue by Campaign Type
# Assignment equivalent: Bar Chart / Comparison
# ============================================================

print("\nCreating Chart 1: Revenue by Campaign Type...")

revenue_by_campaign = (
    df.groupby("Campaign_Type")["Revenue"]
    .sum()
    .sort_values(ascending=True)
)

fig, ax = plt.subplots(figsize=(10, 6))

bars = ax.barh(
    revenue_by_campaign.index,
    revenue_by_campaign.values,
    color=PALETTE["primary"]
)

ax.set_title(
    "Total Revenue by Campaign Type",
    fontsize=14,
    fontweight="bold"
)

ax.set_xlabel("Revenue ($)")
ax.set_ylabel("Campaign Type")

# Data labels
for bar, value in zip(bars, revenue_by_campaign.values):
    ax.text(
        bar.get_width(),
        bar.get_y() + bar.get_height() / 2,
        f"${value:,.0f}",
        va="center",
        ha="left",
        fontsize=9
    )

# Annotation: highest campaign type
highest_campaign = revenue_by_campaign.idxmax()
highest_value = revenue_by_campaign.max()

ax.annotate(
    f"Highest revenue:\n{highest_campaign}",
    xy=(highest_value, list(revenue_by_campaign.index).index(highest_campaign)),
    xytext=(highest_value * 0.65, list(revenue_by_campaign.index).index(highest_campaign) + 0.5),
    arrowprops=dict(arrowstyle="->"),
    fontsize=10
)

ax.grid(axis="x", alpha=0.3)

plt.tight_layout()

chart1_path = os.path.join(
    OUTPUT_DIR,
    "chart1_revenue_by_campaign_type.png"
)

plt.savefig(chart1_path, dpi=300, bbox_inches="tight")
plt.close()


# ============================================================
# CHART 2
# Revenue Trend
# Assignment equivalent: Line Chart / Trend
# ============================================================

print("Creating Chart 2: Monthly Revenue Trend...")

monthly_revenue = (
    df.set_index("Date")
    .resample("ME")["Revenue"]
    .sum()
)

fig, ax = plt.subplots(figsize=(12, 6))

ax.plot(
    monthly_revenue.index,
    monthly_revenue.values,
    marker="o",
    linewidth=2,
    color=PALETTE["primary"],
    label="Monthly Revenue"
)

ax.set_title(
    "Monthly Revenue Trend",
    fontsize=14,
    fontweight="bold"
)

ax.set_xlabel("Month")
ax.set_ylabel("Revenue ($)")

ax.yaxis.set_major_formatter(
    FuncFormatter(lambda x, p: f"${x/1e6:.1f}M")
)

ax.legend()

ax.grid(True, alpha=0.3)

# Reference line: average revenue
average_revenue = monthly_revenue.mean()

ax.axhline(
    average_revenue,
    linestyle="--",
    color=PALETTE["success"],
    linewidth=2,
    label="Average Revenue"
)

# Peak annotation
peak_date = monthly_revenue.idxmax()
peak_value = monthly_revenue.max()

ax.annotate(
    f"Peak\n${peak_value:,.0f}",
    xy=(peak_date, peak_value),
    xytext=(peak_date, peak_value * 1.08),
    arrowprops=dict(arrowstyle="->"),
    fontsize=10
)

ax.legend()

plt.tight_layout()

chart2_path = os.path.join(
    OUTPUT_DIR,
    "chart2_revenue_trend.png"
)

plt.savefig(chart2_path, dpi=300, bbox_inches="tight")
plt.close()


# ============================================================
# CHART 3
# Revenue Distribution
# Assignment equivalent: Histogram / Distribution
# ============================================================

print("Creating Chart 3: Revenue Distribution...")

fig, ax = plt.subplots(figsize=(10, 6))

ax.hist(
    df["Revenue"],
    bins=20,
    color=PALETTE["secondary"],
    edgecolor="black",
    alpha=0.8
)

ax.set_title(
    "Distribution of Campaign Revenue",
    fontsize=14,
    fontweight="bold"
)

ax.set_xlabel("Revenue per Campaign ($)")
ax.set_ylabel("Number of Campaigns")

# Mean reference
mean_revenue = df["Revenue"].mean()

ax.axvline(
    mean_revenue,
    color=PALETTE["danger"],
    linestyle="--",
    linewidth=2,
    label=f"Mean: ${mean_revenue:,.0f}"
)

ax.annotate(
    f"Mean Revenue\n${mean_revenue:,.0f}",
    xy=(mean_revenue, ax.get_ylim()[1] * 0.75),
    xytext=(mean_revenue * 1.15, ax.get_ylim()[1] * 0.75),
    arrowprops=dict(arrowstyle="->"),
    fontsize=10
)

ax.legend()

ax.grid(axis="y", alpha=0.3)

plt.tight_layout()

chart3_path = os.path.join(
    OUTPUT_DIR,
    "chart3_revenue_distribution.png"
)

plt.savefig(chart3_path, dpi=300, bbox_inches="tight")
plt.close()


# ============================================================
# CHART 4
# Quarterly Revenue Composition by Campaign Type
# Assignment equivalent: Stacked Bar / Composition
# ============================================================

print("Creating Chart 4: Quarterly Revenue Composition...")

df["Quarter"] = df["Date"].dt.to_period("Q").astype(str)

quarterly_campaign = (
    df.groupby(["Quarter", "Campaign_Type"])["Revenue"]
    .sum()
    .unstack(fill_value=0)
)

fig, ax = plt.subplots(figsize=(12, 6))

bottom = np.zeros(len(quarterly_campaign))

campaign_types = quarterly_campaign.columns

for i, campaign_type in enumerate(campaign_types):

    values = quarterly_campaign[campaign_type].values

    ax.bar(
        quarterly_campaign.index,
        values,
        bottom=bottom,
        label=campaign_type,
        color=CHART_COLORS[i % len(CHART_COLORS)]
    )

    bottom += values

ax.set_title(
    "Quarterly Revenue Composition by Campaign Type",
    fontsize=14,
    fontweight="bold"
)

ax.set_xlabel("Quarter")
ax.set_ylabel("Revenue ($)")

ax.legend(
    title="Campaign Type",
    bbox_to_anchor=(1.02, 1),
    loc="upper left"
)

# Annotation on largest quarter
quarter_totals = quarterly_campaign.sum(axis=1)

best_quarter = quarter_totals.idxmax()
best_quarter_value = quarter_totals.max()

best_index = list(quarterly_campaign.index).index(best_quarter)

ax.annotate(
    f"Highest quarter\n${best_quarter_value:,.0f}",
    xy=(best_index, best_quarter_value),
    xytext=(best_index, best_quarter_value * 1.08),
    arrowprops=dict(arrowstyle="->"),
    ha="center",
    fontsize=10
)

ax.grid(axis="y", alpha=0.3)

plt.tight_layout()

chart4_path = os.path.join(
    OUTPUT_DIR,
    "chart4_revenue_composition.png"
)

plt.savefig(chart4_path, dpi=300, bbox_inches="tight")
plt.close()


# ============================================================
# CHART 5
# Acquisition Cost vs Revenue
# Assignment equivalent: Scatter Plot / Correlation
# ============================================================

print("Creating Chart 5: Acquisition Cost vs Revenue...")

x = df["Acquisition_Cost"]
y = df["Revenue"]

fig, ax = plt.subplots(figsize=(10, 6))

ax.scatter(
    x,
    y,
    alpha=0.4,
    color=PALETTE["primary"],
    label="Campaigns"
)

# Calculate correlation
correlation = x.corr(y)

# Trend line
slope, intercept = np.polyfit(x, y, 1)

trend_x = np.linspace(x.min(), x.max(), 100)
trend_y = slope * trend_x + intercept

ax.plot(
    trend_x,
    trend_y,
    color=PALETTE["danger"],
    linewidth=2,
    label=f"Trend line (r={correlation:.2f})"
)

ax.set_title(
    "Acquisition Cost vs Campaign Revenue",
    fontsize=14,
    fontweight="bold"
)

ax.set_xlabel("Acquisition Cost ($)")
ax.set_ylabel("Revenue ($)")

ax.legend()

# Correlation annotation
ax.annotate(
    f"Correlation: {correlation:.2f}",
    xy=(0.05, 0.92),
    xycoords="axes fraction",
    fontsize=11,
    bbox=dict(boxstyle="round,pad=0.4", alpha=0.2)
)

ax.grid(True, alpha=0.3)

plt.tight_layout()

chart5_path = os.path.join(
    OUTPUT_DIR,
    "chart5_cost_vs_revenue.png"
)

plt.savefig(chart5_path, dpi=300, bbox_inches="tight")
plt.close()


# ============================================================
# FINAL OUTPUT
# ============================================================

print("\n" + "=" * 70)
print("VISUALISATIONS COMPLETED SUCCESSFULLY")
print("=" * 70)

print("\nCreated charts:")

print("1. chart1_revenue_by_campaign_type.png")
print("2. chart2_revenue_trend.png")
print("3. chart3_revenue_distribution.png")
print("4. chart4_revenue_composition.png")
print("5. chart5_cost_vs_revenue.png")

print(f"\nOutput directory:")
print(OUTPUT_DIR)

print("\n" + "=" * 70)