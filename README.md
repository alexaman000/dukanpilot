# DukaanPilot AI

**Autonomous AI Business Growth Worker for Micro-Entrepreneurs**

DukaanPilot AI is an autonomous agentic system designed to help neighborhood retail shop owners grow their businesses sustainably. Operating within a simulated retail environment, the worker analyzes sales data, designs tailored growth strategies, executes simulated operational tasks, measures financial outcomes, and dynamically replans to reach business targets.

---

## Business Scenario: Sneha Bhandar

* **Store Name:** Sneha Bhandar
* **Location:** Shiv Shakti Nagar, Booty More, Ranchi, Jharkhand – 834009, India
* **Business Type:** Neighborhood grocery and daily-needs shop (*kirana*)
* **Currency:** Indian Rupee (INR / ₹)
* **Growth Goal:** Increase monthly revenue from a baseline of **₹8,000** to **₹10,000**.
* **Simulation Boundary:** All datasets, customer records, inventory operations, and financial transactions are strictly synthetic and offline.

---

## Synthetic Data & Simulation Boundaries

* **Synthetic Retail Records:** All data files in `data/` (`sales.csv`, `products.csv`, `customers.csv`, `expenses.csv`, `promotions.csv`) contain 91 days of deterministic, synthetically generated retail transactions across 20 grocery products.
* **Safe Local Action Tools:** All tools (`create_simulated_promotion`, `recommend_product_bundle`, `create_reorder_suggestion`, `draft_customer_campaign`) execute strictly offline. No real customer contact (SMS/WhatsApp messages), no real vendor supplier orders, and no real financial payments are initiated.
* **Demonstration Benchmarks:** Baseline revenue (₹8,000) and target revenue (₹10,000) are benchmark demonstration settings for Sneha Bhandar and do not represent verified real-world commercial performance.
* **Explicit Distinction:** The system strictly differentiates deterministic, Pandas-calculated historical metrics from AI-generated impact projections and estimates.

---

## Problem Statement

Micro-retailers often operate on thin margins and lack access to dedicated business analysts, marketing specialists, or inventory planners. Business owners carry out all tasks manually, frequently suffering from:

- Unoptimized inventory leading to dead capital and stockouts.
- Static pricing that misses margin-expansion opportunities.
- Lack of data-driven promotional planning.
- Limited time to analyze daily sales records and plan multi-step growth initiatives.

---

## Implemented Modules (Phases 1, 2, 3 & 4)

* **Synthetic Data Layer (`data/`):** 91 days of deterministic retail records for 20 grocery products across 7 categories, including sales transactions, customer profiles, operating expenses, and promotions.
* **Data Loader & Integrity Validation (`database/data_loader.py`):** Schema enforcement, line-item arithmetic consistency, and cross-dataset foreign key constraints.
* **Business Analytics Engine (`agents/business_analyst.py`):** Deterministic financial KPI calculations using Python and Pandas (revenues, COGS, margins, basket values, stockout deficits, target comparisons, period filtering).
* **LangGraph Orchestrator (`workflow/graph.py`):** Stateful workflow engine coordinating 8 nodes: `analyst`, `planner`, `validator`, `human_approval`, `executor`, `measurement`, `learning`, and `rejection`.
* **Growth Planner (`agents/growth_planner.py`):** Proposes practical growth actions using the Gemini API, with deterministic data-grounded fallback for offline testing.
* **Action Validator (`agents/action_validator.py`):** Validates proposed actions against tool schemas, parameter bounds, safety constraints, and estimation labeling policies.
* **Human-in-the-Loop Gate (`workflow/graph.py`):** Native `interrupt()` and `Command(resume=...)` workflow pause before tool execution, requiring explicit owner approval, revision, or rejection.
* **SQLite Persistence (`workflow/graph.py` & `database/run_tracker.py`):** State serialization and checkpointing via `SqliteSaver` in `database/dukaanpilot.db` supporting session resume across restarts.
* **Local Simulation Tools (`tools/`):** Safe, offline demonstration tools (`create_simulated_promotion`, `recommend_product_bundle`, `create_reorder_suggestion`, `draft_customer_campaign`).
* **Outcome Measurement & Replanning (`workflow/evaluator.py`):** Measures simulated uplift vs. verified historical baselines, reflects on learnings, and enforces iteration limits.
* **Interactive Streamlit Dashboard (`app.py`):** Multi-section retail analytics and operations portal connecting live to the LangGraph workflow, SQLite checkpointer, Sarvam AI speech engine, and bilingual interface.
* **AI Voice Business Briefing (`agents/voice_briefing.py` & `tools/sarvam_tts.py`):** Natural Indian Hindi and English spoken briefing powered by Sarvam AI TTS (`bulbul:v3`), including text chunking, SHA-256 audio caching, section-by-section playback, and human approval gates.
* **Automated Test Suite (`tests/`):** 66 comprehensive unit and integration tests covering data loading, deterministic financial analytics, action validation, human approval pause/resume, tool error recovery, dashboard startup, state snapshots, Sarvam AI speech synthesis, and voice briefing reports.
* **Resilient Failure Recovery & Safety Trapping (`tools/registry.py`, `workflow/graph.py`, `workflow/evaluator.py`):** 7-stage failure handling architecture enclosing tool executions in exception barriers, zero phantom uplift attribution, SQLite state durability, diagnostic error logging, and human-supervised safe retries or cancellations.

---

## Streamlit Dashboard Features

The web dashboard is organized into accessible sections for both small shopkeepers and technical evaluators:

0. **🏪 Shopkeeper Summary & Actions:**
   - Friendly greeting: *"Namaste! Here is your shop's business update."*
   - 4 Simple Plain-Language Metric Cards: Current Monthly Sales (₹9,159), Monthly Goal (₹10,000), Remaining Gap (₹841), and Text-Labeled Status (**"Action required"** / **"Needs attention"** / **"Doing well"**).
   - 5 Plain-Language Insights generated dynamically from store data without technical jargon.
   - 1-Click Action Recommendations with **Approve All**, **Reject All**, and **Revise** controls.
   - Honest 5-stage AI Worker Activity Timeline reflecting real workflow states.

1. **🎙️ AI Voice Business Briefing (Sarvam AI Integration):**
   - Natural spoken business explanation in Hindi or English powered by Sarvam AI Text-to-Speech.
   - Friendly assistant character area (**Asha**) with animated soundwave visual feedback when speaking.
   - Complete 9-section structured business report readable alongside or below the audio.
   - Play, Pause, Resume, Replay, and Section-by-Section playback options.
   - Explicit human approval controls after listening (Approve, Reject, Revise) connected directly to LangGraph persistence.

2. **📊 Business Overview:**
   - Real-time financial KPI cards: Total Revenue, Gross Profit, Operating Expenses, Estimated Net Profit, Average Basket Value (ATV).
   - Date period selector ("All Historical Data", "January 2024", "February 2024", "March 2024").
   - Daily sales revenue trajectory chart (Plotly).
   - Category revenue share bar chart (Plotly).
   - Top-selling and slow-moving product tables (period-filtered).
   - Real-time low-stock alerts with reorder deficit warnings.

2. **🎯 Business Goal:**
   - Clear side-by-side display of Baseline Revenue (₹8,000), Target Revenue (₹10,000), and Measured Monthly Average Run Rate.
   - Milestone progress gauge comparing current run rate against the target.
   - Monthly historical revenue breakdown chart with baseline and target reference lines.
   - Demonstration settings disclaimer.

3. **🤖 AI Growth Plan:**
   - Thread / Run ID controller with "🆕 New Run ID" generator.
   - "🚀 Run Growth Planner" button initiating a LangGraph stateful run.
   - Business Analyst diagnostic summary (Pandas-calculated baseline metrics).
   - Proposed growth actions list with explicit `[AI Estimate]` tags, business rationale, parameters, costs, and risks.
   - Action Validation report (schema compliance, cost limits, parameter safety).
   - Notification when execution pauses at the approval gate.

4. **✋ Human Approval (Human-in-the-Loop):**
   - Displays paused workflow state awaiting shop owner authorization.
   - Readable summary of proposed actions with impact projections and estimated costs.
   - **✅ Approve Full Strategy:** Resumes LangGraph workflow to execute approved demonstration tools.
   - **❌ Reject Strategy:** Halts execution immediately; ZERO tools are executed.
   - **✏️ Revise / Customize Actions:** Interactive checkboxes allowing the user to selectively approve a subset of actions.
   - Resumes persisted workflow using its unique SQLite thread ID via LangGraph `Command(resume=...)`.

5. **⚡ Execution & Outcomes:**
   - Execution log cards for each executed tool, including execution status (`SUCCESS` / `FAILED`), execution timestamps (`executed_at`), and detailed output payloads.
   - Financial outcome metrics: Historical Monthly Baseline, Simulated Monthly Uplift, Projected New Monthly Run Rate, Remaining Gap.
   - Learning and replanning strategy summary: Iteration counter, replanning requirement, strategic decision reason, and key business learnings.

6. **📜 Run History:**
   - Audit trail table of all persisted sessions in `database/dukaanpilot.db`.
   - Displays thread ID, timestamps, workflow status, approval status, actions count, and simulated revenue uplift.
   - "🔄 Reopen Selected Session" control: Restores past runs into the active session state, allowing users to continue paused workflows or review past execution outcomes.

---

## Technology Stack

| Layer | Technology | Purpose |
| :--- | :--- | :--- |
| **User Interface** | Streamlit & Plotly | Interactive operations dashboard, charts, and Human-in-the-Loop approval gate |
| **Voice Synthesis** | Sarvam AI TTS (`bulbul:v3`) | Natural Indian English & Hindi spoken business briefings |
| **Workflow Engine** | LangGraph | Stateful workflow management, interrupt handling, cyclic replanning, and persistence |
| **Reasoning Core** | Gemini API (`google-genai` / `langchain-google-genai`) | Analytical reasoning, strategic planning, and reflection (with deterministic fallback) |
| **Data Processing** | Pandas | Deterministic financial metrics, transaction aggregation, and KPI analysis |
| **Persistence** | SQLite (`SqliteSaver`) | Checkpointing of workflow graph state and run history tracking |
| **Testing** | Pytest | Automated unit and integration testing suite |

---

## Setup Instructions

### 1. Prerequisites
- Python 3.10 or higher installed.

### 2. Clone Repository & Setup Virtual Environment
```bash
# Clone the repository
git clone https://github.com/alexaman000/dukanpilot.git
cd dukaanpilot

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# On Windows (cmd):
venv\Scripts\activate.bat
# On Linux/macOS:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables (Optional)
Copy `.env.example` to `.env` to supply API keys for Gemini reasoning and Sarvam AI voice synthesis:

```bash
cp .env.example .env
```

Edit `.env`:
```ini
# Gemini API Key for autonomous growth reasoning
GEMINI_API_KEY=your_gemini_api_key_here

# Sarvam AI Key for natural Hindi/English voice briefings
SARVAM_API_KEY=your_sarvam_api_key_here

# Application Configuration
APP_ENV=development
DATABASE_PATH=database/dukaanpilot.db
```
```bash
cp .env.example .env
```
Edit `.env`:
```ini
GEMINI_API_KEY=your_gemini_api_key_here
```
> **Note:** If no Gemini API key is configured, DukaanPilot AI automatically runs in offline deterministic mode using grounded domain heuristics.

---

## How to Run

### Launch Interactive Streamlit Dashboard
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

### Run Workflow Demonstration via CLI
```bash
# Interactive mode (prompts for approval/rejection in terminal)
python main.py

# Automated demonstration mode (auto-approves plan)
python main.py --auto
```

### Run Automated Test Suite
```bash
pytest
```

### Regenerate Synthetic Datasets
```bash
python data/generate_data.py
```

### Reset Demo State
To restore a pristine demo environment:
1. **Reset Database History:** Remove or clear the local SQLite database file `database/dukaanpilot.db`:
   ```bash
   # On Windows (PowerShell):
   Remove-Item database/dukaanpilot.db -ErrorAction SilentlyContinue
   ```
2. **Fresh Thread ID:** In the dashboard, click **"🆕 New Run ID"** in the **AI Growth Plan** tab to start an isolated, clean execution thread.
3. **Regenerate Clean Data:** Run `python data/generate_data.py` to restore original baseline transaction records.

---

## Documentation Index

- [docs/DukaanPilot_AI_Technical_Report.pdf](docs/DukaanPilot_AI_Technical_Report.pdf): Publication-grade, comprehensive technical report and architectural specification (PDF format).
- [docs/architecture.md](docs/architecture.md): Complete architecture specification, component boundaries, state transitions, and failure handling sequence.
- [docs/architecture.png](docs/architecture.png): High-resolution visual system architecture diagram.
- [docs/failure_recovery_diagram.png](docs/failure_recovery_diagram.png): Visual failure scenario and 7-stage recovery flow diagram.
- [docs/technical_note.md](docs/technical_note.md): In-depth technical note on system design, worker vs. chatbot analysis, 7-stage failure scenario, safety controls, persistence, and limitations.
- [docs/demo_script.md](docs/demo_script.md): Step-by-step 5–7 minute oral presentation script and walkthrough guide.
- [docs/data_dictionary.md](docs/data_dictionary.md): Synthetic schemas, field descriptions, business assumptions, and arithmetic formulas.

---

## Step-by-Step Dashboard Demo Flow (5–7 Minute Walkthrough)

1. **Step 1: Explore Business Overview (`📊 Business Overview`)**
   - Review top KPI cards for **Sneha Bhandar** (Total Revenue, Gross Profit & Margins, Operating Expenses, Net Profit, Average Basket Value).
   - Use the **Time Period** dropdown to filter metrics for January, February, or March 2024. Observe how the daily revenue trajectory, category share chart, and best/slow-selling product tables dynamically update.
   - Check the **Low-Stock Alerts** table showing items below reorder thresholds.

2. **Step 2: Review Business Goal (`🎯 Business Goal`)**
   - View the baseline (₹8,000) and target (₹10,000) demonstration milestones.
   - Inspect the **Target Milestone Progress** gauge comparing the measured monthly average (₹8,061.67) to the target.
   - Examine the monthly breakdown chart showing historical revenue relative to the milestone benchmarks.

3. **Step 3: Trigger Growth Strategy (`🤖 AI Growth Plan`)**
   - Keep the default thread ID or click **"🆕 New Run ID"**.
   - Click **"🚀 Run Growth Planner"**.
   - Observe the LangGraph execution: the `analyst` node calculates baseline metrics, the `planner` node formulates 3–5 data-grounded growth actions, and the `validator` verifies schema bounds.
   - Inspect the **Proposed Growth Interventions** expanders (noting the `[AI Estimate]` tags) and the **Validation Report**.
   - Note the warning indicating the workflow has paused at the Human Approval gate.

4. **Step 4: Authorize or Reject Strategy (`✋ Human Approval`)**
   - Navigate to the **Human Approval** tab.
   - Review the proposed actions awaiting decision.
   - **Option A (Approve):** Click **"✅ Approve Full Strategy"**. The workflow resumes from SQLite state, executes demonstration tools, measures outcomes, and reflects.
   - **Option B (Reject):** Click **"❌ Reject Strategy"**. The workflow halts immediately, terminating with status `rejected` and zero tools executed.
   - **Option C (Revise):** Expand **"✏️ Revise / Customize Actions"**, select specific actions using the checkboxes, and click **"Apply Selected Actions & Resume"**.

5. **Step 5: Inspect Execution and Outcomes (`⚡ Execution & Outcomes`)**
   - View the **Tool Execution Logs** showing each tool's name, execution status (`SUCCESS`), timestamp (`executed_at`), and structured output message.
   - Review **Financial Impact & Goal Achievement** metrics displaying historical baseline vs. simulated uplift and projected run rate.
   - Read the **Learning & Replanning Strategy** summary detailing whether the target was met or if another planning cycle was recommended.

6. **Step 6: Inspect Persisted Audit Trail (`📜 Run History`)**
   - View all past workflow executions stored in `database/dukaanpilot.db`.
   - Select any historical run from the dropdown and click **"🔄 Reopen Selected Session to Active State"** to restore its state snapshot and continue or review the run.
