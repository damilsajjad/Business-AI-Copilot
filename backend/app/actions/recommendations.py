"""Strategic action recommendation generator."""

from uuid import uuid4

from app.schemas.actions import ActionItem
from app.schemas.analytics import FullAnalyticsReport
from app.schemas.ml import CustomerChurnResponse, SalesForecastResponse


def generate_action_recommendations(
    analytics: FullAnalyticsReport,
    forecast: SalesForecastResponse | None = None,
    churn: CustomerChurnResponse | None = None,
) -> list[ActionItem]:
    """Generate prioritized actionable initiatives based on business data facts."""
    kpis = analytics.kpis
    products = analytics.products
    demand = analytics.demand
    items: list[ActionItem] = []

    # 1. Customer Win-Back / Retention Initiative
    if churn and churn.high_risk_count > 0:
        items.append(
            ActionItem(
                id=str(uuid4()),
                title=f"Deploy Win-Back Campaign for {churn.high_risk_count} Churn-Risk Buyers",
                domain="customers",
                urgency="high",
                expected_impact=f"Recover up to ${churn.high_risk_revenue_at_stake:,.2f} in historical revenue",
                effort="low",
                timeframe="1-2 weeks",
                action_steps=[
                    f"Segment the {churn.high_risk_count} customers inactive for >60 days.",
                    "Deploy an automated 3-part email sequence featuring a personalized 15% incentive code.",
                    "Trigger a direct follow-up for top 5 lifetime spenders.",
                ],
                owner="Growth & Marketing Lead",
                risk_if_ignored=f"Permanent loss of ${churn.high_risk_revenue_at_stake:,.2f} in customer lifetime value.",
            )
        )
    else:
        items.append(
            ActionItem(
                id=str(uuid4()),
                title="Launch Automated Post-Purchase Customer Retention Flow",
                domain="customers",
                urgency="medium",
                expected_impact="Boost repeat purchase rate by 15-20% within 60 days",
                effort="low",
                timeframe="1-2 weeks",
                action_steps=[
                    "Implement a day-7 post-delivery check-in and satisfaction review email.",
                    "Send a day-21 personalized cross-sell offer with a 10% returning buyer discount.",
                    "Enroll purchasers into a VIP early-access product tier.",
                ],
                owner="Customer Success Lead",
                risk_if_ignored="Under-monetizing existing customer acquisition spend.",
            )
        )

    # 2. Product Concentration & Bundling
    top_name = products.top_products[0].product_name if products.top_products else "Top SKU"
    items.append(
        ActionItem(
            id=str(uuid4()),
            title=f"Cross-Sell Bundling to Balance Catalog Mix ('{top_name}')",
            domain="products",
            urgency="medium",
            expected_impact="Increase Average Order Value by 8-12% and balance revenue mix",
            effort="medium",
            timeframe="30 days",
            action_steps=[
                f"Create complementary bundle packages combining '{top_name}' with secondary catalog items.",
                "Introduce a 10% bundle discount on the checkout page.",
                "Feature rising product categories on top navigation and promotional banners.",
            ],
            owner="Product Merchandising Lead",
            risk_if_ignored=f"High vulnerability to supply disruptions on top 3 products generating {products.top_3_products_revenue_share_pct}% of sales.",
        )
    )

    # 3. Inventory Stockout Prevention & Velocity Optimization
    if demand and demand.fast_moving_products:
        fast_names = ", ".join([p.product_name for p in demand.fast_moving_products[:2]])
        items.append(
            ActionItem(
                id=str(uuid4()),
                title=f"Safety Stock Rebalancing for High-Velocity SKUs ({fast_names})",
                domain="inventory",
                urgency="high",
                expected_impact="Eliminate stockout loss and maintain daily sales velocity",
                effort="low",
                timeframe="Immediate",
                action_steps=[
                    f"Audit current stock on hand for top velocity items: {fast_names}.",
                    "Set minimum reorder points based on daily velocity run-rate.",
                    "Establish a 14-day supplier lead-time buffer to prevent out-of-stock events.",
                ],
                owner="Operations & Logistics Lead",
                risk_if_ignored="Stockouts will result in direct lost sales and negative customer satisfaction.",
            )
        )
    else:
        items.append(
            ActionItem(
                id=str(uuid4()),
                title="Establish Automated Inventory Reorder & Lead-Time Pacing",
                domain="inventory",
                urgency="medium",
                expected_impact="Maintain continuous fulfillment velocity and prevent stockouts",
                effort="low",
                timeframe="1-2 weeks",
                action_steps=[
                    "Audit warehouse turnover for top 5 volume products.",
                    "Define standard 21-day safety stock buffers with primary suppliers.",
                ],
                owner="Operations Lead",
                risk_if_ignored="Unplanned stock depletion during seasonal sales surges.",
            )
        )

    # 4. AOV Expansion Initiative
    target_aov = round(kpis.average_order_value * 1.20, 2)
    items.append(
        ActionItem(
            id=str(uuid4()),
            title=f"Establish Free Shipping & Tiered Threshold at ${target_aov}",
            domain="sales",
            urgency="medium",
            expected_impact=f"Raise Average Order Value from ${kpis.average_order_value:.2f} to ${target_aov:.2f}",
            effort="low",
            timeframe="1-2 weeks",
            action_steps=[
                f"Set free shipping qualification threshold at ${target_aov} (20% above current ${kpis.average_order_value:.2f} AOV).",
                "Add a dynamic cart progress bar ('Add $X more for Free Shipping!').",
                "Recommend 1-click cart add-ons under $15 at checkout.",
            ],
            owner="E-Commerce Store Manager",
            risk_if_ignored="Leaving customer checkout basket size unoptimized.",
        )
    )

    return items
