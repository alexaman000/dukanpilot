"""Unit and integration tests for dashboard data binding, startup, and workflow controls."""

import sqlite3
import pandas as pd
import pytest

from agents.business_analyst import BusinessAnalyst
from database.data_loader import load_all_data
from database.run_tracker import get_run, list_all_runs, record_run_state
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.types import Command
import app as dashboard_app
from workflow.config import BASELINE_MONTHLY_REVENUE, TARGET_MONTHLY_REVENUE
from workflow.graph import build_growth_workflow
from workflow.state import create_initial_state


def test_dashboard_imports_and_startup():
    """Verify dashboard module imports and core helper bindings exist."""
    assert hasattr(dashboard_app, "get_store_data")
    assert hasattr(dashboard_app, "get_analyst")
    assert hasattr(dashboard_app, "get_workflow_snapshot")
    assert dashboard_app.SHOP_NAME == "Sneha Bhandar"
    assert "Ranchi" in dashboard_app.SHOP_ADDRESS


def test_dashboard_data_loading():
    """Verify that dashboard data access loads and binds all store records."""
    data = dashboard_app.get_store_data()
    assert "sales" in data
    assert "products" in data
    assert "expenses" in data
    assert "customers" in data
    assert "promotions" in data
    assert len(data["sales"]) > 0


def test_dashboard_period_filtering():
    """Verify that period filtering calculates accurate metrics for distinct months."""
    data = dashboard_app.get_store_data()
    analyst = dashboard_app.get_analyst(data)

    all_rev = analyst.get_total_revenue()
    jan_rev = analyst.get_total_revenue("2024-01-01", "2024-01-31")
    feb_rev = analyst.get_total_revenue("2024-02-01", "2024-02-29")
    mar_rev = analyst.get_total_revenue("2024-03-01", "2024-03-31")

    assert all_rev > 0
    assert jan_rev > 0
    assert feb_rev > 0
    assert mar_rev > 0
    assert round(jan_rev + feb_rev + mar_rev, 2) == round(all_rev, 2)


def test_data_display_using_existing_analysis_functions():
    """Verify all analytic queries used by dashboard sections return valid schemas."""
    data = dashboard_app.get_store_data()
    analyst = dashboard_app.get_analyst(data)

    # 1. Total revenue and financial KPIs
    total_rev = analyst.get_total_revenue("2024-01-01", "2024-01-31")
    assert total_rev > 0

    gp = analyst.get_gross_profit("2024-01-01", "2024-01-31")
    assert "gross_profit" in gp
    assert "gross_margin_pct" in gp
    assert gp["gross_profit"] > 0

    np = analyst.get_net_profit("2024-01-01", "2024-01-31")
    assert "estimated_net_profit" in np
    assert "total_expenses" in np

    aov = analyst.get_average_transaction_value("2024-01-01", "2024-01-31")
    assert aov > 0

    # 2. Charts and breakdowns
    daily = analyst.get_revenue_by_day("2024-01-01", "2024-01-31")
    assert not daily.empty
    assert "date" in daily.columns
    assert "revenue" in daily.columns

    cat_df = analyst.get_revenue_by_category("2024-01-01", "2024-01-31")
    assert not cat_df.empty
    assert "category" in cat_df.columns
    assert "revenue" in cat_df.columns
    assert "share_pct" in cat_df.columns

    # 3. Product performance tables
    top_prods = analyst.get_best_selling_products(5, "2024-01-01", "2024-01-31")
    assert len(top_prods) <= 5
    assert "product_name" in top_prods.columns
    assert "revenue" in top_prods.columns

    slow_prods = analyst.get_slow_moving_products(5, "2024-01-01", "2024-01-31")
    assert len(slow_prods) <= 5
    assert "units_sold" in slow_prods.columns

    # 4. Low stock inventory alerts
    low_stock = analyst.get_low_stock_products()
    assert isinstance(low_stock, pd.DataFrame)
    if not low_stock.empty:
        assert "stock_deficit" in low_stock.columns

    # 5. Goal comparison
    growth_data = analyst.compare_to_growth_target(
        baseline_monthly=BASELINE_MONTHLY_REVENUE,
        target_monthly=TARGET_MONTHLY_REVENUE,
    )
    assert growth_data["baseline_monthly_inr"] == 8000.0
    assert growth_data["target_monthly_inr"] == 10000.0
    assert growth_data["actual_monthly_avg_inr"] > 0


def test_workflow_start_and_approval_resume_integration():
    """Verify workflow starts, halts at approval interrupt, and resumes on approve."""
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    saver = SqliteSaver(conn)
    app = build_growth_workflow(checkpointer=saver)

    thread_id = "test-dashboard-start-approve"
    config = {"configurable": {"thread_id": thread_id}}

    # 1. Start workflow
    res1 = app.invoke(create_initial_state(), config=config)
    assert len(res1.get("__interrupt__", [])) > 0
    interrupt_payload = res1["__interrupt__"][0].value
    assert interrupt_payload["type"] == "human_approval_required"
    assert len(interrupt_payload["proposed_actions"]) >= 3

    # 2. Resume with approval
    res2 = app.invoke(Command(resume="approve"), config=config)
    assert res2["approval_status"] == "approved"
    assert len(res2["approved_actions"]) >= 3
    assert len(res2["execution_results"]) >= 3
    for log in res2["execution_results"]:
        assert log["status"] == "success"
        assert "executed_at" in log


def test_rejection_preventing_execution():
    """Verify rejection immediately halts the workflow with zero executed tools."""
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    saver = SqliteSaver(conn)
    app = build_growth_workflow(checkpointer=saver)

    thread_id = "test-dashboard-reject"
    config = {"configurable": {"thread_id": thread_id}}

    res1 = app.invoke(create_initial_state(), config=config)
    assert len(res1.get("__interrupt__", [])) > 0

    res2 = app.invoke(Command(resume="reject"), config=config)
    assert res2["approval_status"] == "rejected"
    assert res2["workflow_status"] == "rejected"
    assert len(res2.get("execution_results", [])) == 0


def test_workflow_revision_resumes_selected_actions():
    """Verify that custom revision only executes user-selected actions."""
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    saver = SqliteSaver(conn)
    app = build_growth_workflow(checkpointer=saver)

    thread_id = "test-dashboard-revise"
    config = {"configurable": {"thread_id": thread_id}}

    res1 = app.invoke(create_initial_state(max_iterations=1), config=config)
    interrupts = res1.get("__interrupt__", [])
    assert len(interrupts) > 0
    proposed = interrupts[0].value.get("proposed_actions", [])
    assert len(proposed) >= 2

    # Choose only the first proposed action
    selected = [proposed[0]]
    res2 = app.invoke(Command(resume={"decision": "revise", "actions": selected}), config=config)
    assert res2["approval_status"] == "approved"
    assert len(res2["approved_actions"]) == 1
    assert len(res2["execution_results"]) == 1
    assert res2["execution_results"][0]["action_id"] == proposed[0]["action_id"]


def test_avoiding_duplicate_execution_on_reruns():
    """Verify that querying state snapshot of an already-completed run does not re-trigger tools."""
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    saver = SqliteSaver(conn)
    app = build_growth_workflow(checkpointer=saver)

    t_id = "test-no-duplicate"
    config = {"configurable": {"thread_id": t_id}}

    # Initial run + approval
    app.invoke(create_initial_state(), config=config)
    res = app.invoke(Command(resume="approve"), config=config)
    initial_actions_count = len(res["execution_results"])

    # Simulating Streamlit page refresh: inspect state snapshot without invoking graph execution
    snapshot = app.get_state(config)
    assert snapshot is not None
    assert snapshot.values["approval_status"] == "approved"
    assert len(snapshot.values["execution_results"]) == initial_actions_count


def test_get_workflow_snapshot_preserves_interrupts():
    """Verify get_workflow_snapshot extracts pending interrupts from tasks on restored sessions."""
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    saver = SqliteSaver(conn)
    app = build_growth_workflow(checkpointer=saver)

    t_id = "test-snapshot-recovery"
    config = {"configurable": {"thread_id": t_id}}

    # Start and pause at interrupt
    app.invoke(create_initial_state(), config=config)

    # Use app's helper
    snapshot = dashboard_app.get_workflow_snapshot(app, t_id)
    assert snapshot is not None
    assert "__interrupt__" in snapshot
    assert len(snapshot["__interrupt__"]) > 0
    assert snapshot["__interrupt__"][0].value["type"] == "human_approval_required"


def test_run_tracker_persistence(tmp_path):
    """Verify run history recording, listing, and querying in SQLite."""
    db_file = str(tmp_path / "test_tracker.db")

    state = create_initial_state()
    state["workflow_status"] = "awaiting_approval"
    state["approval_status"] = "pending"
    state["proposed_actions"] = [{"action_id": "A1"}, {"action_id": "A2"}]

    record_run_state("test-run-101", state, db_path=db_file)

    runs = list_all_runs(db_path=db_file)
    assert len(runs) == 1
    assert runs[0]["thread_id"] == "test-run-101"
    assert runs[0]["workflow_status"] == "awaiting_approval"
    assert runs[0]["approval_status"] == "pending"
    assert runs[0]["actions_count"] == 2

    # Update run state upon approval
    state["approval_status"] = "approved"
    state["workflow_status"] = "completed"
    state["execution_results"] = [{"status": "success"}]
    state["measured_outcomes"] = {"total_simulated_revenue_uplift_inr": 650.0}

    record_run_state("test-run-101", state, db_path=db_file)

    updated_run = get_run("test-run-101", db_path=db_file)
    assert updated_run is not None
    assert updated_run["approval_status"] == "approved"
    assert updated_run["workflow_status"] == "completed"
    assert updated_run["simulated_uplift_inr"] == 650.0


def test_revision_validates_and_rejects_unsafe_actions():
    """Verify that revising a plan requires validation, filtering out unsafe parameters."""
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    saver = SqliteSaver(conn)
    app = build_growth_workflow(checkpointer=saver)

    t_id = "test-revision-validation"
    config = {"configurable": {"thread_id": t_id}}

    res1 = app.invoke(create_initial_state(max_iterations=1), config=config)
    assert len(res1.get("__interrupt__", [])) > 0

    # Submit an invalid revised action (50% discount exceeds 30% limit)
    invalid_revised_actions = [
        {
            "action_id": "ACT-UNSAFE",
            "tool_name": "create_simulated_promotion",
            "action_name": "Dangerous 50% Off",
            "parameters": {
                "promotion_name": "Too Cheap",
                "category": "All",
                "discount_percentage": 50.0,
            },
            "expected_impact": "Estimated impact: Negative margins",
            "success_metric": "Bankruptcy",
        }
    ]

    res2 = app.invoke(Command(resume={"decision": "revise", "actions": invalid_revised_actions}), config=config)
    # Since the only action submitted was invalid, it was rejected
    assert res2["approval_status"] == "rejected"
    assert len(res2.get("execution_results", [])) == 0


def test_missing_gemini_credentials_raises_error(monkeypatch):
    """Verify that requiring Gemini credentials produces a clear, descriptive error when key is missing."""
    from workflow.config import require_gemini_api_key
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    with pytest.raises(ValueError) as excinfo:
        require_gemini_api_key()
    assert "Missing Gemini API credentials" in str(excinfo.value)
    assert "GEMINI_API_KEY" in str(excinfo.value)


def test_mocked_gemini_planning_integration(monkeypatch):
    """Verify growth planner correctly parses live LLM JSON responses without external network access."""
    from unittest.mock import MagicMock, patch
    from agents.growth_planner import generate_growth_plan

    monkeypatch.setenv("GEMINI_API_KEY", "mock-test-key-12345")

    mock_llm_json = """
    [
        {
            "action_id": "ACT-MOCK01",
            "tool_name": "create_simulated_promotion",
            "action_name": "Mocked Snacks Push",
            "business_rationale": "High margin snacks category expansion.",
            "parameters": {
                "promotion_name": "Mock Promo",
                "category": "Snacks & Packaged Foods",
                "discount_percentage": 10.0
            },
            "expected_impact": "Estimated impact: +₹450 monthly revenue",
            "estimated_cost": 50.0,
            "risks_or_constraints": "Display prominently.",
            "success_metric": "Sell 20 units"
        },
        {
            "action_id": "ACT-MOCK02",
            "tool_name": "create_reorder_suggestion",
            "action_name": "Mocked Reorder",
            "business_rationale": "Restock low inventory.",
            "parameters": {
                "product_id": "PROD-007",
                "suggested_quantity": 10
            },
            "expected_impact": "Estimated impact: +₹300 monthly sales",
            "estimated_cost": 700.0,
            "risks_or_constraints": "Capital required.",
            "success_metric": "Zero stockouts"
        }
    ]
    """

    mock_response = MagicMock()
    mock_response.text = mock_llm_json

    mock_client = MagicMock()
    mock_client.models.generate_content.return_value = mock_response

    with patch("google.genai.Client", return_value=mock_client):
        plan = generate_growth_plan(
            business_context={"shop_name": "Sneha Bhandar"},
            metrics={"financials": {"total_revenue": 24000}},
            goal={"description": "Reach ₹10,000/mo"},
            iteration=1,
        )

    assert len(plan) == 2
    assert plan[0]["action_id"] == "ACT-MOCK01"
    assert plan[0]["tool_name"] == "create_simulated_promotion"
    assert plan[1]["action_id"] == "ACT-MOCK02"
    assert "Estimated impact" in plan[0]["expected_impact"]
