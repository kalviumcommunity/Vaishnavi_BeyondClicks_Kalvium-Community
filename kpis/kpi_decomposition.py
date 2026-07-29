"""
KPI Decomposition Module
Decomposes top-level KPIs into sub-component hierarchies (Segment and Product levels)
and verifies sum math across levels.
"""

import pandas as pd


def decompose_revenue(df):
    """
    Decomposes Total Monthly Revenue and Revenue per Customer across:
    Level 1: Top-level metric
    Level 2: Customer Segment level (Enterprise, SMB, Startup)
    Level 3: Product level within Customer Segment
    
    Parameters:
        df (pd.DataFrame): Dataframe containing 'amount', 'customer_type', 'product', and 'customer_id'.
        
    Returns:
        dict: Detailed breakdown dictionary and text report.
    """
    if df.empty:
        return {"error": "DataFrame is empty"}

    # Level 1: Top-Level Revenue & Customers
    total_revenue = df['amount'].sum()
    total_unique_customers = df['customer_id'].nunique()
    overall_rpc = total_revenue / total_unique_customers if total_unique_customers > 0 else 0

    # Level 2: Breakdown by Customer Segment
    revenue_by_segment = df.groupby('customer_type')['amount'].sum().to_dict()
    customers_by_segment = df.groupby('customer_type')['customer_id'].nunique().to_dict()
    
    rpc_by_segment = {
        seg: (revenue_by_segment[seg] / customers_by_segment[seg]) if customers_by_segment.get(seg, 0) > 0 else 0
        for seg in revenue_by_segment
    }

    # Level 3: Breakdown by Customer Segment and Product
    segment_product_breakdown = df.groupby(['customer_type', 'product'])['amount'].sum().unstack(fill_value=0)

    # Verification: Components sum to Total
    segment_sum = sum(revenue_by_segment.values())
    is_sum_valid = abs(total_revenue - segment_sum) < 1e-5

    report = f"""
================================================================================
KPI DECOMPOSITION REPORT: Total Monthly Revenue & Revenue per Customer
================================================================================

Level 1 (Top-Level Overall Metrics):
------------------------------------
  Total Revenue:        ${total_revenue:,.2f}
  Unique Customers:     {total_unique_customers:,}
  Revenue per Customer: ${overall_rpc:,.2f}

Level 2 (By Customer Segment):
------------------------------------
  Enterprise:           ${revenue_by_segment.get('Enterprise', 0):,.2f} ({customers_by_segment.get('Enterprise', 0)} customers, RPC: ${rpc_by_segment.get('Enterprise', 0):,.2f})
  SMB:                  ${revenue_by_segment.get('SMB', 0):,.2f} ({customers_by_segment.get('SMB', 0)} customers, RPC: ${rpc_by_segment.get('SMB', 0):,.2f})
  Startup:              ${revenue_by_segment.get('Startup', 0):,.2f} ({customers_by_segment.get('Startup', 0)} customers, RPC: ${rpc_by_segment.get('Startup', 0):,.2f})

Level 3 (Product Breakdown within Segment):
------------------------------------
{segment_product_breakdown.to_string()}

Mathematical Consistency Verification:
------------------------------------
  Sum of Segment Revenues:  ${segment_sum:,.2f}
  Top-Level Total Revenue:  ${total_revenue:,.2f}
  Verification Status:      {'[PASS] (Components sum to total)' if is_sum_valid else '[FAIL]'}
================================================================================
"""
    
    return {
        'total_revenue': total_revenue,
        'revenue_by_segment': revenue_by_segment,
        'customers_by_segment': customers_by_segment,
        'rpc_by_segment': rpc_by_segment,
        'segment_product_breakdown': segment_product_breakdown,
        'is_sum_valid': is_sum_valid,
        'report_text': report
    }
