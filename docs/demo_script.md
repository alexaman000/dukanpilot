# 5–7 Minute Demo Presentation Script: DukaanPilot AI

**Target Audience:** Evaluators, Retail Mentors, and Engineering Assessors  
**Presenter Tone:** Professional, articulate, clear, and business-focused  
**Total Allocated Duration:** 6 minutes (with 1 minute buffer for Q&A)

---

## Quick Reference Timeline

| Elapsed Time | Section | Focus & Key Takeaway |
| :--- | :--- | :--- |
| **0:00 – 1:00** | Introduction & Problem Context | Kirana store pain points; Sneha Bhandar baseline & goal. |
| **1:00 – 2:00** | 📊 Business Overview & Analytics | Deterministic KPIs, period filters, low-stock inventory risks. |
| **2:00 – 2:45** | 🎯 Business Goal & Milestone Gap | Benchmarks (₹8k to ₹10k), progress gauge, demonstration boundary. |
| **2:45 – 3:45** | 🤖 AI Growth Plan & Validation | LangGraph workflow trigger, Gemini reasoning, action validation. |
| **3:45 – 4:45** | ✋ Human-in-the-Loop Approval Gate | Pause interrupt, safety controls, approve vs. reject vs. revise. |
| **4:45 – 5:45** | ⚡ Execution & Measured Outcomes | Tool execution logs, timestamps, revenue uplift, adaptive reflection. |
| **5:45 – 6:30** | 📜 Run History Audit & Conclusion | State persistence in SQLite, summary, closing takeaway. |

---

## Detailed Presentation Script

### 1. Introduction & Context (0:00 – 1:00)

**On Screen:**
Open browser at `http://localhost:8501`. Show the sidebar: **Sneha Bhandar**, Booty More, Ranchi, Jharkhand, and the "Synthetic Simulation Active" badge.

**Spoken Script:**
> *"Good morning. Today I am presenting **DukaanPilot AI**—an autonomous AI business growth worker designed specifically for micro-retailers in India.*
>
> *Across the country, millions of neighborhood grocery stores, or kiranas, operate on thin margins. The store owners handle sourcing, billing, restocking, and customer relations completely on their own. They rarely have the time or expertise to analyze daily sales records and plan data-backed growth initiatives.*
>
> *DukaanPilot AI solves this by acting not as a passive conversational chatbot, but as an operational co-worker. It analyzes actual store data, designs targeted interventions, pauses for explicit owner approval, executes simulated business actions, and measures results.*
>
> *Our demonstration scenario focuses on **Sneha Bhandar**, a neighborhood grocery shop in Ranchi, Jharkhand, working toward a concrete milestone: expanding monthly revenue from a baseline of **₹8,000** to **₹10,000**."*

---

### 2. Business Overview & Retail Analytics (1:00 – 2:00)

**On Screen:**
Click on **"📊 Business Overview"**. Point to the 5 top metric cards: Total Revenue (₹24,185.00), Gross Profit (₹13,010.50, 53.8% margin), Operating Expenses (₹2,100.00), Net Profit (₹10,910.50), and Average Basket Value (₹52.92).
Switch the **Time Period** dropdown from *"All Historical Data"* to *"January 2024"*.

**Spoken Script:**
> *"Let's examine Sneha Bhandar's operational baseline in the **Business Overview** section.*
>
> *Here, every single metric is calculated deterministically using Python and Pandas over 91 days of store records. We strictly avoid delegating financial arithmetic to LLMs to prevent hallucinations.*
>
> *Notice that across the 3-month synthetic dataset, the shop generated ₹24,185 in revenue, averaging approximately ₹8,061 per month, with a healthy 53.8% gross margin.*
>
> *When I filter by 'January 2024', the daily sales trajectory, category breakdown, best-selling products, and slow-moving items update instantly. Below, the **Low-Stock Alerts** table highlights critical items at or below reorder thresholds—such as Britannia Bread and MDH Deggi Mirch. These are direct opportunities to recover lost sales."*

---

### 3. Business Goal & Milestone Gap (2:00 – 2:45)

**On Screen:**
Click on **"🎯 Business Goal"**. Show the Milestone Progress Gauge (comparing ₹8,061.67 monthly average to the ₹10,000 target) and the monthly historical breakdown chart.

**Spoken Script:**
> *"Next, in the **Business Goal** section, we establish the target. Sneha Bhandar's baseline is set at ₹8,000 per month, with a demonstration milestone target of ₹10,000 per month.*
>
> *Our current measured monthly run rate is ₹8,061.67, leaving a remaining monthly gap of ₹1,938.33 to achieve the milestone.*
>
> *As clearly noted on screen, these figures are benchmark demonstration settings for our scenario. Now let's see how DukaanPilot AI formulates a strategy to bridge this gap."*

---

### 4. AI Growth Strategy & Action Validation (2:45 – 3:45)

**On Screen:**
Click on **"🤖 AI Growth Plan"**. Show the Thread ID input. Click **"🚀 Run Growth Planner"**.
Wait 2–3 seconds while the spinner executes. Show the generated Business Analyst Diagnostic Summary and the 4 Proposed Growth Interventions. Expand one card to show the parameters and `[AI Estimate]` badge. Scroll down to show the **Action Validation Report**.

**Spoken Script:**
> *"Now we move to the **AI Growth Plan**. I'll click **'Run Growth Planner'**.*
>
> *Behind the scenes, a LangGraph state machine initiates. First, the `analyst` node aggregates diagnostic data. Second, the `planner` node leverages the Gemini reasoning engine—or our grounded heuristic fallback if offline—to decompose the goal into 4 data-grounded actions:*
> 1. *Restocking low-inventory staples to prevent stockout losses.*
> 2. *Creating a high-margin tea and biscuits combo bundle to increase basket size.*
> 3. *Drafting a weekend promotional message for weekly family shoppers.*
> 4. *Launching a temporary flash promotion on packaged snacks.*
>
> *Every proposed action includes an explicit business rationale, parameters, costs, and risks. Notice that expected revenue numbers are explicitly labeled with `[AI Estimate]` tags.*
>
> *Crucially, before anything can happen, the `validator` node checks every action against registered tool schemas, verifying that promotional discounts do not exceed our 30% safety limit.*
>
> *Notice the yellow banner at the bottom: **The workflow has safely halted at the Human Approval gate**."*

---

### 5. Human-in-the-Loop Approval Gate (3:45 – 4:45)

**On Screen:**
Click on **"✋ Human Approval"**. Show the status badge: `"⏸️ Approval Required: Execution Halted"`. Show the list of actions with estimated costs. Point to the three action controls: **Approve Full Strategy**, **Reject Strategy**, and the expandable **Revise / Customize Actions**.
Click **"✅ Approve Full Strategy"**.

**Spoken Script:**
> *"Here is the cornerstone of our safety architecture: the **Human-in-the-Loop gate**.*
>
> *Because commercial operations require owner trust, LangGraph pauses execution using a native `interrupt()`. The entire workflow state is serialized to SQLite. Nothing can execute without an explicit decision.*
>
> *The shop owner has three clear choices:*
> - *They can **Reject** the plan—which immediately terminates the run, ensuring zero tools are executed.*
> - *They can **Revise** the plan—selecting only specific actions they feel comfortable with, which are automatically re-validated before execution.*
> - *Or they can **Approve** the plan.*
>
> *I will now click **'Approve Full Strategy'**. The workflow resumes from its saved SQLite checkpoint using its stable thread ID."*

---

### 6. Tool Execution & Measured Outcomes (4:45 – 5:45)

**On Screen:**
The page automatically reloads and indicates approval. Click on **"⚡ Execution & Outcomes"**. Show the Tool Execution Logs with green `SUCCESS` badges, tool names, and execution timestamps (`executed_at`). Scroll to the Financial Impact metrics and the Learning & Replanning Strategy summary.

**Spoken Script:**
> *"Under **Execution & Outcomes**, we can audit the complete results.*
>
> *First, we inspect the **Demonstration Tool Execution Logs**. Each tool—reordering, bundle generation, campaign drafting, and promotion creation—executed locally with full logging, error handling, and exact timestamps.*
>
> *Second, we review the **Measured Outcomes**:*
> - *Historical Monthly Baseline: ₹8,061.67*
> - *Total Simulated Uplift: +₹960.00 per month*
> - *Projected New Monthly Run Rate: ₹9,021.67*
> - *Remaining Gap: ₹978.33*
>
> *Third, the `learning` node reflects on the cycle. It notes that while substantial progress was made (+12% revenue uplift), a gap remains, recommending an additional replanning cycle within our configured iteration limit of 2 cycles."*

---

### 7. Run History Audit & Conclusion (5:45 – 6:30)

**On Screen:**
Click on **"📜 Run History"**. Show the audit trail table showing the thread ID, timestamps, status, approval state, and uplift.
Show the **Reopen Saved Workflow Session** dropdown.

**Spoken Script:**
> *"Finally, in **Run History**, every workflow session is permanently recorded in our SQLite database.*
>
> *Even if the server restarts or the browser is refreshed, an owner can select any previous session and click **'Reopen Selected Session'** to restore the state snapshot or continue a paused workflow without repeating earlier steps.*
>
> *To summarize:*
> - *DukaanPilot AI replaces conversational guesswork with a closed-loop autonomous workflow.*
> - *It couples deterministic financial analytics with generative AI planning.*
> - *It enforces hard human approval gates and schema safety limits.*
> - *And it persists all state transparently for full accountability.*
>
> *Thank you. I am now open to your questions."*
