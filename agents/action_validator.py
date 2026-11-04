"""Action validation module for DukaanPilot AI."""

from typing import Any, Dict, List
from tools.registry import AVAILABLE_TOOLS, TOOL_SCHEMAS


def validate_action(action: Dict[str, Any]) -> Dict[str, Any]:
    """Validate a single proposed growth action against system safety rules.

    Args:
        action: Dictionary specifying proposed action and parameters.

    Returns:
        Dict[str, Any]: Validation report with boolean 'is_valid' and 'reason'.
    """
    if not isinstance(action, dict):
        return {"is_valid": False, "reason": "Action payload must be a dictionary."}

    required_keys = ["tool_name", "action_name", "parameters", "expected_impact", "success_metric"]
    missing = [k for k in required_keys if k not in action]
    if missing:
        return {"is_valid": False, "reason": f"Action is missing required fields: {missing}"}

    tool_name = action["tool_name"]
    if tool_name not in AVAILABLE_TOOLS:
        return {
            "is_valid": False,
            "reason": f"Tool '{tool_name}' is not supported. Supported demonstration tools: {list(AVAILABLE_TOOLS.keys())}",
        }

    schema = TOOL_SCHEMAS.get(tool_name, {})
    params = action.get("parameters", {})
    if not isinstance(params, dict):
        return {"is_valid": False, "reason": "Parameters field must be a dictionary of arguments."}

    missing_params = [p for p in schema.get("required_params", []) if p not in params]
    if missing_params:
        return {
            "is_valid": False,
            "reason": f"Tool '{tool_name}' missing required parameters: {missing_params}",
        }

    # Safety checks
    if tool_name == "create_simulated_promotion":
        discount = params.get("discount_percentage", 0)
        if discount > 30:
            return {"is_valid": False, "reason": f"Promotional discount of {discount}% exceeds safe limit of 30%."}

    if tool_name == "recommend_product_bundle":
        b_disc = params.get("bundle_discount_pct", 0)
        if b_disc > 25:
            return {"is_valid": False, "reason": f"Bundle discount of {b_disc}% exceeds maximum safety threshold of 25%."}

    if tool_name == "create_reorder_suggestion":
        qty = params.get("suggested_quantity", 0)
        if qty <= 0 or qty > 100:
            return {"is_valid": False, "reason": f"Reorder quantity {qty} is out of safe range (1-100)."}

    # Policy guard: Labeling requirement
    impact_str = str(action.get("expected_impact", "")).lower()
    if "estimate" not in impact_str and "project" not in impact_str and "expected" not in impact_str:
        return {"is_valid": False, "reason": "Expected impact must be explicitly labeled as an estimate or projection."}

    return {"is_valid": True, "reason": "Valid action grounded in system constraints."}


def validate_proposed_plan(actions: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Validate a collection of proposed actions.

    Returns:
        Dict[str, Any]: Partitioned dictionary with 'valid_actions' and 'rejected_actions'.
    """
    valid = []
    rejected = []

    for act in actions:
        result = validate_action(act)
        if result["is_valid"]:
            valid.append(act)
        else:
            rejected.append({"action": act, "reason": result["reason"]})

    return {
        "valid_actions": valid,
        "rejected_actions": rejected,
        "total_proposed": len(actions),
        "total_valid": len(valid),
        "total_rejected": len(rejected),
    }
