"""Generate a high-resolution, professional failure recovery flow diagram for DukaanPilot AI."""

import os
import math
from PIL import Image, ImageDraw, ImageFont


def draw_rounded_rectangle(draw, box, radius, fill, outline, width=2):
    """Draw a rounded rectangle with custom border width."""
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def draw_arrow(draw, start, end, color="#64748b", width=2, arrow_size=10):
    """Draw a straight arrow from start (x1, y1) to end (x2, y2)."""
    draw.line([start, end], fill=color, width=width)
    x1, y1 = start
    x2, y2 = end
    angle = math.atan2(y2 - y1, x2 - x1)
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
    # 1600 x 1150 Canvas
    width, height = 1600, 1150
    img = Image.new("RGBA", (width, height), "#0f172a")  # Dark slate background
    draw = ImageDraw.Draw(img)

    # Use Arial truetype fonts or fallback
    try:
        font_title = ImageFont.truetype("arial.ttf", 30)
        font_subtitle = ImageFont.truetype("arial.ttf", 16)
        font_header = ImageFont.truetype("arial.ttf", 18)
        font_body = ImageFont.truetype("arial.ttf", 13)
        font_bold = ImageFont.truetype("arialbd.ttf", 15)
        font_bold_lg = ImageFont.truetype("arialbd.ttf", 17)
        font_badge = ImageFont.truetype("arialbd.ttf", 11)
        font_code = ImageFont.truetype("consola.ttf", 12)
    except Exception:
        font_title = ImageFont.load_default()
        font_subtitle = font_title
        font_header = font_title
        font_body = font_title
        font_bold = font_title
        font_bold_lg = font_title
        font_badge = font_title
        font_code = font_title

    # Header section
    draw.text((60, 40), "DukaanPilot AI - Failure Scenario & Recovery Architecture", fill="#f8fafc", font=font_title)
    draw.text(
        (60, 82),
        "Scenario: Promotional Campaign Execution Tool Failure | 7-Stage Resilient Recovery & Human Supervision Flow",
        fill="#94a3b8",
        font=font_subtitle,
    )

    # Decorative header rule
    draw.line([(60, 115), (1540, 115)], fill="#334155", width=2)

    # -------------------------------------------------------------
    # Left Column: The 7 Stages Reference Guide (Cards)
    # -------------------------------------------------------------
    left_x1, left_x2 = 60, 520
    draw_rounded_rectangle(draw, (left_x1, 135, left_x2, 1100), 12, fill="#1e293b", outline="#334155", width=2)
    draw.text((left_x1 + 20, 155), "7 Stages of Failure Handling", fill="#38bdf8", font=font_header)
    draw.text((left_x1 + 20, 180), "How DukaanPilot AI prevents data corruption & false claims", fill="#64748b", font=font_body)

    stages_info = [
        ("1. Failure Detection", "tools.registry traps exceptions in try...except;\ncatches parameter mismatches, timeouts, or data errors.", "#0284c7"),
        ("2. Error Reporting", "Records status: 'failed' with error string;\nsurfaces explicit red alert badges in Streamlit dashboard.", "#f59e0b"),
        ("3. State Preservation", "LangGraph checkpointer serializes state to SQLite;\npreserves session history, action IDs, and shop context.", "#8b5cf6"),
        ("4. Execution Safety", "Failed action earns zero (₹0) simulated revenue uplift;\nprevents phantom gains and prohibits silent re-runs.", "#ef4444"),
        ("5. Recovery Decision", "System offers clear fork: safe retry with revised inputs\nor explicit cancellation preserving historical state.", "#10b981"),
        ("6. Human Supervision", "All retry candidates must re-pass ActionValidator\nand require explicit owner consent before execution.", "#d97706"),
        ("7. Failure Logging", "Logs timestamp, tool name, full payload, and stack trace\nto workflow_run_history for audit and diagnosis.", "#06b6d4"),
    ]

    card_y = 215
    for title, desc, accent_color in stages_info:
        draw_rounded_rectangle(draw, (left_x1 + 16, card_y, left_x2 - 16, card_y + 110), 8, fill="#0f172a", outline="#334155", width=1)
        # Accent bar on left of card
        draw.rounded_rectangle((left_x1 + 16, card_y, left_x1 + 22, card_y + 110), radius=2, fill=accent_color)
        draw.text((left_x1 + 32, card_y + 12), title, fill="#f1f5f9", font=font_bold)
        
        # Multiline description
        lines = desc.split("\n")
        y_text = card_y + 36
        for line in lines:
            draw.text((left_x1 + 32, y_text), line, fill="#94a3b8", font=font_body)
            y_text += 20
        card_y += 124

    # -------------------------------------------------------------
    # Right Column: The Core Visual Flow Diagram
    # -------------------------------------------------------------
    right_x1, right_x2 = 550, 1540
    draw_rounded_rectangle(draw, (right_x1, 135, right_x2, 1100), 12, fill="#1e293b", outline="#334155", width=2)
    draw.text((right_x1 + 25, 155), "Workflow Execution & Failure Recovery Flow", fill="#34d399", font=font_header)
    draw.text((right_x1 + 25, 180), "State transitions from strategy recommendation to error trap and branch resolution", fill="#64748b", font=font_body)

    # Box coordinates & helper
    center_x = (right_x1 + right_x2) // 2  # 1045
    box_w = 460
    b_half = box_w // 2

    # Step 1: AI Recommendation
    y1 = 220
    draw_rounded_rectangle(draw, (center_x - b_half, y1, center_x + b_half, y1 + 54), 8, fill="#1e3a8a", outline="#3b82f6", width=2)
    draw.text((center_x - b_half + 20, y1 + 10), "AI Recommendation", fill="#ffffff", font=font_bold_lg)
    draw.text((center_x - b_half + 20, y1 + 32), "Planner suggests: 'Launch Weekend Special Promotion' (5% off Snacks)", fill="#93c5fd", font=font_body)
    draw_rounded_rectangle(draw, (center_x + b_half - 110, y1 + 10, center_x + b_half - 15, y1 + 30), 4, fill="#1d4ed8", outline="#60a5fa", width=1)
    draw.text((center_x + b_half - 98, y1 + 14), "PROPOSED", fill="#ffffff", font=font_badge)

    # Arrow 1 -> 2
    draw_arrow(draw, (center_x, y1 + 54), (center_x, y1 + 86), color="#38bdf8", width=3)

    # Step 2: Human Approval Gate
    y2 = y1 + 86  # 306
    draw_rounded_rectangle(draw, (center_x - b_half, y2, center_x + b_half, y2 + 54), 8, fill="#78350f", outline="#f59e0b", width=2)
    draw.text((center_x - b_half + 20, y2 + 10), "Human Approval Gate", fill="#ffffff", font=font_bold_lg)
    draw.text((center_x - b_half + 20, y2 + 32), "Shop owner inspects discount, estimated uplift, and clicks 'Approve'", fill="#fde68a", font=font_body)
    draw_rounded_rectangle(draw, (center_x + b_half - 110, y2 + 10, center_x + b_half - 15, y2 + 30), 4, fill="#b45309", outline="#fde047", width=1)
    draw.text((center_x + b_half - 100, y2 + 14), "AUTHORIZED", fill="#ffffff", font=font_badge)

    # Arrow 2 -> 3
    draw_arrow(draw, (center_x, y2 + 54), (center_x, y2 + 86), color="#38bdf8", width=3)

    # Step 3: Tool Execution (executor_node)
    y3 = y2 + 86  # 392
    draw_rounded_rectangle(draw, (center_x - b_half, y3, center_x + b_half, y3 + 54), 8, fill="#0f766e", outline="#14b8a6", width=2)
    draw.text((center_x - b_half + 20, y3 + 10), "Tool Execution (executor_node)", fill="#ffffff", font=font_bold_lg)
    draw.text((center_x - b_half + 20, y3 + 32), "Dispatcher calls create_simulated_promotion(category='Snacks', ...)", fill="#ccfbf1", font=font_body)
    draw_rounded_rectangle(draw, (center_x + b_half - 110, y3 + 10, center_x + b_half - 15, y3 + 30), 4, fill="#0d9488", outline="#5eead4", width=1)
    draw.text((center_x + b_half - 102, y3 + 14), "DISPATCHING", fill="#ffffff", font=font_badge)

    # Arrow 3 -> 4
    draw_arrow(draw, (center_x, y3 + 54), (center_x, y3 + 86), color="#ef4444", width=3)

    # Step 4: Unexpected Technical Error
    y4 = y3 + 86  # 478
    draw_rounded_rectangle(draw, (center_x - b_half, y4, center_x + b_half, y4 + 54), 8, fill="#7f1d1d", outline="#ef4444", width=2)
    draw.text((center_x - b_half + 20, y4 + 10), "Unexpected Technical Error Occurs", fill="#ffffff", font=font_bold_lg)
    draw.text((center_x - b_half + 20, y4 + 32), "Database lock / downstream timeout / invalid parameter raised in tool", fill="#fecaca", font=font_body)
    draw_rounded_rectangle(draw, (center_x + b_half - 110, y4 + 10, center_x + b_half - 15, y4 + 30), 4, fill="#991b1b", outline="#f87171", width=1)
    draw.text((center_x + b_half - 95, y4 + 14), "EXCEPTION", fill="#ffffff", font=font_badge)

    # Arrow 4 -> 5
    draw_arrow(draw, (center_x, y4 + 54), (center_x, y4 + 86), color="#ef4444", width=3)

    # Step 5: Failure Detection (tools.registry)
    y5 = y4 + 86  # 564
    draw_rounded_rectangle(draw, (center_x - b_half, y5, center_x + b_half, y5 + 54), 8, fill="#451a03", outline="#d97706", width=2)
    draw.text((center_x - b_half + 20, y5 + 10), "Failure Detection (tools.registry)", fill="#ffffff", font=font_bold_lg)
    draw.text((center_x - b_half + 20, y5 + 32), "try...except traps error; prevents crash; returns status: 'failed'", fill="#fed7aa", font=font_body)
    draw_rounded_rectangle(draw, (center_x + b_half - 110, y5 + 10, center_x + b_half - 15, y5 + 30), 4, fill="#b45309", outline="#fde047", width=1)
    draw.text((center_x + b_half - 98, y5 + 14), "INTERCEPTED", fill="#ffffff", font=font_badge)

    # Arrow 5 -> 6
    draw_arrow(draw, (center_x, y5 + 54), (center_x, y5 + 86), color="#a855f7", width=3)

    # Step 6: Error Logging & State Preservation
    y6 = y5 + 86  # 650
    draw_rounded_rectangle(draw, (center_x - b_half, y6, center_x + b_half, y6 + 58), 8, fill="#581c87", outline="#a855f7", width=2)
    draw.text((center_x - b_half + 20, y6 + 10), "Error Logging + State Preservation", fill="#ffffff", font=font_bold_lg)
    draw.text((center_x - b_half + 20, y6 + 32), "Writes error to execution_results & SqliteSaver (dukaanpilot.db)", fill="#e9d5ff", font=font_body)
    draw_rounded_rectangle(draw, (center_x + b_half - 110, y6 + 10, center_x + b_half - 15, y6 + 30), 4, fill="#7e22ce", outline="#d8b4fe", width=1)
    draw.text((center_x + b_half - 98, y6 + 14), "CHECKPOINT", fill="#ffffff", font=font_badge)

    # Arrow 6 -> 7
    draw_arrow(draw, (center_x, y6 + 58), (center_x, y6 + 90), color="#38bdf8", width=3)

    # Step 7: Recovery Decision (Diamond / Fork Hub)
    y7 = y6 + 90  # 740
    hub_w = 380
    draw_rounded_rectangle(draw, (center_x - hub_w // 2, y7, center_x + hub_w // 2, y7 + 54), 8, fill="#0f172a", outline="#38bdf8", width=2)
    draw.text((center_x - 85, y7 + 10), "Recovery Decision Gate", fill="#38bdf8", font=font_bold_lg)
    draw.text((center_x - 145, y7 + 32), "Select: Re-attempt action safely OR cancel safely", fill="#94a3b8", font=font_body)

    # Branch Left: Safe Retry
    branch_left_x = center_x - 240
    branch_right_x = center_x + 240
    branch_y = y7 + 90  # 830
    sub_w = 340
    sub_half = sub_w // 2

    # Draw branching split lines
    draw.line([(center_x - 80, y7 + 54), (branch_left_x, branch_y)], fill="#10b981", width=3)
    draw.polygon([(branch_left_x, branch_y), (branch_left_x - 6, branch_y - 12), (branch_left_x + 6, branch_y - 12)], fill="#10b981")
    draw.text((branch_left_x - 20, y7 + 58), "Safe Retry", fill="#34d399", font=font_bold)

    draw.line([(center_x + 80, y7 + 54), (branch_right_x, branch_y)], fill="#f43f5e", width=3)
    draw.polygon([(branch_right_x, branch_y), (branch_right_x - 6, branch_y - 12), (branch_right_x + 6, branch_y - 12)], fill="#f43f5e")
    draw.text((branch_right_x - 30, y7 + 58), "Cancel Plan", fill="#fb7185", font=font_bold)

    # Box: Safe Retry Branch
    draw_rounded_rectangle(draw, (branch_left_x - sub_half, branch_y, branch_left_x + sub_half, branch_y + 80), 8, fill="#064e3b", outline="#10b981", width=2)
    draw.text((branch_left_x - sub_half + 15, branch_y + 10), "Branch A: Safe Retry", fill="#ffffff", font=font_bold)
    draw.text((branch_left_x - sub_half + 15, branch_y + 32), "1. Revise parameters / resolve dependency", fill="#a7f3d0", font=font_body)
    draw.text((branch_left_x - sub_half + 15, branch_y + 52), "2. Re-validate schema + Human Approval", fill="#6ee7b7", font=font_body)

    # Box: Cancel Branch
    draw_rounded_rectangle(draw, (branch_right_x - sub_half, branch_y, branch_right_x + sub_half, branch_y + 80), 8, fill="#4c0519", outline="#f43f5e", width=2)
    draw.text((branch_right_x - sub_half + 15, branch_y + 10), "Branch B: Cancel / Abort", fill="#ffffff", font=font_bold)
    draw.text((branch_right_x - sub_half + 15, branch_y + 32), "1. Action remains permanently 'failed'", fill="#fecdd3", font=font_body)
    draw.text((branch_right_x - sub_half + 15, branch_y + 52), "2. ₹0 revenue uplift attributed", fill="#fda4af", font=font_body)

    # Outcome boxes below
    out_y = branch_y + 115  # 945
    draw_arrow(draw, (branch_left_x, branch_y + 80), (branch_left_x, out_y), color="#10b981", width=3)
    draw_arrow(draw, (branch_right_x, branch_y + 80), (branch_right_x, out_y), color="#f43f5e", width=3)

    # Final Outcome A
    draw_rounded_rectangle(draw, (branch_left_x - sub_half, out_y, branch_left_x + sub_half, out_y + 60), 8, fill="#0f172a", outline="#059669", width=2)
    draw.text((branch_left_x - sub_half + 15, out_y + 10), "Execution Result Verified", fill="#34d399", font=font_bold)
    draw.text((branch_left_x - sub_half + 15, out_y + 32), "Status: 'success' | Uplift recorded", fill="#cbd5e1", font=font_body)

    # Final Outcome B
    draw_rounded_rectangle(draw, (branch_right_x - sub_half, out_y, branch_right_x + sub_half, out_y + 60), 8, fill="#0f172a", outline="#dc2626", width=2)
    draw.text((branch_right_x - sub_half + 15, out_y + 10), "Action Remains Failed", fill="#f87171", font=font_bold)
    draw.text((branch_right_x - sub_half + 15, out_y + 32), "Audit log finalized | Safe state intact", fill="#cbd5e1", font=font_body)

    # Save diagram
    output_path = os.path.join(os.path.dirname(__file__), "failure_recovery_diagram.png")
    img.save(output_path, "PNG")
    print(f"Successfully generated failure recovery diagram at: {output_path}")


if __name__ == "__main__":
    build_diagram()
