"""Customer churn risk scoring engine using RFM analysis and risk tiering."""

from datetime import UTC, datetime

import pandas as pd

from app.ml.guardrails import check_churn_feasibility
from app.schemas.ml import (
    CustomerChurnResponse,
    CustomerRiskItem,
)


def calculate_customer_churn_risk(
    df: pd.DataFrame,
    file_id: str,
    business_id: str,
) -> CustomerChurnResponse:
    """Calculate customer churn risk scores based on Recency, Frequency, and Monetary metrics."""
    if not df.empty and "order_date" in df.columns and not pd.api.types.is_datetime64_any_dtype(df["order_date"]):
        df = df.copy()
        df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")

    guard = check_churn_feasibility(df)
    now_utc = datetime.now(UTC)

    if not guard.is_feasible:
        return CustomerChurnResponse(
            file_id=file_id,
            business_id=business_id,
            generated_at=now_utc,
            total_customers_evaluated=0,
            high_risk_count=0,
            medium_risk_count=0,
            low_risk_count=0,
            high_risk_revenue_at_stake=0.0,
            customers=[],
            average_churn_risk=0.0,
            status="insufficient_data",
            notes=[guard.reason],
        )

    valid_df = df[
        df["customer_id"].notna()
        & (df["customer_id"] != "Unknown Customer")
        & (df["customer_id"] != "")
    ].copy()

    max_date = valid_df["order_date"].max()

    # Aggregate RFM per customer
    grouped = valid_df.groupby("customer_id").agg(
        last_order=("order_date", "max"),
        first_order=("order_date", "min"),
        frequency=("order_id", "nunique") if "order_id" in valid_df.columns else ("total_revenue", "count"),
        total_spend=("total_revenue", "sum"),
    ).reset_index()

    mean_spend = float(grouped["total_spend"].mean()) if not grouped.empty else 1.0

    customer_items: list[CustomerRiskItem] = []
    total_risk_sum = 0.0

    for _, row in grouped.iterrows():
        cust_id = str(row["customer_id"])
        last_date = row["last_order"]
        recency_days = max(0, (max_date - last_date).days)
        freq = int(row["frequency"])
        spend = round(float(row["total_spend"]), 2)

        # Risk scoring heuristic
        # 1. Recency component (50% weight): 90+ days inactive = max risk
        recency_factor = min(1.0, recency_days / 90.0)

        # 2. Frequency component (30% weight): 1 order = higher risk than multiple
        freq_factor = max(0.0, 1.0 - (freq / 4.0))

        # 3. Monetary deviation component (20% weight)
        monetary_factor = max(0.0, min(1.0, 1.0 - (spend / (mean_spend * 2.0))))

        raw_score = (0.50 * recency_factor) + (0.30 * freq_factor) + (0.20 * monetary_factor)
        score = round(max(0.05, min(0.95, raw_score)), 2)
        total_risk_sum += score

        risk_factors: list[str] = []
        if recency_days >= 60:
            risk_factors.append(f"Inactive for {recency_days} days")
        elif recency_days >= 30:
            risk_factors.append(f"No orders in {recency_days} days")

        if freq == 1:
            risk_factors.append("One-time purchaser with no follow-up order")
        elif freq >= 3:
            risk_factors.append("Historically loyal customer")

        if spend < (mean_spend * 0.5):
            risk_factors.append("Below-average lifetime spend")

        # Tiering & action recommendations
        if score >= 0.65:
            tier = "high"
            action = "Trigger immediate win-back campaign with 15% incentive discount."
        elif score >= 0.35:
            tier = "medium"
            action = "Send personalized product recommendations and check-in survey."
        else:
            tier = "low"
            action = "Enroll in VIP loyalty perks and early product access."

        customer_items.append(
            CustomerRiskItem(
                customer_id=cust_id,
                recency_days=recency_days,
                frequency_orders=freq,
                monetary_spend=spend,
                churn_risk_score=score,
                risk_tier=tier,
                risk_factors=risk_factors,
                suggested_action=action,
            )
        )

    # Sort customers by churn risk descending
    customer_items.sort(key=lambda c: (c.churn_risk_score, c.monetary_spend), reverse=True)

    high_risk = [c for c in customer_items if c.risk_tier == "high"]
    med_risk = [c for c in customer_items if c.risk_tier == "medium"]
    low_risk = [c for c in customer_items if c.risk_tier == "low"]

    high_risk_revenue = round(sum(c.monetary_spend for c in high_risk), 2)
    avg_risk = round(total_risk_sum / len(customer_items), 2) if customer_items else 0.0

    return CustomerChurnResponse(
        file_id=file_id,
        business_id=business_id,
        generated_at=now_utc,
        total_customers_evaluated=len(customer_items),
        high_risk_count=len(high_risk),
        medium_risk_count=len(med_risk),
        low_risk_count=len(low_risk),
        high_risk_revenue_at_stake=high_risk_revenue,
        customers=customer_items,
        average_churn_risk=avg_risk,
        status="success",
        notes=["Churn evaluation is based on RFM inactivity and purchasing velocity."],
    )
