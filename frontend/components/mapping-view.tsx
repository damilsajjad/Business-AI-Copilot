"use client";

import { useEffect, useState } from "react";
import { apiJson } from "@/lib/api";
import { type DataProfileResponse } from "./data-profile-view";

export interface CanonicalField {
  name: string;
  label: string;
  description: string;
  required: boolean;
  expected_type: string;
  category: string;
  example_column_names: string[];
}

export interface ColumnMappingItem {
  target_field: string;
  source_sheet: string;
  source_column: string;
  confidence: number;
  reasoning: string;
}

export interface MappingProposalResponse {
  file_id: string;
  mappings: ColumnMappingItem[];
  unmapped_columns: string[];
  confidence_score: number;
  suggested_by: string;
}

interface MappingViewProps {
  businessId: string;
  fileId: string;
  profile: DataProfileResponse;
  onBackToProfile: () => void;
  onConfirmSuccess: () => void;
}

export default function MappingView({
  businessId,
  fileId,
  profile,
  onBackToProfile,
  onConfirmSuccess,
}: MappingViewProps) {
  const [canonicalFields, setCanonicalFields] = useState<CanonicalField[]>([]);
  const [selectedMappings, setSelectedMappings] = useState<Record<string, { sheet: string; column: string; confidence: number; reasoning: string }>>({});
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [suggestedBy, setSuggestedBy] = useState<string>("heuristic");
  const [error, setError] = useState<string | null>(null);

  // Flatten available columns across sheets
  const availableColumns = profile.sheets.flatMap((sheet) =>
    sheet.columns.map((col) => ({
      sheet: sheet.sheet_name,
      column: col.name,
      type: col.detected_type,
      key: `${sheet.sheet_name}::${col.name}`,
    }))
  );

  useEffect(() => {
    let isMounted = true;

    async function fetchMappingProposal() {
      try {
        const [schema, proposal] = await Promise.all([
          apiJson<CanonicalField[]>("/api/v1/canonical-schema"),
          apiJson<MappingProposalResponse>(
            `/api/v1/businesses/${businessId}/uploads/${fileId}/mapping/propose`,
            { method: "POST" }
          ),
        ]);

        if (!isMounted) return;

        setCanonicalFields(schema);
        setSuggestedBy(proposal.suggested_by);

        const mapObj: Record<string, { sheet: string; column: string; confidence: number; reasoning: string }> = {};
        proposal.mappings.forEach((m) => {
          mapObj[m.target_field] = {
            sheet: m.source_sheet,
            column: m.source_column,
            confidence: m.confidence,
            reasoning: m.reasoning,
          };
        });
        setSelectedMappings(mapObj);
      } catch (err: unknown) {
        if (isMounted) {
          setError(err instanceof Error ? err.message : "Failed to load mapping proposal");
        }
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    }

    fetchMappingProposal();

    return () => {
      isMounted = false;
    };
  }, [businessId, fileId]);

  function handleSelectChange(targetField: string, value: string) {
    if (!value) {
      setSelectedMappings((prev) => {
        const copy = { ...prev };
        delete copy[targetField];
        return copy;
      });
      return;
    }

    const [sheet, column] = value.split("::");
    setSelectedMappings((prev) => ({
      ...prev,
      [targetField]: {
        sheet,
        column,
        confidence: 1.0,
        reasoning: "Manually selected by user.",
      },
    }));
  }

  // Client-side quick validation check
  const isDateMapped = !!selectedMappings["order_date"];
  const isRevenueMapped = !!selectedMappings["total_revenue"] || (!!selectedMappings["quantity"] && !!selectedMappings["unit_price"]);
  const canSubmit = isDateMapped && isRevenueMapped && !saving;

  async function handleConfirm() {
    setSaving(true);
    setError(null);

    const payloadMappings: ColumnMappingItem[] = Object.entries(selectedMappings).map(
      ([target_field, val]) => ({
        target_field,
        source_sheet: val.sheet,
        source_column: val.column,
        confidence: val.confidence,
        reasoning: val.reasoning,
      })
    );

    try {
      await apiJson(`/api/v1/businesses/${businessId}/uploads/${fileId}/mapping/confirm`, {
        method: "POST",
        body: JSON.stringify({ mappings: payloadMappings }),
      });
      onConfirmSuccess();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to confirm mappings.");
    } finally {
      setSaving(false);
    }
  }

  if (loading) {
    return (
      <div className="flex h-64 flex-col items-center justify-center rounded-2xl border border-zinc-200 bg-white dark:border-zinc-800 dark:bg-zinc-900">
        <svg
          className="h-8 w-8 animate-spin text-indigo-600 mb-2"
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
        >
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
        </svg>
        <p className="text-sm text-zinc-500">AI is proposing optimal column mappings...</p>
      </div>
    );
  }

  const categories = [
    { key: "essential", label: "Core Analytics (Required)" },
    { key: "financial", label: "Financial & Revenue" },
    { key: "product", label: "Products & Demand" },
    { key: "customer", label: "Customers & Churn Analysis" },
    { key: "dimension", label: "Channels & Dimensions" },
  ];

  return (
    <div className="space-y-6">
      {/* Header card */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
        <div>
          <div className="flex items-center gap-2">
            <span className="rounded-md bg-indigo-50 px-2 py-0.5 text-xs font-semibold text-indigo-700 dark:bg-indigo-950/50 dark:text-indigo-300 capitalize">
              {suggestedBy === "gemini" ? "✨ Gemini AI Proposed" : "⚡ Inferred Mapping"}
            </span>
            <h2 className="text-lg font-semibold text-zinc-900 dark:text-zinc-100">
              Confirm Column Mapping
            </h2>
          </div>
          <p className="mt-1 text-xs text-zinc-500 dark:text-zinc-400">
            Review and adjust how columns in <span className="font-semibold text-zinc-800 dark:text-zinc-200">{profile.file_name}</span> map to standard business metrics.
          </p>
        </div>

        <button
          onClick={onBackToProfile}
          className="rounded-xl border border-zinc-200 bg-white px-3.5 py-2 text-xs font-medium text-zinc-700 shadow-sm hover:bg-zinc-50 dark:border-zinc-700 dark:bg-zinc-800 dark:text-zinc-300 dark:hover:bg-zinc-700"
        >
          ← Back to Dataset Profile
        </button>
      </div>

      {error && (
        <div className="rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700 dark:border-red-900/50 dark:bg-red-950/20 dark:text-red-400">
          {error}
        </div>
      )}

      {/* Field Mapping Groups */}
      <div className="space-y-6">
        {categories.map((cat) => {
          const fields = canonicalFields.filter((f) => f.category === cat.key || (!f.category && cat.key === "dimension"));
          if (fields.length === 0) return null;

          return (
            <div key={cat.key} className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
              <h3 className="text-sm font-semibold text-zinc-900 dark:text-zinc-100 mb-4 pb-2 border-b border-zinc-100 dark:border-zinc-800">
                {cat.label}
              </h3>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {fields.map((field) => {
                  const currentMapping = selectedMappings[field.name];
                  const currentKey = currentMapping ? `${currentMapping.sheet}::${currentMapping.column}` : "";

                  return (
                    <div
                      key={field.name}
                      className="flex flex-col justify-between rounded-xl border border-zinc-100 bg-zinc-50/50 p-4 dark:border-zinc-800/80 dark:bg-zinc-800/20"
                    >
                      <div>
                        <div className="flex items-center justify-between gap-2">
                          <span className="text-sm font-semibold text-zinc-900 dark:text-zinc-100">
                            {field.label}
                          </span>
                          {field.required ? (
                            <span className="rounded bg-rose-50 px-1.5 py-0.5 text-[10px] font-bold text-rose-600 dark:bg-rose-950/50 dark:text-rose-400">
                              Required
                            </span>
                          ) : (
                            <span className="text-[10px] text-zinc-400">Optional</span>
                          )}
                        </div>
                        <p className="mt-1 text-xs text-zinc-500 dark:text-zinc-400 line-clamp-2">
                          {field.description}
                        </p>
                      </div>

                      <div className="mt-3">
                        <select
                          value={currentKey}
                          onChange={(e) => handleSelectChange(field.name, e.target.value)}
                          className="w-full rounded-lg border border-zinc-300 bg-white py-2 px-3 text-xs text-zinc-900 focus:border-indigo-500 focus:outline-none dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-100"
                        >
                          <option value="">-- Do not map --</option>
                          {availableColumns.map((col) => (
                            <option key={col.key} value={col.key}>
                              {profile.total_sheets > 1 ? `[${col.sheet}] ` : ""}{col.column} ({col.type})
                            </option>
                          ))}
                        </select>

                        {currentMapping && (
                          <div className="mt-1.5 flex items-center justify-between text-[11px] text-zinc-500 dark:text-zinc-400">
                            <span className="text-indigo-600 dark:text-indigo-400 truncate max-w-[200px]">
                              {currentMapping.reasoning || "Mapped"}
                            </span>
                            <span className="font-semibold text-zinc-600 dark:text-zinc-300">
                              {Math.round(currentMapping.confidence * 100)}% match
                            </span>
                          </div>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          );
        })}
      </div>

      {/* Confirmation Sticky Footer */}
      <div className="sticky bottom-4 z-10 flex flex-col sm:flex-row sm:items-center justify-between gap-4 rounded-2xl border border-zinc-200 bg-white/95 p-4 shadow-lg backdrop-blur-md dark:border-zinc-800 dark:bg-zinc-900/95">
        <div className="text-xs">
          {!isDateMapped ? (
            <span className="text-rose-600 dark:text-rose-400 font-medium">
              ⚠️ Please map &quot;Order Date&quot; to continue.
            </span>
          ) : !isRevenueMapped ? (
            <span className="text-rose-600 dark:text-rose-400 font-medium">
              ⚠️ Please map &quot;Total Revenue&quot; or both &quot;Quantity&quot; and &quot;Unit Price&quot;.
            </span>
          ) : (
            <span className="text-emerald-600 dark:text-emerald-400 font-medium">
              ✓ All required core fields are mapped.
            </span>
          )}
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={onBackToProfile}
            className="rounded-xl border border-zinc-200 bg-white px-4 py-2 text-sm font-medium text-zinc-700 hover:bg-zinc-50 dark:border-zinc-700 dark:bg-zinc-800 dark:text-zinc-300"
          >
            Cancel
          </button>
          <button
            onClick={handleConfirm}
            disabled={!canSubmit}
            className="rounded-xl bg-indigo-600 px-5 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed dark:bg-indigo-500 dark:hover:bg-indigo-600"
          >
            {saving ? "Saving Mapping..." : "Confirm & Run Analysis →"}
          </button>
        </div>
      </div>
    </div>
  );
}
