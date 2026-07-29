"""
KPI Package Init
Allows direct imports like: `from kpis.kpi_functions import calculate_mau`
or `from kpis import calculate_mau, calculate_revenue_per_customer, calculate_churn_rate`
"""

from .kpi_functions import (
    calculate_mau,
    calculate_revenue_per_customer,
    calculate_churn_rate,
    calculate_payment_success_rate,
    calculate_customer_acquisition_cost,
    calculate_total_revenue
)
from .kpi_decomposition import decompose_revenue

__all__ = [
    'calculate_mau',
    'calculate_revenue_per_customer',
    'calculate_churn_rate',
    'calculate_payment_success_rate',
    'calculate_customer_acquisition_cost',
    'calculate_total_revenue',
    'decompose_revenue'
]
