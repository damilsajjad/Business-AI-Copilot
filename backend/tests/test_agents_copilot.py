"""Tests for AI Business Copilot conversational Q&A grounding."""

import pytest

from app.agents.copilot import answer_copilot_query
from app.analytics.engine import run_deterministic_analytics
from app.data.synthetic_data import generate_retail_dataset
from app.ml.forecasting import generate_sales_forecast


@pytest.mark.asyncio
async def test_copilot_answers_revenue_query():
    """Verify that Copilot quotes exact total revenue from analytics."""
    df = generate_retail_dataset(num_orders=50)
    analytics = run_deterministic_analytics(df, "file-1", "biz-1")
    forecast = generate_sales_forecast(df, "file-1", "biz-1")

    res = await answer_copilot_query(
        query="What is our total revenue so far?",
        history=[],
        analytics=analytics,
        forecast=forecast,
        churn=None,
    )

    assert res.reply is not None
    assert f"${analytics.kpis.total_revenue:,.2f}" in res.reply
    assert "total_revenue" in res.cited_metrics


@pytest.mark.asyncio
async def test_copilot_answers_product_performance():
    """Verify that Copilot cites top products and concentration shares."""
    df = generate_retail_dataset(num_orders=50)
    analytics = run_deterministic_analytics(df, "file-1", "biz-1")

    res = await answer_copilot_query(
        query="Which products are selling the most?",
        history=[],
        analytics=analytics,
        forecast=None,
        churn=None,
    )

    assert res.reply is not None
    top_prod = analytics.products.top_products[0].product_name
    assert top_prod in res.reply
    assert len(res.suggested_follow_ups) > 0
