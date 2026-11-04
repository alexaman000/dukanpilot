"""Generate a high-resolution, professional architecture diagram for DukaanPilot AI."""

import os
from PIL import Image, ImageDraw, ImageFont


def draw_rounded_rectangle(draw, box, radius, fill, outline, width=2):
    """Draw a rounded rectangle with custom border width."""
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def draw_arrow(draw, start, end, color="#64748b", width=2, arrow_size=8):
    """Draw a straight arrow from start (x1, y1) to end (x2, y2)."""
    draw.line([start, end], fill=color, width=width)
    x1, y1 = start
    x2, y2 = end
    import math
    angle = math.atan2(y2 - y1, x2 - x1)
    # Arrowhead points
    p1 = (
        x2 - arrow_size * math.cos(angle - math.pi / 6),
        y2 - arrow_size * math.sin(angle - math.pi / 6),
    )
    p2 = (
        x2 - arrow_size * math.cos(angle + math.pi / 6),
        y2 - arrow_size * math.sin(angle + math.pi / 6),
    )
    draw.polygon([end, p1, p2], fill=color)


def build_diagram():
    # 1600 x 1050 Canvas
    width, height = 1600, 1050
    img = Image.new("RGBA", (width, height), "#0f172a")  # Dark slate background
    draw = ImageDraw.Draw(img)

    # Use default bitmap or truetype font
    try:
        font_title = ImageFont.truetype("arial.ttf", 28)
        font_subtitle = ImageFont.truetype("arial.ttf", 16)
        font_header = ImageFont.truetype("arial.ttf", 18)
        font_body = ImageFont.truetype("arial.ttf", 13)
        font_bold = ImageFont.truetype("arialbd.ttf", 14)
        font_badge = ImageFont.truetype("arialbd.ttf", 11)
    except Exception:
        font_title = ImageFont.load_default()
        font_subtitle = font_title
        font_header = font_title
        font_body = font_title
        font_bold = font_title
        font_badge = font_title

    # Header section
    draw.text((60, 40), "DukaanPilot AI - System Architecture & Workflow Loop", fill="#f8fafc", font=font_title)
    draw.text(
        (60, 80),
        "Autonomous AI Business Growth Worker for Sneha Bhandar (Ranchi, Jharkhand) | Phase 5 Production Architecture",
        fill="#94a3b8",
        font=font_subtitle,
    )

    # Section 1: Presentation & Interface Layer (Top Left)
    draw_rounded_rectangle(draw, (60, 130, 480, 520), 12, fill="#1e293b", outline="#334155", width=2)
    draw.text((80, 150), "1. Streamlit Dashboard (UI / Portal)", fill="#38bdf8", font=font_header)
    draw.text((80, 175), "Interactive store monitor & operations portal (app.py)", fill="#64748b", font=font_body)

    ui_cards = [
        ("Business Overview", "Total Revenue, Margins, ATV, Daily Trajectory, Categories"),
        ("Business Goal", "Baseline (₹8k), Target (₹10k), Progress Gauge, Milestone Delta"),
        ("AI Growth Plan", "Run Strategy Planner, Action Proposals, Impact Projections"),
        ("Human Approval Gate", "Interactive Approve, Reject, and Action Revision controls"),
        ("Execution & Outcomes", "Simulated tool logs, Execution timestamps, Uplift tracking"),
        ("Run History Audit", "Checkpointed session history & thread resumption"),
    ]
    y_pos = 205
    for title, desc in ui_cards:
        draw_rounded_rectangle(draw, (80, y_pos, 460, y_pos + 42), 6, fill="#0f172a", outline="#1e3a8a", width=1)
        draw.text((95, y_pos + 5), title, fill="#e2e8f0", font=font_bold)
        draw.text((95, y_pos + 22), desc, fill="#94a3b8", font=font_badge)
        y_pos += 48

    # Section 2: Data & Persistence Layer (Bottom Left)
    draw_rounded_rectangle(draw, (60, 560, 480, 980), 12, fill="#1e293b", outline="#334155", width=2)
    draw.text((80, 580), "2. Data & Persistence Layer", fill="#a78bfa", font=font_header)
    draw.text((80, 605), "Offline deterministic datasets & LangGraph checkpointer", fill="#64748b", font=font_body)

    # Sub-box: SQLite Persistence
    draw_rounded_rectangle(draw, (80, 635, 460, 770), 8, fill="#0f172a", outline="#6d28d9", width=2)
    draw.text((95, 650), "SQLite Persistence Checkpointer", fill="#c4b5fd", font=font_bold)
    draw.text((95, 675), "• database/dukaanpilot.db (SqliteSaver)", fill="#cbd5e1", font=font_body)
    draw.text((95, 695), "• Checkpoint state serialization & thread tracking", fill="#94a3b8", font=font_body)
    draw.text((95, 715), "• Task interrupts & resume across restarts", fill="#94a3b8", font=font_body)
    draw.text((95, 735), "• Full execution audit trail (workflow_run_history)", fill="#94a3b8", font=font_body)

    # Sub-box: Synthetic CSV Datasets
    draw_rounded_rectangle(draw, (80, 790, 460, 955), 8, fill="#0f172a", outline="#475569", width=2)
    draw.text((95, 805), "Synthetic CSV Store Records (data/)", fill="#94a3b8", font=font_bold)
    draw.text((95, 830), "• sales.csv (457 transactions over 91 days)", fill="#cbd5e1", font=font_body)
    draw.text((95, 850), "• products.csv (20 items, costs, reorder thresholds)", fill="#cbd5e1", font=font_body)
    draw.text((95, 870), "• expenses.csv (monthly shop overheads)", fill="#cbd5e1", font=font_body)
    draw.text((95, 890), "• customers.csv & promotions.csv", fill="#cbd5e1", font=font_body)
    draw.text((95, 915), "Enforced via database/data_loader.py (integrity checked)", fill="#64748b", font=font_badge)

    # Section 3: Core LangGraph State Machine & Orchestrator (Center & Right)
    draw_rounded_rectangle(draw, (530, 130, 1150, 980), 12, fill="#1e293b", outline="#334155", width=2)
    draw.text((550, 150), "3. LangGraph Workflow Orchestrator (workflow/graph.py)", fill="#34d399", font=font_header)
    draw.text((550, 175), "State machine: StateGraph(WorkflowState) with conditional interrupt & cyclic loop", fill="#64748b", font=font_body)

    # Graph nodes
    nodes = [
        ("Node 1: analyst", "BusinessAnalyst (Deterministic Pandas Engine)", "#065f46", "#047857", 215),
        ("Node 2: planner", "Growth Planner (Gemini API / Grounded Heuristics)", "#1e3a8a", "#1d4ed8", 305),
        ("Node 3: validator", "Action Validator (Schema bounds & Safety checks)", "#831843", "#be185d", 395),
        ("Node 4: human_approval", "Human-in-the-Loop Interrupt Gate (Command resume)", "#78350f", "#b45309", 485),
        ("Node 5: executor", "Tool Execution Engine (Safe simulated tool calls)", "#065f46", "#059669", 635),
        ("Node 6: measurement", "Outcome Evaluator (Uplift vs Baseline evidence)", "#1e3a8a", "#2563eb", 725),
        ("Node 7: learning", "Strategic Reflection (Loop router & Iteration limit)", "#4c1d95", "#6d28d9", 815),
    ]

    for name, desc, bg, border, y in nodes:
        draw_rounded_rectangle(draw, (560, y, 1120, y + 60), 8, fill=bg, outline=border, width=2)
        draw.text((580, y + 10), name, fill="#ffffff", font=font_bold)
        draw.text((580, y + 32), desc, fill="#e2e8f0", font=font_body)

    # Connecting vertical arrows inside LangGraph
    draw_arrow(draw, (840, 275), (840, 305), color="#34d399", width=2)
    draw_arrow(draw, (840, 365), (840, 395), color="#34d399", width=2)
    draw_arrow(draw, (840, 455), (840, 485), color="#34d399", width=2)
    draw_arrow(draw, (840, 545), (840, 635), color="#34d399", width=2)
    draw.text((850, 580), "Approve / Revise", fill="#4ade80", font=font_bold)

    # Branch: Rejection Node
    draw_rounded_rectangle(draw, (920, 550, 1120, 605), 8, fill="#450a0a", outline="#dc2626", width=2)
    draw.text((935, 560), "rejection node", fill="#fca5a5", font=font_bold)
    draw.text((935, 580), "Halt with 0 tools run", fill="#f87171", font=font_badge)
    draw_arrow(draw, (880, 530), (920, 565), color="#f87171", width=2)

    # Post-execution flow
    draw_arrow(draw, (840, 695), (840, 725), color="#34d399", width=2)
    draw_arrow(draw, (840, 785), (840, 815), color="#34d399", width=2)

    # Replanning Loop Curve / Arrow from Learning to Planner
    draw.line([(560, 845), (540, 845), (540, 335), (560, 335)], fill="#fbbf24", width=3)
    draw_arrow(draw, (540, 335), (560, 335), color="#fbbf24", width=3)
    draw.text((545, 410), "Replanning Loop (if gap > 0 & iter < max)", fill="#fbbf24", font=font_bold)

    # Section 4: External Engines & Tools (Right Side)
    draw_rounded_rectangle(draw, (1200, 130, 1540, 520), 12, fill="#1e293b", outline="#334155", width=2)
    draw.text((1220, 150), "4. Reasoning Core", fill="#f43f5e", font=font_header)
    draw.text((1220, 175), "LLM & Analytical Intelligence", fill="#64748b", font=font_body)

    draw_rounded_rectangle(draw, (1220, 210, 1520, 330), 8, fill="#0f172a", outline="#be123c", width=2)
    draw.text((1235, 225), "Gemini API Reasoning", fill="#fda4af", font=font_bold)
    draw.text((1235, 250), "• Model: gemini-2.0-flash", fill="#cbd5e1", font=font_body)
    draw.text((1235, 270), "• Goal decomposition & rationale", fill="#94a3b8", font=font_body)
    draw.text((1235, 290), "• Strict JSON schema output", fill="#94a3b8", font=font_body)

    draw_rounded_rectangle(draw, (1220, 350, 1520, 480), 8, fill="#0f172a", outline="#0284c7", width=2)
    draw.text((1235, 365), "Deterministic Fallback Engine", fill="#7dd3fc", font=font_bold)
    draw.text((1235, 390), "• Automatic offline engaging", fill="#cbd5e1", font=font_body)
    draw.text((1235, 410), "• Domain heuristic generator", fill="#94a3b8", font=font_body)
    draw.text((1235, 430), "• Grounded in actual low-stock data", fill="#94a3b8", font=font_body)

    # Section 5: Local Demonstration Tools (Bottom Right)
    draw_rounded_rectangle(draw, (1200, 560, 1540, 980), 12, fill="#1e293b", outline="#334155", width=2)
    draw.text((1220, 580), "5. Simulated Local Tools (tools/)", fill="#fb923c", font=font_header)
    draw.text((1220, 605), "Safe local execution - zero live external mutations", fill="#64748b", font=font_body)

    tools = [
        ("create_simulated_promotion", "Category promotional discount (1-30%)", "PROM-SIM records, volume uplift model"),
        ("recommend_product_bundle", "Cross-sell combo bundles (e.g. Chai + Biscuits)", "Joint margin calculation, AOV lift"),
        ("create_reorder_suggestion", "Wholesale inventory procurement order draft", "Supplier lead-time, working capital cost"),
        ("draft_customer_campaign", "Targeted customer segment message draft", "Segment matching (WhatsApp/SMS templates)"),
    ]
    ty = 635
    for t_name, t_sub, t_detail in tools:
        draw_rounded_rectangle(draw, (1220, ty, 1520, ty + 68), 6, fill="#0f172a", outline="#ea580c", width=1)
        draw.text((1235, ty + 8), t_name, fill="#fed7aa", font=font_bold)
        draw.text((1235, ty + 28), t_sub, fill="#cbd5e1", font=font_badge)
        draw.text((1235, ty + 46), t_detail, fill="#94a3b8", font=font_badge)
        ty += 78

    # Connecting arrows across layers
    # UI <--> Orchestrator
    draw_arrow(draw, (480, 240), (530, 240), color="#38bdf8", width=2)
    draw_arrow(draw, (530, 510), (480, 510), color="#fbbf24", width=2)
    # Orchestrator <--> Data Layer
    draw_arrow(draw, (530, 700), (480, 700), color="#a78bfa", width=2)
    # Orchestrator <--> Reasoning
    draw_arrow(draw, (1150, 335), (1200, 335), color="#fda4af", width=2)
    # Executor --> Tools
    draw_arrow(draw, (1150, 665), (1200, 665), color="#fb923c", width=2)

    # Save diagram
    os.makedirs("docs", exist_ok=True)
    out_path = os.path.join("docs", "architecture.png")
    img.save(out_path, "PNG")
    print(f"Architecture diagram successfully generated at {out_path} ({width}x{height})")


if __name__ == "__main__":
    build_diagram()
