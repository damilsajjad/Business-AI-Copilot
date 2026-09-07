"""Interactive AI Business Copilot chat engine strictly grounded in verified facts."""

import json
import os
from typing import Any

import httpx

from app.agents.prompts import COPILOT_CHAT_SYSTEM_PROMPT
from app.schemas.agents import ChatMessage, CopilotChatResponse
from app.schemas.analytics import FullAnalyticsReport
from app.schemas.ml import CustomerChurnResponse, SalesForecastResponse


def _deterministic_copilot_reply(
    query: str,
    analytics: FullAnalyticsReport,
    forecast: SalesForecastResponse | None,
    churn: CustomerChurnResponse | None,
) -> CopilotChatResponse:
    """Intelligently answer natural language questions grounded in computed metrics."""
    q = query.lower()
    kpis = analytics.kpis
    sales = analytics.sales
    products = analytics.products
    customers = analytics.customers

    cited_metrics: dict[str, Any] = {}
    follow_ups: list[str] = [
        "What are our top-performing products?",
        "How is our customer retention trending?",
        "What is our projected revenue for next month?",
    ]

    # 1. Revenue & Sales questions
    if any(w in q for w in ["revenue", "sales", "make", "earn", "income", "money"]):
        cited_metrics["total_revenue"] = f"${kpis.total_revenue:,.2f}"
        cited_metrics["total_orders"] = kpis.total_orders
        cited_metrics["average_order_value"] = f"${kpis.average_order_value:.2f}"

        reply = (
            f"Your business generated **${kpis.total_revenue:,.2f}** in total revenue across **{kpis.total_orders:,}** verified orders "
            f"between {kpis.start_date} and {kpis.end_date}. "
            f"Your Average Order Value (AOV) is **${kpis.average_order_value:.2f}**, generating an average daily run-rate of **${kpis.revenue_per_day:,.2f}**."
        )
        if sales.best_month:
            reply += f" Your strongest sales month on record was **{sales.best_month}**."

        return CopilotChatResponse(
            reply=reply,
            cited_metrics=cited_metrics,
            suggested_follow_ups=["Which products generated the most revenue?", "What are our forecasted sales?"],
        )

    # 2. Product performance questions
    if any(w in q for w in ["product", "item", "sku", "sell", "best seller", "catalog", "category"]):
        top_items = products.top_products[:3]
        top_str = ", ".join([f"**{p.product_name}** (${p.total_revenue:,.2f}, {p.revenue_share_pct}%)" for p in top_items])
        cited_metrics["top_3_concentration"] = f"{products.top_3_products_revenue_share_pct}%"

        reply = (
            f"Your top performing products are {top_str}. "
            f"Together, your top 3 products account for **{products.top_3_products_revenue_share_pct}%** of your total revenue. "
            f"You have a total of **{kpis.unique_products}** distinct products active in your catalog across **{len(products.category_breakdown)}** categories."
        )

        return CopilotChatResponse(
            reply=reply,
            cited_metrics=cited_metrics,
            suggested_follow_ups=["How can we reduce product concentration risk?", "Which items have slow inventory velocity?"],
        )

    # 3. Customer & Churn questions
    if any(w in q for w in ["customer", "churn", "retention", "repeat", "buyer", "loyalty"]):
        if customers:
            cited_metrics["unique_customers"] = customers.total_customers
            cited_metrics["repeat_rate"] = f"{customers.repeat_rate_pct}%"
            reply = (
                f"You have **{customers.total_customers}** unique customers with a repeat purchase rate of **{customers.repeat_rate_pct}%** "
                f"({customers.repeat_customers} repeat buyers). "
                f"Your top 10% highest spenders generate **{customers.top_10_pct_revenue_share_pct}%** of all revenue."
            )
            if churn and churn.high_risk_count > 0:
                reply += f" Our ML model identified **{churn.high_risk_count}** customers at high risk of churn, with **${churn.high_risk_revenue_at_stake:,.2f}** in revenue at stake."
        else:
            reply = f"Your dataset records **{kpis.unique_customers}** unique customer transactions."

        return CopilotChatResponse(
            reply=reply,
            cited_metrics=cited_metrics,
            suggested_follow_ups=["What win-back campaign is recommended for churned customers?", "What is our 30-day forecast?"],
        )

    # 4. Forecast & Projection questions
    if any(w in q for w in ["forecast", "future", "project", "next month", "outlook", "projection", "q4"]):
        if forecast and forecast.status == "success":
            cited_metrics["projected_30d"] = f"${forecast.projected_30d_revenue:,.2f}"
            cited_metrics["growth_pct"] = f"{forecast.projected_growth_pct}%"
            cited_metrics["mape"] = f"{forecast.metrics.mape}%"

            reply = (
                f"Our time-series model projects **${forecast.projected_30d_revenue:,.2f}** in sales over the next 30 days "
                f"({'+' if forecast.projected_growth_pct >= 0 else ''}{forecast.projected_growth_pct}% vs the past 30 days), "
                f"and **${forecast.projected_90d_revenue:,.2f}** over the next 90 days. "
                f"The model was trained on {forecast.metrics.training_days} historical days with an accuracy MAPE of {forecast.metrics.mape}%."
            )
        else:
            reply = "Forecasting requires at least 14 days of historical sales records. Please upload more transaction history to enable ML projections."

        return CopilotChatResponse(
            reply=reply,
            cited_metrics=cited_metrics,
            suggested_follow_ups=["How can we accelerate our projected sales growth?", "What are our biggest business risks?"],
        )

    # 5. General summary / Help fallback
    cited_metrics["total_revenue"] = f"${kpis.total_revenue:,.2f}"
    cited_metrics["aov"] = f"${kpis.average_order_value:.2f}"

    reply = (
        f"I am your AI Business Copilot. Based on your analyzed dataset ({kpis.start_date} to {kpis.end_date}), "
        f"your business generated **${kpis.total_revenue:,.2f}** in revenue across **{kpis.total_orders:,}** orders with an AOV of **${kpis.average_order_value:.2f}**. "
        f"Feel free to ask me about sales trends, top product performance, customer retention, or revenue forecasts!"
    )

    return CopilotChatResponse(
        reply=reply,
        cited_metrics=cited_metrics,
        suggested_follow_ups=follow_ups,
    )


async def answer_copilot_query(
    query: str,
    history: list[ChatMessage],
    analytics: FullAnalyticsReport,
    forecast: SalesForecastResponse | None = None,
    churn: CustomerChurnResponse | None = None,
) -> CopilotChatResponse:
    """Generate conversational Copilot answer with Gemini LLM or factual fallback."""
    api_key = os.environ.get("GEMINI_API_KEY")

    if not api_key:
        return _deterministic_copilot_reply(query, analytics, forecast, churn)

    try:
        context_data = {
            "kpis": analytics.kpis.model_dump(),
            "sales": analytics.sales.model_dump(),
            "top_products": [p.model_dump() for p in analytics.products.top_products[:5]],
            "category_breakdown": [c.model_dump() for c in analytics.products.category_breakdown],
            "customers": analytics.customers.model_dump() if analytics.customers else None,
            "forecast_30d": forecast.projected_30d_revenue if forecast else None,
            "churn_revenue_at_stake": churn.high_risk_revenue_at_stake if churn else None,
        }

        messages_text = "\n".join([f"{m.role.upper()}: {m.content}" for m in history[-6:]])

        prompt = f"""{COPILOT_CHAT_SYSTEM_PROMPT}

BUSINESS CONTEXT (GROUND TRUTH):
{json.dumps(context_data, indent=2)}

RECENT CHAT HISTORY:
{messages_text}

USER QUESTION:
{query}

Respond with a JSON object:
{{
  "reply": "<Direct, helpful markdown response citing exact numbers>",
  "suggested_follow_ups": ["<Question 1>", "<Question 2>"]
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

                return CopilotChatResponse(
                    reply=str(parsed.get("reply", "")),
                    suggested_follow_ups=list(parsed.get("suggested_follow_ups", [])),
                )

    except Exception:
        pass

    return _deterministic_copilot_reply(query, analytics, forecast, churn)
