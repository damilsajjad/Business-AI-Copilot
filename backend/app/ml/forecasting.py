"""Time-series sales forecasting engine with confidence intervals and error metrics."""

from datetime import UTC, datetime, timedelta

import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge

from app.ml.guardrails import check_forecasting_feasibility
from app.schemas.ml import (
    ForecastDataPoint,
    ForecastModelMetrics,
    SalesForecastResponse,
)


def generate_sales_forecast(
    df: pd.DataFrame,
    file_id: str,
    business_id: str,
) -> SalesForecastResponse:
    """Generate 30, 60, and 90 day daily sales revenue forecasts."""
    if not df.empty and "order_date" in df.columns and not pd.api.types.is_datetime64_any_dtype(df["order_date"]):
        df = df.copy()
        df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")

    guard = check_forecasting_feasibility(df)
    now_utc = datetime.now(UTC)

    if not guard.is_feasible:
        return SalesForecastResponse(
            file_id=file_id,
            business_id=business_id,
            generated_at=now_utc,
            horizon_30_days=[],
            horizon_60_days=[],
            horizon_90_days=[],
            projected_30d_revenue=0.0,
            projected_60d_revenue=0.0,
            projected_90d_revenue=0.0,
            projected_growth_pct=0.0,
            metrics=ForecastModelMetrics(
                model_name="Trend-Seasonal Ridge",
                mape=0.0,
                rmse=0.0,
                r2_score=0.0,
                training_days=0,
                forecast_horizon_days=90,
            ),
            status="insufficient_data",
            notes=[guard.reason],
        )

    # 1. Prepare continuous daily time series
    daily = df.groupby(df["order_date"].dt.date)["total_revenue"].sum()
    daily.index = pd.to_datetime(daily.index)
    daily = daily.sort_index()

    # Fill date gaps with 0.0 sales
    full_idx = pd.date_range(start=daily.index.min(), end=daily.index.max(), freq="D")
    daily_series = daily.reindex(full_idx, fill_value=0.0)

    daily = pd.DataFrame({"date": daily_series.index, "revenue": daily_series.values})

    n_samples = len(daily)

    # 2. Feature engineering: trend (t), day-of-week seasonality (0-6)
    daily["t"] = np.arange(n_samples)
    day_dummies = pd.get_dummies(daily["date"].dt.dayofweek, prefix="dow", drop_first=True, dtype=float)

    # Align dummies for 7 days
    for d in range(1, 7):
        col = f"dow_{d}"
        if col not in day_dummies.columns:
            day_dummies[col] = 0.0

    x_train = pd.concat([daily[["t"]], day_dummies], axis=1).values
    y_train = daily["revenue"].values

    # 3. Fit Ridge model
    model = Ridge(alpha=1.0)
    model.fit(x_train, y_train)

    in_sample_preds = model.predict(x_train)
    residuals = y_train - in_sample_preds
    std_residual = float(np.std(residuals)) if len(residuals) > 1 else 1.0

    # In-sample metrics calculation
    nonzero_mask = y_train > 0
    if nonzero_mask.sum() > 0:
        mape = float(np.mean(np.abs(residuals[nonzero_mask] / y_train[nonzero_mask])) * 100)
    else:
        mape = 0.0

    rmse = float(np.sqrt(np.mean(residuals**2)))
    ss_tot = np.sum((y_train - np.mean(y_train)) ** 2)
    ss_res = np.sum(residuals**2)
    r2 = float(1 - (ss_res / ss_tot)) if ss_tot > 0 else 0.0

    # 4. Generate future projections for 90 days
    last_date = daily["date"].max()
    future_dates = [last_date + timedelta(days=i) for i in range(1, 91)]

    future_t = np.arange(n_samples, n_samples + 90)
    future_dow = pd.Series([d.weekday() for d in future_dates])
    future_dummies = pd.get_dummies(future_dow, prefix="dow", drop_first=True, dtype=float)

    for d in range(1, 7):
        col = f"dow_{d}"
        if col not in future_dummies.columns:
            future_dummies[col] = 0.0

    x_future = np.column_stack([future_t, future_dummies[[f"dow_{d}" for d in range(1, 7)]].values])
    future_preds = model.predict(x_future)

    # Format forecast points with bounds
    forecast_points: list[ForecastDataPoint] = []
    for date_val, pred in zip(future_dates, future_preds, strict=False):
        clean_pred = max(0.0, float(pred))
        lower = max(0.0, clean_pred - 1.645 * std_residual)
        upper = clean_pred + 1.645 * std_residual
        forecast_points.append(
            ForecastDataPoint(
                date=date_val.strftime("%Y-%m-%d"),
                predicted_revenue=round(clean_pred, 2),
                lower_bound=round(lower, 2),
                upper_bound=round(upper, 2),
            )
        )

    h30 = forecast_points[:30]
    h60 = forecast_points[:60]
    h90 = forecast_points[:90]

    proj_30d = round(sum(p.predicted_revenue for p in h30), 2)
    proj_60d = round(sum(p.predicted_revenue for p in h60), 2)
    proj_90d = round(sum(p.predicted_revenue for p in h90), 2)

    # Compare 30d projected against past 30d actual
    past_30d_rev = float(daily["revenue"].tail(30).sum())
    growth_pct = round(((proj_30d - past_30d_rev) / past_30d_rev * 100), 2) if past_30d_rev > 0 else 0.0

    return SalesForecastResponse(
        file_id=file_id,
        business_id=business_id,
        generated_at=now_utc,
        horizon_30_days=h30,
        horizon_60_days=h60,
        horizon_90_days=h90,
        projected_30d_revenue=proj_30d,
        projected_60d_revenue=proj_60d,
        projected_90d_revenue=proj_90d,
        projected_growth_pct=growth_pct,
        metrics=ForecastModelMetrics(
            model_name="Trend + Seasonality Ridge Regression",
            mape=round(mape, 2),
            rmse=round(rmse, 2),
            r2_score=round(r2, 3),
            training_days=n_samples,
            forecast_horizon_days=90,
        ),
        status="success",
        notes=["Forecast incorporates linear trend and weekly seasonality patterns."],
    )
