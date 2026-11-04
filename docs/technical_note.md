# Technical Note: DukaanPilot AI

**System Design, Architectural Principles, and Implementation Analysis**

---

## 1. Problem and Project Objective

Micro-retailers in India—such as neighborhood *kirana* stores—face structural operating disadvantages:
1. **Thin Operating Margins:** Store owners juggle inventory purchasing, cash management, customer credit (*khata*), and storefront service simultaneously, leaving little time for data-driven strategic planning.
2. **Suboptimal Working Capital Allocation:** Fast-moving consumer goods (FMCG) often suffer from localized stockouts, while slow-moving discretionary goods trap working capital on shelves.
3. **Absence of Domain-Specific Analytics:** While enterprise retailers use sophisticated ERPs and merchandising engines, neighborhood shop owners have access only to passive digital ledgers or manual notebooks.

**Project Objective:**
To construct an autonomous, closed-loop **AI Business Growth Worker** that operates within a safe simulated testing boundary for **Sneha Bhandar** (Shiv Shakti Nagar, Booty More, Ranchi, Jharkhand – 834009). The worker analyzes daily transaction ledgers, formulates actionable growth interventions, enforces human-in-the-loop authorization gates, executes simulated operational tools, measures financial uplift against empirical baselines, and dynamically replans toward a milestone monthly revenue target (increasing from baseline **₹8,000** to target **₹10,000**).

---

## 2. Why an Autonomous AI Worker Rather Than a Simple Chatbot?

Traditional conversational bots (e.g., standard ChatGPT or generic Q&A interfaces) suffer from fundamental architectural deficiencies when applied to business operations:

| Feature | Conventional Chatbot | DukaanPilot AI Worker |
| :--- | :--- | :--- |
| **Interaction Paradigm** | Passive request-response; waits for human prompts. | Goal-directed autonomous loop; drives tasks forward. |
| **Data Processing** | Delegates arithmetic to LLM (frequent hallucinations). | Deterministic Pandas engine; 100% verified arithmetic. |
| **Action Execution** | Emits markdown advice; cannot execute actions. | Dispatches schema-validated tools with structured outputs. |
| **State Persistence** | Ephemeral context window; resets on reload. | SQLite-backed checkpoints; resumes interrupted workflows. |
| **Safety Architecture** | Weak system-prompt warnings ("please be careful"). | Hard interrupt gates; execution strictly blocked without user consent. |
| **Feedback Loop** | Open-loop; no verification of recommendations. | Closed-loop; measures simulated uplift and replans adaptively. |

DukaanPilot AI is designed not as a conversational advisor, but as an **operational co-worker** that executes concrete tasks while keeping the business owner firmly in command.

---

## 3. System Architecture and Technology Choices

DukaanPilot AI adheres to a modular, layered architecture:

```
[ Presentation Layer: Streamlit + Plotly (app.py) ]
                        │
                        ▼
[ Workflow Engine: LangGraph State Machine (workflow/graph.py) ]
        │                   │                   │
        ▼                   ▼                   ▼
[ Data Analytics ]   [ Reasoning Core ]   [ Execution Suite ]
  BusinessAnalyst      Gemini 2.0 Flash     4 Local Tools
  Pandas (verified)    Structured JSON      Safe Simulations
        │                   │                   │
        └───────────────────┼───────────────────┘
                            ▼
[ Persistence & State Store: SQLite Checkpointer (dukaanpilot.db) ]
```

### Technology Selections & Rationale:
- **LangGraph:** Provides cyclic graph topologies with native execution interrupts (`interrupt()`) and checkpoint serialization (`SqliteSaver`), enabling pause-and-resume workflows.
- **Python & Pandas:** Ensures that all revenue, cost of goods sold (COGS), gross margins, inventory deficits, and basket sizes are calculated deterministically. LLMs are never allowed to perform financial arithmetic.
- **Google Gemini API (`gemini-2.0-flash`):** High-speed, cost-effective reasoning for strategic problem decomposition with strict JSON schema compliance.
- **SQLite:** Serverless, portable, embedded relational database for zero-overhead local deployment, checkpointing, and execution history.
- **Streamlit & Plotly:** Rapid, reactive user interface for interactive data exploration, chart rendering, and decision gates.

---

## 4. Agent Workflow and State Management

The workflow is modeled as a state machine (`StateGraph(WorkflowState)`) containing 8 distinct nodes:

1. **`analyst` (`analyst_node`):**
   Loads synthetic records (`data/sales.csv`, `products.csv`, `expenses.csv`), computes financial totals, margins, stock deficits, and growth gaps.
2. **`planner` (`planner_node`):**
   Synthesizes diagnostic metrics and business objectives, calling the Gemini API to formulate 3–5 candidate growth interventions.
3. **`validator` (`validator_node`):**
   Filters proposed actions against registered tool schemas, checking parameter bounds and enforcing mandatory estimation labels.
4. **`human_approval` (`human_approval_node`):**
   Pauses execution using LangGraph's `interrupt()` primitive. Surfaces actions and projected impacts to the user.
5. **`executor` (`executor_node`):**
   Dispatches authorized actions to local demonstration tools, capturing timestamps, status codes, and execution payloads.
6. **`measurement` (`measurement_node`):**
   Calculates simulated monthly revenue uplift, compares projected run rates against the ₹10,000 target, and computes the remaining financial gap.
7. **`learning` (`learning_node`):**
   Evaluates target achievement and tool execution health. If the target is not reached and `iteration_count < max_iterations`, routes back to `planner`; otherwise concludes.
8. **`rejection` (`rejection_node`):**
   Terminal node reached when an owner declines a plan. Halts execution immediately with zero tool invocations.

### State Schema (`WorkflowState`):
Key state variables include:
- `business_context`: Shop identity and location parameters.
- `business_metrics`: Verified financial outputs from `BusinessAnalyst`.
- `business_goal`: Baseline, target, and milestone figures.
- `proposed_actions` / `approved_actions`: Intervention lists.
- `validation_results`: Schema and constraint audit logs.
- `approval_status`: `'pending'`, `'approved'`, or `'rejected'`.
- `execution_results`: Array of tool return dictionaries with timestamps.
- `measured_outcomes`: Post-execution financial uplift calculations.
- `iteration_count` / `max_iterations`: Loop control guardrails.

---

## 5. Human Approval and Safety Controls

To protect retail operations, DukaanPilot AI enforces a strict **Human-in-the-Loop (HITL)** architecture:

1. **Execution Freeze via `interrupt()`:**
   The workflow cannot transition from planning/validation to execution without human authorization. The graph pauses, serializing all intermediate node outputs to SQLite.
2. **Explicit Decision Primitives:**
   - **Approve:** Resumes graph via `Command(resume="approve")`, executing all validated actions.
   - **Reject:** Resumes graph via `Command(resume="reject")`, immediately routing to `rejection` node. Zero tools are executed.
   - **Revise:** Resumes graph via `Command(resume={"decision": "revise", "actions": [...]})`. Selected actions are automatically re-validated through `validate_proposed_plan()` before execution.
3. **Safety Policies Enforced in Validation:**
   - **Discount Ceiling:** Promotional discounts exceeding 30% are automatically rejected to preserve store gross margin.
   - **Schema Compliance:** Actions specifying unregistered tools or missing mandatory parameters fail validation.
   - **Estimation Labeling Policy:** Any expected impact claim lacking explicit estimation qualifiers (e.g., "Estimated impact:", "projected") is rejected to prevent deceptive certainty.

---

## 6. Tool Execution Design

All actions are mapped to registered, offline demonstration tools (`tools/`):

1. **`create_simulated_promotion`:** Models category discount schedules (1–30%), projecting volume elasticity and gross margin impacts.
2. **`recommend_product_bundle`:** Formulates cross-selling pairs (e.g., Red Label Tea 250g paired with Parle-G 250g) to increase average transaction value (ATV).
3. **`create_reorder_suggestion`:** Formulates wholesale replenishment drafts for items below reorder thresholds (e.g., Britannia Bread, MDH Deggi Mirch), estimating procurement working capital.
4. **`draft_customer_campaign`:** Synthesizes localized customer communication templates for specific shopper segments (e.g., Weekly Family Shoppers).

### Resilient Error Recovery:
The dispatcher (`tools.registry.execute_action`) wraps each tool in structured exception handlers. If a tool fails (e.g., invalid product ID), it returns a structured failure dictionary (`status: "failed"`, `error: "..."`). The executor records the error in `execution_results` and continues executing remaining valid tools without crashing the workflow.

---

## 7. Persistence and Failure Recovery

State durability is established through SQLite checkpointing:
- **`SqliteSaver` Checkpointer:** Embedded SQLite checkpointer (`database/dukaanpilot.db`) automatically captures the complete graph state at every node transition.
- **Application Restart Resilience:** If the application process terminates while paused at the approval gate, re-querying `app.get_state({"configurable": {"thread_id": thread_id}})` reconstructs the state snapshot and pending interrupts, allowing the owner to resume without re-running data analysis.
- **Run History Auditing:** Every workflow execution records metadata in `workflow_run_history` (timestamps, status, actions count, simulated uplift, summary), enabling full inspection in the dashboard.
- **Idempotent UI Invocations:** The Streamlit dashboard isolates execution triggers to explicit button callbacks (`st.button`). Standard browser refreshes or tab switches query saved snapshots without re-invoking tools.

---

## 8. Evaluation Approach and Measurable Success Criteria

DukaanPilot AI establishes clear, quantitative benchmarks:

1. **Analytical Accuracy:** 100% agreement between dashboard metrics and manual arithmetic proofs across 91 days of transactions.
2. **Safety Enforcement:** 100% rejection rate for discount actions >30% and 0 tool executions when a plan is rejected.
3. **Test Suite Coverage:** 66+ automated tests spanning unit arithmetic, action validation, graph execution, state restoration, Sarvam AI speech synthesis, bilingual voice reporting, and failure recovery.
4. **Milestone Tracking:** Clear measurement of monthly revenue trajectory toward the ₹10,000 target:
   - Historical Baseline: ₹8,061.67 / month
   - Simulated Monthly Uplift: +₹960.00 / month (approx. 12% revenue expansion)
   - Projected New Run Rate: ₹9,021.67 / month
   - Remaining Projected Gap: ₹978.33 / month

---

## 9. AI Voice Business Briefing (Sarvam AI Integration)

To bridge the literacy and digital divide for small shopkeepers, DukaanPilot AI integrates an **AI Voice Business Briefing** powered by **Sarvam AI Text-to-Speech**:

1. **Bilingual Structured Briefing:** Generates a comprehensive 9-section report in both English and everyday natural Hindi, covering sales totals, target pacing, stockout risks, slow-moving inventory, customer visit profiles, opportunities, and AI-recommended actions.
2. **Sarvam AI Speech Engine:** Connects to `https://api.sarvam.ai/text-to-speech` using Indian voices (`ritu` for Hindi and `priya` for English).
3. **Chunking & Caching Pipeline:** Splits long reports into sentence-aligned chunks (<1500 characters) to adhere to API constraints, while computing deterministic SHA-256 audio cache keys to eliminate redundant API billing and latency.
4. **Resilient Offline Fallback:** If Sarvam AI credentials are unset or the network fails, the written bilingual report remains completely readable, and action authorization remains fully accessible.
5. **Decoupled Approval:** Listening to the voice briefing does not auto-execute actions; shopkeepers must explicitly click Approve, Reject, or Revise to resume the LangGraph workflow.

---

## 10. Limitations and Future Improvements

### Current Limitations:
- **Synthetic Boundary:** All customer records, sales transactions, and supplier orders are synthetic. No live WhatsApp messages, SMS, or bank transfers are conducted.
- **Linear Uplift Heuristics:** Simulated tool impacts rely on conservative rule-based elasticity models rather than dynamic multi-agent market simulations.
- **Single Shop Focus:** Configurations and catalog schemas are tailored to Sneha Bhandar's retail context.

### Future Roadmap:
- **Multi-Tenant Deployment:** Extend database schemas to support multiple micro-retailers with custom inventory catalogs and supplier directories.
- **Real-Time POS Integration:** Connect read-only connectors to popular Indian retail billing apps (e.g., Vyapar, Khatabook, myBillBook).
- **Regional Dialect Expansion:** Broaden Sarvam AI speech options to include local dialects such as Khortha, Bhojpuri, and Nagpuri spoken in Jharkhand.

---

## 11. Disclosure of AI-Assisted Development

In adherence to academic integrity and project transparency standards:
- AI coding assistants were utilized during development for rapid scaffolding, test generation, and documentation drafting.
- All core architectural decisions, data validation rules, state machine transitions, human approval gates, and financial formulas were reviewed, verified, and validated against empirical test suites.
- No live customer data or external proprietary APIs were compromised during development.
