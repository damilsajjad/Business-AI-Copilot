"""Pydantic schemas for Action Items, Recommendations, and What-If Simulations."""

from pydantic import BaseModel


class ActionItem(BaseModel):
    """Actionable recommendation with priority, impact, effort, and step checklist."""

    id: str
    title: str
    domain: str  # "sales", "products", "customers", "inventory"
    urgency: str  # "high", "medium", "low"
    expected_impact: str
    effort: str  # "low", "medium", "high"
    timeframe: str  # "immediate", "1-2 weeks", "30 days"
    action_steps: list[str]
    owner: str
    risk_if_ignored: str
    status: str = "pending"  # "pending", "in_progress", "completed", "dismissed"


class WhatIfSimulationRequest(BaseModel):
    """Parameters for What-If scenario simulation."""

    revenue_growth_pct: float = 0.0
    price_change_pct: float = 0.0
    discount_change_pct: float = 0.0
    churn_reduction_pct: float = 0.0


class WhatIfSimulationResponse(BaseModel):
    """Simulation outcomes across revenue, margin, and recovered churn."""

    current_revenue: float
    simulated_revenue: float
    revenue_delta: float
    revenue_delta_pct: float
    current_margin_estimate: float
    simulated_margin_estimate: float
    margin_delta: float
    recovered_churn_revenue: float
    insights: list[str]
