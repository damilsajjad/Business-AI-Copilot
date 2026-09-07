# 🤖 AI Business Copilot

> **Upload business data. Understand what is happening, why it is happening, and predict what happens next with verified mathematical truth.**

AI Business Copilot is an autonomous, executive-grade business intelligence and decision-support platform designed for SMEs and e-commerce enterprises.

Unlike generic LLM analytics tools that hallucinate numbers, **AI Business Copilot separates deterministic math from AI explanations**:
1. All KPIs, sales trends, Pareto concentrations, customer retention, inventory velocities, and forecasts are calculated using **verified deterministic algorithms and scikit-learn models**.
2. Multi-agent domain specialists (Executive, Sales, Product, Customer, Demand) synthesize strategic insights, risk alerts, and action playbooks strictly grounded in computed numbers.

---

## 🏛️ System Architecture

```text
                               ┌────────────────────────┐
                               │  Next.js 16 Dashboard  │
                               │   (TypeScript / TW)    │
                               └───────────┬────────────┘
                                           │ REST / SSE
                                           ▼
                               ┌────────────────────────┐
                               │     FastAPI Layer      │
                               │   (Python 3.13 / v1)   │
                               └───────────┬────────────┘
                                           │
         ┌───────────────────┬─────────────┴────────────┬────────────────────┐
         ▼                   ▼                          ▼                    ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────────────┐ ┌─────────────────┐
│ Supabase Cloud  │ │  Deterministic  │ │     Machine Learning    │ │ Multi-Agent AI  │
│ Auth / Postgres │ │ Analytics Engine│ │ Sales Forecast (Ridge)  │ │ Domain Briefs   │
│ RLS Isolation   │ │ KPIs & Trends   │ │ RFM Churn Risk Scoring  │ │ Factual Copilot │
└─────────────────┘ └─────────────────┘ └─────────────────────────┘ └─────────────────┘
```

---

## 🚀 Key Feature Modules

- **Flexible Multi-Sheet Ingestion**: Drag-and-drop `.csv` and multi-sheet `.xlsx` workbooks with automated column profiling and semantic discovery.
- **AI Schema Mapping & Validation**: Automated column mapping to a canonical target schema with deterministic type validation.
- **Deterministic Analytics Engine**: High-level financial KPIs (Revenue, Orders, AOV, Daily Run-Rate), MoM sales growth rates, Z-score anomaly detection, Pareto product concentration, customer repeat rate, and inventory velocity.
- **Machine Learning Forecasting**: Ridge regression with linear trend and day-of-week seasonality (30/60/90-day daily projections, upper/lower confidence bounds, MAPE, and RMSE).
- **Customer Churn Risk Scoring**: RFM-based decay scoring evaluating lapsing buyers, risk factors, and revenue at stake.
- **Multi-Agent AI Executive Brief**: Domain-specialized analysts synthesizing a holistic Business Health Score (0–100), strategic risks, and expansion opportunities.
- **Conversational Copilot Q&A**: Interactive executive partner strictly grounded in verified business metrics.
- **Action Center & What-If Sandbox**: Prioritized operational playbooks and real-time commercial parameter simulation (price changes, volume shifts, discounts, churn recovery).
- **1-Click Executive Report Export**: Instant downloadable Markdown briefing document.

---

## 🛠️ Tech Stack

- **Frontend**: Next.js 16 (Turbopack, App Router), React 19, TypeScript, Tailwind CSS, Recharts.
- **Backend**: Python 3.13, FastAPI, Pydantic v2, Pandas, NumPy, Scikit-learn, Google Gemini LLM API.
- **Database / Auth / Storage**: Supabase (PostgreSQL with Row-Level Security, Supabase Auth, Storage).
- **Deployment**: Vercel (Frontend), Render (Backend), Supabase Cloud.

---

## 🧪 Testing & Verification

Run the comprehensive automated test suites:

```powershell
# Backend pytest suite (77+ tests)
cd backend
.\venv\Scripts\python.exe -m pytest tests/ -v

# Backend code formatting and linting
.\venv\Scripts\ruff.exe check app/ tests/

# Frontend linting
cd ../frontend
npx eslint .

# Frontend production build
npx next build
```

---

## 💻 Local Development Setup

### 1. Backend Setup
```powershell
cd backend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Start FastAPI backend
uvicorn app.main:app --reload --port 8000
```

### 2. Frontend Setup
```powershell
cd frontend
npm install
cp .env.example .env.local
# Start Next.js frontend
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) to access the landing page, test the interactive demo sandbox, or log in to your business workspace.
