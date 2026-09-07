"use client";

import { useState } from "react";

export interface ForecastDataPoint {
  date: string;
  predicted_revenue: number;
  lower_bound: number;
  upper_bound: number;
}

export interface ForecastModelMetrics {
  model_name: string;
  mape: number;
  rmse: number;
  r2_score: number;
  training_days: number;
  forecast_horizon_days: number;
}

export interface SalesForecastResponse {
  file_id: string;
  business_id: string;
  generated_at: string;
  horizon_30_days: ForecastDataPoint[];
  horizon_60_days: ForecastDataPoint[];
  horizon_90_days: ForecastDataPoint[];
  projected_30d_revenue: number;
  projected_60d_revenue: number;
  projected_90d_revenue: number;
  projected_growth_pct: number;
  metrics: ForecastModelMetrics;
  status: string;
  notes: string[];
}

interface ForecastViewProps {
  forecast: SalesForecastResponse;
  onRefresh?: () => void;
}

export default function ForecastView({ forecast, onRefresh }: ForecastViewProps) {
  const [horizon, setHorizon] = useState<30 | 60 | 90>(30);

  const activePoints =
    horizon === 30
      ? forecast.horizon_30_days
      : horizon === 60
      ? forecast.horizon_60_days
      : forecast.horizon_90_days;

  const activeProjectedRevenue =
    horizon === 30
      ? forecast.projected_30d_revenue
      : horizon === 60
      ? forecast.projected_60d_revenue
      : forecast.projected_90d_revenue;

  const maxPointRevenue = Math.max(...activePoints.map((p) => p.upper_bound), 1);

  return (
    <div className="space-y-6">
      {/* Header & Meta */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
        <div>
          <div className="flex items-center gap-2">
            <span className="flex h-2.5 w-2.5 rounded-full bg-indigo-500 animate-pulse" />
            <span className="text-xs font-semibold text-indigo-700 dark:text-indigo-400 uppercase tracking-wider">
              ML Time-Series Forecasting
            </span>
          </div>
          <h2 className="mt-1 text-xl font-bold text-zinc-900 dark:text-zinc-100">
            Sales & Revenue Projections
          </h2>
          <p className="mt-0.5 text-xs text-zinc-500 dark:text-zinc-400">
            Trained on {forecast.metrics.training_days} historical days using {forecast.metrics.model_name}
          </p>
        </div>

        {onRefresh && (
          <button
            onClick={onRefresh}
            className="self-start rounded-xl border border-zinc-200 bg-white px-3.5 py-2 text-xs font-medium text-zinc-700 shadow-sm hover:bg-zinc-50 dark:border-zinc-700 dark:bg-zinc-800 dark:text-zinc-300 dark:hover:bg-zinc-700"
          >
            ↻ Re-train Model
          </button>
        )}
      </div>

      {/* Summary KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
        <div className="rounded-2xl border border-zinc-200 bg-white p-5 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
          <span className="text-xs font-medium text-zinc-500 dark:text-zinc-400">30-Day Projection</span>
          <p className="mt-1.5 text-2xl font-bold text-indigo-600 dark:text-indigo-400">
            ${forecast.projected_30d_revenue.toLocaleString()}
          </p>
          <span className="mt-1 block text-[11px] text-emerald-600 dark:text-emerald-400 font-medium">
            {forecast.projected_growth_pct >= 0 ? `+${forecast.projected_growth_pct}%` : `${forecast.projected_growth_pct}%`} vs prior 30d
          </span>
        </div>

        <div className="rounded-2xl border border-zinc-200 bg-white p-5 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
          <span className="text-xs font-medium text-zinc-500 dark:text-zinc-400">60-Day Projection</span>
          <p className="mt-1.5 text-2xl font-bold text-zinc-900 dark:text-zinc-100">
            ${forecast.projected_60d_revenue.toLocaleString()}
          </p>
          <span className="mt-1 block text-[11px] text-zinc-400">cumulative 2-month outlook</span>
        </div>

        <div className="rounded-2xl border border-zinc-200 bg-white p-5 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
          <span className="text-xs font-medium text-zinc-500 dark:text-zinc-400">90-Day Projection</span>
          <p className="mt-1.5 text-2xl font-bold text-zinc-900 dark:text-zinc-100">
            ${forecast.projected_90d_revenue.toLocaleString()}
          </p>
          <span className="mt-1 block text-[11px] text-zinc-400">cumulative quarter outlook</span>
        </div>

        <div className="rounded-2xl border border-zinc-200 bg-white p-5 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
          <span className="text-xs font-medium text-zinc-500 dark:text-zinc-400">Model Accuracy (MAPE)</span>
          <p className="mt-1.5 text-2xl font-bold text-emerald-600 dark:text-emerald-400">
            {forecast.metrics.mape}%
          </p>
          <span className="mt-1 block text-[11px] text-zinc-400">RMSE: ${forecast.metrics.rmse}</span>
        </div>
      </div>

      {/* Interactive Forecast Chart */}
      <div className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
          <div>
            <h3 className="text-base font-semibold text-zinc-900 dark:text-zinc-100">
              Future Daily Projections ({horizon} Days)
            </h3>
            <p className="text-xs text-zinc-500 dark:text-zinc-400 mt-0.5">
              Projected Total: <span className="font-bold text-zinc-900 dark:text-zinc-100">${activeProjectedRevenue.toLocaleString()}</span> with 90% Confidence Intervals
            </p>
          </div>

          <div className="flex items-center gap-1 rounded-xl bg-zinc-100 p-1 dark:bg-zinc-800">
            {([30, 60, 90] as const).map((days) => (
              <button
                key={days}
                onClick={() => setHorizon(days)}
                className={`rounded-lg px-3 py-1 text-xs font-medium transition-colors ${
                  horizon === days
                    ? "bg-white text-zinc-900 shadow-sm dark:bg-zinc-700 dark:text-zinc-100"
                    : "text-zinc-600 hover:text-zinc-900 dark:text-zinc-400 dark:hover:text-zinc-200"
                }`}
              >
                {days} Days
              </button>
            ))}
          </div>
        </div>

        {/* Visual Forecast Bars with Range Error Bars */}
        <div className="h-56 flex items-end gap-1.5 pt-6 pb-2 overflow-x-auto">
          {activePoints.map((pt) => {
            const predHeight = Math.max(6, Math.round((pt.predicted_revenue / maxPointRevenue) * 100));
            return (
              <div
                key={pt.date}
                className="group relative flex-1 min-w-[12px] flex flex-col items-center h-full justify-end"
              >
                {/* Tooltip */}
                <div className="opacity-0 group-hover:opacity-100 transition-opacity absolute -top-14 z-20 pointer-events-none rounded-lg bg-zinc-900 px-2.5 py-1 text-[10px] text-white shadow-lg whitespace-nowrap dark:bg-zinc-100 dark:text-zinc-900">
                  <p className="font-bold">{pt.date}</p>
                  <p>Predicted: ${pt.predicted_revenue.toLocaleString()}</p>
                  <p className="text-zinc-400 dark:text-zinc-500">Range: ${pt.lower_bound} – ${pt.upper_bound}</p>
                </div>

                <div
                  style={{ height: `${predHeight}%` }}
                  className="w-full rounded-t-sm bg-indigo-500 hover:bg-indigo-600 dark:bg-indigo-600 dark:hover:bg-indigo-500 transition-all cursor-pointer"
                />
              </div>
            );
          })}
        </div>

        <div className="flex items-center justify-between text-[11px] text-zinc-400 mt-3 pt-3 border-t border-zinc-100 dark:border-zinc-800">
          <span>{activePoints[0]?.date}</span>
          <span className="flex items-center gap-4">
            <span className="inline-flex items-center gap-1.5">
              <span className="h-2 w-2 rounded-sm bg-indigo-500" /> Predicted Revenue
            </span>
          </span>
          <span>{activePoints[activePoints.length - 1]?.date}</span>
        </div>
      </div>
    </div>
  );
}
