# Task 5: Metric Drift & Manual Investigation Analysis

## Follow-Up Question
> **Question:** You have a validation script that runs daily and catches metrics drift automatically. However, it flags a discrepancy but does not auto-fix it - someone must investigate. Why is manual investigation necessary? What would be the risk of auto-fixing based on a tolerance threshold alone?

---

## Technical Answer & Governance Framework

Automating discrepancy detection through daily validation scripts is essential for data reliability, but **automated resolution (auto-fixing) based purely on tolerance thresholds introduces severe operational and financial risks**. Manual human investigation is indispensable for the following four reasons:

### 1. Tolerance Thresholds Catch Divergence, Not Correctness
- **Divergence vs. Truth:** A tolerance check only evaluates whether two computational engines (e.g., SQL query vs. Python script) produce results within an arbitrary numerical delta ($\le 0.1\%$). It does **not** evaluate whether either result reflects business reality or accurate logic.
- **Risk of Overwriting Truth:** If Python contains a logic bug (e.g., failing to filter refunded orders) and SQL contains correct business logic, automatically syncing SQL to match Python would overwrite a valid metric with erroneous logic simply because the threshold was exceeded.

### 2. Risk of Creeping Drift (Unnoticed Systemic Degradation)
- **Compounding Errors:** Small inaccuracies (e.g., $0.08\%$ daily difference) fall below a $0.1\%$ tolerance threshold and go unflagged. Over weeks or months, these small variances accumulate (creeping drift), distorting quarterly financial models and executive dashboards without ever triggering an automated alert.
- **Threshold Gaming:** Relying on auto-fixing can mask underlying data pipeline issues (such as delayed CDC events, unhandled timezone shifts, or floating-point rounding mismatches) by continually patching outputs rather than resolving upstream data degradation.

### 3. Manual Review Ensures Selection of the "Correct" Definition
- **Disambiguating Business Intent:** When SQL and Python disagree (e.g., SQL counting churn as 50 vs. Python counting 68 due to year-boundary stripping in `MONTH()`), an algorithm cannot discern which layer embodies the authorized definition. 
- **Domain Context Required:** Human investigation determines whether the discrepancy stems from an SQL query syntax error, a Pandas timezone handling difference, NULL propagation differences, or an unannounced schema migration in the data warehouse.

### 4. Root Cause Understanding Prevents Future Recurrence
- **Fixing Symptoms vs. Resolving Root Causes:** Auto-fixing merely masks the symptom at execution time (e.g., overriding values). It leaves broken SQL views, faulty ETL transformations, or flawed downstream scripts active in production.
- **Preventative Engineering:** Manual root cause analysis identifies the exact technical flaw (e.g., replacing `MONTH()` with explicit ISO date ranges), allowing engineers to commit structural fixes to version control, update unit test suites, and prevent systemic metric divergence permanently across all business dashboards.

---

## Summary Matrix

| Metric Drift Approach | Immediate Action | Correctness Assurance | Long-Term Reliability | Risk Level |
| :--- | :--- | :--- | :--- | :--- |
| **Auto-Fixing on Threshold** | Overwrites code/data blindly | ❌ Low (may enforce false values) | ❌ Poor (hides root causes & creeping drift) | 🔴 High |
| **Automated Alert + Manual Investigation** | Flags discrepancy & alerts team | ✅ High (human verifies ground truth) | ✅ Excellent (fixes underlying pipeline code) | 🟢 Low |
