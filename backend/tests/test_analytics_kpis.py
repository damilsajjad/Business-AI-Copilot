"""Tests for deterministic KPI calculation against exact verified dataset values."""

import pandas as pd

from app.analytics.kpis import calculate_kpis


def test_calculate_kpis_known_dataset():
    """Verify KPI calculations on a fixed dataset with manually calculated ground truth."""
    data = [
        {"order_id": "ORD-1", "order_date": "2024-01-01", "customer_id": "C1", "product_name": "Widget A", "quantity": 2, "total_revenue": 100.0},
        {"order_id": "ORD-2", "order_date": "2024-01-02", "customer_id": "C2", "product_name": "Widget B", "quantity": 1, "total_revenue": 50.0},
        {"order_id": "ORD-3", "order_date": "2024-01-03", "customer_id": "C1", "product_name": "Widget A", "quantity": 3, "total_revenue": 150.0},
        {"order_id": "ORD-4", "order_date": "2024-01-10", "customer_id": "C3", "product_name": "Widget C", "quantity": 4, "total_revenue": 200.0},
    ]

    df = pd.DataFrame(data)
    df["order_date"] = pd.to_datetime(df["order_date"])

    kpis = calculate_kpis(df)

    # Ground truth verifications:
    # Total revenue = 100 + 50 + 150 + 200 = 500.0
    assert kpis.total_revenue == 500.0
    # Total orders = 4
    assert kpis.total_orders == 4
    # Total units = 2 + 1 + 3 + 4 = 10
    assert kpis.total_units == 10
    # Unique customers = C1, C2, C3 = 3
    assert kpis.unique_customers == 3
    # Unique products = Widget A, Widget B, Widget C = 3
    assert kpis.unique_products == 3
    # AOV = 500 / 4 = 125.0
    assert kpis.average_order_value == 125.0
    # Date range = 2024-01-01 to 2024-01-10 (10 days)
    assert kpis.start_date == "2024-01-01"
    assert kpis.end_date == "2024-01-10"
    assert kpis.total_days == 10
    # Revenue per day = 500 / 10 = 50.0
    assert kpis.revenue_per_day == 50.0


def test_calculate_kpis_empty_dataframe():
    """Empty dataframe should safely return zeroed KPIs without crashing."""
    df = pd.DataFrame()
    kpis = calculate_kpis(df)

    assert kpis.total_revenue == 0.0
    assert kpis.total_orders == 0
    assert kpis.total_units == 0
    assert kpis.average_order_value == 0.0
    assert kpis.total_days == 0
