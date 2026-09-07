# AI Business Copilot — BUILD BLUEPRINT

## 0. Mission

Build a production-quality hackathon MVP called **AI Business Copilot** for SMEs.

Core promise:

> Upload business data. The system understands it, analyzes what is happening, explains why it is happening, predicts what may happen next where data permits, and clearly tells the owner what matters.

This is a **read-only business intelligence/copilot product**.

### Explicitly OUT of scope

Do NOT build:
- email drafting
- social-media drafting
- marketing campaign generation
- automatic posting/sending
- inventory modification
- order creation
- payment processing
- external business actions
- MCP/action-taking integrations
- n8n
- unnecessary features added only to make the product look larger

The system may generate business explanations and recommendations as part of insight cards, but the product's purpose is analysis and explanation, not content generation or autonomous execution.

---

# 1. NON-NEGOTIABLE DEVELOPMENT RULE

You are the primary coding agent.

**Do not attempt to blindly build the entire project in one uncontrolled pass.**

Build strictly in phases.

For every phase:

1. Read this blueprint.
2. Inspect the current repository.
3. Implement ONLY the current phase.
4. Run all tests required by the phase.
5. Fix failures.
6. Run lint/type checks where applicable.
7. Verify the acceptance criteria manually where required.
8. Produce a short phase completion report.
9. STOP.

Do not start the next phase until the current phase passes.

If a requirement is ambiguous:
- prefer the simplest implementation consistent with this blueprint;
- do not invent a new product feature;
- document the assumption;
- continue only if the assumption does not change architecture or product behavior.

If an architectural problem is discovered:
- stop;
- explain the problem;
- propose the smallest safe correction;
- do not silently redesign the project.

---

# 2. PRODUCT REQUIREMENTS

## Target users

Small and medium-sized businesses.

For the hackathon demonstration, use a realistic **retail/e-commerce dataset** because it naturally demonstrates sales, products, customers, revenue, inventory/demand, and churn-related analysis.

The architecture must remain industry-agnostic enough to support other businesses later.

## Product philosophy

The user should not have to become an analyst.

The system should answer:

1. What is happening?
2. Why is it happening?
3. What evidence supports that conclusion?
4. What should the business owner pay attention to?
5. What may happen next, when enough historical data exists?

The dashboard is **Copilot-first**, not chart-first.

---

# 3. USER FLOW

Landing Page
→ Try Demo OR Get Started
→ Sign Up / Login
→ Simple onboarding
→ Upload CSV/XLSX
→ System profiles and interprets data
→ AI proposes column mapping
→ User confirms mapping
→ Automatic analysis starts
→ Copilot-first dashboard
→ Insight cards
→ Suggested deeper questions
→ Detailed analytics

## Try Demo

The landing page must include a low-friction demo experience using sample retail/e-commerce data.

The demo should show the value of the product without requiring account creation.

Do not make the landing page visually overloaded.

---

# 4. DATA INPUT

## Supported files

MVP supports:

- `.csv`
- `.xlsx`

For XLSX:
- support multiple sheets in the same workbook.

Do NOT make multiple independent file uploads a core MVP requirement.

## Flexible schema

Do not require users to follow a rigid template.

The system should infer likely meanings from column names and values.

Example:

Date → Order Date
Amount → Revenue
Cust_ID → Customer ID
Qty → Quantity
Item → Product

The system then presents the proposed mapping to the user.

The user confirms or corrects it.

Only after confirmation should downstream analysis run.

---

# 5. DATA UNDERSTANDING

Implement a deterministic profiling layer before the LLM.

The profiler should inspect:

- sheet names
- column names
- data types
- null percentages
- unique counts
- sample values
- date ranges
- numeric ranges
- duplicate rows
- obvious categorical fields
- likely identifiers
- likely measures
- likely dimensions

The profiler produces structured metadata.

The LLM receives structured metadata rather than blindly receiving an entire raw spreadsheet whenever possible.

The LLM proposes a mapping.

The backend validates the proposed mapping against actual data types.

Never trust an LLM-generated schema mapping without validation.

---

# 6. INSUFFICIENT DATA POLICY

Never fabricate a result.

Each capability must have a data sufficiency check.

If a capability cannot run:

- do not invent a prediction;
- explain why;
- show the missing requirement;
- tell the user what data/action is needed.

Example:

> Sales Forecast unavailable  
> Not enough historical sales data to generate a reliable forecast. Upload more historical sales records.

The exact threshold must be capability-specific.

---

# 7. CORE ANALYTICS CAPABILITIES

Implement only capabilities that can be supported by the uploaded data.

## A. Data overview

Show:
- total records
- date range
- revenue
- orders/transactions where available
- customers where available
- products where available
- data quality indicators

## B. Sales analysis

Analyze:
- revenue trend
- order/transaction trend
- growth/decline
- period-over-period changes
- best/worst periods
- major contributors to changes

## C. Product analysis

Analyze:
- top products
- underperforming products
- product revenue contribution
- quantity trends
- product growth/decline
- concentration/dependency risks where appropriate

## D. Customer analysis

When customer-level data exists:
- customer count
- repeat customers
- valuable customers
- purchasing trends
- customer concentration
- potential churn risk where sufficient history exists

## E. Inventory/demand insights

When inventory or sufficient sales/quantity history exists:
- demand trends
- fast-moving products
- slow-moving products
- potential stockout risk where inventory fields exist
- demand-related insights

Do not claim actual inventory risk if inventory data is absent.

## F. Sales forecasting

When sufficient historical time-series data exists:
- forecast future sales
- show confidence/uncertainty appropriately
- explain limitations
- show historical vs forecast chart

Use a practical lightweight ML approach.

## G. Churn-risk analysis

When customer history supports it:
- identify customers showing churn-risk behavior
- provide evidence/features behind the risk
- clearly label it as risk, not certainty

## H. Business insights

Combine deterministic analytics and ML outputs into understandable business insights.

---

# 8. AI INSIGHT FORMAT

Use **Insight Cards (Option B)**.

Every major AI insight should contain:

### Conclusion
A short statement of what happened.

### Why
The main reason(s).

### Evidence
Concrete numbers/observations from the analyzed dataset.

### Business implication / recommendation
A concise statement of what deserves attention.

Example:

**Sales dropped 18%**

**Why:** Product A revenue fell 31%.

**Evidence:** Product A revenue decreased from $12K to $8.3K during the comparison period.

**What to pay attention to:** Product A is the largest contributor to the overall decline.

Do not turn this into a generic chatbot response.

---

# 9. COPILOT EXPERIENCE

After automatic analysis, show suggested questions such as:

- Why did sales drop?
- Which products are performing best?
- Which products are underperforming?
- What should I pay attention to?
- Which customers appear at risk?
- What may happen to sales next?

These are **deeper analysis questions**, not an open-ended autonomous agent requirement.

The user may click a suggested question and receive another evidence-based insight.

A conversational interface can be added only if it is trivial and does not compromise the core dashboard.

---

# 10. AI / AGENT ARCHITECTURE

Use **CrewAI** for orchestration.

Recommended logical roles:

### Data Analyst Agent
Consumes validated structured analysis data.

Responsibilities:
- identify trends
- summarize KPI changes
- identify anomalies/patterns
- produce evidence-backed findings

### Business Consultant Agent
Consumes analytical findings.

Responsibilities:
- explain likely business reasons
- connect changes to products/customers/time periods
- turn findings into understandable business implications

### Prediction/ML Analyst
Consumes ML outputs.

Responsibilities:
- explain forecasts/churn/demand results
- state confidence/limitations
- never invent model results

### Executive Reporter
Consumes the verified findings from the other components.

Responsibilities:
- prioritize the most important findings
- produce the executive summary
- structure the dashboard/report insights

Do not create unnecessary agents.

## Important architecture rule

Do not let agents independently calculate financial facts.

Financial facts must come from deterministic Python/data-processing code.

Agents explain verified facts.

---

# 11. LLM

Use a configurable LLM provider.

Initial provider:
**Google Gemini API**

Primary development/coding model in Antigravity:
**Gemini 3.1 Pro High**, when available.

The application model must be configurable via environment variables.

Never hard-code provider/model credentials.

Example:

LLM_PROVIDER=gemini
LLM_MODEL=<configured-model>
GEMINI_API_KEY=<secret>

The application must be architected so the provider can later be changed without rewriting the business logic.

---

# 12. ML ARCHITECTURE

Use:

- Python
- pandas
- numpy
- scikit-learn
- joblib where model persistence is needed

Prefer simple, explainable, reliable models over unnecessarily complex deep learning.

## Forecasting

Build a practical baseline time-series forecasting pipeline.

Requirements:
- aggregate sales by time period
- validate chronological splits
- create appropriate lag/rolling features where applicable
- train model
- evaluate against a baseline
- generate forecast
- expose evaluation metrics
- persist model/configuration when appropriate

Do not use random train/test splitting for time-series forecasting.

## Churn

Use a practical classification pipeline if sufficient customer history exists.

Potential features:
- recency
- frequency
- monetary value
- purchase intervals
- trend/change in purchase behavior

Use an interpretable model first.

Evaluate using suitable metrics such as:
- precision
- recall
- F1
- ROC-AUC where appropriate

Do not present churn as certainty.

## Demand/inventory

Use historical quantity/sales patterns.

Only generate inventory-related conclusions when the required fields exist.

---

# 13. ML VALIDATION RULE

A model is not considered complete merely because it trains successfully.

For each ML capability:

1. Validate data sufficiency.
2. Prepare data.
3. Split correctly.
4. Train.
5. Evaluate.
6. Compare with a simple baseline.
7. Check for obviously broken outputs.
8. Persist model if required.
9. Test inference on unseen data.
10. Expose model metrics.
11. Only then integrate it into the AI insight pipeline.

If the model performs poorly, show the capability as unavailable/unreliable rather than pretending it is accurate.

---

# 14. DATABASE

Use **Supabase PostgreSQL**.

Initial conceptual entities:

- users
- businesses
- business_memberships
- uploaded_files
- data_sources / sheets
- data_mappings
- sales/transactions
- products
- customers
- predictions
- insights
- reports

Do not duplicate raw uploaded files into unnecessary database tables.

Use Supabase Storage for original uploaded files.

Store normalized/processed business data in PostgreSQL where useful for querying and repeat analysis.

Final schema should be designed around actual query patterns and business ownership.

Every business-owned record must be traceable to a `business_id`.

---

# 15. AUTHENTICATION AND SECURITY

Use **Supabase Auth**.

Requirements:

- authenticated users
- business/workspace ownership
- data isolation
- Row Level Security where applicable
- backend authorization checks
- API keys only on backend
- secrets via environment variables
- no secrets in Git
- validate uploaded file type
- enforce upload size limits
- sanitize/validate parsed data
- prevent users from accessing another business's data

Never trust a frontend-supplied business ID without authorization.

---

# 16. BACKEND

Use:

**Python + FastAPI**

FastAPI is the application API layer.

Backend responsibilities:

- authentication/authorization integration
- file upload handling
- CSV/XLSX parsing
- data profiling
- schema mapping
- validation
- deterministic analytics
- ML execution
- CrewAI orchestration
- LLM communication
- report generation
- persistence
- scheduled report processing

Do not put heavy ML/agent processing inside the Next.js frontend.

---

# 17. API DESIGN

Use versioned REST APIs.

Suggested structure:

`/api/v1/...`

Core endpoint groups:

### Health
`GET /api/v1/health`

### Uploads
`POST /api/v1/uploads`
`GET /api/v1/uploads/{id}`

### Profiling/mapping
`POST /api/v1/uploads/{id}/profile`
`POST /api/v1/uploads/{id}/mapping/confirm`

### Analysis
`POST /api/v1/analysis/run`
`GET /api/v1/analysis/{id}`

### Dashboard
`GET /api/v1/dashboard`

### Insights
`GET /api/v1/insights`
`POST /api/v1/insights/question`

### Predictions
`POST /api/v1/predictions/forecast`
`POST /api/v1/predictions/churn`
`POST /api/v1/predictions/demand`

### Reports
`GET /api/v1/reports`
`POST /api/v1/reports/generate`

Exact request/response schemas must be typed and documented with Pydantic.

Do not expose internal stack traces to users.

---

# 18. LONG-RUNNING WORK

Analysis can involve:

- file processing
- ML
- CrewAI
- LLM calls
- report generation

Do not assume these operations are instant.

For MVP, use a job/status pattern if needed.

Example:

POST analysis
→ returns analysis/job ID
→ backend processes
→ frontend polls status
→ completed result available

Keep the architecture simple enough for the hackathon.

---

# 19. FRONTEND

Use:

- Next.js
- TypeScript
- Tailwind CSS
- a consistent component library
- Recharts

Design goals:

- minimal
- polished
- professional
- human-designed
- easy for non-technical business owners
- responsive
- accessible

Avoid:
- excessive gradients
- generic AI-looking layouts
- giant walls of cards
- unnecessary animations
- technical jargon

---

# 20. LANDING PAGE

Required sections:

### Navbar
Simple navigation and primary CTA.

### Hero
Clearly communicate the business value.

### Interactive demo
A small motion/animation showing:

Upload business data
→ AI understands it
→ analysis
→ useful business insight/chart

Keep this demo minimal.

### CTA
Try Demo / Get Started.

### How it works
Simple 3–4 step explanation.

Do not overload the landing page with analytics.

---

# 21. DASHBOARD

Copilot-first layout.

Example structure:

Good morning 👋

### Here's what you should know

🔴 Sales dropped 18%
🟢 Product A is performing strongly
⚠️ 12 customers show churn-risk behavior
📦 Product X demand is increasing

Then:

**Insight cards**

Each card:
- conclusion
- why
- evidence
- implication/recommendation

Then:

**Suggested questions**

Then:

**Detailed analytics**

Charts should support the story, not become the story.

---

# 22. DETAILED ANALYTICS

Use charts for:

- revenue over time
- orders over time
- product performance
- customer trends
- forecast vs actual
- demand trends
- churn-risk distribution

Charts must have:
- clear titles
- units
- meaningful labels
- useful tooltips
- empty/insufficient-data states

Never display misleading zero values when data is unavailable.

---

# 23. DEMO DATA

Create a deterministic synthetic retail/e-commerce dataset for development and demo purposes.

It should include enough history to demonstrate:

- revenue trends
- products
- customers
- quantities
- dates
- repeat purchases
- a visible sales change
- product performance differences
- sufficient history for forecasting
- customer behavior suitable for churn demonstration

The synthetic dataset must be reproducible.

Do not use fabricated real-world company claims.

---

# 24. PROJECT STRUCTURE

Use a monorepo:

```text
business-copilot/
├── frontend/
│   ├── app/
│   ├── components/
│   ├── lib/
│   ├── hooks/
│   ├── types/
│   └── tests/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── analytics/
│   │   ├── ml/
│   │   ├── agents/
│   │   ├── data/
│   │   └── main.py
│   └── tests/
│
├── shared/
│   └── contracts/
│
├── docs/
├── scripts/
├── supabase/
│   └── migrations/
│
├── .env.example
├── BLUEPRINT.md
├── PROJECT_PRD.md
├── README.md
└── .gitignore
```

Adapt names only when technically necessary.

Keep modules small and responsibility-focused.

---

# 25. INFRASTRUCTURE

## Frontend
Deploy to:
**Vercel**

## Backend
Deploy to:
**Render**

The backend should be a persistent service because analysis/ML/agent tasks can be long-running.

## Database/Auth/Storage
Use:
**Supabase Cloud**

## Source control
Use:
**GitHub**

## Scheduling
Use:
**Supabase scheduled jobs/cron** calling the backend where scheduled reporting is required.

Do not introduce n8n.

---

# 26. ENVIRONMENT VARIABLES

Create `.env.example`.

Never commit real credentials.

Expected categories:

Frontend:
- NEXT_PUBLIC_API_URL
- NEXT_PUBLIC_SUPABASE_URL
- NEXT_PUBLIC_SUPABASE_ANON_KEY

Backend:
- SUPABASE_URL
- SUPABASE_SERVICE_ROLE_KEY
- GEMINI_API_KEY
- LLM_PROVIDER
- LLM_MODEL
- DATABASE_URL
- allowed origins
- environment configuration

Use the minimum secrets actually required.

---

# 27. TESTING STRATEGY

Testing is mandatory.

## Frontend

Test:
- rendering
- upload UI
- mapping confirmation
- dashboard states
- insight cards
- insufficient-data states
- API error states

## Backend

Test:
- health endpoint
- authentication/authorization
- upload validation
- CSV parsing
- XLSX parsing
- multi-sheet handling
- profiling
- mapping validation
- analytics calculations
- API schemas
- error handling

## ML

Test:
- minimum data checks
- preprocessing
- training
- inference
- evaluation
- baseline comparison
- model persistence
- prediction output ranges

## Agents/LLM

Test with mocked LLM responses where possible.

Verify:
- structured output schema
- evidence references
- no unsupported claims
- correct handling of missing data
- deterministic facts are preserved

Do not make tests depend entirely on live LLM calls.

## Integration

Test:

Upload
→ profile
→ mapping
→ confirmation
→ analysis
→ ML
→ agents
→ database
→ dashboard

---

# 28. ACCEPTANCE CRITERIA

The MVP is complete only when a new user can:

1. Open the landing page.
2. Understand what the product does.
3. Try the demo.
4. Create/login to an account.
5. Upload CSV/XLSX.
6. Upload an XLSX containing multiple sheets.
7. See AI-proposed column mapping.
8. Confirm/correct the mapping.
9. Start automatic analysis.
10. See processing status.
11. See a Copilot-first dashboard.
12. See evidence-backed insight cards.
13. See detailed charts.
14. See forecasting when sufficient data exists.
15. See churn analysis when sufficient data exists.
16. See demand/inventory insights when sufficient data exists.
17. Receive clear insufficient-data messages when a capability cannot run.
18. Ask/click a deeper business question.
19. Receive an evidence-backed answer.
20. Never see fabricated metrics.
21. Never access another business's data.
22. Use the deployed application successfully.

---

# 29. PHASE PLAN

## Phase 0 — Repository and development setup

Create:
- monorepo
- Git configuration
- frontend scaffold
- backend scaffold
- Python environment
- test infrastructure
- linting/formatting
- environment templates
- README
- initial documentation

Acceptance:
- frontend starts
- backend starts
- health endpoint works
- tests run
- no secrets committed

STOP.

## Phase 1 — Supabase + Auth + database foundation

Implement:
- Supabase connection
- Auth
- businesses/workspaces
- membership/ownership
- migrations
- RLS
- backend authorization

Tests:
- user creation
- business ownership
- unauthorized access rejection

STOP.

## Phase 2 — File upload + data profiling

Implement:
- CSV upload
- XLSX upload
- multi-sheet extraction
- validation
- storage
- profiler
- profile API
- UI upload flow

Tests:
- valid CSV
- valid XLSX
- multiple sheets
- invalid file
- malformed data
- size limit

STOP.

## Phase 3 — AI mapping + confirmation

Implement:
- mapping schema
- deterministic validation
- Gemini mapping proposal
- mapping UI
- confirmation
- persistence

Tests:
- valid mappings
- invalid mappings
- missing required fields
- LLM malformed output
- correction flow

STOP.

## Phase 4 — Deterministic analytics engine

Implement:
- KPI calculations
- sales trends
- product analysis
- customer analysis
- demand/inventory analysis
- anomaly detection where appropriate

Tests:
- known synthetic dataset
- compare calculations with manually verified expected values

STOP.

## Phase 5 — ML

Implement:
- forecasting
- churn-risk
- demand modeling where appropriate
- data sufficiency checks
- evaluation
- baselines
- persistence
- inference APIs

Tests:
- training
- evaluation
- unseen inference
- insufficient data
- broken/missing columns
- output validation

STOP.

## Phase 6 — CrewAI + LLM insight engine

Implement:
- agents
- structured prompts
- verified analytical context
- evidence-based insight schema
- insight generation
- deeper-question flow

Tests:
- mocked LLM
- schema validation
- unsupported-claim protection
- evidence preservation
- insufficient-data handling

STOP.

## Phase 7 — Dashboard

Implement:
- Copilot-first dashboard
- insight cards
- suggested questions
- detailed analytics
- charts
- forecast visualization
- churn visualization
- loading/error/empty states

Tests:
- responsive UI
- API integration
- all major states

STOP.

## Phase 8 — Landing page + demo

Implement:
- navbar
- hero
- interactive demo
- CTA
- how-it-works
- polished responsive design

STOP.

## Phase 9 — Reports + scheduling

Implement:
- executive report generation
- report persistence
- scheduled weekly report trigger
- backend scheduled endpoint/job integration

Do not add external actions.

STOP.

## Phase 10 — Integration hardening

Run full end-to-end test.

Verify:
- auth
- upload
- mapping
- analytics
- ML
- agents
- dashboard
- database isolation
- error handling
- performance
- deployment configuration

Fix integration bugs.

STOP.

## Phase 11 — Deployment

Deploy:

Frontend → Vercel
Backend → Render
Database/Auth/Storage → Supabase

Configure:
- environment variables
- CORS
- production URLs
- database migrations
- storage
- health checks

Run production smoke tests.

STOP.

## Phase 12 — Hackathon polish

Do NOT add random features.

Improve:
- visual consistency
- speed
- empty states
- error messages
- demo reliability
- sample data
- onboarding
- presentation flow

Perform final end-to-end demo rehearsal.

---

# 30. FINAL ENGINEERING PRINCIPLES

1. Correctness over feature count.
2. Evidence over AI-generated claims.
3. Deterministic calculations over LLM arithmetic.
4. ML must be evaluated, not merely trained.
5. No fabricated results.
6. No hidden failures.
7. Every failure should tell the user what to do next.
8. Keep architecture modular.
9. Keep APIs typed.
10. Keep secrets out of source control.
11. Do not over-engineer.
12. Do not introduce technologies not required by this blueprint.
13. Do not silently change product requirements.
14. Test each phase before proceeding.
15. Prefer a reliable smaller MVP over an impressive but fragile system.

# FINAL DEFINITION OF DONE

The project is done when the complete user journey works in production:

Landing page
→ demo
→ authentication
→ upload
→ AI mapping
→ confirmation
→ automatic analysis
→ ML where supported
→ evidence-backed AI insights
→ Copilot-first dashboard
→ detailed analytics
→ deeper questions
→ executive report
→ secure isolated business data
→ deployed frontend/backend/database

The system must feel like a polished business product, not a collection of AI-generated demos.
