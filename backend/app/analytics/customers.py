"""Deterministic customer retention and lifetime spend analytics engine."""

import pandas as pd

from app.schemas.analytics import (
    CustomerAnalytics,
    CustomerSpendItem,
)


def calculate_customer_analytics(df: pd.DataFrame) -> CustomerAnalytics | None:
    """Compute customer retention, repeat purchase rate, and spend concentration."""
    if df.empty or "customer_id" not in df.columns:
        return None

    valid_customers = df[df["customer_id"].notna() & (df["customer_id"] != "Unknown Customer") & (df["customer_id"] != "")]
    if valid_customers.empty or valid_customers["customer_id"].nunique() < 2:
        return None

    total_revenue = float(df["total_revenue"].sum())

    grouped = valid_customers.groupby("customer_id").agg(
        total_spend=("total_revenue", "sum"),
        order_count=("order_id", "nunique") if "order_id" in df.columns else ("total_revenue", "count"),
    ).reset_index()

    total_customers = len(grouped)
    repeat_customers = int((grouped["order_count"] > 1).sum())
    repeat_rate = round((repeat_customers / total_customers * 100), 2) if total_customers > 0 else 0.0

    customer_items = []
    for _, row in grouped.iterrows():
        spend = round(float(row["total_spend"]), 2)
        orders = int(row["order_count"])
        aov = round(spend / orders, 2) if orders > 0 else 0.0

        customer_items.append(
            CustomerSpendItem(
                customer_id=str(row["customer_id"]),
                total_spend=spend,
                order_count=orders,
                average_order_value=aov,
            )
        )

    sorted_customers = sorted(customer_items, key=lambda c: c.total_spend, reverse=True)
    top_customers = sorted_customers[:10]

    # Top 10% customer spend share
    top_10_pct_count = max(1, int(total_customers * 0.10))
    top_10_pct_spend = sum(c.total_spend for c in sorted_customers[:top_10_pct_count])
    top_10_pct_share = round((top_10_pct_spend / total_revenue * 100), 2) if total_revenue > 0 else 0.0

    return CustomerAnalytics(
        total_customers=total_customers,
        repeat_customers=repeat_customers,
        repeat_rate_pct=repeat_rate,
        top_customers=top_customers,
        top_10_pct_revenue_share_pct=top_10_pct_share,
    )
