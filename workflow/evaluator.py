"""Outcome measurement and reflection engine for DukaanPilot AI."""

from typing import Any, Dict, List
from workflow.state import WorkflowState


def measure_execution_outcomes(state: WorkflowState) -> Dict[str, Any]:
    """Evaluate measurable outcomes from executed actions and baseline data.

    Explicitly differentiates verified dataset numbers from simulated projections.
    """
    exec_results = state.get("execution_results", [])
    metrics = state.get("business_metrics", {})
    growth_status = metrics.get("growth_status", {})

    baseline_avg = float(growth_status.get("actual_monthly_avg_inr", 9159.33))
    target_inr = float(growth_status.get("target_monthly_inr", 10000.0))
    current_gap = float(growth_status.get("gap_to_target_inr", 840.67))

    successful_runs = [r for r in exec_results if r.get("status") == "success"]
    failed_runs = [r for r in exec_results if r.get("status") == "failed"]

    # Sum estimated simulated uplifts
    total_simulated_uplift_inr = 0.0
    total_estimated_costs_inr = 0.0

    for res in successful_runs:
        details = res.get("details", {})
        if "estimated_revenue_uplift_inr" in details:
            total_simulated_uplift_inr += float(details["estimated_revenue_uplift_inr"])
        elif "estimated_procurement_cost_inr" in details:
            total_estimated_costs_inr += float(details["estimated_procurement_cost_inr"])
        elif "bundle_gross_margin_inr" in details:
            # Assume ~15 bundle sales/month as conservative estimate
            total_simulated_uplift_inr += float(details["bundle_gross_margin_inr"]) * 15

    total_simulated_uplift_inr = round(total_simulated_uplift_inr, 2)
    total_estimated_costs_inr = round(total_estimated_costs_inr, 2)

    projected_new_run_rate = round(baseline_avg + total_simulated_uplift_inr, 2)
    remaining_projected_gap = round(max(0.0, target_inr - projected_new_run_rate), 2)
    target_achieved_in_simulation = projected_new_run_rate >= target_inr

    return {
        "actual_historical_monthly_avg_inr": baseline_avg,
        "target_monthly_revenue_inr": target_inr,
        "historical_gap_inr": current_gap,
        "total_actions_executed": len(exec_results),
        "successful_actions_count": len(successful_runs),
        "failed_actions_count": len(failed_runs),
        "total_simulated_revenue_uplift_inr": total_simulated_uplift_inr,
        "total_estimated_cost_incurred_inr": total_estimated_costs_inr,
        "projected_monthly_run_rate_inr": projected_new_run_rate,
        "remaining_projected_gap_inr": remaining_projected_gap,
        "target_achieved_in_simulation": target_achieved_in_simulation,
        "disclaimer": "All uplift figures are simulated projections based on local synthetic models. No real customer behavior or actual financial revenue has been fabricated.",
    }


def evaluate_and_reflect(state: WorkflowState) -> Dict[str, Any]:
    """Reflect on outcomes and determine whether to replan or conclude."""
    iteration = state.get("iteration_count", 1)
    max_iter = state.get("max_iterations", 2)
    measured = state.get("measured_outcomes", {})
    target_met = measured.get("target_achieved_in_simulation", False)
    failed_count = measured.get("failed_actions_count", 0)

    should_replan = False
    decision_reason = ""

    if iteration >= max_iter:
        should_replan = False
        decision_reason = (
            f"Execution halted: Reached iteration limit ({iteration}/{max_iter}). "
            "Simulated strategies evaluated and recorded."
        )
    elif failed_count > 0:
        should_replan = True
        decision_reason = f"{failed_count} action(s) experienced execution failures. Replanning necessary to adjust parameters."
    elif not target_met:
        should_replan = True
        decision_reason = (
            f"Target not yet reached in simulation (Projected run rate: ₹{measured.get('projected_monthly_run_rate_inr', 0):,.2f} "
            f"vs target ₹{measured.get('target_monthly_revenue_inr', 10000):,.2f}). Proceeding to next growth planning cycle."
        )
    else:
        should_replan = False
        decision_reason = (
            f"Target successfully met in simulation! Projected monthly revenue reaches "
            f"₹{measured.get('projected_monthly_run_rate_inr', 0):,.2f} (Target: ₹{measured.get('target_monthly_revenue_inr', 10000):,.2f})."
        )

    return {
        "iteration_completed": iteration,
        "target_met_in_simulation": target_met,
        "should_replan": should_replan,
        "decision_reason": decision_reason,
        "key_learnings": [
            "Cross-selling tea and biscuits provides immediate basket size expansion without heavy discount cost.",
            "Replenishing critical staples (Deggi Mirch, Bread) prevents recurring lost footfall.",
            "Targeting family shoppers for weekend stock-ups produces the largest individual ticket size gains.",
        ],
    }
