"""Tests for time-series ML sales forecasting engine."""

import pandas as pd

from app.data.synthetic_data import generate_retail_dataset
from app.ml.forecasting import generate_sales_forecast
from app.ml.guardrails import check_forecasting_feasibility


def test_forecast_guardrail_on_empty_or_sparse_data():
    """Guardrail should catch datasets with insufficient history."""
    empty_df = pd.DataFrame()
    guard = check_forecasting_feasibility(empty_df)
    assert not guard.is_feasible

    sparse_df = pd.DataFrame([
        {"order_date": "2024-01-01", "total_revenue": 100.0},
        {"order_date": "2024-01-02", "total_revenue": 200.0},
    ])
    sparse_df["order_date"] = pd.to_datetime(sparse_df["order_date"])
    guard2 = check_forecasting_feasibility(sparse_df)
    assert not guard2.is_feasible
    assert "Insufficient" in guard2.reason


def test_forecast_generation_on_retail_dataset():
    """Verify 30, 60, and 90 day projections on synthetic retail data."""
    df = generate_retail_dataset(num_orders=150)
    df["order_date"] = pd.to_datetime(df["order_date"])

    res = generate_sales_forecast(df, "file-123", "biz-123")

    assert res.status == "success"
    assert len(res.horizon_30_days) == 30
    assert len(res.horizon_60_days) == 60
    assert len(res.horizon_90_days) == 90

    # Projected totals must be positive and non-decreasing across horizons
    assert res.projected_30d_revenue > 0
    assert res.projected_60d_revenue >= res.projected_30d_revenue
    assert res.projected_90d_revenue >= res.projected_60d_revenue

    # Each forecast point must have valid bounds: lower <= predicted <= upper
    for pt in res.horizon_30_days:
        assert pt.lower_bound <= pt.predicted_revenue
        assert pt.predicted_revenue <= pt.upper_bound
        assert pt.lower_bound >= 0.0

    # Model metrics must be populated
    assert res.metrics.training_days > 0
    assert res.metrics.forecast_horizon_days == 90
