# Beyond Clicks – Marketing Campaign Activation Analytics Dashboard

## Project Overview

Beyond Clicks is a marketing analytics platform designed to help organizations evaluate digital marketing campaigns using meaningful business outcomes instead of vanity metrics. It consolidates campaign data from multiple CSV datasets—including impressions, clicks, signups, and activation events—into a centralized analytics dashboard.

The platform automates data cleaning, KPI calculation, database storage, and visualization, enabling marketing teams and business leaders to identify which campaigns generate genuine customer activation and make informed marketing decisions.

---

## Problem Statement

A digital marketing team stores campaign impressions, click-through rates, and signup events across multiple tools, but leadership still lacks visibility into which campaigns generate meaningful downstream activation instead of vanity traffic.

---

## Project Objectives

* Centralize campaign performance data from multiple sources.
* Clean and preprocess raw marketing datasets.
* Store processed data in an SQLite database.
* Calculate key marketing performance indicators (KPIs).
* Provide interactive dashboards using Streamlit and Plotly.
* Support data-driven marketing decision making.

---

## Technology Stack

* **Programming Language:** Python
* **Data Processing:** Pandas, NumPy
* **Database:** SQLite
* **Visualization:** Plotly
* **Dashboard Framework:** Streamlit
* **Environment Management:** Python Virtual Environment (venv)
* **Configuration Management:** python-dotenv

---

## Key Performance Indicators (KPIs)

The dashboard calculates the following business metrics:

* Click Through Rate (CTR)
* Signup Rate
* Activation Rate
* Overall Conversion Rate

---

## Expected Workflow

1. Import marketing campaign CSV files.
2. Clean and preprocess the datasets using Pandas.
3. Store processed data in SQLite.
4. Calculate marketing KPIs.
5. Generate interactive visualizations using Plotly.
6. Display insights through the Streamlit dashboard.

---

## Future Enhancements

* Live integration with Google Ads, Meta Ads, and LinkedIn Ads APIs.
* Predictive analytics using machine learning.
* User authentication and role-based access control.
* Automated report generation.
* Real-time campaign monitoring.

---

## Team Roles

| Role                | Responsibilities                                                |
| ------------------- | --------------------------------------------------------------- |
| Backend Developer   | Data cleaning, database design, KPI calculation, SQL operations |
| Frontend Developer  | Streamlit dashboard, interactive charts, user interface         |
| Full Stack / DevOps | Project integration, testing, repository management, deployment |
