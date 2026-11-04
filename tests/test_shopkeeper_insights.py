"""Unit and integration tests for shopkeeper plain-language insights and bilingual translations."""

import pandas as pd
import pytest

from agents.business_analyst import BusinessAnalyst
from agents.shopkeeper_insights import (
    TRANSLATIONS,
    get_plain_language_insights,
    get_shopkeeper_action_view,
    get_shopkeeper_status,
    get_shopkeeper_summary,
    get_workflow_timeline,
    t,
)
from database.data_loader import load_all_data
from workflow.config import BASELINE_MONTHLY_REVENUE, TARGET_MONTHLY_REVENUE


@pytest.fixture
def store_analyst() -> BusinessAnalyst:
    """Fixture providing initialized BusinessAnalyst with synthetic store data."""
    data = load_all_data("data")
    return BusinessAnalyst(
        sales_df=data["sales"],
        products_df=data["products"],
        expenses_df=data["expenses"],
        customers_df=data["customers"],
        promotions_df=data["promotions"],
    )


def test_bilingual_dictionary_coverage():
    """Verify that both English and Hindi translation dictionaries have all essential UI keys."""
    assert "en" in TRANSLATIONS
    assert "hi" in TRANSLATIONS

    required_keys = [
        "greeting",
        "current_monthly_sales",
        "monthly_goal",
        "remaining_to_goal",
        "overall_status",
        "key_issue",
        "recommended_action",
        "status_doing_well",
        "status_needs_attention",
        "status_action_required",
        "what_to_do_next",
        "plain_insights_title",
        "worker_activity_title",
        "btn_run_planner",
        "btn_approve_all",
        "btn_reject_all",
    ]

    for key in required_keys:
        assert key in TRANSLATIONS["en"], f"Missing '{key}' in English dictionary"
        assert key in TRANSLATIONS["hi"], f"Missing '{key}' in Hindi dictionary"
        assert t(key, "en") != ""
        assert t(key, "hi") != ""


def test_shopkeeper_status_evaluation(store_analyst):
    """Verify that shopkeeper status returns a valid code, label, and explanation."""
    status_en = get_shopkeeper_status(store_analyst, "en")
    assert status_en["code"] in ("doing_well", "needs_attention", "action_required")
    assert status_en["label"] in ("Doing well", "Needs attention", "Action required")
    assert len(status_en["description"]) > 10

    status_hi = get_shopkeeper_status(store_analyst, "hi")
    assert status_hi["code"] == status_en["code"]
    assert status_hi["label"] in ("सब ठीक है", "ध्यान देने की ज़रूरत", "तुरंत कार्रवाई आवश्यक")


def test_shopkeeper_summary_generation_english_and_hindi(store_analyst):
    """Verify top-level summary delivers friendly greetings, goal progress, and key next step."""
    summary_en = get_shopkeeper_summary(store_analyst, "en")
    assert "Namaste" in summary_en["greeting"]
    assert summary_en["monthly_goal"] == TARGET_MONTHLY_REVENUE
    assert summary_en["current_monthly_sales"] > 0
    assert summary_en["remaining_gap"] >= 0
    assert "status" in summary_en
    assert "key_issue" in summary_en
    assert "recommended_action" in summary_en
    assert "Demonstration" in summary_en["disclaimer"]

    summary_hi = get_shopkeeper_summary(store_analyst, "hi")
    assert "नमस्ते" in summary_hi["greeting"]
    assert summary_hi["monthly_goal"] == TARGET_MONTHLY_REVENUE
    assert "प्रदर्शन" in summary_hi["disclaimer"]


def test_plain_language_insights_dynamic_generation(store_analyst):
    """Verify dynamic insights translate data metrics into simple retail observations."""
    insights_en = get_plain_language_insights(store_analyst, "en")
    assert len(insights_en) == 5

    topics = [i["topic"] for i in insights_en]
    assert "Goal Progress" in topics
    assert "Top Category" in topics
    assert "Slow Items" in topics
    assert "Stock Alert" in topics
    assert "Profitability" in topics

    # Ensure insights contain actual store numbers and names, not static placeholder text
    goal_text = next(i["text"] for i in insights_en if i["topic"] == "Goal Progress")
    assert "₹" in goal_text
    assert "10,000" in goal_text

    cat_text = next(i["text"] for i in insights_en if i["topic"] == "Top Category")
    assert "Grains & Staples" in cat_text or "%" in cat_text

    # Test Hindi insights translation
    insights_hi = get_plain_language_insights(store_analyst, "hi")
    assert len(insights_hi) == 5
    hi_topics = [i["topic"] for i in insights_hi]
    assert "लक्ष्य की प्रगति" in hi_topics
    assert "मुख्य बिक्री श्रेणी" in hi_topics


def test_workflow_timeline_honest_state_mapping():
    """Verify 5-stage timeline faithfully reflects workflow execution states without faking progress."""
    # 1. Idle / None state
    t_idle = get_workflow_timeline(None, "en")
    assert len(t_idle) == 5
    for stage in t_idle:
        assert stage["status"] == "pending"
        assert stage["badge"] == "Not Started Yet"

    # 2. Paused at human approval
    paused_state = {
        "business_metrics": {"financials": {"total_revenue": 24000}},
        "proposed_actions": [{"action_id": "A1"}],
        "__interrupt__": [{"value": {"proposed_actions": [{"action_id": "A1"}]}}],
        "workflow_status": "awaiting_approval",
        "approval_status": "pending",
    }
    t_paused = get_workflow_timeline(paused_state, "en")
    assert t_paused[0]["status"] == "completed"
    assert t_paused[1]["status"] == "completed"
    assert t_paused[2]["status"] == "waiting"
    assert t_paused[2]["badge"] == "Waiting for You"
    assert t_paused[3]["status"] == "pending"
    assert t_paused[4]["status"] == "pending"

    # 3. Approved and executed
    approved_state = {
        "business_metrics": {"financials": {"total_revenue": 24000}},
        "proposed_actions": [{"action_id": "A1"}],
        "approved_actions": [{"action_id": "A1"}],
        "approval_status": "approved",
        "workflow_status": "completed",
        "execution_results": [{"action_id": "A1", "status": "success"}],
        "measured_outcomes": {"total_simulated_revenue_uplift_inr": 450.0},
    }
    t_approved = get_workflow_timeline(approved_state, "en")
    assert all(stage["status"] == "completed" for stage in t_approved)

    # 4. Rejected plan
    rejected_state = {
        "business_metrics": {"financials": {"total_revenue": 24000}},
        "proposed_actions": [{"action_id": "A1"}],
        "approval_status": "rejected",
        "workflow_status": "rejected",
        "execution_results": [],
    }
    t_rejected = get_workflow_timeline(rejected_state, "en")
    assert t_rejected[2]["status"] == "rejected"
    assert t_rejected[3]["status"] == "skipped"
    assert t_rejected[4]["status"] == "skipped"


def test_shopkeeper_action_view_adaptation():
    """Verify action parameters and rationale are translated into accessible shopkeeper format."""
    action = {
        "action_id": "ACT-001",
        "action_name": "Evening Tea Snack Bundle",
        "tool_name": "create_bundled_offer",
        "business_rationale": "Encourages customers buying tea to pick up biscuits.",
        "expected_impact": "Estimated impact: +₹400 monthly revenue",
        "estimated_cost": 30.0,
        "risks_or_constraints": "Check biscuit freshness.",
    }

    view_en = get_shopkeeper_action_view(action, "en")
    assert "Combo Savings Pack" in view_en["title"]
    assert view_en["why"] == action["business_rationale"]
    assert "AI Estimate" in view_en["benefit"]
    assert "₹30.00" in view_en["cost"]

    view_hi = get_shopkeeper_action_view(action, "hi")
    assert "कॉम्बो बचत पैक" in view_hi["title"]
    assert "AI अनुमान" in view_hi["benefit"]
