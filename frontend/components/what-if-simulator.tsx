"use client";

import { useState } from "react";

interface WhatIfSimulatorProps {
  businessId: string;
  fileId: string;
  baseRevenue: number;
}

export default function WhatIfSimulator({ baseRevenue }: WhatIfSimulatorProps) {
  const [revenueGrowth, setRevenueGrowth] = useState<number>(10);
  const [priceChange, setPriceChange] = useState<number>(0);
  const [discountChange, setDiscountChange] = useState<number>(0);
  const [churnReduction, setChurnReduction] = useState<number>(15);

  // Pure deterministic instant simulation
  const currentRev = baseRevenue;
  const baseMarginPct = 0.40;
  const currentMargin = Math.round(currentRev * baseMarginPct * 100) / 100;

  const volMult = 1.0 + revenueGrowth / 100.0;
  const priceMult = 1.0 + priceChange / 100.0;
  const discMult = 1.0 - discountChange / 100.0;

  const recoveredChurn = Math.round(currentRev * 0.15 * (churnReduction / 100.0) * 100) / 100;

  const simulatedRevenue = Math.round((currentRev * volMult * priceMult * discMult + recoveredChurn) * 100) / 100;
  const revenueDelta = Math.round((simulatedRevenue - currentRev) * 100) / 100;
  const revenueDeltaPct = currentRev > 0 ? Math.round((revenueDelta / currentRev) * 1000) / 10 : 0;

  const marginShift = priceChange * 0.005 - discountChange * 0.005;
  const simulatedMarginPct = Math.max(0.1, Math.min(0.8, baseMarginPct + marginShift));
  const simulatedMargin = Math.round(simulatedRevenue * simulatedMarginPct * 100) / 100;
  const marginDelta = Math.round((simulatedMargin - currentMargin) * 100) / 100;

  const insights: string[] = [];
  if (revenueDelta > 0) {
    insights.push(`Projected to unlock +$${revenueDelta.toLocaleString()} (+${revenueDeltaPct}%) in total sales revenue.`);
  } else if (revenueDelta < 0) {
    insights.push(`Simulated contraction of -$${Math.abs(revenueDelta).toLocaleString()} (${revenueDeltaPct}%) in revenue.`);
  }

  if (recoveredChurn > 0) {
    insights.push(`Recovers $${recoveredChurn.toLocaleString()} from previously lapsing buyers.`);
  }

  if (marginDelta > 0) {
    insights.push(`Estimated gross profit expands by +$${marginDelta.toLocaleString()}.`);
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
        <div>
          <div className="flex items-center gap-2">
            <span className="flex h-2.5 w-2.5 rounded-full bg-indigo-500 animate-pulse" />
            <span className="text-xs font-semibold text-indigo-700 dark:text-indigo-400 uppercase tracking-wider">
              Scenario Modeling & Strategy Sandbox
            </span>
          </div>
          <h2 className="mt-1 text-xl font-bold text-zinc-900 dark:text-zinc-100">
            What-If Scenario Simulator
          </h2>
          <p className="mt-0.5 text-xs text-zinc-500 dark:text-zinc-400">
            Simulate the bottom-line financial impact of price changes, promotional shifts, and churn reductions
          </p>
        </div>

        <button
          onClick={() => {
            setRevenueGrowth(0);
            setPriceChange(0);
            setDiscountChange(0);
            setChurnReduction(0);
          }}
          className="self-start rounded-xl border border-zinc-200 bg-white px-3.5 py-2 text-xs font-medium text-zinc-700 shadow-sm hover:bg-zinc-50 dark:border-zinc-700 dark:bg-zinc-800 dark:text-zinc-300 dark:hover:bg-zinc-700"
        >
          Reset Baseline
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left: Interactive Control Sliders (7 Cols) */}
        <div className="lg:col-span-7 rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm dark:border-zinc-800 dark:bg-zinc-900 space-y-6">
          <h3 className="text-sm font-semibold text-zinc-900 dark:text-zinc-100">
            Commercial Levers & Assumptions
          </h3>

          {/* Slider 1: Sales Volume Growth */}
          <div className="space-y-2">
            <div className="flex items-center justify-between text-xs">
              <span className="font-medium text-zinc-700 dark:text-zinc-300">
                Sales Volume Growth
              </span>
              <span className="font-bold text-indigo-600 dark:text-indigo-400">
                {revenueGrowth > 0 ? `+${revenueGrowth}%` : `${revenueGrowth}%`}
              </span>
            </div>
            <input
              type="range"
              min="-30"
              max="50"
              step="1"
              value={revenueGrowth}
              onChange={(e) => setRevenueGrowth(Number(e.target.value))}
              className="w-full accent-indigo-600 cursor-pointer"
            />
            <div className="flex justify-between text-[10px] text-zinc-400">
              <span>-30% Contraction</span>
              <span>Baseline (0%)</span>
              <span>+50% Expansion</span>
            </div>
          </div>

          {/* Slider 2: Price Adjustment */}
          <div className="space-y-2">
            <div className="flex items-center justify-between text-xs">
              <span className="font-medium text-zinc-700 dark:text-zinc-300">
                Unit Price Adjustment
              </span>
              <span className="font-bold text-indigo-600 dark:text-indigo-400">
                {priceChange > 0 ? `+${priceChange}%` : `${priceChange}%`}
              </span>
            </div>
            <input
              type="range"
              min="-20"
              max="30"
              step="1"
              value={priceChange}
              onChange={(e) => setPriceChange(Number(e.target.value))}
              className="w-full accent-indigo-600 cursor-pointer"
            />
            <div className="flex justify-between text-[10px] text-zinc-400">
              <span>-20% Price Cut</span>
              <span>Current Price</span>
              <span>+30% Premium</span>
            </div>
          </div>

          {/* Slider 3: Discount Rate Shift */}
          <div className="space-y-2">
            <div className="flex items-center justify-between text-xs">
              <span className="font-medium text-zinc-700 dark:text-zinc-300">
                Promotional Discount Reduction
              </span>
              <span className="font-bold text-emerald-600 dark:text-emerald-400">
                {discountChange > 0 ? `+${discountChange}%` : `${discountChange}%`}
              </span>
            </div>
            <input
              type="range"
              min="-15"
              max="20"
              step="1"
              value={discountChange}
              onChange={(e) => setDiscountChange(Number(e.target.value))}
              className="w-full accent-emerald-600 cursor-pointer"
            />
            <div className="flex justify-between text-[10px] text-zinc-400">
              <span>More Discounts (-15%)</span>
              <span>Zero Shift</span>
              <span>Tighter Margins (+20%)</span>
            </div>
          </div>

          {/* Slider 4: Churn Recovery */}
          <div className="space-y-2">
            <div className="flex items-center justify-between text-xs">
              <span className="font-medium text-zinc-700 dark:text-zinc-300">
                Churn Customer Recovery Rate
              </span>
              <span className="font-bold text-indigo-600 dark:text-indigo-400">
                {churnReduction}%
              </span>
            </div>
            <input
              type="range"
              min="0"
              max="50"
              step="5"
              value={churnReduction}
              onChange={(e) => setChurnReduction(Number(e.target.value))}
              className="w-full accent-indigo-600 cursor-pointer"
            />
            <div className="flex justify-between text-[10px] text-zinc-400">
              <span>0% Recovered</span>
              <span>25% Win-Back</span>
              <span>50% Win-Back</span>
            </div>
          </div>
        </div>

        {/* Right: Projected Outcome Display (5 Cols) */}
        <div className="lg:col-span-5 flex flex-col justify-between rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm dark:border-zinc-800 dark:bg-zinc-900 space-y-6">
          <div>
            <span className="text-[11px] font-semibold text-zinc-400 uppercase tracking-wider">
              Simulated Financial Outcome
            </span>

            <div className="mt-4 space-y-4">
              <div>
                <span className="text-xs text-zinc-500 dark:text-zinc-400">Simulated Revenue</span>
                <p className="text-3xl font-extrabold text-zinc-900 dark:text-zinc-100">
                  ${simulatedRevenue.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                </p>
                <span
                  className={`inline-block mt-1 rounded-full px-2.5 py-0.5 text-xs font-bold ${
                    revenueDelta >= 0
                      ? "bg-emerald-50 text-emerald-700 dark:bg-emerald-950/40 dark:text-emerald-300"
                      : "bg-rose-50 text-rose-700 dark:bg-rose-950/40 dark:text-rose-300"
                  }`}
                >
                  {revenueDelta >= 0 ? `+` : ""}${revenueDelta.toLocaleString()} ({revenueDeltaPct > 0 ? `+` : ""}{revenueDeltaPct}%)
                </span>
              </div>

              <div className="grid grid-cols-2 gap-3 pt-3 border-t border-zinc-100 dark:border-zinc-800 text-xs">
                <div>
                  <span className="text-zinc-400">Gross Margin</span>
                  <p className="font-bold text-zinc-900 dark:text-zinc-100 mt-0.5">
                    ${simulatedMargin.toLocaleString()}
                  </p>
                  <span className="text-[10px] text-emerald-600">
                    {marginDelta >= 0 ? `+` : ""}${marginDelta.toLocaleString()}
                  </span>
                </div>

                <div>
                  <span className="text-zinc-400">Churn Recovered</span>
                  <p className="font-bold text-zinc-900 dark:text-zinc-100 mt-0.5">
                    ${recoveredChurn.toLocaleString()}
                  </p>
                </div>
              </div>

              {/* Simulation Narrative */}
              <div className="space-y-1.5 pt-3 border-t border-zinc-100 dark:border-zinc-800">
                {insights.map((ins, i) => (
                  <p key={i} className="text-[11px] text-zinc-600 dark:text-zinc-300 flex items-center gap-1.5">
                    <span className="text-indigo-600 font-bold">→</span> {ins}
                  </p>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
