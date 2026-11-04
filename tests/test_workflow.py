"""Integration and unit tests for the LangGraph workflow orchestrator."""

import sqlite3
import pytest
try:
    from langgraph.checkpoint.sqlite import SqliteSaver
except ImportError:
    try:
        from langgraph_checkpoint_sqlite import SqliteSaver
    except ImportError:
        try:
            from langgraph.checkpoint.memory import MemorySaver as SqliteSaver
        except ImportError:
            from langgraph_checkpoint.memory import MemorySaver as SqliteSaver
from langgraph.types import Command

from workflow.graph import (
    analyst_node,
    build_growth_workflow,
    executor_node,
    learning_node,
    measurement_node,
    planner_node,
    validator_node,
)
from workflow.state import create_initial_state


@pytest.fixture
def memory_workflow():
    """Create a workflow compiled with an in-memory SQLite checkpointer."""
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    saver = SqliteSaver(conn)
    return build_growth_workflow(checkpointer=saver)


def test_workflow_state_initialization():
    """Verify clean initial state values and business identity."""
    state = create_initial_state(baseline_monthly=8000.0, target_monthly=10000.0)
    assert state["business_context"]["shop_name"] == "Sneha Bhandar"
    assert "Ranchi" in state["business_context"]["address"]
    assert state["business_goal"]["baseline_monthly_revenue"] == 8000.0
    assert state["business_goal"]["target_monthly_revenue"] == 10000.0
    assert state["business_goal"]["required_growth_inr"] == 2000.0
    assert state["approval_status"] == "pending"
    assert state["iteration_count"] == 0
    assert state["workflow_status"] == "initialized"


def test_analyst_node():
    """Verify analyst node populates verified deterministic business metrics."""
    initial = create_initial_state()
    res = analyst_node(initial)
    assert res["workflow_status"] == "analyzed"
    metrics = res["business_metrics"]
    assert "financials" in metrics
    assert "growth_status" in metrics
    assert metrics["financials"]["total_revenue"] > 0
    assert metrics["growth_status"]["target_monthly_inr"] == 10000.0


def test_planner_node_deterministic_structure():
    """Verify planner node generates 3-5 grounded actions."""
    initial = create_initial_state()
    analyzed = analyst_node(initial)
    state = {**initial, **analyzed}

    planned = planner_node(state)
    assert planned["workflow_status"] == "planned"
    assert planned["iteration_count"] == 1
    actions = planned["proposed_actions"]
    assert 3 <= len(actions) <= 5

    for act in actions:
        assert "action_id" in act
        assert "tool_name" in act
        assert "action_name" in act
        assert "business_rationale" in act
        assert "expected_impact" in act
        assert "success_metric" in act
        assert "parameters" in act


def test_validator_node():
    """Verify validator node accepts valid actions and filters appropriately."""
    initial = create_initial_state()
    state = {
        **initial,
        "proposed_actions": [
            {
                "action_id": "ACT-1",
                "tool_name": "create_reorder_suggestion",
                "action_name": "Restock",
                "parameters": {"product_id": "PROD-007", "suggested_quantity": 5},
                "expected_impact": "Estimated impact: Protects sales",
                "success_metric": "Zero stockouts",
            }
        ],
    }
    validated = validator_node(state)
    assert validated["workflow_status"] == "validated"
    assert validated["validation_results"]["total_valid"] == 1
    assert len(validated["proposed_actions"]) == 1


def test_human_approval_pause_and_resume(memory_workflow):
    """Verify workflow pauses at human approval node and resumes upon approval."""
    thread_id = "test-approval-pause-01"
    config = {"configurable": {"thread_id": thread_id}}
    initial_state = create_initial_state()

    # Run until approval interrupt
    step1 = memory_workflow.invoke(initial_state, config=config)

    # Verify pause via interrupt
    interrupts = step1.get("__interrupt__", [])
    assert len(interrupts) > 0
    interrupt_payload = interrupts[0].value
    assert interrupt_payload["type"] == "human_approval_required"
    assert len(interrupt_payload["proposed_actions"]) >= 3

    # Resume with approval
    step2 = memory_workflow.invoke(Command(resume="approve"), config=config)
    assert step2["approval_status"] == "approved"
    assert len(step2["execution_results"]) >= 3
    assert step2["workflow_status"] in ("completed", "replanning")


def test_rejection_prevents_tool_execution(memory_workflow):
    """Verify rejection immediately terminates workflow without executing any tools."""
    thread_id = "test-rejection-01"
    config = {"configurable": {"thread_id": thread_id}}
    initial_state = create_initial_state()

    # Run until interrupt
    step1 = memory_workflow.invoke(initial_state, config=config)
    assert len(step1.get("__interrupt__", [])) > 0

    # Resume with rejection
    step2 = memory_workflow.invoke(Command(resume="reject"), config=config)
    assert step2["approval_status"] == "rejected"
    assert step2["workflow_status"] == "rejected"
    assert len(step2.get("execution_results", [])) == 0


def test_approved_actions_invoke_local_tools():
    """Verify executor node runs approved tools and collects structured outcomes."""
    state = {
        "approved_actions": [
            {
                "action_id": "ACT-01",
                "action_name": "Test Reorder",
                "tool_name": "create_reorder_suggestion",
                "parameters": {"product_id": "PROD-007", "suggested_quantity": 5},
            },
            {
                "action_id": "ACT-02",
                "action_name": "Test Bundle",
                "tool_name": "recommend_product_bundle",
                "parameters": {
                    "bundle_name": "Tea & Biscuits",
                    "primary_product_id": "PROD-008",
                    "complementary_product_id": "PROD-011",
                },
            },
        ],
        "execution_results": [],
    }
    executed = executor_node(state)
    assert executed["workflow_status"] == "executed"
    results = executed["execution_results"]
    assert len(results) == 2
    assert results[0]["status"] == "success"
    assert results[1]["status"] == "success"


def test_tool_failure_recovery_in_executor():
    """Verify executor recovers when an individual tool fails without halting entire run."""
    state = {
        "approved_actions": [
            {
                "action_id": "ACT-FAIL",
                "action_name": "Broken Reorder",
                "tool_name": "create_reorder_suggestion",
                "parameters": {"product_id": "GHOST-PRODUCT"},  # triggers error
            },
            {
                "action_id": "ACT-PASS",
                "action_name": "Working Promotion",
                "tool_name": "create_simulated_promotion",
                "parameters": {
                    "promotion_name": "Snacks Promo",
                    "category": "Snacks & Packaged Foods",
                    "discount_percentage": 5.0,
                },
            },
        ],
        "execution_results": [],
    }
    executed = executor_node(state)
    assert executed["workflow_status"] == "executed"
    results = executed["execution_results"]
    assert len(results) == 2
    assert results[0]["status"] == "failed"
    assert "not found in catalog" in results[0]["error"]
    assert results[1]["status"] == "success"


def test_outcome_measurement_and_replanning_limits():
    """Verify outcome measurement calculations and replanning guardrail limits."""
    state = {
        "iteration_count": 2,
        "max_iterations": 2,  # at max limit
        "business_metrics": {
            "growth_status": {
                "actual_monthly_avg_inr": 9159.33,
                "target_monthly_inr": 10000.0,
                "gap_to_target_inr": 840.67,
            }
        },
        "execution_results": [
            {
                "status": "success",
                "details": {"estimated_revenue_uplift_inr": 200.0},
            }
        ],
    }

    # Measurement
    measured = measurement_node(state)
    assert measured["workflow_status"] == "measured"
    assert measured["measured_outcomes"]["total_simulated_revenue_uplift_inr"] == 200.0

    # Learning reflection
    state["measured_outcomes"] = measured["measured_outcomes"]
    reflection = learning_node(state)
    assert reflection["workflow_status"] == "completed"
    assert reflection["learning_summary"]["should_replan"] is False
    assert "Reached iteration limit" in reflection["learning_summary"]["decision_reason"]
