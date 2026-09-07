"use client";

import { useEffect, useState, useCallback } from "react";
import { createClient } from "@/lib/supabase";
import { useRouter } from "next/navigation";
import { apiFetch, apiJson } from "@/lib/api";
import FileUpload from "@/components/file-upload";
import DataProfileView, { type DataProfileResponse } from "@/components/data-profile-view";
import MappingView from "@/components/mapping-view";
import AnalyticsOverview, { type FullAnalyticsReport } from "@/components/analytics-overview";
import ForecastView, { type SalesForecastResponse } from "@/components/forecast-view";
import ChurnView, { type CustomerChurnResponse } from "@/components/churn-view";
import InsightsView, { type ExecutiveBriefReport } from "@/components/insights-view";
import CopilotChat from "@/components/copilot-chat";
import ActionCenter, { type ActionItem } from "@/components/action-center";
import WhatIfSimulator from "@/components/what-if-simulator";
import type { User } from "@supabase/supabase-js";

interface Business {
  id: string;
  name: string;
  industry: string;
  description: string;
  role: string;
}

interface UploadedFileItem {
  id: string;
  original_filename: string;
  file_type: string;
  file_size_bytes: number;
  status: string;
  sheet_count: number;
  created_at: string;
}

type ActiveTab = "overview" | "forecast" | "churn" | "insights" | "copilot" | "actions" | "simulator";

export default function DashboardPage() {
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  const [businesses, setBusinesses] = useState<Business[]>([]);
  const [selectedBusiness, setSelectedBusiness] = useState<Business | null>(null);
  const [newBusinessName, setNewBusinessName] = useState("");
  const [newIndustry, setNewIndustry] = useState("Retail / E-Commerce");
  const [showNewWorkspaceModal, setShowNewWorkspaceModal] = useState(false);
  const [creatingBusiness, setCreatingBusiness] = useState(false);

  const [uploads, setUploads] = useState<UploadedFileItem[]>([]);
  const [activeProfile, setActiveProfile] = useState<DataProfileResponse | null>(null);
  const [activeFileId, setActiveFileId] = useState<string | null>(null);
  const [isMappingMode, setIsMappingMode] = useState(false);
  const [loadingProfile, setLoadingProfile] = useState(false);

  // Tabbed Intelligence State
  const [activeTab, setActiveTab] = useState<ActiveTab>("overview");
  const [analyticsReport, setAnalyticsReport] = useState<FullAnalyticsReport | null>(null);
  const [forecastReport, setForecastReport] = useState<SalesForecastResponse | null>(null);
  const [churnReport, setChurnReport] = useState<CustomerChurnResponse | null>(null);
  const [insightsReport, setInsightsReport] = useState<ExecutiveBriefReport | null>(null);
  const [actionsList, setActionsList] = useState<ActionItem[]>([]);
  const [runningAnalysis, setRunningAnalysis] = useState(false);
  const [tabLoading, setTabLoading] = useState(false);

  const fetchAnalytics = useCallback(async (businessId: string, fileId: string) => {
    try {
      const report = await apiJson<FullAnalyticsReport>(
        `/api/v1/businesses/${businessId}/uploads/${fileId}/analytics`
      );
      setAnalyticsReport(report);
      return report;
    } catch {
      setAnalyticsReport(null);
      return null;
    }
  }, []);

  const loadTabData = useCallback(
    async (tab: ActiveTab, businessId: string, fileId: string) => {
      setTabLoading(true);
      try {
        if (tab === "forecast" && !forecastReport) {
          const fc = await apiJson<SalesForecastResponse>(
            `/api/v1/businesses/${businessId}/uploads/${fileId}/ml/forecast`,
            { method: "POST" }
          );
          setForecastReport(fc);
        } else if (tab === "churn" && !churnReport) {
          const ch = await apiJson<CustomerChurnResponse>(
            `/api/v1/businesses/${businessId}/uploads/${fileId}/ml/churn`,
            { method: "POST" }
          );
          setChurnReport(ch);
        } else if (tab === "insights" && !insightsReport) {
          const ins = await apiJson<ExecutiveBriefReport>(
            `/api/v1/businesses/${businessId}/uploads/${fileId}/insights/generate`,
            { method: "POST" }
          );
          setInsightsReport(ins);
        } else if (tab === "actions" && actionsList.length === 0) {
          const acts = await apiJson<ActionItem[]>(
            `/api/v1/businesses/${businessId}/uploads/${fileId}/actions`
          );
          setActionsList(acts);
        }
      } catch (err) {
        console.error(`Failed to load ${tab} data:`, err);
      } finally {
        setTabLoading(false);
      }
    },
    [forecastReport, churnReport, insightsReport, actionsList]
  );

  const handleTabSelect = (tab: ActiveTab) => {
    setActiveTab(tab);
    if (selectedBusiness && activeFileId) {
      loadTabData(tab, selectedBusiness.id, activeFileId);
    }
  };

  const runFullPipeline = useCallback(
    async (businessId: string, fileId: string) => {
      setRunningAnalysis(true);
      try {
        const report = await apiJson<FullAnalyticsReport>(
          `/api/v1/businesses/${businessId}/uploads/${fileId}/analyze`,
          { method: "POST" }
        );
        setAnalyticsReport(report);
        setIsMappingMode(false);
        setActiveTab("overview");

        // Pre-fetch ML & Insights in background
        apiJson<SalesForecastResponse>(
          `/api/v1/businesses/${businessId}/uploads/${fileId}/ml/forecast`,
          { method: "POST" }
        ).then(setForecastReport).catch(() => {});

        apiJson<CustomerChurnResponse>(
          `/api/v1/businesses/${businessId}/uploads/${fileId}/ml/churn`,
          { method: "POST" }
        ).then(setChurnReport).catch(() => {});

        apiJson<ExecutiveBriefReport>(
          `/api/v1/businesses/${businessId}/uploads/${fileId}/insights/generate`,
          { method: "POST" }
        ).then(setInsightsReport).catch(() => {});

        apiJson<ActionItem[]>(
          `/api/v1/businesses/${businessId}/uploads/${fileId}/actions`
        ).then(setActionsList).catch(() => {});
      } catch (err) {
        console.error("Full pipeline execution failed:", err);
      } finally {
        setRunningAnalysis(false);
      }
    },
    []
  );

  const fetchProfile = useCallback(
    async (businessId: string, fileId: string) => {
      setLoadingProfile(true);
      setIsMappingMode(false);
      setAnalyticsReport(null);
      setForecastReport(null);
      setChurnReport(null);
      setInsightsReport(null);
      setActionsList([]);
      try {
        const profile = await apiJson<DataProfileResponse>(
          `/api/v1/businesses/${businessId}/uploads/${fileId}/profile`
        );
        setActiveProfile(profile);
        setActiveFileId(fileId);

        const existingAnalytics = await fetchAnalytics(businessId, fileId);
        if (existingAnalytics) {
          setActiveTab("overview");
        }
      } catch (err) {
        console.error("Failed to load profile:", err);
      } finally {
        setLoadingProfile(false);
      }
    },
    [fetchAnalytics]
  );

  const loadUploads = useCallback(async (businessId: string) => {
    try {
      const items = await apiJson<UploadedFileItem[]>(
        `/api/v1/businesses/${businessId}/uploads`
      );
      setUploads(items);
    } catch (err) {
      console.error("Failed to load uploads:", err);
    }
  }, []);

  const loadBusinesses = useCallback(async () => {
    try {
      const data = await apiJson<Business[]>("/api/v1/businesses");
      setBusinesses(data);
      if (data.length > 0) {
        setSelectedBusiness((prev) => {
          if (prev && data.some((b) => b.id === prev.id)) return prev;
          loadUploads(data[0].id);
          return data[0];
        });
      } else {
        setSelectedBusiness(null);
      }
    } catch (err) {
      console.error("Failed to load businesses:", err);
    }
  }, [loadUploads]);

  useEffect(() => {
    const supabase = createClient();

    async function checkAuth() {
      // 1. Check Guest / Demo Mode
      if (typeof window !== "undefined" && sessionStorage.getItem("guest_mode") === "true") {
        let storedEmail = "guest@businesscopilot.ai";
        try {
          const stored = localStorage.getItem("demo_user");
          if (stored) {
            const parsed = JSON.parse(stored);
            if (parsed.email) storedEmail = parsed.email;
          }
        } catch {
          // ignore error
        }
        setUser({ id: "demo-guest-user", email: storedEmail } as User);
        await loadBusinesses();
        setLoading(false);
        return;
      }

      // 2. Check Supabase Auth
      try {
        const {
          data: { session },
        } = await supabase.auth.getSession();

        if (session) {
          setUser(session.user);
          await loadBusinesses();
          setLoading(false);
          return;
        }
      } catch (err) {
        console.warn("Supabase auth check failed:", err);
      }

      // 3. Fallback to login
      router.push("/auth/login");
    }

    checkAuth();
  }, [router, loadBusinesses]);

  async function handleCreateBusiness(e: React.FormEvent) {
    e.preventDefault();
    if (!newBusinessName.trim()) return;

    setCreatingBusiness(true);
    try {
      const created = await apiJson<Business>("/api/v1/businesses", {
        method: "POST",
        body: JSON.stringify({
          name: newBusinessName.trim(),
          industry: newIndustry || "Retail / E-Commerce",
        }),
      });

      setBusinesses((prev) => [created, ...prev]);
      setSelectedBusiness(created);
      setNewBusinessName("");
      setUploads([]);
      setActiveProfile(null);
      setActiveFileId(null);
      setAnalyticsReport(null);
      setShowNewWorkspaceModal(false);
    } catch (err) {
      console.error("Error creating business:", err);
    } finally {
      setCreatingBusiness(false);
    }
  }

  const [exporting, setExporting] = useState(false);

  async function handleExportReport() {
    if (!selectedBusiness || !activeFileId) return;
    setExporting(true);
    try {
      const res = await apiFetch(
        `/api/v1/businesses/${selectedBusiness.id}/uploads/${activeFileId}/export`
      );
      if (!res.ok) {
        throw new Error(`Export failed with status ${res.status}`);
      }
      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      const safeBizName = selectedBusiness.name.replace(/[^a-zA-Z0-9_-]/g, "_");
      a.download = `Executive_Brief_${safeBizName}_${activeFileId.slice(0, 8)}.md`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      console.error("Failed to export report:", err);
    } finally {
      setExporting(false);
    }
  }

  async function handleSignOut() {
    const supabase = createClient();
    await supabase.auth.signOut();
    router.push("/auth/login");
    router.refresh();
  }

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-zinc-50 dark:bg-zinc-950">
        <div className="flex flex-col items-center gap-3">
          <svg
            className="h-8 w-8 animate-spin text-indigo-600"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
          >
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
          </svg>
          <p className="text-sm text-zinc-500 dark:text-zinc-400">Loading AI Business Copilot...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-zinc-50 dark:bg-zinc-950">
      {/* Top Navigation */}
      <header className="sticky top-0 z-10 border-b border-zinc-200 bg-white/80 backdrop-blur-md dark:border-zinc-800 dark:bg-zinc-900/80">
        <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4">
          <div className="flex items-center gap-6">
            <div className="flex items-center gap-3">
              <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-indigo-600 font-bold text-white shadow-sm">
                BC
              </div>
              <span className="text-sm font-semibold tracking-tight text-zinc-900 dark:text-zinc-100">
                AI Business Copilot
              </span>
            </div>

            {/* Business Selector & + New Workspace Button */}
            <div className="flex items-center gap-2">
              {businesses.length > 0 && selectedBusiness && (
                <div className="relative">
                  <select
                    value={selectedBusiness.id}
                    onChange={(e) => {
                      const found = businesses.find((b) => b.id === e.target.value);
                      if (found) {
                        setSelectedBusiness(found);
                        setActiveProfile(null);
                        setActiveFileId(null);
                        setIsMappingMode(false);
                        setAnalyticsReport(null);
                        loadUploads(found.id);
                      }
                    }}
                    className="rounded-lg border border-zinc-200 bg-zinc-50 py-1.5 pl-3 pr-8 text-xs font-medium text-zinc-800 focus:border-indigo-500 focus:outline-none dark:border-zinc-700 dark:bg-zinc-800 dark:text-zinc-200 cursor-pointer"
                  >
                    {businesses.map((b) => (
                      <option key={b.id} value={b.id}>
                        {b.name} ({b.role})
                      </option>
                    ))}
                  </select>
                </div>
              )}
              <button
                id="create-new-workspace-btn"
                onClick={() => {
                  setNewBusinessName("");
                  setShowNewWorkspaceModal(true);
                }}
                className="flex items-center gap-1 rounded-lg border border-indigo-200 bg-indigo-50/70 px-2.5 py-1.5 text-xs font-semibold text-indigo-700 hover:bg-indigo-100 dark:border-indigo-800 dark:bg-indigo-950/50 dark:text-indigo-300 dark:hover:bg-indigo-900/60 transition-colors shadow-sm cursor-pointer"
                title="Create a new business workspace"
              >
                <span className="text-sm font-bold leading-none">+</span> New Workspace
              </button>
            </div>
          </div>

          <div className="flex items-center gap-4">
            <span className="text-xs text-zinc-500 dark:text-zinc-400 hidden sm:inline">
              {user?.email}
            </span>
            <button
              id="sign-out-button"
              onClick={handleSignOut}
              className="rounded-lg border border-zinc-200 bg-white px-3 py-1.5 text-xs font-medium text-zinc-700 shadow-sm transition-colors hover:bg-zinc-50 dark:border-zinc-700 dark:bg-zinc-800 dark:text-zinc-300 dark:hover:bg-zinc-700"
            >
              Sign out
            </button>
          </div>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="mx-auto max-w-7xl px-4 py-8 space-y-8">
        {businesses.length === 0 ? (
          <div className="mx-auto max-w-md rounded-2xl border border-zinc-200 bg-white p-8 shadow-sm dark:border-zinc-800 dark:bg-zinc-900 text-center">
            <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-2xl bg-indigo-50 text-indigo-600 dark:bg-indigo-950 dark:text-indigo-400">
              🏢
            </div>
            <h2 className="text-lg font-semibold text-zinc-900 dark:text-zinc-100">
              Create Your Business Workspace
            </h2>
            <p className="mt-1 text-xs text-zinc-500 dark:text-zinc-400">
              Set up your business workspace to begin uploading and analyzing data.
            </p>
            <form onSubmit={handleCreateBusiness} className="mt-6 flex flex-col gap-3 text-left">
              <div>
                <label className="block text-xs font-semibold text-zinc-700 dark:text-zinc-300 mb-1">
                  Workspace Name
                </label>
                <input
                  type="text"
                  placeholder="e.g. Apex Retail, My Online Store"
                  value={newBusinessName}
                  onChange={(e) => setNewBusinessName(e.target.value)}
                  className="h-10 w-full rounded-lg border border-zinc-300 px-3 text-sm text-zinc-900 placeholder:text-zinc-400 focus:border-indigo-500 focus:outline-none dark:border-zinc-700 dark:bg-zinc-800 dark:text-zinc-100"
                  required
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-zinc-700 dark:text-zinc-300 mb-1">
                  Industry / Category
                </label>
                <select
                  value={newIndustry}
                  onChange={(e) => setNewIndustry(e.target.value)}
                  className="h-10 w-full rounded-lg border border-zinc-300 px-3 text-sm text-zinc-900 focus:border-indigo-500 focus:outline-none dark:border-zinc-700 dark:bg-zinc-800 dark:text-zinc-100"
                >
                  <option value="Retail / E-Commerce">Retail / E-Commerce</option>
                  <option value="SaaS / Software">SaaS / Software</option>
                  <option value="Wholesale / Distribution">Wholesale / Distribution</option>
                  <option value="Manufacturing">Manufacturing</option>
                  <option value="Services / Consulting">Services / Consulting</option>
                  <option value="General Business">General Business</option>
                </select>
              </div>
              <button
                type="submit"
                disabled={creatingBusiness || !newBusinessName.trim()}
                className="mt-2 flex h-10 items-center justify-center rounded-lg bg-indigo-600 px-4 text-sm font-semibold text-white hover:bg-indigo-700 disabled:opacity-60 dark:bg-indigo-500"
              >
                {creatingBusiness ? "Creating..." : "Create Workspace"}
              </button>
            </form>
          </div>
        ) : (
          <>
            {/* Header / Actions Bar */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
              <div>
                <h1 className="text-2xl font-bold tracking-tight text-zinc-900 dark:text-zinc-100">
                  {selectedBusiness?.name} Copilot
                </h1>
                <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">
                  Deterministic analytics, machine learning projections, multi-agent briefs, and decision playbooks.
                </p>
              </div>

              <div className="flex items-center gap-3">
                {analyticsReport && (
                  <button
                    disabled={exporting}
                    onClick={handleExportReport}
                    className="rounded-xl border border-zinc-200 bg-white px-3.5 py-2 text-xs font-semibold text-zinc-700 shadow-sm hover:bg-zinc-50 dark:border-zinc-700 dark:bg-zinc-800 dark:text-zinc-200 flex items-center gap-1.5 disabled:opacity-60"
                  >
                    <span>📥</span> {exporting ? "Exporting..." : "Export Brief (.md)"}
                  </button>
                )}

                {(activeProfile || isMappingMode || analyticsReport) && (
                  <button
                    onClick={() => {
                      setActiveProfile(null);
                      setActiveFileId(null);
                      setIsMappingMode(false);
                      setAnalyticsReport(null);
                      setForecastReport(null);
                      setChurnReport(null);
                      setInsightsReport(null);
                      setActionsList([]);
                    }}
                    className="rounded-xl border border-zinc-200 bg-white px-3.5 py-2 text-xs font-medium text-zinc-700 hover:bg-zinc-50 dark:border-zinc-700 dark:bg-zinc-800 dark:text-zinc-300"
                  >
                    + Upload New File
                  </button>
                )}
              </div>
            </div>

            {/* Analysis Loading State */}
            {runningAnalysis ? (
              <div className="flex h-80 flex-col items-center justify-center rounded-2xl border border-zinc-200 bg-white dark:border-zinc-800 dark:bg-zinc-900">
                <svg
                  className="h-10 w-10 animate-spin text-indigo-600 mb-4"
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                >
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                </svg>
                <h3 className="text-base font-bold text-zinc-900 dark:text-zinc-100">
                  Synthesizing Business Intelligence...
                </h3>
                <p className="text-xs text-zinc-400 mt-1 max-w-md text-center">
                  Executing deterministic analytics, ML forecasting models, customer churn risk scoring, and multi-agent synthesis
                </p>
              </div>
            ) : analyticsReport && selectedBusiness && activeFileId ? (
              /* Tabbed Intelligence Suite */
              <div className="space-y-6">
                {/* Navigation Tabs */}
                <div className="flex items-center gap-1.5 overflow-x-auto rounded-2xl border border-zinc-200 bg-white p-1.5 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
                  {[
                    { id: "overview", label: "📊 Overview & KPIs" },
                    { id: "forecast", label: "🔮 Sales Forecast" },
                    { id: "churn", label: "👥 Churn Risk" },
                    { id: "insights", label: "🧠 Executive Brief" },
                    { id: "copilot", label: "💬 Copilot Q&A" },
                    { id: "actions", label: "⚡ Action Center" },
                    { id: "simulator", label: "🎛️ What-If Sandbox" },
                  ].map((tab) => (
                    <button
                      key={tab.id}
                      onClick={() => handleTabSelect(tab.id as ActiveTab)}
                      className={`rounded-xl px-3.5 py-2 text-xs font-semibold whitespace-nowrap transition-all ${
                        activeTab === tab.id
                          ? "bg-indigo-600 text-white shadow-sm dark:bg-indigo-500"
                          : "text-zinc-600 hover:text-zinc-900 hover:bg-zinc-50 dark:text-zinc-400 dark:hover:text-zinc-200 dark:hover:bg-zinc-800"
                      }`}
                    >
                      {tab.label}
                    </button>
                  ))}
                </div>

                {/* Tab Views */}
                {tabLoading ? (
                  <div className="flex h-64 items-center justify-center rounded-2xl border border-zinc-200 bg-white dark:border-zinc-800 dark:bg-zinc-900">
                    <p className="text-xs text-zinc-400">Loading intelligence view...</p>
                  </div>
                ) : (
                  <>
                    {activeTab === "overview" && (
                      <AnalyticsOverview
                        report={analyticsReport}
                        onBackToUploads={() => {
                          setActiveProfile(null);
                          setActiveFileId(null);
                          setIsMappingMode(false);
                          setAnalyticsReport(null);
                          setForecastReport(null);
                          setChurnReport(null);
                          setInsightsReport(null);
                          setActionsList([]);
                        }}
                      />
                    )}

                    {activeTab === "forecast" && forecastReport && (
                      <ForecastView
                        forecast={forecastReport}
                        onRefresh={() => loadTabData("forecast", selectedBusiness.id, activeFileId)}
                      />
                    )}

                    {activeTab === "churn" && churnReport && (
                      <ChurnView
                        churn={churnReport}
                        onRefresh={() => loadTabData("churn", selectedBusiness.id, activeFileId)}
                      />
                    )}

                    {activeTab === "insights" && insightsReport && (
                      <InsightsView
                        brief={insightsReport}
                        onRefresh={() => loadTabData("insights", selectedBusiness.id, activeFileId)}
                      />
                    )}

                    {activeTab === "copilot" && (
                      <CopilotChat businessId={selectedBusiness.id} fileId={activeFileId} />
                    )}

                    {activeTab === "actions" && (
                      <ActionCenter
                        businessId={selectedBusiness.id}
                        fileId={activeFileId}
                        initialActions={actionsList}
                      />
                    )}

                    {activeTab === "simulator" && (
                      <WhatIfSimulator
                        businessId={selectedBusiness.id}
                        fileId={activeFileId}
                        baseRevenue={analyticsReport.kpis.total_revenue}
                      />
                    )}
                  </>
                )}
              </div>
            ) : loadingProfile ? (
              <div className="flex h-64 items-center justify-center rounded-2xl border border-zinc-200 bg-white dark:border-zinc-800 dark:bg-zinc-900">
                <p className="text-sm text-zinc-500">Loading dataset profile...</p>
              </div>
            ) : isMappingMode && selectedBusiness && activeFileId && activeProfile ? (
              <MappingView
                businessId={selectedBusiness.id}
                fileId={activeFileId}
                profile={activeProfile}
                onBackToProfile={() => setIsMappingMode(false)}
                onConfirmSuccess={() => {
                  if (selectedBusiness && activeFileId) {
                    runFullPipeline(selectedBusiness.id, activeFileId);
                    loadUploads(selectedBusiness.id);
                  }
                }}
              />
            ) : activeProfile ? (
              <DataProfileView
                profile={activeProfile}
                onContinueToMapping={() => setIsMappingMode(true)}
              />
            ) : (
              selectedBusiness && (
                <div className="space-y-6">
                  <FileUpload
                    businessId={selectedBusiness.id}
                    onUploadSuccess={(fileId) => {
                      loadUploads(selectedBusiness.id);
                      fetchProfile(selectedBusiness.id, fileId);
                    }}
                  />

                  {/* Previous Uploads List */}
                  {uploads.length > 0 && (
                    <div className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
                      <h3 className="text-sm font-semibold text-zinc-900 dark:text-zinc-100 mb-4">
                        Previously Uploaded Files
                      </h3>
                      <div className="divide-y divide-zinc-100 dark:divide-zinc-800">
                        {uploads.map((file) => (
                          <div
                            key={file.id}
                            onClick={() => fetchProfile(selectedBusiness.id, file.id)}
                            className="flex items-center justify-between py-3 hover:bg-zinc-50 dark:hover:bg-zinc-800/50 rounded-lg px-2 cursor-pointer transition-colors"
                          >
                            <div className="flex items-center gap-3">
                              <span className="text-base">📄</span>
                              <div>
                                <p className="text-sm font-medium text-zinc-900 dark:text-zinc-100">
                                  {file.original_filename}
                                </p>
                                <p className="text-xs text-zinc-400">
                                  {(file.file_size_bytes / 1024).toFixed(1)} KB • {file.sheet_count} sheet(s)
                                </p>
                              </div>
                            </div>
                            <div className="flex items-center gap-2">
                              {file.status === "ready" && (
                                <button
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    runFullPipeline(selectedBusiness.id, file.id);
                                  }}
                                  className="rounded-lg bg-indigo-50 px-2.5 py-1 text-xs font-semibold text-indigo-700 hover:bg-indigo-100 dark:bg-indigo-950/40 dark:text-indigo-300"
                                >
                                  Open Intelligence Suite →
                                </button>
                              )}
                              <span className="rounded-full bg-emerald-50 px-2.5 py-0.5 text-xs font-medium text-emerald-700 dark:bg-emerald-950/40 dark:text-emerald-400 capitalize">
                                {file.status}
                              </span>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )
            )}
          </>
        )}
      </main>

      {/* New Workspace Modal */}
      {showNewWorkspaceModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4 backdrop-blur-sm">
          <div className="w-full max-w-md rounded-2xl border border-zinc-200 bg-white p-6 shadow-2xl dark:border-zinc-800 dark:bg-zinc-900">
            <div className="flex items-center justify-between pb-3 border-b border-zinc-100 dark:border-zinc-800">
              <div className="flex items-center gap-2">
                <span className="text-xl">🏢</span>
                <h3 className="text-base font-bold text-zinc-900 dark:text-zinc-100">
                  Create New Workspace
                </h3>
              </div>
              <button
                onClick={() => setShowNewWorkspaceModal(false)}
                className="rounded-lg p-1 text-zinc-400 hover:bg-zinc-100 hover:text-zinc-700 dark:hover:bg-zinc-800 dark:hover:text-zinc-200"
              >
                ✕
              </button>
            </div>
            <form onSubmit={handleCreateBusiness} className="mt-4 flex flex-col gap-4">
              <div>
                <label className="block text-xs font-semibold text-zinc-700 dark:text-zinc-300 mb-1">
                  Workspace Name
                </label>
                <input
                  type="text"
                  placeholder="e.g. My E-commerce Brand, Bakery Co."
                  value={newBusinessName}
                  onChange={(e) => setNewBusinessName(e.target.value)}
                  className="h-10 w-full rounded-lg border border-zinc-300 px-3 text-sm text-zinc-900 placeholder:text-zinc-400 focus:border-indigo-500 focus:outline-none dark:border-zinc-700 dark:bg-zinc-800 dark:text-zinc-100"
                  required
                  autoFocus
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-zinc-700 dark:text-zinc-300 mb-1">
                  Industry / Domain
                </label>
                <select
                  value={newIndustry}
                  onChange={(e) => setNewIndustry(e.target.value)}
                  className="h-10 w-full rounded-lg border border-zinc-300 px-3 text-sm text-zinc-900 focus:border-indigo-500 focus:outline-none dark:border-zinc-700 dark:bg-zinc-800 dark:text-zinc-100"
                >
                  <option value="Retail / E-Commerce">Retail / E-Commerce</option>
                  <option value="SaaS / Software">SaaS / Software</option>
                  <option value="Wholesale / Distribution">Wholesale / Distribution</option>
                  <option value="Manufacturing">Manufacturing</option>
                  <option value="Services / Consulting">Services / Consulting</option>
                  <option value="General Business">General Business</option>
                </select>
              </div>
              <div className="flex items-center justify-end gap-2 pt-2 border-t border-zinc-100 dark:border-zinc-800">
                <button
                  type="button"
                  onClick={() => setShowNewWorkspaceModal(false)}
                  className="rounded-lg border border-zinc-200 bg-white px-3.5 py-2 text-xs font-medium text-zinc-700 hover:bg-zinc-50 dark:border-zinc-700 dark:bg-zinc-800 dark:text-zinc-300"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={creatingBusiness || !newBusinessName.trim()}
                  className="flex items-center justify-center rounded-lg bg-indigo-600 px-4 py-2 text-xs font-semibold text-white hover:bg-indigo-700 disabled:opacity-50 dark:bg-indigo-500"
                >
                  {creatingBusiness ? "Creating..." : "Create Workspace"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
