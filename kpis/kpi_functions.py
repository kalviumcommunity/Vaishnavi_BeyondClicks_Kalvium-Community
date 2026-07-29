"""
KPI Computation Module
Provides reusable functions to compute key performance indicators from dataframes.
"""

import pandas as pd
import numpy as np


def _ensure_datetime(df, date_col='transaction_date'):
    """Helper to ensure date column is datetime object."""
    if date_col in df.columns:
        if not pd.api.types.is_datetime64_any_dtype(df[date_col]):
            df = df.copy()
            df[date_col] = pd.to_datetime(df[date_col])
    return df


def calculate_mau(df, days=30, reference_date=None, formatted=False):
    """
    Monthly Active Users: distinct customers active in last N days.
    
    Parameters:
        df (pd.DataFrame): Dataframe containing 'customer_id' and 'transaction_date'.
        days (int): Number of days lookback window.
        reference_date (pd.Timestamp, optional): Anchor timestamp (defaults to current time).
        formatted (bool): If True, returns formatted string (e.g., "5,500").
        
    Returns:
        int or str: Number of distinct active users in period.
    """
    if df.empty or 'customer_id' not in df.columns or 'transaction_date' not in df.columns:
        val = 0
    else:
        df_clean = _ensure_datetime(df, 'transaction_date')
        now = reference_date if reference_date is not None else pd.Timestamp.now()
        cutoff = now - pd.Timedelta(days=days)
        val = df_clean[df_clean['transaction_date'] >= cutoff]['customer_id'].nunique()

    if formatted:
        return f"{val:,}"
    return int(val)


def calculate_revenue_per_customer(df, formatted=False):
    """
    Average revenue per unique customer.
    
    Parameters:
        df (pd.DataFrame): Dataframe containing 'amount' and 'customer_id'.
        formatted (bool): If True, returns formatted currency string (e.g., "$95.50").
        
    Returns:
        float or str: Revenue per customer.
    """
    if df.empty or 'amount' not in df.columns or 'customer_id' not in df.columns:
        val = 0.0
    else:
        unique_customers = df['customer_id'].nunique()
        val = (df['amount'].sum() / unique_customers) if unique_customers > 0 else 0.0

    if formatted:
        return f"${val:,.2f}"
    return float(val)


def calculate_churn_rate(df, period_days=30, reference_date=None, formatted=False):
    """
    Churn Rate: Customers who had activity in period 1 but none in period 2.
    
    Parameters:
        df (pd.DataFrame): Dataframe containing 'customer_id' and 'transaction_date'.
        period_days (int): Length of each observation period in days.
        reference_date (pd.Timestamp, optional): Anchor timestamp (defaults to current time).
        formatted (bool): If True, returns formatted percentage string (e.g., "3.5%").
        
    Returns:
        float or str: Churn rate as a decimal (0.0 - 1.0) or formatted string.
    """
    if df.empty or 'customer_id' not in df.columns or 'transaction_date' not in df.columns:
        val = 0.0
    else:
        df_clean = _ensure_datetime(df, 'transaction_date')
        now = reference_date if reference_date is not None else pd.Timestamp.now()
        period_2_start = now - pd.Timedelta(days=period_days)
        period_2_end = now
        period_1_end = period_2_start
        period_1_start = period_1_end - pd.Timedelta(days=period_days)

        active_p1 = df_clean[(df_clean['transaction_date'] >= period_1_start) & 
                             (df_clean['transaction_date'] <= period_1_end)]['customer_id'].unique()
        active_p2 = df_clean[(df_clean['transaction_date'] >= period_2_start) & 
                             (df_clean['transaction_date'] <= period_2_end)]['customer_id'].unique()

        churned = len([x for x in active_p1 if x not in active_p2])
        val = churned / len(active_p1) if len(active_p1) > 0 else 0.0

    if formatted:
        return f"{val:.1%}"
    return float(val)


def calculate_payment_success_rate(df, status_col='status', success_val='SUCCESS', formatted=False):
    """
    Payment Success Rate: Ratio of successful transactions to total payment transactions.
    
    Parameters:
        df (pd.DataFrame): Dataframe containing transaction status.
        status_col (str): Column indicating payment status.
        success_val (str): Value signifying a successful transaction.
        formatted (bool): If True, returns formatted percentage string (e.g., "98.0%").
        
    Returns:
        float or str: Payment success rate as decimal.
    """
    if df.empty or status_col not in df.columns:
        val = 0.0
    else:
        total = len(df)
        successful = len(df[df[status_col] == success_val])
        val = successful / total if total > 0 else 0.0

    if formatted:
        return f"{val:.1%}"
    return float(val)


def calculate_customer_acquisition_cost(spend_data, new_customers=None, formatted=False):
    """
    Customer Acquisition Cost (CAC): Total marketing spend divided by new customers acquired.
    
    Parameters:
        spend_data (float, int, or pd.DataFrame): Total marketing spend amount or DataFrame with spend column.
        new_customers (int, optional): Count of new customers (if spend_data is numeric).
        formatted (bool): If True, returns formatted currency string (e.g., "$35.00").
        
    Returns:
        float or str: CAC value.
    """
    if isinstance(spend_data, (pd.DataFrame, pd.Series)):
        spend_col = 'spend' if 'spend' in spend_data.columns else spend_data.columns[0]
        total_spend = spend_data[spend_col].sum()
        if new_customers is None and 'new_customer_id' in spend_data.columns:
            new_customers = spend_data['new_customer_id'].nunique()
    else:
        total_spend = float(spend_data)

    count = new_customers if new_customers and new_customers > 0 else 1
    val = total_spend / count if count > 0 else 0.0

    if formatted:
        return f"${val:,.2f}"
    return float(val)


def calculate_total_revenue(df, amount_col='amount', formatted=False):
    """
    Total Revenue: Sum of all revenue amounts.
    
    Parameters:
        df (pd.DataFrame): Dataframe containing amount column.
        amount_col (str): Column name for amount.
        formatted (bool): If True, returns formatted currency string.
        
    Returns:
        float or str: Total revenue value.
    """
    if df.empty or amount_col not in df.columns:
        val = 0.0
    else:
        val = float(df[amount_col].sum())

    if formatted:
        return f"${val:,.2f}"
    return val
