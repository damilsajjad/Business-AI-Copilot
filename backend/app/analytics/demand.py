"""Deterministic inventory demand velocity analytics engine."""

import pandas as pd

from app.schemas.analytics import (
    DemandAnalytics,
    DemandItem,
)


def calculate_demand_analytics(df: pd.DataFrame) -> DemandAnalytics | None:
    """Compute product velocity rates (units/day) and categorize into velocity tiers."""
    if df.empty or "quantity" not in df.columns or "product_name" not in df.columns:
        return None

    min_date = df["order_date"].min()
    max_date = df["order_date"].max()

    if pd.isna(min_date) or pd.isna(max_date):
        total_days = 1
    else:
        total_days = max((max_date - min_date).days + 1, 1)

    grouped = df.groupby("product_name").agg(
        category=("category", "first") if "category" in df.columns else ("product_name", lambda x: "General"),
        total_units=("quantity", "sum"),
    ).reset_index()

    items: list[DemandItem] = []
    for _, row in grouped.iterrows():
        units = int(row["total_units"])
        daily_vel = round(units / total_days, 3)

        if daily_vel >= 1.0:
            tier = "fast"
        elif daily_vel >= 0.25:
            tier = "medium"
        else:
            tier = "slow"

        items.append(
            DemandItem(
                product_name=str(row["product_name"]),
                category=str(row["category"]),
                total_units=units,
                units_per_day=daily_vel,
                velocity_tier=tier,
            )
        )

    sorted_by_vel = sorted(items, key=lambda d: d.units_per_day, reverse=True)
    fast_moving = [item for item in sorted_by_vel if item.velocity_tier == "fast"]
    slow_moving = sorted([item for item in sorted_by_vel if item.velocity_tier == "slow"], key=lambda d: d.units_per_day)

    total_units_sum = sum(i.total_units for i in items)
    avg_daily_units = round(total_units_sum / total_days, 2)

    return DemandAnalytics(
        fast_moving_products=fast_moving[:10],
        slow_moving_products=slow_moving[:10],
        average_daily_units=avg_daily_units,
    )
