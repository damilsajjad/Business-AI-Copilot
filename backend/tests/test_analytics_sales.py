"""Tests for time-series sales trend and anomaly calculations."""

import pandas as pd

from app.analytics.sales import calculate_sales_analytics


def test_sales_trends_monthly_aggregation():
    """Verify monthly aggregation and MoM growth rate calculation on known dataset."""
    records = [
        # January: Total $300 across 2 orders
        {"order_id": "ORD-1", "order_date": "2024-01-05", "quantity": 2, "total_revenue": 100.0},
        {"order_id": "ORD-2", "order_date": "2024-01-15", "quantity": 1, "total_revenue": 200.0},
        # February: Total $600 across 2 orders (+100% MoM growth)
        {"order_id": "ORD-3", "order_date": "2024-02-10", "quantity": 3, "total_revenue": 300.0},
        {"order_id": "ORD-4", "order_date": "2024-02-20", "quantity": 3, "total_revenue": 300.0},
        # March: Total $450 across 1 order (-25% MoM growth)
        {"order_id": "ORD-5", "order_date": "2024-03-01", "quantity": 5, "total_revenue": 450.0},
    ]

    df = pd.DataFrame(records)
    df["order_date"] = pd.to_datetime(df["order_date"])

    sales = calculate_sales_analytics(df)

    assert len(sales.monthly_trends) == 3

    # Check January: 300.0, 2 orders
    assert sales.monthly_trends[0].period == "2024-01"
    assert sales.monthly_trends[0].revenue == 300.0
    assert sales.monthly_trends[0].orders == 2

    # Check February: 600.0, 2 orders
    assert sales.monthly_trends[1].period == "2024-02"
    assert sales.monthly_trends[1].revenue == 600.0

    # Best and worst months
    assert sales.best_month == "2024-02"
    assert sales.worst_month == "2024-01"

    # MoM Average Growth: (100% + (-25%)) / 2 = 37.5%
    assert sales.mom_growth_rate_pct == 37.5


def test_sales_anomaly_detection():
    """Verify that a massive outlier day is detected as a spike anomaly."""
    # 20 regular days with $100 daily revenue
    records = []
    for day in range(1, 21):
        records.append({
            "order_id": f"ORD-{day}",
            "order_date": f"2024-01-{day:02d}",
            "quantity": 1,
            "total_revenue": 100.0,
        })

    # Day 21 with a massive spike of $2000
    records.append({
        "order_id": "ORD-21",
        "order_date": "2024-01-21",
        "quantity": 20,
        "total_revenue": 2000.0,
    })

    df = pd.DataFrame(records)
    df["order_date"] = pd.to_datetime(df["order_date"])

    sales = calculate_sales_analytics(df)

    assert len(sales.anomalies) >= 1
    spike = sales.anomalies[0]
    assert spike.date == "2024-01-21"
    assert spike.type == "spike"
    assert spike.revenue == 2000.0
    assert spike.z_score > 2.0
