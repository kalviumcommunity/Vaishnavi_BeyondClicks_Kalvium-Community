# Analysis Report Export Guide

This guide describes the auto-generated export formats, their structures, and intended business use cases for stakeholders.

---

## What's Included in the Export Package

Every scheduled or on-demand export creates a timestamped folder (e.g. `output/2026-08-05_1700_analysis/`) containing the following four files:

### 1. `cleaned_data.csv`
- **Purpose**: Cleaned, raw transactional and engagement dataset.
- **Rows**: Dynamic based on records analyzed (e.g. 100 to 50,000 records).
- **Columns**: `customer_id`, `segment`, `churn_risk`, `support_interactions`, `response_time_hours`.
- **Use Case**: For financial analysts and data teams who want to filter, sort, and construct custom pivot tables or charts in Microsoft Excel.
- **Refresh**: Automatically updated daily at 5:00 PM.

### 2. `summary_report.pdf`
- **Purpose**: A concise executive summary of key churn findings and decisions needed.
- **Content**: Key findings, business impact risk analysis, ROI estimations, and next steps.
- **Length**: 1 to 2 pages max.
- **Use Case**: Perfect for printing, emailing to executive leadership, or embedding in strategic slides.
- **Format**: Standard PDF.

### 3. `interactive_report.html`
- **Purpose**: Full-featured interactive report containing embedded visualizations.
- **Content**: Executive summary text combined with dynamic Plotly charts (pan, zoom, hover tooltips).
- **Size**: Self-contained single file with no local dependencies (loads Plotly via CDN).
- **Use Case**: For operations and support managers who want to explore details and segment distributions in their web browsers without needing Python.
- **Sharing**: Can be emailed directly to stakeholders and opened in any modern browser.

### 4. `README.md`
- **Purpose**: Manifest metadata detailing exactly when the report ran, row count, and column listings.
- **Use Case**: Audit tracking.

---

## How to Use These Files

1. **For Excel pivot tables**: Open `cleaned_data.csv` in Excel.
2. **For business meetings**: Attach or present the PDF `summary_report.pdf`.
3. **For deep-dive analysis**: Open `interactive_report.html` in your browser.
4. **For dashboard downloads**: Click the **Export Analysis** sidebar button in our Streamlit dashboard to retrieve the latest version instantly.

---

## Refresh Schedule

- **Daily Batch Run**: The scheduler triggers an automated export daily at **5:00 PM** to reflect fresh CRM data.
- **On-Demand**: Triggered immediately by clicking the export button in the Streamlit application interface.
