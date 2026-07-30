import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# =========================================================
# PROJECT PATHS
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent

RAW_FILE = BASE_DIR / "data" / "raw" / "anomaly_campaign_data.csv"

PROCESSED_DIR = BASE_DIR / "data" / "processed"
OUTPUT_DIR = BASE_DIR / "output"

PROCESSED_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

print("=" * 70)
print("ANOMALY DETECTION & RISK IDENTIFICATION")
print("=" * 70)

# =========================================================
# LOAD DATA
# =========================================================

df = pd.read_csv(RAW_FILE)

print("\nDataset loaded successfully")
print(f"Rows: {len(df)}")
print(f"Columns: {list(df.columns)}")

# Convert date to datetime
df["date"] = pd.to_datetime(df["date"])


# =========================================================
# DAILY METRICS
# =========================================================

daily_metrics = df.groupby("date").agg({
    "daily_revenue": "sum",
    "transaction_count": "sum"
}).sort_index()

daily_metrics.rename(columns={
    "daily_revenue": "Revenue",
    "transaction_count": "Conversions"
}, inplace=True)

print("\nDaily Metrics:")
print(daily_metrics.head())

# =========================================================
# TASK 1
# THRESHOLD-BASED ANOMALY DETECTION
# =========================================================

print("\n" + "=" * 70)
print("TASK 1 : THRESHOLD-BASED ANOMALY DETECTION")
print("=" * 70)

alert_rules = {
    "Revenue": {
        "min": 5000,
        "max": 50000
    },
    "Conversions": {
        "min": 100,
        "max": 10000
    }
}


def check_thresholds(metrics, rules):
    """
    Check whether business metrics fall outside
    predefined minimum and maximum thresholds.
    """

    alerts = []

    for metric_name, rule in rules.items():

        value = metrics[metric_name]

        if value < rule["min"]:
            alerts.append({
                "metric": metric_name,
                "value": value,
                "threshold": rule["min"],
                "direction": "BELOW_MIN",
                "severity": "HIGH"
            })

        elif value > rule["max"]:
            alerts.append({
                "metric": metric_name,
                "value": value,
                "threshold": rule["max"],
                "direction": "ABOVE_MAX",
                "severity": "MEDIUM"
            })

    return alerts


# Check latest available day
latest_date = daily_metrics.index.max()
today_metrics = daily_metrics.loc[latest_date]

threshold_alerts = check_thresholds(
    today_metrics,
    alert_rules
)

print(f"\nChecking metrics for: {latest_date.date()}")

if threshold_alerts:
    for alert in threshold_alerts:
        print(
            f"ALERT: {alert['metric']} "
            f"{alert['direction']} - "
            f"{alert['value']:.2f}"
        )
else:
    print("No threshold violations detected.")

# =========================================================
# TASK 2
# Z-SCORE STATISTICAL ANOMALY DETECTION
# =========================================================

print("\n" + "=" * 70)
print("TASK 2 : Z-SCORE ANOMALY DETECTION")
print("=" * 70)


def detect_anomalies_zscore(series, threshold=2):
    """
    Detect values more than N standard deviations
    away from the mean.
    """

    mean = series.mean()
    std = series.std()

    if std == 0:
        z_scores = pd.Series(0, index=series.index)
    else:
        z_scores = (series - mean) / std

    anomalies = series[abs(z_scores) > threshold]

    return anomalies, z_scores


# Use last 30 available days
daily_revenue = daily_metrics["Revenue"].tail(30)

anomalies, z_scores = detect_anomalies_zscore(
    daily_revenue,
    threshold=2
)

mean_revenue = daily_revenue.mean()
std_revenue = daily_revenue.std()

print(f"\n30-day average revenue: {mean_revenue:.2f}")
print(f"Standard deviation: {std_revenue:.2f}")

print(f"\nDetected {len(anomalies)} anomalies.")

for date, value in anomalies.items():

    print(
        f"{date.date()} : "
        f"Revenue = {value:.2f}, "
        f"Z-score = {z_scores[date]:.2f}"
    )

# =========================================================
# TASK 3
# SEVERITY CLASSIFICATION
# =========================================================

print("\n" + "=" * 70)
print("TASK 3 : SEVERITY CLASSIFICATION")
print("=" * 70)


def classify_severity(value, mean, std):
    """
    Classify anomaly based on absolute Z-score.
    """

    if std == 0:
        return "LOW"

    z_score = abs((value - mean) / std)

    if z_score > 3:
        return "CRITICAL"

    elif z_score > 2:
        return "HIGH"

    elif z_score > 1.5:
        return "MEDIUM"

    else:
        return "LOW"


severity_records = []

for date, value in anomalies.items():

    severity = classify_severity(
        value,
        mean_revenue,
        std_revenue
    )

    severity_records.append({
        "date": date,
        "value": value,
        "z_score": z_scores[date],
        "severity": severity
    })


severity_df = pd.DataFrame(severity_records)

if not severity_df.empty:

    print("\nAnomaly Severity:")
    print(severity_df)

    high_priority = severity_df[
        severity_df["severity"].isin(
            ["CRITICAL", "HIGH"]
        )
    ]

    print(
        f"\nHigh priority anomalies: "
        f"{len(high_priority)}"
    )

else:

    print("\nNo statistical anomalies detected.")

# =========================================================
# TASK 4
# ANOMALY LOGGING & AUDIT TRAIL
# =========================================================

print("\n" + "=" * 70)
print("TASK 4 : ANOMALY LOGGING & AUDIT TRAIL")
print("=" * 70)

anomaly_log = []

for date, value in anomalies.items():

    severity = classify_severity(
        value,
        mean_revenue,
        std_revenue
    )

    anomaly_log.append({
        "timestamp": pd.Timestamp.now(),
        "anomaly_date": date,
        "metric": "Revenue",
        "value": round(value, 2),
        "expected_min": round(
            mean_revenue - 2 * std_revenue,
            2
        ),
        "expected_max": round(
            mean_revenue + 2 * std_revenue,
            2
        ),
        "z_score": round(
            z_scores[date],
            2
        ),
        "severity": severity,
        "status": "OPEN"
    })


anomalies_df = pd.DataFrame(anomaly_log)

anomaly_log_file = (
    PROCESSED_DIR / "anomaly_log.csv"
)

anomalies_df.to_csv(
    anomaly_log_file,
    index=False
)

print(
    f"Anomaly log saved to: "
    f"{anomaly_log_file}"
)

# =========================================================
# ANOMALY SUMMARY
# =========================================================

summary = pd.DataFrame({
    "Metric": [
        "Days Monitored",
        "Average Revenue",
        "Standard Deviation",
        "Anomalies Detected",
        "High/Critical Anomalies"
    ],
    "Value": [
        len(daily_revenue),
        round(mean_revenue, 2),
        round(std_revenue, 2),
        len(anomalies),
        len(
            severity_df[
                severity_df["severity"].isin(
                    ["HIGH", "CRITICAL"]
                )
            ]
        ) if not severity_df.empty else 0
    ]
})

summary_file = (
    PROCESSED_DIR / "anomaly_summary.csv"
)

summary.to_csv(
    summary_file,
    index=False
)

print(f"Summary saved to: {summary_file}")

# =========================================================
# TASK 5
# VISUALIZATION
# =========================================================

print("\n" + "=" * 70)
print("TASK 5 : ANOMALY VISUALIZATION")
print("=" * 70)

fig, ax = plt.subplots(figsize=(14, 6))

# Raw daily revenue
ax.plot(
    daily_revenue.index,
    daily_revenue.values,
    marker="o",
    label="Daily Revenue",
    linewidth=2
)

# 7-day rolling average
rolling_avg = daily_revenue.rolling(
    window=7
).mean()

ax.plot(
    rolling_avg.index,
    rolling_avg.values,
    label="7-Day Moving Average",
    linewidth=2
)

# Expected range
upper_limit = mean_revenue + 2 * std_revenue
lower_limit = mean_revenue - 2 * std_revenue

ax.fill_between(
    daily_revenue.index,
    lower_limit,
    upper_limit,
    alpha=0.2,
    label="Expected Range ±2σ"
)

# Highlight anomalies
for date, value in anomalies.items():

    ax.scatter(
        date,
        value,
        s=180,
        marker="X",
        zorder=5,
        label="Anomaly" if date == anomalies.index[0]
        else ""
    )

    ax.annotate(
        "ANOMALY",
        (date, value),
        xytext=(0, 12),
        textcoords="offset points",
        ha="center",
        fontweight="bold"
    )


ax.set_xlabel("Date")
ax.set_ylabel("Revenue")
ax.set_title(
    "Beyond Clicks - Daily Revenue Anomaly Detection"
)

ax.legend()
ax.grid(True, alpha=0.3)

plt.xticks(rotation=45)
plt.tight_layout()

chart_file = (
    OUTPUT_DIR / "anomaly_detection.png"
)

plt.savefig(
    chart_file,
    dpi=150
)

plt.show()

print(f"Visualization saved to: {chart_file}")

# =========================================================
# FINAL RESULT
# =========================================================

print("\n" + "=" * 70)
print("ANOMALY DETECTION COMPLETED")
print("=" * 70)

print(f"Days monitored: {len(daily_revenue)}")
print(f"Anomalies found: {len(anomalies)}")
print(f"Average revenue: {mean_revenue:.2f}")
print(f"Expected lower limit: {lower_limit:.2f}")
print(f"Expected upper limit: {upper_limit:.2f}")

print("\nFiles generated:")
print("✓ data/processed/anomaly_log.csv")
print("✓ data/processed/anomaly_summary.csv")
print("✓ output/anomaly_detection.png")