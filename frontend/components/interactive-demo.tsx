"use client";

import { useState } from "react";
import Link from "next/link";

export default function InteractiveDemo() {
  const [step, setStep] = useState<1 | 2 | 3 | 4>(1);

  return (
    <div className="mx-auto max-w-5xl rounded-3xl border border-zinc-200 bg-white/70 backdrop-blur-xl p-4 sm:p-8 shadow-xl dark:border-zinc-800 dark:bg-zinc-900/70">
      {/* Demo Stepper Navigation */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 border-b border-zinc-100 dark:border-zinc-800 pb-6 mb-6">
        {[
          { num: 1, title: "1. Upload File", subtitle: "CSV / Multi-Sheet XLSX" },
          { num: 2, title: "2. AI Schema Mapping", subtitle: "Auto-detect & Validate" },
          { num: 3, title: "3. Deterministic KPIs", subtitle: "Verified Calculations" },
          { num: 4, title: "4. AI Copilot Q&A", subtitle: "Grounded Insights" },
        ].map((s) => (
          <button
            key={s.num}
            onClick={() => setStep(s.num as 1 | 2 | 3 | 4)}
            className={`flex flex-col items-start p-3 rounded-2xl text-left transition-all ${
              step === s.num
                ? "bg-indigo-50 dark:bg-indigo-950/50 border border-indigo-200 dark:border-indigo-800"
                : "hover:bg-zinc-50 dark:hover:bg-zinc-800/40"
            }`}
          >
            <span
              className={`text-xs font-bold ${
                step === s.num ? "text-indigo-600 dark:text-indigo-400" : "text-zinc-800 dark:text-zinc-200"
              }`}
            >
              {s.title}
            </span>
            <span className="text-[10px] text-zinc-400 mt-0.5">{s.subtitle}</span>
          </button>
        ))}
      </div>

      {/* Step Contents */}
      <div className="min-h-[340px] flex flex-col justify-between">
        {step === 1 && (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h4 className="text-sm font-bold text-zinc-900 dark:text-zinc-100">
                  Sample Dataset: Retail Store Sales (90 Days)
                </h4>
                <p className="text-xs text-zinc-500 dark:text-zinc-400">
                  Spreadsheet containing 842 customer orders across 12 product categories.
                </p>
              </div>
              <span className="rounded-full bg-emerald-50 px-2.5 py-0.5 text-xs font-semibold text-emerald-700 dark:bg-emerald-950/40 dark:text-emerald-300">
                Validated CSV
              </span>
            </div>

            <div className="rounded-xl border border-zinc-200 bg-zinc-50/50 p-4 dark:border-zinc-800 dark:bg-zinc-950 overflow-x-auto text-xs font-mono">
              <table className="w-full text-left">
                <thead className="text-zinc-400 border-b border-zinc-200 dark:border-zinc-800">
                  <tr>
                    <th className="py-1 px-2">order_id</th>
                    <th className="py-1 px-2">order_date</th>
                    <th className="py-1 px-2">product_name</th>
                    <th className="py-1 px-2">quantity</th>
                    <th className="py-1 px-2">revenue</th>
                    <th className="py-1 px-2">customer_id</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-zinc-200/50 dark:divide-zinc-800/50 text-zinc-700 dark:text-zinc-300">
                  <tr>
                    <td className="py-1.5 px-2 font-semibold">ORD-001</td>
                    <td className="py-1.5 px-2">2024-01-05</td>
                    <td className="py-1.5 px-2">Smart Watch Pro</td>
                    <td className="py-1.5 px-2">2</td>
                    <td className="py-1.5 px-2">$399.98</td>
                    <td className="py-1.5 px-2">CUST-881</td>
                  </tr>
                  <tr>
                    <td className="py-1.5 px-2 font-semibold">ORD-002</td>
                    <td className="py-1.5 px-2">2024-01-05</td>
                    <td className="py-1.5 px-2">Wireless Earbuds</td>
                    <td className="py-1.5 px-2">1</td>
                    <td className="py-1.5 px-2">$129.99</td>
                    <td className="py-1.5 px-2">CUST-412</td>
                  </tr>
                  <tr>
                    <td className="py-1.5 px-2 font-semibold">ORD-003</td>
                    <td className="py-1.5 px-2">2024-01-06</td>
                    <td className="py-1.5 px-2">Noise-Cancelling Headset</td>
                    <td className="py-1.5 px-2">1</td>
                    <td className="py-1.5 px-2">$249.50</td>
                    <td className="py-1.5 px-2">CUST-903</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        )}

        {step === 2 && (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h4 className="text-sm font-bold text-zinc-900 dark:text-zinc-100">
                  AI Column Mapping & Semantic Type Inference
                </h4>
                <p className="text-xs text-zinc-500 dark:text-zinc-400">
                  Automatically aligns your raw column headers to the canonical business schema.
                </p>
              </div>
              <span className="rounded-full bg-indigo-50 px-2.5 py-0.5 text-xs font-semibold text-indigo-700 dark:bg-indigo-950/40 dark:text-indigo-300">
                100% Match Confidence
              </span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs">
              <div className="rounded-xl border border-zinc-200 bg-zinc-50/50 p-3.5 dark:border-zinc-800 dark:bg-zinc-800/40">
                <span className="text-zinc-400">Target: order_date</span>
                <p className="font-bold text-zinc-900 dark:text-zinc-100 mt-0.5">← Source: order_date</p>
                <span className="text-[10px] text-emerald-600 font-medium">Verified Timestamp</span>
              </div>
              <div className="rounded-xl border border-zinc-200 bg-zinc-50/50 p-3.5 dark:border-zinc-800 dark:bg-zinc-800/40">
                <span className="text-zinc-400">Target: total_revenue</span>
                <p className="font-bold text-zinc-900 dark:text-zinc-100 mt-0.5">← Source: revenue</p>
                <span className="text-[10px] text-emerald-600 font-medium">Verified Float ($)</span>
              </div>
              <div className="rounded-xl border border-zinc-200 bg-zinc-50/50 p-3.5 dark:border-zinc-800 dark:bg-zinc-800/40">
                <span className="text-zinc-400">Target: customer_id</span>
                <p className="font-bold text-zinc-900 dark:text-zinc-100 mt-0.5">← Source: customer_id</p>
                <span className="text-[10px] text-emerald-600 font-medium">Unique Identifier</span>
              </div>
            </div>
          </div>
        )}

        {step === 3 && (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h4 className="text-sm font-bold text-zinc-900 dark:text-zinc-100">
                  Deterministic Verified Business Intelligence
                </h4>
                <p className="text-xs text-zinc-500 dark:text-zinc-400">
                  Mathematically exact KPIs, Pareto product rankings, and 30-day ML forecast.
                </p>
              </div>
              <span className="rounded-full bg-emerald-50 px-2.5 py-0.5 text-xs font-semibold text-emerald-700 dark:bg-emerald-950/40 dark:text-emerald-300">
                No LLM Hallucinations
              </span>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              <div className="rounded-xl border border-zinc-200 bg-zinc-50/50 p-3.5 dark:border-zinc-800 dark:bg-zinc-800/40">
                <span className="text-[11px] text-zinc-400">Total Revenue</span>
                <p className="text-xl font-bold text-zinc-900 dark:text-zinc-100 mt-0.5">$128,450.00</p>
                <span className="text-[10px] text-emerald-600 font-medium">+14.2% MoM Growth</span>
              </div>
              <div className="rounded-xl border border-zinc-200 bg-zinc-50/50 p-3.5 dark:border-zinc-800 dark:bg-zinc-800/40">
                <span className="text-[11px] text-zinc-400">Orders / AOV</span>
                <p className="text-xl font-bold text-zinc-900 dark:text-zinc-100 mt-0.5">842 ($152.55)</p>
                <span className="text-[10px] text-zinc-400">per transaction</span>
              </div>
              <div className="rounded-xl border border-zinc-200 bg-zinc-50/50 p-3.5 dark:border-zinc-800 dark:bg-zinc-800/40">
                <span className="text-[11px] text-zinc-400">30-Day ML Forecast</span>
                <p className="text-xl font-bold text-indigo-600 dark:text-indigo-400 mt-0.5">$46,200.00</p>
                <span className="text-[10px] text-zinc-400">MAPE: 7.8% (High Acc)</span>
              </div>
              <div className="rounded-xl border border-zinc-200 bg-zinc-50/50 p-3.5 dark:border-zinc-800 dark:bg-zinc-800/40">
                <span className="text-[11px] text-zinc-400">Customer Repeat Rate</span>
                <p className="text-xl font-bold text-zinc-900 dark:text-zinc-100 mt-0.5">42.8%</p>
                <span className="text-[10px] text-rose-500">14 Churn-Risk Buyers</span>
              </div>
            </div>
          </div>
        )}

        {step === 4 && (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h4 className="text-sm font-bold text-zinc-900 dark:text-zinc-100">
                  Conversational Copilot (Strictly Grounded)
                </h4>
                <p className="text-xs text-zinc-500 dark:text-zinc-400">
                  Ask complex business questions in plain English and receive evidence-backed answers.
                </p>
              </div>
              <span className="rounded-full bg-indigo-50 px-2.5 py-0.5 text-xs font-semibold text-indigo-700 dark:bg-indigo-950/40 dark:text-indigo-300">
                Executive Partner
              </span>
            </div>

            <div className="rounded-xl border border-zinc-200 bg-zinc-50/50 p-4 dark:border-zinc-800 dark:bg-zinc-800/40 space-y-3 text-xs">
              <div className="flex justify-end">
                <div className="rounded-xl bg-indigo-600 text-white px-3.5 py-2">
                  What is driving our growth, and what are our main vulnerabilities?
                </div>
              </div>
              <div className="flex justify-start">
                <div className="rounded-xl bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-700 px-4 py-3 text-zinc-800 dark:text-zinc-200 space-y-1.5 max-w-xl">
                  <p>
                    Your business achieved <strong>$128,450.00</strong> in revenue (+14.2% MoM growth) primarily led by <strong>Smart Watch Pro</strong> ($42,100 revenue).
                  </p>
                  <p className="text-rose-600 dark:text-rose-400">
                    ⚠️ <strong>Vulnerability:</strong> Your top 3 products account for <strong>68.4%</strong> of total sales (Pareto concentration risk), and 14 high-value customers have been inactive for &gt;60 days ($8,200 at stake).
                  </p>
                  <p className="text-indigo-600 dark:text-indigo-400 font-semibold">
                    💡 Recommended: Deploy a targeted 15% win-back campaign and bundle accessories with Smart Watch Pro.
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Stepper Controls & CTA */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pt-6 border-t border-zinc-100 dark:border-zinc-800 mt-4">
          <div className="flex items-center gap-2">
            <button
              disabled={step === 1}
              onClick={() => setStep((prev) => (Math.max(1, prev - 1) as 1 | 2 | 3 | 4))}
              className="rounded-xl border border-zinc-200 bg-white px-3.5 py-2 text-xs font-medium text-zinc-700 hover:bg-zinc-50 disabled:opacity-40 dark:border-zinc-700 dark:bg-zinc-800 dark:text-zinc-300"
            >
              ← Previous Step
            </button>
            <button
              disabled={step === 4}
              onClick={() => setStep((prev) => (Math.min(4, prev + 1) as 1 | 2 | 3 | 4))}
              className="rounded-xl bg-indigo-600 px-3.5 py-2 text-xs font-semibold text-white hover:bg-indigo-700 disabled:opacity-40 transition-colors dark:bg-indigo-500"
            >
              Next Demo Step →
            </button>
          </div>

          <Link
            href="/auth/signup"
            className="rounded-xl bg-zinc-900 px-5 py-2.5 text-xs font-bold text-white shadow-md hover:bg-black transition-colors dark:bg-zinc-100 dark:text-zinc-900 dark:hover:bg-white text-center"
          >
            Analyze Your Own Business Data Free →
          </Link>
        </div>
      </div>
    </div>
  );
}
