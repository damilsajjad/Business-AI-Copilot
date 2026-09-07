"""Tests for multi-agent executive brief synthesis."""

import pytest

from app.agents.orchestrator import run_multi_agent_synthesis
from app.analytics.engine import run_deterministic_analytics
from app.data.synthetic_data import generate_retail_dataset
from app.ml.churn import calculate_customer_churn_risk
from app.ml.forecasting import generate_sales_forecast


@pytest.mark.asyncio
async def test_multi_agent_synthesis_generation():
    """Verify that multi-agent synthesis computes a complete executive brief."""
    df = generate_retail_dataset(num_orders=100)
    analytics = run_deterministic_analytics(df, "file-123", "biz-123")
    forecast = generate_sales_forecast(df, "file-123", "biz-123")
    churn = calculate_customer_churn_risk(df, "file-123", "biz-123")

    brief = await run_multi_agent_synthesis(analytics, forecast, churn)

    assert brief.file_id == "file-123"
    assert brief.business_id == "biz-123"
    assert 0 <= brief.health_score <= 100
    assert len(brief.executive_summary) > 20
    assert len(brief.domain_insights) >= 3
    assert len(brief.key_risks) > 0
    assert len(brief.strategic_opportunities) > 0
    assert len(brief.recommended_initiatives) > 0

    # Verify domain names
    domains = [d.domain for d in brief.domain_insights]
    assert "sales" in domains
    assert "products" in domains
