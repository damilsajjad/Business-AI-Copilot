"""Tests for customer churn risk scoring and RFM calculations."""

import pandas as pd

from app.ml.churn import calculate_customer_churn_risk
from app.ml.guardrails import check_churn_feasibility


def test_churn_guardrail_on_single_customer():
    """Datasets with 1 customer cannot be meaningfully scored for churn."""
    data = [
        {"customer_id": "C1", "order_date": "2024-01-01", "total_revenue": 100.0},
        {"customer_id": "C1", "order_date": "2024-01-02", "total_revenue": 100.0},
    ]
    df = pd.DataFrame(data)
    df["order_date"] = pd.to_datetime(df["order_date"])

    guard = check_churn_feasibility(df)
    assert not guard.is_feasible
    assert "Insufficient customer base" in guard.reason


def test_churn_risk_evaluation_on_known_customers():
    """Verify churn risk tiers and high-risk identification."""
    data = [
        # Customer Inactive: Last bought 100 days ago, 1 order ($50) -> High churn risk
        {"order_id": "O1", "customer_id": "InactiveCust", "order_date": "2024-01-01", "total_revenue": 50.0},
        # Customer Active: Last bought 2 days ago, 5 orders ($500) -> Low churn risk
        {"order_id": "O2", "customer_id": "ActiveCust", "order_date": "2024-04-10", "total_revenue": 100.0},
        {"order_id": "O3", "customer_id": "ActiveCust", "order_date": "2024-04-15", "total_revenue": 100.0},
        {"order_id": "O4", "customer_id": "ActiveCust", "order_date": "2024-04-20", "total_revenue": 100.0},
        {"order_id": "O5", "customer_id": "ActiveCust", "order_date": "2024-04-25", "total_revenue": 100.0},
        {"order_id": "O6", "customer_id": "ActiveCust", "order_date": "2024-04-28", "total_revenue": 100.0},
        # Customer Moderate: Last bought 35 days ago, 2 orders ($200) -> Medium churn risk
        {"order_id": "O7", "customer_id": "ModCust", "order_date": "2024-03-01", "total_revenue": 100.0},
        {"order_id": "O8", "customer_id": "ModCust", "order_date": "2024-03-25", "total_revenue": 100.0},
    ]

    df = pd.DataFrame(data)
    df["order_date"] = pd.to_datetime(df["order_date"])

    churn = calculate_customer_churn_risk(df, "file-1", "biz-1")

    assert churn.status == "success"
    assert churn.total_customers_evaluated == 3

    # InactiveCust should have higher churn risk than ActiveCust
    inactive_item = next(c for c in churn.customers if c.customer_id == "InactiveCust")
    active_item = next(c for c in churn.customers if c.customer_id == "ActiveCust")

    assert inactive_item.churn_risk_score > active_item.churn_risk_score
    assert inactive_item.risk_tier == "high"
    assert active_item.risk_tier == "low"
    assert len(inactive_item.risk_factors) > 0
