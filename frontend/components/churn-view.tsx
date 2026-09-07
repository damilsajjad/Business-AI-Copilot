"use client";

import { useState } from "react";

export interface CustomerRiskItem {
  customer_id: string;
  recency_days: number;
  frequency_orders: number;
  monetary_spend: number;
  churn_risk_score: number;
  risk_tier: "high" | "medium" | "low" | string;
  risk_factors: string[];
  suggested_action: string;
}

export interface CustomerChurnResponse {
  file_id: string;
  business_id: string;
  generated_at: string;
  total_customers_evaluated: number;
  high_risk_count: number;
  medium_risk_count: number;
  low_risk_count: number;
  high_risk_revenue_at_stake: number;
  customers: CustomerRiskItem[];
  average_churn_risk: number;
  status: string;
  notes: string[];
}

interface ChurnViewProps {
  churn: CustomerChurnResponse;
  onRefresh?: () => void;
}

export default function ChurnView({ churn, onRefresh }: ChurnViewProps) {
  const [filterTier, setFilterTier] = useState<"all" | "high" | "medium" | "low">("all");

  const filteredCustomers =
    filterTier === "all"
      ? churn.customers
      : churn.customers.filter((c) => c.risk_tier === filterTier);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
        <div>
          <div className="flex items-center gap-2">
            <span className="flex h-2.5 w-2.5 rounded-full bg-rose-500 animate-pulse" />
            <span className="text-xs font-semibold text-rose-700 dark:text-rose-400 uppercase tracking-wider">
              Customer Retention & Churn Risk
            </span>
          </div>
          <h2 className="mt-1 text-xl font-bold text-zinc-900 dark:text-zinc-100">
            Churn Risk Evaluation
          </h2>
          <p className="mt-0.5 text-xs text-zinc-500 dark:text-zinc-400">
            RFM recency and purchasing velocity analysis for {churn.total_customers_evaluated} customers
          </p>
        </div>

        {onRefresh && (
          <button
            onClick={onRefresh}
            className="self-start rounded-xl border border-zinc-200 bg-white px-3.5 py-2 text-xs font-medium text-zinc-700 shadow-sm hover:bg-zinc-50 dark:border-zinc-700 dark:bg-zinc-800 dark:text-zinc-300 dark:hover:bg-zinc-700"
          >
            ↻ Re-evaluate Churn
          </button>
        )}
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
        <div className="rounded-2xl border border-zinc-200 bg-white p-5 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
          <span className="text-xs font-medium text-zinc-500 dark:text-zinc-400">Revenue at Stake</span>
          <p className="mt-1.5 text-2xl font-bold text-rose-600 dark:text-rose-400">
            ${churn.high_risk_revenue_at_stake.toLocaleString()}
          </p>
          <span className="mt-1 block text-[11px] text-zinc-400">from high-risk churn customers</span>
        </div>

        <div className="rounded-2xl border border-zinc-200 bg-white p-5 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
          <span className="text-xs font-medium text-zinc-500 dark:text-zinc-400">High Risk Customers</span>
          <p className="mt-1.5 text-2xl font-bold text-zinc-900 dark:text-zinc-100">
            {churn.high_risk_count}
          </p>
          <span className="mt-1 block text-[11px] text-rose-500 font-medium">
            {churn.total_customers_evaluated > 0
              ? `${Math.round((churn.high_risk_count / churn.total_customers_evaluated) * 100)}% of customer base`
              : "0%"}
          </span>
        </div>

        <div className="rounded-2xl border border-zinc-200 bg-white p-5 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
          <span className="text-xs font-medium text-zinc-500 dark:text-zinc-400">Medium Risk Customers</span>
          <p className="mt-1.5 text-2xl font-bold text-amber-600 dark:text-amber-400">
            {churn.medium_risk_count}
          </p>
          <span className="mt-1 block text-[11px] text-zinc-400">requires nurture campaigns</span>
        </div>

        <div className="rounded-2xl border border-zinc-200 bg-white p-5 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
          <span className="text-xs font-medium text-zinc-500 dark:text-zinc-400">Average Churn Risk</span>
          <p className="mt-1.5 text-2xl font-bold text-zinc-900 dark:text-zinc-100">
            {(churn.average_churn_risk * 100).toFixed(0)}%
          </p>
          <span className="mt-1 block text-[11px] text-emerald-600 dark:text-emerald-400">
            {churn.low_risk_count} loyal low-risk customers
          </span>
        </div>
      </div>

      {/* Customer Risk Breakdown Table */}
      <div className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-4">
          <h3 className="text-base font-semibold text-zinc-900 dark:text-zinc-100">
            Customer Risk Scoring & Win-Back Actions
          </h3>

          <div className="flex items-center gap-1 rounded-xl bg-zinc-100 p-1 dark:bg-zinc-800">
            {(["all", "high", "medium", "low"] as const).map((tier) => (
              <button
                key={tier}
                onClick={() => setFilterTier(tier)}
                className={`rounded-lg px-3 py-1 text-xs font-medium capitalize transition-colors ${
                  filterTier === tier
                    ? "bg-white text-zinc-900 shadow-sm dark:bg-zinc-700 dark:text-zinc-100"
                    : "text-zinc-600 hover:text-zinc-900 dark:text-zinc-400 dark:hover:text-zinc-200"
                }`}
              >
                {tier}
              </button>
            ))}
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="border-b border-zinc-200 bg-zinc-50/50 text-zinc-500 dark:border-zinc-800 dark:bg-zinc-800/30 dark:text-zinc-400">
              <tr>
                <th className="py-2.5 px-3 font-medium">Customer</th>
                <th className="py-2.5 px-3 font-medium text-center">Risk Tier</th>
                <th className="py-2.5 px-3 font-medium text-right">Recency</th>
                <th className="py-2.5 px-3 font-medium text-right">Orders</th>
                <th className="py-2.5 px-3 font-medium text-right">Spend</th>
                <th className="py-2.5 px-3 font-medium">Identified Risk Factors</th>
                <th className="py-2.5 px-3 font-medium">Suggested Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-zinc-100 dark:divide-zinc-800">
              {filteredCustomers.map((cust) => (
                <tr key={cust.customer_id} className="hover:bg-zinc-50/50 dark:hover:bg-zinc-800/30 transition-colors">
                  <td className="py-3 px-3 font-semibold text-zinc-900 dark:text-zinc-100">
                    {cust.customer_id}
                  </td>
                  <td className="py-3 px-3 text-center">
                    <span
                      className={`inline-block rounded-full px-2.5 py-0.5 text-[10px] font-bold uppercase tracking-wider ${
                        cust.risk_tier === "high"
                          ? "bg-rose-50 text-rose-700 dark:bg-rose-950/40 dark:text-rose-300"
                          : cust.risk_tier === "medium"
                          ? "bg-amber-50 text-amber-700 dark:bg-amber-950/40 dark:text-amber-300"
                          : "bg-emerald-50 text-emerald-700 dark:bg-emerald-950/40 dark:text-emerald-300"
                      }`}
                    >
                      {cust.risk_tier} ({(cust.churn_risk_score * 100).toFixed(0)}%)
                    </span>
                  </td>
                  <td className="py-3 px-3 text-right text-zinc-600 dark:text-zinc-400">
                    {cust.recency_days}d ago
                  </td>
                  <td className="py-3 px-3 text-right text-zinc-600 dark:text-zinc-400">
                    {cust.frequency_orders}
                  </td>
                  <td className="py-3 px-3 text-right font-medium text-zinc-900 dark:text-zinc-100">
                    ${cust.monetary_spend.toLocaleString()}
                  </td>
                  <td className="py-3 px-3">
                    <div className="flex flex-wrap gap-1">
                      {cust.risk_factors.map((f, i) => (
                        <span key={i} className="rounded bg-zinc-100 px-1.5 py-0.5 text-[10px] text-zinc-600 dark:bg-zinc-800 dark:text-zinc-300">
                          {f}
                        </span>
                      ))}
                    </div>
                  </td>
                  <td className="py-3 px-3 text-xs text-indigo-600 dark:text-indigo-400">
                    {cust.suggested_action}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
