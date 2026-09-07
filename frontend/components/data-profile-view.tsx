"use client";

import { useState } from "react";

export interface ColumnStats {
  min?: number | string | null;
  max?: number | string | null;
  mean?: number | null;
  median?: number | null;
  std?: number | null;
}

export interface ColumnProfile {
  name: string;
  index: number;
  detected_type: string;
  null_count: number;
  null_percentage: number;
  unique_count: number;
  sample_values: (string | number)[];
  stats?: ColumnStats | null;
  is_likely_id: boolean;
  is_likely_metric: boolean;
  is_likely_dimension: boolean;
  is_likely_date: boolean;
  warnings: string[];
}

export interface SheetProfile {
  sheet_name: string;
  row_count: number;
  column_count: number;
  duplicate_rows_count: number;
  columns: ColumnProfile[];
  warnings: string[];
}

export interface DataProfileResponse {
  file_id: string;
  file_name: string;
  total_sheets: number;
  sheets: SheetProfile[];
  data_quality_score: number;
  overall_warnings: string[];
}

interface DataProfileViewProps {
  profile: DataProfileResponse;
  onContinueToMapping?: () => void;
}

export default function DataProfileView({ profile, onContinueToMapping }: DataProfileViewProps) {
  const [selectedSheetIndex, setSelectedSheetIndex] = useState(0);

  const currentSheet = profile.sheets[selectedSheetIndex] || profile.sheets[0];

  const getScoreColor = (score: number) => {
    if (score >= 90) return "text-emerald-600 bg-emerald-50 border-emerald-200 dark:bg-emerald-950/30 dark:border-emerald-800/50 dark:text-emerald-400";
    if (score >= 70) return "text-amber-600 bg-amber-50 border-amber-200 dark:bg-amber-950/30 dark:border-amber-800/50 dark:text-amber-400";
    return "text-rose-600 bg-rose-50 border-rose-200 dark:bg-rose-950/30 dark:border-rose-800/50 dark:text-rose-400";
  };

  const getTypeBadge = (type: string) => {
    switch (type.toLowerCase()) {
      case "numeric":
        return "bg-blue-50 text-blue-700 border-blue-200 dark:bg-blue-950/40 dark:text-blue-300 dark:border-blue-800";
      case "datetime":
        return "bg-purple-50 text-purple-700 border-purple-200 dark:bg-purple-950/40 dark:text-purple-300 dark:border-purple-800";
      case "categorical":
        return "bg-emerald-50 text-emerald-700 border-emerald-200 dark:bg-emerald-950/40 dark:text-emerald-300 dark:border-emerald-800";
      case "boolean":
        return "bg-amber-50 text-amber-700 border-amber-200 dark:bg-amber-950/40 dark:text-amber-300 dark:border-amber-800";
      default:
        return "bg-zinc-100 text-zinc-700 border-zinc-200 dark:bg-zinc-800 dark:text-zinc-300 dark:border-zinc-700";
    }
  };

  return (
    <div className="space-y-6">
      {/* Header Card: File overview & quality score */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
        <div>
          <div className="flex items-center gap-2">
            <span className="flex h-2 w-2 rounded-full bg-emerald-500" />
            <h2 className="text-lg font-semibold text-zinc-900 dark:text-zinc-100">
              {profile.file_name}
            </h2>
          </div>
          <p className="mt-1 text-xs text-zinc-500 dark:text-zinc-400">
            {profile.total_sheets} sheet{profile.total_sheets > 1 ? "s" : ""} analyzed • Ready for AI mapping
          </p>
        </div>

        <div className="flex items-center gap-4">
          <div className={`flex items-center gap-2 rounded-xl border px-3.5 py-1.5 text-sm font-semibold ${getScoreColor(profile.data_quality_score)}`}>
            <span>Data Health:</span>
            <span className="text-base font-bold">{profile.data_quality_score}%</span>
          </div>

          {onContinueToMapping && (
            <button
              onClick={onContinueToMapping}
              className="rounded-xl bg-indigo-600 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-700 transition-colors dark:bg-indigo-500 dark:hover:bg-indigo-600"
            >
              Proceed to Mapping →
            </button>
          )}
        </div>
      </div>

      {/* Multi-sheet Tabs if workbook has multiple sheets */}
      {profile.total_sheets > 1 && (
        <div className="flex items-center gap-2 border-b border-zinc-200 dark:border-zinc-800 pb-2">
          {profile.sheets.map((sheet, index) => (
            <button
              key={sheet.sheet_name}
              onClick={() => setSelectedSheetIndex(index)}
              className={`rounded-lg px-3 py-1.5 text-xs font-medium transition-colors ${
                selectedSheetIndex === index
                  ? "bg-zinc-900 text-white dark:bg-zinc-100 dark:text-zinc-900"
                  : "bg-zinc-100 text-zinc-600 hover:bg-zinc-200 dark:bg-zinc-800 dark:text-zinc-400 dark:hover:bg-zinc-700"
              }`}
            >
              {sheet.sheet_name} ({sheet.row_count} rows)
            </button>
          ))}
        </div>
      )}

      {/* Sheet Summary Metrics */}
      {currentSheet && (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <div className="rounded-xl border border-zinc-200 bg-white p-4 dark:border-zinc-800 dark:bg-zinc-900">
            <span className="text-xs font-medium text-zinc-500 dark:text-zinc-400">Total Records</span>
            <p className="mt-1 text-xl font-bold text-zinc-900 dark:text-zinc-100">
              {currentSheet.row_count.toLocaleString()}
            </p>
          </div>
          <div className="rounded-xl border border-zinc-200 bg-white p-4 dark:border-zinc-800 dark:bg-zinc-900">
            <span className="text-xs font-medium text-zinc-500 dark:text-zinc-400">Total Columns</span>
            <p className="mt-1 text-xl font-bold text-zinc-900 dark:text-zinc-100">
              {currentSheet.column_count}
            </p>
          </div>
          <div className="rounded-xl border border-zinc-200 bg-white p-4 dark:border-zinc-800 dark:bg-zinc-900">
            <span className="text-xs font-medium text-zinc-500 dark:text-zinc-400">Duplicate Rows</span>
            <p className="mt-1 text-xl font-bold text-zinc-900 dark:text-zinc-100">
              {currentSheet.duplicate_rows_count}
            </p>
          </div>
          <div className="rounded-xl border border-zinc-200 bg-white p-4 dark:border-zinc-800 dark:bg-zinc-900">
            <span className="text-xs font-medium text-zinc-500 dark:text-zinc-400">Inferred Dimensions</span>
            <p className="mt-1 text-xl font-bold text-zinc-900 dark:text-zinc-100">
              {currentSheet.columns.filter((c) => c.is_likely_dimension).length}
            </p>
          </div>
        </div>
      )}

      {/* Column Detail Table */}
      {currentSheet && (
        <div className="overflow-hidden rounded-2xl border border-zinc-200 bg-white shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
          <div className="px-6 py-4 border-b border-zinc-200 dark:border-zinc-800">
            <h3 className="text-sm font-semibold text-zinc-900 dark:text-zinc-100">
              Schema & Column Profile ({currentSheet.columns.length} columns)
            </h3>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="border-b border-zinc-200 bg-zinc-50/50 text-zinc-500 dark:border-zinc-800 dark:bg-zinc-800/40 dark:text-zinc-400">
                <tr>
                  <th className="py-3 px-4 font-medium">#</th>
                  <th className="py-3 px-4 font-medium">Column Name</th>
                  <th className="py-3 px-4 font-medium">Type</th>
                  <th className="py-3 px-4 font-medium">Roles</th>
                  <th className="py-3 px-4 font-medium">Completeness</th>
                  <th className="py-3 px-4 font-medium">Sample Values</th>
                  <th className="py-3 px-4 font-medium">Summary Stats</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-zinc-200 dark:divide-zinc-800">
                {currentSheet.columns.map((col, idx) => (
                  <tr key={col.name} className="hover:bg-zinc-50/50 dark:hover:bg-zinc-800/30 transition-colors">
                    <td className="py-3 px-4 text-zinc-400">{idx + 1}</td>
                    <td className="py-3 px-4 font-semibold text-zinc-900 dark:text-zinc-100">
                      {col.name}
                      {col.warnings.length > 0 && (
                        <span className="block text-[10px] text-amber-600 dark:text-amber-400 mt-0.5">
                          ⚠️ {col.warnings.join("; ")}
                        </span>
                      )}
                    </td>
                    <td className="py-3 px-4">
                      <span className={`inline-block rounded-md border px-2 py-0.5 text-[11px] font-medium capitalize ${getTypeBadge(col.detected_type)}`}>
                        {col.detected_type}
                      </span>
                    </td>
                    <td className="py-3 px-4">
                      <div className="flex flex-wrap gap-1">
                        {col.is_likely_metric && (
                          <span className="rounded bg-indigo-50 px-1.5 py-0.5 text-[10px] font-medium text-indigo-700 dark:bg-indigo-950/40 dark:text-indigo-300">
                            Metric
                          </span>
                        )}
                        {col.is_likely_dimension && (
                          <span className="rounded bg-teal-50 px-1.5 py-0.5 text-[10px] font-medium text-teal-700 dark:bg-teal-950/40 dark:text-teal-300">
                            Dimension
                          </span>
                        )}
                        {col.is_likely_id && (
                          <span className="rounded bg-zinc-100 px-1.5 py-0.5 text-[10px] font-medium text-zinc-700 dark:bg-zinc-800 dark:text-zinc-300">
                            ID
                          </span>
                        )}
                        {col.is_likely_date && (
                          <span className="rounded bg-purple-50 px-1.5 py-0.5 text-[10px] font-medium text-purple-700 dark:bg-purple-950/40 dark:text-purple-300">
                            Date
                          </span>
                        )}
                      </div>
                    </td>
                    <td className="py-3 px-4">
                      <div className="flex items-center gap-2">
                        <div className="h-1.5 w-16 rounded-full bg-zinc-200 dark:bg-zinc-700 overflow-hidden">
                          <div
                            className="h-full bg-emerald-500"
                            style={{ width: `${100 - col.null_percentage}%` }}
                          />
                        </div>
                        <span className="text-[11px] text-zinc-600 dark:text-zinc-400">
                          {100 - col.null_percentage}%
                        </span>
                      </div>
                    </td>
                    <td className="py-3 px-4">
                      <div className="flex flex-wrap gap-1 max-w-xs">
                        {col.sample_values.slice(0, 3).map((val, i) => (
                          <span
                            key={i}
                            className="truncate max-w-[100px] rounded bg-zinc-100 px-1.5 py-0.5 text-[10px] text-zinc-600 dark:bg-zinc-800 dark:text-zinc-400"
                          >
                            {String(val)}
                          </span>
                        ))}
                      </div>
                    </td>
                    <td className="py-3 px-4 text-zinc-500 dark:text-zinc-400 font-mono text-[11px]">
                      {col.stats ? (
                        <div>
                          {col.stats.min !== undefined && col.stats.min !== null && (
                            <div>Min: {String(col.stats.min)}</div>
                          )}
                          {col.stats.max !== undefined && col.stats.max !== null && (
                            <div>Max: {String(col.stats.max)}</div>
                          )}
                          {col.stats.mean !== undefined && col.stats.mean !== null && (
                            <div>Avg: {col.stats.mean}</div>
                          )}
                        </div>
                      ) : (
                        <span className="text-zinc-400">—</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
