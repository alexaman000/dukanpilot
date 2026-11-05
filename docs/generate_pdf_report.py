"""Generate a publication-grade, professional PDF technical report for DukaanPilot AI."""

import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, KeepTogether, PageBreak, HRFlowable
)
from reportlab.pdfgen import canvas


class NumberedCanvas(canvas.Canvas):
    """Canvas that enables two-pass 'Page X of Y' numbering and running header/footer."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_header_footer(num_pages)
            super().showPage()
        super().save()

    def draw_header_footer(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748b"))

        # Header (Pages > 1)
        if self._pageNumber > 1:
            self.drawString(54, 11 * 72 - 36, "DukaanPilot AI — Technical Architecture & Failure Recovery Report")
            self.drawRightString(8.5 * 72 - 54, 11 * 72 - 36, "Sneha Bhandar (Ranchi, Jharkhand)")
            self.setStrokeColor(colors.HexColor("#e2e8f0"))
            self.setLineWidth(0.5)
            self.line(54, 11 * 72 - 42, 8.5 * 72 - 54, 11 * 72 - 42)

        # Footer (All pages)
        self.setStrokeColor(colors.HexColor("#e2e8f0"))
        self.setLineWidth(0.5)
        self.line(54, 46, 8.5 * 72 - 54, 46)
        self.drawString(54, 34, "Confidential — Evaluator Technical Note | Autonomous Retail AI Worker")
        page_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(8.5 * 72 - 54, 34, page_text)
        self.restoreState()


def generate_report():
    base_dir = os.path.dirname(__file__)
    pdf_path = os.path.join(base_dir, "DukaanPilot_AI_Technical_Report.pdf")

    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54,
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=24,
        leading=28,
        textColor=colors.HexColor("#0f172a"),
        spaceAfter=6,
    )
    subtitle_style = ParagraphStyle(
        "DocSubTitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#0284c7"),
        spaceAfter=14,
    )
    h1_style = ParagraphStyle(
        "Heading1_Custom",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=14,
        leading=18,
        textColor=colors.HexColor("#0f172a"),
        spaceBefore=14,
        spaceAfter=6,
        keepWithNext=True,
    )
    h2_style = ParagraphStyle(
        "Heading2_Custom",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=15,
        textColor=colors.HexColor("#1e293b"),
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True,
    )
    body_style = ParagraphStyle(
        "Body_Custom",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#334155"),
        spaceAfter=6,
    )
    body_bold = ParagraphStyle(
        "BodyBold_Custom",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#0f172a"),
        spaceAfter=6,
    )
    callout_style = ParagraphStyle(
        "Callout_Custom",
        parent=styles["Normal"],
        fontName="Helvetica-Oblique",
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#1e293b"),
    )
    table_text = ParagraphStyle(
        "TableText",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#1e293b"),
    )
    table_header = ParagraphStyle(
        "TableHeader",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#ffffff"),
    )

    story = []

    # Title & Subtitle Banner
    story.append(Paragraph("DukaanPilot AI — Technical Architecture & System Report", title_style))
    story.append(Paragraph("Autonomous Closed-Loop AI Business Growth Worker for Micro-Retailers | Sneha Bhandar (Ranchi)", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0284c7"), spaceAfter=12))

    # Metadata Card
    meta_data = [
        [
            Paragraph("<b>Target Retailer:</b> Sneha Bhandar (Grocery / Kirana)", table_text),
            Paragraph("<b>Location:</b> Shiv Shakti Nagar, Booty More, Ranchi, Jharkhand (834009)", table_text),
        ],
        [
            Paragraph("<b>Milestone Goal:</b> Baseline ₹8,000 → Target ₹10,000 / month", table_text),
            Paragraph("<b>Key Orchestrator:</b> LangGraph Cyclic StateGraph + SQLite Checkpointer", table_text),
        ],
        [
            Paragraph("<b>Speech Synthesis:</b> Sarvam AI TTS (Bilingual Hindi / English)", table_text),
            Paragraph("<b>Safety Architecture:</b> Human-in-the-Loop Interrupt Gate + Zero Phantom Uplift", table_text),
        ],
    ]
    meta_table = Table(meta_data, colWidths=[240, 264])
    meta_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
        ("BOX", (0, 0), (-1, -1), 0.75, colors.HexColor("#cbd5e1")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 10))

    # Section 1: Executive Summary & Objective
    story.append(Paragraph("1. Executive Summary & Problem Formulation", h1_style))
    story.append(Paragraph(
        "Micro-retailers across India—such as neighborhood <i>kirana</i> stores—operate on thin margins and juggle multiple operational responsibilities: purchasing inventory, balancing cash vs. credit (<i>khata</i>), and servicing walk-in patrons. Store owners lack dedicated data analysts or merchandisers, resulting in trapped working capital, frequent stockouts of fast-moving staples, and missed margin opportunities. "
        "<b>DukaanPilot AI</b> transforms passive retail ledger records into proactive, goal-directed interventions. Operating within a strictly verified offline simulation boundary for <b>Sneha Bhandar</b> (Ranchi), the autonomous worker ingests 91 days of transactions, formulates strategic promotions and bundle deals, halts at mandatory human approval gates, executes simulated operational tools, and evaluates uplift against verified historical baselines.",
        body_style,
    ))

    # Section 2: AI Worker vs Chatbot
    story.append(Paragraph("2. Why an Autonomous AI Worker Rather Than a Chatbot?", h1_style))
    comp_data = [
        [Paragraph("Architectural Dimension", table_header), Paragraph("Conventional Chatbot", table_header), Paragraph("DukaanPilot AI Worker", table_header)],
        [Paragraph("<b>Operating Mode</b>", table_text), Paragraph("Passive request-response; waits for queries.", table_text), Paragraph("Proactive goal-driven loop; drives monthly targets.", table_text)],
        [Paragraph("<b>Arithmetic Precision</b>", table_text), Paragraph("Delegates math to LLM (frequent hallucinations).", table_text), Paragraph("Deterministic Pandas engine; 100% verified math.", table_text)],
        [Paragraph("<b>Action Execution</b>", table_text), Paragraph("Emits markdown advice; cannot execute actions.", table_text), Paragraph("Dispatches schema-validated tools with structured logs.", table_text)],
        [Paragraph("<b>State Durability</b>", table_text), Paragraph("Ephemeral context; resets on browser refresh.", table_text), Paragraph("SQLite-backed checkpoints; resumes across restarts.", table_text)],
        [Paragraph("<b>Safety Architecture</b>", table_text), Paragraph("Vague system prompts ('please be careful').", table_text), Paragraph("Hard LangGraph interrupt() gates requiring authorization.", table_text)],
        [Paragraph("<b>Closed-Loop Learning</b>", table_text), Paragraph("Open-loop; zero outcome verification.", table_text), Paragraph("Measures uplift vs baselines and replans adaptively.", table_text)],
    ]
    comp_table = Table(comp_data, colWidths=[120, 180, 204])
    comp_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f172a")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#ffffff"), colors.HexColor("#f8fafc")]),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(comp_table)
    story.append(Spacer(1, 10))

    # Section 3: System Architecture
    story.append(Paragraph("3. System Architecture & Component Design", h1_style))
    story.append(Paragraph(
        "DukaanPilot AI employs a modular 4-layer architecture comprising (1) Presentation (Streamlit + Sarvam AI UI), (2) Orchestration (LangGraph StateGraph), (3) Deterministic Analytics & LLM Reasoning Core (Pandas + Gemini 2.0 Flash), and (4) Persistence (SQLite checkpointer).",
        body_style,
    ))
    arch_img_path = os.path.join(base_dir, "architecture.png")
    if os.path.exists(arch_img_path):
        story.append(Image(arch_img_path, width=504, height=330))
        story.append(Spacer(1, 6))

    # Page Break for Failure Scenario
    story.append(PageBreak())

    # Section 4: Dedicated Failure Scenario & Recovery Strategy
    story.append(Paragraph("4. Dedicated Failure Scenario: Business Tool Execution Failure", h1_style))
    story.append(Paragraph(
        "<b>Scenario Context:</b> DukaanPilot AI analyzes 91 days of transaction ledgers for Sneha Bhandar and detects that packaged snacks and beverages have high footfall but small ticket sizes. The Growth Planner (<code>planner_node</code>) formulates a recommendation: launch a 'Weekend Family Snack Special' offering a 5% discount on snacks to boost basket value (projecting an estimated monthly uplift of +₹350). The shopkeeper inspects the proposal in the dashboard and clicks <b>'Approve'</b>. "
        "However, when the worker attempts to dispatch <code>create_simulated_promotion</code> in <code>executor_node</code>, the simulated business tool encounters an <b>unexpected technical error</b> (such as a database file lock, downstream repository timeout, or catalog parameter serialization mismatch).",
        body_style,
    ))

    story.append(Paragraph("The 7 Stages of Resilient Failure Handling:", h2_style))

    stages_data = [
        [
            Paragraph("<b>Stage 1: Failure Detection</b>", table_header),
            Paragraph("The dispatcher (<code>tools.registry.execute_action</code>) wraps every tool call in a structured <code>try...except Exception as exc:</code> boundary. Unhandled exceptions are trapped immediately before they can crash the LangGraph workflow runtime, constructing an explicit payload: <code>{'status': 'failed', 'tool': ..., 'error': str(exc)}</code>.", table_text),
        ],
        [
            Paragraph("<b>Stage 2: Error Reporting</b>", table_header),
            Paragraph("The system never masks errors or claims false success. The <code>executor_node</code> appends a structured failure entry into <code>WorkflowState['execution_results']</code> with timestamp and full error diagnostics. The Streamlit dashboard renders prominent alert badges (<code>🚨 FAILED</code>) notifying the shopkeeper immediately.", table_text),
        ],
        [
            Paragraph("<b>Stage 3: State Preservation</b>", table_header),
            Paragraph("LangGraph's <code>SqliteSaver</code> checkpointer commits the complete state to <code>database/dukaanpilot.db</code> after every transition. The shop's baseline metrics, original recommendations, approval timestamps, and partial tool logs remain intact. If the application restarts, execution resumes from the saved checkpoint without data loss.", table_text),
        ],
        [
            Paragraph("<b>Stage 4: Execution Safety</b>", table_header),
            Paragraph("The failed action is strictly marked as <code>failed</code> and never marked completed. The evaluation engine (<code>workflow/evaluator.py</code>) filters successful runs only; failed actions contribute exactly <b>₹0.00</b> simulated revenue uplift. No phantom gains are attributed. Unaffected batch tools continue executing independently.", table_text),
        ],
        [
            Paragraph("<b>Stage 5: Recovery Strategy</b>", table_header),
            Paragraph("The <code>learning_node</code> reflects on failures, setting <code>should_replan = True</code>. In the UI, the owner is offered two distinct paths: (A) <b>Safe Retry / Revision</b> via the revision panel with adjusted parameters, or (B) <b>Safe Cancellation</b>, terminating the run with zero unapproved side effects.", table_text),
        ],
        [
            Paragraph("<b>Stage 6: Human Supervision</b>", table_header),
            Paragraph("No autonomous background retries alter retail state without human oversight. Any retried or modified action must re-pass <code>ActionValidator</code> (schema rules & ≤30% discount ceiling) and pause at the <code>human_approval</code> gate via <code>interrupt()</code> for explicit owner consent.", table_text),
        ],
        [
            Paragraph("<b>Stage 7: Failure Logging</b>", table_header),
            Paragraph("Full diagnostic telemetry—action ID, tool name, submitted parameters, timestamp (<code>executed_at</code>), and error stack trace—is persisted to SQLite (<code>workflow_run_history</code>) for post-mortem auditing, compliance, and debugging.", table_text),
        ],
    ]
    stages_table = Table(stages_data, colWidths=[130, 374])
    stages_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#1e293b")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("ROWBACKGROUNDS", (1, 0), (1, -1), [colors.HexColor("#ffffff"), colors.HexColor("#f8fafc")]),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(stages_table)
    story.append(Spacer(1, 10))

    # Section 5: Flow Diagram
    story.append(Paragraph("5. Failure Recovery Flow Architecture", h1_style))
    rec_img_path = os.path.join(base_dir, "failure_recovery_diagram.png")
    if os.path.exists(rec_img_path):
        story.append(Image(rec_img_path, width=504, height=360))
        story.append(Spacer(1, 6))

    # Page Break for Evaluation Table & Limitations
    story.append(PageBreak())

    # Section 6: Failure Handling Evaluation Table
    story.append(Paragraph("6. Failure Handling Evaluation Matrix", h1_style))
    eval_matrix = [
        [
            Paragraph("Failure Condition", table_header),
            Paragraph("Expected Worker Behaviour", table_header),
            Paragraph("Safety Mechanism", table_header),
            Paragraph("Recovery Approach", table_header),
        ],
        [
            Paragraph("<b>Tool Execution Failure</b><br/><i>(Timeout, I/O lock, key mismatch)</i>", table_text),
            Paragraph("Intercept error at boundary; set status='failed'; log error; attribute ₹0 uplift; continue other batch tools.", table_text),
            Paragraph("<code>try...except</code> in registry.py; zero-uplift filter in evaluator.py; schema boundary rules.", table_text),
            Paragraph("Isolate failed tool; trigger replanning in learning node; offer owner parameter revision & re-approval.", table_text),
        ],
        [
            Paragraph("<b>Missing / Corrupted Data</b><br/><i>(Missing CSV, NaN price, broken foreign keys)</i>", table_text),
            Paragraph("Halt data ingestion before computation; prevent corrupt records from reaching LLM or tools; alert user.", table_text),
            Paragraph("<code>validate_data_integrity()</code> enforces primary keys, non-null values, and positive prices.", table_text),
            Paragraph("Report exact schema breach; fall back to verified default synthetic dataset; emit diagnostic logs.", table_text),
        ],
        [
            Paragraph("<b>Gemini API Unavailable</b><br/><i>(Network timeout, quota exhausted, invalid key)</i>", table_text),
            Paragraph("Formulate grounded strategic actions without crashing, hanging, or requiring active internet.", table_text),
            Paragraph("Heuristic rule-based fallback in <code>generate_fallback_plan()</code>; structured JSON validation.", table_text),
            Paragraph("Automatically route to deterministic recommendations; tag plan with <code>planner_source: 'fallback'</code>.", table_text),
        ],
        [
            Paragraph("<b>Interrupted Workflow</b><br/><i>(Tab close, server kill, power outage mid-session)</i>", table_text),
            Paragraph("Retain exact state snapshot and pending interrupts; avoid duplicate runs or restarting analysis.", table_text),
            Paragraph("LangGraph <code>SqliteSaver</code> checkpointer commits state to SQLite after every node execution.", table_text),
            Paragraph("Re-open session with identical thread ID; <code>get_state()</code> restores pending interrupt cleanly.", table_text),
        ],
        [
            Paragraph("<b>Duplicate Execution Attempt</b><br/><i>(Double click, browser refresh, multi-POST)</i>", table_text),
            Paragraph("Execute approved actions exactly once; ignore redundant clicks; prevent multiple orders/discounts.", table_text),
            Paragraph("Idempotent thread IDs; state execution tracking (<code>workflow_status: 'executed'</code>).", table_text),
            Paragraph("Inspect thread state before dispatch; return cached execution results if thread is already executed.", table_text),
        ],
    ]
    eval_table = Table(eval_matrix, colWidths=[100, 134, 134, 136])
    eval_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f172a")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#ffffff"), colors.HexColor("#f8fafc")]),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(eval_table)
    story.append(Spacer(1, 10))

    # Section 7: Limitations & Future Improvements
    story.append(Paragraph("7. Implementation Status, Limitations, and Production Roadmap", h1_style))
    story.append(Paragraph(
        "To maintain rigorous technical transparency, DukaanPilot AI explicitly distinguishes verified implemented features from future architectural enhancements:",
        body_style,
    ))

    status_data = [
        [
            Paragraph("<b>Existing Implemented Capabilities (Verified in 66 Automated Tests)</b>", table_header),
            Paragraph("<b>Proposed Future Improvements (Architecture Roadmap)</b>", table_header),
        ],
        [
            Paragraph(
                "• <b>Structured Exception Trapping:</b> <code>tools.registry.execute_action</code> prevents runtime crashes.<br/>"
                "• <b>Zero Phantom Uplift:</b> Evaluator assigns ₹0.00 revenue to failed actions.<br/>"
                "• <b>Durable SQLite State:</b> <code>SqliteSaver</code> preserves complete thread history across restarts.<br/>"
                "• <b>Transparent UI Diagnostics:</b> Red failure badges and error traces rendered in dashboard.<br/>"
                "• <b>Mandatory Re-Validation:</b> Custom/revised actions must re-pass schema & discount checks.<br/>"
                "• <b>Bilingual Voice Briefing:</b> Sarvam AI TTS with text chunking and SHA-256 audio caching.",
                table_text,
            ),
            Paragraph(
                "• <b>Automatic Retries with Controlled Limits:</b> Jittered exponential backoff (max 3 attempts) with circuit breakers for transient I/O faults.<br/>"
                "• <b>Real-Time API Failure Monitoring:</b> OpenTelemetry tracing and Prometheus metrics for API latency and failure alarms.<br/>"
                "• <b>Real-World POS Tool Integrations:</b> Live authenticated connectors for Vyapar, Khatabook, and WhatsApp Business API.<br/>"
                "• <b>Compensating Rollback Sagas:</b> Automated reversing transactions for multi-step operational failures.<br/>"
                "• <b>Cryptographic Audit Trail:</b> Hash-chained (SHA-256) immutable ledgers for compliance and dispute resolution.",
                table_text,
            ),
        ],
    ]
    status_table = Table(status_data, colWidths=[250, 254])
    status_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e293b")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("BACKGROUND", (0, 1), (-1, 1), colors.HexColor("#f8fafc")),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(status_table)
    story.append(Spacer(1, 12))

    # Conclusion & Signoff Callout Box
    signoff_data = [[
        Paragraph(
            "<b>Integrity & Verification Note:</b> All business arithmetic, financial margins, and inventory formulas are deterministically computed with Python/Pandas. LLMs are never permitted to hallucinate business figures. All tool simulations operate safely offline. Verified against a comprehensive 66-test automated suite.",
            callout_style,
        )
    ]]
    signoff_table = Table(signoff_data, colWidths=[504])
    signoff_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#ecfdf5")),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#10b981")),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
    ]))
    story.append(signoff_table)

    # Build PDF
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Successfully generated publication-grade PDF technical report at: {pdf_path}")


if __name__ == "__main__":
    generate_report()
