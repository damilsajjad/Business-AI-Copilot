"use client";

import { useState } from "react";
import { apiJson } from "@/lib/api";

export interface ActionItem {
  id: string;
  title: string;
  domain: string;
  urgency: "high" | "medium" | "low" | string;
  expected_impact: string;
  effort: "low" | "medium" | "high" | string;
  timeframe: string;
  action_steps: string[];
  owner: string;
  risk_if_ignored: string;
  status: "pending" | "in_progress" | "completed" | "dismissed" | string;
}

interface ActionCenterProps {
  businessId: string;
  fileId: string;
  initialActions: ActionItem[];
}

export default function ActionCenter({ businessId, fileId, initialActions }: ActionCenterProps) {
  const [actions, setActions] = useState<ActionItem[]>(initialActions);
  const [updatingId, setUpdatingId] = useState<string | null>(null);
  const [filterDomain, setFilterDomain] = useState<string>("all");

  async function handleStatusChange(actionId: string, newStatus: string) {
    setUpdatingId(actionId);
    try {
      const updated = await apiJson<ActionItem>(
        `/api/v1/businesses/${businessId}/uploads/${fileId}/actions/${actionId}`,
        {
          method: "PATCH",
          body: JSON.stringify({ status: newStatus }),
        }
      );

      setActions((prev) => prev.map((item) => (item.id === actionId ? updated : item)));
    } catch (err) {
      console.error("Failed to update action status:", err);
    } finally {
      setUpdatingId(null);
    }
  }

  const filteredActions =
    filterDomain === "all"
      ? actions
      : actions.filter((a) => a.domain === filterDomain);

  const completedCount = actions.filter((a) => a.status === "completed").length;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
        <div>
          <div className="flex items-center gap-2">
            <span className="flex h-2.5 w-2.5 rounded-full bg-emerald-500 animate-pulse" />
            <span className="text-xs font-semibold text-emerald-700 dark:text-emerald-400 uppercase tracking-wider">
              Autonomous Decision Support
            </span>
          </div>
          <h2 className="mt-1 text-xl font-bold text-zinc-900 dark:text-zinc-100">
            Action Center & Strategic Initiatives
          </h2>
          <p className="mt-0.5 text-xs text-zinc-500 dark:text-zinc-400">
            Prioritized operational playbooks generated from verified data anomalies and growth bottlenecks
          </p>
        </div>

        <div className="flex items-center gap-3">
          <div className="rounded-xl bg-zinc-100 px-3.5 py-2 text-xs font-semibold text-zinc-700 dark:bg-zinc-800 dark:text-zinc-300">
            {completedCount} of {actions.length} Completed
          </div>
        </div>
      </div>

      {/* Domain Filters */}
      <div className="flex items-center gap-1 rounded-xl bg-zinc-100 p-1 dark:bg-zinc-800 w-fit">
        {(["all", "customers", "products", "inventory", "sales"] as const).map((dom) => (
          <button
            key={dom}
            onClick={() => setFilterDomain(dom)}
            className={`rounded-lg px-3 py-1 text-xs font-medium capitalize transition-colors ${
              filterDomain === dom
                ? "bg-white text-zinc-900 shadow-sm dark:bg-zinc-700 dark:text-zinc-100"
                : "text-zinc-600 hover:text-zinc-900 dark:text-zinc-400"
            }`}
          >
            {dom}
          </button>
        ))}
      </div>

      {/* Action Initiatives Cards */}
      <div className="space-y-4">
        {filteredActions.map((act) => {
          const isUpdating = updatingId === act.id;

          return (
            <div
              key={act.id}
              className={`rounded-2xl border p-6 shadow-sm transition-all ${
                act.status === "completed"
                  ? "border-emerald-200 bg-emerald-50/20 dark:border-emerald-900/40 dark:bg-emerald-950/10 opacity-75"
                  : act.status === "dismissed"
                  ? "border-zinc-200 bg-zinc-50/40 dark:border-zinc-800 opacity-50"
                  : "border-zinc-200 bg-white dark:border-zinc-800 dark:bg-zinc-900"
              }`}
            >
              <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4">
                <div className="space-y-2 flex-1">
                  <div className="flex flex-wrap items-center gap-2">
                    <span
                      className={`rounded-full px-2.5 py-0.5 text-[10px] font-bold uppercase tracking-wider ${
                        act.urgency === "high"
                          ? "bg-rose-50 text-rose-700 dark:bg-rose-950/40 dark:text-rose-300"
                          : act.urgency === "medium"
                          ? "bg-amber-50 text-amber-700 dark:bg-amber-950/40 dark:text-amber-300"
                          : "bg-indigo-50 text-indigo-700 dark:bg-indigo-950/40 dark:text-indigo-300"
                      }`}
                    >
                      {act.urgency} Urgency
                    </span>
                    <span className="rounded-full bg-zinc-100 px-2 py-0.5 text-[10px] font-medium text-zinc-600 dark:bg-zinc-800 dark:text-zinc-400 capitalize">
                      {act.domain}
                    </span>
                    <span className="text-[11px] text-zinc-400">
                      • {act.effort.toUpperCase()} Effort • {act.timeframe}
                    </span>
                  </div>

                  <h3 className="text-base font-bold text-zinc-900 dark:text-zinc-100">
                    {act.title}
                  </h3>

                  <p className="text-xs font-medium text-emerald-700 dark:text-emerald-400">
                    Expected Impact: {act.expected_impact}
                  </p>
                </div>

                {/* Status Switcher */}
                <div className="flex items-center gap-2">
                  <select
                    disabled={isUpdating}
                    value={act.status}
                    onChange={(e) => handleStatusChange(act.id, e.target.value)}
                    className="rounded-xl border border-zinc-200 bg-zinc-50 py-1.5 px-3 text-xs font-semibold text-zinc-800 focus:border-indigo-500 focus:outline-none dark:border-zinc-700 dark:bg-zinc-800 dark:text-zinc-200 cursor-pointer"
                  >
                    <option value="pending">Pending</option>
                    <option value="in_progress">In Progress</option>
                    <option value="completed">Completed</option>
                    <option value="dismissed">Dismissed</option>
                  </select>
                </div>
              </div>

              {/* Action Steps Checklist */}
              <div className="mt-4 pt-4 border-t border-zinc-100 dark:border-zinc-800 space-y-2">
                <span className="text-[11px] font-semibold text-zinc-700 dark:text-zinc-300 uppercase tracking-wider">
                  Implementation Playbook:
                </span>
                <ul className="space-y-1.5">
                  {act.action_steps.map((step, idx) => (
                    <li key={idx} className="text-xs text-zinc-600 dark:text-zinc-300 flex items-start gap-2">
                      <span className="text-indigo-600 font-bold">•</span>
                      <span>{step}</span>
                    </li>
                  ))}
                </ul>
              </div>

              {/* Owner & Risk Footer */}
              <div className="mt-4 flex flex-col sm:flex-row sm:items-center justify-between gap-2 text-[11px] text-zinc-400">
                <span>Owner: <strong className="text-zinc-700 dark:text-zinc-300">{act.owner}</strong></span>
                {act.risk_if_ignored && (
                  <span className="text-rose-600 dark:text-rose-400">
                    Risk if ignored: {act.risk_if_ignored}
                  </span>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
