"""Tests for What-If scenario simulation engine."""

from app.actions.simulator import run_scenario_simulation
from app.analytics.engine import run_deterministic_analytics
from app.data.synthetic_data import generate_retail_dataset
from app.ml.churn import calculate_customer_churn_risk
from app.schemas.actions import WhatIfSimulationRequest


def test_scenario_simulation_growth_and_price_increase():
    """Verify that a 10% volume increase and 5% price increase produce expected revenue gains."""
    df = generate_retail_dataset(num_orders=50)
    analytics = run_deterministic_analytics(df, "file-1", "biz-1")
    churn = calculate_customer_churn_risk(df, "file-1", "biz-1")

    base_rev = analytics.kpis.total_revenue
    params = WhatIfSimulationRequest(
        revenue_growth_pct=10.0,
        price_change_pct=5.0,
        discount_change_pct=0.0,
        churn_reduction_pct=20.0,
    )

    sim = run_scenario_simulation(analytics, params, churn)

    assert sim.current_revenue == base_rev
    assert sim.simulated_revenue > base_rev
    assert sim.revenue_delta > 0
    assert sim.simulated_margin_estimate > sim.current_margin_estimate
    assert len(sim.insights) > 0
