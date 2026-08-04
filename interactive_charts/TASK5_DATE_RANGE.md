# Task 5 — Plotly Date Range Slider

## Question

You have a time-series Plotly chart showing revenue by week. How can you add a date range slider so users can select which weeks to view, such as only Q1 2024?

## Answer

Plotly provides a `rangeslider` on the x-axis that allows users to
drag the handles and select a custom date range.

It can be combined with a `rangeselector`, which provides predefined
buttons such as 1 Month, 3 Months, 6 Months, and All.

### Date Range Slider Example

```python
fig.update_xaxes(
    rangeselector=dict(
        buttons=[
            dict(
                count=1,
                label="1M",
                step="month",
                stepmode="backward"
            ),
            dict(
                count=3,
                label="3M",
                step="month",
                stepmode="backward"
            ),
            dict(
                count=6,
                label="6M",
                step="month",
                stepmode="backward"
            ),
            dict(
                step="all",
                label="All"
            )
        ]
    ),
    rangeslider=dict(
        visible=True
    )
)