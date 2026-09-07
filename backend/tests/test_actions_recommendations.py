"""Tests for strategic action recommendation generator."""

from app.actions.recommendations import generate_action_recommendations
from app.analytics.engine import run_deterministic_analytics
from app.data.synthetic_data import generate_retail_dataset
from app.ml.churn import calculate_customer_churn_risk
from app.ml.forecasting import generate_sales_forecast


def test_action_recommendations_generation():
    """Verify that action recommendations contain concrete steps, owners, and impacts."""
    df = generate_retail_dataset(num_orders=100)
    analytics = run_deterministic_analytics(df, "file-1", "biz-1")
    forecast = generate_sales_forecast(df, "file-1", "biz-1")
    churn = calculate_customer_churn_risk(df, "file-1", "biz-1")

    actions = generate_action_recommendations(analytics, forecast, churn)

    assert len(actions) >= 3
    for act in actions:
        assert act.id is not None
        assert act.title != ""
        assert act.urgency in ["high", "medium", "low"]
        assert act.effort in ["low", "medium", "high"]
        assert len(act.action_steps) >= 2
        assert act.owner != ""
        assert act.status == "pending"
