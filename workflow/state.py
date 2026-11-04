"""Workflow state definition for DukaanPilot AI LangGraph orchestrator."""

from typing import Any, Dict, List, Optional
from typing_extensions import TypedDict
from workflow.config import (
    BASELINE_MONTHLY_REVENUE,
    MONTHLY_REVENUE_GROWTH_TARGET,
    SHOP_ADDRESS,
    SHOP_CURRENCY,
    SHOP_NAME,
    SHOP_TYPE,
    TARGET_MONTHLY_REVENUE,
)


class WorkflowState(TypedDict, total=False):
    """Structured state container passed between LangGraph nodes."""

    # Business Identity & Baseline
    business_context: Dict[str, Any]
    business_metrics: Dict[str, Any]
    business_goal: Dict[str, Any]

    # Planning & Validation
    proposed_actions: List[Dict[str, Any]]
    validation_results: Dict[str, Any]

    # Human-in-the-Loop Gate
    approval_status: str  # 'pending', 'approved', 'rejected', 'revised'
    approved_actions: List[Dict[str, Any]]

    # Tool Execution & Results
    execution_results: List[Dict[str, Any]]

    # Evaluation & Learning
    measured_outcomes: Dict[str, Any]
    learning_summary: Dict[str, Any]

    # Lifecycle & Loop Controls
    iteration_count: int
    max_iterations: int
    errors: List[str]
    workflow_status: str  # 'initialized', 'analyzed', 'planned', 'awaiting_approval', 'executing', 'measuring', 'replanning', 'completed', 'rejected', 'error'


def create_initial_state(
    baseline_monthly: float = BASELINE_MONTHLY_REVENUE,
    target_monthly: float = TARGET_MONTHLY_REVENUE,
    max_iterations: int = 2,
) -> WorkflowState:
    """Create and return a freshly initialized workflow state for Sneha Bhandar."""
    return {
        "business_context": {
            "shop_name": SHOP_NAME,
            "address": SHOP_ADDRESS,
            "business_type": SHOP_TYPE,
            "currency": SHOP_CURRENCY,
        },
        "business_metrics": {},
        "business_goal": {
            "baseline_monthly_revenue": baseline_monthly,
            "target_monthly_revenue": target_monthly,
            "required_growth_inr": target_monthly - baseline_monthly,
            "description": f"Increase monthly revenue from ₹{baseline_monthly:,.0f} to ₹{target_monthly:,.0f}",
        },
        "proposed_actions": [],
        "validation_results": {"valid_actions": [], "rejected_actions": []},
        "approval_status": "pending",
        "approved_actions": [],
        "execution_results": [],
        "measured_outcomes": {},
        "learning_summary": {},
        "iteration_count": 0,
        "max_iterations": max_iterations,
        "errors": [],
        "workflow_status": "initialized",
    }
