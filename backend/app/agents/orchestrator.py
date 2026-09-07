"""Multi-Agent AI synthesis orchestrator grounded in deterministic metrics."""

import json
import os
from datetime import UTC, datetime

import httpx

from app.agents.prompts import EXECUTIVE_SYSTEM_PROMPT
from app.schemas.agents import DomainInsight, ExecutiveBriefReport
from app.schemas.analytics import FullAnalyticsReport
from app.schemas.ml import CustomerChurnResponse, SalesForecastResponse


def _synthesize_deterministic_brief(
    analytics: FullAnalyticsReport,
    forecast: SalesForecastResponse | None,
    churn: CustomerChurnResponse | None,
) -> ExecutiveBriefReport:
    """Generate verified, grounded executive brief using deterministic rules and calculations."""
    kpis = analytics.kpis
    sales = analytics.sales
    products = analytics.products
    customers = analytics.customers
    demand = analytics.demand

    # 1. Calculate holistic Business Health Score (0-100)
    score = 70

    # Sales growth impact
    if sales.mom_growth_rate_pct is not None:
        if sales.mom_growth_rate_pct > 10:
            score += 10
        elif sales.mom_growth_rate_pct < -10:
            score -= 15

    # Concentration risk impact
    if products.top_3_products_revenue_share_pct > 70:
        score -= 10
    elif products.top_3_products_revenue_share_pct < 40:
        score += 5

    # Customer repeat rate impact
    if customers:
        if customers.repeat_rate_pct > 40:
            score += 10
        elif customers.repeat_rate_pct < 15:
            score -= 10

    # Churn impact
    if churn and churn.average_churn_risk > 0.5:
        score -= 10

    health_score = max(20, min(95, score))

    # 2. Build Domain Insights
    domain_insights: list[DomainInsight] = []

    # Domain: Sales
    sales_positives = [
        f"Generated ${kpis.total_revenue:,.2f} across {kpis.total_orders} verified orders",
        f"Average daily run-rate of ${kpis.revenue_per_day:,.2f}",
    ]
    if sales.best_month:
        sales_positives.append(f"Peak monthly performance achieved in {sales.best_month}")

    sales_concerns = []
    if sales.anomalies:
        sales_concerns.append(f"Detected {len(sales.anomalies)} statistical revenue anomalies requiring review")
    if sales.mom_growth_rate_pct is not None and sales.mom_growth_rate_pct < 0:
        sales_concerns.append(f"Average Month-over-Month revenue contracted by {abs(sales.mom_growth_rate_pct)}%")

    domain_insights.append(
        DomainInsight(
            domain="sales",
            headline=f"Total Revenue of ${kpis.total_revenue:,.2f} with {kpis.total_orders} orders.",
            summary=f"The business generated an Average Order Value of ${kpis.average_order_value:.2f} across {kpis.total_days} active operational days.",
            key_metrics={
                "total_revenue": kpis.total_revenue,
                "aov": kpis.average_order_value,
                "mom_growth_rate": sales.mom_growth_rate_pct,
            },
            positives=sales_positives,
            concerns=sales_concerns,
        )
    )

    # Domain: Products
    prod_positives = [
        f"Catalog contains {kpis.unique_products} active products across {len(products.category_breakdown)} categories",
    ]
    if products.top_products:
        prod_positives.append(f"Top performing product '{products.top_products[0].product_name}' contributes {products.top_products[0].revenue_share_pct}% of sales")

    prod_concerns = []
    if products.top_3_products_revenue_share_pct > 65:
        prod_concerns.append(f"High product concentration: Top 3 products generate {products.top_3_products_revenue_share_pct}% of total revenue")

    domain_insights.append(
        DomainInsight(
            domain="products",
            headline=f"{len(products.top_products)} top products driving primary revenue.",
            summary=f"Top 3 products account for {products.top_3_products_revenue_share_pct}% of sales across {len(products.category_breakdown)} categories.",
            key_metrics={
                "unique_products": kpis.unique_products,
                "top_3_concentration_pct": products.top_3_products_revenue_share_pct,
            },
            positives=prod_positives,
            concerns=prod_concerns,
        )
    )

    # Domain: Customers & Churn
    if customers:
        cust_positives = [
            f"Active customer base of {customers.total_customers} distinct buyers",
            f"Repeat buyer rate of {customers.repeat_rate_pct}% ({customers.repeat_customers} returning customers)",
        ]
        cust_concerns = []
        if churn and churn.high_risk_count > 0:
            cust_concerns.append(f"{churn.high_risk_count} customers at high risk of churn (${churn.high_risk_revenue_at_stake:,.2f} revenue at stake)")

        domain_insights.append(
            DomainInsight(
                domain="customers",
                headline=f"Customer repeat rate stands at {customers.repeat_rate_pct}%.",
                summary=f"Top 10% highest spenders generate {customers.top_10_pct_revenue_share_pct}% of total business revenue.",
                key_metrics={
                    "total_customers": customers.total_customers,
                    "repeat_rate_pct": customers.repeat_rate_pct,
                    "high_risk_churn_revenue": churn.high_risk_revenue_at_stake if churn else 0.0,
                },
                positives=cust_positives,
                concerns=cust_concerns,
            )
        )

    # Domain: Demand
    if demand:
        domain_insights.append(
            DomainInsight(
                domain="demand",
                headline=f"Average sales velocity of {demand.average_daily_units} units per day.",
                summary=f"Identified {len(demand.fast_moving_products)} fast-moving SKUs requiring proactive inventory replenishment.",
                key_metrics={"daily_units_sold": demand.average_daily_units},
                positives=[f"{len(demand.fast_moving_products)} high-velocity SKUs with steady turnover"],
                concerns=[f"{len(demand.slow_moving_products)} slow-moving products tying up working capital"] if demand.slow_moving_products else [],
            )
        )

    # 3. Synthesize Key Risks, Opportunities, and Initiatives
    key_risks = []
    if products.top_3_products_revenue_share_pct > 60:
        key_risks.append(f"Revenue Dependency: Top 3 products represent {products.top_3_products_revenue_share_pct}% of total sales.")
    if churn and churn.high_risk_count > 0:
        key_risks.append(f"Customer Churn Exposure: ${churn.high_risk_revenue_at_stake:,.2f} in historical revenue is at high risk of lapsing.")
    if not key_risks:
        key_risks.append("Operational pacing: Monitor inventory stock levels against seasonal sales fluctuations.")

    opportunities = [
        f"Increase AOV: Current Average Order Value of ${kpis.average_order_value:.2f} can be expanded via bundling with high-margin items.",
        "Re-engagement Campaign: Target inactive buyers with personalized incentive offers to improve repeat purchase frequency.",
    ]
    if forecast and forecast.projected_growth_pct > 0:
        opportunities.append(f"Capitalize on positive momentum: Projections estimate {forecast.projected_growth_pct}% growth over next 30 days.")

    recommended_initiatives = [
        "Deploy automated win-back discount emails to inactive repeat customers.",
        f"Diversify product catalog promotions to reduce {products.top_3_products_revenue_share_pct}% top-3 SKU concentration.",
        "Establish minimum safety stock thresholds for top 5 fast-moving inventory items.",
    ]

    exec_summary = (
        f"Overall business performance is rated at a Health Score of {health_score}/100. "
        f"Total verified revenue is ${kpis.total_revenue:,.2f} with an AOV of ${kpis.average_order_value:.2f}. "
        f"Core growth priorities should focus on mitigating product concentration risk and re-engaging high-value customers."
    )

    return ExecutiveBriefReport(
        file_id=analytics.file_id,
        business_id=analytics.business_id,
        generated_at=datetime.now(UTC),
        executive_summary=exec_summary,
        health_score=health_score,
        domain_insights=domain_insights,
        key_risks=key_risks,
        strategic_opportunities=opportunities,
        recommended_initiatives=recommended_initiatives,
        synthesized_by="Deterministic Multi-Agent Synthesis",
    )


async def run_multi_agent_synthesis(
    analytics: FullAnalyticsReport,
    forecast: SalesForecastResponse | None = None,
    churn: CustomerChurnResponse | None = None,
) -> ExecutiveBriefReport:
    """Orchestrate domain agents to generate executive brief with LLM or deterministic fallback."""
    api_key = os.environ.get("GEMINI_API_KEY")

    # If no API key is provided, execute deterministic synthesis
    if not api_key:
        return _synthesize_deterministic_brief(analytics, forecast, churn)

    # If API key is available, call Gemini to enrich the synthesis
    try:
        context_data = {
            "kpis": analytics.kpis.model_dump(),
            "sales": {
                "best_month": analytics.sales.best_month,
                "worst_month": analytics.sales.worst_month,
                "mom_growth_pct": analytics.sales.mom_growth_rate_pct,
                "anomaly_count": len(analytics.sales.anomalies),
            },
            "products": {
                "top_products": [p.model_dump() for p in analytics.products.top_products[:5]],
                "top_3_share_pct": analytics.products.top_3_products_revenue_share_pct,
            },
            "customers": analytics.customers.model_dump() if analytics.customers else None,
            "forecast_30d": forecast.projected_30d_revenue if forecast else None,
            "churn_revenue_at_stake": churn.high_risk_revenue_at_stake if churn else None,
        }

        prompt = f"""{EXECUTIVE_SYSTEM_PROMPT}

Verified Business Facts:
{json.dumps(context_data, indent=2)}

Generate a JSON object matching this schema:
{{
  "health_score": <number 0-100>,
  "executive_summary": "<string>",
  "key_risks": ["<string>", "<string>"],
  "strategic_opportunities": ["<string>", "<string>"],
  "recommended_initiatives": ["<string>", "<string>"]
}}"""

        async with httpx.AsyncClient(timeout=25.0) as client:
            resp = await client.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}",
                json={
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {"response_mime_type": "application/json"},
                },
            )

            if resp.status_code == 200:
                data = resp.json()
                text_content = data["candidates"][0]["content"]["parts"][0]["text"]
                parsed = json.loads(text_content)

                # Combine LLM executive summary with deterministic domain breakdowns
                base_brief = _synthesize_deterministic_brief(analytics, forecast, churn)
                base_brief.health_score = int(parsed.get("health_score", base_brief.health_score))
                base_brief.executive_summary = str(parsed.get("executive_summary", base_brief.executive_summary))
                if parsed.get("key_risks"):
                    base_brief.key_risks = parsed["key_risks"]
                if parsed.get("strategic_opportunities"):
                    base_brief.strategic_opportunities = parsed["strategic_opportunities"]
                if parsed.get("recommended_initiatives"):
                    base_brief.recommended_initiatives = parsed["recommended_initiatives"]
                base_brief.synthesized_by = "Gemini Flash Multi-Agent Synthesis"
                return base_brief

    except Exception:
        # Fallback to deterministic synthesis on any LLM error
        pass

    return _synthesize_deterministic_brief(analytics, forecast, churn)
