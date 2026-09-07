"use client";

import Link from "next/link";
import InteractiveDemo from "@/components/interactive-demo";

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-zinc-50 text-zinc-900 dark:bg-zinc-950 dark:text-zinc-50 selection:bg-indigo-500 selection:text-white">
      {/* Navbar */}
      <header className="sticky top-0 z-50 border-b border-zinc-200/80 bg-white/80 backdrop-blur-md dark:border-zinc-800/80 dark:bg-zinc-900/80">
        <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6">
          <div className="flex items-center gap-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-indigo-600 font-bold text-white shadow-md shadow-indigo-500/20">
              BC
            </div>
            <span className="text-base font-bold tracking-tight text-zinc-900 dark:text-zinc-100">
              AI Business Copilot
            </span>
          </div>

          <nav className="hidden md:flex items-center gap-8 text-xs font-semibold text-zinc-600 dark:text-zinc-400">
            <a href="#demo" className="hover:text-zinc-900 dark:hover:text-zinc-100 transition-colors">
              Interactive Demo
            </a>
            <a href="#how-it-works" className="hover:text-zinc-900 dark:hover:text-zinc-100 transition-colors">
              How It Works
            </a>
            <a href="#features" className="hover:text-zinc-900 dark:hover:text-zinc-100 transition-colors">
              Core Capabilities
            </a>
          </nav>

          <div className="flex items-center gap-3">
            <Link
              href="/auth/login"
              className="rounded-xl px-3.5 py-2 text-xs font-semibold text-zinc-700 hover:text-zinc-900 hover:bg-zinc-100/60 dark:text-zinc-300 dark:hover:text-zinc-100 dark:hover:bg-zinc-800/60 transition-colors"
            >
              Sign In
            </Link>
            <Link
              href="/auth/signup"
              className="rounded-xl bg-indigo-600 px-4 py-2 text-xs font-semibold text-white shadow-md shadow-indigo-600/20 hover:bg-indigo-700 transition-colors dark:bg-indigo-500 dark:hover:bg-indigo-600"
            >
              Get Started Free
            </Link>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="relative overflow-hidden pt-20 pb-16 sm:pt-28 sm:pb-24">
        {/* Ambient Gradient Glow */}
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[350px] bg-indigo-500/15 blur-[120px] rounded-full pointer-events-none -z-10" />

        <div className="mx-auto max-w-5xl px-4 text-center space-y-6">
          <div className="inline-flex items-center gap-2 rounded-full border border-indigo-200/60 bg-indigo-50/50 px-3.5 py-1 text-xs font-semibold text-indigo-700 dark:border-indigo-900/50 dark:bg-indigo-950/40 dark:text-indigo-300">
            <span className="flex h-2 w-2 rounded-full bg-indigo-500 animate-pulse" />
            Deterministic Business Intelligence + Multi-Agent AI
          </div>

          <h1 className="text-4xl sm:text-6xl font-black tracking-tight text-zinc-900 dark:text-zinc-100 leading-[1.12]">
            Upload Business Data. <br />
            <span className="bg-gradient-to-r from-indigo-600 via-violet-600 to-indigo-500 bg-clip-text text-transparent">
              Understand Everything.
            </span> <br />
            Predict What&apos;s Next.
          </h1>

          <p className="mx-auto max-w-2xl text-base sm:text-lg text-zinc-600 dark:text-zinc-400 font-normal leading-relaxed">
            AI Business Copilot turns messy retail and commercial spreadsheets into verified mathematical KPIs, 30/60/90-day ML sales forecasts, customer churn risk alerts, and executive decision playbooks.
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-3 pt-4">
            <Link
              href="/auth/signup"
              className="w-full sm:w-auto rounded-2xl bg-indigo-600 px-6 py-3.5 text-sm font-bold text-white shadow-xl shadow-indigo-600/25 hover:bg-indigo-700 transition-all dark:bg-indigo-500 dark:hover:bg-indigo-600"
            >
              Get Started Free →
            </Link>
            <Link
              href="/dashboard"
              onClick={() => {
                if (typeof window !== "undefined") {
                  sessionStorage.setItem("guest_mode", "true");
                }
              }}
              className="w-full sm:w-auto rounded-2xl border border-indigo-200 bg-indigo-50/70 px-6 py-3.5 text-sm font-semibold text-indigo-700 shadow-sm hover:bg-indigo-100 dark:border-indigo-900/60 dark:bg-indigo-950/40 dark:text-indigo-300 dark:hover:bg-indigo-900/50 transition-colors"
            >
              ⚡ Enter Demo Workspace
            </Link>
            <a
              href="#demo"
              className="w-full sm:w-auto rounded-2xl border border-zinc-200 bg-white/80 px-6 py-3.5 text-sm font-semibold text-zinc-800 shadow-sm hover:bg-zinc-50 dark:border-zinc-700 dark:bg-zinc-800/80 dark:text-zinc-200 dark:hover:bg-zinc-800"
            >
              How It Works
            </a>
          </div>
        </div>
      </section>

      {/* Interactive Demo Section */}
      <section id="demo" className="py-12 sm:py-20 bg-zinc-100/50 dark:bg-zinc-900/40 border-y border-zinc-200/60 dark:border-zinc-800/60">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 space-y-8">
          <div className="text-center space-y-2 max-w-2xl mx-auto">
            <span className="text-xs font-bold text-indigo-600 dark:text-indigo-400 uppercase tracking-widest">
              Zero-Login Interactive Experience
            </span>
            <h2 className="text-2xl sm:text-3xl font-extrabold text-zinc-900 dark:text-zinc-100">
              See How It Works in 30 Seconds
            </h2>
            <p className="text-xs sm:text-sm text-zinc-500 dark:text-zinc-400">
              Walk through the exact pipeline: raw spreadsheet ingestion, AI column discovery, verified calculations, and factual Copilot Q&A.
            </p>
          </div>

          <InteractiveDemo />
        </div>
      </section>

      {/* How It Works Section */}
      <section id="how-it-works" className="py-20">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 space-y-12">
          <div className="text-center space-y-2 max-w-xl mx-auto">
            <h2 className="text-2xl sm:text-3xl font-extrabold text-zinc-900 dark:text-zinc-100">
              The 4-Step Intelligence Engine
            </h2>
            <p className="text-xs sm:text-sm text-zinc-500 dark:text-zinc-400">
              Engineered to eliminate LLM arithmetic hallucinations and deliver verifiable truth.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            {[
              {
                step: "01",
                title: "Flexible Upload",
                desc: "Drop any CSV or multi-sheet XLSX file. Our engine extracts sheets and profiles columns safely.",
              },
              {
                step: "02",
                title: "AI Schema Mapping",
                desc: "LLM + heuristic mappers suggest canonical alignments with deterministic type validation.",
              },
              {
                step: "03",
                title: "Verified Analytics & ML",
                desc: "Pure Python mathematical algorithms compute exact KPIs, sales trends, Pareto shares, and Ridge forecasts.",
              },
              {
                step: "04",
                title: "Executive Synthesis",
                desc: "Multi-agent domain specialists produce actionable briefs, health scores, and an interactive Copilot partner.",
              },
            ].map((item) => (
              <div
                key={item.step}
                className="rounded-3xl border border-zinc-200 bg-white p-6 shadow-sm dark:border-zinc-800 dark:bg-zinc-900 space-y-3"
              >
                <span className="text-2xl font-black text-indigo-600 dark:text-indigo-400">
                  {item.step}
                </span>
                <h3 className="text-base font-bold text-zinc-900 dark:text-zinc-100">
                  {item.title}
                </h3>
                <p className="text-xs text-zinc-500 dark:text-zinc-400 leading-relaxed">
                  {item.desc}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Core Capabilities Grid */}
      <section id="features" className="py-20 bg-zinc-100/40 dark:bg-zinc-900/30 border-t border-zinc-200/60 dark:border-zinc-800/60">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 space-y-12">
          <div className="text-center space-y-2 max-w-xl mx-auto">
            <h2 className="text-2xl sm:text-3xl font-extrabold text-zinc-900 dark:text-zinc-100">
              Built for Serious Business Owners
            </h2>
            <p className="text-xs sm:text-sm text-zinc-500 dark:text-zinc-400">
              No guesswork. Every insight is backed by cited numbers and statistical algorithms.
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {[
              {
                icon: "📊",
                title: "Deterministic Analytics",
                desc: "Verified mathematical aggregations for Revenue, AOV, run-rate, MoM growth rates, and Z-score anomalies.",
              },
              {
                icon: "🔮",
                title: "Machine Learning Forecasting",
                desc: "Ridge regression with linear trend and day-of-week seasonality for 30/60/90-day daily predictions with MAPE/RMSE.",
              },
              {
                icon: "👥",
                title: "Customer Churn Risk Scoring",
                desc: "RFM recency and monetary decay scoring identifying lapsing customers and revenue at stake.",
              },
              {
                icon: "🧠",
                title: "Multi-Agent AI Briefs",
                desc: "Executive, Sales, Product, Customer, and Demand domain analysts synthesize an overall Business Health Score (0-100).",
              },
              {
                icon: "⚡",
                title: "Action Center Playbooks",
                desc: "Prioritized operational initiatives with step-by-step checklists, effort ratings, and ownership assignment.",
              },
              {
                icon: "🎛️",
                title: "What-If Scenario Sandbox",
                desc: "Simulate pricing shifts, volume expansions, discounts, and churn win-backs with real-time bottom-line impact.",
              },
            ].map((f, i) => (
              <div
                key={i}
                className="rounded-3xl border border-zinc-200 bg-white p-6 shadow-sm dark:border-zinc-800 dark:bg-zinc-900 space-y-2.5"
              >
                <div className="text-2xl mb-1">{f.icon}</div>
                <h3 className="text-base font-bold text-zinc-900 dark:text-zinc-100">
                  {f.title}
                </h3>
                <p className="text-xs text-zinc-500 dark:text-zinc-400 leading-relaxed">
                  {f.desc}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Final Call to Action */}
      <section className="py-20 text-center">
        <div className="mx-auto max-w-4xl px-4 space-y-6">
          <h2 className="text-3xl sm:text-4xl font-black text-zinc-900 dark:text-zinc-100 tracking-tight">
            Ready to Unlock Autonomous Intelligence for Your Business?
          </h2>
          <p className="text-sm text-zinc-500 dark:text-zinc-400 max-w-xl mx-auto">
            Create your private workspace today and transform your business spreadsheets into actionable strategic clarity.
          </p>
          <div className="pt-2">
            <Link
              href="/auth/signup"
              className="inline-block rounded-2xl bg-indigo-600 px-8 py-4 text-sm font-bold text-white shadow-xl shadow-indigo-600/30 hover:bg-indigo-700 transition-all dark:bg-indigo-500"
            >
              Get Started Free Today →
            </Link>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-zinc-200 dark:border-zinc-800 py-8 text-center text-xs text-zinc-400">
        <div className="mx-auto max-w-7xl px-4 flex flex-col sm:flex-row items-center justify-between gap-4">
          <span>© 2026 AI Business Copilot. All rights reserved.</span>
          <div className="flex items-center gap-6 font-medium">
            <Link href="/auth/login" className="hover:text-zinc-600 dark:hover:text-zinc-200">
              Sign In
            </Link>
            <Link href="/auth/signup" className="hover:text-zinc-600 dark:hover:text-zinc-200">
              Sign Up
            </Link>
            <Link href="/dashboard" className="hover:text-zinc-600 dark:hover:text-zinc-200">
              Dashboard
            </Link>
          </div>
        </div>
      </footer>
    </div>
  );
}
