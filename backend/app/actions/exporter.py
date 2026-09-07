"""Executive Brief Markdown and summary report exporter."""

from app.schemas.actions import ActionItem
from app.schemas.agents import ExecutiveBriefReport
from app.schemas.analytics import FullAnalyticsReport
from app.schemas.ml import CustomerChurnResponse, SalesForecastResponse


def generate_executive_markdown_report(
    business_name: str,
    analytics: FullAnalyticsReport,
    brief: ExecutiveBriefReport,
    actions: list[ActionItem],
    forecast: SalesForecastResponse | None = None,
    churn: CustomerChurnResponse | None = None,
) -> str:
    """Generate comprehensive, beautifully formatted Markdown executive briefing report."""
    kpis = analytics.kpis
    products = analytics.products
    customers = analytics.customers

    md = []
    md.append(f"# Executive Business Intelligence Brief — {business_name}")
    md.append(f"**Generated:** {brief.generated_at.strftime('%Y-%m-%d %H:%M UTC')} | **Overall Health Score:** {brief.health_score}/100\n")

    md.append("## 1. Executive Summary")
    md.append(f"{brief.executive_summary}\n")

    md.append("## 2. Core Business Performance Metrics (Ground Truth)")
    md.append(f"- **Total Verified Revenue:** ${kpis.total_revenue:,.2f}")
    md.append(f"- **Total Orders:** {kpis.total_orders:,}")
    md.append(f"- **Average Order Value (AOV):** ${kpis.average_order_value:.2f}")
    md.append(f"- **Units Sold:** {kpis.total_units:,} across {kpis.unique_products} active SKUs")
    md.append(f"- **Daily Revenue Run-Rate:** ${kpis.revenue_per_day:,.2f}/day")
    md.append(f"- **Reporting Period:** {kpis.start_date} to {kpis.end_date} ({kpis.total_days} days)\n")

    md.append("## 3. Top Performing Products")
    md.append("| Product Name | Category | Total Revenue | Units Sold | Share % |")
    md.append("| :--- | :--- | :--- | :--- | :--- |")
    for p in products.top_products[:5]:
        md.append(f"| {p.product_name} | {p.category or 'General'} | ${p.total_revenue:,.2f} | {p.total_quantity:,} | {p.revenue_share_pct}% |")
    md.append(f"\n*Top 3 products generate **{products.top_3_products_revenue_share_pct}%** of total sales.*\n")

    if customers:
        md.append("## 4. Customer Retention & Churn Risk")
        md.append(f"- **Total Unique Buyers:** {customers.total_customers}")
        md.append(f"- **Repeat Customer Rate:** {customers.repeat_rate_pct}% ({customers.repeat_customers} returning)")
        md.append(f"- **Top 10% Spender Share:** {customers.top_10_pct_revenue_share_pct}% of total revenue")
        if churn:
            md.append(f"- **Customers at High Churn Risk:** {churn.high_risk_count} (${churn.high_risk_revenue_at_stake:,.2f} revenue at stake)\n")

    if forecast and forecast.status == "success":
        md.append("## 5. Machine Learning Sales Forecast")
        md.append(f"- **30-Day Projected Revenue:** ${forecast.projected_30d_revenue:,.2f} ({'+' if forecast.projected_growth_pct >= 0 else ''}{forecast.projected_growth_pct}%)")
        md.append(f"- **60-Day Projected Revenue:** ${forecast.projected_60d_revenue:,.2f}")
        md.append(f"- **90-Day Projected Revenue:** ${forecast.projected_90d_revenue:,.2f}")
        md.append(f"- **Model Accuracy:** MAPE {forecast.metrics.mape}% (Trained on {forecast.metrics.training_days} days)\n")

    md.append("## 6. Strategic Risks & Opportunities")
    md.append("### Critical Risks")
    for r in brief.key_risks:
        md.append(f"- ⚠️ {r}")
    md.append("\n### High-Value Opportunities")
    for o in brief.strategic_opportunities:
        md.append(f"- 🚀 {o}")
    md.append("")

    md.append("## 7. Recommended Action Initiatives")
    for idx, act in enumerate(actions, 1):
        md.append(f"### Initiative {idx}: {act.title} [{act.urgency.upper()} PRIORITY]")
        md.append(f"- **Impact:** {act.expected_impact}")
        md.append(f"- **Effort & Timeframe:** {act.effort.capitalize()} effort • {act.timeframe}")
        md.append(f"- **Owner:** {act.owner}")
        md.append("- **Action Checklist:**")
        for step in act.action_steps:
            md.append(f"  - [ ] {step}")
        if act.risk_if_ignored:
            md.append(f"- **Risk if Ignored:** {act.risk_if_ignored}")
        md.append("")

    return "\n".join(md)
