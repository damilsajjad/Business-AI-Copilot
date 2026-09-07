"""Pydantic schemas for deterministic business analytics."""

from datetime import datetime

from pydantic import BaseModel


class KPISummary(BaseModel):
    """Core high-level summary KPIs."""

    total_revenue: float
    total_orders: int
    total_units: int
    unique_customers: int
    unique_products: int
    average_order_value: float
    revenue_per_day: float
    start_date: str
    end_date: str
    total_days: int


class TimeSeriesPoint(BaseModel):
    """Aggregated sales data point for a specific time interval."""

    period: str
    revenue: float
    orders: int
    units: int
    aov: float


class SalesAnomaly(BaseModel):
    """Detected spike or dip in sales."""

    date: str
    revenue: float
    expected_revenue: float
    type: str  # "spike" or "dip"
    z_score: float
    deviation_pct: float


class SalesAnalytics(BaseModel):
    """Sales trends, growth rates, and time-series patterns."""

    monthly_trends: list[TimeSeriesPoint]
    weekly_trends: list[TimeSeriesPoint]
    daily_trends: list[TimeSeriesPoint]
    mom_growth_rate_pct: float | None = None
    best_month: str | None = None
    worst_month: str | None = None
    anomalies: list[SalesAnomaly] = []


class ProductPerformanceItem(BaseModel):
    """Metrics for an individual product."""

    product_id: str | None = None
    product_name: str
    category: str | None = None
    total_revenue: float
    total_quantity: int
    revenue_share_pct: float
    average_unit_price: float


class CategoryBreakdownItem(BaseModel):
    """Aggregated category performance."""

    category: str
    total_revenue: float
    total_quantity: int
    revenue_share_pct: float


class ProductAnalytics(BaseModel):
    """Product and category performance metrics."""

    top_products: list[ProductPerformanceItem]
    bottom_products: list[ProductPerformanceItem]
    category_breakdown: list[CategoryBreakdownItem]
    top_3_products_revenue_share_pct: float


class CustomerSpendItem(BaseModel):
    """Customer purchasing summary."""

    customer_id: str
    total_spend: float
    order_count: int
    average_order_value: float


class CustomerAnalytics(BaseModel):
    """Customer retention and spend concentration metrics."""

    total_customers: int
    repeat_customers: int
    repeat_rate_pct: float
    top_customers: list[CustomerSpendItem]
    top_10_pct_revenue_share_pct: float


class DemandItem(BaseModel):
    """Demand velocity metrics for a single product."""

    product_name: str
    category: str | None = None
    total_units: int
    units_per_day: float
    velocity_tier: str  # "fast", "medium", "slow"


class DemandAnalytics(BaseModel):
    """Inventory velocity and movement rate analytics."""

    fast_moving_products: list[DemandItem]
    slow_moving_products: list[DemandItem]
    average_daily_units: float


class FullAnalyticsReport(BaseModel):
    """Comprehensive verified deterministic analytics output."""

    file_id: str
    business_id: str
    generated_at: datetime
    kpis: KPISummary
    sales: SalesAnalytics
    products: ProductAnalytics
    customers: CustomerAnalytics | None = None
    demand: DemandAnalytics | None = None
    available_capabilities: list[str]
