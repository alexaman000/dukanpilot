"""Unit tests for demonstration business tools."""

import pytest
from tools.bundle_tool import recommend_product_bundle
from tools.campaign_tool import draft_customer_campaign
from tools.promotion_tool import create_simulated_promotion
from tools.registry import AVAILABLE_TOOLS, execute_action
from tools.reorder_tool import create_reorder_suggestion


def test_create_simulated_promotion():
    """Verify promotion creation tool structure and safe limits."""
    res = create_simulated_promotion(
        promotion_name="Weekend Snacks Blast",
        category="Snacks & Packaged Foods",
        discount_percentage=10.0,
        duration_days=7,
    )
    assert res["status"] == "success"
    assert res["details"]["is_simulated"] is True
    assert res["details"]["discount_percentage"] == 10.0
    assert res["details"]["estimated_volume_uplift_pct"] > 0
    assert res["details"]["estimated_revenue_uplift_inr"] > 0


def test_promotion_bounds_validation():
    """Verify promotion tool rejects unsafe discount percentage."""
    with pytest.raises(ValueError, match="out of safe range"):
        create_simulated_promotion(
            promotion_name="Extreme Markdown",
            category="Staples",
            discount_percentage=50.0,  # exceeds 30%
        )


def test_recommend_product_bundle():
    """Verify product bundle pricing, margin calculation, and customer savings."""
    res = recommend_product_bundle(
        bundle_name="Tea & Biscuit Combo",
        primary_product_id="PROD-008",  # Red Label Tea 250g (Price: ₹115, Cost: ₹98)
        complementary_product_id="PROD-011",  # Parle-G 250g (Price: ₹25, Cost: ₹20)
        bundle_discount_pct=5.0,
    )
    assert res["status"] == "success"
    details = res["details"]
    assert details["is_simulated"] is True
    assert details["standalone_total_inr"] == 140.0
    assert details["bundle_price_inr"] == 133.0
    assert details["customer_savings_inr"] == 7.0
    assert details["bundle_gross_margin_inr"] > 0


def test_bundle_invalid_product():
    """Verify bundle tool rejects nonexistent product IDs."""
    with pytest.raises(ValueError, match="not found in catalog"):
        recommend_product_bundle(
            bundle_name="Ghost Bundle",
            primary_product_id="NONEXISTENT-PROD",
            complementary_product_id="PROD-008",
        )


def test_create_reorder_suggestion():
    """Verify procurement purchase order draft generation."""
    res = create_reorder_suggestion(
        product_id="PROD-007",  # MDH Deggi Mirch (Low stock)
        suggested_quantity=10,
    )
    assert res["status"] == "success"
    details = res["details"]
    assert details["is_simulated"] is True
    assert details["product_id"] == "PROD-007"
    assert details["suggested_units"] == 10
    assert details["estimated_procurement_cost_inr"] > 0
    assert details["stockout_risk_averted"] is True


def test_draft_customer_campaign():
    """Verify customer communication drafting and template rendering."""
    res = draft_customer_campaign(
        target_segment="Weekly Family Shopper",
        campaign_title="Weekend Family Savings",
        message_template="Namaste! Visit {shop_name} at {location} this weekend for family staples.",
        channel="WhatsApp",
    )
    assert res["status"] == "success"
    details = res["details"]
    assert details["is_simulated"] is True
    assert details["targeted_customer_count"] > 0
    assert "Sneha Bhandar" in details["rendered_message"]
    assert "Shiv Shakti Nagar" in details["rendered_message"]


def test_execute_action_unknown_tool():
    """Verify graceful error reporting when an unknown tool is invoked."""
    report = execute_action("nonexistent_teleport_tool", {})
    assert report["status"] == "failed"
    assert "is not in available demonstration tools" in report["error"]


def test_execute_action_tool_failure_recovery():
    """Verify dispatcher captures tool parameter exceptions without crashing."""
    report = execute_action("create_reorder_suggestion", {"product_id": "INVALID-ID"})
    assert report["status"] == "failed"
    assert "not found in catalog" in report["error"]
