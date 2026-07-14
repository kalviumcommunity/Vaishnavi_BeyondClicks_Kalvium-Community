# Beyond Clicks – Marketing Campaign Activation Analytics Dashboard

## Problem Statement

A digital marketing team stores campaign impressions, click-through rates, and signup events across multiple tools, but leadership still lacks visibility into which campaigns generate meaningful downstream activation instead of vanity traffic.

---

## Project Overview

Beyond Clicks is a marketing analytics platform designed to help organizations evaluate digital marketing campaigns using meaningful business outcomes instead of vanity metrics. It consolidates campaign data from multiple CSV datasets—including impressions, clicks, signups, and activation events—into a centralized analytics dashboard.

The platform automates data cleaning, KPI calculation, database storage, and visualization, enabling marketing teams and business leaders to identify which campaigns generate genuine customer activation and make informed marketing decisions.

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

## Project Structure

```text
Beyond-Clicks/
│
├── data/
│   ├── raw/
│   └── processed/
│
├── notebooks/
│
├── scripts/
│
├── output/
│
├── venv/
│
├── .env
├── .gitignore
├── requirements.txt
└── README.md
```

### Folder Description

* **data/raw/** – Original marketing datasets received from different platforms.
* **data/processed/** – Cleaned and transformed datasets used for analysis.
* **notebooks/** – Jupyter notebooks for exploratory analysis and experimentation.
* **scripts/** – Python scripts for data cleaning, KPI calculation, database operations, and automation.
* **output/** – Generated reports, exported files, and visual outputs.
* **venv/** – Python virtual environment (not committed to Git).
* **requirements.txt** – List of project dependencies.
* **.gitignore** – Files and folders excluded from version control.
* **README.md** – Project documentation and setup instructions.
---

## Installation

### 1. Clone the repository

```bash
git clone <repository-url>
cd BeyondClicks
```

### 2. Create a virtual environment

**Windows**

```bash
python -m venv venv
```

### 3. Activate the virtual environment

**Windows Command Prompt**

```bash
venv\Scripts\activate
```

**Windows PowerShell**

```powershell
venv\Scripts\Activate.ps1
```

### 4. Install project dependencies

```bash
pip install -r requirements.txt
```

---

### 5.Configure environment variables

Copy .env.example to .env and update the required configuration values.

Example:
DATABASE_NAME=marketing.db


## Running the Analysis

Run the data cleaning script:

```bash
python scripts/clean_data.py
```

Load the cleaned data into the SQLite database:

```bash
python scripts/load_database.py
```

Calculate campaign KPIs:

```bash
python scripts/calculate_kpis.py
```

Launch the Streamlit dashboard:

```bash
streamlit run app.py
```

If using Jupyter notebooks for exploratory analysis:

```bash
jupyter notebook notebooks/
```

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

## Team Workflow

The project follows a GitHub-based workflow using feature branches, GitHub Issues, Pull Requests, and Conventional Commit messages to ensure safe collaboration.