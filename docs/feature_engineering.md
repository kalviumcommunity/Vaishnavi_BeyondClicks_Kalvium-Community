# BeyondClicks Feature Engineering

## Objective

Feature engineering was performed to create meaningful campaign performance metrics from the cleaned campaign dataset.

The processed dataset contains 55,555 rows and 16 columns. Feature engineering adds seven derived features without changing the number of rows.

## Input Dataset

Rows: 55,555

Columns: 16

## Engineered Features

### 1. CTR

Click-Through Rate measures the percentage of impressions that resulted in clicks.

Formula:

CTR = (Clicks / Impressions) × 100

### 2. Signup Rate

Measures the percentage of clicks that resulted in signups.

Formula:

Signup Rate = (Signups / Clicks) × 100

### 3. Activation Rate

Measures the percentage of signups that became activated users.

Formula:

Activation Rate = (Activated Users / Signups) × 100

### 4. Click-to-Activation Rate

Measures the percentage of clicks that eventually resulted in activated users.

Formula:

Click-to-Activation Rate = (Activated Users / Clicks) × 100

### 5. Revenue per Activated User

Measures the average revenue generated per activated user.

Formula:

Revenue per Activated User = Revenue / Activated Users

### 6. Cost per Activated User

Measures the acquisition cost associated with each activated user.

Formula:

Cost per Activated User = Acquisition Cost / Activated Users

### 7. Cost per Signup

Measures the acquisition cost associated with each signup.

Formula:

Cost per Signup = Acquisition Cost / Signups

## Output

The feature-engineered dataset contains:

- Rows: 55,555
- Columns: 23

The output is stored at:

`data/processed/feature_engineered_campaign_data.csv`

## Business Value

These engineered features help BeyondClicks evaluate campaigns based on meaningful outcomes rather than only vanity metrics such as impressions and clicks.

The features allow analysis of:

- Click efficiency
- Signup conversion
- User activation
- Revenue efficiency
- Acquisition cost efficiency