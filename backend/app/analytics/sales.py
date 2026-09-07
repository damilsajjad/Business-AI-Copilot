"""Sales trend, growth rate, and time-series anomaly detection engine."""

import numpy as np
import pandas as pd

from app.schemas.analytics import (
    SalesAnalytics,
    SalesAnomaly,
    TimeSeriesPoint,
)


def _aggregate_time_series(df: pd.DataFrame, freq: str) -> list[TimeSeriesPoint]:
    """Aggregate revenue, order counts, and units by a pandas period frequency."""
    if df.empty:
        return []

    # Create period column
    if freq == "D":
        periods = df["order_date"].dt.strftime("%Y-%m-%d")
    elif freq == "W":
        periods = df["order_date"].dt.to_period("W").astype(str)
    elif freq == "M":
        periods = df["order_date"].dt.to_period("M").astype(str)
    else:
        periods = df["order_date"].dt.strftime("%Y-%m-%d")

    grouped = df.groupby(periods).agg(
        revenue=("total_revenue", "sum"),
        orders=("order_id", "nunique"),
        units=("quantity", "sum"),
    ).reset_index()

    grouped.columns = ["period", "revenue", "orders", "units"]
    grouped["revenue"] = grouped["revenue"].round(2)

    points = []
    for _, row in grouped.iterrows():
        orders = int(row["orders"])
        rev = float(row["revenue"])
        aov = round(rev / orders, 2) if orders > 0 else 0.0
        points.append(
            TimeSeriesPoint(
                period=str(row["period"]),
                revenue=rev,
                orders=orders,
                units=int(row["units"]),
                aov=aov,
            )
        )

    return points


def _detect_sales_anomalies(df: pd.DataFrame) -> list[SalesAnomaly]:
    """Detect statistical spikes and dips in daily revenue using z-scores."""
    if len(df) < 14:
        return []

    daily = df.groupby(df["order_date"].dt.strftime("%Y-%m-%d"))["total_revenue"].sum().reset_index()
    daily.columns = ["date", "revenue"]

    mean_rev = daily["revenue"].mean()
    std_rev = daily["revenue"].std()

    if std_rev == 0 or np.isnan(std_rev):
        return []

    anomalies: list[SalesAnomaly] = []

    for _, row in daily.iterrows():
        rev = float(row["revenue"])
        z = (rev - mean_rev) / std_rev
        dev_pct = round(((rev - mean_rev) / mean_rev) * 100, 1) if mean_rev > 0 else 0.0

        if z >= 2.2:
            anomalies.append(
                SalesAnomaly(
                    date=str(row["date"]),
                    revenue=round(rev, 2),
                    expected_revenue=round(mean_rev, 2),
                    type="spike",
                    z_score=round(z, 2),
                    deviation_pct=dev_pct,
                )
            )
        elif z <= -2.0 and mean_rev > 0:
            anomalies.append(
                SalesAnomaly(
                    date=str(row["date"]),
                    revenue=round(rev, 2),
                    expected_revenue=round(mean_rev, 2),
                    type="dip",
                    z_score=round(z, 2),
                    deviation_pct=dev_pct,
                )
            )

    return anomalies


def calculate_sales_analytics(df: pd.DataFrame) -> SalesAnalytics:
    """Compute time-series trends, month-over-month growth, and anomalies."""
    if df.empty:
        return SalesAnalytics(
            monthly_trends=[],
            weekly_trends=[],
            daily_trends=[],
            mom_growth_rate_pct=None,
            best_month=None,
            worst_month=None,
            anomalies=[],
        )

    monthly_points = _aggregate_time_series(df, "M")
    weekly_points = _aggregate_time_series(df, "W")
    daily_points = _aggregate_time_series(df, "D")

    # MoM Growth rate
    mom_growth: float | None = None
    best_month: str | None = None
    worst_month: str | None = None

    if len(monthly_points) >= 2:
        revs = [p.revenue for p in monthly_points]
        changes = []
        for i in range(1, len(revs)):
            prev = revs[i - 1]
            curr = revs[i]
            if prev > 0:
                changes.append((curr - prev) / prev * 100)

        if changes:
            mom_growth = round(float(np.mean(changes)), 2)

    if monthly_points:
        sorted_months = sorted(monthly_points, key=lambda p: p.revenue, reverse=True)
        best_month = sorted_months[0].period
        worst_month = sorted_months[-1].period

    anomalies = _detect_sales_anomalies(df)

    return SalesAnalytics(
        monthly_trends=monthly_points,
        weekly_trends=weekly_points,
        daily_trends=daily_points,
        mom_growth_rate_pct=mom_growth,
        best_month=best_month,
        worst_month=worst_month,
        anomalies=anomalies,
    )
