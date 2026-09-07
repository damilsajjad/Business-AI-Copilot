"""Deterministic KPI calculation engine."""

import pandas as pd

from app.schemas.analytics import KPISummary


def calculate_kpis(df: pd.DataFrame) -> KPISummary:
    """Calculate summary business KPIs from a normalized canonical DataFrame."""
    if df.empty:
        return KPISummary(
            total_revenue=0.0,
            total_orders=0,
            total_units=0,
            unique_customers=0,
            unique_products=0,
            average_order_value=0.0,
            revenue_per_day=0.0,
            start_date="",
            end_date="",
            total_days=0,
        )

    total_revenue = round(float(df["total_revenue"].sum()), 2)
    total_orders = int(df["order_id"].nunique()) if "order_id" in df.columns else len(df)
    total_units = int(df["quantity"].sum()) if "quantity" in df.columns else len(df)
    unique_customers = int(df["customer_id"].nunique()) if "customer_id" in df.columns else 0
    unique_products = int(df["product_name"].nunique()) if "product_name" in df.columns else 0

    aov = round(total_revenue / total_orders, 2) if total_orders > 0 else 0.0

    min_date = df["order_date"].min()
    max_date = df["order_date"].max()

    start_date_str = min_date.strftime("%Y-%m-%d") if pd.notna(min_date) else ""
    end_date_str = max_date.strftime("%Y-%m-%d") if pd.notna(max_date) else ""

    if pd.notna(min_date) and pd.notna(max_date):
        total_days = max((max_date - min_date).days + 1, 1)
    else:
        total_days = 1

    revenue_per_day = round(total_revenue / total_days, 2) if total_days > 0 else total_revenue

    return KPISummary(
        total_revenue=total_revenue,
        total_orders=total_orders,
        total_units=total_units,
        unique_customers=unique_customers,
        unique_products=unique_products,
        average_order_value=aov,
        revenue_per_day=revenue_per_day,
        start_date=start_date_str,
        end_date=end_date_str,
        total_days=total_days,
    )
