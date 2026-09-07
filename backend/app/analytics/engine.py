"""Master deterministic analytics engine orchestrator."""

from datetime import UTC, datetime

import pandas as pd

from app.analytics.customers import calculate_customer_analytics
from app.analytics.demand import calculate_demand_analytics
from app.analytics.kpis import calculate_kpis
from app.analytics.products import calculate_product_analytics
from app.analytics.sales import calculate_sales_analytics
from app.schemas.analytics import FullAnalyticsReport


def run_deterministic_analytics(
    df: pd.DataFrame,
    file_id: str,
    business_id: str,
) -> FullAnalyticsReport:
    """Run full deterministic analytics pipeline on normalized canonical data."""
    if not df.empty and "order_date" in df.columns and not pd.api.types.is_datetime64_any_dtype(df["order_date"]):
        df = df.copy()
        df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")

    kpis = calculate_kpis(df)
    sales = calculate_sales_analytics(df)
    products = calculate_product_analytics(df)
    customers = calculate_customer_analytics(df)
    demand = calculate_demand_analytics(df)

    capabilities = ["data_overview", "sales_analysis", "product_analysis"]

    if customers is not None:
        capabilities.append("customer_analysis")
        if customers.total_customers >= 5 and customers.repeat_customers >= 2:
            capabilities.append("churn_risk_analysis")

    if demand is not None:
        capabilities.append("demand_analysis")

    # Forecasting capability check
    if kpis.total_days >= 30 and len(sales.monthly_trends) >= 2:
        capabilities.append("sales_forecasting")

    return FullAnalyticsReport(
        file_id=file_id,
        business_id=business_id,
        generated_at=datetime.now(UTC),
        kpis=kpis,
        sales=sales,
        products=products,
        customers=customers,
        demand=demand,
        available_capabilities=capabilities,
    )
