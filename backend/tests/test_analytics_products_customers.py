"""Tests for product, customer, and demand analytics engines."""

import pandas as pd

from app.analytics.customers import calculate_customer_analytics
from app.analytics.demand import calculate_demand_analytics
from app.analytics.products import calculate_product_analytics


def test_product_performance_and_category_shares():
    """Verify product ranking, share percentages, and category totals on known data."""
    data = [
        {"order_id": "O1", "product_name": "Laptop", "product_id": "P1", "category": "Electronics", "quantity": 1, "total_revenue": 1000.0},
        {"order_id": "O2", "product_name": "Mouse", "product_id": "P2", "category": "Electronics", "quantity": 2, "total_revenue": 50.0},
        {"order_id": "O3", "product_name": "Desk Lamp", "product_id": "P3", "category": "Home", "quantity": 1, "total_revenue": 50.0},
    ]
    df = pd.DataFrame(data)
    df["order_date"] = pd.to_datetime("2024-01-01")

    products = calculate_product_analytics(df)

    # Total revenue = $1100
    assert len(products.top_products) == 3
    # Top product is Laptop with $1000 (1000/1100 = 90.91%)
    assert products.top_products[0].product_name == "Laptop"
    assert products.top_products[0].total_revenue == 1000.0
    assert products.top_products[0].revenue_share_pct == 90.91

    # Category breakdown: Electronics ($1050), Home ($50)
    assert len(products.category_breakdown) == 2
    assert products.category_breakdown[0].category == "Electronics"
    assert products.category_breakdown[0].total_revenue == 1050.0
    assert products.category_breakdown[1].category == "Home"
    assert products.category_breakdown[1].total_revenue == 50.0


def test_customer_repeat_rate_and_spend():
    """Verify customer repeat purchase rates and top customer identification."""
    data = [
        # Customer C1 makes 3 orders ($300 total) -> Repeat
        {"order_id": "O1", "customer_id": "C1", "order_date": "2024-01-01", "total_revenue": 100.0},
        {"order_id": "O2", "customer_id": "C1", "order_date": "2024-01-05", "total_revenue": 100.0},
        {"order_id": "O3", "customer_id": "C1", "order_date": "2024-01-10", "total_revenue": 100.0},
        # Customer C2 makes 1 order ($50 total) -> One-time
        {"order_id": "O4", "customer_id": "C2", "order_date": "2024-01-02", "total_revenue": 50.0},
        # Customer C3 makes 2 orders ($200 total) -> Repeat
        {"order_id": "O5", "customer_id": "C3", "order_date": "2024-01-03", "total_revenue": 100.0},
        {"order_id": "O6", "customer_id": "C3", "order_date": "2024-01-08", "total_revenue": 100.0},
        # Customer C4 makes 1 order ($50 total) -> One-time
        {"order_id": "O7", "customer_id": "C4", "order_date": "2024-01-04", "total_revenue": 50.0},
    ]
    df = pd.DataFrame(data)
    df["order_date"] = pd.to_datetime(df["order_date"])

    customers = calculate_customer_analytics(df)
    assert customers is not None

    # Total customers = 4 (C1, C2, C3, C4)
    assert customers.total_customers == 4
    # Repeat customers = 2 (C1, C3)
    assert customers.repeat_customers == 2
    # Repeat rate = 2 / 4 = 50.0%
    assert customers.repeat_rate_pct == 50.0

    # Top customer is C1 ($300 spend across 3 orders)
    assert customers.top_customers[0].customer_id == "C1"
    assert customers.top_customers[0].total_spend == 300.0
    assert customers.top_customers[0].order_count == 3


def test_demand_velocity_and_tiers():
    """Verify inventory demand velocity (units per day) across a 10-day period."""
    data = [
        # Product Fast: 20 units over 10 days -> 2.0 units/day -> "fast"
        {"order_id": "O1", "product_name": "Fast Item", "order_date": "2024-01-01", "quantity": 10},
        {"order_id": "O2", "product_name": "Fast Item", "order_date": "2024-01-10", "quantity": 10},
        # Product Slow: 1 unit over 10 days -> 0.1 units/day -> "slow"
        {"order_id": "O3", "product_name": "Slow Item", "order_date": "2024-01-05", "quantity": 1},
    ]
    df = pd.DataFrame(data)
    df["order_date"] = pd.to_datetime(df["order_date"])

    demand = calculate_demand_analytics(df)
    assert demand is not None

    assert len(demand.fast_moving_products) == 1
    assert demand.fast_moving_products[0].product_name == "Fast Item"
    assert demand.fast_moving_products[0].units_per_day == 2.0
    assert demand.fast_moving_products[0].velocity_tier == "fast"

    assert len(demand.slow_moving_products) == 1
    assert demand.slow_moving_products[0].product_name == "Slow Item"
    assert demand.slow_moving_products[0].units_per_day == 0.1
    assert demand.slow_moving_products[0].velocity_tier == "slow"
