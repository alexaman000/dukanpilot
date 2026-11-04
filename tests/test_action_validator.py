"""Unit tests for the Action Validator module."""

from agents.action_validator import validate_action, validate_proposed_plan


def test_validate_valid_action():
    """Verify that a properly constructed action passes validation."""
    action = {
        "action_id": "ACT-01",
        "tool_name": "create_reorder_suggestion",
        "action_name": "Restock Deggi Mirch",
        "business_rationale": "Inventory is below reorder threshold.",
        "parameters": {
            "product_id": "PROD-007",
            "suggested_quantity": 10,
        },
        "expected_impact": "Estimated impact: Protects ~₹500 monthly sales.",
        "estimated_cost": 700.0,
        "risks_or_constraints": "Working capital required.",
        "success_metric": "Zero stockouts for 30 days.",
    }
    report = validate_action(action)
    assert report["is_valid"] is True


def test_reject_unsupported_tool():
    """Verify rejection of actions specifying an unsupported tool."""
    action = {
        "action_id": "ACT-02",
        "tool_name": "automated_bank_transfer_tool",
        "action_name": "Transfer funds",
        "parameters": {},
        "expected_impact": "Estimated impact: None",
        "success_metric": "Transfer complete",
    }
    report = validate_action(action)
    assert report["is_valid"] is False
    assert "not supported" in report["reason"]


def test_reject_missing_required_params():
    """Verify rejection when required parameters for the tool are missing."""
    action = {
        "action_id": "ACT-03",
        "tool_name": "create_simulated_promotion",
        "action_name": "Discount Flash",
        "parameters": {"discount_percentage": 10.0},  # missing promotion_name and category
        "expected_impact": "Estimated impact: +₹200",
        "success_metric": "Volume up",
    }
    report = validate_action(action)
    assert report["is_valid"] is False
    assert "missing required parameters" in report["reason"]


def test_reject_excessive_discount():
    """Verify safety policy rejecting promotional discounts exceeding 30%."""
    action = {
        "action_id": "ACT-04",
        "tool_name": "create_simulated_promotion",
        "action_name": "Deep Discount Clearance",
        "parameters": {
            "promotion_name": "Clearance",
            "category": "All",
            "discount_percentage": 50.0,
        },
        "expected_impact": "Estimated impact: Fast clearance",
        "success_metric": "Stock cleared",
    }
    report = validate_action(action)
    assert report["is_valid"] is False
    assert "exceeds safe limit of 30%" in report["reason"]


def test_reject_unlabeled_expected_impact():
    """Verify policy requiring explicit labeling of expected impact as estimate/projection."""
    action = {
        "action_id": "ACT-05",
        "tool_name": "create_reorder_suggestion",
        "action_name": "Restock",
        "parameters": {"product_id": "PROD-007", "suggested_quantity": 5},
        "expected_impact": "Will definitely increase sales by ₹1,000",  # missing estimate/project/expected
        "success_metric": "Sales up",
    }
    report = validate_action(action)
    assert report["is_valid"] is False
    assert "must be explicitly labeled as an estimate" in report["reason"]


def test_validate_proposed_plan_partition():
    """Verify partitioning of valid and rejected actions."""
    actions = [
        {
            "action_id": "A1",
            "tool_name": "create_reorder_suggestion",
            "action_name": "Valid Restock",
            "parameters": {"product_id": "PROD-007", "suggested_quantity": 10},
            "expected_impact": "Estimated impact: +₹300",
            "success_metric": "Stock maintained",
        },
        {
            "action_id": "A2",
            "tool_name": "fake_tool",
            "action_name": "Invalid Action",
            "parameters": {},
            "expected_impact": "Estimated impact: Unknown",
            "success_metric": "None",
        },
    ]
    summary = validate_proposed_plan(actions)
    assert summary["total_proposed"] == 2
    assert summary["total_valid"] == 1
    assert summary["total_rejected"] == 1
    assert len(summary["valid_actions"]) == 1
    assert len(summary["rejected_actions"]) == 1
