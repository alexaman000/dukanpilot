"""DukaanPilot AI - Core Application Entry Point

Autonomous AI Business Growth Worker for Sneha Bhandar (Ranchi, Jharkhand).
Orchestrates the LangGraph workflow, human approval gate, tool execution, and replanning loop.
"""

import sys
import uuid

# Ensure UTF-8 output on platforms where default console encoding is legacy (e.g., Windows cp1252)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from database.run_tracker import record_run_state
from langgraph.types import Command
from workflow import (
    BASELINE_MONTHLY_REVENUE,
    SHOP_ADDRESS,
    SHOP_NAME,
    TARGET_MONTHLY_REVENUE,
    build_growth_workflow,
    create_initial_state,
    is_gemini_available,
)


def run_demonstration(
    thread_id: str = "demo-sneha-session-01",
    auto_approve: bool = False,
    decision_override: str = "approve",
) -> None:
    """Run an end-to-end demonstration of DukaanPilot AI for Sneha Bhandar."""
    print("=" * 72)
    print(f"🏪 DukaanPilot AI: Autonomous Growth Worker")
    print(f"   Business: {SHOP_NAME}")
    print(f"   Location: {SHOP_ADDRESS}")
    print(f"   Mission:  Increase Monthly Revenue (₹{BASELINE_MONTHLY_REVENUE:,.0f} -> ₹{TARGET_MONTHLY_REVENUE:,.0f})")
    print(f"   Gemini Engine: {'Configured & Active' if is_gemini_available() else 'Offline / Deterministic Mode'}")
    print(f"   Thread ID: {thread_id}")
    print("=" * 72)

    # 1. Compile stateful workflow with persistent SQLite checkpointer
    app = build_growth_workflow()
    config = {"configurable": {"thread_id": thread_id}}
    state = create_initial_state()

    print("\n[Phase 1/4] Running Business Analyst & Growth Planner nodes...")
    # Invoke until human approval interrupt
    result = app.invoke(state, config=config)
    record_run_state(thread_id, result)

    # Check if workflow paused at human approval
    interrupts = result.get("__interrupt__", [])
    if interrupts:
        interrupt_val = interrupts[0].value
        actions = interrupt_val.get("proposed_actions", [])
        print(f"\n⏸️  WORKFLOW PAUSED: Human-in-the-Loop Approval Required")
        print("-" * 72)
        print(f"Proposed Strategy for {SHOP_NAME} ({len(actions)} actions):")
        for idx, act in enumerate(actions, 1):
            print(f"\n  {idx}. [{act.get('action_id')}] {act.get('action_name')}")
            print(f"     Tool:       {act.get('tool_name')}")
            print(f"     Rationale:  {act.get('business_rationale')}")
            print(f"     Impact:     {act.get('expected_impact')}")
            print(f"     Est. Cost:  ₹{act.get('estimated_cost', 0):,.2f}")
            print(f"     Metric:     {act.get('success_metric')}")

        print("-" * 72)

        # Prompt user or use automated choice
        if auto_approve:
            user_decision = decision_override
            print(f"Auto-selected decision: '{user_decision}'")
        else:
            try:
                prompt_text = "Enter decision: [A]pprove / [R]eject / [E]xit (Default: Approve): "
                user_choice = input(prompt_text).strip().lower()
                if user_choice in ("r", "reject"):
                    user_decision = "reject"
                else:
                    user_decision = "approve"
            except (EOFError, KeyboardInterrupt):
                user_decision = "approve"
                print("\n[Non-interactive detected] Defaulting to 'approve'.")

        print(f"\n[Phase 2/4] Resuming workflow with decision: '{user_decision.upper()}'...")
        # Resume the paused workflow from SQLite saved checkpoint
        result = app.invoke(Command(resume=user_decision), config=config)
        record_run_state(thread_id, result)

    # Inspect final outcome
    status = result.get("workflow_status")
    if status == "rejected":
        print("\n❌ Workflow Terminated: Proposed plan was rejected by the shop owner.")
        return

    print("\n[Phase 3/4] Tool Execution Results:")
    exec_logs = result.get("execution_results", [])
    for res in exec_logs:
        icon = "✅" if res.get("status") == "success" else "⚠️"
        print(f"  {icon} {res.get('action_name')}: {res.get('message', res.get('error'))}")

    print("\n[Phase 4/4] Outcome Measurement & Learning:")
    measured = result.get("measured_outcomes", {})
    learning = result.get("learning_summary", {})

    print(f"  • Historical Baseline:           ₹{measured.get('actual_historical_monthly_avg_inr', 0):,.2f} / month")
    print(f"  • Milestone Target:               ₹{measured.get('target_monthly_revenue_inr', 0):,.2f} / month")
    print(f"  • Simulated Monthly Uplift:      +₹{measured.get('total_simulated_revenue_uplift_inr', 0):,.2f} / month")
    print(f"  • Projected New Monthly Rate:     ₹{measured.get('projected_monthly_run_rate_inr', 0):,.2f} / month")
    print(f"  • Remaining Projected Gap:        ₹{measured.get('remaining_projected_gap_inr', 0):,.2f}")
    print(f"  • Iteration Cycle Status:         {learning.get('decision_reason', 'Completed')}")

    print("\n" + "=" * 72)
    print("DukaanPilot AI demonstration complete. All state persisted to database/dukaanpilot.db.")
    print("=" * 72)


def main() -> None:
    """CLI Entry point."""
    auto = "--auto" in sys.argv or "-y" in sys.argv
    thread = "demo-sneha-01"
    for arg in sys.argv:
        if arg.startswith("--thread="):
            thread = arg.split("=", 1)[1]

    run_demonstration(thread_id=thread, auto_approve=auto, decision_override="approve")


if __name__ == "__main__":
    main()
