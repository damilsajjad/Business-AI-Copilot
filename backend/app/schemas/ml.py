"""Pydantic schemas for Machine Learning (Sales Forecasting & Churn Risk)."""

from datetime import datetime

from pydantic import BaseModel


class ForecastDataPoint(BaseModel):
    """Predicted future sales revenue data point with confidence intervals."""

    date: str
    predicted_revenue: float
    lower_bound: float
    upper_bound: float


class ForecastModelMetrics(BaseModel):
    """Model evaluation accuracy metrics."""

    model_name: str
    mape: float  # Mean Absolute Percentage Error
    rmse: float  # Root Mean Squared Error
    r2_score: float
    training_days: int
    forecast_horizon_days: int


class SalesForecastResponse(BaseModel):
    """Complete sales forecasting output for 30, 60, and 90 day horizons."""

    file_id: str
    business_id: str
    generated_at: datetime
    horizon_30_days: list[ForecastDataPoint]
    horizon_60_days: list[ForecastDataPoint]
    horizon_90_days: list[ForecastDataPoint]
    projected_30d_revenue: float
    projected_60d_revenue: float
    projected_90d_revenue: float
    projected_growth_pct: float
    metrics: ForecastModelMetrics
    status: str = "success"
    notes: list[str] = []


class CustomerRiskItem(BaseModel):
    """Customer-level churn risk evaluation and RFM breakdown."""

    customer_id: str
    recency_days: int
    frequency_orders: int
    monetary_spend: float
    churn_risk_score: float  # 0.0 to 1.0
    risk_tier: str  # "high", "medium", "low"
    risk_factors: list[str]
    suggested_action: str


class CustomerChurnResponse(BaseModel):
    """Complete customer churn risk scoring report."""

    file_id: str
    business_id: str
    generated_at: datetime
    total_customers_evaluated: int
    high_risk_count: int
    medium_risk_count: int
    low_risk_count: int
    high_risk_revenue_at_stake: float
    customers: list[CustomerRiskItem]
    average_churn_risk: float
    status: str = "success"
    notes: list[str] = []
