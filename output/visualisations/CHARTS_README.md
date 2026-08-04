# BeyondClicks Business Visualisations

## Overview

These visualisations apply business visualisation principles to the
BeyondClicks marketing campaign dataset.

The visualisations use the feature-engineered dataset containing
55,555 campaign records and 23 columns.

---

## Chart 1: Revenue by Campaign Type

- **Type:** Horizontal Bar Chart
- **Business Question:** Which campaign type generates the most revenue?
- **Data:** Campaign_Type and Revenue
- **Purpose:** Compare total revenue across different campaign types.
- **Annotation:** Highlights the campaign type with the highest revenue.

A bar chart was selected because campaign types are discrete categories
and the objective is to compare their revenue values.

---

## Chart 2: Monthly Revenue Trend

- **Type:** Line Chart
- **Business Question:** How is campaign revenue changing over time?
- **Data:** Date and Revenue
- **Purpose:** Identify revenue growth, declines, peaks, and changes over time.
- **Annotation:** Highlights the peak revenue month.
- **Reference Line:** Average monthly revenue.

A line chart was selected because Date is a continuous time dimension
and the objective is to identify trends.

---

## Chart 3: Revenue Distribution

- **Type:** Histogram
- **Business Question:** How is revenue distributed across campaigns?
- **Data:** Revenue
- **Purpose:** Understand typical campaign revenue and the spread of values.
- **Annotation:** Shows the mean revenue.
- **Reference Line:** Mean campaign revenue.

A histogram was selected because the objective is to understand the
distribution of a numerical variable.

---

## Chart 4: Quarterly Revenue Composition

- **Type:** Stacked Bar Chart
- **Business Question:** How is quarterly revenue composed of different
  campaign types?
- **Data:** Date, Campaign_Type, Revenue
- **Purpose:** Compare total quarterly revenue while showing the contribution
  of each campaign type.
- **Annotation:** Highlights the quarter with the highest total revenue.

A stacked bar chart was selected because it shows both total revenue and
the composition of that revenue by campaign type.

---

## Chart 5: Acquisition Cost vs Revenue

- **Type:** Scatter Plot
- **Business Question:** Is higher acquisition cost associated with higher
  campaign revenue?
- **Data:** Acquisition_Cost and Revenue
- **Purpose:** Explore the relationship between campaign spending and revenue.
- **Annotation:** Displays the calculated correlation coefficient.
- **Trend Line:** Shows the overall relationship between acquisition cost
  and revenue.

A scatter plot was selected because the objective is to investigate the
relationship between two numerical variables.

---

# Complete Labelling

Every chart includes:

- Descriptive title
- X-axis label
- Y-axis label
- Appropriate units
- Legend where multiple series are present
- Data labels where appropriate
- Annotation or reference line

The labels are designed so that each chart can be understood without
additional explanation.

---

# Consistent Colour Palette

The project uses a common colour palette:

- **Blue (#1f77b4):** Primary campaign data
- **Orange (#ff7f0e):** Secondary distribution/comparison
- **Green (#2ca02c):** Positive/reference information
- **Red (#d62728):** Warnings, trend lines, or important references
- **Purple (#9467bd):** Additional campaign category

The same palette is reused across the visualisations to create a
consistent visual language.

---

# Annotations

Each visualisation contains at least one annotation or reference:

1. **Revenue by Campaign Type**
   - Highest-revenue campaign type

2. **Monthly Revenue Trend**
   - Peak revenue month
   - Average revenue reference line

3. **Revenue Distribution**
   - Mean campaign revenue

4. **Quarterly Revenue Composition**
   - Highest-revenue quarter

5. **Acquisition Cost vs Revenue**
   - Correlation coefficient and trend line

Annotations were added to direct attention toward important patterns
rather than simply displaying raw data.

---

# Accessibility

Colour is not the only way information is communicated.

The charts also use:

- Text labels
- Axis labels
- Legends
- Different chart structures
- Dashed reference lines
- Trend lines
- Annotations

This helps reduce dependence on colour alone and improves readability
for users with colour vision deficiencies.

---

# Output

All charts are exported as PNG files at 300 DPI for clear presentation
and submission.