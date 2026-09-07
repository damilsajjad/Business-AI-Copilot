"use client";

import { useState } from "react";

export interface DomainInsight {
  domain: string;
  headline: string;
  summary: string;
  key_metrics: Record<string, string | number>;
  positives: string[];
  concerns: string[];
}

export interface ExecutiveBriefReport {
  file_id: string;
  business_id: string;
  generated_at: string;
  executive_summary: string;
  health_score: number;
  domain_insights: DomainInsight[];
  key_risks: string[];
  strategic_opportunities: string[];
  recommended_initiatives: string[];
  synthesized_by: string;
}

interface InsightsViewProps {
  brief: ExecutiveBriefReport;
  onRefresh?: () => void;
}

export default function InsightsView({ brief, onRefresh }: InsightsViewProps) {
  const [selectedDomain, setSelectedDomain] = useState<string>("all");

  const displayedDomains =
    selectedDomain === "all"
      ? brief.domain_insights
      : brief.domain_insights.filter((d) => d.domain === selectedDomain);

  return (
    <div className="space-y-6">
      {/* Executive Header & Health Score */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-6 rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
        <div className="space-y-2 max-w-2xl">
          <div className="flex items-center gap-2">
            <span className="flex h-2.5 w-2.5 rounded-full bg-indigo-500 animate-pulse" />
            <span className="text-xs font-semibold text-indigo-700 dark:text-indigo-400 uppercase tracking-wider">
              {brief.synthesized_by}
            </span>
          </div>
          <h2 className="text-xl font-bold text-zinc-900 dark:text-zinc-100">
            Executive Performance Brief
          </h2>
          <p className="text-xs text-zinc-600 dark:text-zinc-300 leading-relaxed">
            {brief.executive_summary}
          </p>
          {onRefresh && (
            <button
              onClick={onRefresh}
              className="mt-2 inline-flex rounded-lg border border-zinc-200 bg-white px-3 py-1.5 text-xs font-medium text-zinc-700 shadow-sm hover:bg-zinc-50 dark:border-zinc-700 dark:bg-zinc-800 dark:text-zinc-300"
            >
              ↻ Re-synthesize Brief
            </button>
          )}
        </div>

        {/* Health Score Gauge */}
        <div className="flex sm:flex-col items-center justify-center p-4 rounded-2xl bg-zinc-50 dark:bg-zinc-800/60 border border-zinc-100 dark:border-zinc-800 min-w-[140px] text-center">
          <span className="text-3xl font-black text-indigo-600 dark:text-indigo-400">
            {brief.health_score}
            <span className="text-sm font-normal text-zinc-400">/100</span>
          </span>
          <span className="text-[11px] font-semibold text-zinc-700 dark:text-zinc-300 mt-0.5">
            Business Health
          </span>
          <span className="text-[10px] text-emerald-600 dark:text-emerald-400">
            {brief.health_score >= 75 ? "Strong Performance" : brief.health_score >= 55 ? "Stable Growth" : "Attention Required"}
          </span>
        </div>
      </div>

      {/* Strategic Priorities & Risks Split */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Risks */}
        <div className="rounded-2xl border border-rose-100 bg-rose-50/40 p-6 shadow-sm dark:border-rose-950/50 dark:bg-rose-950/10">
          <div className="flex items-center gap-2 mb-3">
            <span className="text-base">⚠️</span>
            <h3 className="text-sm font-bold text-rose-900 dark:text-rose-200">
              Critical Strategic Risks
            </h3>
          </div>
          <ul className="space-y-2">
            {brief.key_risks.map((risk, i) => (
              <li key={i} className="text-xs text-rose-800 dark:text-rose-300 flex items-start gap-2">
                <span className="text-rose-500 font-bold">•</span>
                <span>{risk}</span>
              </li>
            ))}
          </ul>
        </div>

        {/* Opportunities */}
        <div className="rounded-2xl border border-emerald-100 bg-emerald-50/40 p-6 shadow-sm dark:border-emerald-950/50 dark:bg-emerald-950/10">
          <div className="flex items-center gap-2 mb-3">
            <span className="text-base">🚀</span>
            <h3 className="text-sm font-bold text-emerald-900 dark:text-emerald-200">
              High-Value Opportunities
            </h3>
          </div>
          <ul className="space-y-2">
            {brief.strategic_opportunities.map((opp, i) => (
              <li key={i} className="text-xs text-emerald-800 dark:text-emerald-300 flex items-start gap-2">
                <span className="text-emerald-500 font-bold">•</span>
                <span>{opp}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>

      {/* Domain Insights Grid */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-base font-semibold text-zinc-900 dark:text-zinc-100">
            Domain-Specialized Insights
          </h3>

          <div className="flex items-center gap-1 rounded-xl bg-zinc-100 p-1 dark:bg-zinc-800">
            <button
              onClick={() => setSelectedDomain("all")}
              className={`rounded-lg px-3 py-1 text-xs font-medium capitalize transition-colors ${
                selectedDomain === "all"
                  ? "bg-white text-zinc-900 shadow-sm dark:bg-zinc-700 dark:text-zinc-100"
                  : "text-zinc-600 hover:text-zinc-900 dark:text-zinc-400"
              }`}
            >
              All Domains
            </button>
            {brief.domain_insights.map((d) => (
              <button
                key={d.domain}
                onClick={() => setSelectedDomain(d.domain)}
                className={`rounded-lg px-3 py-1 text-xs font-medium capitalize transition-colors ${
                  selectedDomain === d.domain
                    ? "bg-white text-zinc-900 shadow-sm dark:bg-zinc-700 dark:text-zinc-100"
                    : "text-zinc-600 hover:text-zinc-900 dark:text-zinc-400"
                }`}
              >
                {d.domain}
              </button>
            ))}
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {displayedDomains.map((d) => (
            <div
              key={d.domain}
              className="rounded-2xl border border-zinc-200 bg-white p-5 shadow-sm dark:border-zinc-800 dark:bg-zinc-900 space-y-3"
            >
              <div className="flex items-center justify-between">
                <span className="rounded-full bg-indigo-50 px-2.5 py-0.5 text-[10px] font-bold text-indigo-700 dark:bg-indigo-950/40 dark:text-indigo-300 uppercase tracking-wider">
                  {d.domain} Agent
                </span>
              </div>

              <h4 className="text-sm font-semibold text-zinc-900 dark:text-zinc-100">
                {d.headline}
              </h4>
              <p className="text-xs text-zinc-500 dark:text-zinc-400 leading-relaxed">
                {d.summary}
              </p>

              {/* Positives & Concerns */}
              <div className="space-y-1.5 pt-2 border-t border-zinc-100 dark:border-zinc-800">
                {d.positives.map((p, i) => (
                  <p key={i} className="text-[11px] text-emerald-700 dark:text-emerald-400 flex items-center gap-1.5">
                    <span>✓</span> {p}
                  </p>
                ))}
                {d.concerns.map((c, i) => (
                  <p key={i} className="text-[11px] text-rose-600 dark:text-rose-400 flex items-center gap-1.5">
                    <span>!</span> {c}
                  </p>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
