"""Full End-to-End Integration Journey Test for AI Business Copilot."""

from uuid import uuid4

import pytest

from app.actions.exporter import generate_executive_markdown_report
from app.actions.recommendations import generate_action_recommendations
from app.actions.simulator import run_scenario_simulation
from app.agents.copilot import answer_copilot_query
from app.agents.orchestrator import run_multi_agent_synthesis
from app.analytics.engine import run_deterministic_analytics
from app.data.synthetic_data import generate_retail_dataset
from app.ml.churn import calculate_customer_churn_risk
from app.ml.forecasting import generate_sales_forecast
from app.schemas.actions import WhatIfSimulationRequest
from app.schemas.agents import ChatMessage
from app.schemas.mapping import ColumnMappingItem
from app.services.mapping_validator import validate_mapping
from app.services.profiler import profile_dataset


@pytest.mark.asyncio
async def test_full_business_copilot_e2e_journey():
    """Verify the complete user journey from raw data to exportable executive intelligence."""
    file_id = str(uuid4())
    business_id = str(uuid4())

    # 1. Ingest realistic retail dataset
    df = generate_retail_dataset(num_orders=120)
    assert len(df) == 120

    # 2. Profile the dataset
    profile = profile_dataset(
        file_id=file_id,
        file_name="retail_sales.csv",
        sheets_dict={"Sheet1": df},
    )
    assert profile.sheets[0].row_count == 120
    assert len(profile.sheets[0].columns) >= 5

    # 3. Schema Mapping & Validation
    mapping_items = [
        ColumnMappingItem(target_field="order_date", source_sheet="Sheet1", source_column="order_date"),
        ColumnMappingItem(target_field="total_revenue", source_sheet="Sheet1", source_column="total_revenue"),
        ColumnMappingItem(target_field="order_id", source_sheet="Sheet1", source_column="order_id"),
        ColumnMappingItem(target_field="customer_id", source_sheet="Sheet1", source_column="customer_id"),
        ColumnMappingItem(target_field="product_name", source_sheet="Sheet1", source_column="product_name"),
        ColumnMappingItem(target_field="category", source_sheet="Sheet1", source_column="category"),
        ColumnMappingItem(target_field="quantity", source_sheet="Sheet1", source_column="quantity"),
    ]
    val_res = validate_mapping(mapping_items, profile)
    assert val_res.is_valid is True
    assert len(val_res.errors) == 0

    # 4. Deterministic Analytics Engine
    analytics = run_deterministic_analytics(df, file_id, business_id)
    assert analytics.kpis.total_revenue > 0
    assert analytics.kpis.total_orders == 120
    assert analytics.kpis.average_order_value > 0
    assert len(analytics.sales.monthly_trends) >= 1
    assert len(analytics.products.top_products) >= 1
    assert analytics.customers is not None

    # 5. Machine Learning Forecasting
    forecast = generate_sales_forecast(df, file_id, business_id)
    assert len(forecast.horizon_30_days) == 30
    assert len(forecast.horizon_60_days) == 60
    assert len(forecast.horizon_90_days) == 90
    assert forecast.metrics.mape >= 0.0

    # 6. Customer Churn Risk Scoring
    churn = calculate_customer_churn_risk(df, file_id, business_id)
    assert churn.total_customers_evaluated > 0
    assert churn.high_risk_revenue_at_stake >= 0.0

    # 7. Multi-Agent AI Core Synthesis
    brief = await run_multi_agent_synthesis(
        analytics=analytics,
        forecast=forecast,
        churn=churn,
    )
    assert brief.health_score >= 0 and brief.health_score <= 100
    assert len(brief.domain_insights) >= 3
    assert len(brief.key_risks) >= 1

    # 8. Interactive Copilot Chat
    history = [ChatMessage(role="user", content="What was our total revenue?")]
    copilot_res = await answer_copilot_query(
        query="What was our total revenue and what is our best selling product?",
        history=history,
        analytics=analytics,
        forecast=forecast,
        churn=churn,
    )
    assert "$" in copilot_res.reply
    assert len(copilot_res.cited_metrics) >= 1

    # 9. Action Engine Recommendations
    actions = generate_action_recommendations(analytics, forecast, churn)
    assert len(actions) >= 3
    for act in actions:
        assert act.status == "pending"
        assert len(act.action_steps) >= 2

    # 10. Commercial What-If Scenario Sandbox
    sim_params = WhatIfSimulationRequest(
        revenue_growth_pct=15.0,
        price_change_pct=5.0,
        discount_change_pct=-2.0,
        churn_reduction_pct=25.0,
    )
    sim = run_scenario_simulation(analytics, sim_params, churn)
    assert sim.simulated_revenue > analytics.kpis.total_revenue
    assert sim.revenue_delta > 0
    assert len(sim.insights) > 0

    # 11. Markdown Executive Brief Export
    md_report = generate_executive_markdown_report(
        analytics=analytics,
        forecast=forecast,
        churn=churn,
        brief=brief,
        actions=actions,
        business_name="Apex Retail Co.",
    )
    assert "Executive Business Intelligence Brief" in md_report
    assert "Apex Retail Co." in md_report
    assert f"${analytics.kpis.total_revenue:,.2f}" in md_report
    assert "Recommended Action Initiatives" in md_report
