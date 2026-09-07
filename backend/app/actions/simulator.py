"""What-If scenario simulation engine."""

from app.schemas.actions import (
    WhatIfSimulationRequest,
    WhatIfSimulationResponse,
)
from app.schemas.analytics import FullAnalyticsReport
from app.schemas.ml import CustomerChurnResponse


def run_scenario_simulation(
    analytics: FullAnalyticsReport,
    params: WhatIfSimulationRequest,
    churn: CustomerChurnResponse | None = None,
) -> WhatIfSimulationResponse:
    """Simulate business performance outcomes under hypothetical commercial parameters."""
    current_rev = analytics.kpis.total_revenue
    base_margin_pct = 0.40  # 40% estimated baseline gross margin
    current_margin = round(current_rev * base_margin_pct, 2)

    vol_mult = 1.0 + (params.revenue_growth_pct / 100.0)
    price_mult = 1.0 + (params.price_change_pct / 100.0)
    disc_mult = 1.0 - (params.discount_change_pct / 100.0)

    # Churn recovery
    recovered_churn = 0.0
    if churn and churn.high_risk_revenue_at_stake > 0:
        recovered_churn = round(churn.high_risk_revenue_at_stake * (params.churn_reduction_pct / 100.0), 2)

    simulated_rev = round((current_rev * vol_mult * price_mult * disc_mult) + recovered_churn, 2)
    rev_delta = round(simulated_rev - current_rev, 2)
    rev_delta_pct = round((rev_delta / current_rev * 100), 2) if current_rev > 0 else 0.0

    # Margin impact
    margin_shift = (params.price_change_pct * 0.005) - (params.discount_change_pct * 0.005)
    simulated_margin_pct = max(0.10, min(0.80, base_margin_pct + margin_shift))
    simulated_margin = round(simulated_rev * simulated_margin_pct, 2)
    margin_delta = round(simulated_margin - current_margin, 2)

    # Narrative insights
    insights = []
    if rev_delta > 0:
        insights.append(f"Projected to unlock +${rev_delta:,.2f} (+{rev_delta_pct}%) in total sales revenue.")
    elif rev_delta < 0:
        insights.append(f"Simulated contraction of -${abs(rev_delta):,.2f} ({rev_delta_pct}%) in revenue.")

    if recovered_churn > 0:
        insights.append(f"Recovers ${recovered_churn:,.2f} from previously lapsing customers.")

    if margin_delta > 0:
        insights.append(f"Estimated gross profit expands by +${margin_delta:,.2f}.")

    return WhatIfSimulationResponse(
        current_revenue=current_rev,
        simulated_revenue=simulated_rev,
        revenue_delta=rev_delta,
        revenue_delta_pct=rev_delta_pct,
        current_margin_estimate=current_margin,
        simulated_margin_estimate=simulated_margin,
        margin_delta=margin_delta,
        recovered_churn_revenue=recovered_churn,
        insights=insights,
    )
