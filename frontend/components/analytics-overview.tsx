"use client";

import { useState } from "react";

export interface KPISummary {
  total_revenue: number;
  total_orders: number;
  total_units: number;
  unique_customers: number;
  unique_products: number;
  average_order_value: number;
  revenue_per_day: number;
  start_date: string;
  end_date: string;
  total_days: number;
}

export interface TimeSeriesPoint {
  period: string;
  revenue: number;
  orders: number;
  units: number;
  aov: number;
}

export interface SalesAnomaly {
  date: string;
  revenue: number;
  expected_revenue: number;
  type: string;
  z_score: number;
  deviation_pct: number;
}

export interface SalesAnalytics {
  monthly_trends: TimeSeriesPoint[];
  weekly_trends: TimeSeriesPoint[];
  daily_trends: TimeSeriesPoint[];
  mom_growth_rate_pct?: number | null;
  best_month?: string | null;
  worst_month?: string | null;
  anomalies: SalesAnomaly[];
}

export interface ProductPerformanceItem {
  product_id?: string | null;
  product_name: string;
  category?: string | null;
  total_revenue: number;
  total_quantity: number;
  revenue_share_pct: number;
  average_unit_price: number;
}

export interface CategoryBreakdownItem {
  category: string;
  total_revenue: number;
  total_quantity: number;
  revenue_share_pct: number;
}

export interface ProductAnalytics {
  top_products: ProductPerformanceItem[];
  bottom_products: ProductPerformanceItem[];
  category_breakdown: CategoryBreakdownItem[];
  top_3_products_revenue_share_pct: number;
}

export interface CustomerSpendItem {
  customer_id: string;
  total_spend: number;
  order_count: number;
  average_order_value: number;
}

export interface CustomerAnalytics {
  total_customers: number;
  repeat_customers: number;
  repeat_rate_pct: number;
  top_customers: CustomerSpendItem[];
  top_10_pct_revenue_share_pct: number;
}

export interface DemandItem {
  product_name: string;
  category?: string | null;
  total_units: number;
  units_per_day: number;
  velocity_tier: string;
}

export interface DemandAnalytics {
  fast_moving_products: DemandItem[];
  slow_moving_products: DemandItem[];
  average_daily_units: number;
}

export interface FullAnalyticsReport {
  file_id: string;
  business_id: string;
  generated_at: string;
  kpis: KPISummary;
  sales: SalesAnalytics;
  products: ProductAnalytics;
  customers?: CustomerAnalytics | null;
  demand?: DemandAnalytics | null;
  available_capabilities: string[];
}

interface AnalyticsOverviewProps {
  report: FullAnalyticsReport;
  onBackToUploads: () => void;
}

export default function AnalyticsOverview({ report, onBackToUploads }: AnalyticsOverviewProps) {
  const [trendView, setTrendView] = useState<"monthly" | "weekly" | "daily">("monthly");
  const { kpis, sales, products, customers, demand } = report;

  const currentTrendPoints =
    trendView === "monthly"
      ? sales.monthly_trends
      : trendView === "weekly"
      ? sales.weekly_trends
      : sales.daily_trends.slice(-30); // Last 30 days for daily view

  const maxTrendRevenue = Math.max(...currentTrendPoints.map((p) => p.revenue), 1);

  return (
    <div className="space-y-8">
      {/* Top Banner & Actions */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
        <div>
          <div className="flex items-center gap-2">
            <span className="flex h-2.5 w-2.5 rounded-full bg-emerald-500 animate-pulse" />
            <span className="text-xs font-semibold text-emerald-700 dark:text-emerald-400 uppercase tracking-wider">
              Deterministic Analytics Verified
            </span>
          </div>
          <h2 className="mt-1 text-xl font-bold text-zinc-900 dark:text-zinc-100">
            Business Intelligence Overview
          </h2>
          <p className="mt-0.5 text-xs text-zinc-500 dark:text-zinc-400">
            Analyzed {kpis.total_orders.toLocaleString()} orders over {kpis.total_days} days ({kpis.start_date} to {kpis.end_date})
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={onBackToUploads}
            className="rounded-xl border border-zinc-200 bg-white px-3.5 py-2 text-xs font-medium text-zinc-700 shadow-sm hover:bg-zinc-50 dark:border-zinc-700 dark:bg-zinc-800 dark:text-zinc-300 dark:hover:bg-zinc-700"
          >
            ← Back to Datasets
          </button>
        </div>
      </div>

      {/* Primary KPI Metrics Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
        <div className="rounded-2xl border border-zinc-200 bg-white p-5 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
          <span className="text-xs font-medium text-zinc-500 dark:text-zinc-400">Total Revenue</span>
          <p className="mt-1.5 text-2xl font-bold text-zinc-900 dark:text-zinc-100">
            ${kpis.total_revenue.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
          </p>
          <span className="mt-1 block text-[11px] text-zinc-400">${kpis.revenue_per_day}/day avg</span>
        </div>

        <div className="rounded-2xl border border-zinc-200 bg-white p-5 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
          <span className="text-xs font-medium text-zinc-500 dark:text-zinc-400">Total Orders</span>
          <p className="mt-1.5 text-2xl font-bold text-zinc-900 dark:text-zinc-100">
            {kpis.total_orders.toLocaleString()}
          </p>
          <span className="mt-1 block text-[11px] text-zinc-400">verified orders</span>
        </div>

        <div className="rounded-2xl border border-zinc-200 bg-white p-5 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
          <span className="text-xs font-medium text-zinc-500 dark:text-zinc-400">Average Order Value</span>
          <p className="mt-1.5 text-2xl font-bold text-indigo-600 dark:text-indigo-400">
            ${kpis.average_order_value.toFixed(2)}
          </p>
          <span className="mt-1 block text-[11px] text-zinc-400">AOV per checkout</span>
        </div>

        <div className="rounded-2xl border border-zinc-200 bg-white p-5 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
          <span className="text-xs font-medium text-zinc-500 dark:text-zinc-400">Units Sold</span>
          <p className="mt-1.5 text-2xl font-bold text-zinc-900 dark:text-zinc-100">
            {kpis.total_units.toLocaleString()}
          </p>
          <span className="mt-1 block text-[11px] text-zinc-400">{kpis.unique_products} distinct SKUs</span>
        </div>

        <div className="rounded-2xl border border-zinc-200 bg-white p-5 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
          <span className="text-xs font-medium text-zinc-500 dark:text-zinc-400">Customer Base</span>
          <p className="mt-1.5 text-2xl font-bold text-zinc-900 dark:text-zinc-100">
            {kpis.unique_customers.toLocaleString()}
          </p>
          <span className="mt-1 block text-[11px] text-emerald-600 dark:text-emerald-400">
            {customers ? `${customers.repeat_rate_pct}% repeat rate` : "total buyers"}
          </span>
        </div>

        <div className="rounded-2xl border border-zinc-200 bg-white p-5 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
          <span className="text-xs font-medium text-zinc-500 dark:text-zinc-400">MoM Growth Rate</span>
          <p className={`mt-1.5 text-2xl font-bold ${
            (sales.mom_growth_rate_pct ?? 0) >= 0 ? "text-emerald-600 dark:text-emerald-400" : "text-rose-600 dark:text-rose-400"
          }`}>
            {sales.mom_growth_rate_pct !== null && sales.mom_growth_rate_pct !== undefined
              ? `${sales.mom_growth_rate_pct > 0 ? "+" : ""}${sales.mom_growth_rate_pct}%`
              : "—"}
          </p>
          <span className="mt-1 block text-[11px] text-zinc-400">monthly trend</span>
        </div>
      </div>

      {/* Sales Trend Visualizer */}
      <div className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
          <div>
            <h3 className="text-base font-semibold text-zinc-900 dark:text-zinc-100">
              Revenue Over Time
            </h3>
            <p className="text-xs text-zinc-500 dark:text-zinc-400 mt-0.5">
              Best period: <span className="font-semibold text-zinc-800 dark:text-zinc-200">{sales.best_month || "N/A"}</span> •
              Lowest: <span className="font-semibold text-zinc-800 dark:text-zinc-200">{sales.worst_month || "N/A"}</span>
            </p>
          </div>

          {/* Time Frequency Selector */}
          <div className="flex items-center gap-1 rounded-xl bg-zinc-100 p-1 dark:bg-zinc-800">
            {(["monthly", "weekly", "daily"] as const).map((freq) => (
              <button
                key={freq}
                onClick={() => setTrendView(freq)}
                className={`rounded-lg px-3 py-1 text-xs font-medium capitalize transition-colors ${
                  trendView === freq
                    ? "bg-white text-zinc-900 shadow-sm dark:bg-zinc-700 dark:text-zinc-100"
                    : "text-zinc-600 hover:text-zinc-900 dark:text-zinc-400 dark:hover:text-zinc-200"
                }`}
              >
                {freq}
              </button>
            ))}
          </div>
        </div>

        {/* Visual Bar Chart */}
        <div className="space-y-3">
          <div className="h-48 flex items-end gap-2 pt-4 pb-2">
            {currentTrendPoints.map((point) => {
              const heightPct = Math.max(8, Math.round((point.revenue / maxTrendRevenue) * 100));
              return (
                <div key={point.period} className="group relative flex-1 flex flex-col items-center h-full justify-end">
                  {/* Tooltip */}
                  <div className="opacity-0 group-hover:opacity-100 transition-opacity absolute -top-12 z-20 pointer-events-none rounded-lg bg-zinc-900 px-2.5 py-1 text-[10px] text-white shadow-lg whitespace-nowrap dark:bg-zinc-100 dark:text-zinc-900">
                    <p className="font-bold">{point.period}</p>
                    <p>${point.revenue.toLocaleString()} • {point.orders} orders</p>
                  </div>

                  <div
                    style={{ height: `${heightPct}%` }}
                    className="w-full rounded-t-md bg-indigo-500 hover:bg-indigo-600 dark:bg-indigo-600 dark:hover:bg-indigo-500 transition-all cursor-pointer"
                  />
                  <span className="truncate w-full text-center text-[10px] text-zinc-400 mt-1">
                    {point.period.replace(/^\d{4}-/, "")}
                  </span>
                </div>
              );
            })}
          </div>
        </div>

        {/* Anomalies Callout if any */}
        {sales.anomalies.length > 0 && (
          <div className="mt-4 pt-4 border-t border-zinc-100 dark:border-zinc-800">
            <h4 className="text-xs font-semibold text-zinc-700 dark:text-zinc-300 mb-2">
              🚨 Detected Anomalies ({sales.anomalies.length})
            </h4>
            <div className="flex flex-wrap gap-2">
              {sales.anomalies.map((a, i) => (
                <span
                  key={i}
                  className={`rounded-lg border px-2.5 py-1 text-xs font-medium ${
                    a.type === "spike"
                      ? "border-emerald-200 bg-emerald-50 text-emerald-700 dark:border-emerald-900 dark:bg-emerald-950/40 dark:text-emerald-300"
                      : "border-rose-200 bg-rose-50 text-rose-700 dark:border-rose-900 dark:bg-rose-950/40 dark:text-rose-300"
                  }`}
                >
                  {a.date}: ${a.revenue.toLocaleString()} ({a.type.toUpperCase()}{" "}
                  {a.deviation_pct > 0 ? `+${a.deviation_pct}%` : `${a.deviation_pct}%`})
                </span>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Product & Category Analytics Split */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Top Products Table (2 Cols) */}
        <div className="lg:col-span-2 rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-base font-semibold text-zinc-900 dark:text-zinc-100">
                Top Products by Revenue
              </h3>
              <p className="text-xs text-zinc-500 dark:text-zinc-400">
                Top 3 items generate {products.top_3_products_revenue_share_pct}% of total sales
              </p>
            </div>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="border-b border-zinc-200 bg-zinc-50/50 text-zinc-500 dark:border-zinc-800 dark:bg-zinc-800/30 dark:text-zinc-400">
                <tr>
                  <th className="py-2.5 px-3 font-medium">Product</th>
                  <th className="py-2.5 px-3 font-medium">Category</th>
                  <th className="py-2.5 px-3 font-medium text-right">Revenue</th>
                  <th className="py-2.5 px-3 font-medium text-right">Units</th>
                  <th className="py-2.5 px-3 font-medium text-right">Share</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-zinc-100 dark:divide-zinc-800">
                {products.top_products.slice(0, 7).map((p) => (
                  <tr key={p.product_name} className="hover:bg-zinc-50/50 dark:hover:bg-zinc-800/30 transition-colors">
                    <td className="py-3 px-3 font-semibold text-zinc-900 dark:text-zinc-100">
                      {p.product_name}
                    </td>
                    <td className="py-3 px-3 text-zinc-500 dark:text-zinc-400">{p.category || "General"}</td>
                    <td className="py-3 px-3 text-right font-medium text-zinc-900 dark:text-zinc-100">
                      ${p.total_revenue.toLocaleString()}
                    </td>
                    <td className="py-3 px-3 text-right text-zinc-600 dark:text-zinc-400">{p.total_quantity}</td>
                    <td className="py-3 px-3 text-right font-semibold text-indigo-600 dark:text-indigo-400">
                      {p.revenue_share_pct}%
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Category Breakdown & Concentration (1 Col) */}
        <div className="space-y-6">
          <div className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
            <h3 className="text-base font-semibold text-zinc-900 dark:text-zinc-100 mb-4">
              Category Distribution
            </h3>
            <div className="space-y-3">
              {products.category_breakdown.map((cat) => (
                <div key={cat.category} className="space-y-1">
                  <div className="flex items-center justify-between text-xs">
                    <span className="font-medium text-zinc-800 dark:text-zinc-200">{cat.category}</span>
                    <span className="font-semibold text-zinc-900 dark:text-zinc-100">
                      ${cat.total_revenue.toLocaleString()} ({cat.revenue_share_pct}%)
                    </span>
                  </div>
                  <div className="h-2 w-full rounded-full bg-zinc-100 dark:bg-zinc-800 overflow-hidden">
                    <div
                      className="h-full bg-indigo-600 rounded-full"
                      style={{ width: `${cat.revenue_share_pct}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Customer Retention Card */}
          {customers && (
            <div className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
              <h3 className="text-base font-semibold text-zinc-900 dark:text-zinc-100 mb-1">
                Customer Retention
              </h3>
              <p className="text-xs text-zinc-500 dark:text-zinc-400 mb-4">
                {customers.repeat_customers} of {customers.total_customers} customers made repeat purchases ({customers.repeat_rate_pct}%)
              </p>

              <div className="space-y-2">
                <span className="text-[11px] font-medium text-zinc-400 uppercase tracking-wider">Top Spenders</span>
                {customers.top_customers.slice(0, 3).map((c) => (
                  <div key={c.customer_id} className="flex items-center justify-between text-xs py-1">
                    <span className="font-medium text-zinc-800 dark:text-zinc-200">{c.customer_id}</span>
                    <span className="font-semibold text-zinc-900 dark:text-zinc-100">
                      ${c.total_spend.toLocaleString()} ({c.order_count} orders)
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Inventory Demand Velocity Card */}
          {demand && demand.fast_moving_products.length > 0 && (
            <div className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
              <h3 className="text-base font-semibold text-zinc-900 dark:text-zinc-100 mb-1">
                ⚡ Fast-Moving Items
              </h3>
              <p className="text-xs text-zinc-500 dark:text-zinc-400 mb-3">
                High-velocity products requiring regular stock monitoring
              </p>
              <div className="space-y-2">
                {demand.fast_moving_products.slice(0, 3).map((d) => (
                  <div key={d.product_name} className="flex items-center justify-between text-xs py-1 border-b border-zinc-50 dark:border-zinc-800 last:border-0">
                    <span className="font-medium text-zinc-800 dark:text-zinc-200 truncate max-w-[150px]">{d.product_name}</span>
                    <span className="font-semibold text-emerald-600 dark:text-emerald-400">
                      {d.units_per_day} units/day
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
