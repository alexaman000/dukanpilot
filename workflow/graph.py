"""LangGraph workflow definition for DukaanPilot AI - Sneha Bhandar."""

from datetime import datetime
import os
import sqlite3
from typing import Any, Dict, List, Literal, Optional

from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt

from agents.action_validator import validate_proposed_plan
from agents.business_analyst import BusinessAnalyst
from agents.growth_planner import generate_growth_plan
from database.data_loader import load_all_data
from tools.registry import execute_action
from workflow.config import DEFAULT_DB_PATH
from workflow.evaluator import evaluate_and_reflect, measure_execution_outcomes
from workflow.state import WorkflowState


def analyst_node(state: WorkflowState) -> Dict[str, Any]:
    """Execute deterministic data analysis on Sneha Bhandar's synthetic dataset."""
    try:
        data = load_all_data("data")
        analyst = BusinessAnalyst(
            sales_df=data["sales"],
            products_df=data["products"],
            expenses_df=data["expenses"],
            customers_df=data["customers"],
            promotions_df=data["promotions"],
        )
        summary = analyst.generate_executive_summary()
        return {
            "business_metrics": summary,
            "workflow_status": "analyzed",
        }
    except Exception as exc:
        return {
            "errors": state.get("errors", []) + [f"Analyst error: {str(exc)}"],
            "workflow_status": "error",
        }


def planner_node(state: WorkflowState) -> Dict[str, Any]:
    """Generate structured, data-grounded growth actions."""
    metrics = state.get("business_metrics", {})
    goal = state.get("business_goal", {})
    context = state.get("business_context", {})
    current_iter = state.get("iteration_count", 0) + 1

    actions = generate_growth_plan(
        business_context=context,
        metrics=metrics,
        goal=goal,
        iteration=current_iter,
    )

    return {
        "proposed_actions": actions,
        "iteration_count": current_iter,
        "workflow_status": "planned",
    }


def validator_node(state: WorkflowState) -> Dict[str, Any]:
    """Validate proposed actions against tool schemas and safety constraints."""
    proposed = state.get("proposed_actions", [])
    val_report = validate_proposed_plan(proposed)

    return {
        "validation_results": val_report,
        "proposed_actions": val_report["valid_actions"],
        "workflow_status": "validated",
    }


def human_approval_node(state: WorkflowState) -> Dict[str, Any]:
    """Pause workflow for human review, or process approval decision."""
    # If state already marked approved (e.g. pre-set in automated test), bypass interrupt
    current_status = state.get("approval_status", "pending")
    if current_status == "approved":
        return {
            "approval_status": "approved",
            "approved_actions": state.get("approved_actions") or state.get("proposed_actions", []),
            "workflow_status": "approval_processed",
        }

    valid_actions = state.get("proposed_actions", [])

    # Interrupt execution and wait for human response
    decision_payload = interrupt({
        "type": "human_approval_required",
        "shop": state.get("business_context", {}).get("shop_name", "Sneha Bhandar"),
        "goal": state.get("business_goal", {}).get("description", ""),
        "proposed_actions": valid_actions,
        "message": (
            "Please review the proposed growth actions for Sneha Bhandar. "
            "Reply with 'approve' to execute, 'reject' to cancel, or provide revised actions."
        ),
    })

    # Parse resume decision
    approval_status = "approved"
    approved_actions = valid_actions

    if isinstance(decision_payload, str):
        normalized = decision_payload.strip().lower()
        if normalized in ("approve", "approved", "yes", "y"):
            approval_status = "approved"
            approved_actions = valid_actions
        elif normalized in ("reject", "rejected", "no", "n"):
            approval_status = "rejected"
            approved_actions = []
        else:
            # Default to reject if input unrecognized
            approval_status = "rejected"
            approved_actions = []
    elif isinstance(decision_payload, dict):
        decision = decision_payload.get("decision", "approve").lower()
        if decision in ("reject", "rejected"):
            approval_status = "rejected"
            approved_actions = []
        elif decision in ("revise", "revised"):
            revised_candidates = decision_payload.get("actions", valid_actions)
            # Re-validate revised actions to guarantee schema & parameter compliance
            val_report = validate_proposed_plan(revised_candidates)
            approved_actions = val_report.get("valid_actions", [])
            approval_status = "approved" if approved_actions else "rejected"
        else:
            approval_status = "approved"
            approved_actions = decision_payload.get("actions", valid_actions)
    elif isinstance(decision_payload, list):
        # User passed customized action list directly: validate before approval
        val_report = validate_proposed_plan(decision_payload)
        approved_actions = val_report.get("valid_actions", [])
        approval_status = "approved" if approved_actions else "rejected"

    return {
        "approval_status": approval_status,
        "approved_actions": approved_actions,
        "workflow_status": "approval_processed",
    }


def executor_node(state: WorkflowState) -> Dict[str, Any]:
    """Safely execute approved actions using local demonstration tools."""
    approved = state.get("approved_actions", [])
    exec_logs = list(state.get("execution_results", []))

    for act in approved:
        tool_name = act.get("tool_name", "")
        params = act.get("parameters", {})
        result = execute_action(tool_name, params)
        exec_logs.append({
            "action_id": act.get("action_id"),
            "action_name": act.get("action_name"),
            "tool_name": tool_name,
            "status": result.get("status", "unknown"),
            "executed_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "details": result.get("details", {}),
            "message": result.get("message", ""),
            "error": result.get("error"),
        })

    return {
        "execution_results": exec_logs,
        "workflow_status": "executed",
    }


def measurement_node(state: WorkflowState) -> Dict[str, Any]:
    """Measure outcomes and contrast with baseline and target revenue."""
    outcomes = measure_execution_outcomes(state)
    return {
        "measured_outcomes": outcomes,
        "workflow_status": "measured",
    }


def learning_node(state: WorkflowState) -> Dict[str, Any]:
    """Reflect on completed cycle and determine next strategic step."""
    reflection = evaluate_and_reflect(state)
    next_status = "completed" if not reflection.get("should_replan") else "replanning"
    return {
        "learning_summary": reflection,
        "workflow_status": next_status,
    }


def rejection_node(state: WorkflowState) -> Dict[str, Any]:
    """Handle plan rejection by shop owner."""
    return {
        "workflow_status": "rejected",
        "errors": state.get("errors", []) + ["Plan was rejected by shop owner. No tools executed."],
    }


def route_approval(state: WorkflowState) -> Literal["executor", "rejection"]:
    """Conditional router following human approval gate."""
    if state.get("approval_status") == "approved":
        return "executor"
    return "rejection"


def route_learning(state: WorkflowState) -> Literal["planner", "__end__"]:
    """Conditional router determining replanning loop vs workflow completion."""
    reflection = state.get("learning_summary", {})
    iter_count = state.get("iteration_count", 0)
    max_iter = state.get("max_iterations", 2)

    if reflection.get("should_replan") and iter_count < max_iter:
        return "planner"
    return END


def build_growth_workflow(checkpointer: Optional[Any] = None) -> Any:
    """Build and compile the complete DukaanPilot AI LangGraph workflow.

    Args:
        checkpointer: Optional persistence checkpointer (defaults to SQLite checkpointer).

    Returns:
        Compiled StateGraph runnable.
    """
    builder = StateGraph(WorkflowState)

    # Register workflow nodes
    builder.add_node("analyst", analyst_node)
    builder.add_node("planner", planner_node)
    builder.add_node("validator", validator_node)
    builder.add_node("human_approval", human_approval_node)
    builder.add_node("executor", executor_node)
    builder.add_node("measurement", measurement_node)
    builder.add_node("learning", learning_node)
    builder.add_node("rejection", rejection_node)

    # Define linear graph edges
    builder.add_edge(START, "analyst")
    builder.add_edge("analyst", "planner")
    builder.add_edge("planner", "validator")
    builder.add_edge("validator", "human_approval")

    # Conditional routing after human approval
    builder.add_conditional_edges(
        "human_approval",
        route_approval,
        {
            "executor": "executor",
            "rejection": "rejection",
        },
    )

    # Post-execution stages
    builder.add_edge("executor", "measurement")
    builder.add_edge("measurement", "learning")

    # Rejection exits immediately
    builder.add_edge("rejection", END)

    # Replanning loop from learning node
    builder.add_conditional_edges(
        "learning",
        route_learning,
        {
            "planner": "planner",
            END: END,
        },
    )

    # Initialize checkpointer
    if checkpointer is None:
        db_dir = os.path.dirname(DEFAULT_DB_PATH)
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)
        conn = sqlite3.connect(DEFAULT_DB_PATH, check_same_thread=False)
        checkpointer = SqliteSaver(conn)

    return builder.compile(checkpointer=checkpointer)
