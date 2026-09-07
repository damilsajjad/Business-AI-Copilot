"""Validation guardrails for ML models to prevent running on sparse data."""

import pandas as pd


class MLGuardrailResult:
    """Outcome of ML model feasibility check."""

    def __init__(self, is_feasible: bool, reason: str = ""):
        self.is_feasible = is_feasible
        self.reason = reason


def check_forecasting_feasibility(df: pd.DataFrame) -> MLGuardrailResult:
    """Check if dataset has sufficient time-series depth for forecasting."""
    if df.empty or "order_date" not in df.columns or "total_revenue" not in df.columns:
        return MLGuardrailResult(False, "Missing order_date or total_revenue columns.")

    valid_dates = df["order_date"].dropna()
    if len(valid_dates) < 10:
        return MLGuardrailResult(False, "Insufficient total records (minimum 10 required).")

    distinct_days = valid_dates.dt.date.nunique()
    if distinct_days < 10:
        return MLGuardrailResult(
            False,
            f"Insufficient time-series history: Dataset contains only {distinct_days} distinct days (minimum 10 required).",
        )

    return MLGuardrailResult(True, "Dataset meets time-series forecasting requirements.")


def check_churn_feasibility(df: pd.DataFrame) -> MLGuardrailResult:
    """Check if dataset has sufficient customer history for churn scoring."""
    if df.empty or "customer_id" not in df.columns:
        return MLGuardrailResult(False, "No customer_id column mapped in dataset.")

    valid_customers = df[
        df["customer_id"].notna()
        & (df["customer_id"] != "Unknown Customer")
        & (df["customer_id"] != "")
    ]

    distinct_customers = valid_customers["customer_id"].nunique()
    if distinct_customers < 3:
        return MLGuardrailResult(
            False,
            f"Insufficient customer base: Only {distinct_customers} unique customers found (minimum 3 required).",
        )

    orders_per_customer = valid_customers.groupby("customer_id")["order_id"].nunique() if "order_id" in valid_customers.columns else valid_customers.groupby("customer_id")["total_revenue"].count()
    repeat_customers = (orders_per_customer > 1).sum()

    if repeat_customers < 1:
        return MLGuardrailResult(
            False,
            "Insufficient repeat purchase events to evaluate churn risk patterns.",
        )

    return MLGuardrailResult(True, "Dataset meets customer churn scoring requirements.")
