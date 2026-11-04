"""Tool registry and dispatcher for DukaanPilot AI."""

from typing import Any, Callable, Dict
from tools.bundle_tool import recommend_product_bundle
from tools.campaign_tool import draft_customer_campaign
from tools.promotion_tool import create_simulated_promotion
from tools.reorder_tool import create_reorder_suggestion

# Registered demonstration tools
AVAILABLE_TOOLS: Dict[str, Callable[..., Dict[str, Any]]] = {
    "create_simulated_promotion": create_simulated_promotion,
    "recommend_product_bundle": recommend_product_bundle,
    "create_reorder_suggestion": create_reorder_suggestion,
    "draft_customer_campaign": draft_customer_campaign,
}

TOOL_SCHEMAS: Dict[str, Dict[str, Any]] = {
    "create_simulated_promotion": {
        "description": "Create a simulated promotional discount for a category",
        "required_params": ["promotion_name", "category", "discount_percentage"],
        "optional_params": ["duration_days", "data_dir"],
    },
    "recommend_product_bundle": {
        "description": "Formulate a cross-selling combo bundle with shared discount",
        "required_params": ["bundle_name", "primary_product_id", "complementary_product_id"],
        "optional_params": ["bundle_discount_pct", "data_dir"],
    },
    "create_reorder_suggestion": {
        "description": "Generate low-stock wholesale procurement draft order",
        "required_params": ["product_id"],
        "optional_params": ["suggested_quantity", "data_dir"],
    },
    "draft_customer_campaign": {
        "description": "Draft targeted communication for a customer segment",
        "required_params": ["target_segment", "campaign_title", "message_template"],
        "optional_params": ["channel", "data_dir"],
    },
}


def execute_action(tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
    """Execute a registered demonstration tool with comprehensive failure recovery.

    Args:
        tool_name: Name of tool in AVAILABLE_TOOLS
        parameters: Keyword arguments for the tool

    Returns:
        Dict[str, Any]: Structured execution outcome report.
    """
    if tool_name not in AVAILABLE_TOOLS:
        return {
            "status": "failed",
            "tool": tool_name,
            "error": f"Tool '{tool_name}' is not in available demonstration tools.",
            "available_tools": list(AVAILABLE_TOOLS.keys()),
        }

    func = AVAILABLE_TOOLS[tool_name]
    try:
        result = func(**parameters)
        return result
    except Exception as exc:
        return {
            "status": "failed",
            "tool": tool_name,
            "error": str(exc),
            "parameters": parameters,
        }
